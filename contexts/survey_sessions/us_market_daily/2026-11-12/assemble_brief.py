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
prior=rd(P/'daily_brief_before.json');seed=rd(P/'seed_before.json');before=copy.deepcopy(seed);now=datetime.now(timezone.utc).isoformat()
M={x['symbol']:x for x in rd(P/'metrics.json')};co=rd(P/'company_update.json');social=rd(P/'public_source_sections.json')
nv={'title':'NVDA盘后明显下跌：暂缓追涨，先核风险变化','fact':'11/11常规收盘173.73美元、涨2.87%；盘后Yahoo在18:29 EST（北京11/12 07:29）报160.24美元、较同日收盘−7.76%；StockAnalysis在18:27 EST报159.46美元、−8.21%。不同时间报价有差异，盘后尚未结束。','implication':'半导体常规时段强反弹后再次出现价格压力，可能扰动科技ETF与行业预期。公司官网可读的治理披露仍是11/10聘请独立调查律师；本次未核到新的调查结论、管理层变更或量化财务影响，不能把全部跌幅归因于未确认传闻。','judgment':'暂缓因常规收盘反弹追加半导体或科技集中暴露；价格跌幅不能代替对订单、现金流和治理风险的估值。盘后参考不用于改写QQQM等收盘观察档。','counter':'Yahoo分钟柱成交量为0，可能是延续报价；两来源不在同一时刻，不能当作同步可成交价格。也未确认新的经营指引下调，盘后跌幅不保证下一日开盘幅度。','next':'看下一常规交易日成交与公司独立调查的实质结论；按官方安排跟踪11/17财报。若没有新经营损害且价格/现金流证据改善，再重新评估，不将传闻当事实。','sources':[src('Yahoo本次盘后分钟数据','https://query1.finance.yahoo.com/v8/finance/chart/NVDA?range=5d&interval=1m&includePrePost=true'),src('NVDA第二来源及明确时间','https://stockanalysis.com/stocks/nvda/history/'),src('独立董事11/10官方声明','https://nvidianews.nvidia.com/news/statement-from-the-independent-members-of-the-nvidia-board')]}
market={'title':'QQQM收复200日线，但单日反弹仍不足以确认转势','fact':f"11/11标普500+{M['^GSPC']['day_pct']:.2f}%、纳斯达克100+{M['^NDX']['day_pct']:.2f}%；QQQM收284.23美元、+2.29%，距52周盘中高点回撤9.51%，高于200日线{M['QQQM']['ma200']:.2f}美元。三项收盘观察均无新触发。",'implication':f"11行业ETF加SMH共11涨1跌；SMH+4.82%、XLK+3.23%，修复范围扩大。QQQM成交量仅此前20日均量{M['QQQM']['volume_vs_prior20']:.2f}倍，尚缺强量能确认；老兵日债市缺新官方收益率，不能据股涨推断折现率已下降。",'judgment':'继续观察、暂缓追涨。趋势判断较昨日改善，但仍等待持续站稳均线、盘后风险消化与盈利兑现；15%／25%只是研究条件，不是自动交易。','counter':'行业多数上涨且VIX降至17.49，确实削弱短线悲观情景；若后续回踩保持、现金流改善，等待的理由会减弱。VIX描述期权波动预期，不直接证明股票便宜。','next':'11/12初请及Cisco/Applied Materials盘后业绩，11/13 PPI；下一次核QQQM是否继续守住200日线。BRK.B新高更新观察价，不视为独立买点。','sources':[src('QQQM第二来源','https://stockanalysis.com/etf/qqqm/history/'),src('Yahoo本次指数日线',M['^GSPC']['source_url']),src('Cboe VIX','https://www.cboe.com/tradable-products/vix'),src('财政部每日收益率','https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?field_tdr_date_value=202611&type=daily_treasury_yield_curve')]}
retained=[copy.deepcopy(s) for s in prior['sections'] if s['title'].startswith(('11/10研究留存','11/8研究留存','11/5估值专题留存','FDE上市公司','AI应用专题','11/7研究留存','既有研究留存'))]
for s in retained:
 s['paragraphs']=[t.replace('本日无可据以恢复旧买价的新经营披露','当时未取得可据以恢复旧买价的新经营披露') for t in s['paragraphs']]
valuation={'title':'四股条件估值跟踪｜11/11价格，11/5模型假设','paragraphs':['11/11常规收盘（美元）：NOW102.76、CRM218.01、GEHC82.60、CGNX51.72，Yahoo与StockAnalysis一致至美分。四项仍高于既有基准八折研究价，本次仅更新报价比较，不声称完成新一轮估值。','11/5基准价值／基准八折研究价（美元）：NOW83.30／66.64、CRM183.93／147.14、GEHC现金流法68.68／54.94、CGNX31.98／25.58。GEHC另有盈利法90／72，分母不同不能平均；折扣依赖经营假设，不是最大损失保证。','本日SEC不接收新申报，不能把新申报为空说成没有公司动态。财报/股数/SBC/负债或CGNX收购状态变化时须重估；AI应用增长不自动等于老股东每股现金流增长。具体经营复核范围见公司章节。'],'sources':[src(s+'历史价格','https://stockanalysis.com/stocks/'+s.lower()+'/history/') for s in ['NOW','CRM','GEHC','CGNX']]}
credit=copy.deepcopy(next(s for s in prior['sections'] if s['title'].startswith('信用风险')));credit['title']='11/11研究留存｜NYFed债务存量与新增逾期流量'
items=[nv,market]+co.get('headline_candidates',[])[:1]
assert len(items)<=3
brief={'schema_version':1,'report_date':'2026-11-12','market_session':'2026-11-11','reviewed_at':now,'summary':'⚠️ 暂缓追涨：QQQM回撤缩至9.51%、收复200日线，但NVDA盘后约跌8%，价格与治理风险需继续核实。三项收盘观察档无新触发，研究与盘后参考分别标时。','items':items,'sections':rd(P/'market_sections.json')+rd(P/'macro_public_sections.json')+rd(P/'public_company_sections.json')+[valuation]+social['sections']+[credit]+retained}
a={a['symbol']:a for g in seed['catalog']['groups'] for a in g['assets']};assert len(a)==43
sg=a['SGOV']['facts'];sg.update(sec_yield_pct=3.85,sec_yield_date='2026-11-10')
sg['notes']=[v for v in sg['notes'] if 'SEC收益率' not in v]+['30日SEC收益率3.85%，截至2026-11-10，本次11/12复核；数值与前次相同。12个月分配收益率另有口径，均非未来总回报保证。']
for s in sg['sources']:
 if 'SEC收益率' in s['title']:s['asof']='SEC收益率2026-11-10，11/12读取；其他字段各自日期'
old={v['symbol']:v for g in before['catalog']['groups'] for v in g['assets']};changed=[s for s in a if a[s]!=old[s]]
assert set(changed)=={'SGOV'} and seed['risk_metrics']==before['risk_metrics']
assert all(a[s]['quote']==old[s]['quote'] and a[s].get('extended')==old[s].get('extended') for s in a)
assert len([v for v in a.values() if v['kind']=='fund'])==17
assert not set(a)&{'QQQ','PDD','DDL','BABA','XPEV','TCEHY','KWEB'}
for obj in [brief,seed]:
 txt=json.dumps(obj,ensure_ascii=False)
 for bad in ['portfolio_private','30,000','30000美元','账户号','我的持仓','已持有GOOG']:assert bad not in txt,bad
save(bp,brief);save(sp,seed);save(P/'daily_brief_published_candidate.json',brief)
save(P/'assembly_audit.json',{'reviewed_at':now,'items':len(brief['items']),'sections':len(brief['sections']),'changed_research_symbols':changed,'quotes_changed':False,'risk_metrics_changed':False,'private_data_imported':False,'watchlist_symbols_added':[]})
print({'date':brief['report_date'],'headlines':len(brief['items']),'sections':len(brief['sections']),'changed':changed})
