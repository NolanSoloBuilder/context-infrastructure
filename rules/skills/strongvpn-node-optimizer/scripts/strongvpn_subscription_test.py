import base64
import copy
import contextlib
import io
import json
from pathlib import Path
import stat
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import yaml

import strongvpn_subscription as tool


def key(byte):
    return base64.b64encode(bytes([byte]) * 32).decode()


def conf(private=3, ipv6=False, extra=""):
    endpoint = "[2001:db8::1]:55001" if ipv6 else "192.0.2.30:55001"
    address = "10.0.0.3/32, 2001:db8::3/128" if ipv6 else "10.0.0.3/32"
    return (f"[Interface]\nPrivateKey = {key(private)}\nAddress = {address}\nDNS = 1.1.1.1\n"
            f"[Peer]\nPublicKey = {key(8)}\nAllowedIPs = 0.0.0.0/0, ::/0\nEndpoint = {endpoint}\n{extra}")


class SubscriptionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.current = self.root / "current.yaml"
        self.old_conf = self.root / "str-sin303.conf"
        self.old_conf.write_text(conf(1))
        first = {"name": "Singapore · str-sin303", "type": "wireguard", "udp": True,
                 **tool.connection_fields(self.old_conf)}
        second = copy.deepcopy(first)
        second.update(name="Seoul · str-sel302", **{"private-key": key(2)})
        self.config = {"proxies": [first, second], "proxy-groups": [{"name": "StrongVPN", "proxies": [first["name"], second["name"]]}],
                       "rule-providers": {"cn": {"type": "http", "format": "mrs"}},
                       "rules": ["PROCESS-NAME,UURemote,DIRECT", "RULE-SET,cn,DIRECT", "MATCH,StrongVPN"],
                       "dns": {"enable": False}, "mixed-port": 7897, "mode": "rule"}
        self.current.write_text(yaml.safe_dump(self.config, allow_unicode=True, sort_keys=False))
        self.fresh = self.root / "new.conf"
        self.fresh.write_text(conf())
        self.output = self.root / "candidate.yaml"

    def test_single_node_preserves_everything_else_and_input_bytes(self):
        before = self.current.read_bytes()
        report = tool.prepare_replacement(self.current, "str-sin303", self.fresh, self.output)
        result = tool.load_current(self.output)
        self.assertEqual(self.current.read_bytes(), before)
        self.assertEqual(result["proxies"][1], self.config["proxies"][1])
        self.assertEqual({k: v for k, v in result.items() if k != "proxies"},
                         {k: v for k, v in self.config.items() if k != "proxies"})
        self.assertEqual(result["proxies"][0]["name"], self.config["proxies"][0]["name"])
        self.assertEqual(result["proxies"][0]["private-key"], key(3))
        self.assertEqual(stat.S_IMODE(self.output.stat().st_mode), 0o600)
        self.assertFalse(report["network_verified"])

    def test_reused_identity_rejected_before_output(self):
        self.fresh.write_text(conf(2))
        with self.assertRaises(tool.SkillError):
            tool.prepare_replacement(self.current, "str-sin303", self.fresh, self.output)
        self.assertFalse(self.output.exists())

    def test_prefix_id_does_not_replace_another_node(self):
        with self.assertRaises(tool.SkillError):
            tool.prepare_replacement(self.current, "str-sin30", self.fresh, self.output)
        self.assertFalse(self.output.exists())

    def test_ipv6_endpoint_and_optional_settings(self):
        self.fresh.write_text(conf(ipv6=True, extra=f"PresharedKey = {key(9)}\nPersistentKeepalive = 25\n"))
        tool.prepare_replacement(self.current, "str-sin303", self.fresh, self.output)
        node = tool.load_current(self.output)["proxies"][0]
        self.assertEqual((node["server"], node["port"]), ("2001:db8::1", 55001))
        self.assertEqual(node["ipv6"], "2001:db8::3")
        self.assertEqual(node["pre-shared-key"], key(9))
        self.assertEqual(node["persistent-keepalive"], 25)

    def test_unknown_hook_or_multiple_addresses_fail_closed(self):
        for data in (conf(extra="PostUp = touch /tmp/should-not-run\n"),
                     conf().replace("10.0.0.3/32", "10.0.0.3/32, 10.0.0.4/32"),
                     conf() + "[Peer]\nPublicKey = invalid\n",
                     conf(ipv6=True).replace("[2001:db8::1]", "2001:db8::1")):
            with self.subTest(data_kind=len(data)):
                self.fresh.write_text(data)
                with self.assertRaises(tool.SkillError):
                    tool.prepare_replacement(self.current, "str-sin303", self.fresh, self.output)
                self.assertFalse(self.output.exists())

    def test_absent_optional_fields_do_not_retain_old_connection_values(self):
        self.config["proxies"][0].update({"ipv6": "2001:db8::9", "mtu": 1380,
                                          "pre-shared-key": key(7), "persistent-keepalive": 25})
        self.current.write_text(yaml.safe_dump(self.config))
        tool.prepare_replacement(self.current, "str-sin303", self.fresh, self.output)
        node = tool.load_current(self.output)["proxies"][0]
        for name in ("ipv6", "mtu", "pre-shared-key", "persistent-keepalive"):
            self.assertNotIn(name, node)

    def test_existing_output_and_symlink_are_not_overwritten(self):
        target = self.root / "preserve.txt"
        target.write_text("preserve")
        self.output.symlink_to(target)
        with self.assertRaises(tool.SkillError):
            tool.prepare_replacement(self.current, "str-sin303", self.fresh, self.output)
        self.assertTrue(self.output.is_symlink())
        self.assertEqual(target.read_text(), "preserve")

    def test_export_prefers_latest_verified_override(self):
        tool.prepare_replacement(self.current, "str-sin303", self.fresh, self.output)
        sources = self.root / "sources.json"
        sources.write_text(json.dumps({"overrides": {"str-sin303": {"file": str(self.fresh), "sha256": tool.sha(self.fresh.read_bytes())}}}))
        dest = self.root / "export.conf"
        report = tool.export_conf(self.output, "str-sin303", dest, sources, self.root)
        self.assertEqual(dest.read_bytes(), self.fresh.read_bytes())
        self.assertNotEqual(dest.read_bytes(), self.old_conf.read_bytes())
        self.assertTrue(report["original_bytes_preserved"])

    def test_stale_override_never_falls_back_to_original(self):
        sources = self.root / "sources.json"
        sources.write_text(json.dumps({"overrides": {"str-sin303": {"file": str(self.fresh), "sha256": "0" * 64}}}))
        with self.assertRaises(tool.SkillError):
            tool.export_conf(self.current, "str-sin303", self.output, sources, self.root)
        self.assertFalse(self.output.exists())

    def test_export_legacy_source_without_registering_new_key(self):
        report = tool.export_conf(self.current, "str-sin303", self.output, original_dir=self.root)
        self.assertEqual(self.output.read_bytes(), self.old_conf.read_bytes())
        self.assertFalse(report["new_key_registered_by_this_tool"])

    def make_manifest(self):
        url = "https://example.invalid/private-secret/strongvpn.yaml"
        value = {"mode": "unified", "url": url, "path": "/private-secret/strongvpn.yaml",
                 "file": str(self.current), "sha256": tool.sha(self.current.read_bytes())}
        path = self.root / "manifest.json"
        path.write_text(json.dumps(value))
        return path, value

    def test_curl_uses_stdin_and_verified_tls_without_leaking_error(self):
        _, value = self.make_manifest()
        seen = {}
        def fail(args, **kwargs):
            seen.update(args=args, input=kwargs["input"])
            return subprocess.CompletedProcess(args, 60, b"", value["url"].encode())
        with patch.object(tool.subprocess, "run", side_effect=fail):
            with self.assertRaises(tool.SkillError) as error:
                tool.native_fetch(value["url"], "GET")
        self.assertNotIn(value["url"], str(error.exception))
        self.assertNotIn(value["url"], " ".join(seen["args"]))
        self.assertIn(value["url"].encode(), seen["input"])
        self.assertNotIn("--insecure", seen["args"])
        self.assertEqual(seen["args"][1], "--disable")

    def test_mirror_mismatch_stops_before_network(self):
        path, value = self.make_manifest()
        value["url"] = "https://example.invalid/another-secret/strongvpn.yaml"
        mirror = self.root / "mirror.json"
        mirror.write_text(json.dumps(value))
        with patch.object(tool, "native_fetch") as fetch:
            with self.assertRaises(tool.SkillError):
                tool.verify_subscription(path, mirror, transport="curl")
            fetch.assert_not_called()

    def test_http_hash_or_private_header_mismatch_is_failure(self):
        path, _ = self.make_manifest()
        for responses in ([(200, b"stale")], [(200, self.current.read_bytes()), (200, b"Content-Type: text/yaml\n")]):
            with self.subTest(response_count=len(responses)), patch.object(tool, "native_fetch", side_effect=responses):
                with self.assertRaises(tool.SkillError):
                    tool.verify_subscription(path, transport="curl")

    def test_good_verified_response_reports_only_safe_summary(self):
        path, value = self.make_manifest()
        head = b"HTTP/2 200\r\nCache-Control: private, no-store\r\nContent-Type: text/yaml\r\nReferrer-Policy: no-referrer\r\nX-Content-Type-Options: nosniff\r\nX-Robots-Tag: noindex\r\n"
        with patch.object(tool, "native_fetch", side_effect=[(200, self.current.read_bytes()), (200, head)]):
            result = tool.verify_subscription(path, transport="curl")
        self.assertTrue(result["tls_verified"])
        self.assertEqual(result["node_count"], 2)
        self.assertFalse(result["remote_mutation"])
        self.assertNotIn(value["url"], json.dumps(result))
        self.assertNotIn(key(1), json.dumps(result))

    def test_explicit_candidate_verification_keeps_manifests_untouched(self):
        path, _ = self.make_manifest()
        before = path.read_bytes()
        tool.prepare_replacement(self.current, "str-sin303", self.fresh, self.output)
        head = b"Cache-Control: private, no-store\nContent-Type: text/yaml\nReferrer-Policy: no-referrer\nX-Content-Type-Options: nosniff\nX-Robots-Tag: noindex\n"
        with patch.object(tool, "native_fetch", side_effect=[(200, self.output.read_bytes()), (200, head)]):
            result = tool.verify_subscription(path, expected_file=self.output, transport="curl")
        self.assertEqual(result["sha256"], tool.sha(self.output.read_bytes()))
        self.assertEqual(path.read_bytes(), before)

    def test_cli_errors_do_not_echo_config_contents(self):
        self.fresh.write_text(conf(extra="PostUp = sensitive-command\n"))
        output = io.StringIO()
        with contextlib.redirect_stderr(output):
            result = tool.main(["prepare-replacement", "--current", str(self.current), "--node", "str-sin303",
                                "--conf", str(self.fresh), "--output", str(self.output)])
        self.assertEqual(result, 1)
        self.assertNotIn(key(3), output.getvalue())
        self.assertNotIn("sensitive-command", output.getvalue())


if __name__ == "__main__":
    unittest.main()
