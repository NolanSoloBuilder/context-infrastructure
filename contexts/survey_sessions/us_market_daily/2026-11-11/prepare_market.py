import json,csv,copy
from pathlib import Path
from datetime import datetime,timezone
P=Path(__file__).resolve().parent;R=P.parent
M={x['symbol']:x for x in json.loads((P/'metrics.json').read_text())};NOW=datetime.now(timezone.utc).isoformat()
def save(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def src(t,u):return {'title':t,'url':u}
def yf(s):return src(s+'本次Yahoo日线',M[s]['source_url'])
def sa(s):return 'https://stockanalysis.com/'+('etf/' if s in ['QQQM','VOO'] else 'stocks/')+s.lower().replace('-','.')+'/history/'
second={'QQQM':277.88,'VOO':689.40,'BRK-B':583.62,'NVDA':168.78,'GOOGL':287.44,'SOFI':16.37,'NOW':99.59,'CRM':213.48,'GEHC':83.68,'CGNX':50.79}
highs={'QQQM':314.12,'VOO':718.47,'BRK-B':586.45}
verify={'reviewed_at':NOW,'report_date':'2026-11-11','market_session':'2026-11-10','currency':'USD','quote_comparisons':[{'symbol':s,'yahoo_close_usd':M[s]['close'],'stockanalysis_close_usd':v,'difference_usd':round(M[s]['close']-v,4),'url':sa(s)} for s,v in second.items()], 'high_comparisons':[{'symbol':s,'yahoo_high':M[s]['high_52w'],'stockanalysis_high':h,'date_both':M[s]['high_date'],'drawdown_secondary_pct':100*(1-second[s]/h)} for s,h in highs.items()],'official_gap':'Nasdaq QQQM historical page: Data is currently not available. Cross-checks are third-party, not official closing-auction certification.','third_source_attempt':'MarketScreener page fetched but targeted data retrieval timed out; no third-source value used.','errors':json.loads((P/'manifest.json').read_text())['errors']}
save('verification.json',verify)
state=json.loads((R/'alert_state.json').read_text());save('alert_state_before.json',state)
def stage(d):return 'at_or_above_25' if d>=25 else 'near_25' if d>=23 else 'at_or_above_15' if d>=15 else 'near_15' if d>=13 else 'below_13'
lines=[]
for key,s in [('QQQM','QQQM'),('VOO','VOO'),('BRK.B','BRK-B')]:
 m=M[s];d=100*(1-m['close']/m['high_52w']);d2=100*(1-second[s]/highs[s]);assert stage(d)==stage(d2)=='below_13'
 old=state['symbols'][key];prev=old['stage'];old.update(last_checked_session='2026-11-10',close_usd=m['close'],high_52w_usd=m['high_52w'],high_date=m['high_date'],drawdown_pct=d,stage=stage(d),previous_stage=prev,level_15_usd=m['level_15'],level_25_usd=m['level_25'],gap_to_15_percentage_points=15-d,price_change_to_15_pct=100*(m['level_15']/m['close']-1),new_highlight=False)
 if stage(d)!=prev:old['stage_since_session']='2026-11-10'
 old['verification_note']='Yahoo/StockAnalysis close/high differences disclosed; both yield below_13; BRK.B new intraday high date agrees, magnitude differs by $0.04.'
 lines.append(f"{key}：11/10常规收盘{m['close']:.2f}美元（日{m['day_pct']:+.2f}%）；52周盘中高点{m['high_52w']:.2f}美元／{m['high_date']}，回撤{d:.2f}%。15%／25%观察价{m['level_15']:.2f}／{m['level_25']:.2f}美元。距15%尚差{15-d:.2f}个百分点；当前价格到15%观察价还需变化{old['price_change_to_15_pct']:+.2f}%。阶段：below_13，无新触发。")
state.update(last_checked_session='2026-11-10',report_date_beijing='2026-11-11',updated_at_utc=NOW,highlighted_symbols=[])
state['data_validation']={'watchlist_closes_verified':True,'status':'third_party_crosschecked_same_stages_with_disclosed_price_differences','fully_valid_symbols':['QQQM','VOO','BRK.B'],'deferred_symbols':[],'verification_file':str(P/'verification.json')}
save('alert_state_proposal.json',state)
alerts={'title':'收盘观察档｜三项均未新触发，BRK.B高点基准更新','paragraphs':lines+['BRK.B两源均确认11/10高于11/5前高：Yahoo高点586.41、StockAnalysis586.45美元，日期一致；采用Yahoo同序列后观察价更新为498.45／439.81美元。高点修订不是买入信号，0.04美元差异不改变分档。','Yahoo／StockAnalysis收盘分别为QQQM277.87／277.88、VOO689.50／689.40、BRK.B583.34／583.62美元；QQQM高点314.11／314.12美元（10/6），VOO高点718.47一致（10/6）。所有来源组合均低于13%接近区间，保留差异，不称官方价格完全一致。','回撤基准是各自滚动(日期−364天,日期]盘中High；MA采用拆股调整Close，不含分红。观察价先恢复报价至美分再按十进制计算，到目标的价格变化按显示观察价复算；审计曲线保留来源小数，两位回撤一致。盘后不改收盘分档；BRK.B按单一公司研究，不套ETF仓位。'],'sources':[src(s+'第二来源历史',sa(s)) for s in highs]+[src('Nasdaq历史页本次无数据','https://www.nasdaq.com/market-activity/etf/qqqm/historical')]}
q=M['QQQM'];v=M['VOO']
market={'title':'指数与趋势｜反弹暂停，QQQM仍低于200日线','paragraphs':[
 *[f"{label}：{M[s]['close']:,.2f}点；日{M[s]['day_pct']:+.2f}%／5交易日{M[s]['five_session_pct']:+.2f}%／21交易日{M[s]['twenty_one_session_pct']:+.2f}%。" for s,label in [('^GSPC','标普500'),('^IXIC','纳斯达克综合（环境参考）'),('^NDX','纳斯达克100')]],
 f"QQQM MA50／200为{q['ma50']:.2f}／{q['ma200']:.2f}美元，偏离{q['vs_ma50_pct']:+.2f}%／{q['vs_ma200_pct']:+.2f}%；成交量为此前20日均量{q['volume_vs_prior20']:.2f}倍。VOO MA50／200为{v['ma50']:.2f}／{v['ma200']:.2f}美元，偏离{v['vs_ma50_pct']:+.2f}%／{v['vs_ma200_pct']:+.2f}%。",
 '判断：继续观察，追加节奏暂缓。反证是本日回落量能较轻、VOO仍在200日线上方；单日调整既不证明新一轮下跌，也不保证已见底。下一步看长端利率能否回落、QQQM能否持续收复200日线及企业现金流证据。',
 '日／5日／21日为拆股一致价格收益，不含分红；网站1／2／3年总回报使用Adj Close复权代理。研究日期与自动行情刷新日期分别展示。'],'sources':[yf(s) for s in ['^GSPC','^IXIC','^NDX','QQQM','VOO']]}
names={'XLK':'科技','XLC':'通信','XLY':'可选消费','XLP':'必需消费','XLV':'医疗','XLF':'金融','XLI':'工业','XLE':'能源','XLU':'公用事业','XLB':'材料','XLRE':'房地产','SMH':'半导体'}
rows=[];paras=[]
for s,n in names.items():
 m=M[s];row={'symbol':s,'name':n}
 for k in ['day_pct','five_session_pct','twenty_one_session_pct']:row[k]=m[k];row['relative_'+k]=m[k]-M['^GSPC'][k]
 rows.append(row);paras.append(f"{s} {n}：日{row['day_pct']:+.2f}%／5日{row['five_session_pct']:+.2f}%／21日{row['twenty_one_session_pct']:+.2f}%；相对标普{row['relative_day_pct']:+.2f}／{row['relative_five_session_pct']:+.2f}／{row['relative_twenty_one_session_pct']:+.2f}个百分点。")
with (P/'sector_summary.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
sector={'title':'行业观察｜金融、能源略强，科技与半导体仍弱','paragraphs':['12项行业观察6涨6跌。XLF金融+0.52%、XLE能源+0.44%、XLC通信+0.37%，XLK科技−1.15%、SMH半导体−0.78%；涨跌分化不能证明资金净流入或轮动已确立。',f"SMH近21交易日{M['SMH']['twenty_one_session_pct']:+.2f}%、XLK{M['XLK']['twenty_one_session_pct']:+.2f}%，科技修复仍有限；金融相对强势也不能直接推出SOFI信用质量改善。",'值得继续核查：通信服务的盈利兑现、金融信用成本、半导体订单与资本回报。单日领涨不构成买点；AI应用与基础设施可以同步增长，不按价格分化替代经营证据。'],'sources':[yf(s) for s in ['XLF','XLE','XLC','XLK','SMH']]}
full={'title':'行业完整比较｜日／5交易日／21交易日','paragraphs':['11/10已完成常规时段；相对基准为标普500价格指数，差值单位为百分点。',*paras],'sources':[yf('^GSPC'),yf('SMH')]}
e=json.loads((P/'extended_quotes.json').read_text());obs={x['symbol']:x for x in e['observations']};post2={'QQQM':(279.00,'18:33'),'VOO':(690.80,'18:32'),'BRK-B':(583.60,'16:52'),'NVDA':(169.47,'18:17'),'GOOGL':(288.50,'18:13'),'SOFI':(16.34,'16:54')}
ep=[f"本轮采集北京时间{e['captured_at_beijing']}。11/10盘后尚在进行，结束于11/11北京09:00；以下不是最终盘后收盘。11/11盘前尚未开始（北京17:00起），常规开盘北京22:30。11/11老兵日美股股票常规开市；不含20:00–04:00券商夜盘。"]
for s,(p,t) in post2.items():
 a=obs[s]['post'];ep.append(f"{s}：常规收盘{M[s]['close']:.2f}美元；Yahoo盘后{a['price_usd']:.2f}（相对同日收盘{a['change_vs_reference_pct']:+.2f}%），美东{a['bar_start_et']}／北京{a['bar_start_beijing']}。StockAnalysis另报{p:.2f}美元，11/10 {t} EST；不同时间，不当作同笔成交一致。")
ep+=['以上Yahoo盘后分钟柱成交量均为0，可能为延续参考价，不能确认新实际成交；第二来源也不是可成交保证。昨日盘前数据仅留原日期审计，不冒称下一交易日盘前。']
ext={'title':'盘后观察｜11/10未结束，下一盘前尚未开始','paragraphs':ep,'sources':[src(s+'第二来源含时刻历史页',sa(s)) for s in post2]}
gaps={'title':'核验范围｜43项已更新，跨源仍有价差','paragraphs':['本次本地43项及云端43项均已更新至11/10，日线通过OHLC校验。昨日被拒绝的XSW、ATS以及行业补充XLY，来源此次返回的序列已通过校验；没有手工补价。云端仍为Yahoo单源自动采集，不把43项更新成功说成43项已跨源验证。','三项观察标的及NVDA、GOOGL、SOFI、NOW、CRM、GEHC、CGNX重要收盘已进行第三方对照；并非全部43项均经第二源核验。均线、量能及真实历史曲线为Yahoo单源计算，行情刷新不代表估值已重新完成。','本地保留60交易日走势／滚动回撤与12项行业图、CSV、原始证据；网站1／2／3年交互区间独立。MRNA历史大跳变仍显著影响回报/波动，不能作为预期收益；未核明事件因果。'],'sources':[yf('XSW'),yf('ATS'),yf('XLY')]}
save('market_sections.json',[alerts,market,sector,full,ext,gaps])
save('session_check.json',{'checked_at':NOW,'report_date_beijing':'2026-11-11','latest_completed_regular_session':'2026-11-10','next_session':'2026-11-11','next_open_et':'2026-11-11T09:30:00-05:00','next_open_beijing':'2026-11-11T22:30:00+08:00','next_premarket_status':'not_started','postmarket_at_capture':'in_progress','calendar_url':'https://www.nyse.com/trade/hours-calendars','archival_key':'2026-11-10'})
print('Market and alert proposal ready; global state untouched')
