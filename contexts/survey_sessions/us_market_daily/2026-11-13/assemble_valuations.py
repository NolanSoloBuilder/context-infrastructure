from pathlib import Path
import json
from urllib.parse import urlparse

here = Path(__file__).resolve().parent
seed_path = here.parents[3] / "adhoc_jobs/us_market_site/worker/seed.json"
files = {
    "core": "INTC SNDK SKHY ATS RRX SOFI GOOGL NVDA",
    "funds": "IGV XSW IHI BOTZ AIQ",
    "industry": "MRNA ISRG TEM BA TSLA SPCX BRK-B",
    "software": "AMZN MSFT AAPL PLTR ACN EPAM GLOB",
}
models = {}
for name, symbols in files.items():
    rows = json.loads((here / f"valuation_{name}.json").read_text())
    assert set(rows) == set(symbols.split()), (name, list(rows))
    models.update(rows)
for symbol, model in models.items():
    assert all(model.get(k) for k in ("judgment", "basis", "next", "reviewed_at", "market_session", "sources")), symbol
    assert all(urlparse(s["url"]).scheme == "https" for s in model["sources"]), symbol
    for k in ("base_value", "discount_price"):
        assert model.get(k) is None or isinstance(model[k], (int,float)) and model[k]>0, (symbol,k)
seed = json.loads(seed_path.read_text())
assets = {a["symbol"]: a for group in seed["catalog"]["groups"] for a in group["assets"]}
assert len(assets) == 43
for symbol, model in models.items():
    assets[symbol]["valuation"] = model
    assets[symbol]["research_status"] = model["judgment"]
remaining = [
    a["symbol"] for a in assets.values()
    if not a.get("valuation") and any(term in a.get("research_status","") for term in ("研究候选","估值待完成"))
]
assert not remaining, remaining
encoded = json.dumps(seed,ensure_ascii=False,indent=2,allow_nan=False)+"\n"
assert all(term not in encoded for term in ("portfolio_private","我的持仓","账户号"))
seed_path.write_text(encoded)
(here/"valuation_review_all.json").write_text(json.dumps(models,ensure_ascii=False,indent=2,allow_nan=False)+"\n")
print(f"Updated {len(models)} models across {len(assets)} public watchlist cards.")

def price(value):
    return "—" if value is None else f"${value:,.2f}"

lines = [
    "# 美股观察台估值复核", "",
    "价格基准为美东 2026-11-12 常规收盘。估值倍数、增长、折扣和汇率情景均为研究假设。",
    "ETF 数值为组合情景参考现值。空白价格表示证据不足以给出可用的每股估值。", "",
    "| 标的 | 基准或情景参考 | 压力 | 折扣研究价 | 判断 |",
    "|---|---:|---:|---:|---|",
]
for symbol, model in models.items():
    lines.append(f"| {symbol} | {price(model.get('base_value'))} | {price(model.get('stress_value'))} | {price(model.get('discount_price'))} | {model['judgment']} |")
for symbol, model in models.items():
    lines.extend(["", f"## {symbol}", "", model["basis"], "", model["next"], ""])
    lines.extend(f"- [{s['title']}]({s['url']})" for s in model["sources"])
(here/"valuation_review_all.md").write_text("\n".join(lines)+"\n")
