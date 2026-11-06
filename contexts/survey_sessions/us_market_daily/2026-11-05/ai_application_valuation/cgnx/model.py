"""Cognex: reproducible conditional valuation; USD millions except per-share values.

Owner cash flow deducts SBC economically. Routine future dilution is therefore
not charged a second time. RealSense is kept outside standalone operating FCF.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
FACTS = {
    "report_period_end": "2026-10-04", "release_date": "2026-11-04",
    "regular_session": "2026-11-04", "regular_close_usd": 53.06,
    "revenue_9m": 873.087, "cfo_9m": 220.661, "capex_9m": 6.928,
    "sbc_9m": 34.291, "investment_income_9m": 13.285,
    "cash": 694.695, "current_investments": 0.997,
    "noncurrent_investments": 150.292, "interest_bearing_debt": 0,
    "diluted_shares_q3": 171.027, "actual_shares_oct4": 168.372,
    "fy2026_adjusted_eps_guidance": [1.68, 1.72],
    "realsense_announced_purchase_price": 500,
    "realsense_contingent_cash_retention_3y": 56.5,
    "realsense_additional_rsu_value": 50,
}

ASSUMPTIONS = {
    "conservative": {"core_owner_fcf0": 205, "growth_years_1_5": .06, "growth_years_6_10": .04, "discount_rate": .11, "terminal_growth": .025, "realsense_value_sensitivity": 250},
    "base": {"core_owner_fcf0": 225, "growth_years_1_5": .10, "growth_years_6_10": .05, "discount_rate": .10, "terminal_growth": .03, "realsense_value_sensitivity": 500},
    "optimistic": {"core_owner_fcf0": 250, "growth_years_1_5": .15, "growth_years_6_10": .08, "discount_rate": .095, "terminal_growth": .035, "realsense_value_sensitivity": 750},
}

def calculate(a):
    fcf = a["core_owner_fcf0"]
    flows = []
    for t in range(1, 11):
        fcf *= 1 + a["growth_years_1_5" if t <= 5 else "growth_years_6_10"]
        flows.append({"year": t, "fcf": fcf, "present_value": fcf / (1 + a["discount_rate"]) ** t})
    terminal = fcf * (1 + a["terminal_growth"]) / (a["discount_rate"] - a["terminal_growth"]) / (1 + a["discount_rate"]) ** 10
    core_value = sum(x["present_value"] for x in flows) + terminal
    cash = sum(FACTS[k] for k in ["cash", "current_investments", "noncurrent_investments"])
    capital_bridge = cash - 500 - 56.5 - 50 + a["realsense_value_sensitivity"]
    price = (core_value + capital_bridge) / FACTS["diluted_shares_q3"]
    return {"assumptions": a, "annual_cash_flows": flows, "standalone_operating_value": core_value,
            "terminal_present_value_fraction": terminal/core_value, "capital_bridge": capital_bridge,
            "fair_value_per_share": price, "twenty_percent_discount_price": price*.8,
            "current_discount_to_fair_value_pct": (1-FACTS["regular_close_usd"]/price)*100}

if __name__ == "__main__":
    f = FACTS
    core_anchor = ((f["cfo_9m"]-f["capex_9m"]-f["sbc_9m"])-f["investment_income_9m"]*.8)*4/3
    result = {
        "schema_version": 1, "symbol": "CGNX", "unit": "USD millions except per-share values",
        "facts": FACTS, "annualized_core_owner_fcf_anchor": core_anchor,
        "anchor_note": "9m annualization is only a normalization anchor, not a company forecast; 20% tax haircut on investment income is a model assumption.",
        "scenarios": {k: calculate(a) for k,a in ASSUMPTIONS.items()},
        "method": "Ten-year standalone owner-FCF DCF plus cash and a separate announced acquisition capital bridge. No claim that RealSense has independently verified 250/500/750m value.",
        "safety_margin_definition": "20% below conditional fair value, not a maximum-loss guarantee. Base-discount and conservative-discount prices must be distinguished.",
        "caveats": [
            "RealSense had not been confirmed closed. Target profitability is undisclosed; 0.5/1/1.5x purchase-price target values are explicit transaction-value sensitivities, not independent appraisals.",
            "Entire 56.5m conditional three-year cash retention and 50m RSU cost are charged upfront conservatively; do not also add RSU shares. RSU vesting duration not verified.",
            "Routine SBC remains in adjusted EPS; do not deduct SBC again from the EPS multiple comparison.",
            "Operating leases remain operating costs; no extra lease-debt deduction in this cash-flow convention.",
            "Full Q3 10-Q not yet in freshly read SEC submissions; Q3 financial release is published. Working capital, acquisition allocation and call commentary remain pending.",
            "The postmarket Yahoo 50.99 at 19:13:19 EST and StockAnalysis 50.60 at 19:56 EST differ in time; Yahoo volume is zero and is an indicative bar, not verified last trade.",
        ],
        "sources": [
            "https://www.prnewswire.com/news-releases/cognex-reports-third-quarter-2026-results-302929644.html",
            "https://investor.cognex.com/news/news-details/2026/Cognex-to-Acquire-RealSense-Expanding-Machine-Vision-Leadership-into-High-Growth-Robotic-Perception-Market/default.aspx",
            "https://data.sec.gov/submissions/CIK0000851205.json",
            "https://stockanalysis.com/stocks/cgnx/history/",
        ]
    }
    assert abs(core_anchor-225.0853333333)<.0001
    prices=[x["fair_value_per_share"] for x in result["scenarios"].values()]
    assert prices == sorted(prices)
    (HERE/"valuation.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({k:{"fair":round(v["fair_value_per_share"],2),"discount20":round(v["twenty_percent_discount_price"],2)} for k,v in result["scenarios"].items()}))
