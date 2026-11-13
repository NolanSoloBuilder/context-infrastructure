import json,csv,copy
from pathlib import Path
from datetime import datetime,timezone
P=Path(__file__).resolve().parent
R=P.parent
M={x['symbol']:x for x in json.loads((P/'metrics.json').read_text())}
NOW=datetime.now(timezone.utc).isoformat()
def save(n,x): (P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def src(t,u):return {'title':t,'url':u}
def yf(s):return src(s+'本次Yahoo日线',M[s]['source_url'])
def sa(s):return 'https://stockanalysis.com/'+('etf/' if s in ['QQQM','VOO'] else 'stocks/')+s.lower().replace('-','.')+'/history/'
second={'QQQM':279.49,'VOO':691.83,'BRK-B':574.76,'NVDA':178.59,'GOOGL':288.11,'SOFI':16.75,'NOW':102.75,'CRM':214.90,'GEHC':84.09,'CGNX':50.33}
comparisons=[{'symbol':s,'regular_session':'2026-11-09','yahoo_close_usd':M[s]['close'],'stockanalysis_close_usd':v,'difference_usd':round(M[s]['close']-v,4),'source_url':sa(s)} for s,v in second.items()]
second_high={'QQQM':314.12,'VOO':718.47,'BRK-B':586.30}
verify={'reviewed_at':NOW,'report_date':'2026-11-10','market_session':'2026-11-09','currency':'USD','quote_comparisons':comparisons,'official_gap':'Nasdaq QQQM historical page returned no usable rows. Cross-checks are third-party, not official closing auction certification.','high_comparisons':[{'symbol':s,'yahoo':M[s]['high_52w'],'stockanalysis':h,'date_both':M[s]['high_date'],'drawdown_secondary_pct':100*(1-second[s]/h)} for s,h in second_high.items()], 'brkb_third_source':{'url':'https://www.marketscreener.com/quote/stock/BERKSHIRE-HATHAWAY-INC-11916/quotes/','dated_last':'2026-11-09','price':575.25,'high':586.30,'note':'Dated daily Last matches Yahoo; trades include16:05:01 575.25 and16:00 574.76. Auction/consolidation meaning not confirmed; do not relabel16:05 as afterhours or independently claim official closing price.'},'errors':json.loads((P/'manifest.json').read_text())['errors']}
save('verification.json',verify)
alertlines=[]
state=json.loads((R/'alert_state.json').read_text());save('alert_state_before.json',state)
def stage(d):return 'at_or_above_25' if d>=25 else 'near_25' if d>=23 else 'at_or_above_15' if d>=15 else 'near_15' if d>=13 else 'below_13'
for key,s in [('QQQM','QQQM'),('VOO','VOO'),('BRK.B','BRK-B')]:
 m=M[s];D=100*(1-m['close']/m['high_52w']);secondaryD=100*(1-second[s]/second_high[s]);assert stage(D)==stage(secondaryD)
 old=state['symbols'][key];prev=old['stage'];new=stage(D)
 alertlines.append(f"{key}：11/9常规收盘{m['close']:.2f}美元（日{m['day_pct']:+.2f}%）；52周盘中高点{m['high_52w']:.2f}美元／{m['high_date']}，回撤{D:.3f}%。15%／25%观察价{m['level_15']:.2f}／{m['level_25']:.2f}美元。距15%尚差{15-D:.3f}个百分点；从当前价格到15%观察价还需变化{100*(m['high_52w']*.85/m['close']-1):+.3f}%。阶段：低于13%接近区间。")
 old.update(last_checked_session='2026-11-09',close_usd=m['close'],high_52w_usd=m['high_52w'],high_date=m['high_date'],drawdown_pct=D,stage=new,previous_stage=prev,level_15_usd=m['level_15'],level_25_usd=m['level_25'],gap_to_15_percentage_points=15-D,price_change_to_15_pct=100*(m['high_52w']*.85/m['close']-1),new_highlight=False)
 if new!=prev:old['stage_since_session']='2026-11-09'
 old['verification_note']='Yahoo/StockAnalysis differences disclosed; both yield same stage. BRK.B additionally corroborated by MarketScreener.'
state.update(last_checked_session='2026-11-09',report_date_beijing='2026-11-10',updated_at_utc=NOW,highlighted_symbols=[])
state['data_validation']={'watchlist_closes_verified':True,'status':'third_party_crosschecked_same_stages_with_disclosed_price_differences','fully_valid_symbols':['QQQM','VOO','BRK.B'],'deferred_symbols':[],'verification_file':str(P/'verification.json')}
save('alert_state_proposal.json',state)
alerts={'title':'收盘观察档｜QQQM离开接近区间，三项均未新触发','paragraphs':alertlines+['QQQM由11/6的near_15回到below_13，属于回撤缓解，不是新买入触发；15%／25%条件不变。BRK.B按单一公司风险评估，不套ETF仓位。','Yahoo／StockAnalysis收盘依次为QQQM279.52／279.49、VOO691.87／691.83、BRK.B575.25／574.76美元。QQQM高点314.11／314.12（同为10/6）差0.01；另两项高点与日期一致。差异均不改变分档。','BRK.B的MarketScreener11/9日表Last为575.25，与Yahoo一致；其明细同时出现16:05的575.25及16:00的574.76。收盘汇总／竞价口径未获官方说明，保留差异，不声称精确官方收盘已经一致。','回撤采用各自滚动(日期−364天,日期]盘中High；MA采用拆股调整Close，不计分红。盘后不更新收盘观察档。'],'sources':[src(s+'第二来源历史',sa(s)) for s in second_high]+[src('BRK.B第三来源日表',verify['brkb_third_source']['url'])]}
q=M['QQQM'];v=M['VOO']
market={'title':'指数与趋势｜广泛反弹，QQQM仍略低于200日线','paragraphs':[
 *[f"{label}：{M[s]['close']:,.2f}点；日{M[s]['day_pct']:+.2f}%／5交易日{M[s]['five_session_pct']:+.2f}%／21交易日{M[s]['twenty_one_session_pct']:+.2f}%。" for s,label in [('^GSPC','标普500'),('^IXIC','纳斯达克综合（环境参考）'),('^NDX','纳斯达克100')]],
 f"QQQM MA50／200为{q['ma50']:.2f}／{q['ma200']:.2f}美元，偏离{q['vs_ma50_pct']:+.2f}%／{q['vs_ma200_pct']:+.2f}%；成交量为此前20日均量{q['volume_vs_prior20']:.2f}倍。VOO MA50／200为{v['ma50']:.2f}／{v['ma200']:.2f}美元，偏离{v['vs_ma50_pct']:+.2f}%／{v['vs_ma200_pct']:+.2f}%。",
 '判断：继续观察，CPI公布前暂不因单日反弹加快追加；反证是行业上涨面改善、QQQM已接近200日线。下次观察通胀结果、长端收益率与反弹能否连续站稳均线；不把宏观单一结果等同买点。',
 '日、5日、21日均为拆股一致的价格收益，未计分红；线上1／2／3年回报是Adj Close含分红复权代理。两个口径分别展示，不能混为总回报。'],'sources':[yf(s) for s in ['^GSPC','^IXIC','^NDX','QQQM','VOO']]}
names={'XLK':'科技','XLC':'通信服务','XLY':'可选消费','XLP':'必需消费','XLV':'医疗','XLF':'金融','XLI':'工业','XLE':'能源','XLU':'公用事业','XLB':'材料','XLRE':'房地产','SMH':'半导体'}
rows=[];paras=[]
for s,n in names.items():
 row={'symbol':s,'name':n,'day_pct':None,'five_session_pct':None,'twenty_one_session_pct':None,'relative_day_pct':None,'relative_five_session_pct':None,'relative_twenty_one_session_pct':None}
 if s in M:
  for k in ['day_pct','five_session_pct','twenty_one_session_pct']:row[k]=M[s][k];row['relative_'+k]=M[s][k]-M['^GSPC'][k]
  paras.append(f"{s} {n}：日{row['day_pct']:+.2f}%／5日{row['five_session_pct']:+.2f}%／21日{row['twenty_one_session_pct']:+.2f}%；相对标普{row['relative_day_pct']:+.2f}／{row['relative_five_session_pct']:+.2f}／{row['relative_twenty_one_session_pct']:+.2f}个百分点。")
 else:paras.append(f'{s} {n}：缺失；11/9开盘低于最低价，整项序列拒绝，不填0、不借前日当今日。')
 rows.append(row)
with (P/'sector_summary.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
sector={'title':'行业观察｜半导体、科技与工业反弹，月度修复仍不均','paragraphs':['12项观察中11项取得有效序列，11项均上涨；XLY缺失，不声称全部12项上涨。SMH日+5.05%但21日−19.21%，XLK日+3.73%但21日−14.04%，反弹尚未抹平此前跌幅。','XLI工业日+3.82%、21日−0.21%，比科技更接近修复；XLC通信日+2.45%、5日+7.08%，平台业务改善值得观察，但不等于已核AI营收增长。','价格走势不能证明资金净流入或从基础设施流向应用。SMH上涨而NVDA下跌也提示个股风险与行业行情可以分离；单日领涨不构成买点。'],'sources':[yf(s) for s in ['SMH','XLK','XLI','XLC']]}
full={'title':'行业完整比较｜日／5交易日／21交易日','paragraphs':['同一11/9已完成常规时段；相对基准为标普500价格指数^GSPC，差值单位为百分点。',*paras],'sources':[yf('^GSPC'),yf('SMH')]}
e=json.loads((P/'extended_quotes.json').read_text());obs={x['symbol']:x for x in e['observations']};post2={'QQQM':(279.98,'18:19'),'VOO':(692.55,'18:24'),'BRK-B':(572.58,'18:31'),'NVDA':(179.10,'18:23'),'GOOGL':(290.35,'18:32'),'SOFI':(16.80,'18:19')}
ep=[f"本轮采集北京时间{e['captured_at_beijing']}。11/9美东盘后尚在进行，将于11/10北京09:00结束；以下不是最终盘后收盘。11/10盘前尚未开始（北京17:00起），常规开盘北京22:30，不含20:00–04:00券商夜盘。"]
for s,(p,t) in post2.items():
 o=obs[s];a=o['post'];ep.append(f"{s}：常规收盘{o['regular_close_usd']:.2f}美元；Yahoo盘后{a['price_usd']:.2f}（较同日收盘{a['change_vs_reference_pct']:+.2f}%），美东{a['bar_start_et']}／北京{a['bar_start_beijing']}。StockAnalysis另报{p:.2f}美元，11/9 {t} EST；时刻不同，不能当成交价一致。")
ep+=['上述Yahoo分钟柱成交量均为0，可能为延续参考价。XSW／ATS盘后提取因常规序列校验失败，留缺失；下一交易日盘前未开始，前日盘前不冒称今日。']
ext={'title':'盘后观察｜11/9未结束，各来源时刻分开','paragraphs':ep,'sources':[src(s+'含时刻第二来源',sa(s)) for s in post2]}
gaps={'title':'核验缺口｜41项更新，XSW与ATS保留11/6；XLY缺图','paragraphs':['公开清单43项中41项历史已更新到11/9。XSW开盘203.90低于最低204.23、ATS开盘17.31低于最低17.3324，来源OHLC矛盾，云端按既有规则保留11/6有效历史；不手工猜测修正，不用旧值当11/9。','行业补充XLY也出现开盘119.69低于最低119.71的矛盾，其11/9日/周/月及行业条形图留缺失，不填0。其余11项行业有效。','重要收盘与高点已进行第三方交叉，价格差异就近列出；均线、量能与历史曲线仍来自Yahoo同一序列，不声称全部43项已跨源核验。行情自动刷新不等于估值已重做。','本地保留两张真实60交易日／行业审计图及CSV，已核图中末值与表格一致。历史区间与网站1／2／3年交互图独立；MRNA历史大跳变仍对收益和波动有重大影响，未核定其原始事件因果。'],'sources':[src('XSW原始来源','https://query1.finance.yahoo.com/v8/finance/chart/XSW?range=2y&interval=1d'),src('ATS原始来源','https://query1.finance.yahoo.com/v8/finance/chart/ATS?range=2y&interval=1d'),src('XLY原始来源','https://query1.finance.yahoo.com/v8/finance/chart/XLY?range=2y&interval=1d')]}
save('market_sections.json',[alerts,market,sector,full,ext,gaps])
save('market_item.json',{'title':'继续观察：QQQM回撤降至约11%，今晚CPI后再看修复','fact':f"11/9常规收盘QQQM279.52美元、日+3.44%，距10/6盘中高点314.11回撤11.01%；已离开13%–15%接近区间。标普500+2.35%，纳指100+3.40%。",'implication':'上涨面改善，但QQQM仍略低于200日线280.47美元；价格反弹本身不提高企业未来现金流。今晚北京21:30的CPI尚未公布。','judgment':'继续观察，暂不因反弹加快追加；三项15%／25%收盘观察档本次均无新触发。','counter':'若通胀缓和、长端利率回落且指数持续站稳均线，等待的理由会减弱；不能用一天走势断言反弹结束或已经见底。','next':'核CPI实际值与构成、10年期收益率、QQQM能否站稳200日线；若回撤重新进入13%–15%，按原规则重新提示。','sources':[yf('QQQM'),src('QQQM第二来源历史',sa('QQQM')),src('BLS CPI日程','https://www.bls.gov/schedule/news_release/cpi.htm')]})
save('session_check.json',{'checked_at':NOW,'report_date_beijing':'2026-11-10','latest_completed_regular_session':'2026-11-09','next_session':'2026-11-10','next_open_et':'2026-11-10T09:30:00-05:00','next_open_beijing':'2026-11-10T22:30:00+08:00','next_premarket_status':'not_started','current_postmarket_status':'in_progress','calendar_url':'https://www.nyse.com/trade/hours-calendars','archival_key':'2026-11-09'})
print('Market sections and alert proposal prepared; global alert file unchanged.')
