#!/usr/bin/env python3
"""Read-only audit of migrated skills using Codex's live skills/list response."""

import argparse
import json
import os
from pathlib import Path
import selectors
import subprocess
import sys
import time


def absolute_path(value):
    if not isinstance(value, str) or not os.path.isabs(value):
        raise ValueError("manifest 中的路径必须是绝对路径")
    return os.path.normpath(value)


def within(path, root):
    """Compare canonical paths, including symlinked project skill directories."""
    try:
        Path(path).resolve().relative_to(Path(root).resolve())
        return True
    except (ValueError, OSError, RuntimeError):
        return False


def load_manifest(path):
    manifest = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or not isinstance(manifest.get("entries"), list):
        raise ValueError("manifest 必须包含 entries 数组")
    entries = []
    for item in manifest["entries"]:
        if not isinstance(item, dict):
            raise ValueError("每个 entry 必须是对象")
        name = item.get("name")
        names = item.get("skillNames")
        if not isinstance(name, str) or not name:
            raise ValueError("每个 entry 必须包含非空 name")
        if not isinstance(names, list) or not names or any(
            not isinstance(value, str) or not value for value in names
        ):
            raise ValueError("每个 entry 必须包含非空 skillNames 数组")
        entry = {
            "name": name,
            "skillNames": list(dict.fromkeys(names)),
            "canonicalPath": absolute_path(item.get("canonicalPath")),
        }
        for key in ("globals", "targets"):
            if not isinstance(item.get(key), list):
                raise ValueError("每个 entry 必须包含 globals 和 targets 数组")
            entry[key] = list(dict.fromkeys(absolute_path(value) for value in item[key]))
        entries.append(entry)
    negative = manifest.get("negativeCwds", [])
    if not isinstance(negative, list):
        raise ValueError("negativeCwds 必须是数组")
    negative = list(dict.fromkeys(absolute_path(value) for value in negative))
    cwds = list(dict.fromkeys([cwd for entry in entries for cwd in entry["targets"]] + negative))
    if not entries or not cwds:
        raise ValueError("manifest 至少需要一个 entry 和一个待验证项目")
    return entries, negative, cwds


class AppServer:
    def __init__(self, timeout):
        self.timeout = timeout
        self.next_id = 0
        self.buffer = b""
        self.process = subprocess.Popen(
            ["codex", "app-server", "--stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        self.selector = selectors.DefaultSelector()
        self.selector.register(self.process.stdout, selectors.EVENT_READ)

    def send(self, message):
        self.process.stdin.write((json.dumps(message, ensure_ascii=False) + "\n").encode("utf-8"))
        self.process.stdin.flush()

    def request(self, method, params):
        self.next_id += 1
        request_id = self.next_id
        self.send({"id": request_id, "method": method, "params": params})
        deadline = time.monotonic() + self.timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("app-server 请求超时: " + method)
            if b"\n" not in self.buffer:
                if not self.selector.select(timeout=remaining):
                    raise TimeoutError("app-server 请求超时: " + method)
                chunk = os.read(self.process.stdout.fileno(), 65536)
                if not chunk:
                    raise RuntimeError("app-server 在请求完成前退出: " + method)
                self.buffer += chunk
                continue
            line, _, self.buffer = self.buffer.partition(b"\n")
            try:
                message = json.loads(line)
            except json.JSONDecodeError:
                raise RuntimeError("app-server 返回了非 JSON 协议数据") from None
            if not isinstance(message, dict) or message.get("id") != request_id:
                continue
            if "error" in message:
                # Never print server payloads: they may contain private configuration.
                code = message["error"].get("code") if isinstance(message["error"], dict) else None
                raise RuntimeError("app-server 请求失败: %s (code=%s)" % (method, code))
            if "result" not in message:
                raise RuntimeError("app-server 响应缺少 result: " + method)
            return message["result"]

    def close(self):
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=3)
        self.selector.close()
        self.process.stdin.close()
        self.process.stdout.close()


def related_error(path, entries):
    for entry in entries:
        roots = [entry["canonicalPath"]] + entry["globals"]
        for target in entry["targets"]:
            for name in [entry["name"]] + entry["skillNames"]:
                roots.extend(str(Path(target) / folder / name) for folder in (".agents/skills", ".codex/skills"))
        if any(within(path, root) for root in roots):
            return True
    return False


def audit(entries, negative_cwds, cwds, response):
    if not isinstance(response, dict) or not isinstance(response.get("data"), list):
        raise ValueError("skills/list 响应缺少 data 数组")
    migrated_names = {name for entry in entries for name in entry["skillNames"]}
    failures = []
    remaining_globals = sorted({
        path for entry in entries for path in entry["globals"]
        if Path(path).exists() or Path(path).is_symlink()
    })
    for path in remaining_globals:
        failures.append({"code": "global_entry_remains", "path": path})

    by_cwd = {}
    for item in response["data"]:
        if not isinstance(item, dict) or not isinstance(item.get("cwd"), str):
            raise ValueError("skills/list 项目缺少 cwd")
        key = str(Path(item["cwd"]).resolve())
        if key in by_cwd:
            raise ValueError("skills/list 返回了重复 cwd")
        by_cwd[key] = item

    projects = []
    load_errors = []
    for cwd in cwds:
        item = by_cwd.get(str(Path(cwd).resolve()))
        if item is None:
            failures.append({"code": "cwd_missing", "cwd": cwd})
            projects.append({"cwd": cwd, "missing": True})
            continue
        skills = item.get("skills")
        errors = item.get("errors")
        if not isinstance(skills, list) or not isinstance(errors, list):
            raise ValueError("skills/list 项目缺少 skills 或 errors 数组")
        if any(not isinstance(skill, dict) or not {"name", "scope", "enabled", "path"}.issubset(skill) for skill in skills):
            raise ValueError("skills/list 返回了不完整的 Skill metadata")
        enabled = [skill for skill in skills if skill["enabled"] is True]
        expected = {name for entry in entries if any(within(cwd, target) for target in entry["targets"]) for name in entry["skillNames"]}
        repo_names = {skill["name"] for skill in enabled if skill["scope"] == "repo"}
        missing = sorted(expected - repo_names)
        unexpected = sorted((repo_names & migrated_names) - expected)
        user_leaks = sorted({skill["name"] for skill in enabled if skill["scope"] == "user" and skill["name"] in migrated_names})
        negative_leaks = []
        if cwd in negative_cwds:
            allowed = {name for entry in entries if any(within(cwd, target) for target in entry["targets"]) for name in entry["skillNames"]}
            negative_leaks = sorted({skill["name"] for skill in skills if skill["name"] in migrated_names - allowed})
        for code, names in (("repo_skill_missing", missing), ("unexpected_repo_skill", unexpected), ("user_scope_leak", user_leaks), ("negative_cwd_leak", negative_leaks)):
            for name in names:
                failures.append({"code": code, "cwd": cwd, "skillName": name})
        related_count = 0
        for error in errors:
            if not isinstance(error, dict) or not isinstance(error.get("path"), str):
                raise ValueError("skills/list 返回了不完整的 Skill error")
            related = related_error(error["path"], entries)
            load_errors.append({"cwd": cwd, "path": error["path"], "related": related})
            if related:
                related_count += 1
                failures.append({"code": "migrated_skill_load_error", "cwd": cwd, "path": error["path"]})
        projects.append({
            "cwd": cwd,
            "total": len(skills),
            "enabled": len(enabled),
            "repoEnabled": sum(skill["scope"] == "repo" for skill in enabled),
            "userEnabled": sum(skill["scope"] == "user" for skill in enabled),
            "expectedRepo": len(expected),
            "foundExpectedRepo": len(expected - set(missing)),
            "unexpectedRepoSkills": unexpected,
            "userLeaks": user_leaks,
            "negativeLeaks": negative_leaks,
            "loadErrorCount": len(errors),
            "relatedLoadErrorCount": related_count,
        })
    return {
        "passed": not failures,
        "entryCount": len(entries),
        "migratedSkillCount": len(migrated_names),
        "projectCount": len(cwds),
        "remainingGlobals": remaining_globals,
        "projects": projects,
        "loadErrors": load_errors,
        "failures": failures,
    }


def print_summary(summary):
    for project in summary.get("projects", []):
        if project.get("missing"):
            print("项目 %s: 响应缺失" % project["cwd"])
            continue
        print("项目 %s: enabled=%d repo=%d user=%d 期望repo=%d/%d 全局泄漏=%d 私人项目泄漏=%d 加载错误=%d(相关=%d)" % (
            project["cwd"], project["enabled"], project["repoEnabled"], project["userEnabled"],
            project["foundExpectedRepo"], project["expectedRepo"], len(project["userLeaks"]),
            len(project["negativeLeaks"]), project["loadErrorCount"], project["relatedLoadErrorCount"],
        ))
    for error in summary.get("loadErrors", []):
        print("加载错误(%s): %s | %s" % ("迁移相关" if error["related"] else "无关，不阻塞", error["cwd"], error["path"]))
    for failure in summary.get("failures", []):
        print("失败: " + " | ".join(str(failure[key]) for key in ("code", "cwd", "skillName", "path") if key in failure))
    print("审计%s: %d 个项目，%d 个迁移 Skill，%d 个失败项" % (
        "通过" if summary["passed"] else "失败", summary.get("projectCount", 0),
        summary.get("migratedSkillCount", 0), len(summary.get("failures", [])),
    ))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, help="迁移清单 JSON")
    parser.add_argument("--output", help="保存原始 skills/list 响应和审计摘要")
    parser.add_argument("--timeout", type=float, default=60, help="每次 app-server 请求超时秒数，默认 60，最大 300")
    args = parser.parse_args()
    if not 0 < args.timeout <= 300:
        parser.error("--timeout 必须大于 0 且不超过 300")
    server = None
    response = None
    summary = None
    try:
        entries, negative, cwds = load_manifest(args.manifest)
        server = AppServer(args.timeout)
        server.request("initialize", {"clientInfo": {"name": "skill-scope-audit", "version": "1.0.0"}})
        server.send({"method": "initialized"})
        response = server.request("skills/list", {"cwds": cwds, "forceReload": True})
        summary = audit(entries, negative, cwds, response)
    except (OSError, ValueError, RuntimeError, TimeoutError) as error:
        summary = {"passed": False, "failures": [{"code": "audit_unavailable"}]}
        # Protocol errors are deliberately sanitized; manifest parser errors are local.
        print("审计错误: " + str(error))
    finally:
        if server is not None:
            try:
                server.close()
            except (OSError, subprocess.TimeoutExpired):
                summary["passed"] = False
                summary["failures"].append({"code": "app_server_cleanup_failed"})
    if args.output:
        try:
            Path(args.output).write_text(json.dumps({"skillsList": response, "summary": summary}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        except OSError:
            summary["passed"] = False
            summary["failures"].append({"code": "output_write_failed"})
    print_summary(summary)
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
