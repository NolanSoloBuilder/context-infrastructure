"""Render saved daily observations. No interpolation or generated market history."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager, ticker
import numpy as np
import pandas as pd

from collect import SECTORS

FONT = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
font_manager.fontManager.addfont(FONT)
plt.rcParams.update({
    "font.family": font_manager.FontProperties(fname=FONT).get_name(),
    "font.size": 12, "axes.unicode_minus": False, "savefig.dpi": 160,
    "axes.edgecolor": "#DCE2EB", "text.color": "#20304A",
    "xtick.color": "#68768D", "ytick.color": "#68768D",
})
COLORS = {"QQQM": "#4D6BE8", "VOO": "#148B83", "BRK-B": "#BA8125"}
LABELS = {"QQQM": "QQQM · 纳斯达克100", "VOO": "VOO · 标普500", "BRK-B": "BRK.B · 伯克希尔"}
BG = "#F5F7FB"


def style(ax):
    ax.set_facecolor("white")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#E8ECF2", linewidth=.7)
    ax.set_axisbelow(True)
    ax.tick_params(length=0, pad=9)


def save(fig, out, name):
    for suffix in ["png", "svg"]:
        fig.savefig(out / f"{name}.{suffix}", facecolor=BG)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--report-date", required=True)
    args = parser.parse_args()
    out = args.out
    metrics = {row["symbol"]: row for row in json.loads((out / "metrics.json").read_text())}
    asof = metrics["QQQM"]["session"]
    data = {s: pd.read_csv(out / f"{s}_daily.csv", index_col="date", parse_dates=True).tail(60) for s in COLORS}
    dates = data["QQQM"].index
    assert len(dates) == 60
    assert all(df.index.equals(dates) for df in data.values()), "Chart dates must align exactly"
    assert all(df.index[0] > pd.Timestamp(asof) - pd.Timedelta(days=150) for df in data.values())
    positions = [0, 14, 29, 44, 59]
    ticks = [dates[i].strftime("%m/%d") for i in positions]
    x = np.arange(60)

    fig = plt.figure(figsize=(13.4, 10.4), facecolor=BG)
    fig.text(.075, .951, "美股观察日报", fontsize=25, weight="bold")
    fig.text(.925, .953, args.report_date, fontsize=18, ha="right", color="#68768D")
    fig.text(.075, .914, f"美东 {asof} 常规收盘  /  空仓观察  /  价格数据不含分红再投资", fontsize=12, color="#68768D")
    fig.text(.075, .866, "01   近 60 个交易日走势", fontsize=17, weight="bold")
    fig.text(.075, .835, f"{dates[0]:%Y/%m/%d} — {dates[-1]:%Y/%m/%d}  ·  首日价格统一为 100", fontsize=11, color="#68768D")
    ax = fig.add_axes([.085, .537, .82, .272])
    style(ax)
    normalized = {}
    for s, df in data.items():
        y = df.close / df.close.iloc[0] * 100
        normalized[s] = float(y.iloc[-1])
        ax.plot(x, y, color=COLORS[s], linewidth=2.3, label=LABELS[s])
        ax.scatter([59], [y.iloc[-1]], color=COLORS[s], s=30, zorder=4)
    # Keep terminal labels separated even when the time series finish near each other.
    ordered = sorted(normalized, key=normalized.get)
    value_range = max(df.close.max() / df.close.iloc[0] * 100 for df in data.values()) - min(df.close.min() / df.close.iloc[0] * 100 for df in data.values())
    gap = max(value_range * .075, .7)
    labels_y = {}
    for s in ordered:
        labels_y[s] = max(normalized[s], max(labels_y.values(), default=-1000) + gap)
    for s in ordered:
        label = f"{'BRK.B' if s == 'BRK-B' else s}  {normalized[s]-100:+.1f}%"
        ax.annotate(label, (59, normalized[s]), (61, labels_y[s]), textcoords="data", fontsize=11,
                    color=COLORS[s], va="center", arrowprops={"arrowstyle": "-", "color": COLORS[s], "lw": .8})
    ax.axhline(100, color="#A8B2C1", linewidth=.8, linestyle=(0, (3, 3)))
    ax.set_xlim(0, 75)
    ymin, ymax = ax.get_ylim()
    ax.set_ylim(ymin, max(ymax, max(labels_y.values()) + gap))
    ax.set_xticks(positions, ticks)
    ax.yaxis.set_major_locator(ticker.MaxNLocator(5))
    ax.legend(loc="upper left", frameon=False, fontsize=11, ncol=3)

    fig.text(.075, .459, "02   距各自 52 周高点的回撤", fontsize=17, weight="bold")
    fig.text(.075, .428, "高点随当时可见行情滚动更新；虚线是观察条件，不能证明已见底", fontsize=11, color="#68768D")
    ax = fig.add_axes([.085, .126, .82, .278])
    style(ax)
    ax.axhspan(-25, -15, color="#FDF1E1", alpha=.75)
    for s, df in data.items():
        y = df.drawdown_pct
        ax.plot(x, y, color=COLORS[s], linewidth=2.3)
        ax.scatter([59], [y.iloc[-1]], color=COLORS[s], s=30, zorder=4)
    # Collision-aware terminal labels; relative order follows current actual drawdowns.
    previous = -1000
    for s in sorted(data, key=lambda k: float(data[k].drawdown_pct.iloc[-1])):
        value = float(data[s].drawdown_pct.iloc[-1])
        label_y = max(value, previous + 2.6)
        previous = label_y
        ax.annotate(f"{'BRK.B' if s == 'BRK-B' else s}  {value:.2f}%", (59, value), (61, label_y),
                    textcoords="data", fontsize=11, color=COLORS[s], va="center",
                    arrowprops={"arrowstyle": "-", "color": COLORS[s], "lw": .8})
    for level, label in [(-15, "−15%  第一观察档"), (-25, "−25%  第二观察档")]:
        ax.axhline(level, color="#B88443", linewidth=1, linestyle=(0, (5, 4)))
        ax.text(74, level + .65, label, ha="right", va="bottom", color="#996A31", fontsize=11)
    ax.set_xlim(0, 75)
    ax.set_ylim(-27, 2)
    ax.set_xticks(positions, ticks)
    ax.set_yticks([0, -5, -10, -15, -20, -25], ["0%", "−5%", "−10%", "−15%", "−20%", "−25%"])
    fig.text(.075, .066, "数据：Yahoo Finance 日线；最新收盘已与 Stock Analysis 交叉核对。", fontsize=10, color="#68768D")
    fig.text(.075, .041, "QQQ / QQQM 跟踪相同指数，曲线展示 QQQM。回撤以盘中高点计算；所有指标截至标注日期。", fontsize=10, color="#68768D")
    save(fig, out, "watchlist_curves")

    fig = plt.figure(figsize=(13.4, 7.4), facecolor=BG)
    fig.text(.075, .93, "03   行业表现", fontsize=23, weight="bold")
    fig.text(.925, .936, f"{asof} · 单日", fontsize=14, ha="right", color="#68768D")
    fig.text(.075, .884, "11 个行业 ETF ＋ 半导体专题  ·  价格涨跌不代表资金净流入", fontsize=12, color="#68768D")
    rows = sorted([metrics[s] for s in SECTORS], key=lambda r: r["day_pct"], reverse=True)
    ax = fig.add_axes([.205, .15, .66, .68])
    style(ax)
    ax.grid(False, axis="y")
    ax.grid(True, axis="x", color="#E8ECF2", linewidth=.7)
    y = np.arange(len(rows))
    values = [r["day_pct"] for r in rows]
    colors = ["#148B83" if v >= 0 else "#D66359" for v in values]
    ax.barh(y, values, color=colors, height=.58, zorder=3)
    ax.axvline(0, color="#A2ACBB", lw=1)
    for i, row in enumerate(rows):
        value = row["day_pct"]
        ax.text(value + (.13 if value >= 0 else -.13), i, f"{value:+.2f}%", va="center",
                ha="left" if value >= 0 else "right", color=colors[i], fontsize=12, weight="bold")
    ax.set_yticks(y, [f"{SECTORS[r['symbol']]}  {r['symbol']}" for r in rows], fontsize=12)
    ax.invert_yaxis()
    half_width = max(abs(v) for v in values) + 1.3
    ax.set_xlim(-half_width, half_width)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f"{v:g}%"))
    ax.spines[["left", "bottom"]].set_visible(False)
    fig.text(.075, .075, "数据：Yahoo Finance，同一常规交易日收盘价相对前一日收盘价。", fontsize=10, color="#68768D")
    fig.text(.075, .041, "SMH 为半导体细分行业，与 XLK 等持仓存在重叠；各 ETF 涨跌不能相加为整体市场收益。", fontsize=10, color="#68768D")
    save(fig, out, "sector_daily")
    pd.DataFrame({s: data[s].close / data[s].close.iloc[0] * 100 for s in data}).to_csv(out / "normalized_60_sessions.csv", float_format="%.6f")
    print(json.dumps({"period": [str(dates[0].date()), str(dates[-1].date())], "normalized_end": normalized,
                      "images": [str(out / "watchlist_curves.png"), str(out / "sector_daily.png")]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
