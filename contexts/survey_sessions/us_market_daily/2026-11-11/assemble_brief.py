from pathlib import Path
from datetime import datetime,timezone
import json,copy
P=Path(__file__).resolve().parent;SITE=P.parents[3]/'adhoc_jobs/us_market_site'
def rd(p):return json.loads(p.read_text())
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def src(t,u):return {'title':t,'url':u}
bp=SITE/'worker/daily-brief.json';sp=SITE/'worker/seed.json'
if not (P/'daily_brief_before.json').exists():save(P/'daily_brief_before.json',rd(bp))
if not (P/'seed_before.json').exists():save(P/'seed_before.json',rd(sp))
prior=rd(P/'daily_brief_before.json');seed=rd(P/'seed_before.json');before=copy.deepcopy(seed)
M={x['symbol']:x for x in rd(P/'metrics.json')};now=datetime.now(timezone.utc).isoformat()
macro=rd(P/'macro_calendar.json');co=rd(P/'company_update.json');social=rd(P/'public_source_sections.json')
market={'title':'CPI已公布，利率压力仍在：继续观察、暂缓追加','fact':'10月CPI季调环比+0.4%、核心+0.3%。BLS因2025年10月停摆缺少基数，本次总项与核心同比未公布，不能填成0或用上月替代。11/10美债2年4.73%、10年4.98%，分别升17／10基点。','implication':'总环比放缓，但核心连续三个月+0.3%，名义折现率未缓解。QQQM收277.87美元（日−0.59%，第二源277.88），回撤11.54%，仍低于200日线280.57；标普500−0.38%、纳指100−0.60%。','judgment':'继续观察，暂缓因前一日反弹而追加。QQQM、VOO、BRK.B均未新触发15%／25%观察档；公司未来现金回报仍需独立验证。','counter':'能源和住房环比压力已有缓和，VIX也回落；本日QQQM回落量能较轻。若利率回落且指数持续收复均线，谨慎理由会减弱。未核一致预期，不称CPI超预期或低于预期。','next':'看11/12初请、11/13 PPI及企业现金流；11/11老兵日股票市场照常交易。观察QQQM能否站稳200日线，重新接近13%时再按原条件提示。','sources':[src('BLS 11/10 CPI实际发布','https://www.bls.gov/news.release/cpi.nr0.htm'),src('财政部11月每日收益率',macro['macro']['treasury']['source']),src('QQQM本次Yahoo日线',M['QQQM']['source_url']),src('QQQM第二来源','https://stockanalysis.com/etf/qqqm/history/')]}
nv=copy.deepcopy(co['homepage_items'][0]);nv['fact']+=' 11/10常规收盘Yahoo168.89美元（−5.47%），StockAnalysis168.78美元（−5.54%），两源均显示继续下跌。'
nv['implication']+=f" 本日成交量为此前20日均量{M['NVDA']['volume_vs_prior20']:.2f}倍；不能把全部跌幅因果归于调查。"
nv['sources'] += [src('NVDA本次Yahoo日线',M['NVDA']['source_url']),src('NVDA第二来源','https://stockanalysis.com/stocks/nvda/history/')]
cr=copy.deepcopy(co['homepage_items'][1]);cr['judgment']=cr['judgment'].replace('、不新增监测标的','')
retained=[]
for sec in prior['sections']:
 if sec['title'].startswith(('11/8研究留存','11/5估值专题留存','FDE上市公司','AI应用专题','11/7研究留存','既有研究留存')):
  s=copy.deepcopy(sec)
  if s['title'].startswith('FDE上市公司'):s['title']='FDE上市公司地图｜11/5专题留存，后续披露另标日期'
  s['paragraphs']=[t.replace('本次周末','原专题研究时') for t in s['paragraphs']];retained.append(s)
google=copy.deepcopy(next(s for s in prior['sections'] if s['title'].startswith('Google现金流')))
google['title']='11/10研究留存｜Google Q3现金流与TPU周转敏感性'
google['paragraphs']=[t.replace('本次新增','11/10新增').replace('新增TPU周转敏感性','11/10 TPU周转敏感性').replace('今日没有给出新买价','11/10未给出新买价；本日无可据以恢复旧买价的新经营披露') for t in google['paragraphs']]
google['sources']=[dict(s,title=s['title'].replace('本次重新读取','11/10重新读取')) for s in google['sources']]
team=prior['items'][2]
teamsec={'title':'11/10研究留存｜TEAM的FDE证据与现金流反证','paragraphs':[team[k] for k in ['fact','implication','judgment','counter','next']],'sources':team['sources']}
valuation={'title':'四股条件估值跟踪｜更新股价，模型仍按11/5假设','paragraphs':['11/10常规收盘Yahoo／StockAnalysis（美元）：NOW99.61／99.59、CRM213.48／213.48、GEHC83.65／83.68、CGNX50.80／50.79。均未低于既有基准八折研究价；仅比较价格，不声称四套估值重新完成。','11/5模型的基准价值／基准八折研究价（美元）：NOW83.30／66.64、CRM183.93／147.14、GEHC现金流法68.68／54.94、CGNX31.98／25.58。GEHC另有盈利法90／72，分母与假设不同，不能平均得出低估；折扣是模型条件，不是损失上限或自动买价。','本次未取得可重置四家经营分母的新披露。CGNX新13G不是RealSense交割，含收购的完整重估仍待完成；NOW/CRM需要核AI新增收费、席位替代及SBC，GEHC需核现金转化与负债。价格下跌本身不提高安全边际的可信度。'],'sources':[src(s+'本次第二来源','https://stockanalysis.com/stocks/'+s.lower()+'/history/') for s in ['NOW','CRM','GEHC','CGNX']]}
credit=social['items'][0];creditsec={'title':'信用风险｜债务存量与新增逾期流量要分开','paragraphs':[credit[k] for k in ['fact','implication','judgment','counter','next']],'sources':credit['sources']}
brief={'schema_version':1,'report_date':'2026-11-11','market_session':'2026-11-10','reviewed_at':now,'summary':'⏳ 继续观察，利率压力下暂缓追加。QQQM回撤11.54%，三项收盘观察档无新触发。NVDA调查新增程序进展；CoreWeave显示AI需求强劲与融资压力并存，基础设施和应用并非简单接棒。','items':[market,nv,cr],'sections':rd(P/'market_sections.json')+rd(P/'macro_public_sections.json')+rd(P/'public_company_sections.json')+[valuation,creditsec]+social['sections']+[google,teamsec]+retained}
a={a['symbol']:a for g in seed['catalog']['groups'] for a in g['assets']};assert len(a)==43
sg=a['SGOV']['facts'];sg.update(sec_yield_pct=3.85,sec_yield_date='2026-11-09')
sg['notes']=[v for v in sg['notes'] if 'SEC收益率' not in v]+['30日SEC收益率3.85%，截至2026-11-09，本次11/11复核；12个月分配收益率3.63%口径不同，二者不是未来总回报。']
for s in sg['sources']:
 if 'SEC收益率' in s['title']:s['asof']='SEC收益率2026-11-09，11/11读取；其他字段各自日期'
n=a['NVDA'];n['research_status']='11/10聘请独立调查律师；结论与财务影响未定，估值未完成'
n['facts']['governance_event'].update(reviewed_date='2026-11-11',reviewed_at=now,latest_event_date='2026-11-10',latest_confirmed='独立董事已聘请Joon H. Kim及Wachtell律所开展调查；尚无调查结论或量化财务影响。')
n['facts']['fact_lines'].append('11/10新增声明、11/11复核：独立董事正式聘请Joon H. Kim及Wachtell律所开展独立调查。这是程序进展，不是风险解除或责任认定；未披露量化经营影响。')
n['facts']['sources'].append(dict(co['homepage_items'][0]['sources'][0],asof='2026-11-10公告，11/11复核'))
n['facts']['governance_event']['financial_impact']=n['facts']['governance_event']['financial_impact'].replace('两份官方声明','已读取的官方声明')
n['facts']['fact_lines']=[t.replace('两份官方声明','11/8两份官方声明') for t in n['facts']['fact_lines']]
epam=a['EPAM'];ff=epam['facts'];ff['fact_lines']=[x.replace('预计11/9当周的5亿美元ASR尚为计划','11/9已签5亿美元ASR协议，预计初始交付和最终结算仍须核实').replace('拟11/9当周5亿美元ASR尚待执行，不能把授权当支出','11/9已签5亿美元ASR协议，不能把签约或预计初交付当全部完成') for x in ff['fact_lines']]
ff['fact_lines'].append('11/10 8-K确认11/9签UBS加速回购：金额5亿美元，预计11/10初交付255.0695万股（按11/9股价价值4亿），2027Q1最终结算；资金来自现金及现有信贷借款，实际交付/借款待核。')
ff['reviewed_date']='2026-11-11';ff['sources'].append(src('EPAM 11/10 ASR协议8-K','https://www.sec.gov/Archives/edgar/data/1352010/000135201026000057/epam-20261109.htm'))
epam['next']='核ASR实际初交付、借款成本和2027Q1结算，重算SBC后净股数；FDE单列收入/利润与正常化估值仍待完成。'
old={v['symbol']:v for g in before['catalog']['groups'] for v in g['assets']};changed=[s for s in a if a[s]!=old[s]]
assert set(changed)=={'NVDA','EPAM','SGOV'} and seed['risk_metrics']==before['risk_metrics']
assert all(a[s]['quote']==old[s]['quote'] and a[s].get('extended')==old[s].get('extended') for s in a)
assert len([v for v in a.values() if v['kind']=='fund'])==17
assert not set(a)&{'QQQ','PDD','DDL','BABA','XPEV','TCEHY','KWEB'}
for obj in [brief,seed]:
 txt=json.dumps(obj,ensure_ascii=False)
 for bad in ['portfolio_private','30,000','30000美元','账户号','我的持仓','已持有GOOG'] :assert bad not in txt,bad
save(bp,brief);save(sp,seed);save(P/'daily_brief_published_candidate.json',brief)
save(P/'assembly_audit.json',{'reviewed_at':now,'items':len(brief['items']),'sections':len(brief['sections']),'changed_research_symbols':changed,'quotes_changed':False,'risk_metrics_changed':False,'private_data_imported':False,'watchlist_symbols_added':[]})
print({'date':brief['report_date'],'headlines':len(brief['items']),'sections':len(brief['sections']),'changed':changed})
