#!/usr/bin/env python3
"""Collect a bounded internal XHS signal set for parent-reported child assessments."""

from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import datetime
from pathlib import Path


QUERIES = [
    "儿童性格测试",
    "孩子性格测试",
    "儿童天赋测试",
    "孩子天赋测试",
    "儿童优势测试",
    "孩子优势测评",
    "儿童气质测试",
    "亲子关系测试",
    "家庭教育测评",
    "多元智能测评",
    "学习力测评",
    "孩子学习方式测试",
    "儿童心理测评",
    "青少年心理测评",
    "儿童注意力测评",
]


def load_collector(path: Path):
    spec = importlib.util.spec_from_file_location("xhs_signal_collector", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load collector: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("cookie_file", type=Path)
    parser.add_argument("base_collector", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--page-size", type=int, default=50)
    args = parser.parse_args()

    cookie = args.cookie_file.read_text(encoding="utf-8").strip()
    if not cookie:
        raise SystemExit("Cookie file is empty")
    collector = load_collector(args.base_collector)
    results = [collector.collect(cookie, query, args.page_size) for query in QUERIES]

    all_ids = {
        note["note_id"]
        for result in results
        for note in result["notes"]
        if note["note_id"]
    }
    output = {
        "collected_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "window_days": 7,
        "order_by": "premium_imp_num",
        "page_size": args.page_size,
        "query_count": len(QUERIES),
        "unique_note_count": len(all_ids),
        "results": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
