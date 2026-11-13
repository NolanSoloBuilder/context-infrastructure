import json,datetime
from pathlib import Path
B=Path(__file__).resolve().parent
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
prices={'AMZN':267.44,'MSFT':523.00,'AAPL':354.88,'PLTR':171.58,'ACN':249.95,'EPAM':163.83,'GLOB':45.75}
filings={
'AMZN':'https://www.sec.gov/Archives/edgar/data/1018724/000101872426000040/amzn-20260930.htm',
'MSFT':'https://www.sec.gov/Archives/edgar/data/789019/000119312526436133/msft-20260930.htm',
'AAPL':'https://www.sec.gov/Archives/edgar/data/320193/000032019326000026/aapl-20260926.htm',
'PLTR':'https://www.sec.gov/Archives/edgar/data/1321655/000132165526000048/pltr-20260930.htm',
'ACN':'https://www.sec.gov/Archives/edgar/data/1467373/000146737326000049/acn-20260831.htm',
'EPAM':'https://www.sec.gov/Archives/edgar/data/1352010/000135201026000052/epam-20260930.htm',
'GLOB':'https://investors.globant.com/2026-08-13-Globant-Reports-2026-Second-Quarter-Financial-Results'}
common='条件估值，非目标价或确定内在价值。PE 与增长率是研究假设，不冒充历史均值或市场一致预期；基准值的折扣也不是损失上限。利润口径保留 SBC 和利息，不再次从 EPS 扣 SBC，不把净现金重复加回。现金流减 SBC 仅是稀释成本校验，非公司报告的自由现金流，且不等同完整股东现金流 DCF。'
records={}
def add(s,anchor,bg,bpe,sg,spe,disc,judgment,basis,next_,financials,anchor_formula,pe_reason,extra=[],stress_anchor=None):
 baseeps=anchor*(1+bg); stresseps=(anchor if stress_anchor is None else stress_anchor)*(1+sg)
 base=baseeps*bpe;stress=stresseps*spe;discount=base*(1-disc)
 records[s]={
 'judgment':judgment,'basis':basis+f' 条件基准：{baseeps:.4f}美元 EPS × {bpe}倍 = {base:.2f}美元；压力：{stresseps:.4f}美元 × {spe}倍 = {stress:.2f}美元；基准再折让{disc*100:.0f}%为{discount:.2f}美元。',
 'next':next_,'reviewed_at':now,'market_session':'2026-11-12','price':prices[s],'currency':'USD','quote_session':'regular_close','quote_crosscheck':'本次 Yahoo 日线与 StockAnalysis 2026-11-12 常规收盘一致；不使用盘后价。',
 'base_value':round(base,2),'stress_value':round(stress,2),'discount_price':round(discount,2),'discount_to_base_pct':round((1-prices[s]/base)*100,2),
 'model':{'type':'conditional_earnings_multiple','anchor_eps':anchor,'anchor_formula':anchor_formula,'base_eps_growth_assumption':bg,'base_pe_assumption':bpe,'base_eps':baseeps,'stress_anchor_eps':anchor if stress_anchor is None else stress_anchor,'stress_eps_growth_assumption':sg,'stress_pe_assumption':spe,'stress_eps':stresseps,'margin_of_safety_assumption':disc,'multiple_reasoning':pe_reason,'limitations':common},
 'financials':financials,'sources':[{'title':s+' 最新 SEC/IR 财务原文','url':filings[s]},{'title':s+' 11/12 常规收盘第二来源','url':f'https://stockanalysis.com/stocks/{s.lower()}/history/'}]+extra}
add('AMZN',1.89*4,.15,27,-.15,21,.20,
 '估值偏高；投资重估收益放大表面盈利，当前未见足够折扣。',
 '11/12 收267.44美元。2026Q3 GAAP EPS 1.89；用该季年化7.56作为透明盈利锚，基准再增15%，压力降15%，年化并非全年预测。TTM EPS 12.37含大额投资浮盈；9个月私募股权估值上调628.53亿美元，不能按这部分收益长期资本化。TTM公司口径FCF约负424亿美元，现金投入尚未兑现为股东现金。',
 '核AWS利润增长能否持续抵消资本投入与折旧、投资收益回落后经营EPS，以及净PPE投入与融资租赁；若基准增长无法兑现，下调估值。',
 {'unit':'USD million except EPS','period':'2026Q3 / TTM to 2026-09-30','q3_gaap_eps':1.89,'ttm_gaap_eps':7.17+10.42-5.22,'ttm_operating_income':79975+79389-54998,'ttm_cfo':139514+113841-85055,'ttm_gross_cash_ppe':131819+175670-92297,'ttm_sbc':19467+15476-15070,'ttm_reported_fcf_approx':-42400,'cash_and_marketable_securities':114226,'debt_carrying_value_excluding_leases':6827+173125,'private_equity_upward_adjustments_9m':62853,'debt_note':'现金证券中含公开股权；账面债务不含租赁。FCF采用公司净PPE口径，不用现金流表毛购置额冒充公司FCF。'},
 'Q3 GAAP EPS 1.89 × 4 = 7.56；未把季度负其他收入加回。',
 '27倍基准需要AWS高增长与零售利润率支持；21倍压力反映增长放缓和高投入，二者均为假设。',
 [{'title':'Amazon 2026Q3 业绩及公司FCF口径','url':'https://ir.aboutamazon.com/news-release/news-release-details/2026/Amazon-com-Announces-Third-Quarter-Results/'}])
add('MSFT',4.89*4,.12,26,-.10,22,.20,
 '接近合理区间但折扣不足；需用融资租赁与资本开支检验利润质量。',
 '11/12 收523.00美元。FY27Q1（2026/9）GAAP EPS4.92，剔除OpenAI投资影响的公司EPS4.89仍保留SBC；年化19.56作锚，基准增12%、压力降10%。TTM CFO1958.78亿美元减现金PPE1359.21亿美元仅599.57亿美元，再扣SBC的校验值474.01亿美元，且尚未扣融资租赁本金。',
 '核Azure与AI收入增长、OpenAI应收回款、融资租赁资本投入和现金转化；折旧加速或现金投入持续高于假设将压低倍数。',
 {'unit':'USD million except EPS','period':'FY27Q1 / TTM to 2026-09-30','q1_gaap_eps':4.92,'q1_eps_ex_openai_investment_effect':4.89,'ttm_cfo':182935+58000-45057,'ttm_cash_ppe':115948+39367-19394,'ttm_sbc':12405+3134-2983,'cash_and_short_investments':64509,'debt_excluding_leases':35481,'finance_lease_liability':70973,'q1_finance_lease_principal_approx':1000,'q1_new_finance_lease_rou_assets':5192,'fcf_note':'CFO减现金PPE尚未覆盖融资租赁本金及新取得融资租赁资产；不可视作全部AI资本投入。'},
 '最新季度 EPS（仅剔除OpenAI投资影响）4.89 × 4 = 19.56；并非FY27指引。',
 '26倍基准要求双位数持续增长与软件续费优势；22倍压力包含10%盈利回落、资本效率降低。',
 [{'title':'Microsoft FY27Q1 官方业绩及OpenAI调节','url':'https://www.microsoft.com/en-us/investor/earnings/fy-2027-q1/press-release-webcast'}])
add('AAPL',8.98-.11-.05,.08,28,-.10,22,.20,
 '当前溢价明显；优质现金流仍不足以证明当前价格有安全边际。',
 '11/12 收354.88美元。FY26 GAAP EPS8.98，减已披露Q3/Q4关税退款贡献0.11/0.05，得到8.82；当前约40.2倍该调整盈利。基准EPS增8%，压力降10%；不预设回购必然抬高EPS。FY26 FCF1360.56亿美元，减SBC校验值1222.67亿美元，现金质量好但估值要求高。',
 '核AI终端换机带来的增量毛利、服务收入、存储成本和关税退款消退；若增长无法覆盖高倍数，不能仅因回调买入。',
 {'unit':'USD million except EPS','period':'FY2026 ended 2026-09-26','gaap_eps':8.98,'identified_tariff_refund_eps_q3':.11,'identified_tariff_refund_eps_q4':.05,'cfo':145097,'cash_ppe':9041,'sbc':13789,'cash_and_marketable_securities':36305+20417+80213,'term_debt_and_commercial_paper':9906+68208+1997,'finance_lease_liability':1456,'normalization_note':'只扣已核Q3/Q4退款，不声称穷尽全部一次项；EPS仍含SBC与利息。'},
 'FY26 EPS 8.98 − Q3退款0.11 − Q4退款0.05 = 8.82。',
 '28倍基准已给予品牌、生态和现金回收溢价；22倍压力计入换机不足、成本上行。',
 [{'title':'Apple FY26Q3：退款贡献EPS0.11','url':'https://www.apple.com/newsroom/2026/07/apple-reports-third-quarter-results/'},{'title':'Apple FY26Q4：退款贡献EPS0.05','url':'https://www.apple.com/newsroom/2026/11/apple-reports-fourth-quarter-results/'}])
panchor=(1148.001*.8-6.429)/2573.926*4
add('PLTR',panchor,.40,45,.10,30,.25,
 '高增长仍被高价计入；即使给予积极增长，当前也缺少安全边际。',
 '11/12 收171.58美元。2026Q3税前利润11.48001亿美元、所得税仅0.13560亿美元；不能永久外推约1.18%税率。按20%假设税率、扣少数股东利润，再除25.73926亿稀释股并年化；保留SBC。基准再增40%且给45倍，压力仍增10%但30倍。TTM FCF40.54亿美元，减SBC校验值30.72亿美元，相对当前市值不足1%。',
 '核美国商业收入、合同现金回收、正常税率与SBC稀释；FDE变现没有单列利润，不能给同一公司再叠加独立FDE估值。',
 {'unit':'USD million except EPS','period':'2026Q3 / TTM to 2026-09-30','q3_pretax_income':1148.001,'q3_tax_expense':13.560,'q3_noncontrolling_income':6.429,'q3_diluted_shares_million':2573.926,'normal_tax_assumption':.20,'ttm_cfo':2134.473+3319.902-1357.178,'ttm_cash_ppe':33.882+29.969-20.610,'ttm_sbc':684.033+785.690-487.628,'cash':3619.414,'marketable_securities':6942.117,'debt_note':'盈利估值未额外加入现金；没有把现金总额当现金流或用非GAAP剔除SBC。'},
 '(Q3税前利润1148.001 × 80% − 少数股东利润6.429) ÷ 稀释股数2573.926 × 4；金额和股数均以百万计。',
 '45倍基准已容纳40%盈利增长，仍依赖持续商业化；30倍压力给10%增长，25%折扣反映客户/合同/税率与高倍数风险。',
 [{'title':'Palantir 2026Q3 业绩','url':'https://www.sec.gov/Archives/edgar/data/1321655/000132165526000045/a2026q3ex991pressrelease.htm'}])
add('ACN',13.56,.06,21,-.10,16,.20,
 '七项中最接近条件折扣线；可能存在温和低估，但当前仍略高于20%折扣价。',
 '11/12 收249.95美元。FY26 GAAP EPS13.56保留SBC及3.08亿美元优化费用；基准增6%，压力降10%。FY26 CFO123.63亿美元减现金PPE7.43亿美元，再扣SBC21.00亿美元，现金校验值95.20亿美元；现金证券128.38亿美元、债务101.12亿美元（不含租赁），提供相对较好财务缓冲。',
 '核AI订单转为收入和毛利、项目定价从工时到结果后的利润率、重组是否反复；若项目缩减使EPS下滑10%，压力价值明显低于现价。',
 {'unit':'USD million except EPS','period':'FY2026 ended 2026-08-31','gaap_eps':13.56,'cfo':12363.346,'cash_ppe':742.748,'sbc':2100.433,'cash_and_short_investments':12837.769,'debt_excluding_leases':10111.758,'operating_lease_liability':3285.232,'retirement_obligation':1558.775,'optimization_charge':308,'normalization_note':'保留优化费用；不把每次重组都当永久可加回一次项。'},
 'FY26 GAAP EPS 13.56；基准×1.06，压力×0.90。',
 '21倍基准对应稳定服务现金流和6%增长；16倍压力反映客户削减项目及AI压缩工时定价。',
 [{'title':'Accenture FY26 全年业绩','url':'https://www.sec.gov/Archives/edgar/data/1467373/000146737326000037/q4fy26earnings8-kexhibit.htm'}])
add('EPAM',6.72+6.00-4.75,.10,20,-.10,15,.20,
 '较基准有小幅折扣，尚不足以覆盖现金转化与回购融资风险。',
 '11/12 收163.83美元。TTM GAAP EPS=6.72+6.00−4.75=7.97，保留SBC；基准增10%，压力降10%。TTM FCF4.704亿美元，减SBC校验值2.865亿美元。9/30现金9.652亿美元、债务0.25亿美元是旧资产负债表；11/9签约5亿美元ASR将消耗现金或融资，不能再把旧净现金完整叠加估值。',
 '核ASR实际交付及最终结算后的现金/债务/股数、Q4经营现金与应收回款；2026/11/12新增申报为Form4/144，未发现ASR最终完成披露。',
 {'unit':'USD million except EPS','period':'TTM to 2026-09-30','ttm_gaap_eps':6.72+6.00-4.75,'ttm_cfo':654.934+250.052-372.044,'ttm_cash_ppe':42.243+47.749-27.462,'ttm_sbc':176.764+138.798-131.618,'cash_asof_20260930':965.173,'debt_asof_20260930':25,'asr_signed_20261109':500,'asr_status':'已签约；不将预计11/10初始交付当作最终完成，不据此制造新股数。'},
 'FY25 GAAP EPS6.72 + 9M26 EPS6.00 − 9M25 EPS4.75 =7.97；季度EPS加总受四舍五入和股数变化影响，属TTM每股盈利近似。',
 '20倍基准要求10%EPS恢复与现金转换正常；15倍压力计入项目预算、人才成本和融资回购风险。',
 [{'title':'EPAM 2026Q3 业绩','url':'https://www.sec.gov/Archives/edgar/data/1352010/000135201026000048/exhibit99_q3x2026.htm'},{'title':'EPAM 11/9 ASR协议8-K','url':'https://www.sec.gov/Archives/edgar/data/1352010/000135201026000057/epam-20261109.htm'}])
ganchor=(38.746+32.294*.75)*2/43.405
gstress=38.746*2/43.405
add('GLOB',ganchor,0,18,0,14,.25,
 '低于恢复基准但未到足够折扣；存在价值陷阱风险，11/19财报是下一核验点。',
 '11/12 收45.75美元。最新已公布为2026H1：归母利润3874.6万美元；只将3229.4万美元重组费按假设25%税率加回，保留SBC与收购费用，半年年化作恢复锚；压力完全不加回重组。Q2经营现金3021.7万美元、资本开支1758.4万美元，减SBC1904.7万美元后的校验值为负。6/30借款4.22亿美元高于现金短投1.69亿美元，不能用调整EPS把杠杆和反复重组忽略。',
 '11/19盘后核Q3：AI Pods收入能否补足传统项目、回款与借款、重组是否再次发生；最新完整季度尚是Q2，不把Q3指引当实际业绩。',
 {'unit':'USD million except EPS','period':'H1 / Q2 2026 ended 2026-06-30','h1_common_income':38.746,'h1_business_optimization_common_reconciliation':32.294,'normalization_tax_assumption':.25,'h1_sbc_common_reconciliation':37.234,'h1_diluted_shares_million':43.405,'q2_cfo':30.217,'q2_cash_ppe':17.584,'q2_sbc_common_reconciliation':19.047,'cash_and_short_investments':168.815,'borrowings':19.364+402.591,'lease_liabilities':25.739+70.160,'other_financial_liabilities':97.811+50.179,'goodwill':1595.460,'common_equity':2113.548,'normalization_note':'2025也发生重组，故基准加回具争议，压力不加回；IR财务表未审计且并非完整IAS34中期报告。'},
 '(H1归母利润38.746 + 归母调节表重组费32.294 ×75%) ×2 ÷ H1稀释股数43.405；压力=38.746×2÷43.405。',
 '18倍恢复基准要求重组停止并稳定收入，14倍压力使用未加回盈利；25%折扣用于客户、执行、净债务及商誉风险。',
 [{'title':'Globant Q3财报将于11/19盘后发布','url':'https://investors.globant.com/2026-11-05-Globant-to-Announce-Third-Quarter-2026-Financial-Results-on-November-19th'}],stress_anchor=gstress)
for s,r in records.items():
 f=r['financials']
 if 'ttm_cfo' in f and 'ttm_cash_ppe' in f:
  f['ttm_fcf_proxy']=round(f['ttm_cfo']-f['ttm_cash_ppe'],6)
  f['ttm_fcf_less_sbc_proxy']=round(f['ttm_fcf_proxy']-f['ttm_sbc'],6)
 if 'cfo' in f:
  f['fcf_proxy']=round(f['cfo']-f['cash_ppe'],6)
  f['fcf_less_sbc_proxy']=round(f['fcf_proxy']-f['sbc'],6)
 r['model']['base_value_exact']=r['model']['base_eps']*r['model']['base_pe_assumption']
 r['model']['stress_value_exact']=r['model']['stress_eps']*r['model']['stress_pe_assumption']
 assert round(r['model']['base_value_exact']*(1-r['model']['margin_of_safety_assumption']),2)==r['discount_price']
 assert all(k in r for k in ['judgment','basis','next','reviewed_at','market_session','sources'])
assert set(records)==set(prices)
(B.parent/'valuation_software.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
(B/'model_methodology.json').write_text(json.dumps({'reviewed_at':now,'status':'conditional_models_completed_not_full_dcf','methodology':common,'raw_source_coverage':'Fresh SEC submissions/companyfacts all seven downloaded; SEC filing HTML curl returned403 and remains failure evidence, relevant financial and risk sections were read through web tool. Globant Q2 primary IR financial tables were read through web. StockAnalysis historical regular closes read via web and agree with local Yahoo daily CSV on11/12.','price_crosscheck':prices,'market_session':'2026-11-12','non_annual_eps_caveat':'季度/半年年化并非未来全年预测；不同公司财年不同；TTM EPS相加有舍入及加权股数近似；PE/增长/折扣均属显式研究假设。'},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({s:{k:r[k] for k in ['price','base_value','stress_value','discount_price']} for s,r in records.items()},ensure_ascii=False,indent=2))
