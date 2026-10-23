"""Fetch public daily bars, retain evidence, and calculate dated watchlist metrics."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json
from pathlib import Path
import subprocess
from urllib.parse import quote

import pandas as pd

WATCH = ["QQQ", "QQQM", "VOO", "BRK-B"]
SECTORS = {
    "XLK": "科技", "XLC": "通信服务", "XLY": "可选消费", "XLP": "必需消费",
    "XLV": "医疗", "XLF": "金融", "XLI": "工业", "XLE": "能源",
    "XLU": "公用事业", "XLB": "原材料", "XLRE": "房地产", "SMH": "半导体",
}
INDICES = {"^GSPC": "标普500", "^IXIC": "纳斯达克综合", "^NDX": "纳斯达克100", "^VIX": "VIX"}


def money(value: float, factor: str = "1") -> float:
    # First restore quoted prices to cents; then multiply using decimal arithmetic.
    cents = Decimal(str(round(value, 2)))
    return float((cents * Decimal(factor)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def collect(ticker: str, out: Path, asof: pd.Timestamp, refresh: bool):
    slug = ticker.replace("^", "index_")
    raw = out / "raw" / f"{slug}.json"
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{quote(ticker, safe='')}?range=2y&interval=1d&events=div%2Csplits"
    if refresh or not raw.exists():
        payload = subprocess.run(
            ["curl", "--silent", "--show-error", "--location", "--fail", "--max-time", "35",
             "--retry", "1", "-A", "Mozilla/5.0", url],
            check=True, capture_output=True,
        ).stdout
        parsed = json.loads(payload)
        if parsed["chart"].get("error") or not parsed["chart"].get("result"):
            raise ValueError(f"{ticker}: unusable chart response")
        raw.write_bytes(payload)
    parsed = json.loads(raw.read_bytes())
    result = parsed["chart"]["result"][0]
    quotes = result["indicators"]["quote"][0]
    dates = pd.to_datetime(result["timestamp"], unit="s", utc=True).tz_convert("America/New_York").tz_localize(None).normalize()
    df = pd.DataFrame(quotes, index=dates).rename_axis("date")
    df = df.loc[df.index <= asof, ["open", "high", "low", "close", "volume"]].dropna(subset=["open", "high", "low", "close"])
    if df.index.has_duplicates or not df.index.is_monotonic_increasing:
        raise ValueError(f"{ticker}: duplicate or unordered dates")
    if len(df) < 320 or df.index[-1] != asof:
        raise ValueError(f"{ticker}: incomplete history ({len(df)} bars, latest {df.index[-1]})")
    valid_ohlc = (df.high >= df[["open", "close", "low"]].max(axis=1) - 0.001) & (df.low <= df[["open", "close", "high"]].min(axis=1) + 0.001) & (df.low > 0)
    if not valid_ohlc.all():
        raise ValueError(f"{ticker}: inconsistent OHLC")
    # A trailing 364-calendar-day window, (date - 364 days, date]. Never look ahead.
    df["high_52w"] = df.high.rolling("364D", closed="right").max()
    df["drawdown_pct"] = (df.close / df.high_52w - 1) * 100
    df["ma50"] = df.close.rolling(50).mean()
    df["ma200"] = df.close.rolling(200).mean()
    df["volume_vs_prior20"] = df.volume / df.volume.shift(1).rolling(20).mean()
    df.to_csv(out / f"{slug}_daily.csv", float_format="%.8f")
    latest = df.iloc[-1]
    window = df.loc[df.index > asof - pd.Timedelta(days=364)]
    hi = float(latest.high_52w)
    summary = {
        "symbol": ticker, "label": "BRK.B" if ticker == "BRK-B" else INDICES.get(ticker, SECTORS.get(ticker, ticker)),
        "session": str(asof.date()), "close": money(latest.close),
        "day_pct": float((latest.close / df.close.iloc[-2] - 1) * 100),
        "five_session_pct": float((latest.close / df.close.iloc[-6] - 1) * 100),
        "twenty_one_session_pct": float((latest.close / df.close.iloc[-22] - 1) * 100),
        "high_52w": money(hi), "high_date": str(window.high.idxmax().date()),
        "drawdown_pct": float(latest.drawdown_pct), "level_15": money(hi, ".85"), "level_25": money(hi, ".75"),
        "additional_drop_to_15_pct": float((hi * .85 / latest.close - 1) * 100),
        "ma50": float(latest.ma50), "ma200": float(latest.ma200),
        "vs_ma50_pct": float((latest.close / latest.ma50 - 1) * 100),
        "vs_ma200_pct": float((latest.close / latest.ma200 - 1) * 100),
        "volume": int(latest.volume), "volume_vs_prior20": None if pd.isna(latest.volume_vs_prior20) else float(latest.volume_vs_prior20),
        "bars": len(df), "source_url": url,
    }
    source = {"symbol": ticker, "url": url, "raw_file": str(raw.name), "sha256": hashlib.sha256(raw.read_bytes()).hexdigest(),
              "file_saved_utc": datetime.fromtimestamp(raw.stat().st_mtime, timezone.utc).isoformat(),
              "first_session": str(df.index[0].date()), "last_session": str(df.index[-1].date()),
              "bars": len(df), "currency": result["meta"].get("currency"), "splits": result.get("events", {}).get("splits", {})}
    return summary, source


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--asof", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    (args.out / "raw").mkdir(parents=True, exist_ok=True)
    asof = pd.Timestamp(args.asof)
    summaries, sources, errors = [], [], []
    with ThreadPoolExecutor(max_workers=4) as pool:
        jobs = {pool.submit(collect, ticker, args.out, asof, args.refresh): ticker for ticker in WATCH + list(SECTORS) + list(INDICES) + ["SGOV"]}
        for job in as_completed(jobs):
            ticker = jobs[job]
            try:
                summary, source = job.result()
                summaries.append(summary)
                sources.append(source)
                print(f"{ticker}: {summary['close']:.2f} {summary['day_pct']:+.2f}% ({summary['bars']} bars)", flush=True)
            except Exception as exc:
                errors.append({"symbol": ticker, "error": str(exc)})
                print(f"ERROR {ticker}: {exc}", flush=True)
    manifest = {"asof_session": args.asof, "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                "method": {"prices": "Yahoo daily OHLC close; split-adjusted provider series, not dividend-reinvested total returns",
                           "drawdown": "100*(close / max(high in (date-364 calendar days,date]) - 1)",
                           "volume_baseline": "20 preceding sessions, excluding report session",
                           "screening_levels": "52-week intraday high * .85 / .75, cents rounded half-up; observation only"},
                "sources": sorted(sources, key=lambda row: row["symbol"]), "errors": errors}
    (args.out / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    (args.out / "metrics.json").write_text(json.dumps(sorted(summaries, key=lambda row: row["symbol"]), indent=2, ensure_ascii=False, allow_nan=False) + "\n")
    pd.DataFrame(summaries).sort_values("symbol").to_csv(args.out / "metrics.csv", index=False, float_format="%.6f")
    if errors:
        raise SystemExit("Some symbols could not be verified; inspect manifest.json before charting.")


if __name__ == "__main__":
    main()
