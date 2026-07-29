#!/usr/bin/env python3
"""Collect a bounded, anonymized summary from the internal content-square API."""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
from datetime import datetime
from pathlib import Path


ENDPOINT = "https://edith.xiaohongshu.com/api/pgy_outside/content_square/search_note_v2"
QUERIES = [
    "人类十大天赋",
    "天赋测试",
    "优势测试",
    "个人说明书",
    "恋爱人格测试",
    "依恋型人格",
    "MBTI测试",
    "职业天赋测试",
    "高敏感测试",
    "情绪测试",
    "隐藏人格测试",
    "审美人格测试",
    "SBTI测试",
    "心理测试",
    "恋爱测试",
    "爱情观测试",
    "原生家庭测试",
    "边界感测试",
    "社交人格测试",
    "动物人格测试",
    "精神状态测试",
    "内耗测试",
    "AI天赋",
    "职业性格测试",
]


def number(value: object) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def collect(cookie: str, query: str, page_size: int) -> dict:
    payload = json.dumps(
        {
            "searchWord": query,
            "pageSize": page_size,
            "pageNum": 1,
            "platform": 5,
            "bizType": "1",
            "orderBy": "premium_imp_num",
            "nd": "7",
            "sort": "desc",
        },
        ensure_ascii=False,
    ).encode("utf-8")
    try:
        completed = subprocess.run(
            [
                "curl",
                "-fsS",
                "--max-time",
                "25",
                "-H",
                f"Cookie: {cookie}",
                "-H",
                "Content-Type: application/json",
                "-H",
                "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
                "-X",
                "POST",
                ENDPOINT,
                "--data-binary",
                "@-",
            ],
            input=payload,
            capture_output=True,
            check=True,
            timeout=30,
        )
        result = json.loads(completed.stdout)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        raise RuntimeError(f"{query}: request failed ({type(exc).__name__})") from exc
    if result.get("code") != 0:
        raise RuntimeError(f"{query}: code={result.get('code')} msg={result.get('msg')}")

    data = result.get("data") or {}
    notes = []
    for item in data.get("noteList") or []:
        note = item.get("noteInfo") or {}
        notes.append(
            {
                "note_id": str(note.get("noteId") or ""),
                "title": str(note.get("title") or "无标题").strip(),
                "publish_time": note.get("notePublishTime"),
                "read": number(note.get("readNum")),
                "like": number(note.get("likeNum")),
                "fav": number(note.get("favNum")),
                "comment": number(note.get("cmtNum")),
                "is_ad": bool(note.get("isAdNote")),
            }
        )

    def median(field: str) -> int:
        return round(statistics.median([n[field] for n in notes])) if notes else 0

    def p90(field: str) -> int:
        if not notes:
            return 0
        values = sorted(n[field] for n in notes)
        return values[min(len(values) - 1, max(0, int(len(values) * 0.9) - 1))]

    ranked = sorted(notes, key=lambda n: (n["read"], n["like"] + n["fav"] + n["comment"]), reverse=True)
    return {
        "query": query,
        "api_total": number(data.get("total")),
        "returned": len(notes),
        "unique_notes": len({n["note_id"] for n in notes if n["note_id"]}),
        "median_read": median("read"),
        "p90_read": p90("read"),
        "max_read": max((n["read"] for n in notes), default=0),
        "median_like": median("like"),
        "median_fav": median("fav"),
        "median_comment": median("comment"),
        "ad_count": sum(n["is_ad"] for n in notes),
        "top_notes": ranked[:3],
        "notes": notes,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("cookie_file", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--page-size", type=int, default=50)
    args = parser.parse_args()

    cookie = args.cookie_file.read_text(encoding="utf-8").strip()
    if not cookie:
        raise SystemExit("Cookie file is empty")
    results = [collect(cookie, query, args.page_size) for query in QUERIES]

    note_to_queries: dict[str, list[str]] = {}
    for result in results:
        for note in result["notes"]:
            if note["note_id"]:
                note_to_queries.setdefault(note["note_id"], []).append(result["query"])
    overlap_notes = {note_id: queries for note_id, queries in note_to_queries.items() if len(queries) > 1}

    output = {
        "collected_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "window_days": 7,
        "order_by": "premium_imp_num",
        "page_size": args.page_size,
        "query_count": len(QUERIES),
        "unique_note_count": len(note_to_queries),
        "overlap_note_count": len(overlap_notes),
        "results": results,
    }
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
