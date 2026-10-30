from pathlib import Path
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import json,re,html,hashlib
p=Path(__file__).resolve().parent
now=datetime.now(timezone.utc).isoformat()
urls={
'gdp':'https://bea.gov/news/2026/gdp-advance-estimate-3rd-quarter-2026',
'pce':'https://www.bea.gov/news/2026/personal-income-and-outlays-september-2026',
'treasury':'https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value=2026',
'amazon':'https://ir.aboutamazon.com/news-release/news-release-details/2026/Amazon-com-Announces-Third-Quarter-Results/default.aspx',
'amazon_blog':'https://www.aboutamazon.com/news/company-news/amazon-earnings-q3-2026-report',
'fed':'https://www.federalreserve.gov/newsevents/pressreleases/monetary20261028a.htm',
'fed_calendar':'https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm',
'bls_oct':'https://www.bls.gov/schedule/2026/10_sched.htm',
'bls_nov':'https://www.bls.gov/schedule/2026/11_sched.htm',
'rrx':'https://investors.regalrexnord.com/investors/ir-news/press-release-details/2026/Regal-Rexnord-Corporation-to-Host-Third-Quarter-2026-Earnings-Conference-Call-on-Tuesday-November-3rd-2026/default.aspx',
'cgnx':'https://investor.cognex.com/news/news-details/2026/Cognex-Announces-Third-Quarter-2026-Earnings-Release-and-Conference-Call-Dates/default.aspx',
'vix':'https://www.cboe.com/tradable-products/vix/'
}
rows=json.loads((p/'treasury_rows.json').read_text()); header=rows['headers'][0]; dated={r[0]:dict(zip(header,r)) for r in rows['rows']}
two=float(dated['10/29/2026']['2 Yr']);ten=float(dated['10/29/2026']['10 Yr']);two_change=round((two-float(dated['10/28/2026']['2 Yr']))*100);ten_change=round((ten-float(dated['10/28/2026']['10 Yr']))*100)
def event(name,iso,source,condition):
 d=datetime.fromisoformat(iso);return {'name':name,'us_eastern':d.astimezone(ZoneInfo('America/New_York')).isoformat(),'beijing':d.astimezone(ZoneInfo('Asia/Shanghai')).isoformat(),'source':source,'condition':condition,'status':'scheduled_officially_verified'}
events=[
 event('Q3 Employment Cost Index','2026-10-30T08:30:00-04:00',urls['bls_oct'],'工资成本是否持续抬高服务通胀'),
 event('September JOLTS','2026-11-03T10:00:00-05:00',urls['bls_nov'],'职位空缺、招聘与离职变化'),
 event('RRX Q3 call','2026-11-03T10:00:00-05:00',urls['rrx'],'去退税盈利、现金转化与去杠杆；财报同日盘前，精确发布时间未披露'),
 event('Q3 Productivity and Costs preliminary','2026-11-05T08:30:00-05:00',urls['bls_nov'],'单位劳动成本与生产率'),
 event('CGNX Q3 call','2026-11-05T08:30:00-05:00',urls['cgnx'],'RealSense现金支出、留任和稀释；财报11/4盘后，精确发布时间未披露'),
 event('October Employment Situation','2026-11-06T08:30:00-05:00',urls['bls_nov'],'非农、失业率及工资增长')]
context={'report_date_beijing':'2026-10-30','session':'2026-10-29','updated_at_utc':now,'scope':'Completed 10/29 US session and publicly released after-hours company results; no account access or transactions',
'gdp':{'release_us':'2026-10-29T08:30:00-04:00','quarter':'2026Q3 advance','real_growth_saar_pct':3.4,'previous_quarter_growth_saar_pct':2.2,'real_private_domestic_final_sales_saar_pct':4.9,'quarter_pce_price_saar_pct':2.1,'quarter_core_pce_price_saar_pct':2.5,'source':urls['gdp']},
'pce':{'release_us':'2026-10-29T08:30:00-04:00','reference_month':'2026-09','headline_mom_pct':0.5,'headline_yoy_pct':3.6,'core_mom_pct':0.3,'core_yoy_pct':3.1,'real_pce_mom_pct_display':0.0,'real_pce_exact_description':'less than0.1% monthly increase','personal_income_mom_pct':0.2,'source':urls['pce'],'not_consensus_comparison':'No independent consensus estimate verified; do not assert surprise versus estimates'},
'fed':{'publication_date':'2026-10-28','target_pct':[3.75,4.0],'vote':'10-2','dissent':'preferred raise25bp','source':urls['fed'],'next_meeting_us':['2026-12-08','2026-12-09'],'no_fomc_in_next_week':True,'calendar':urls['fed_calendar']},
 'treasury':{'session':'2026-10-29','two_year_pct':two,'ten_year_pct':ten,'two_year_change_bp':two_change,'ten_year_change_bp':ten_change,'source':urls['treasury'],'raw_rows':'treasury_rows.json','basis':'official nominal par yield curve; reference rates, not broker executable quotes'},
'vix':{'asof_date':'2026-10-29','value':17.20,'change':0.29,'change_pct':1.71,'source':urls['vix'],'timestamp_limit':'Cboe date-labelled spot17.20; separate page module says8:15PM10/29, later than capture if interpreted EDT and timezone unspecified. Do not treat module time as synchronized close.'},
'amazon':{'release_date_us':'2026-10-29','quarter':'2026Q3','units':'USD billions unless otherwise stated','sales':201.944,'aws_sales':45.984,'aws_sales_yoy_pct_computed':(45.984/33.006-1)*100,'aws_operating_income':17.773,'aws_operating_margin_pct':38.7,'aws_operating_margin_prior_quarter_pct':39.4,'ttm_operating_cashflow':168.300,'ttm_pp_and_e_net':210.657,'ttm_fcf':-42.357,'ttm_fcf_prior_year':14.788,'cash_capex_2026_guidance':220,'cash_capex_guidance_change':'unchanged','net_income_q3':20.7,'gaap_diluted_eps':1.89,'source':urls['amazon'],'timing':'Release after10/29 regular close; not reflected in same-day close as released outcome','full_call_audio_reviewed':False,'limits':['FCF is TTM, not Q3; definition OCF less net PP&E purchases','No complete financed-capex or valuation reconstruction in this macro task','Management2027/2028AWSgrowth forecasts not realized results']},
'events':events,'other_calendar_notes':{'cgnx_release':'2026-11-04 after regular close (EST), Beijing11/5 early morning; exact time not asserted','rrx_release':'2026-11-03 before regular open (EST); exact time not asserted','cpi_next':'2026-11-10T08:30:00-05:00','dst':'America/New_York returns to EST on2026-11-01; Nov08:30ET becomes21:30Beijing,10:00ET becomes23:00Beijing','apple':'Official latest earnings date/results not obtained in this pass; third-partyNov2date not adopted as verified'},
'sources':urls,'read_gaps':['Official Apple earnings page inaccessible; no official new result inferred','CNBC related originals inaccessible; no bypass','CLI archive of Amazon release failed, web tool body read successfully','FiNews web root cache stale10/28; live publicHTML10/29 archived separately'],'not_traded':True}
assert round(context['amazon']['ttm_operating_cashflow']-context['amazon']['ttm_pp_and_e_net'],3)==context['amazon']['ttm_fcf']
assert two_change==-6 and ten_change==-7
(p/'market_context.json').write_text(json.dumps(context,ensure_ascii=False,indent=2)+'\n')
macro=f'''# 宏观与盘后事件｜北京时间2026-10-30

数据对应美东2026-10-29；本次核验时间为UTC {now}。用户已明确30000美元、3–5年、可接受约20%暂时回撤，没有确认持仓；配置草案尚未采用。

## 对首次建仓最有用的变化

**判断：可继续推进小额按时间分批的研究，但本次宏观和Amazon结果不支持加速投入；不再以昨天已经公布的GDP/PCE作为等待理由。** 私人内需与AWS增长支持需求韧性，核心通胀及资本投入仍限制能承受的买入估值。是否实际首笔由主日报结合当天价格、行业广度与未确认配置给判断。

1. **增长有韧性，月度通胀仍有压力。** BEA的Q3实际GDP环比折年+3.4%，Q2+2.2%，私人国内最终销售+4.9%。9月PCE物价环比+0.5%、同比+3.6%，核心+0.3%/+3.1%，实际消费月增不足0.1%。不能因季度增长强就忽略9月消费的实际增量，也没有核验独立市场预期，故不写“超预期”。[GDP原文]({urls['gdp']}) · [月度PCE原文]({urls['pce']})

2. **季度PCE与月度PCE须分开。** GDP报告中的季度PCE物价折年2.1%、核心2.5%为季度窗口；9月0.5%/0.3%为单月变化，3.6%/3.1%为同比。三种口径不能互相替代。我的解释：收入与估值研究仍需为高于2%的核心通胀留余地，不把一次数据称为确定降息或加息路径。

3. **美债收益率回落不等于成长股风险解除。** 财政部10/29参考曲线2年4.61%、10年4.98%，较前日分别−6、−7基点；数值从相同官方表头和日期行提取，不是可成交收益率。[财政部原表]({urls['treasury']}) · [提取行](./treasury_rows.json)。10/28联储维持3.75%–4.00%，两名异议者希望加息；本周没有新FOMC决定。[原声明]({urls['fed']})

## Amazon：云需求强，但现金投入压力没有消失

10/29盘后Q3结果：AWS收入459.84亿美元、同比约39.3%，营业利润177.73亿美元，利润率38.7%（Q2为39.4%）。集团TTM经营现金流1683.00亿美元，减净购置固定资产2106.57亿美元，得到TTM自由现金流**−423.57亿美元**；2026现金资本开支展望仍约2200亿美元。该负FCF是过去12个月，不是三季度单季。[Amazon官方表与展望]({urls['amazon']})

**我的分析：** 需求增长与自由现金流可以同时向相反方向变化。AWS的实际盈利是支持AI需求的反证，利润率环比降低及集团现金支出是约束；二者都不直接给出AMZN或QQQM低估结论。不可把2027/2028的管理层高增长预期当已实现收入，也不能把GoogleTPU系统销售与AWS服务增长混成同口径比较。对用户，保留小额、限定总股票预算比因云业务增长一次买满更符合回撤偏好。

最强反证是这些投入形成高回报且逐步释放现金，持续等待可能错过上涨。下一核查：新增算力投产后的AWS利润和回款、集团净现金资本支出及融资租赁口径、QQQM权重股盈利与当日ETF广度。主线程另列盘后报价及精确时点，本文件不从标题推导股价或确定因果。

## 未来一周日历

| 事件 | 美东时间 | 北京时间 | 核查重点 |
|---|---|---|---|
| Q3雇佣成本指数 | 10/30 08:30 EDT | 10/30 20:30 | 工资与服务通胀 |
| 9月JOLTS | 11/3 10:00 EST | 11/3 23:00 | 职位空缺与用工需求 |
| RRX Q3电话会 | 11/3 10:00 EST | 11/3 23:00 | 现金转化、调整项目、去杠杆 |
| CGNX Q3发布 | 11/4盘后EST | 11/5凌晨，精确时间未披露 | RealSense支出与整合 |
| Q3生产率/成本初值 | 11/5 08:30 EST | 11/5 21:30 | 单位劳动成本 |
| CGNX电话会 | 11/5 08:30 EST | 11/5 21:30 | 增长、留任与稀释 |
| 10月非农 | 11/6 08:30 EST | 11/6 21:30 | 工资、失业与招聘 |

来源：[BLS10月]({urls['bls_oct']}) / [11月]({urls['bls_nov']})、[RRX]({urls['rrx']})、[CGNX]({urls['cgnx']})。RRX财报11/3盘前，未填精确分钟。下一CPI11/10，下一FOMC12/8–9，均不在前述一周内。[FOMC日历]({urls['fed_calendar']})

Apple第三方报道说11/2财报，但本次未取得官方明确日期或新结果，不按已核实事件填表。11/1后美国冬令时，以上已按America/New_York换算。

## VIX和证据边界

Cboe官方日期标注10/29的现货值17.20，+0.29（+1.71%）。页面另有“8:15PM10/29”模块，若按EDT解释晚于采集，且未明时区，故不将该模块时间当与股票16:00同步的证明。[Cboe]({urls['vix']})。主日报最终值请与本次统一日线核对。

完整事实与缺口见[market_context.json](./market_context.json)。官方BEA、财政部、FiNews原HTML已保存，AmazonCLI存档失败但网页工具正文已读；不声称完整原文均已离线保存。
'''
(p/'macro_events.md').write_text(macro)
s=(p/'macro_raw/finews.html').read_text(); articles=re.findall(r'<article class="news-item">(.*?)</article>',s,re.S)
def strip(t):return html.unescape(re.sub('<[^>]+>','',t)).strip()
index=[]
for chunk in articles:
 title=re.search(r'class="news-title"[^>]*>(.*?)</a>',chunk,re.S)
 href=re.search(r'class="news-title" href="([^"]+)"',chunk)
 stamp=re.search(r'<div class="news-meta">(.*?)</div>',chunk,re.S)
 index.append({'title':strip(title.group(1)) if title else None,'url':html.unescape(href.group(1)) if href else None,'source_timestamp_text':strip(stamp.group(1)) if stamp else None})
(p/'macro_raw/finews_news_index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n')
finews={'collected_at_utc':'2026-10-29T23:36:13.153814+00:00','url':'https://finews.fyi/','page_session_date':'2026-10-29','page_update_at_utc':'2026-10-29T22:09:48Z','page_update_beijing':'2026-10-30T06:09:48+08:00','read_scope':f'Public liveHTML:8summary points,{len(index)}news titles/summaries/links,calendar andmarketwidgets. Web toolrootreturnedstale10/28;CLIrootreturned10/29.','saved_html':'macro_raw/finews.html','saved_html_sha256':hashlib.sha256(s.encode()).hexdigest(),'news_metadata_index':'macro_raw/finews_news_index.json','role':'discovery_only_primary_recheck','items':[
 {'key':'amazon_q3_cash_return','aggregation_url':'https://finews.fyi/','original_url':'https://www.cnbc.com/2026/10/29/amazon-amzn-q3-earnings-report-2026.html','original_timestamp_at_utc':'2026-10-29T22:05:59Z','original_read':'not_accessible_not_bypassed','primary_url':urls['amazon'],'status':'company_results_verified_from_original_release','claims':['AWSQ3revenue45.984B+39.3%','TTMFCFminus42.357B','2026cashcapex220Bmaintained'],'counterevidence':'AWSoperatingincomeandcashfromoperationsgrowing; investmentreturntimingnotyetsettled'},
 {'key':'gdp_pce_actual','aggregation_url':'https://finews.fyi/','original_url':'https://www.nytimes.com/2026/10/29/business/economy/us-economy-gdp.html','original_timestamp_at_utc':'2026-10-29T21:10:37Z','original_read':'not_read_primary_substituted','primary_urls':[urls['gdp'],urls['pce']],'status':'official_actuals_verified_no_consensus_checked','counterevidence':'quarterpricegrowthslowedwhilemonthlyheadlineaccelerated; differentwindows'},
 {'key':'google_capital_return','aggregation_url':'https://finews.fyi/','original_url':'https://www.cnbc.com/2026/10/29/alphabet-google-microsoft-msft-shares-today-earnings.html','original_timestamp_at_utc':'2026-10-29T20:15:19Z','original_read':'not_accessible_not_bypassed','primary_verification':'Googleprimaryreviewhandledseparatelybyparentteam; notclaimedindependentverificationinthisfile','status':'lead_only_in_this_file'},
 {'key':'link_quality_gap','example_original_url':'https://finance.yahoo.com/markets/stocks/articles/why-the-market-dipped-but-medtronic-mdt-gained-today-205003819.html?.tsrc=rss','aggregation_title':'Apple、Meta等少数科技股逆势上涨，资金寻找防守型成长','status':'title_URL_subject_mismatch_flag_body_inaccessible_not_proven_false','handling':'Do notusethisitemasfact;notinferfundflowsfromstockprice'}],
 'limitations':['FiNewsquoteunderlyingYahooisnotanindependentcrosscheck','Calendarrequiresofficialrecheck,DSTcorrection','ValuationtemperatureandFearGreednotverifiedorusedasentrytriggers','SomeaggregatedtitlesandURLsubjectsappearmismatched; originalsnotaccessibledonotupgradeclaim','Noassertioncapitalflowbasedonprices']}
(p/'finews_sources.json').write_text(json.dumps(finews,ensure_ascii=False,indent=2)+'\n')
(p/'finews_digest.md').write_text(f'''# FiNews线索与核验｜北京时间2026-10-30

实际新取[FiNews根页](https://finews.fyi/)对应**10/29交易日**，更新UTC10/29 **22:09:48**／北京时间10/30 **06:09:48**；采集UTC23:36:13。本次网页工具根页缓存仍10/28，公开HTML已更新并存档；以新取HTML日期为准。读取8条总结、{len(index)}条新闻标题/摘要及外链、日历与行情模块。

最有用的新增线索是**Amazon增长与现金回报分化、GDP/PCE实际公布结果**，已回查官方。Google资本回报线索交主线程独立核验。Amazon的AWS增长支持需求，负TTM自由现金流限制能支付的估值；9月核心PCE仍高于2%，不能单凭指数下跌就认定利率压力消退。详见[本次宏观与财报核验](./macro_events.md)。

FiNews适合作新闻索引。其部分标题与链接URL主题看似不一致，例如Apple/Meta摘要链接指向Medtronic文章；原文不可读，所以只记质量缺口，不据此断言内容为假。价格上涨不视作资金净流入；情绪温度不作为买点；日历改由BLS/公司官方与正确时区确认。

[来源、读取范围与限制](./finews_sources.json)。正文没有复写全部聚合新闻，也没有因此新增推荐股票。
''')
print(json.dumps({'files':['market_context.json','macro_events.md','finews_digest.md','finews_sources.json'],'treasury':[two,ten,two_change,ten_change],'finews_articles':len(index),'amazon_fcf_check':168.300-210.657},ensure_ascii=False))
