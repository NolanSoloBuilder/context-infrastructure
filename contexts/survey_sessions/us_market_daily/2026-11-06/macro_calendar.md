# 2026-11-06 宏观、交易日及事件核验

复核完成：2026-11-06 07:30:51 北京时间（2026-11-05 18:30:51 EST）。此文件仅是公开资料核验底稿，未改站点、私账或提醒状态。

## 交易日期与时段

美国11月5日（周四）为正常交易日，最近常规时段已结束；下一常规交易日11月6日（周五），09:30–16:00 EST，对应北京时间11月6日22:30至11月7日05:00。当前美国已采用冬令时，北京快13小时。11月6日盘前尚未开始；11月5日盘后通常至20:00 EST＝北京时间11月6日09:00，07:30日报时仍不能称最终盘后收盘。11月11日Veterans Day不是NYSE股票休市日；政府/债券发布日历应另看。[NYSE官方休市与时段表](https://www.nyse.com/trade/hours-calendars)

## 最新宏观读数

| 指标 | 日期与口径 | 最新 | 前值／变化 | 核验 |
|---|---|---:|---:|---|
| VIX | 11月5日指数收盘参考，单位为指数点 | 28.18 | 前16.61；+11.57点／+69.66% | Cboe官方概览、Yahoo日线、Reuters正文一致 |
| 2年美债 | 11月5日财政部CMT日度收益率 | 4.46% | 前4.58%；−12bp | 财政部原表；不是股票收盘成交价 |
| 10年美债 | 同上 | 4.84% | 前4.90%；−6bp | 财政部原表；10Y−2Y为+38bp |
| SGOV 30日SEC收益率 | 官方最新可读截至11月4日 | 3.83% | 非派息率／非总回报 | 本周新读取官方日期；未冒充11月5日 |

VIX官方概览已经更新11月5日28.18，历史CSV仍只到11月4日16.61。Yahoo元数据时刻为11月5日16:15:01 EST（北京时间11月6日05:15:01）；Cboe页面另写9:15 PM却未标时区，不将其转写为EST。Yahoo网页显示的69.78%与前收不符，采用(28.18/16.61−1)算出的69.66%，与Cboe一致。[Cboe](https://www.cboe.com/tradable-products/vix/) · [官方历史CSV](https://cdn-api.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv) · [Yahoo日线](https://finance.yahoo.com/quote/%5EVIX/history/?p=%5EVIX) · [Reuters转载正文](https://new.streetinsider.com/Reuters/Wall%2BStreet%2Bfear%2Bgauge%2Bsoars%2Band%2Bretail%2Btraders%2Bbolt%2Bas%2Bmarkets%2Bin%2Btailspin%C2%A0/27298625.html)

财政部收益率来自约15:30 EST的指示性买价拟合（北京时间次日04:30），并非实际债券成交。FRED本次最新观察仍为11月4日2Y4.58%、10Y4.90%，故不能拿FRED更新时间11月5日冒充观察日。财政部新路径原表已经读到11月5日，采用该表。[财政部11月原表](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?field_tdr_date_value=202611&type=daily_treasury_yield_curve)

SGOV官方另列12个月追踪派息收益率3.63%、费率0.09%、有效久期0.11年，均要与30日SEC口径区别。30日SEC收益率为短期净投资收益的标准化年化尺度，不等于未来一年回报承诺；不将派息率与价格变动简单混称总回报。当前网页“持仓数0”看似缺字段，未采为真实持仓结论。[iShares SGOV官方](https://www.ishares.com/us/products/314116/ishares-0-3-month-treasury-bond-etf)

**解释：** 利率下降与VIX急升同时发生，更支持风险偏好恶化而非单纯贴现率利好；这只是宏观解释，不能据此判断个股已低估或自动触发买入。

## 未来一周：11月6日至12日，美国日期

| 事件 | 美国东部时间（EST） | 北京时间 | 状态与出处 |
|---|---|---|---|
| Moderna 2026Q3电话会 | 11月6日08:00 | 11月6日21:00 | 尚未召开；发布时间不等同电话会开始，具体业绩须等公告。[公司分发公告](https://www.nasdaq.com/press-release/moderna-report-third-quarter-2026-financial-results-friday-november-6-2026-2026-10-13) |
| 10月就业报告／非农 | 11月6日08:30 | 11月6日21:30 | 尚未公布。[BLS月历](https://www.bls.gov/schedule/2026/11_sched.htm) |
| 10月CPI | **11月10日08:30** | **11月10日21:30** | 尚未公布；本次11/3更新的月历与CPI专门日程均核为11/10，不能写11/12。[BLS CPI日程](https://www.bls.gov/schedule/news_release/cpi.htm) |
| 首次申请失业救济 | 11月12日08:30 | 11月12日21:30 | 尚未公布；按DOL已发布周四规则及2026明确例外清单推定，该周未列例外。[DOL日程](https://oui.doleta.gov/unemploy/claims_arch.asp) |
| Cisco FY2027Q1业绩／电话会 | 11月12日盘后／16:30电话会 | 11月13日05:00后／05:30电话会 | 尚未公布。[Cisco官方11/3公告](https://newsroom.cisco.com/c/r/newsroom/en/us/a/y2026/m11/cisco-schedules-conference-call-for-q1-fiscal-year-2027-financial-results.html?source=rss) |
| Applied Materials FY2026Q4电话会 | 11月12日16:30 | 11月13日05:30 | 尚未召开；已核官方活动页。[AMAT官方](https://investor.appliedmaterials.com/events/event-details/q4-2026-applied-materials-earnings-conference-call) |

未来一周**没有预定FOMC决议**。10月28日决议已经发布，维持3.75%–4.00%；该次决议仍是EDT，对应北京时间10月29日02:00。下一次会议12月8–9日；10月会议纪要11月18日14:00 EST＝北京时间11月19日03:00，均在本周窗口之外。[FOMC会议表](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) · [已公布10/28声明](https://www.federalreserve.gov/newsevents/pressreleases/monetary20261028a.htm) · [11月官方日历](https://www.federalreserve.gov/newsevents/2026-november.htm)

窗口外保留两项：10月PPI于11月13日08:30 EST＝北京时间21:30；NVDA FY2027Q3业绩计划11月17日约16:20 EST＝北京时间11月18日05:20，电话会17:00 EST＝06:00，不能误写成未来一周财报。[NVDA官方10/28预告](https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Sets-Conference-Call-for-Third-Quarter-Financial-Results/default.aspx)

## 数据缺口

没有将搜索摘要当成最终利率原表；已解决财政部旧地址404。Cboe历史CSV与FRED存在发布滞后，官方概览和财政部原表已补足最新读数。Moderna官网直接打开动态活动栏为空，本次以公司分发原文（Nasdaq转载）并官方检索结果交叉核会期。SGOV只标最新实际可读11/4日期。本周宏观尚未公布的数值、市场预期及财报结果不填猜测。
