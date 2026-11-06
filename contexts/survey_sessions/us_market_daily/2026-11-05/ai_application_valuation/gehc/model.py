#!/usr/bin/env python3
"""GEHC research valuation, USD millions except per-share values. No trading."""
from pathlib import Path
import json, csv, math

HERE = Path(__file__).resolve().parent

FACTS = {
    "asof_session": "2026-11-04", "currency": "USD", "price": 85.81,
    "previous_close": 80.66, "actual_shares_m_oct21": 452.137831,
    "diluted_shares_m_q3": 453, "diluted_shares_m_9m": 455,
    "revenue_q3": 5513, "revenue_q3_2025": 5143,
    "revenue_9m": 15939, "revenue_9m_2025": 14927,
    "gaap_eps_q3": 1.36, "adjusted_eps_q3": 1.34,
    "gaap_eps_9m": 3.44, "adjusted_eps_9m": 3.46,
    "gaap_eps_fy2025": 4.55, "gaap_eps_9m2025": 3.26,
    "adjusted_eps_fy2025": 4.59, "adjusted_eps_9m2025": 3.15,
    "guidance_adjusted_eps_low": 4.95, "guidance_adjusted_eps_high": 5.05,
    "guidance_fcf_floor": 1600, "guidance_fcf_is_floor_not_point_estimate": True,
    "cfo_q3": 907, "capex_q3": 114,
    "cfo_9m": 1365, "capex_9m": 392,
    "cfo_9m2025": 937, "capex_9m2025": 348,
    "cfo_fy2025": 1987, "capex_fy2025": 482,
    "sbc_9m": 116, "sbc_9m2025": 94, "sbc_fy2025": 130,
    "net_interest_9m": 332, "net_interest_9m2025": 335,
    "net_interest_fy2025": 440,
    "cash_interest_9m": 364, "cash_interest_9m2025": 327,
    "cash_interest_fy2025": 522,
    "cash_tariff_refunds_q3": 55, "cash_tariff_refunds_9m": 162,
    "pnl_prior_year_tariff_refund_q3": 9,
    "pnl_prior_year_tariff_refund_9m": 115,
    "pnl_current_year_tariff_refund_q3": 4,
    "pnl_current_year_tariff_refund_9m": 27,
    "restructuring_9m": 92, "acquisition_costs_9m": 57,
    "unrestricted_cash_sep30": 2826,
    "short_restricted_cash_sep30": 28, "long_restricted_cash_sep30": 3,
    "borrowing_book_sep30": 9973,
    "borrowing_principal_sep30": 10162,
    "redeemable_nci_book": 234, "nci_book": 17,
    "known_noncurrent_finance_lease": 52,
    "operating_lease_liabilities": 382,
    "pension_cash_9m": 243, "pension_cash_2026_expected": 350,
    "pending_sofie_cash_price": 945,
    "intelerad_cash_acquisition_mar18": 2293,
    "inventories_cf_9m": -430, "contract_deferred_assets_cf_9m": -265,
}

# All below are analyst assumptions, not management forecasts or market consensus.
ASSUMPTIONS = {
    "normalized_tax": 0.205,
    "restructuring_integration_recurring_fraction": 1.0,
    "normalization_sbc_treated_as_owner_cost": True,
    "refund_cash_deduction_is_gross_conservative_proxy": True,
    "debt_for_dcf": "principal (not book fair-value-hedge carrying amount)",
    "nci_value_proxy": "book amount, fair value not separately disclosed",
    "finance_lease_deduction": 52,
    "scenarios": [
        {"id": "conservative", "label": "保守", "eps_forward": 4.4, "pe": 14,
         "fcff_year1": 1650, "fcff_growth_years2_5": .04, "wacc": .095, "terminal_growth": .02},
        {"id": "base", "label": "基准", "eps_forward": 5.0, "pe": 18,
         "fcff_year1": 2000, "fcff_growth_years2_5": .07, "wacc": .085, "terminal_growth": .025},
        {"id": "optimistic", "label": "乐观", "eps_forward": 5.4, "pe": 21,
         "fcff_year1": 2400, "fcff_growth_years2_5": .10, "wacc": .08, "terminal_growth": .03},
    ],
    "dcf_year1_definition": "next 12 months from 2026-11-04; later years are consecutive 12-month periods",
    "eps_definition": "forward normalized annual earning power around 2027, not official 2027 guidance",
    "cash_interest_limitation": "Net financing expense is used as an unlevering proxy; cash net interest is not separately reconciled. See sensitivity.",
    "no_scheduled_debt_repayment_or_cash_balance_double_count": True,
    "pension_and_operating_lease_cash_costs_remain_in_fcff": True,
    "pending_sofie_excluded_from_both_price_and_cashflows": True,
}

def dcf(first, growth, wacc, terminal_growth, bridge, shares):
    assert wacc > terminal_growth
    fs = [first * (1 + growth) ** i for i in range(5)]
    pvs = [x / (1 + wacc) ** (i + 1) for i, x in enumerate(fs)]
    terminal = fs[-1] * (1 + terminal_growth) / (wacc - terminal_growth)
    terminal_pv = terminal / (1 + wacc) ** 5
    ev = sum(pvs) + terminal_pv
    eq = ev - bridge
    return {"fcff": fs, "fcff_pv": pvs, "terminal_value": terminal,
            "terminal_value_pv": terminal_pv, "enterprise_value": ev,
            "equity_value": eq, "value_per_share": eq / shares,
            "terminal_pv_share_of_ev": terminal_pv / ev}

def build():
    f, a = FACTS, ASSUMPTIONS
    market_cap = f['price'] * f['actual_shares_m_oct21']
    ttm_cfo = f['cfo_fy2025'] + f['cfo_9m'] - f['cfo_9m2025']
    ttm_capex = f['capex_fy2025'] + f['capex_9m'] - f['capex_9m2025']
    ttm_fcf = ttm_cfo - ttm_capex
    ttm_sbc = f['sbc_fy2025'] + f['sbc_9m'] - f['sbc_9m2025']
    ttm_interest = f['net_interest_fy2025'] + f['net_interest_9m'] - f['net_interest_9m2025']
    ttm_cash_interest = f['cash_interest_fy2025'] + f['cash_interest_9m'] - f['cash_interest_9m2025']
    owner_fcf = ttm_fcf - f['cash_tariff_refunds_9m'] - ttm_sbc
    fcff_proxy = owner_fcf + ttm_interest * (1 - a['normalized_tax'])
    net_debt_book = f['borrowing_book_sep30'] - f['unrestricted_cash_sep30']
    net_debt_principal = f['borrowing_principal_sep30'] - f['unrestricted_cash_sep30']
    bridge = net_debt_principal + f['redeemable_nci_book'] + f['nci_book'] + a['finance_lease_deduction']
    eps_mid = (f['guidance_adjusted_eps_low'] + f['guidance_adjusted_eps_high']) / 2
    expense_haircut = (f['restructuring_9m'] + f['acquisition_costs_9m']) * 4 / 3 * (1-a['normalized_tax']) / f['diluted_shares_m_9m']
    current_refund_haircut = f['pnl_current_year_tariff_refund_9m'] * (1-a['normalized_tax']) / f['diluted_shares_m_9m']
    result = {
      "schema_version": 1, "facts": f, "assumptions": a,
      "derived": {
        "day_change_pct": (f['price']/f['previous_close']-1)*100,
        "market_cap": market_cap, "net_debt_book": net_debt_book,
        "net_debt_principal": net_debt_principal, "enterprise_to_equity_deduction": bridge,
        "ttm_cfo": ttm_cfo, "ttm_capex": ttm_capex, "ttm_fcf": ttm_fcf,
        "ttm_sbc": ttm_sbc, "ttm_net_financial_expense": ttm_interest,
        "ttm_cash_interest_gross": ttm_cash_interest,
        "owner_fcf_after_refunds_and_sbc": owner_fcf,
        "normalized_fcff_anchor_proxy": fcff_proxy,
        "reported_ttm_fcf_yield_pct": ttm_fcf/market_cap*100,
        "normalized_owner_fcf_yield_pct": owner_fcf/market_cap*100,
        "fy_guidance_fcf_floor_yield_pct": f['guidance_fcf_floor']/market_cap*100,
        "adjusted_2026_pe_at_guidance_mid": f['price']/eps_mid,
        "gaap_ttm_eps_sum_proxy": f['gaap_eps_fy2025']+f['gaap_eps_9m']-f['gaap_eps_9m2025'],
        "adjusted_ttm_eps_sum_proxy": f['adjusted_eps_fy2025']+f['adjusted_eps_9m']-f['adjusted_eps_9m2025'],
        "normalization_eps_restructuring_integration_haircut": expense_haircut,
        "normalization_eps_current_refund_haircut": current_refund_haircut,
        "normalized_2026_eps_anchor": eps_mid-expense_haircut-current_refund_haircut,
        "pending_sofie_cash_only_downside_per_share": f['pending_sofie_cash_price']/f['diluted_shares_m_q3'],
      }, "scenarios": []}
    for s in a['scenarios']:
        x=dict(s); x['eps_multiple_value']=s['eps_forward']*s['pe']
        x['eps_value_upside_pct']=(x['eps_multiple_value']/f['price']-1)*100
        x['dcf']=dcf(s['fcff_year1'],s['fcff_growth_years2_5'],s['wacc'],s['terminal_growth'],bridge,f['diluted_shares_m_q3'])
        x['dcf_value_upside_pct']=(x['dcf']['value_per_share']/f['price']-1)*100
        x['eps_20pct_value_discount']=x['eps_multiple_value']*.8
        x['dcf_20pct_value_discount']=x['dcf']['value_per_share']*.8
        result['scenarios'].append(x)
    base=a['scenarios'][1]
    sens=[]
    for w in [.075,.08,.085,.09,.095]:
      for tg in [.02,.025,.03]:
        x=dcf(base['fcff_year1'],base['fcff_growth_years2_5'],w,tg,bridge,f['diluted_shares_m_q3'])
        sens.append({"wacc":w,"terminal_growth":tg,"price":x['value_per_share']})
    result['dcf_sensitivity']=sens
    # Solve forward FCFF needed for observed price under all other base assumptions.
    unit_ev=dcf(1,base['fcff_growth_years2_5'],base['wacc'],base['terminal_growth'],0,1)['enterprise_value']
    result['derived']['required_year1_fcff_at_price_base_assumptions']=(f['price']*f['diluted_shares_m_q3']+bridge)/unit_ev
    result['derived']['dcf_value_change_for_100m_year1_fcff']=100*unit_ev/f['diluted_shares_m_q3']
    assert math.isclose(ttm_fcf,1889)
    assert math.isclose(ttm_sbc,152)
    assert math.isclose(net_debt_book,7147)
    assert math.isclose(fcff_proxy,1922.415)
    return result

if __name__ == '__main__':
    result=build()
    (HERE/'valuation_model.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    with (HERE/'valuation_scenarios.csv').open('w') as fp:
      wr=csv.writer(fp); wr.writerow(['scenario','forward_eps','pe','eps_value','first_year_fcff_usdm','growth','wacc','terminal_growth','dcf_value','eps_value_discount20','dcf_value_discount20'])
      for x in result['scenarios']:
        wr.writerow([x['label'],x['eps_forward'],x['pe'],x['eps_multiple_value'],x['fcff_year1'],x['fcff_growth_years2_5'],x['wacc'],x['terminal_growth'],x['dcf']['value_per_share'],x['eps_20pct_value_discount'],x['dcf_20pct_value_discount']])
    print(json.dumps({'derived':result['derived'],'scenarios':result['scenarios']},ensure_ascii=False,indent=2))
