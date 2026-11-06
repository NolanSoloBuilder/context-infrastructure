import json, math
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parent
TAX=.235
SOURCES={
'now_q3':'https://www.sec.gov/Archives/edgar/data/1373715/000137371526000096/now-20260930.htm',
'now_fy25':'https://www.sec.gov/Archives/edgar/data/1373715/000137371526000007/now-20251231.htm',
'now_release':'https://investor.servicenow.com/news/news-details/2026/ServiceNow-Reports-Third-Quarter-2026-Financial-Results/default.aspx',
'crm_q2':'https://www.sec.gov/Archives/edgar/data/1108524/000110852426000190/crm-20260731.htm',
'crm_fy26':'https://www.sec.gov/Archives/edgar/data/1108524/000110852426000060/crm-20260131.htm',
'crm_release':'https://investor.salesforce.com/news/news-details/2026/Salesforce-Delivers-Record-Second-Quarter-Fiscal-2027-Results/default.aspx',
'crm_fin':'https://www.salesforce.com/news/press-releases/2026/09/10/salesforce-completes-acquisition-of-fin/',
'crm_contentful':'https://www.salesforce.com/news/stories/salesforce-signs-definitive-agreement-to-acquire-contentful/',
'crm_m3ter':'https://www.salesforce.com/news/stories/salesforce-signs-definitive-agreement-to-acquire-m3ter/',
'crm_loops':'https://www.salesforce.com/news/stories/salesforce-signs-definitive-agreement-to-acquire-loops/',
'crm_braze':'https://www.salesforce.com/news/press-releases/2026/10/20/salesforce-signs-definitive-agreement-to-acquire-braze/?bc=DB',
'now_price':'https://stockanalysis.com/stocks/now/history/',
'crm_price':'https://stockanalysis.com/stocks/crm/history/'
}
# All financial amounts and share counts in USD million / million shares.
# TTM = prior full fiscal year + current YTD - comparable prior YTD.
INPUT={
'NOW':{
 'financial_asof':'2026-09-30','release_date':'2026-10-28','price':108.81,'diluted_shares':1043.011,
 'share_basis':'Q3 2026 weighted diluted shares; 5-for-1 Dec 17 2025 split restated; no further dilution forecast after expensing SBC',
 'periods':{'fy':{'cfo':5444,'capex':868,'sbc_cashflow':1955,'cash_interest_paid':22,'interest_income':451,'acquisition_cash_cost':60,'financing_obligation_principal':0},'ytd':{'cfo':3096,'capex':346,'sbc_cashflow':1829,'cash_interest_paid':50,'interest_income':227,'acquisition_cash_cost':371,'financing_obligation_principal':0},'prior_ytd':{'cfo':3206,'capex':630,'sbc_cashflow':1461,'cash_interest_paid':22,'interest_income':346,'acquisition_cash_cost':28,'financing_obligation_principal':0}},
 'balance':{'cash':2393,'short_securities':2214,'long_securities':2354,'debt_principal_approx':7600,'debt_carrying':7524,'strategic_investments_excluded':2050,'post_balance_completed_acquisition_reserve':0},
 'quarter':{'revenue':4106,'gaap_operating_income':385,'sbc_pl':633,'acquisition_amortization':198,'acquisition_related_cost':35,'severance':87,'non_gaap_operating_income':1338,'gaap_net_income':277,'non_gaap_net_income':1039,'gaap_diluted_eps':.27,'cash_flow_cfo':839,'capex':91,'company_fcf':822},
 'assumption_notes':['Debt principal 7,600 is rounded: senior notes 5,500 + commercial paper approximately 2,100; fair-value sensitivity versus carrying debt is about $0.07/share.','TTM cash interest paid is used rather than accrued interest expense because CFO is cash based. Interest received is approximated with reported interest income; exact timing/tax and finance lease interest separation remain a model limitation.','Base reverses 50% of after-tax acquisition cash costs; bear zero, bull 100%. This is analyst normalization, not management guidance.','Strategic investments are excluded from base equity bridge; full reported book-value inclusion sensitivity is disclosed, not an assertion of zero value.']
},
'CRM':{
 'financial_asof':'2026-07-31','release_date':'2026-08-26','price':227.11,'diluted_shares':827,
 'share_basis':'Management Q3 FY27 diluted-share guidance, provisional after large ASR; Q2 actual weighted diluted 821m and Aug20 outstanding 823m. Final ASR settlement shares not verified.',
 'periods':{'fy':{'cfo':14996,'capex':594,'sbc_cashflow':3509,'cash_interest_paid':276,'interest_income':539,'acquisition_cash_cost':0,'financing_obligation_principal':584},'ytd':{'cfo':7970,'capex':316,'sbc_cashflow':1763,'cash_interest_paid':240,'interest_income':206,'acquisition_cash_cost':0,'financing_obligation_principal':306},'prior_ytd':{'cfo':7216,'capex':314,'sbc_cashflow':1607,'cash_interest_paid':115,'interest_income':319,'acquisition_cash_cost':0,'financing_obligation_principal':278}},
 'balance':{'cash':8310,'short_securities':3093,'long_securities':0,'debt_principal_approx':39500,'debt_carrying':39288,'strategic_investments_excluded':11324,'post_balance_completed_acquisition_reserve':5100},
 'quarter':{'revenue':11345,'informatica_revenue':456,'prior_revenue':10236,'gaap_operating_income':2331,'sbc_pl_ex_restructuring':904,'acquisition_amortization':522,'restructuring_acquisition_cost':115,'non_gaap_operating_income':3872,'gaap_net_income':3526,'non_gaap_net_income':4844,'gaap_diluted_eps':4.29,'non_gaap_diluted_eps':5.90,'six_month_investment_gains':3171,'six_month_gaap_eps':6.67,'cash_flow_cfo':1269,'capex':171},
 'guidance':{'fiscal_year':'FY2027 ending January 31 2027','revenue_midpoint':46250,'gaap_eps_midpoint':10.23,'non_gaap_eps_midpoint':16.69,'weighted_shares':838,'amortization_eps_addback':2.45,'restructuring_acquisition_eps_addback':.42,'sbc_eps_addback':4.96,'tax_rate_assumption':.235,'status':'management forecast, not actual'},
 'assumption_notes':['Base adds 5,100 post-July cash acquisition reserve (Fin 3,600 + Contentful 1,500) to historical net debt. This is a model bridge, NOT observed November net debt; Q3 operating cashflow, dividends, target cash and final purchase accounting unknown.','Loops closed November 2; undisclosed consideration is a gap, not assumed zero economic cost. Pending Braze 5,660 enterprise value is not yet cash paid and not subtracted in base. Other pending deal prices not fully reconciled.','The March 25,000 ASR funding is already in July debt/cash and initial shares; not deducted again. Informatica 6,000 refinancing is not incremental debt twice.','Recurring financing-obligation principal is deducted from owner cashflow; related financing/lease liabilities are NOT also added to debt. CFO already bears lease interest. Cash-interest adjustment lacks an exact current finance-lease split, flagged below.','Base has an additional 4% normalized cashflow reserve for cash-tax/working-capital timing, not a reported impairment. Bull requires 12,000 owner FCFF rather than assuming current actual cashflow equals this amount.','SBC cashflow addback differs from P&L expense; use cashflow figure to reverse the actual cashflow addback, not both.','Strategic investment marks are excluded from recurring cash earnings; portfolio excluded from base value but sensitivity disclosed.']
}}
def ttm(p,k):return p['fy'][k]+p['ytd'][k]-p['prior_ytd'][k]
def dcf(f0,g1,g2,r,t,netdebt,shares,acquired_business_value=0):
 f=f0; flows=[]
 for y in range(1,11):
  f*=1+(g1 if y<=5 else g2)
  flows.append({'year':y,'owner_fcff':f,'discounted_owner_fcff':f/(1+r)**y})
 pv=sum(x['discounted_owner_fcff'] for x in flows)
 tv=f*(1+t)/(r-t)/(1+r)**10
 ev=pv+tv
 return {'f0':f0,'growth_years_1_5':g1,'growth_years_6_10':g2,'discount_rate':r,'terminal_growth':t,'annual_cashflows':flows,'pv_explicit_cashflows':pv,'pv_terminal':tv,'terminal_share_of_ev':tv/ev,'enterprise_value':ev,'net_debt_deduction':netdebt,'acquired_business_value_placeholder':acquired_business_value,'equity_value':ev-netdebt+acquired_business_value,'diluted_shares':shares,'fair_value_per_share':(ev-netdebt+acquired_business_value)/shares}
OUT={'schema_version':1,'report_date':'2026-11-05','reviewed_at':datetime.now(timezone.utc).isoformat(),'financial_units':'USD million; shares million; price USD/share','market_session':'2026-11-04','sources':SOURCES,'formulas':{'ttm':'FY + current YTD - comparable prior YTD','owner_levered_cash_proxy':'CFO - cash capex - SBC cashflow addback - recurring financing-obligation principal','owner_fcff_proxy':'owner_levered_cash_proxy + (cash interest paid - reported interest income proxy) * (1 - 0.235)','enterprise_value':'sum(Ft/(1+r)^t, t=1..10) + F10*(1+gT)/(r-gT)/(1+r)^10','equity_value':'legacy enterprise_value - interest-bearing principal + cash and marketable securities - post-balance completed acquisition reserve + post-balance acquired-business value placeholder; strategic investments excluded in base','margin_price':'0.8 * base intrinsic value; research margin, not approved buy order','sbc_rule':'Economic SBC deducted once; no additional future share dilution or cash buyback cost assumed for the same compensation. Current diluted-share claims remain in denominator.'},'companies':{}}
for sym,x in INPUT.items():
 ts={k:ttm(x['periods'],k) for k in x['periods']['fy']}
 ts['standard_fcf']=ts['cfo']-ts['capex']
 ts['owner_levered_cash_proxy']=ts['standard_fcf']-ts['sbc_cashflow']-ts['financing_obligation_principal']
 ts['net_interest_tax_adjustment']=(ts['cash_interest_paid']-ts['interest_income'])*(1-TAX)
 ts['owner_fcff_proxy']=ts['owner_levered_cash_proxy']+ts['net_interest_tax_adjustment']
 b=x['balance']; liquid=b['cash']+b['short_securities']+b['long_securities']; nd=b['debt_principal_approx']-liquid+b['post_balance_completed_acquisition_reserve']
 if sym=='NOW':
  a=ts['acquisition_cash_cost']*(1-TAX)
  scenarios={'bear':(ts['owner_fcff_proxy'],.12,.06,.115,.025),'base':(ts['owner_fcff_proxy']+.5*a,.20,.10,.10,.03),'bull':(ts['owner_fcff_proxy']+a,.24,.12,.09,.035)}
 else:scenarios={'bear':(9500,.03,.02,.11,.02),'base':(ts['owner_fcff_proxy']*.96,.07,.04,.10,.025),'bull':(12000,.10,.06,.09,.03)}
 target_values={n:(5100*{'bear':.5,'base':1,'bull':1.5}[n] if sym=='CRM' else 0) for n in scenarios}
 results={n:dcf(*p,nd,x['diluted_shares'],target_values[n]) for n,p in scenarios.items()}
 for v in results.values():v['price_vs_value_pct']=(x['price']/v['fair_value_per_share']-1)*100;v['value_vs_price_pct']=(v['fair_value_per_share']/x['price']-1)*100
 base=results['base'];f0,g1,g2,r,t=scenarios['base'];lo,hi=-.3,.8
 for i in range(100):
  mid=(lo+hi)/2
  if dcf(f0,mid,g2,r,t,nd,x['diluted_shares'],target_values['base'])['fair_value_per_share']<x['price']:lo=mid
  else:hi=mid
 sensitivity=[{'discount_rate':rr,'terminal_growth':tt,'fair_value_per_share':dcf(f0,g1,g2,rr,tt,nd,x['diluted_shares'],target_values['base'])['fair_value_per_share']}for rr in [.09,.10,.11] for tt in [.02,.025,.03]]
 rec={'inputs':x,'ttm':ts,'liquid_assets':liquid,'historical_net_debt':b['debt_principal_approx']-liquid,'model_net_debt':nd,'scenarios':results,'base_20pct_margin_price':base['fair_value_per_share']*.8,'price_to_base_owner_cashflow':x['price']*x['diluted_shares']/f0,'standard_fcf_yield_pct':ts['standard_fcf']/(x['price']*x['diluted_shares'])*100,'owner_cash_yield_pct':ts['owner_levered_cash_proxy']/(x['price']*x['diluted_shares'])*100,'reverse_dcf_first_5yr_growth':(lo+hi)/2,'strategic_portfolio_full_book_per_share_sensitivity':b['strategic_investments_excluded']/x['diluted_shares'],'sensitivity':sensitivity}
 if sym=='CRM':
  rec['acquired_business_value_sensitivity']=[{'target_value':v,'fair_value_per_share':dcf(f0,g1,g2,r,t,nd,x['diluted_shares'],v)['fair_value_per_share']} for v in [0,2550,5100,7650]]
  rec['acquired_business_value_note']='Fin/Contentful post-July target cashflow is not in July TTM. Legacy growth assumptions exclude these target businesses; add target standalone value at 0.5x/1x/1.5x known cash cost across bear/base/bull as an explicit placeholder, not independently verified fair value. No incremental synergies included. Loops undisclosed price remains unquantified.'
  g=x['guidance'];core_eps=g['gaap_eps_midpoint']-x['quarter']['six_month_investment_gains']*(1-TAX)/g['weighted_shares']+(g['amortization_eps_addback']+g['restructuring_acquisition_eps_addback'])*(1-TAX)
  rec['normalized_eps_crosscheck']={'formula':'10.23 - 3171 * 0.765 / 838 + (2.45 + 0.42) * 0.765','normalized_eps_guidance_proxy':core_eps,'price_multiple':x['price']/core_eps,'headline_adjusted_guidance_pe':x['price']/g['non_gaap_eps_midpoint'],'notes':'Forward proxy, not actual; retains SBC, strips known investment gains, reverses amortization and restructuring/acquisition at tax assumption; recurring restructuring and future interest remain uncertainties.'}
 OUT['companies'][sym]=rec
(ROOT/'valuation_inputs_and_results.json').write_text(json.dumps(OUT,ensure_ascii=False,indent=2)+'\n')
yahoo=json.loads((ROOT.parent/'cgnx/fresh_quotes.json').read_text())
price={'captured_at':OUT['reviewed_at'],'regular_session':'2026-11-04','regular_close_et':'2026-11-04T16:00:00-05:00','regular_close_beijing':'2026-11-05T05:00:00+08:00','currency':'USD','primary':[q for q in yahoo if q['symbol'] in INPUT],'second_source':{'NOW':{'url':SOURCES['now_price'],'regular_price':108.81,'timestamp_et':'2026-11-04 16:00 EST','price_difference_usd_to_rounded_yahoo':0,'after_hours':{'price':108.50,'timestamp_et':'2026-11-04 19:59 EST','timestamp_beijing':'2026-11-05 08:59 CST','cross_verified':False}},'CRM':{'url':SOURCES['crm_price'],'regular_price':227.11,'timestamp_et':'2026-11-04 16:00 EST','price_difference_usd_to_rounded_yahoo':0,'after_hours':{'price':227.68,'timestamp_et':'2026-11-04 19:59 EST','timestamp_beijing':'2026-11-05 08:59 CST','cross_verified':False}}},'notes':['Both regular sources are third-party; match to USD0.01.','Yahoo daily bar timestamp is session open, not the close execution timestamp; regular quote and completed-session close independently matched.','After-hours quotes are single-source references, excluded from valuations; session has ended but quotes are not asserted as official final closes.']}
(ROOT/'price_verification.json').write_text(json.dumps(price,ensure_ascii=False,indent=2)+'\n')
for sym,c in OUT['companies'].items():
 print(sym,{k:round(v['fair_value_per_share'],2) for k,v in c['scenarios'].items()},'margin',round(c['base_20pct_margin_price'],2),'reverse_g',round(c['reverse_dcf_first_5yr_growth']*100,2),'ttm',c['ttm'])
 if sym=='CRM':print(c['normalized_eps_crosscheck'])
