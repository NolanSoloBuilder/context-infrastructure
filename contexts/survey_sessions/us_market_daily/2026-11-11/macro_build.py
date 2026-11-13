import json
from pathlib import Path
from datetime import datetime,timezone
from zoneinfo import ZoneInfo
from html.parser import HTMLParser
OUT=Path(__file__).parent
now=datetime.now(timezone.utc).isoformat()
def url(id):
 return {
"cpi":"https://www.bls.gov/news.release/cpi.nr0.htm",
"cpi_table":"https://www.bls.gov/news.release/cpi.t01.htm",
"treasury":"https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?field_tdr_date_value=202611&type=daily_treasury_yield_curve",
"vix":"https://www.cboe.com/tradable-products/vix",
"vix_wsj":"https://www.wsj.com/market-data/quotes/index/VIX/historical-prices",
"nyse":"https://www.nyse.com/trade/hours-calendars",
"sifma":"https://www.sifma.org/resources/general/holiday-schedule/",
"bls_nov":"https://www.bls.gov/schedule/2026/11_sched.htm",
"jobs":"https://www.bls.gov/schedule/news_release/empsit.htm",
"fomc":"https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
"claims":"https://oui.doleta.gov/unemploy/claims_arch.asp",
"sgov":"https://www.ishares.com/us/products/314116/ishares-0-3-month-treasury-bond-etf",
"csco":"https://newsroom.cisco.com/c/r/newsroom/en/us/a/y2026/m11/cisco-schedules-conference-call-for-q1-fiscal-year-2027-financial-results.html",
"amat":"https://ir.appliedmaterials.com/news-releases/news-release-details/applied-materials-report-fourth-quarter-and-fiscal-2026-results",
"nvda":"https://nvidianews.nvidia.com/news/nvidia-sets-conference-call-for-third-quarter-financial-results-6928873",
"mrna":"https://www.sec.gov/Archives/edgar/data/1682852/000168285226000194/exhibit9912026q3pressrelea.htm",
"nyfed":"https://www.newyorkfed.org/newsevents/news/research/2026/20261110",
"nyfed_blog":"https://libertystreeteconomics.newyorkfed.org/2026/11/a-look-at-the-wider-divide-in-credit-card-delinquency-by-income/"
 }[id]
def event(id,title,et,sources,note="",status="scheduled_not_released"):
 dt=datetime.fromisoformat(et)
 return dict(id=id,title=title,time_et=et,time_beijing=dt.astimezone(ZoneInfo("Asia/Shanghai")).isoformat(),status=status,sources=[url(s) for s in sources],note=note)
events=[
event("claims","美国初请失业金","2026-11-12T08:30:00-05:00",["claims"],"DOL周四08:30 EST例行安排，本周无改期例外。"),
event("csco","Cisco FY27Q1业绩电话会","2026-11-12T16:30:00-05:00",["csco"],"财报同日收盘后发布；16:30为电话会，不能当精确公告分钟。"),
event("amat","Applied Materials FY26Q4及全年业绩电话会","2026-11-12T16:30:00-05:00",["amat"],"16:30为电话会时刻，公告精确分钟未披露。"),
event("ppi_oct","美国10月PPI","2026-11-13T08:30:00-05:00",["bls_nov"]),
event("import_export_oct","美国10月进出口价格指数","2026-11-17T08:30:00-05:00",["bls_nov"]),
event("nvda_result","NVIDIA FY27Q3业绩及CFO书面说明","2026-11-17T16:20:00-05:00",["nvda"],"公司表述approximately 13:20 PT，16:20 EST为约定时间；季度截至2026-10-25。"),
event("nvda_call","NVIDIA FY27Q3业绩电话会","2026-11-17T17:00:00-05:00",["nvda"])
]
events.append(dict(id="mrna_analyst",title="Moderna分析师日（非季度财报）",date_et="2026-11-12",time_et=None,time_beijing=None,status="date_confirmed_exact_time_unverified",sources=[url("mrna"),"https://investors.modernatx.com/events-presentations"],note="本次SEC原文确认日期；官网动态事件页未返回小时，不采用搜索摘要时间。Q3业绩已于11/6公布。"))
cpi={
"reference_month":"2026-10","released_at_et":"2026-11-10T08:30:00-05:00","released_at_beijing":"2026-11-10T21:30:00+08:00","status":"released",
"headline_mom_seasonally_adjusted_pct":0.4,"prior_headline_mom_pct":0.6,"core_mom_seasonally_adjusted_pct":0.3,"core_mom_august_pct":0.3,"core_mom_september_pct":0.3,
"headline_yoy_pct":None,"core_yoy_pct":None,
"yoy_unavailable_reason":"BLS因2025年10月拨款中断未采集调查数据，多数2025-10指数未公布，因此2026-10相应同比无法公布；总CPI及核心CPI表格均为缺失，并非0。",
"components_mom_pct":{"shelter":0.3,"owners_equivalent_rent":0.3,"rent_primary_residence":0.2,"food":0.5,"food_at_home":0.4,"food_away_from_home":0.5,"energy":0.7,"prior_energy":5.2,"gasoline":1.0,"electricity":0.9,"utility_gas":-0.8,"used_cars_trucks":-1.2,"medical_care":0.3,"recreation":0.8,"motor_vehicle_insurance":0.7,"services_less_energy":0.3},
"component_adjustment_note":"除food_away_from_home为未季调（BLS表1脚注1）外，上列本月百分比为BLS季调口径；不得与未季调汽油-0.7%混用。",
"headline_unadjusted_index":337.511,"headline_unadjusted_mom_pct":0.2,"shelter_contribution_note":"官方称住房贡献超过总月涨幅的30%。",
"consensus_surprise":None,"sources":[url("cpi"),url("cpi_table")],
"interpretation":"总环比较9月放缓，但核心0.3%连续三月；尚不足确认通胀快速消退或降息。没有核市场一致预期，不作超预期/低于预期标签。",
"counterargument":"能源月涨幅由5.2%降至0.7%、住房由0.4%降至0.3%，说明部分压力在缓和；不能只据单月核心判定持续再通胀。"
}
treasury={"date":"2026-11-10","two_year_pct":4.73,"ten_year_pct":4.98,"previous_date":"2026-11-09","previous_two_year_pct":4.56,"previous_ten_year_pct":4.88,"two_year_change_bp":17,"ten_year_change_bp":10,"ten_minus_two_bp":25,"prior_ten_minus_two_bp":32,"source":url("treasury"),"basis":"美国财政部名义平价收益率/CMT，依近15:30 EST指示性买方报价插值得出，并非实际成交或实时收益率。","indicative_time_et":"2026-11-10T15:30:00-05:00","indicative_time_beijing":"2026-11-11T04:30:00+08:00","interpretation":"名义折现率约束加重，尤其影响远期现金流权重高的成长公司；同日变动不能全部因果归于CPI。"}
vix={"date":"2026-11-10","close":19.46,"unit":"index_points","previous_close":19.92,"change_points":-0.46,"change_pct":round((19.46/19.92-1)*100,8),"sources":[url("vix"),url("vix_wsj")],"official_display_time":"9:15 PM 11/10/2026，页面未注明时区","secondary_time_original":"3:15 PM CST 11/10/26","time_et":"2026-11-10T16:15:00-05:00","time_beijing":"2026-11-11T05:15:00+08:00","official_csv_latest_date":"2026-11-09","verification":"Cboe本次页面19.46与WSJ历史表11/10收盘19.46吻合；Cboe历史CSV本次仍仅至11/9，不冒称CSV已核11/10。","interpretation":"期权隐含波动下降与名义利率上升同时发生，VIX下降不能替代估值或信用风险判断。"}
sgov={"sec_30_day_yield_pct":3.85,"asof":"2026-11-09","previous_verified_pct":3.84,"previous_verified_asof":"2026-11-06","change_bp_vs_previous_verified":1,"trailing_12m_yield_pct":3.63,"expense_ratio_pct":0.09,"source":url("sgov"),"note":"SEC30日收益率为历史区间收入年化口径；不是总回报、派息率或未来保证收益。本次官网收益日期仅11/9，不标成11/10。"}
credit={"release_date":"2026-11-10","release_time_et":None,"reference_quarter":"2026Q3","household_debt_trillion_usd":19.105,"quarter_increase_billion_usd":334,"credit_card_debt_trillion_usd":1.285,"credit_card_quarter_increase_billion_usd":22,"all_debt_any_delinquency_stock_pct":5.0,"stock_change_pp_qoq":0.3,"credit_card_new_90plus_delinquency_annualized_flow_pct":6.87,"credit_card_prior_year_flow_pct":7.05,"flow_change_pp_yoy":-0.18,"card_flow_qoq_direction":"slightly_improved","mortgage_flow_90plus_pct":1.60,"mortgage_flow_90plus_prior_year_pct":1.28,"sources":[url("nyfed"),url("nyfed_blog")],"definition":"存量5.0%是所有债务已有某阶段逾期的余额占比；6.87%是信用卡余额新转入90天以上逾期的年化流量，分母为上期未达90天逾期的余额，二者不能直接比较。","sofi_readthrough":"只构成SOFI信用风险研究背景，不能套成其借款人或个人贷款净核销率。继续核其分产品净核销、30/90天逾期、出售/留存贷款与公允价值假设。","counterargument":"信用卡新增严重逾期流量略改善；低收入地区压力更大，但NY Fed按邮编平均收入分组，不等于每个借款人的实际收入。"}
gaps=[
"BLS与AMAT直接curl本次403，已用公开web读取官方完整页/关键表并保存web响应，不绕过限制。",
"NYSE直接curl DNS超时、WSJ curl TLS失败；公开web官方日历和WSJ历史表读取成功，HTTP失败记录保留。",
"10月CPI总/核心同比是BLS正式缺失，不能计算或用近月同比填补；未核市场一致预期。",
"Cboe页面9:15 PM未明示时区，明确时区来自WSJ；本次官方VIX历史CSV仅到11/9。",
"MRNA分析师日仅日期确认，精确开始时间未核；未来科技财报为相关性精选，不声称完整43家公司日历。",
"NY Fed新闻稿只列发布日期、未列小时；博客索引11:00显示时区未明示，未用来推算发布北京时间。"
]
sources=[]
for r in json.loads((OUT/"macro_raw/http_receipts.json").read_text()):
 sources.append(r)
sources.extend([
dict(id="web_cpi_credit_vix",file="macro_raw/web_primary_cpi_credit_vix.json",read_scope="官方CPI正文与同比缺失说明、CPI表1、NYFed正文/表格及VIX官网；本轮web原文读取",retrieved_at_utc=now),
dict(id="web_schedules_vix",file="macro_raw/web_schedules_cpi_table_vix.json",read_scope="BLS日历、就业日历、表1、WSJ历史表、AMAT公告的本轮web原文响应",retrieved_at_utc=now),
dict(id="web_credit_blog",file="macro_raw/web_credit_blog.json",read_scope="NYFed研究博客原文（正文、图注、定义及反证），未将作者观点等同FOMC政策",retrieved_at_utc=now),
dict(id="web_mrna_nyse",file="macro_raw/web_mrna_nyse_calendar.json",read_scope="MRNA SEC分析师日与NYSE官方日历",retrieved_at_utc=now)
])
data=dict(schema_version=1,report_date="2026-11-11",reviewed_at=now,market_session="2026-11-10",next_session="2026-11-11",calendar_window_et=["2026-11-11","2026-11-17"],timezone={"market":"America/New_York","report":"Asia/Shanghai","utc_offset_et":"-05:00","beijing_minus_et_hours":13},
session_check={"latest_regular_close_et":"2026-11-10T16:00:00-05:00","latest_regular_close_beijing":"2026-11-11T05:00:00+08:00","next_regular_open_et":"2026-11-11T09:30:00-05:00","next_regular_open_beijing":"2026-11-11T22:30:00+08:00","next_premarket_start_et":"2026-11-11T04:00:00-05:00","next_premarket_start_beijing":"2026-11-11T17:00:00+08:00","next_premarket_status":"not_started","after_hours_session_date":"2026-11-10","after_hours_end_et":"2026-11-10T20:00:00-05:00","after_hours_end_beijing":"2026-11-11T09:00:00+08:00","after_hours_status_at_review":"ongoing","veterans_day":"11/11美国股票按NYSE日历正常开市；SIFMA对美元债券等市场建议休市，不能由政府/债市假期推成股票休市。","sources":[url("nyse"),url("sifma")]},
macro={"cpi":cpi,"treasury":treasury,"vix":vix,"sgov":sgov,"nyfed_household_credit":credit},events=events,
outside_window=[event("next_cpi","美国11月CPI","2026-12-10T08:30:00-05:00",["cpi"]),event("next_jobs","美国11月就业报告","2026-12-04T08:30:00-05:00",["jobs"]),dict(id="next_fomc",title="下次FOMC会议",dates_et=["2026-12-08","2026-12-09"],status="scheduled",sources=[url("fomc")],note="未来7日无FOMC决议。")],
coverage_gaps=gaps,sources=sources)
(OUT/"macro_calendar.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")
# Fresh conclusions for the parent; generic research only, no private holdings.
items=[
dict(id="cpi_and_discount_rate",title="CPI环比放缓但核心仍黏；利率上升时暂不放宽安全边际",
fact="10月总CPI季调环比+0.4%（9月+0.6%），核心+0.3%连续三月；2年/10年美债平价收益率11/10升至4.73%/4.98%，日升17/10bp。",
impact="工资、保险和融资成本仍可能挤压利润；远期现金流折现压力上升，AI应用公司的业务增长不能直接抵消估值风险。",
judgment="继续核现金流兑现与保守估值，不因总CPI放缓或VIX下降上调买入上限；未核一致预期，不判定意外方向。",
counter="能源月涨幅由5.2%降至0.7%、住房由0.4%降至0.3%，部分压力正在缓和；同日利率变化不能全部归因CPI。",
next="11/12初请、11/13 PPI和后续价格分项；CPI总/核心同比因2025-10基数缺失未公布，应留空。",
sources=[url("cpi"),url("cpi_table"),url("treasury")]),
dict(id="credit_stock_vs_flow",title="家庭逾期存量上升，但信用卡新增严重逾期略改善",
fact="NY Fed Q3：总债务$19.105万亿，某阶段逾期余额占比5.0%（季升0.3pp）；信用卡新转90天以上逾期年化流量6.87%，低于去年同期7.05%。",
impact="消费信贷压力值得跟踪，但存量累积与新增违约速度给出的信号不同。",
judgment="SOFI继续以自身贷款质量、核销与估值为依据，不能把全国信用卡指标直接当作其个人贷款违约率。",
counter="信用卡新增严重逾期环比略改善，疫情期低质量批次影响正在减弱；借款人和产品结构有差异。",
next="核SOFI分产品逾期/净核销、出售贷款与留存敞口、公允价值及正常化EPS假设。",
sources=[url("nyfed"),url("nyfed_blog")])
]
(OUT/"macro_items.json").write_text(json.dumps(items,ensure_ascii=False,indent=2)+"\n")
md=f"""# 宏观与日历复核｜北京时间2026-11-11

复核：{now}。市场日：2026-11-10；未来事件窗：美东11/11–11/17。本文件仅公开研究。

## 可用于首页的结论

**CPI环比放缓，但核心仍黏；名义利率明显上升，暂不放宽估值安全边际。** 总CPI季调环比+0.4%（9月+0.6%），核心+0.3%连续三月；住房+0.3%、食品+0.5%、能源+0.7%，二手车-1.2%。这是11/10 08:30 EST／北京时间11/10 21:30已发布结果。**总CPI、核心CPI同比均未公布**：去年10月拨款中断造成基数缺失，官方表1显示缺失，不能补数。[BLS正文]({url("cpi")})、[BLS表1]({url("cpi_table")})

解释：整体涨幅下降不代表价格下跌，也不足确认通胀快速回落或降息。最强反证是能源、住房环比放缓；未核一致预期，不能写超/低于预期。下一步看11/13 PPI及后续核心分项。

## 利率、波动及SGOV

| 指标 | 本次核定值 | 日期与口径 |
|---|---:|---|
| 2年美债 | 4.73%，日升17bp | 11/10 Treasury名义平价/CMT，前日4.56% |
| 10年美债 | 4.98%，日升10bp | 11/10 Treasury名义平价/CMT，前日4.88% |
| 10年−2年 | 25bp | 前日32bp；按同源同日计算 |
| VIX | 19.46，-0.46／-2.31% | 11/10；Cboe与WSJ历史收盘一致 |
| SGOV SEC30日收益率 | 3.85% | 官网截至11/9；前次核定11/6为3.84%，上升1bp |
| SGOV 12月尾随收益率 | 3.63% | 与SEC30日不同口径，均非未来总回报保证 |

[Treasury]({url("treasury")})使用约15:30 EST指示性买方报价插值（北京时间11/11 04:30），非实际成交或实时利率。[Cboe]({url("vix")})显示9:15 PM未注明时区；[WSJ历史表]({url("vix_wsj")})明确11/10 15:15 CST＝16:15 EST＝北京时间11/11 05:15。本次Cboe CSV只到11/9。VIX用指数点、不用美元。利率上升与隐含波动下降同时发生，不能将VIX下降直接当成风险消失。[SGOV官方]({url("sgov")})收益日期只有11/9，不冒称11/10。

## NY Fed家庭信用：对SOFI的研究线索

11/10新发布Q3数据：家庭债务$19.105万亿（季增$3340亿），信用卡$1.285万亿（季增$220亿）。所有债务中某阶段逾期的**存量**余额占比5.0%，季升0.3个百分点；信用卡新转入90天以上逾期的**年化流量**为6.87%，去年同期7.05%，官方称环比略改善。这是不同分母和含义，不能写成“信用卡逾期5.0%升到6.87%”。[官方新闻稿]({url("nyfed")})

判断：跟踪消费者偿债压力；不据全国信用卡数据单独上调SOFI贷款损失假设。反证：新增严重逾期流量略改善，疫情期间发放批次的影响减弱。补核SOFI自身个人贷款净核销、逾期、出售与留存敞口。纽约联储博客按邮编平均收入分组，不能当成每个借款人的实际收入，也不能直接映射SOFI客群。[官方研究博客]({url("nyfed_blog")})

## 交易时间与未来7日

最近完成常规交易日11/10；下一交易日11/11，NYSE股票正常开市（北京时间22:30）。老兵日SIFMA建议美元债券等市场休市，**不等于股票休市**。本次北京时间07:30附近为前一美东18:30，11/10盘后仍进行至北京时间09:00；下一交易日盘前尚未开始（北京时间17:00）。[NYSE]({url("nyse")})、[SIFMA]({url("sifma")})

| 事件 | 美东EST | 北京时间 | 说明 |
|---|---|---|---|
"""
for e in events:
 et=e.get("time_et")
 if et:
  dt=datetime.fromisoformat(et);bj=datetime.fromisoformat(e["time_beijing"])
  md+=f'| {e["title"]} | {dt:%m/%d %H:%M} | {bj:%m/%d %H:%M} | {e.get("note","")} [官方]({e["sources"][0]}) |\n'
 else: md+=f'| {e["title"]} | {e["date_et"]}，具体小时未核 | 待核 | {e["note"]} [SEC]({e["sources"][0]}) |\n'
md+=f"""
未来7日无新CPI、月度就业报告或FOMC决议：下一CPI12/10 08:30 EST／21:30北京；下一就业12/4同一时刻；FOMC12/8–9。[BLS就业日历]({url("jobs")})、[FOMC日历]({url("fomc")})。科技财报为相关性精选，非43项穷尽列表。

## 核验缺口与证据

"""
md+="\n".join("- "+x for x in gaps)
md+="\n\n原始证据在macro_raw/；每项HTTP获取时刻与失败状态保留于http_receipts.json，web原文响应另存。行情/来源本轮重新取得；只用前次SGOV记录作已核值变化比较。未修改站点、alert_state、私账或其他全局状态。\n"
(OUT/"macro_calendar.md").write_text(md)
print(json.dumps({"outputs":["macro_calendar.json","macro_calendar.md","macro_items.json"],"reviewed_at":now,"events":len(events)},ensure_ascii=False))

