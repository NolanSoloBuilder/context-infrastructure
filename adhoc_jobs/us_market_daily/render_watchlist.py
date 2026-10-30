"""Build one categorized observation table from dated prices and reviewed notes."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from collect import OBSERVATION_GROUPS, WATCH


def cell(value):
    return str(value).replace("|", "／").replace("\n", " ")


def build(out, report_date, next_session, premarket_status):
    metrics = {r["symbol"]: r for r in json.loads((out / "metrics.json").read_text())}
    session = metrics["QQQM"]["session"]
    if any(r["session"] != session for r in metrics.values()):
        raise ValueError("Regular market metrics contain mixed sessions")
    extended_path = out / "extended_quotes.json"
    extended = json.loads(extended_path.read_text()) if extended_path.exists() else {}
    quotes = {r["symbol"]: r for r in extended.get("observations", [])}
    verified_path = out / "extended_verification.json"
    verified = json.loads(verified_path.read_text()) if verified_path.exists() else {}
    overrides = {r["symbol"]: r for r in verified.get("rows", [])} if verified.get("quote_session_us") == session else {}
    research_path = out / "watchlist_research.json"
    research = json.loads(research_path.read_text()) if research_path.exists() else {}
    records, rows = [], []
    for number, group in enumerate(OBSERVATION_GROUPS, 1):
        for index, asset in enumerate(group["assets"]):
            symbol = asset["symbol"]
            m = metrics.get(symbol)
            label = "BRK.B" if symbol == "BRK-B" else symbol
            category = f"**{number:02d} {group['label']}**" if index == 0 else ""
            symbol_cell = f"**{label}** · {asset['name']}"
            regular = f"{m['close']:.2f}（{m['day_pct']:+.2f}%）" if m else "缺失"
            drawdown = f"{-m['drawdown_pct']:.2f}%" if m and m.get('drawdown_pct') is not None else "不足52周／缺失"
            levels = f"{m['level_15']:.2f} / {m['level_25']:.2f}" if m and symbol in WATCH else "未设置"
            note = research.get(symbol, {})
            judgment = note.get("status", "估值待完成") + "；" + note.get("next", "补核最新经营与估值分母")
            quote = quotes.get(symbol, {})
            post = quote.get("post", {})
            override = overrides.get(symbol)
            post_record = None
            if override and override.get("regular_close_usd") == (m or {}).get("close"):
                post_record = {"price_usd": override["afterhours_display_usd"],
                               "change_pct": override["afterhours_change_vs_same_regular_pct"],
                               "time_beijing": override["display_quote_time_beijing"],
                               "time_et": override["display_quote_time_et"],
                               "source_url": override["source_url"], "source": "Stock Analysis dated after-hours",
                               "verification_file": "extended_verification.json"}
            elif post.get("status") == "available" and post.get("session") == session:
                stamp = datetime.fromisoformat(post["bar_start_et"])
                # An isolated16:00bar may be the regular closing auction. Do not
                # present that boundary observation as a valid latest post quote.
                if (stamp.hour, stamp.minute) > (16, 0):
                    post_record = {"price_usd": post["price_usd"], "change_pct": post["change_vs_reference_pct"],
                                   "time_beijing": post["bar_start_beijing"], "time_et": post["bar_start_et"],
                                   "source_url": quote["source_url"], "source": "Yahoo minute reference, single-source",
                                   "zero_or_missing_volume": not post.get("bar_has_positive_volume", False)}
            if post_record:
                t = datetime.fromisoformat(post_record["time_beijing"])
                post_cell = f"[{post_record['price_usd']:.2f}（{post_record['change_pct']:+.2f}%）]({post_record['source_url']}) · 北京{t:%m/%d %H:%M}"
            else:
                post_cell = "未取得有效报价"
            if premarket_status == "not_started":
                pre_cell, pre_record = "尚未开始", {"status": "not_started", "session": next_session}
            else:
                pre_record = quote.get("pre", {})
                if pre_record.get("status") == "available" and pre_record.get("session") == next_session:
                    t = datetime.fromisoformat(pre_record["bar_start_beijing"])
                    pre_cell = f"[{pre_record['price_usd']:.2f}（{pre_record['change_vs_reference_pct']:+.2f}%）]({quote['source_url']}) · 北京{t:%m/%d %H:%M}"
                else:
                    pre_cell = "缺失"
            rows.append("| " + " | ".join(cell(v) for v in [category, symbol_cell, regular, pre_cell, post_cell, drawdown, levels, judgment]) + " |")
            records.append({"group_id": group["id"], "group": group["label"], "symbol": symbol, "name": asset["name"],
                            "regular_metrics": m, "pre": pre_record, "post": post_record,
                            "has_original_drawdown_alert": symbol in WATCH, "reviewed_research": note})
    header = ["分类", "标的／定位", f"{session[5:]}收盘／当日", f"{next_session[5:]}盘前", f"{session[5:]}盘后参考／时间", "常规收盘距52周高点回撤", "15% / 25%观察价", "研究判断／下一条件"]
    table = "| " + " | ".join(header) + " |\n| " + " | ".join(["---"] * len(header)) + " |\n" + "\n".join(rows)
    text = f"""**分类观察总表**

按重点指数ETF → 机器人 → AI／半导体 → 金融科技排列；伯克希尔与SGOV另列价值、现金管理。当前共{len(records)}项，每个标的只归入一个主类别。纳斯达克100保留QQQM，QQQ已从当前清单移除。

收盘及回撤采用美东 **{session}** 常规时段，报价均为美元。盘前列对应 **{next_session}**；本版盘前状态为{'尚未开始' if premarket_status == 'not_started' else '按实际报价更新'}，上一交易日历史盘前放在[时段详情](./extended_detail.md)。盘后每行附自身北京时间，美东时间和来源见[总表数据](./watchlist_table.json)。盘前相对之前最近一次常规收盘、盘后相对同日常规收盘。

{table}

研究状态表达当前结论，不代表持仓或已批准交易；15%/25%观察价只保留QQQM、VOO、BRK.B三项。其他行的“未设置”不等于没有风险。盘后无有效报价写缺失，不用收盘填充；单源分钟价格与零量延续报价仅作参考，来源差异见[盘后核验](./extended_verification.json)。SGOV的价格回撤受派息影响，不能按股票跌幅解释。

"""
    payload = {"schema_version": 1, "report_date_beijing": report_date, "regular_session": session,
               "premarket_session": next_session, "premarket_status": premarket_status,
               "generated_at_utc": datetime.now(timezone.utc).isoformat(), "rows": records,
               "group_registry": "adhoc_jobs/us_market_daily/watchlist_groups.json"}
    (out / "watchlist_table.md").write_text(text)
    (out / "watchlist_table.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    return payload


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--next-session", required=True, help="Exchange-calendar verified US session, not guessed")
    parser.add_argument("--premarket-status", choices=["not_started", "read_quotes"], required=True)
    args = parser.parse_args()
    result = build(args.out, args.report_date, args.next_session, args.premarket_status)
    print(json.dumps({"rows": len(result["rows"]), "groups": len(OBSERVATION_GROUPS)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
