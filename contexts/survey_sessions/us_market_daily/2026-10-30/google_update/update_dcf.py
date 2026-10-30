from pathlib import Path
import json,copy,sys
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parents[4]/'adhoc_jobs/us_market_daily'))
from value_google import value
old=json.loads((P.parents[1]/'2026-10-28/equity_valuation/google_model_inputs.json').read_text())
bridge=json.loads((P/'google_bridge_nwc_scenarios.json').read_text());f=bridge['facts']
inputs=copy.deepcopy(old)
inputs['valuation_date_beijing']='2026-10-30';inputs['quote_session_us']='2026-10-29';inputs['financial_basis']='Q3 10-Q throughSep30, common shares cover asofOct21, TTM revenue/EBIT throughSep30; future periods remain analyst scenarios, not new management guidance or fully reconciled TPU segment forecasts.'
inputs['facts'].update(close_usd=283.82,ttm_revenue_B=f['ttm_revenue_B'],ttm_ebit_B=f['ttm_ebit_B'],non_equity_cash_and_bonds_B=f['non_equity_cash_and_bonds_B'],market_equity_B=f['marketable_equity_B'],private_investments_B=f['nonmarketable_securities_B'],interest_debt_B=f['interest_debt_total_B'],finance_lease_B=f['finance_lease_B'],preferred_claim_B=f['preferred_claim_B'],nci_proxy_B=f['nci_proxy_B_rounded'],current_common_shares_B=f['current_common_shares_B'])
inputs['source_basis']=['https://www.sec.gov/Archives/edgar/data/1652044/000165204426000084/goog-20260930.htm','https://www.sec.gov/Archives/edgar/data/1652044/000165204426000071/goog-20260630.htm','https://stockanalysis.com/stocks/googl/history/']
inputs['accounting_policy']['working_capital']='Baseline2%of incremental revenue preserved only to isolate updated financial facts;5%/10%stresses run separately. No duplicate capex/inventory charge. Future cash release scenarios are separate, not baseDCF addbacks.'
inputs['update_limitations']=['All three growth/margin/capex/D&A/tax/WACC/terminalROIC/retention assumptions preserved fromOct28; no numerical2027 company capex guidance fabricated','Cloud service versusTPUsystem revenue/margin economics and future working capital not separately disclosed','Current debt carrying+current portion used; market debt fair value mismatch not netted opportunistically','Debt assets are fair/book proxies, not riskfree immediately distributable cash','NCI6.9B rounded book proxy; preferred claim proxy19.25B, not simultaneous ifconverted dilution','Operational forecasts include rent and future financedcapex; operating lease liabilities not subtracted twice','Cashflowfine5.2B and inventory reversal not added toDCF; separate explanatory scenario only','TPU repurchase contingent maximum6.6B is not subtracted from baseline; hypothetical gross stress only']
(P/'google_model_inputs.json').write_text(json.dumps(inputs,ensure_ascii=False,indent=2)+'\n')
# NWC stress across full10-year explicit model. Year10 reinvestment remains ROIC-consistent by existing model identity.
scenarios=[]
for ratio in [.02,.05,.10]:
 sc=copy.deepcopy(inputs['scenarios'][1]);sc['incremental_nwc_ratio']=ratio
 result=value(inputs,sc)
 scenarios.append({'incremental_nwc_ratio':ratio,'price_sensitivity_usd':result['price_usd'],'enterprise_value_B':result['enterprise_value_B'],'first_year_nwc_B':result['forecast'][0]['nwc_change_B'],'terminal_note':'Model capex year10 adjusts to preserve terminal growth/ROIC total reinvestment; no arbitrary extra terminal WC double count.'})
base=value(inputs,inputs['scenarios'][1]);gross=6.6/inputs['facts']['current_common_shares_B']
output={'status':'Q3_FINANCIAL_FACTS_UPDATED_DCF_SCENARIOS_NOT_APPROVED_ENTRY_BANDS','nwc_scenarios':scenarios,'contingent_guarantee':{'maximum_gross_payment_B':6.6,'company_fair_value':'not material','company_economic_incentive_view':'unlikely to exercise because repurchase is discounted and requires hardware returned working','gross_maximum_per_share_USD':gross,'base_DCF_without_gross_deduction_USD':base['price_usd'],'hypothetical_100pct_today_no_asset_recovery_lower_value_USD':base['price_usd']-gross,'note':'Not probability-weighted expected loss, not forecast, time-distributed and returned assets omitted deliberately for stress bound. Baseline keeps disclosure separate.'},'bridge_change_contribution_vs_Oct29_partial_per_share_USD':(119.6248-132.8698)/12.294,'not_fair_value_precision_or_buy_instruction':True}
(P/'google_nwc_dcf_stress.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'nwc':scenarios,'gross_guarantee_per_share':gross},ensure_ascii=False))
# Keep source/model status aligned after a deterministic two-step rerun.
sources=json.loads((P/'google_sources.json').read_text())
sources.pop('no_new_complete_valuation_or_entry_price',None)
sources['new_entry_price_instruction_issued']=False
sources['completed_model_update']={'updated_to_Q3':['TTM revenue/operating income','cash/debt versus listed equity split','private securities','short+long financial debt','finance leases','preferred liquidation claim proxy','NCI book proxy','Oct21 common shares','Oct29 regular close283.82 via parent'],'operating_assumptions_maintained_from_Oct28':True,'main_scenarios_USD':{sc['name']:value(inputs,sc)['price_usd'] for sc in inputs['scenarios']},'model_file':'google_valuation_model.json','NWC_model_file':'google_nwc_dcf_stress.json','old_entry_bands_reactivated':False,'source_of_quote':'Parent verified Yahoo/StockAnalysis10/29 regular close; not newly retrieved by this subtask'}
(P/'google_sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2)+'\n')
bridge['status']='Q3_CAPITAL_BRIDGE_UPDATED_NWC_PRESSURE_CHECK'
bridge['policies']['full_model_gap']='A full10-year scenario calculator is rerun separately withQ3facts. Future TPU/service mix, margins, external compute, capex and remaining assumptions are not fully recalibrated; outputs are conditional research values, not certified fair values or entry bands.'
(P/'google_bridge_nwc_scenarios.json').write_text(json.dumps(bridge,ensure_ascii=False,indent=2)+'\n')
