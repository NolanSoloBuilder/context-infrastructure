"""2026-11-10 official-disclosure research. All financial inputs are USD millions.

Run from any directory; writes only sibling research JSON. The inputs below were
read from CoreWeave's furnished 8-K Exhibit 99.1, not a completed 10-Q. No valuation
target or portfolio instruction is produced.
"""
from datetime import datetime, timezone
from pathlib import Path
import json

OUT = Path(__file__).resolve().parent
SOURCE = 'https://www.sec.gov/Archives/edgar/data/1769628/000176962826000461/coreweave3q26earningspress.htm'
inputs = {
    'revenue_q3_2026': 3661, 'revenue_q3_2025': 1365,
    'gaap_operating_income_q3': 207, 'net_interest_expense_q3': 846,
    'net_loss_q3': -709, 'adjusted_ebitda_q3': 2256,
    'depreciation_amortization_q3': 1889, 'sbc_q3': 160,
    'cfo_q3': 1975, 'cash_ppe_software_q3': 9441,
    'cashflow_change_deferred_revenue_q3': 2127,
    'cashflow_change_accounts_receivable_q3': -1741,
    'investing_cashflow_q3': -9836, 'financing_cashflow_q3': 7361,
    'cash_restricted_cash_change_q3': -500,
    'recourse_debt_current': 9183, 'recourse_debt_noncurrent': 32417,
    'nonrecourse_debt_current': 1389, 'nonrecourse_debt_noncurrent': 3884,
    'cash_cash_equivalents': 4122, 'marketable_securities': 62,
    'restricted_cash_current': 1405, 'restricted_cash_noncurrent': 877,
    'finance_lease_current': 296, 'finance_lease_noncurrent': 353,
    'operating_lease_current': 668, 'operating_lease_noncurrent': 18029,
    'revenue_guidance_fy2026_low': 13000, 'revenue_guidance_fy2026_high': 13300,
    'capex_guidance_fy2026_low': 37000, 'capex_guidance_fy2026_high': 39000,
    'expected_next_three_months_prepayments_deposits': 9000,
    'revenue_backlog': 132500,
}
i = inputs
fcf = i['cfo_q3'] - i['cash_ppe_software_q3']
other_investing = i['investing_cashflow_q3'] + i['cash_ppe_software_q3']
debt = sum(i[k] for k in ['recourse_debt_current','recourse_debt_noncurrent','nonrecourse_debt_current','nonrecourse_debt_noncurrent'])
computed = {
    'revenue_growth_yoy_pct': (i['revenue_q3_2026']/i['revenue_q3_2025']-1)*100,
    'cash_fcf_proxy_q3': fcf,
    'cfo_excluding_only_deferred_revenue_movement_q3': i['cfo_q3']-i['cashflow_change_deferred_revenue_q3'],
    'other_investing_cashflow_q3': other_investing,
    'cash_movement_bridge_q3': fcf + other_investing + i['financing_cashflow_q3'],
    'gaap_ebit_to_net_interest_expense': i['gaap_operating_income_q3']/i['net_interest_expense_q3'],
    'net_interest_expense_as_pct_of_revenue': i['net_interest_expense_q3']/i['revenue_q3_2026']*100,
    'debt_balance_carrying_value': debt,
    'debt_less_unrestricted_cash_and_marketable_securities': debt-i['cash_cash_equivalents']-i['marketable_securities'],
    'restricted_cash': i['restricted_cash_current']+i['restricted_cash_noncurrent'],
    'finance_leases_excluded_from_debt_sum': i['finance_lease_current']+i['finance_lease_noncurrent'],
    'operating_leases_excluded_from_debt_sum': i['operating_lease_current']+i['operating_lease_noncurrent'],
    'fy_capex_guidance_midpoint_to_revenue_guidance_midpoint': (i['capex_guidance_fy2026_low']+i['capex_guidance_fy2026_high'])/(i['revenue_guidance_fy2026_low']+i['revenue_guidance_fy2026_high']),
}
assert fcf == -7466
assert computed['cash_movement_bridge_q3'] == i['cash_restricted_cash_change_q3'] == -500
assert debt == 46873
assert computed['debt_less_unrestricted_cash_and_marketable_securities'] == 42689
payload = {
    'schema_version':1, 'report_date':'2026-11-11', 'market_session':'2026-11-10',
    'computed_at':datetime.now(timezone.utc).isoformat(), 'source':SOURCE,
    'financial_period':'2026Q3; balance sheet 2026-09-30; FY2026 management outlook',
    'unit':'USD millions except ratios and percentages', 'inputs':i, 'computed':computed,
    'formulas':{
        'cash_fcf_proxy_q3':'1975 - 9441 = -7466',
        'cfo_excluding_only_deferred_revenue_movement_q3':'1975 - 2127 = -152',
        'cash_bridge':'-7466 + (-9836 + 9441) + 7361 = -500',
        'gaap_ebit_to_net_interest_expense':'207 / 846 = 0.2446808511',
        'net_debt_proxy':'9183 + 32417 + 1389 + 3884 - 4122 - 62 = 42689',
    },
    'limitations':[
        '现金FCF代理=CFO减现金购置物业设备及资本化软件；不是公司披露调整指标，不是完整股东可分配现金，不扣债务本金偿付。',
        '仅剔除递延收入变动的−1.52亿美元是敏感性核对，不是正常化CFO；预收也具有经济价值和未来交付义务。',
        'EBIT/净利息费用0.245倍不是贷款契约利息覆盖率，净利息费用包含非现金项目，不等于现金付息。',
        '债务采用期末账面余额，并非合同本金或市场价值；减现金及有价证券未扣受限现金，另有融资租赁和经营租赁负债。',
        '年度capex指引与单季现金PPE口径未逐项调节，不据此预测全年FCF。',
        '未来三个月约90亿美元预付款和押金、全年收入及capex均为管理层展望，尚非到账或已完成开支。',
        'Q3完整10-Q在本次SEC recent读取中尚未出现；未完成客户集中、合同取消、GPU抵押/折旧、债务到期、稀释及股权DCF，不给低估或买入价格。',
    ],
}
(OUT/'company_crwv_cash_model.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'checks':'passed','cash_fcf_proxy_q3':fcf,'cash_bridge':computed['cash_movement_bridge_q3'],'debt_balance':debt},ensure_ascii=False))
