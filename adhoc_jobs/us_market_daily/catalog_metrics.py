"""Collect source-dated return/risk/trend metrics for reviewed watchlist cards.

No brokerage access; no synthetic OHLC or forward-filled dividends. Yahoo's
adjusted close is used as a split/dividend-adjusted total-return proxy. Close
is the provider's split-adjusted price series for moving-average comparisons.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import subprocess
from urllib.parse import quote

import pandas as pd


def number(value):
    return float(value) if value is not None and pd.notna(value) and math.isfinite(float(value)) else None


def process(symbol, asset, out, asof, captured_at):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{quote(symbol, safe='')}?range=2y&interval=1d&events=div%2Csplits&includeAdjustedClose=true"
    saved = out / "raw" / f"metrics_{symbol}_{captured_at:%Y%m%dT%H%M%SZ}.json"
    response = subprocess.run(["curl", "--silent", "--show-error", "--fail", "--location", "--max-time", "35", "--retry", "1", "-A", "Mozilla/5.0", url], check=True, capture_output=True).stdout
    saved.write_bytes(response)
    decoded = json.loads(response)
    if decoded["chart"].get("error") or not decoded["chart"].get("result"):
        raise ValueError("Unusable chart result")
    result = decoded["chart"]["result"][0]
    if result["meta"].get("symbol") != symbol or result["meta"].get("currency") != "USD":
        raise ValueError("Symbol or currency mismatch")
    dates = pd.to_datetime(result["timestamp"], unit="s", utc=True).tz_convert("America/New_York").tz_localize(None).normalize()
    bars = result["indicators"]["quote"][0]
    df = pd.DataFrame({"close": bars["close"], "high": bars["high"], "low": bars["low"], "volume": bars["volume"]}, index=dates).rename_axis("date")
    adjustment = result["indicators"].get("adjclose", [{}])[0].get("adjclose")
    df["adjclose"] = adjustment if adjustment is not None else float("nan")
    df = df.loc[df.index <= asof]
    df = df.dropna(subset=["close"])
    if len(df) < 2 or not df.index.is_monotonic_increasing or df.index.has_duplicates or (df.close <= 0).any():
        raise ValueError("Invalid or insufficient daily close history")
    latest = df.index[-1]
    gaps = []
    if latest != asof:
        gaps.append(f"完整日线截至{latest.date()}，落后请求日{asof.date()}；本卡收益、风险与均线只按实际日线计算，未将收盘快照拼入历史。")
    # Exactly one calendar year, with the last actual close on/before the
    # anniversary as the starting observation. No 252-session approximation.
    anniversary = latest - pd.DateOffset(years=1)
    earlier = df.loc[df.index <= anniversary]
    inception_text = asset.get("inception_date") or asset.get("facts", {}).get("inception_date")
    inception = pd.Timestamp(inception_text) if inception_text else None
    if len(earlier):
        start = earlier.index[-1]
        period_label = "近一年"
        complete_year = True
    elif inception is not None and df.index[0] <= inception + pd.Timedelta(days=7):
        start = df.index[0]
        period_label = "成立以来"
        complete_year = False
        gaps.append(f"成立不足一年：从{start.date()}首个有效收盘起计算累计回报，波动率仍按日收益年化；不是实际一年收益。")
    else:
        start = df.index[0]
        period_label = "可用区间"
        complete_year = False
        gaps.append("历史不足一年且无法核验成立日覆盖，仅展示可用区间指标，不称近一年或成立以来。")
    window = df.loc[start:latest]
    dividends = result.get("events", {}).get("dividends", {})
    splits = result.get("events", {}).get("splits", {})
    window_dividends = [event for event in dividends.values() if start <= pd.Timestamp(event["date"], unit="s", tz="UTC").tz_convert("America/New_York").tz_localize(None).normalize() <= latest]
    adjusted_ok = bool(window.adjclose.notna().all() and (window.adjclose > 0).all())
    if adjusted_ok and window_dividends and float((window.adjclose / window.close).max() - (window.adjclose / window.close).min()) < 1e-7:
        adjusted_ok = False
        gaps.append("提供方列出窗口内分红，但Adj Close/Close比例没有变化，无法确认分红调整，降级为价格回报。")
    if adjusted_ok:
        wealth = window.adjclose
        return_basis = "Yahoo Adj Close分红/拆股复权总回报代理（税前，非个人账户实际回报）"
    else:
        wealth = window.close
        return_basis = "价格回报（未确认现金分红再投资）"
        gaps.append("Adj Close不完整或未通过分红调整检查；收益、波动和最大回撤使用价格序列降级，不能当总回报。")
    daily = wealth.pct_change().dropna()
    extreme_jumps = [{"date": str(date.date()), "return_pct": float(value * 100)} for date, value in daily.items() if abs(value) > .5]
    quality_status = "provider_series_calculation_checked"
    quality_sources = []
    if extreme_jumps:
        overrides_path = out / "metrics_quality_overrides.json"
        overrides = json.loads(overrides_path.read_text()) if overrides_path.exists() else {}
        override = overrides.get(symbol, {})
        verified_dates = set(override.get("crosschecked_jump_dates", []))
        if all(j["date"] in verified_dates for j in extreme_jumps):
            quality_status = "outlier_cross_source_price_checked"
            quality_sources = override.get("sources", [])
            gaps.append("窗口包含已核对第二网页价格的极端单日变化；年化波动率受该事件显著影响，不代表未来预期波动。不同网页可能共享行情供应商。")
        else:
            quality_status = "outlier_pending_verification"
            gaps.append("窗口含超过50%的单日变化，仍需核对第二来源与公司行为；保留数值供审计，页面应标待核并退出收益排序。")
    running_high = wealth.cummax()
    drawdown = (wealth / running_high - 1) * 100
    trough = drawdown.idxmin()
    peak = wealth.loc[:trough].idxmax()
    trailing = df.loc[df.index > latest - pd.Timedelta(days=364)]
    full_high_window = df.index[0] <= latest - pd.Timedelta(days=364)
    high = number(trailing.high.max()) if full_high_window else None
    high_date = str(trailing.high.idxmax().date()) if full_high_window and high else None
    ma50 = number(df.close.iloc[-50:].mean()) if len(df) >= 50 else None
    ma200 = number(df.close.iloc[-200:].mean()) if len(df) >= 200 else None
    if ma200 is None:
        gaps.append(f"仅{len(df)}个有效收盘，不足200交易日；200日均线及偏离留空。")
    split_checks = []
    for event in splits.values():
        event_date = pd.Timestamp(event["date"], unit="s", tz="UTC").tz_convert("America/New_York").tz_localize(None).normalize()
        before = df.loc[df.index < event_date]
        after = df.loc[df.index >= event_date]
        check = {"date": str(event_date.date()), "split_ratio": event.get("splitRatio"), "source_event": event}
        if len(before) and len(after):
            ratio = float(after.close.iloc[0] / before.close.iloc[-1])
            check["close_ratio_across_event"] = ratio
            split_multiple = float(event.get("numerator", 1)) / float(event.get("denominator", 1))
            # This detects a visible unadjusted split discontinuity. It does not
            # independently audit every historical price or corporate action.
            if split_multiple != 1 and abs(math.log(ratio * split_multiple)) < abs(math.log(ratio)) and abs(math.log(ratio)) > .5:
                gaps.append(f"{event_date.date()}拆股附近价格可能未统一调整，均线与价格位置待复核。")
                check["status"] = "possible_unadjusted_discontinuity"
            else:
                check["status"] = "no_split_sized_discontinuity_detected"
        else:
            check["status"] = "outside_available_close_history"
        split_checks.append(check)
    price_return = float((window.close.iloc[-1] / window.close.iloc[0] - 1) * 100)
    spark = df.loc[df.index <= latest].iloc[-60:]
    spark_basis = "分红/拆股复权" if adjusted_ok and spark.adjclose.notna().all() and (spark.adjclose > 0).all() else "仅价格"
    spark_values = spark.adjclose if spark_basis == "分红/拆股复权" else spark.close
    summary = {
        "symbol": symbol, "requested_asof": str(asof.date()), "asof_session": str(latest.date()),
        "period_label": period_label, "period_start": str(start.date()), "period_end": str(latest.date()),
        "complete_year": complete_year, "period_bars": len(window), "bars": len(df),
        "return_pct": float((wealth.iloc[-1] / wealth.iloc[0] - 1) * 100), "return_basis": return_basis,
        "price_return_pct": price_return, "return_adjustment_status": "adjusted_close" if adjusted_ok else "price_only_downgrade",
        "annualized_volatility_pct": number(daily.std(ddof=1) * math.sqrt(252) * 100),
        "quality_status": quality_status, "extreme_daily_moves": extreme_jumps, "quality_sources": quality_sources,
        "max_drawdown_pct": float(drawdown.min()), "max_drawdown_peak_date": str(peak.date()), "max_drawdown_trough_date": str(trough.date()),
        "current_drawdown_pct": float(drawdown.iloc[-1]), "current_drawdown_basis": "同一回报窗口的复权收盘历史高点；区别于52周盘中高点",
        "price_drawdown_52w_pct": float((df.close.iloc[-1] / high - 1) * 100) if high else None,
        "high_52w": high, "high_date": high_date, "close": float(df.close.iloc[-1]),
        "ma50": ma50, "ma200": ma200,
        "vs_ma50_pct": float((df.close.iloc[-1] / ma50 - 1) * 100) if ma50 else None,
        "vs_ma200_pct": float((df.close.iloc[-1] / ma200 - 1) * 100) if ma200 else None,
        "lag_calendar_days": (asof - latest).days,
        "window_dividend_count": len(window_dividends), "adjustment_ratio_start": float(window.adjclose.iloc[0] / window.close.iloc[0]) if adjusted_ok else None,
        "adjustment_ratio_end": float(window.adjclose.iloc[-1] / window.close.iloc[-1]) if adjusted_ok else None,
        "split_checks": split_checks, "split_price_basis": "提供方Close为拆股调整历史价；事件跨日检查仅排除明显拆股级跳变，未逐笔审计。",
        "sparkline": [{"date": str(date.date()), "value": float(value / spark_values.iloc[0] * 100)} for date, value in spark_values.items()],
        "sparkline_basis": spark_basis, "sparkline_bars": len(spark),
        "source_url": url, "raw_file": str(saved.relative_to(out)), "captured_at_utc": captured_at.isoformat(),
        "raw_sha256": hashlib.sha256(response).hexdigest(), "gaps": gaps,
    }
    df["return_proxy"] = df.adjclose if adjusted_ok else df.close
    df.to_csv(out / f"metrics_{symbol}_daily.csv", float_format="%.10f")
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--asof", required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "raw").mkdir(exist_ok=True)
    catalog = json.loads(args.catalog.read_text())
    assets = {a["symbol"]: a for g in catalog["groups"] for a in g["assets"]}
    captured = datetime.now(timezone.utc)
    symbols, errors = {}, []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(process, symbol, asset, args.out, pd.Timestamp(args.asof), captured): symbol for symbol, asset in assets.items()}
        for future in as_completed(futures):
            symbol = futures[future]
            try:
                symbols[symbol] = future.result()
                m = symbols[symbol]
                print(f"{symbol}: {m['asof_session']} {m['period_label']} {m['return_pct']:+.2f}% vol {m['annualized_volatility_pct']:.2f}% MDD {m['max_drawdown_pct']:.2f}%", flush=True)
            except Exception as exc:
                error = {"symbol": symbol, "error": str(exc)}
                errors.append(error)
                symbols[symbol] = {"symbol": symbol, "requested_asof": args.asof, "asof_session": None, "status": "unavailable", "gaps": [str(exc)]}
                print(f"ERROR {symbol}: {exc}", flush=True)
    payload = {
        "schema_version": 1, "requested_asof": args.asof, "captured_at_utc": captured.isoformat(),
        "method": {
            "return": "Adj Close(end)/Adj Close(start)-1; split/dividend-adjusted tax-before return proxy; no personal commissions or taxes",
            "window": "End is latest actual valid daily close on/before requested asof; start is last session on/before one calendar year earlier; young funds use first available inception close",
            "volatility": "sample standard deviation (ddof=1) of simple daily return proxy * sqrt(252), expressed in percent",
            "max_drawdown": "minimum of 100*(return_proxy/running_max(return_proxy)-1) within same return window; closing observations only, no lookahead",
            "moving_averages": "50/200 latest available split-adjusted provider Close observations; missing if insufficient; not dividend-adjusted",
            "drawdown_52w": "latest Close vs max intraday High in trailing 364 calendar days; missing without full window; separate from maximum drawdown",
            "provider_adjustment_documentation": "https://in.help.yahoo.com/kb/adjusted-close-sln28256.html",
        },
        "symbols": dict(sorted(symbols.items())), "errors": errors,
    }
    (args.out / "risk_metrics.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    scalar_keys = ["symbol", "requested_asof", "asof_session", "period_label", "period_start", "period_end", "period_bars", "return_pct", "price_return_pct", "annualized_volatility_pct", "max_drawdown_pct", "price_drawdown_52w_pct", "ma50", "ma200", "vs_ma50_pct", "vs_ma200_pct", "return_adjustment_status", "quality_status", "source_url"]
    pd.DataFrame([{key: m.get(key) for key in scalar_keys} for m in sorted(symbols.values(), key=lambda row: row["symbol"])]).to_csv(args.out / "risk_metrics.csv", index=False, float_format="%.8f")
    manifest = {"captured_at_utc": captured.isoformat(), "requested_asof": args.asof, "symbols": [{k: m.get(k) for k in ["symbol", "asof_session", "source_url", "raw_file", "raw_sha256", "return_adjustment_status", "lag_calendar_days"]} for m in symbols.values()], "errors": errors}
    (args.out / "risk_metrics_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    if errors:
        raise SystemExit("Some metrics unavailable; retain rows and disclose gaps.")


if __name__ == "__main__":
    main()
