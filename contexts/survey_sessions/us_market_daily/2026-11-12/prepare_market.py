import json,csv,re,copy
from pathlib import Path
from datetime import datetime,timezone
P=Path(__file__).resolve().parent;R=P.parent
M={x['symbol']:x for x in json.loads((P/'metrics.json').read_text())};NOW=datetime.now(timezone.utc).isoformat()
def save(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def src(t,u):return {'title':t,'url':u}
def yf(s):return src(s+'本次Yahoo日线',M[s]['source_url'])
def sa(s):return 'https://stockanalysis.com/'+('etf/' if s in ['QQQM','VOO'] else 'stocks/')+s.lower().replace('-','.')+'/history/'
second={};highs={'QQQM':314.12,'VOO':718.47,'BRK-B':588.54}
for s in ['QQQM','VOO','BRK-B','NVDA','GOOGL','SOFI','NOW','CRM','GEHC','CGNX']:
 t=(P/'market_crosscheck_raw'/(s.lower().replace('-','.')+'.txt')).read_text();t=t[t.index('Date'):];v=t[t.index('Nov 11, 2026'):].splitlines();second[s]=float(v[4].replace(',',''))
verify={'reviewed_at':NOW,'report_date':'2026-11-12','market_session':'2026-11-11','currency':'USD','quote_comparisons':[{'symbol':s,'yahoo_close_usd':M[s]['close'],'stockanalysis_close_usd':v,'difference_usd':round(M[s]['close']-v,4),'url':sa(s)} for s,v in second.items()],'high_comparisons':[{'symbol':s,'yahoo_high':M[s]['high_52w'],'stockanalysis_high':h,'date_both':M[s]['high_date'],'drawdown_secondary_pct':100*(1-second[s]/h)} for s,h in highs.items()],'official_gap':'Nasdaq QQQM historical page read today: Data is currently not available. Key prices cross-checked using third parties, not official auction certification.','errors':json.loads((P/'manifest.json').read_text())['errors']}
assert all(abs(M[s]['close']-v)<.005 for s,v in second.items());save('verification.json',verify)
state=json.loads((R/'alert_state.json').read_text());save('alert_state_before.json',state)
def stage(d):return 'at_or_above_25' if d>=25 else 'near_25' if d>=23 else 'at_or_above_15' if d>=15 else 'near_15' if d>=13 else 'below_13'
lines=[]
for key,s in [('QQQM','QQQM'),('VOO','VOO'),('BRK.B','BRK-B')]:
 m=M[s];d=100*(1-m['close']/m['high_52w']);d2=100*(1-second[s]/highs[s]);assert stage(d)==stage(d2)=='below_13'
 old=state['symbols'][key];prev=old['stage'];old.update(last_checked_session='2026-11-11',close_usd=m['close'],high_52w_usd=m['high_52w'],high_date=m['high_date'],drawdown_pct=d,stage=stage(d),previous_stage=prev,level_15_usd=m['level_15'],level_25_usd=m['level_25'],gap_to_15_percentage_points=15-d,price_change_to_15_pct=100*(m['level_15']/m['close']-1),new_highlight=False)
 if stage(d)!=prev:old['stage_since_session']='2026-11-11'
 old['verification_note']='Fresh Yahoo/StockAnalysis regular closes agree to cents; high differences disclosed and both yield below_13. BRK.B new high date agrees; magnitude difference $0.06.'
 lines.append(f"{key}：11/11常规收盘{m['close']:.2f}美元（日{m['day_pct']:+.2f}%）；52周盘中高点{m['high_52w']:.2f}美元／{m['high_date']}，回撤{d:.2f}%。15%／25%观察价{m['level_15']:.2f}／{m['level_25']:.2f}美元。距15%尚差{15-d:.2f}个百分点；当前价格到15%观察价还需变化{old['price_change_to_15_pct']:+.2f}%。仍低于13%接近区间，无新触发。")
state.update(last_checked_session='2026-11-11',report_date_beijing='2026-11-12',updated_at_utc=NOW,highlighted_symbols=[])
state['data_validation']={'watchlist_closes_verified':True,'status':'third_party_crosschecked_same_stages_high_differences_disclosed','fully_valid_symbols':['QQQM','VOO','BRK.B'],'deferred_symbols':[],'verification_file':str(P/'verification.json')};save('alert_state_proposal.json',state)
alerts={'title':'收盘观察档｜无新触发，BRK.B继续更新高点','paragraphs':lines+['BRK.B两源均确认11/11新高：Yahoo588.48、StockAnalysis588.54美元，日期一致；采用Yahoo同序列后观察价更新为500.21／441.36美元。0.06美元差异不改变分档，更新高点不是买入信号。','三项收盘两源一致至美分。QQQM高点314.11／314.12美元（10/6），VOO高点718.47一致（10/6）；保留高点差异，不称官方认证。','回撤采用各标的当时滚动52周盘中High，均线用拆股一致Close、不含分红。到目标的价格变化按显示美分观察价复算；百分点差与价格涨跌百分比不同。盘后不改收盘分档；BRK.B按单一公司研究，不套ETF仓位。'],'sources':[src(s+'第二来源历史',sa(s)) for s in highs]+[src('Nasdaq历史页本次无数据','https://www.nasdaq.com/market-activity/etf/qqqm/historical')]}
q=M['QQQM'];v=M['VOO']
market={'title':'指数与趋势｜收复200日线，尚需持续性验证','paragraphs':[*[f"{label}：{M[s]['close']:,.2f}点；日{M[s]['day_pct']:+.2f}%／5交易日{M[s]['five_session_pct']:+.2f}%／21交易日{M[s]['twenty_one_session_pct']:+.2f}%。" for s,label in [('^GSPC','标普500'),('^IXIC','纳斯达克综合（环境参考）'),('^NDX','纳斯达克100')]],f"QQQM MA50／200为{q['ma50']:.2f}／{q['ma200']:.2f}美元，偏离{q['vs_ma50_pct']:+.2f}%／{q['vs_ma200_pct']:+.2f}%；本日量为此前20日均量{q['volume_vs_prior20']:.2f}倍。VOO MA50／200为{v['ma50']:.2f}／{v['ma200']:.2f}美元，偏离{v['vs_ma50_pct']:+.2f}%／{v['vs_ma200_pct']:+.2f}%。",'收盘趋势改善是事实，但QQQM量能低于近期均量，英伟达盘后重新显著走弱。继续观察，暂缓因单日反弹追加科技集中暴露；若后续收盘持续站稳200日线、行业改善且公司现金流兑现，谨慎理由会减弱。','日／5日／21日为拆股一致价格收益，不含分红；网站1／2／3年总回报为Adj Close复权代理，指标与研究日期分别展示。'],'sources':[yf(s) for s in ['^GSPC','^IXIC','^NDX','QQQM','VOO']]}
names={'XLK':'科技','XLC':'通信','XLY':'可选消费','XLP':'必需消费','XLV':'医疗','XLF':'金融','XLI':'工业','XLE':'能源','XLU':'公用事业','XLB':'材料','XLRE':'房地产','SMH':'半导体'};rows=[];paras=[]
for s,n in names.items():
 m=M[s];row={'symbol':s,'name':n}
 for k in ['day_pct','five_session_pct','twenty_one_session_pct']:row[k]=m[k];row['relative_'+k]=m[k]-M['^GSPC'][k]
 rows.append(row);paras.append(f"{s} {n}：日{row['day_pct']:+.2f}%／5日{row['five_session_pct']:+.2f}%／21日{row['twenty_one_session_pct']:+.2f}%；相对标普{row['relative_day_pct']:+.2f}／{row['relative_five_session_pct']:+.2f}／{row['relative_twenty_one_session_pct']:+.2f}个百分点。")
with (P/'sector_summary.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
up=sum(r['day_pct']>0 for r in rows);order=sorted(rows,key=lambda x:x['day_pct'],reverse=True)
sector={'title':'行业观察｜半导体反弹，关注盘后反复','paragraphs':[f"12项观察{up}涨{12-up}跌；涨幅前列："+'，'.join(f"{r['symbol']} {r['name']}{r['day_pct']:+.2f}%" for r in order[:3])+'。价格变化不是资金净流入证据。',f"SMH半导体日{M['SMH']['day_pct']:+.2f}%、21日{M['SMH']['twenty_one_session_pct']:+.2f}%；XLK科技日{M['XLK']['day_pct']:+.2f}%、21日{M['XLK']['twenty_one_session_pct']:+.2f}%。本日强反弹未消除近期回撤，NVDA盘后异动不纳入这张常规收盘行业图。",f"XLC通信日{M['XLC']['day_pct']:+.2f}%，与Google盈利/现金回款继续对照；XLV医疗日{M['XLV']['day_pct']:+.2f}%，不能用主题表现替代GEHC个体现金转化。观察半导体持续性、软件AI付费与医疗兑现，单日领涨不是买点。"],'sources':[yf(s) for s in ['SMH','XLK','XLC','XLV']]}
full={'title':'行业完整比较｜日／5交易日／21交易日','paragraphs':['11/11已完成常规时段；相对标普500价格指数，差值为百分点。',*paras],'sources':[yf('^GSPC'),yf('SMH')]}
e=json.loads((P/'extended_quotes.json').read_text());obs={x['symbol']:x for x in e['observations']};post2={'QQQM':(282.00,'18:28'),'VOO':(695.85,'18:28'),'BRK-B':(590.98,'18:22'),'NVDA':(159.46,'18:27'),'GOOGL':(296.59,'18:28'),'SOFI':(16.29,'16:59')}
ep=[f"本轮采集北京时间{e['captured_at_beijing']}。11/11盘后仍进行，11/12北京时间09:00结束；以下不是最终盘后收盘。11/12盘前尚未开始（北京17:00起），常规开盘北京22:30。不含20:00–04:00券商夜盘。"]
for s,(p,t) in post2.items():
 a=obs[s]['post'];ep.append(f"{s}：常规收盘{M[s]['close']:.2f}美元；Yahoo盘后{a['price_usd']:.2f}（相对同日收盘{100*(a['price_usd']/M[s]['close']-1):+.2f}%），美东{a['bar_start_et']}／北京{a['bar_start_beijing']}。StockAnalysis另报{p:.2f}美元，11/11 {t} EST；时间不同，不能声称同笔成交一致。")
ep+=['Yahoo上述分钟柱成交量为0，可能是延续参考，不能证明对应时刻新实际成交。NVDA第二源18:21为157.99美元、18:27为159.46美元，与Yahoo18:29的160.24不同，表明报价/时间变化，应保留时间与差异；盘后跌幅不保证次日开盘幅度，也不更新收盘提醒。']
ext={'title':'盘后观察｜NVDA明显走弱，11/11盘后尚未结束','paragraphs':ep,'sources':[src(s+'带时间第二来源',sa(s)) for s in post2]}
gaps={'title':'核验范围｜43项当日有效，盘后与估值各有边界','paragraphs':['本地全部43项与额外行业/指数本次日线采集成功、OHLC有效；云端同源刷新43/43成功至11/11。云端自动采集仍为Yahoo单源，不等于43项完成独立跨源核验。','QQQM、VOO、BRK.B及NVDA、GOOGL、SOFI、NOW、CRM、GEHC、CGNX共10项重要收盘与StockAnalysis一致至美分。高点差异见观察档；均线和量能仍为Yahoo单源计算。','真实60交易日趋势/滚动回撤和12项行业图与CSV保留本地审计，网站1／2／3年交互区间不变。MRNA历史大跳变仍主导部分历史指标，不能当未来收益；股价刷新也不意味着旧估值模型已重算。'],'sources':[yf('QQQM'),src('第二来源','https://stockanalysis.com/etf/qqqm/history/')]}
save('market_sections.json',[alerts,market,sector,full,ext,gaps]);save('session_check.json',{'checked_at':NOW,'report_date_beijing':'2026-11-12','latest_completed_regular_session':'2026-11-11','next_session':'2026-11-12','next_open_et':'2026-11-12T09:30:00-05:00','next_open_beijing':'2026-11-12T22:30:00+08:00','next_premarket_status':'not_started','postmarket_at_capture':'in_progress','calendar_url':'https://www.nyse.com/trade/hours-calendars','archival_key':'2026-11-11'})
print({'alerts':state['highlighted_symbols'],'qqqm_drawdown':-M['QQQM']['drawdown_pct'],'sectors_up':up,'closes_crosschecked':len(second)})
