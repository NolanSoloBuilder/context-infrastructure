"""Reproducible scenario valuation; all forecasts are analyst assumptions, not prices."""
import argparse
import copy
import csv
import json
from pathlib import Path


def value(inputs, scenario):
    facts = inputs['facts']
    revenue = facts['ttm_revenue_B']
    margin0 = facts['ttm_ebit_B'] / revenue
    rows = []
    pv = 0.0
    for year in range(1, 11):
        previous = revenue
        growth = (scenario['growth_first5'] if year <= 5 else
                  scenario['growth_next5'] + (scenario['terminal_growth'] - scenario['growth_next5']) * (year - 6) / 4)
        revenue *= 1 + growth
        margin = margin0 + (scenario['mature_ebit_margin'] - margin0) * min(year / 5, 1)
        ebit = revenue * margin
        nopat = ebit * (1 - scenario['tax_rate'])
        da_ratio = scenario['da_revenue_ratios'][year - 1]
        da = revenue * da_ratio
        capex_ratio = scenario['capex_revenue_ratios'][year - 1]
        if capex_ratio is None:
            # Match the end of the forecast to growth / ROIC reinvestment.
            capex_ratio = (da_ratio + margin * (1 - scenario['tax_rate'])
                           * growth / scenario['terminal_roic']
                           - scenario['incremental_nwc_ratio'] * growth / (1 + growth))
        capex = revenue * capex_ratio
        nwc_change = scenario['incremental_nwc_ratio'] * (revenue - previous)
        fcff = nopat + da - capex - nwc_change
        discounted = fcff / (1 + scenario['wacc']) ** year
        pv += discounted
        rows.append(dict(year=year, revenue_growth=growth, revenue_B=revenue, ebit_margin=margin,
                         ebit_B=ebit, nopat_B=nopat, da_B=da, capex_B=capex,
                         nwc_change_B=nwc_change, fcff_B=fcff, pv_fcff_B=discounted))
    terminal_nopat = rows[-1]['nopat_B'] * (1 + scenario['terminal_growth'])
    terminal_fcff = terminal_nopat * (1 - scenario['terminal_growth'] / scenario['terminal_roic'])
    terminal_value = terminal_fcff / (scenario['wacc'] - scenario['terminal_growth'])
    pv_terminal = terminal_value / (1 + scenario['wacc']) ** 10
    enterprise = pv + pv_terminal
    bridge = (facts['non_equity_cash_and_bonds_B'] - scenario['operating_cash_reserve_B']
              + facts['market_equity_B'] * scenario['market_equity_retention']
              + facts['private_investments_B'] * scenario['private_investments_retention']
              - facts['interest_debt_B'] - facts['finance_lease_B']
              - facts['preferred_claim_B'] - facts['nci_proxy_B'])
    equity = enterprise + bridge
    per_share = equity / facts['current_common_shares_B']
    return dict(name=scenario['name'], price_usd=per_share,
                relative_to_close_pct=(per_share / facts['close_usd'] - 1) * 100,
                enterprise_value_B=enterprise, asset_bridge_B=bridge, equity_value_B=equity,
                pv_explicit_fcff_B=pv, pv_terminal_B=pv_terminal,
                terminal_share_enterprise_pct=pv_terminal / enterprise * 100,
                terminal_fcff_B=terminal_fcff,
                extra_10pct_share_dilution_price_usd=per_share / 1.1,
                forecast=rows, assumptions=scenario)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    inputs = json.loads((args.out / 'google_model_inputs.json').read_text())
    results = [value(inputs, scenario) for scenario in inputs['scenarios']]
    base = inputs['scenarios'][1]
    sensitivity = []
    for wacc in [.09, .095, .10, .105, .11]:
        for growth in [.02, .025, .03, .035]:
            test = copy.deepcopy(base)
            test.update(wacc=wacc, terminal_growth=growth)
            sensitivity.append(dict(wacc=wacc, terminal_growth=growth,
                                    price_usd=value(inputs, test)['price_usd']))
    faster = copy.deepcopy(base)
    faster.update(name='较快兑现检查', growth_first5=.20, growth_next5=.10)
    faster_result = value(inputs, faster)
    low, high = .01, .40
    for _ in range(80):
        guess = (low + high) / 2
        test = copy.deepcopy(base)
        test['growth_first5'] = guess
        if value(inputs, test)['price_usd'] < inputs['facts']['close_usd']:
            low = guess
        else:
            high = guess
    reverse = dict(required_first5_revenue_cagr=(low + high) / 2,
                   all_other_parameters='Hold baseline margin, capex ratios, year6 growth/taper to terminal, WACC, terminal ROIC and asset bridge fixed.')
    output = dict(inputs=inputs, scenarios=results, faster_execution_check=faster_result,
                  sensitivity=sensitivity, reverse_dcf=reverse)
    (args.out / 'google_valuation_model.json').write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n')
    with (args.out / 'google_forecast.csv').open('w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['scenario'] + list(results[0]['forecast'][0]))
        writer.writeheader()
        for result in results:
            writer.writerows(dict(scenario=result['name'], **row) for row in result['forecast'])
    print(json.dumps(dict(scenarios=[{k: r[k] for k in ['name', 'price_usd', 'terminal_share_enterprise_pct']} for r in results],
                          faster=faster_result['price_usd'], reverse=reverse), ensure_ascii=False))


if __name__ == '__main__':
    main()
