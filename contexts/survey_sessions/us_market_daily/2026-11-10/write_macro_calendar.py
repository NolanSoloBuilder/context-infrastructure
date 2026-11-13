import json,datetime
from pathlib import Path
from zoneinfo import ZoneInfo
P=Path(__file__).parent
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
ny=ZoneInfo('America/New_York');bj=ZoneInfo('Asia/Shanghai')
urls={
'nyse':'https://www.nyse.com/trade/hours-calendars',
'bls':'https://www.bls.gov/schedule/2026/11_sched.htm',
'cpi':'https://www.bls.gov/schedule/news_release/cpi.htm',
'jobs':'https://www.bls.gov/schedule/news_release/empsit.htm',
'fed':'https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm',
'claims':'https://oui.doleta.gov/unemploy/claims_arch.asp',
'treasury':'https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?field_tdr_date_value=202611&type=daily_treasury_yield_curve',
'vix_official':'https://www.cboe.com/tradable-products/vix',
'vix_wsj':'https://www.wsj.com/market-data/quotes/index/VIX/historical-prices',
'vix_investing':'https://www.investing.com/indices/volatility-s-p-500-historical-data',
'vix_csv':'https://cdn-api.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv',
'sgov':'https://www.ishares.com/us/products/314116/ishares-0-3-month-treasury-bond-etf',
'csco':'https://newsroom.cisco.com/c/r/newsroom/en/us/a/y2026/m11/cisco-schedules-conference-call-for-q1-fiscal-year-2027-financial-results.html',
'amat':'https://ir.appliedmaterials.com/news-releases/news-release-details/applied-materials-report-fourth-quarter-and-fiscal-2026-results',
'mrna_sec':'https://www.sec.gov/Archives/edgar/data/1682852/000168285226000194/exhibit9912026q3pressrelea.htm',
'mrna_events':'https://investors.modernatx.com/events-presentations',
'nvda_event':'https://nvidianews.nvidia.com/news/nvidia-sets-conference-call-for-third-quarter-financial-results-6928873'
}
findings={
'nyse':'2026 holiday table has Thanksgiving11/26 thenChristmas12/25, noVeteransDay closure. Core09:30-16:00ET. Date calculation giveslatestcompleted11/9,next11/10.',
'bls':'Official November calendar: OctoberCPI/RealEarnings11/10 08:30ET;OctoberPPI11/13 08:30;Novembermonthlyjobs12/4 08:30;lastmodified11/3.',
'cpi':'October2026 reference month releaseNovember10 2026 08:30ET; still future atreviewtime.',
'jobs':'Octoberreleased11/6; Novemberreference month releases12/4 08:30ET.',
'fed':'NextscheduledFOMC12/8-9; none11/10-16.',
'claims':'Thursday08:30EST standard; listedNovember2026holidayexception11/25,not11/12.',
'treasury':'11/9officialpar/CMT2Y4.56%,10Y4.88%;11/6 4.51%,4.86%. Indicativebid-sidequotesaround15:30ET,nottransactions.',
'vix_official':'DatedNov9spot19.92,change-5.72(-22.31%),prevclose25.64. Page time21:15doesnotstatezone; do notinferfromit.',
'vix_wsj':'Explicit3:15PM CST11/09/26(=16:15EST);table11/9OHLC25.08,25.08,19.64,19.92;11/6close25.64.',
'vix_investing':'Dailyhistoryrow11/9 close19.92,open25.08,high25.08,low19.64,change-22.31%.',
'vix_csv':'OfficialdailyCSVdownloadsuccessbutlastrow11/6,25.64;notusedas11/9close.',
'sgov':'30DaySEC3.84%asof11/6,12mtrailing3.63%,expense.09%;previous11/5SEC3.83%.',
'csco':'11/3announcement:FY27Q1results11/12aftermarketclose;call16:30ET,notprecisereleaseminute.',
'amat':'10/22announcement:FY26Q4/full-yearcall11/12 16:30ET. Exactrelease minute notstated.',
'mrna_sec':'11/6earningsrelease:AnalystDay11/12 date; exacthournotstated. Q3alreadyreleased.',
'mrna_events':'OpenedofficialdynamicpagebutUpcomingEventsnotpopulated;precisehourunverifiedthisrun.',
'nvda_event':'10/28announcement:FY27Q3ended10/25;resultsapproximately11/17 16:20EST,call17:00EST. Outside11/10-16window.'
}
events=[]
def event(id,title,local,source,note=''):
 d=datetime.datetime.fromisoformat(local).replace(tzinfo=ny)
 events.append({'id':id,'title':title,'time_et':d.isoformat(),'time_beijing':d.astimezone(bj).isoformat(),'status':'scheduled_not_released','sources':[urls[x] for x in source],'note':note})
event('cpi_oct','美国10月CPI','2026-11-10T08:30:00',['cpi','bls'],'北京时间今晚21:30，复核时尚未公布；不把预期当结果。')
event('real_earnings','美国10月实际收入','2026-11-10T08:30:00',['bls'])
event('claims','初请失业金','2026-11-12T08:30:00',['claims'])
event('csco','Cisco FY27Q1业绩电话会','2026-11-12T16:30:00',['csco'],'公司公告财报同日收盘后发布，16:30为电话会时刻。')
event('amat','Applied Materials FY26Q4及全年业绩电话会','2026-11-12T16:30:00',['amat'],'16:30为电话会时刻，精确公告分钟未披露。')
event('ppi_oct','美国10月PPI','2026-11-13T08:30:00',['bls'])
events.append({'id':'mrna_analyst','title':'Moderna分析师日（非季度财报）','date_et':'2026-11-12','time_et':None,'time_beijing':None,'status':'date_confirmed_exact_time_unverified','sources':[urls['mrna_sec'],urls['mrna_events']],'note':'本次SEC确认日期；官方动态事件页未返回具体小时，未把前次搜索索引09:00当本次完整核验。'})
obj={'schema_version':1,'report_date':'2026-11-10','reviewed_at':now,'market_session':'2026-11-09','next_session':'2026-11-10','calendar_window_et':['2026-11-10','2026-11-16'],'timezone':'America/New_York','session_check':{'calendar_url':urls['nyse'],'regular_close_et':'2026-11-09T16:00:00-05:00','regular_close_beijing':'2026-11-10T05:00:00+08:00','next_regular_open_et':'2026-11-10T09:30:00-05:00','next_regular_open_beijing':'2026-11-10T22:30:00+08:00','next_premarket_et':'2026-11-10T04:00:00-05:00','next_premarket_beijing':'2026-11-10T17:00:00+08:00','next_premarket_status':'not_started','afterhours_status':'in_progress','veterans_day_nyse_open':True},'macro':{'vix':{'date':'2026-11-09','close':19.92,'unit':'index_points','change_points':-5.72,'change_pct':(19.92/25.64-1)*100,'previous_close':25.64,'time_et':'2026-11-09T16:15:00-05:00','time_beijing':'2026-11-10T05:15:00+08:00','time_basis':'WSJ explicitly3:15PM CST anddateddailyclose row; officialcurrentpage confirmsprice/date','sources':[urls['vix_official'],urls['vix_wsj'],urls['vix_investing']],'official_daily_csv_latest':'2026-11-06','yahoo_crosscheck':'Parent reports freshlycollectedraw/index_VIX.json19.92; independentprimaryandWSJmatch.'},'treasury_2y':{'date':'2026-11-09','yield_pct':4.56,'change_bp':5,'previous_pct':4.51,'source':urls['treasury']},'treasury_10y':{'date':'2026-11-09','yield_pct':4.88,'change_bp':2,'previous_pct':4.86,'source':urls['treasury']},'spread_10y_2y_bp':32,'treasury_basis':'Treasury每日平价收益率曲线/CMT，来自约15:30ET报价插值，非实时成交收益率。','sgov':{'asof':'2026-11-06','sec_30day_yield_pct':3.84,'trailing_12m_yield_pct':3.63,'expense_ratio_pct':0.09,'previous_asof':'2026-11-05','previous_sec_30day_yield_pct':3.83,'change_bp':1,'source':urls['sgov'],'note':'SEC标准化30日收益率；非保证回报，不以12月派息率替代，不是11/9时点收益率。'}},'events':events,'outside_window':[{'id':'fomc_next','dates_et':['2026-12-08','2026-12-09'],'source':urls['fed'],'no_scheduled_meeting_in_window':True},{'id':'jobs_next','time_et':'2026-12-04T08:30:00-05:00','time_beijing':'2026-12-04T21:30:00+08:00','reference_month':'2026-11','source':urls['jobs']},{'id':'nvda_results','time_et_approx':'2026-11-17T16:20:00-05:00','time_beijing_approx':'2026-11-18T05:20:00+08:00','call_time_et':'2026-11-17T17:00:00-05:00','call_time_beijing':'2026-11-18T06:00:00+08:00','source':urls['nvda_event'],'note':'在11/10-16七日窗口之外，单列下一重要行业财报，不误写11/18美国日。'}],'coverage_gaps':['This is targetedcalendarreview,notproofthatnoeventsfor43assets.','CboeCSVonlythrough11/6;Cboecurrentpage11/9andWSJ/Investingdailycloseconfirmed11/9.','MRNAexacthournotconfirmedthisrun;dateisSECverified.','BLSandAMATcurlarchive403,webtoolofficialfulltextsuccessful;recordsretainactualaccesspath.','InitialTreasuryURLusedincorrectresource-center-data-chart-centerpath404;correctofficialresource-center/data-chart-centerpath200verified11/9.'],'sources':[{'id':k,'url':u,'reviewed_at':now,'read_scope':'officialrelevantdate/metricrows' if k not in ['vix_wsj','vix_investing'] else 'thirdpartydateddailyquoteandhistoryrows','finding':findings[k]} for k,u in urls.items()]}
(P/'macro_calendar.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2))
md='''# 2026-11-10 宏观与日历核验

今晚21:30公布美国10月CPI，当前尚未公布。11/9美股已完成常规交易，下一常规交易为11/10北京时间22:30；本次采集仍在11/9盘后，11/10盘前尚未开始。11/11老兵日不是NYSE股票休市日。

| 指标 | 最新已核日期 | 数值 | 较前一交易日 |
|---|---|---:|---:|
| VIX | 11/9收盘 | 19.92点 | −5.72点／−22.31% |
| 2年美国国债CMT | 11/9 | 4.56% | +5bp |
| 10年美国国债CMT | 11/9 | 4.88% | +2bp |
| 10−2年利差 | 11/9 | 32bp | −3bp |
| SGOV标准化30日SEC收益率 | 11/6 | 3.84% | 较11/5 +1bp |

事实：波动预期回落，但2/10年官方收益率均上涨。解释：风险情绪改善并不等于贴现率压力消失；CPI结果及收益率反应仍是下一可核条件。SGOV收益率数据日期仍11/6，非11/9即时利率，亦不承诺总回报。

VIX采用Cboe官方当日页并以WSJ、Investing当日日线交叉；WSJ明确11/9 15:15 CST＝16:15 EST＝11/10 05:15北京时间。官方CSV本次只到11/6，未冒充11/9；官方当前页21:15无时区，不单凭它推算。Treasury为约15:30ET报价插值的官方平价收益率，不是实时成交。

| 事件 | 美国东部时间 | 北京时间 |
|---|---|---|
| 10月CPI、实际收入 | 11/10 08:30 EST | 11/10 21:30 |
| 初请失业金 | 11/12 08:30 EST | 11/12 21:30 |
| Moderna分析师日 | 11/12，具体小时本次未核 | 具体时刻待核 |
| Cisco FY27Q1业绩电话会 | 11/12 16:30 EST | 11/13 05:30 |
| AMAT FY26Q4/全年业绩电话会 | 11/12 16:30 EST | 11/13 05:30 |
| 10月PPI | 11/13 08:30 EST | 11/13 21:30 |

电话会与公告分钟分开：Cisco为11/12收盘后公告；两家公司16:30均为电话会。七日窗口无FOMC议息和月度就业报告：下次FOMC12/8–9，下次就业12/4。NVDA下一重要财报在窗口外：11/17约16:20 EST公告、17:00电话会（北京时间11/18约05:20／06:00）。Moderna Q3已11/6公布，11/12是分析师日。

来源：
'''
for k,u in urls.items():md+=f'- [{k}]({u})：{findings[k]}\n'
md+='\n访问缺口：BLS及AMAT本机curl返回403，但本次web工具成功读取官方正文；原始失败回执亦保留。Moderna动态事件页没有具体小时。独立日历定向检查不等于43项事件完全覆盖。\n'
(P/'macro_calendar.md').write_text(md)
(P/'macro_raw'/'web_verified_extracts.json').write_text(json.dumps({'collected_at':now,'method':'web tool direct opens and relevant rows; not full raw HTML','sources':{k:{'url':urls[k],'finding':findings[k]} for k in urls}},ensure_ascii=False,indent=2))
print(json.dumps({'files':['macro_calendar.json','macro_calendar.md'],'reviewed_at':now,'vix_change_pct':obj['macro']['vix']['change_pct']},ensure_ascii=False))
