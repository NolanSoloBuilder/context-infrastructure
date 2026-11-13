import json, csv, hashlib
from pathlib import Path
from datetime import datetime, timezone

P=Path(__file__).parent
ROOT=P.parent
M={x['symbol']:x for x in json.loads((P/'metrics.json').read_text())}
NOW=datetime.now(timezone.utc).isoformat()
def save(name,obj): (P/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def src(title,url): return {'title':title,'url':url}
def yf(s): return src(s+' Yahoo本次日线',M[s]['source_url'])
def sa(s): return 'https://stockanalysis.com/'+('etf/' if s in ['QQQM','VOO','SOXX','XSW'] else 'stocks/')+s.lower().replace('-','.')+'/history/'
prices={'QQQM':270.15,'VOO':676.13,'BRK-B':570.96,'NOW':101.98,'CRM':213.65,'GEHC':82.39,'CGNX':47.70,'MRNA':254.15,'GOOGL':284.68,'SOFI':16.20,'SOXX':136.43,'XSW':202.17}
verify={'report_date':'2026-11-07','market_session':'2026-11-06','reviewed_at':NOW,'currency':'USD','regular_quote_comparisons':[{'symbol':s,'yahoo_close':M[s]['close'],'stockanalysis_close':v,'difference_usd':round(M[s]['close']-v,4),'source_url':sa(s),'read_scope':'dated regular close and historical table; after-hours distinguished'} for s,v in prices.items()], 'official_quote_gap':'Nasdaq QQQM historical page opened this run, says Data is currently not available. Third-party cross-checks explicitly identified.', 'additional_sources':[
 {'symbol':'QQQM','url':'https://ca.investing.com/etfs/qqqm-historical-data','regular_session':'2026-11-06','close':270.22,'high_52w':314.11,'high_date':'2026-10-06','prior_2026_11_05_close':266.85},
 {'symbol':'VOO','url':'https://raymondjames.websol.barchart.com/?0=NEWS&1_selected=etfQuote&module=etfDetail&region=US&symbol=VOO','regular_session':'2026-11-06','close':675.99,'high_52w':718.47,'high_date':'2026-10-06'},
 {'symbol':'BRK-B','url':'https://www.marketscreener.com/quote/stock/BERKSHIRE-HATHAWAY-INC-11916/quotes/','regular_session':'2026-11-06','close':570.89,'high_52w':586.30,'high_date':'2026-11-05'}],
 'prior_cross_reconciled':{'session':'2026-11-05','checked_on':'2026-11-07','close':266.85,'high_yahoo_investing':314.11,'high_stockanalysis':314.12,'d_yahoo':100*(1-266.85/314.11),'d_stockanalysis':100*(1-266.85/314.12),'finding':'StockAnalysis historical close now266.85 vs267.02 captured yesterday. Both high variants now yield D>15. Record retrospective confirmation, not a fresh crossing on11/6.'},
 'data_recovery':{'SOXX':'Provider now adjusts 11/4 close to150.13667 and full pre-split history; StockAnalysis150.14 supports. 11/5 close131.90 means -12.15%, not the mixed-unit -70%. No manual adjustment. Current close136.53 vs136.43 remains disclosed.','XSW':'11/5 high corrected to211.65, now encloses open211.65 and close203.85. Historical OHLC validation passes. Current close202.67 vs StockAnalysis202.17 differs; automatic source retained, exact close unresolved.'}}
save('verification.json',verify)

rows=[]
for public,s in [('QQQM','QQQM'),('VOO','VOO'),('BRK.B','BRK-B')]:
 m=M[s];D=-m['drawdown_pct'];level=m['high_52w']*.85;rows.append(f"{public}：11/6收盘{m['close']:.2f}美元，日{m['day_pct']:+.2f}%；52周盘中高点{m['high_52w']:.2f}（{m['high_date']}），回撤{D:.3f}%。15%/25%观察价{m['level_15']:.2f}/{m['level_25']:.2f}美元；距第一档{15-D:.3f}个百分点，从现价到15%价需变化{100*(level/m['close']-1):+.3f}%。")
alert={'title':'🔎 接近第一观察档｜QQQM补核11/5跨档，11/6回到约14%回撤','paragraphs':[
 '回撤用各自滚动52周盘中高点，窗口为(交易日−364天,交易日]；价格均为美国11/6常规收盘、美元。百分点距离与价格变化百分比分开。',*rows,
 'QQQM 11/5的StockAnalysis历史收盘已由昨日所读267.02修正至266.85，与Yahoo/Investing一致；高点314.11或314.12均使当日回撤超过15%。因此今天补记11/5曾达到第一档，11/6反弹后回到near_15，不把昨日待核说成当时已确认，也不把今天写成新向下跨档。',
 '11/6仍有小额跨源收盘差异：QQQM270.22/270.15、VOO675.99/676.13、BRK.B570.89/570.96（前者Yahoo统一序列，后者StockAnalysis）；已分别取得Investing、Barchart、MarketScreener支持前者，高点差异不改变当前分档。官方可比收盘本次未读到，属于第三方核验。',
 '判断：继续观察，暂不因一次反弹加快追加。QQQM仍低于200日线，下一条件是CPI与更广泛的行业企稳；BRK.B单一公司另外等11/7公司披露。15%/25%是研究条件，不指定买入金额或保证盈利。'
 ],'sources':[src('QQQM最新历史及11/5修正',sa('QQQM')),src('Investing QQQM历史',verify['additional_sources'][0]['url']),src('Barchart VOO历史',verify['additional_sources'][1]['url']),src('MarketScreener BRK.B历史',verify['additional_sources'][2]['url'])]}
save('public_alert_section.json',alert)

sector_names={'XLK':'科技','XLC':'通信服务','XLY':'可选消费','XLP':'必需消费','XLV':'医疗','XLF':'金融','XLI':'工业','XLE':'能源','XLU':'公用事业','XLB':'材料','XLRE':'房地产','SMH':'半导体'}
ordered=sorted(sector_names,key=lambda s:M[s]['day_pct'],reverse=True)
idx=M['^GSPC'];table=[];paras=[]
for s in ordered:
 m=M[s];r={'symbol':s,'name':sector_names[s]}
 for k in ['day_pct','five_session_pct','twenty_one_session_pct']:
  r[k]=m[k];r['relative_'+k]=m[k]-idx[k]
 table.append(r);paras.append(f"{s} {sector_names[s]}：日{m['day_pct']:+.2f}%／5交易日{m['five_session_pct']:+.2f}%／21交易日{m['twenty_one_session_pct']:+.2f}%；相对标普分别{r['relative_day_pct']:+.2f}／{r['relative_five_session_pct']:+.2f}／{r['relative_twenty_one_session_pct']:+.2f}个百分点。")
with (P/'sector_summary.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(table[0]));w.writeheader();w.writerows(table)
q=M['QQQM'];v=M['VOO'];count=sum(M[s]['day_pct']>0 for s in ordered)
market=[{'title':'指数与趋势｜反弹仍未修复纳指100长期均线','paragraphs':[
 *[f"{label}：{M[s]['close']:,.2f}点；日{M[s]['day_pct']:+.2f}%／5交易日{M[s]['five_session_pct']:+.2f}%／21交易日{M[s]['twenty_one_session_pct']:+.2f}%。" for s,label in [('^GSPC','标普500'),('^IXIC','纳斯达克综合（环境参考）'),('^NDX','纳斯达克100')]],
 f"QQQM MA50/200为{q['ma50']:.2f}/{q['ma200']:.2f}美元，偏离{q['vs_ma50_pct']:+.2f}%/{q['vs_ma200_pct']:+.2f}%；成交量为此前20日均量{q['volume_vs_prior20']:.2f}倍。VOO MA50/200为{v['ma50']:.2f}/{v['ma200']:.2f}，偏离{v['vs_ma50_pct']:+.2f}%/{v['vs_ma200_pct']:+.2f}%。",'11/6较11/5收盘；周/月用5与21个交易日价格表现，未计分红，均线用拆股调整Close。在线1/2/3年累计回报使用含分红复权Adj Close代理，二者不同。趋势与量能为Yahoo单序列，不能据反弹认定见底。'],'sources':[yf(s) for s in ['^GSPC','^IXIC','^NDX','QQQM','VOO']]},
 {'title':'行业观察｜科技反弹，广度仍窄','paragraphs':[f"11行业加SMH共12项，仅{count}项上涨。SMH日{M['SMH']['day_pct']:+.2f}%、21日{M['SMH']['twenty_one_session_pct']:+.2f}%；XLK日{M['XLK']['day_pct']:+.2f}%、21日{M['XLK']['twenty_one_session_pct']:+.2f}%。半导体和科技仍需观察能否持续修复，而非一天反弹就上调盈利估值。",f"XLC通信服务日{M['XLC']['day_pct']:+.2f}%、21日{M['XLC']['twenty_one_session_pct']:+.2f}%；含广告、内容和平台业务，不能整体当作纯AI应用。XLP日{M['XLP']['day_pct']:+.2f}%、21日{M['XLP']['twenty_one_session_pct']:+.2f}%，防御领域短期也回落。",'价格分化不等于资金净流入。SMH/XLK和头部公司存在经济暴露重叠；研究优先看盈利、交付与现金回收，单日领涨不构成买点。'],'sources':[yf(s) for s in ['SMH','XLK','XLC','XLP']]},
 {'title':'行业完整比较｜日／5交易日／21交易日与相对标普','paragraphs':['基准为标普500价格指数^GSPC；相对值是收益率差，单位百分点，不是资金流。',*paras],'sources':[yf('^GSPC'),yf('SMH')]},
 {'title':'数据修正与口径｜SOXX及XSW恢复完整序列','paragraphs':['本次43项完整日线均通过既有引擎检查。SOXX提供方已把11/4及以前历史统一到3:1拆股后单位，11/4收盘约150.1367、11/5为131.90；11/5真实价格变化约−12.15%，不使用昨日混合单位导致的−70%假跌幅。MA50/200仍为50/200交易日，未手工猜测复权。','XSW 11/5最高价已从209.00更正至211.65，与开盘211.65一致，原OHLC矛盾已消除。11/6 Yahoo收202.67、StockAnalysis收202.17，后者盘后16:15为202.67；同日收盘定义差异仍未查明，自动页面保留来源标注，不称精确收盘完全一致。SOXX11/6收136.53/136.43亦有0.10差异。','本地保留原始序列、关键交叉核验、真实60交易日归一走势/各历史日当时52周盘中高点回撤图、行业图与CSV；线上曲线按1/2/3年交互，旧归档不被今日研究覆盖。MRNA历史收益仍受8/19异常大涨主导，事件原因未核原披露，不当未来收益预期。'],'sources':[src('SOXX历史',sa('SOXX')),src('XSW修正历史',sa('XSW')),yf('SOXX'),yf('XSW')]}]
save('market_sections.json',market)

e=json.loads((P/'extended_quotes.json').read_text());obs={x['symbol']:x for x in e['observations']}
post_ref={'QQQM':(270.75,'18:18'),'VOO':(676.87,'18:30'),'BRK-B':(571.63,'18:11'),'GOOGL':(285.58,'18:25'),'SOFI':(16.20,'18:02'),'MRNA':(256.66,'18:24')}
ep=['采集北京时间'+e['captured_at_beijing']+'。以下均为11/6盘后，美东EST与北京时间分别标注；盘后仍未结束（至北京时间09:00），无20:00–04:00券商夜盘。下一交易日11/9盘前尚未开始。']
for s,(price,time) in post_ref.items():
 o=obs[s];post=o['post'];ep.append(f"{s}：常规收盘{o['regular_close_usd']:.2f}美元；Yahoo盘后{post['price_usd']:.2f}，较同日收盘{post['change_vs_reference_pct']:+.2f}%，美东{post['bar_start_et']}／北京时间{post['bar_start_beijing']}；StockAnalysis另报{price:.2f}（11/6美东{time}）。不同时间参考并列，不能称成交一致。")
ep.append('所列Yahoo分钟柱成交量为0，可能是延续报价；不声称最新实际成交或最终盘后收盘。盘后不更新收盘提醒档位。')
save('public_extended_section.json',{'title':'盘后观察｜11/6各自时刻参考，非最终收盘','paragraphs':ep,'sources':[src(s+'第二来源含时刻盘后',sa(s)) for s in post_ref]})

state=json.loads((ROOT/'alert_state.json').read_text());save('alert_state_before.json',state)
def stage_for(d):
 if d>=25:return 'at_or_above_25'
 if d>=23:return 'near_25'
 if d>=15:return 'at_or_above_15'
 if d>=13:return 'near_15'
 return 'below_13'
event_id='QQQM:2026-11-05:15:retrospective-confirmation'
already_reported=event_id in state.get('reported_event_ids',[])
highlights=[]
for key,s in [('QQQM','QQQM'),('VOO','VOO'),('BRK.B','BRK-B')]:
 m=M[s];x=state['symbols'][key];D=-m['drawdown_pct'];stage=stage_for(D);previous=x['stage'];fresh=key=='QQQM' and not already_reported
 if fresh:highlights.append(key)
 x.update(last_checked_session='2026-11-06',close_usd=m['close'],high_52w_usd=m['high_52w'],high_date=m['high_date'],drawdown_pct=D,stage=stage,previous_stage=previous,level_15_usd=m['level_15'],level_25_usd=m['level_25'],gap_to_15_percentage_points=15-D,price_change_to_15_pct=100*(m['high_52w']*.85/m['close']-1),new_highlight=fresh)
 if key=='QQQM':
  x.update(stage_since_session='2026-11-06',last_highlight_report_date='2026-11-07',previous_verified_market_stage='at_or_above_15',highlight_reason='retrospective confirmation of11/5 crossing, current11/6 return to near_15')
  if not already_reported:state.setdefault('resolved_checks',{})[key]={'resolved_session':'2026-11-06','resolved_at_utc':NOW,'old_deferred_check':state.get('deferred_checks',{}).pop(key,None),'basis':verify['prior_cross_reconciled']}
if not already_reported:state.setdefault('reported_event_ids',[]).append(event_id)
state.update(last_checked_session='2026-11-06',report_date_beijing='2026-11-07',updated_at_utc=NOW,highlighted_symbols=highlights)
state['data_validation']={'watchlist_closes_verified':True,'status':'third_party_corroborated_current_stages_prior_QQQM_cross_reconciled','fully_valid_symbols':['QQQM','VOO','BRK.B'],'deferred_symbols':[],'verification_file':str((P/'verification.json').resolve()),'site_url':'https://nolan-market-watch.choice-calf-0415.chatgpt.site/'}
save('alert_state_proposal.json',state)
print('Prepared current market sections, audit comparisons and alert proposal; global alert state not yet modified.')
