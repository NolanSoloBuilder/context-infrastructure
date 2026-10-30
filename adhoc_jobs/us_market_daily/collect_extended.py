"""Keep dated pre/post-market observations separate from regular daily bars.

Quotes are positive closes of one-minute provider bars, not consolidated
last-sale ticks. A zero volume may be a carried quote; disclose it and require
cross-checks before interpreting a move. Never change daily metrics or alerts.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import subprocess
from urllib.parse import quote
from zoneinfo import ZoneInfo


ET = ZoneInfo("America/New_York")
BJ = ZoneInfo("Asia/Shanghai")


def flatten_periods(value):
    if isinstance(value, dict):
        if "start" in value and "end" in value:
            yield value
        else:
            for child in value.values():
                yield from flatten_periods(child)
    elif isinstance(value, list):
        for child in value:
            yield from flatten_periods(child)


def latest_bar(result, session, segment, captured_at):
    periods = list(flatten_periods(result["meta"].get("tradingPeriods", {}).get(segment, [])))
    if session is None:
        started = [p for p in periods if p["start"] <= captured_at.timestamp()]
        if not started:
            return {"status": "not_started", "session": None, "segment": segment}
        session = datetime.fromtimestamp(max(started, key=lambda p: p["start"])["start"], ET).date().isoformat()
    intervals = [p for p in periods if datetime.fromtimestamp(p["start"], ET).date().isoformat() == session]
    if len(intervals) != 1:
        return {"status": "period_metadata_missing", "session": session, "segment": segment}
    period = intervals[0]
    rows = result["indicators"]["quote"][0]
    observations = []
    for i, stamp in enumerate(result.get("timestamp", [])):
        close = rows["close"][i]
        volume = rows.get("volume", [None] * len(result["timestamp"]))[i]
        if period["start"] <= stamp < period["end"] and stamp <= captured_at.timestamp():
            if close is not None and math.isfinite(close) and close > 0:
                observations.append((stamp, close, volume))
    if not observations:
        status = "not_started" if captured_at.timestamp() < period["start"] else "no_positive_price_bar"
        return {"status": status, "session": session, "segment": segment}
    stamp, close, volume = observations[-1]
    return {
        "status": "available", "session": session, "segment": segment,
        "price_usd": round(close, 2), "price_raw": close, "bar_start_unix": stamp,
        "bar_start_et": datetime.fromtimestamp(stamp, ET).isoformat(),
        "bar_start_beijing": datetime.fromtimestamp(stamp, BJ).isoformat(),
        "minute_volume": volume, "sampling": "latest positive close in provider 1-minute bars; indicative when volume is zero or missing",
        "bar_has_positive_volume": volume is not None and volume > 0,
        "session_window_ended_at_capture": captured_at.timestamp() >= period["end"],
    }


def collect_symbol(symbol, out, session, captured_at, raw_directory):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{quote(symbol, safe='')}?range=5d&interval=1m&includePrePost=true"
    base = {"symbol": symbol, "label": "BRK.B" if symbol == "BRK-B" else symbol,
            "currency": "USD", "source_url": url, "captured_at_utc": captured_at.isoformat()}
    try:
        payload = subprocess.run(["curl", "--silent", "--show-error", "--location", "--fail",
                                  "--max-time", "30", "-A", "Mozilla/5.0", url],
                                 capture_output=True, check=True).stdout
        raw_file = raw_directory / f"{symbol}.json"
        raw_file.write_bytes(payload)
        parsed = json.loads(payload)
        if parsed["chart"].get("error") or not parsed["chart"].get("result"):
            raise ValueError("Unusable chart result")
        result = parsed["chart"]["result"][0]
        if result["meta"].get("currency") != "USD" or result["meta"]["symbol"] != symbol:
            raise ValueError("Symbol or currency mismatch")
        # Baselines come from saved, dated regular bars; never use ambiguous full-day metadata.
        import csv
        with (out / f"{symbol}_daily.csv").open() as stream:
            daily = [r for r in csv.DictReader(stream) if r["date"] <= session]
        if len(daily) < 2 or daily[-1]["date"] != session:
            raise ValueError("Requested regular-session baseline missing")
        regular = float(daily[-1]["close"])
        previous = float(daily[-2]["close"])
        base.update(status="available", regular_session=session, regular_close_usd=round(regular, 2),
                    previous_regular_session=daily[-2]["date"], previous_regular_close_usd=round(previous, 2),
                    raw_file=str(raw_file.relative_to(out)), sha256=hashlib.sha256(payload).hexdigest())
        for segment in ["pre", "post"]:
            # A new day's premarket may have started while the last complete
            # regular session is still yesterday. The quote's own date decides
            # its benchmark, never the local report date or an assumed timezone.
            observation = latest_bar(result, None if segment == "pre" else session, segment, captured_at)
            if observation["status"] == "available":
                candidates = [r for r in daily if r["date"] < observation["session"]] if segment == "pre" else [r for r in daily if r["date"] == observation["session"]]
                if not candidates:
                    observation.update(status="benchmark_missing", change_vs_reference_pct=None)
                else:
                    reference = candidates[-1]
                    baseline = float(reference["close"])
                    observation.update(reference_close_usd=round(baseline, 2), reference_session=reference["date"],
                                       change_vs_reference_pct=(observation["price_raw"] / baseline - 1) * 100)
            base[segment] = observation
        return base
    except Exception as exc:
        return {**base, "status": "failed", "error": str(exc)}


def main():
    from collect import OBSERVATION_SYMBOLS, PORTFOLIO_SYMBOLS
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--asof", required=True, help="Latest completed regular US session, YYYY-MM-DD")
    args = parser.parse_args()
    captured_at = datetime.now(timezone.utc)
    datetime.strptime(args.asof, "%Y-%m-%d")
    raw_directory = args.out / "extended_raw" / captured_at.strftime("%Y%m%dT%H%M%SZ")
    raw_directory.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=3) as pool:
        symbols = list(dict.fromkeys(OBSERVATION_SYMBOLS + PORTFOLIO_SYMBOLS))
        observations = list(pool.map(lambda s: collect_symbol(s, args.out, args.asof, captured_at, raw_directory), symbols))
    report = {"schema_version": 1, "captured_at_utc": captured_at.isoformat(),
              "captured_at_beijing": captured_at.astimezone(BJ).isoformat(),
              "regular_asof_session": args.asof, "observations": observations,
              "method": {"regular": "Saved daily OHLC close, unchanged", "extended": "Latest positive 1-minute bar close within provider pre/post windows; zero/missing volume does not establish a new trade and must be disclosed",
                         "returns": "pre vs preceding regular close; post vs same-day regular close; do not add percentages",
                         "alerts": "Extended prices do not update the regular-close four-symbol alert state",
                         "scope": "No overnight 20:00-04:00 quotes; pre/post data are venue/provider snapshots, not guaranteed consolidated executable quotes"}}
    filename = raw_directory / "snapshot.json"
    filename.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    (args.out / "extended_quotes.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"snapshot": str(filename), "observations": observations}, ensure_ascii=False))
    if any(r["status"] != "available" for r in observations):
        raise SystemExit("Some extended observations failed; preserve and disclose missing values.")


if __name__ == "__main__":
    main()
