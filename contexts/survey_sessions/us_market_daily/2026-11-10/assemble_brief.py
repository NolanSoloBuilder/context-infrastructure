from pathlib import Path
from datetime import datetime,timezone
import json,copy
P=Path(__file__).resolve().parent
SITE=P.parents[3]/'adhoc_jobs/us_market_site'
def rd(p):return json.loads(p.read_text())
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def src(t,u):return {'title':t,'url':u}
prior=rd(SITE/'worker/daily-brief.json')
if not (P/'daily_brief_before.json').exists():save(P/'daily_brief_before.json',prior)
else:prior=rd(P/'daily_brief_before.json')
now=datetime.now(timezone.utc).isoformat();m={x['symbol']:x for x in rd(P/'metrics.json')}
macro=rd(P/'macro_calendar.json');company=rd(P/'public_company_sections.json');social=rd(P/'public_source_sections.json')
retained=[copy.deepcopy(s) for s in prior['sections'] if s['title'].startswith(('11/8研究留存','11/5估值专题留存','FDE上市公司','AI应用专题','11/7研究留存','既有研究留存'))]
for s in retained:
 s['paragraphs']=[v.replace('SEC recent本次尚未见对应新入库条目','该历史研究时SEC尚未入库；11/9已出现10-Q，详见本次公司更新') for v in s['paragraphs']]
calendar={'title':'宏观与未来一周｜今晚CPI，VIX下降但美债收益率上升','paragraphs':[
 '11/9 VIX收19.92点，较11/6下降5.72点（−22.31%），Cboe当日页与WSJ/Investing日表交叉一致；官方历史CSV暂只到11/6。VIX收盘时刻16:15 EST／北京11/10 05:15，不能与ETF16:00时间混写。',
 '美国财政部11/9平价收益率：2年4.56%（较11/6 +5基点）、10年4.88%（+2基点），利差32基点。来源是约15:30 EST报价推导的CMT，不是实时成交或SGOV收益率。推断：风险偏好回升，但折现率压力未同步缓解。',
 '📅 10月CPI与实际收入：11/10 08:30 EST／北京今晚21:30；当前尚未公布。初请11/12、PPI11/13均08:30 EST／北京21:30；本周无预定FOMC或月度非农，下一FOMC12/8–9、非农12/4。',
 'Cisco和AMAT电话会均11/12 16:30 EST／北京11/13 05:30；电话会时间不等于公告精确分钟。Moderna 11/12分析师日仅核日期，具体小时本次未取得。NVDA11/17约16:20 EST发业绩、17:00电话会，在本次七日窗之外。',
 'SGOV官方30日SEC收益率3.84%，截至11/6、较11/5增加1基点；12个月分配收益率3.63%是另一指标，二者不是保证回报或总回报。发行人收益率日期与行情日期分开。',
 '下一常规交易日11/10，09:30–16:00 EST／北京22:30–次日05:00。11/11老兵日不在NYSE股票休市表；FiNews所述银行假日不能推导美股休市。'],'sources':[src(s['id'],s['url']) for s in macro['sources'] if s['id'] in ['nyse','cpi','bls','jobs','fed','claims','treasury','vix_official','vix_wsj','sgov','csco','amat','mrna_sec','nvda_event']]}
nvda={'title':'NVDA逆势下跌：治理风险未消除，不能直接判定低估','fact':'11/9 NVDA常规收盘178.67美元、日−4.27%；StockAnalysis为178.59美元、−4.31%。同日SMH上涨5.05%。这是11/8董事会声明之后首个常规交易日，但不能仅凭同时发生就确认全部跌幅由调查造成。','implication':'成交量为此前20日均量约3.88倍，个股风险与行业反弹分离；新投资及合作公告未披露可量化盈利贡献，不能抵销未定的治理风险。','judgment':'暂缓因跌幅而追加NVDA；本次没有证实其低估，待调查与经营现金流提供可量化依据。','counter':'董事会仍信任领导团队，且未量化订单或利润损失；若核心业务未受影响且价格已充分折价，后续可能出现研究机会。','next':'核董事会、SEC及客户订单更新，11/17财报后重看收入质量与资本投入；不把当前行情当调查结论或自动套用ETF观察档。','sources':[src('NVIDIA董事会11/8声明','https://nvidianews.nvidia.com/news/statement-from-nvidia-board-of-directors'),src('NVDA11/9第二来源','https://stockanalysis.com/stocks/nvda/history/'),src('NVDA本次Yahoo日线',m['NVDA']['source_url']),company[1]['sources'][1]]}
valuation={'title':'四股条件估值跟踪｜价格更新，旧模型不自动变成新估值','paragraphs':['11/9常规收盘Yahoo／StockAnalysis（美元）：NOW102.76／102.75、CRM214.94／214.90、GEHC84.03／84.09、CGNX50.34／50.33。四项均仍高于11/5条件模型的基准八折研究价；这里仅把新价格与旧假设作比较，未声称今日完成四套重估。','既有基准价值／基准八折研究价（美元）：NOW83.30／66.64、CRM183.93／147.14、GEHC现金流法68.68／54.94、CGNX31.98／25.58。GEHC另有盈利法90／72，不能将两个方法平均成确定低估；这些是条件研究数值，不是买入指令或保证损失上限。','11/9读取范围内未见四家新实质经营申报，NOW Form144仅为计划出售通知。CGNX RealSense交割尚未确认，含收购的完整重估仍未完成，旧情景保持条件属性；出现经营、融资或稀释新证据时须更新分母，不能只按股价跌幅下调买价。'],'sources':[src(s+'第二来源历史','https://stockanalysis.com/stocks/'+s.lower()+'/history/') for s in ['NOW','CRM','GEHC','CGNX']]}
items=[rd(P/'market_item.json'),nvda]+social['items'][:1]
brief={'schema_version':1,'report_date':'2026-11-10','market_session':'2026-11-09','reviewed_at':now,'summary':'⏳ 反弹后继续观察，今晚21:30看CPI。QQQM回撤约11%，已离开接近区间；NVDA逆势下跌，治理风险仍待核。新增TEAM的FDE商业化证据及现金流反证。','items':items,'sections':rd(P/'market_sections.json')+[calendar]+company+[valuation]+social['sections']+retained}
seedpath=SITE/'worker/seed.json';seed=rd(seedpath);before=copy.deepcopy(seed)
a={a['symbol']:a for g in seed['catalog']['groups'] for a in g['assets']}
assert len(a)==43 and sum(x['kind']=='fund' for x in a.values())==17
assert not {'QQQ','PDD','DDL','BABA','XPEV','TCEHY','KWEB'}&set(a)
sg=a['SGOV']['facts'];sg.update(sec_yield_pct=3.84,sec_yield_date='2026-11-06')
sg['notes']=[v for v in sg['notes'] if 'SEC收益率' not in v]+['30日SEC收益率3.84%，截至2026-11-06、本次11/10核验；12个月分配收益率3.63%口径不同，均不等于未来总回报。']
g=a['GOOGL'];g['research_status']='11/10补核Q3现金流与TPU周转敏感性；未证实低估，旧研究价暂停'
g['next']='核TPU销售与租赁结构、回款条款、预付款及维护/增长资本开支，再更新完整估值；本次敏感性假设不能当公司指引。'
g['facts']['notes'].append('11/10研究推进：重新读取Q2/Q3差分，Q3 FCF−90.65亿美元；SBC86.30亿。FCF减SBC−176.95亿仅为股东经济代理，不是额外现金支出或正常化预测；已含SBC的EBIT模型不能重复扣。')
g['facts']['gaps']=['TPU收入、毛利及应收/库存未单列；周转天数和25%毛利率仅为敏感性假设，完整估值尚未恢复。']
g['facts']['fact_lines'].append('11/4公告的马来西亚2027–2028年150亿美元投资计划于11/10补核；分年付款与是否已纳入集团资本开支指引未拆分，不能当已花费或额外加总。')
g['facts']['sources'].append(src('Google马来西亚11/4投资计划','https://blog.google/intl/en-my/company-news/inside-google/google-investment-malaysia-digital-infrastructure-november-2026/'))
b=a['BRK-B'];b['facts']['gaps']=['11/9 SEC已列Q3 10-Q与8-K，11/7公司官网财报不再属于SEC缺失；最新逐项13F及完整分部估值仍未完成。','11/9日元债初稿尚未定规模、票息及交割日，待最终条款。']
b['facts']['fact_lines'].append('11/9新增日元债初稿：用途包括再融资734亿及230亿日元旧债，新发行规模、票息及交割日尚空白；未确认资金到账或用于增持日本股票。')
b['next']='跟踪日元债最终条款和净融资用途；结合保险赔付及经营现金流完成分部估值，不把回购均价当内在价值。'
n=a['NVDA'];n['facts']['fact_lines']=[v.replace('11/6报价早于此事件，不能作为公告后的市场反应。','11/9首次常规交易反应见当日研究，不据此归因全部跌幅。') for v in n['facts']['fact_lines']]
n['facts']['fact_lines'].append('11/9宣布韩国互联与AI初创投资布局，未披露可量化金额或盈利贡献；11/8 NVLink Fusion合作预计2028部署，属于计划，非已实现收入。')
for sym,sources in [('GOOGL',company[0]['sources']),('BRK-B',company[1]['sources'][:1]),('NVDA',company[1]['sources'][1:])]:
 seen={s['url'] for s in a[sym]['facts']['sources']}
 for s in sources:
  if s['url'] not in seen:a[sym]['facts']['sources'].append(dict(s,asof='2026-11-10复核；披露日期见原文'))
old={x['symbol']:x for gr in before['catalog']['groups'] for x in gr['assets']}
changed=[s for s in a if a[s]!=old[s]]
assert set(changed)=={'SGOV','GOOGL','NVDA','BRK-B'}
assert seed['risk_metrics']==before['risk_metrics']
assert all(a[s]['quote']==old[s]['quote'] and a[s].get('extended')==old[s].get('extended') for s in a)
for obj in [brief,seed]:
 t=json.dumps(obj,ensure_ascii=False)
 for v in ['portfolio_private','30,000','30000美元','账户号','我的持仓','已持有GOOG']:
  assert v not in t,v
save(SITE/'worker/daily-brief.json',brief);save(seedpath,seed);save(P/'daily_brief_published_candidate.json',brief)
save(P/'assembly_audit.json',{'reviewed_at':now,'date':'2026-11-10','session':'2026-11-09','items':len(items),'sections':len(brief['sections']),'changed_research_symbols':changed,'quotes_changed':False,'risk_metrics_changed':False,'private_data_imported':False,'watchlist_symbols_added':[]})
print({'date':brief['report_date'],'headlines':len(items),'sections':len(brief['sections']),'changed':changed})
