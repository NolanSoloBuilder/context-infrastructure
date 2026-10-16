#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["PyYAML>=6,<7"]
# ///
"""Local candidate/export helpers and read-only HTTPS verification; never registers keys."""

import argparse
import base64
import configparser
import copy
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import re
import secrets
import ssl
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

import yaml


class SkillError(Exception):
    pass


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load_json(path):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError):
        raise SkillError("JSON 文件无法读取或格式无效。") from None


def load_current(path):
    try:
        data = yaml.safe_load(Path(path).read_text())
        nodes = data["proxies"]
        if not isinstance(nodes, list) or not nodes:
            raise ValueError()
        names = [n["name"] for n in nodes]
        if len(set(names)) != len(names):
            raise ValueError()
        return data
    except (OSError, ValueError, TypeError, KeyError, yaml.YAMLError):
        raise SkillError("当前 YAML 无效、为空或含重复节点名。") from None


def target_index(current, node_id):
    if not re.fullmatch(r"str-[a-z0-9]+", node_id):
        raise SkillError("需要完整节点 ID，例如 str-sin303。")
    pattern = re.compile(r"(?<![a-zA-Z0-9-])" + re.escape(node_id) + r"(?![a-zA-Z0-9-])")
    matches = [i for i, n in enumerate(current["proxies"]) if pattern.search(n["name"])]
    if len(matches) != 1 or current["proxies"][matches[0]].get("type") != "wireguard":
        raise SkillError("节点 ID 必须唯一匹配一个现有 WireGuard 节点。")
    return matches[0]


def checked_key(value):
    if len(base64.b64decode(value, validate=True)) != 32:
        raise ValueError()
    return value


def connection_fields(path):
    """Parse the supported single-Peer format without executing hooks."""
    try:
        parser = configparser.ConfigParser(interpolation=None, strict=True)
        parser.read_string(Path(path).read_text())
        if set(parser.sections()) != {"Interface", "Peer"} or parser.defaults():
            raise ValueError()
        a, p = parser["Interface"], parser["Peer"]
        if set(a) - {"privatekey", "address", "dns", "mtu"} or set(p) - {
            "publickey", "endpoint", "allowedips", "presharedkey", "persistentkeepalive"
        }:
            raise ValueError()
        addresses = [ipaddress.ip_interface(x.strip()) for x in a["Address"].split(",")]
        if not addresses or len({x.version for x in addresses}) != len(addresses):
            raise ValueError()
        dns = [str(ipaddress.ip_address(x.strip())) for x in a["DNS"].split(",")]
        allowed = [x.strip() for x in p["AllowedIPs"].split(",")]
        for cidr in allowed:
            ipaddress.ip_network(cidr)
        host, port = p["Endpoint"].rsplit(":", 1)
        bracketed = host.startswith("[") and host.endswith("]")
        host = host.removeprefix("[").removesuffix("]")
        # This generator returns IP endpoints, not arbitrary hostnames or config fragments.
        endpoint_ip = ipaddress.ip_address(host)
        if bracketed != (endpoint_ip.version == 6):
            raise ValueError()
        host = str(endpoint_ip)
        port = int(port)
        if not 1 <= port <= 65535:
            raise ValueError()
        fields = {
            "private-key": checked_key(a["PrivateKey"]),
            "public-key": checked_key(p["PublicKey"]),
            "server": host, "port": port, "dns": dns,
            "remote-dns-resolve": True, "allowed-ips": allowed,
        }
        for address in addresses:
            fields["ip" if address.version == 4 else "ipv6"] = str(address.ip)
        for section, source, dest in ((a, "MTU", "mtu"), (p, "PersistentKeepalive", "persistent-keepalive")):
            if source in section:
                fields[dest] = int(section[source])
                if fields[dest] < (1 if dest == "mtu" else 0) or fields[dest] > 65535:
                    raise ValueError()
        if "PresharedKey" in p:
            fields["pre-shared-key"] = checked_key(p["PresharedKey"])
        return fields
    except (OSError, ValueError, KeyError, configparser.Error):
        raise SkillError("不支持的 WireGuard 配置：检查单 Peer、地址/密钥/端口及未知字段；未输出配置内容。") from None


CONNECTION_KEYS = {
    "private-key", "public-key", "server", "port", "dns", "remote-dns-resolve",
    "allowed-ips", "ip", "ipv6", "mtu", "pre-shared-key", "persistent-keepalive",
}


def write_private_new(path, data):
    path = Path(path).expanduser().absolute()
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        raise SkillError("输出已存在（含符号链接）；请选择新路径，未覆盖文件。") from None
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise
    return {"file": str(path), "sha256": sha(data), "mode": "0600"}


def prepare_replacement(current_path, node_id, conf_path, output):
    original = load_current(current_path)
    index = target_index(original, node_id)
    fields = connection_fields(conf_path)
    old_node = original["proxies"][index]
    if "peers" in old_node:
        raise SkillError("不自动替换多 Peer 出站。")
    if fields["private-key"] in [n.get("private-key") for n in original["proxies"]]:
        raise SkillError("替换配置并非新密钥或与现有节点复用身份；未创建候选。")
    candidate = copy.deepcopy(original)
    node = candidate["proxies"][index]
    for key in CONNECTION_KEYS:
        node.pop(key, None)
    node.update(fields)
    payload = yaml.safe_dump(candidate, allow_unicode=True, sort_keys=False).encode()
    result = write_private_new(output, payload)
    return {**result, "node_id": node_id, "node_count": len(candidate["proxies"]),
            "other_nodes_unchanged": True, "non_proxy_settings_unchanged": True,
            "new_key_registered_by_this_tool": False, "network_verified": False}


def conf_matches(node, path):
    fields = connection_fields(path)
    return all(node.get(k) == fields.get(k) for k in CONNECTION_KEYS)


def export_conf(current_path, node_id, output, sources=None, original_dir=None):
    current = load_current(current_path)
    node = current["proxies"][target_index(current, node_id)]
    override = load_json(sources).get("overrides", {}).get(node_id) if sources else None
    if override is not None:
        try:
            path = Path(override["file"]).expanduser()
            if sha(path.read_bytes()) != override["sha256"]:
                raise ValueError()
        except (OSError, ValueError, KeyError, TypeError):
            raise SkillError("最新配置覆盖表无效或哈希不符；不回退到历史配置。") from None
        paths = [path]
    elif original_dir:
        paths = [p for p in Path(original_dir).glob("*.conf") if re.search(
            r"(?<![a-zA-Z0-9-])" + re.escape(node_id) + r"(?![a-zA-Z0-9-])", p.stem)]
    else:
        raise SkillError("缺少该节点的原生源配置；请提供覆盖表或原始导出目录。")
    matching = [p for p in paths if conf_matches(node, p)]
    if len(matching) != 1:
        raise SkillError("原生配置未唯一匹配当前 YAML，可能已换密钥；不生成或猜测配置。")
    result = write_private_new(output, matching[0].read_bytes())
    return {**result, "node_id": node_id, "current_yaml_fields_match": True,
            "original_bytes_preserved": True, "new_key_registered_by_this_tool": False}


def manifest_entry(path):
    data = load_json(path)
    try:
        if "subscriptions" in data:
            if data.get("mode") != "unified" or len(data["subscriptions"]) != 1:
                raise ValueError()
            data = data["subscriptions"][0]
        parsed = urllib.parse.urlsplit(data["url"])
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.fragment:
            raise ValueError()
        if not re.fullmatch(r"[0-9a-f]{64}", data["sha256"]):
            raise ValueError()
        return data
    except (KeyError, ValueError, TypeError):
        raise SkillError("需要有效的单份 HTTPS 订阅清单；未输出私人 URL。") from None


def native_fetch(url, method):
    marker = ("\nSTRONGVPN-" + secrets.token_hex(12) + ":").encode()
    args = ["/usr/bin/curl", "--disable", "--config", "-", "--noproxy", "*",
            "--silent", "--show-error", "--proto", "=https", "--tlsv1.2",
            "--connect-timeout", "10", "--max-time", "25", "--max-filesize", "4194304",
            "--write-out", marker.decode() + "%{http_code} %{ssl_verify_result}"]
    if method == "HEAD":
        args.append("--head")
    result = subprocess.run(args, input=("url = " + json.dumps(url) + "\n").encode(),
                            capture_output=True, timeout=30)
    if result.returncode:
        # curl stderr can contain the full private URL. Do not forward it.
        raise SkillError(f"macOS HTTPS 请求失败（curl {result.returncode}）；证书验证保持开启。")
    body, separator, trailer = result.stdout.rpartition(marker)
    try:
        status, verified = trailer.decode().split()
        if not separator or verified != "0":
            raise ValueError()
        return int(status), body
    except ValueError:
        raise SkillError("未取得已验证的 HTTPS 状态；未输出响应正文。") from None


def python_fetch(url, method):
    request = urllib.request.Request(url, method=method)
    # No redirects: do not forward a private subscription path to another destination.
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *args, **kwargs):
            return None
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    try:
        with opener.open(request, timeout=25) as response:
            body = response.read(4194305)
            if len(body) > 4194304:
                raise SkillError("订阅响应超出 4 MiB 限制。")
            if method == "HEAD":
                body = str(response.headers).encode()
            return response.status, body
    except urllib.error.HTTPError as error:
        return error.code, b""
    except urllib.error.URLError as error:
        if isinstance(error.reason, ssl.SSLCertVerificationError):
            raise SkillError("本机 Python 证书链校验失败；macOS 可用系统原生 curl 验收，不能关闭 TLS 校验。") from None
        raise SkillError("HTTPS 连接失败；未输出私人 URL。") from None


def verify_subscription(manifest, mirror=None, expected_file=None, transport="auto"):
    entry = manifest_entry(manifest)
    if mirror:
        other = manifest_entry(mirror)
        if any(entry.get(k) != other.get(k) for k in ("url", "path", "file", "sha256")):
            raise SkillError("两个私人清单不一致，先核对现网，不选择某个旧清单覆盖。")
    expected = Path(expected_file or entry["file"]).read_bytes()
    node_count = len(load_current(expected_file or entry["file"])["proxies"])
    # A candidate override is useful after remote replacement but before local manifest commit.
    if expected_file is None and sha(expected) != entry["sha256"]:
        raise SkillError("本地源文件与清单哈希不一致。")
    chosen = ("curl" if sys.platform == "darwin" else "python") if transport == "auto" else transport
    fetch = native_fetch if chosen == "curl" else python_fetch
    status, body = fetch(entry["url"], "GET")
    if status != 200 or sha(body) != sha(expected):
        raise SkillError("HTTPS GET 状态或字节哈希与预期文件不符。")
    status, head = fetch(entry["url"], "HEAD")
    headers = {k.strip().lower(): v.strip().lower() for line in head.decode(errors="replace").splitlines()
               if ":" in line for k, v in [line.split(":", 1)]}
    if status != 200 or not all((
        "private" in headers.get("cache-control", ""), "no-store" in headers.get("cache-control", ""),
        "yaml" in headers.get("content-type", ""), headers.get("referrer-policy") == "no-referrer",
        headers.get("x-content-type-options") == "nosniff", "noindex" in headers.get("x-robots-tag", ""),
    )):
        raise SkillError("HTTPS HEAD 状态或私人订阅响应头不符合现有合同。")
    return {"sha256": sha(expected), "node_count": node_count, "http_get": 200, "http_head": 200,
            "tls_verified": True, "transport": chosen, "private_headers": "passed",
            "remote_mutation": False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare-replacement", help="仅创建单节点替换候选；不生成密钥、不发布")
    export = commands.add_parser("export-conf", help="复制匹配当前 YAML 的原生 .conf；不重新生成")
    for command in (prepare, export):
        command.add_argument("--current", required=True)
        command.add_argument("--node", required=True)
        command.add_argument("--output", required=True)
    prepare.add_argument("--conf", required=True)
    export.add_argument("--sources")
    export.add_argument("--original-dir")
    verify = commands.add_parser("verify-subscription", help="只读验证原 HTTPS 订阅、哈希和响应头")
    verify.add_argument("--manifest", required=True)
    verify.add_argument("--mirror")
    verify.add_argument("--expected-file")
    verify.add_argument("--transport", choices=("auto", "curl", "python"), default="auto")
    args = parser.parse_args(argv)
    try:
        if args.command == "prepare-replacement":
            result = prepare_replacement(args.current, args.node, args.conf, args.output)
        elif args.command == "export-conf":
            result = export_conf(args.current, args.node, args.output, args.sources, args.original_dir)
        else:
            result = verify_subscription(args.manifest, args.mirror, args.expected_file, args.transport)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except SkillError as error:
        print(f"错误：{error}", file=sys.stderr)
    except (OSError, ValueError, TypeError, KeyError, subprocess.SubprocessError):
        print("错误：输入或执行环境无效；未输出配置正文、密钥或私人 URL。", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
