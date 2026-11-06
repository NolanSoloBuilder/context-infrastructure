from pathlib import Path
from datetime import datetime,timezone
import json
P=Path(__file__).resolve().parent;R=P.parents[3];m={r['symbol']:r for r in json.loads((P/'metrics.json').read_text())}
portfolio=json.loads((P.parent/'portfolio_private/latest.json').read_text());positions=portfolio['positions'];cost=sum(p['broker_cost_basis_usd'] for p in positions);market=sum(p['quantity']*m[p['symbol']]['close'] for p in positions);google_weight=next(p['quantity']*m[p['symbol']]['close'] for p in positions if p['symbol']=='GOOG')/market*100
f=lambda x: f'{x:+.2f}%';d=lambda x:f'{x:.2f}'
held='| 实际代码 | 基线券商均价／美元 | 10/30收盘／美元 | 相对基线均价参考变化 |\n|---|---|---|---|\n'
for p in positions:held+=f"|{p['symbol']}|{p['average_cost_usd']:.4f}|{m[p['symbol']]['close']:.2f}|{f((m[p['symbol']]['close']/p['average_cost_usd']-1)*100)}|\n"
watch=(P/'watchlist_table.md').read_text()
# Preserve same-source observation prices while making the BRK discrepancy visible.
watch=watch.replace('467.76 / 412.73','467.76 / 412.73（新高待核）')
watch+='\nBRK.B表中与图中暂按Yahoo新高550.30计算，第二来源为550.47；精确高点未核定，因此本日不将它写入持久提醒状态。上次有效高点549.96对应467.47／412.47，保留作历史状态，不当成已核的10/30新观察价。QQQM高点314.11与第二源314.12差一美分，阈值相差一美分，已披露而不触发重复提醒。\n'
levels='| 标的 | 当日收盘 | 高点／日期 | 回撤幅度 | 距15%差额（百分点） | 当前价至15%需变动 | 状态 |\n|---|---|---|---|---|---|---|\n'
for s in ['QQQM','VOO','BRK-B']:
 r=m[s];D=-r['drawdown_pct'];levels+=f"|{'BRK.B' if s=='BRK-B' else s}|{r['close']:.2f}|{r['high_52w']:.2f}／{r['high_date']}|{D:.2f}%|{15-D:.2f}|{r['additional_drop_to_15_pct']:+.2f}%|{'新高差异待核，不更新提醒' if s=='BRK-B' else '不足13%，无新提醒'}|\n"
sector=['XLK','XLC','XLY','XLP','XLV','XLF','XLI','XLE','XLU','XLB','XLRE','SMH'];sector.sort(key=lambda s:m[s]['day_pct'],reverse=True)
sector_table='| 行业／ETF | 当日 | 近5交易日 | 近21交易日 | 当日相对VOO（百分点） | 近21日相对VOO（百分点） |\n|---|---|---|---|---|---|\n'
for s in sector:
 r=m[s];sector_table+=f"|{r['label']} {s}|{f(r['day_pct'])}|{f(r['five_session_pct'])}|{f(r['twenty_one_session_pct'])}|{r['day_pct']-m['VOO']['day_pct']:+.2f}|{r['twenty_one_session_pct']-m['VOO']['twenty_one_session_pct']:+.2f}|\n"
trends='|标的|当日|近5交易日|近21交易日|MA50|MA200|当日量／此前20日均量|\n|---|---|---|---|---|---|---|\n'
for s in ['VOO','QQQM','GOOG','GOOGL','BRK-B','RRX','CGNX','ATS','SOFI','NVDA','SMH','SOXX','SPMO','MAGS','VGT','DRAM','MRNA','SGOV']:
 r=m[s];trends+=f"|{s}|{f(r['day_pct'])}|{f(r['five_session_pct'])}|{f(r['twenty_one_session_pct'])}|{r['ma50']:.2f}|{r['ma200']:.2f}|{r['volume_vs_prior20']:.2f}倍|\n" if r['ma200'] is not None else f"|{s}|{f(r['day_pct'])}|{f(r['five_session_pct'])}|{f(r['twenty_one_session_pct'])}|{r['ma50']:.2f}|不足200交易日|{r['volume_vs_prior20']:.2f}倍|\n"
index_table='| 指数 | 收盘（点） | 当日 | 近5交易日 | 近21交易日 |\n|---|---|---|---|---|\n'
for s in ['^GSPC','^IXIC','^NDX']:
 r=m[s];index_table+=f"|{r['label']}|{r['close']:,.2f}|{f(r['day_pct'])}|{f(r['five_session_pct'])}|{f(r['twenty_one_session_pct'])}|\n"
report=f'''# 美股观察｜2026-10-31 北京时间

采用**美东2026-10-30（周五）常规收盘**，对应北京时间10/31 04:00。股票／ETF均为美元；指数为点。10/30正常交易，下一常规交易日为**11/2，因11/1结束夏令时，北京时间22:30开盘**。[NYSE](https://www.nyse.com/trade/hours-calendars) · [NIST](https://www.nist.gov/pml/time-and-frequency-division/popular-links/daylight-saving-time-dst)

**今日判断：已有VOO／QQQM／GOOG仓位，后续分批暂不加速；不要把半导体大跌直接当成便宜。** 标普500{f(m['^GSPC']['day_pct'])}，纳斯达克综合{f(m['^IXIC']['day_pct'])}，纳斯达克100{f(m['^NDX']['day_pct'])}。QQQM回撤9.48%，尚未进入13%接近档；VOO亦未进入，今日没有已核实的新跨档提醒。BRK.B新高存在来源差异，提醒状态保留上次有效记录。

你的期限仍为3–5年、计划预算30,000美元、可接受约6,000美元暂时亏损。45%股票／55%SGOV仍是未采用草案，20%不是保证的最大损失。持仓依据为**10/30 09:37北京时间核验的本地基线**，本次只更新市场价格，未重新登录嘉信核对数量或可用资金。

**今天对你最重要的事**

1. **已经买入，重点改为控制叠加风险。** QQQM今日−3.46%，成交量约此前20日均量2.89倍；VOO−1.77%，约1.87倍。按最后有效数量计算，GOOG直接占已知股票市值约**{google_weight:.1f}%**，VOO／QQQM还提供同公司的间接暴露，穿透权重本次未重核。它不等于总资产权重，也不能用30,000美元计划预算推断全部钱已经到账。建议下一笔先确认股票上限和固定额度，研究排序仍偏VOO、再QQQM；暂不同时叠加MAGS／VGT／半导体来追跌。反证是成长股现金兑现好于预期、迅速反弹；代价是放弃部分反弹弹性。[QQQM历史行情](https://stockanalysis.com/etf/qqqm/history/) · [VOO历史行情](https://stockanalysis.com/etf/voo/history/)
2. **AI融资风险出现新的原始证据，Google的回款模型仍需保守。** S&P于10/30 **17:01 EDT（北京10/31 05:01）**将Meta展望从稳定调为负面，**AA−评级维持**。这是收盘后的事件，不能倒推解释全天跌幅，也不是Alphabet被降评级。它提示QQQM／MAGS内的AI投入风险可能同时发生。本次又核Google已发布10-Q：TPU硬件交付与持续安装／支持服务收入确认不同，部分合同有多年回购权，云订单不应全部按永续服务利润率估值。最强反证是客户持续回款、硬件与服务单位经济性兑现；下一项看交付、实际回款及回购／担保变化，旧买价继续暂停。[S&P官方行动表](https://www.spglobal.com/ratings/en/regulatory/ratings-actions?tz=hkt) · [具体核验与限制](./macro_research.md) · [FiNews线索回查](./finews_digest.md)
3. **半导体跌幅很大，安全边际尚未因此成立。** SOXX−8.24%，SMH−6.98%，DRAM−7.23%；SOXX／SMH距各自52周盘中高点回撤28.12%／22.23%。这些标的**没有获批的15%／25%仓位规则**，不能据此自动补仓。你目前明确持有的三只证券未包含它们；已有纳指与Google敞口时，应先验证盈利和现金回报，再考虑从同一股票预算中划出额度。反证是订单与盈利继续强劲、价格调整早于经营兑现；下周AMD业绩是新增可核查条件。[SOXX历史行情](https://stockanalysis.com/etf/soxx/history/) · [SMH历史行情](https://stockanalysis.com/etf/smh/history/)

**对你当前状态的建议**

按10/30最后有效持仓数量、用10/30常规收盘估算，已知股票市值约**{market:,.2f}美元**，较基线券商成本约**{(market/cost-1)*100:+.2f}%**。这是价格更新后的参考浮盈亏，不含分红、税费或后续成交，不是账户总回报；买入日期和税批未核验。

{held}
GOOG相对自身52周高点已回撤31.21%，相对你的基线均价仅约−1.31%，两种参照不同。GOOGL279.84仅作公司研究；真实持仓GOOG使用278.22，绝不混算股价或成本。

当前建议是维持既有观察，后续按固定时间和限定额度评估，**今天暂不因单日跌幅追加额外批次，也不恢复Google旧研究价位**。原45／55配置与定额分批没有被当成已执行。若下一步配置仍以控制回撤为先，新增主题ETF与个股共用同一股票预算；可留有短期美债防守配置，无急用资金不等于应全部持有股票。结算状态须看实际券商余额，不能仅按自然日两天推定资金已结算。[嘉信现金账户规则](https://www.schwab.com/learn/story/avoid-these-violations-when-trading-cash)

[固定在线观察台](https://nolan-market-watch.choice-calf-0415.chatgpt.site/)已按你的新要求支持一年／两年／三年同步切换收益、年化波动和最大回撤，MA50／200固定，曲线可看收盘极值及日期／价格提示。公开站点仅含行情与通用研究，本篇个性化持仓信息只保留在本地日报。

{watch}

![近60交易日价格走势与当时可见滚动回撤](./watchlist_curves.png)

**Google估值结果**

GOOGL收279.84（−1.40%），GOOG收278.22（−1.45%）；公司研究与真实持仓报价分开。10/30没有在所读SEC recent列表中发现更新的经营8-K；最新Form4正文未读，不能推断减持意图。已发布Q3 10-Q及昨日资本桥继续有效，**本次没有重算新合理价**。

昨日十年模型三情景68.25／216.28／402.11美元仍是带主观增长、利润率、资本支出、营运资金与折现率的条件结果。GOOGL现价高于该基准约{(m['GOOGL']['close']/216.2809582074652-1)*100:.1f}%，下跌后仍未证明充分安全边际，不把区间结果改成买单。TPU收入确认、回购与服务经济性的本次追加核验，见[原始合同条款与推论](./macro_research.md)；财务基线与模型见[10/30资本桥](../2026-10-30/google_update/google_update.md)。下一次重点在回款和2027投入，不再用“尚缺10-Q”拖延。

**SOFI研究观察**

SOFI16.76（−4.83%），近5交易日仍+14.68%。以公司2027管理层调整EPS0.90展望作简单参照约**18.62倍**，它是未来非GAAP口径，不是已实现盈利，也没有完整计入潜在稀释。SEC recent本次重取，仍未见Q3完整10-Q；不能把已出业绩公告与完整贷款／信用附注混为一谈。保持估值待完成，继续查信用损失、资金成本、资本回报和股数。[原有资本回报检验](../2026-10-30/sofi_research.md) · [本次SEC核验](./macro_research.md)

**机器人供应链筛选**

RRX157.24（−3.90%）相较未经压力调整的165.07参考值低约4.7%，仍高于恢复25%摊销为经济成本的主观148.41情景；上述EPS／17倍乘数及恢复比例都是研究假设，不足以判定低估。11/3财报重点是现金转化、持续调整项和去杠杆。CGNX56.15、ATS18.39保留有条件候选；11/4盘后CGNX核整合支出与稀释，ATS继续核订单回款及杠杆。[昨日成本压力依据](../2026-10-30/robotics_update.md)

MRNA221.72（−0.47%）只是医疗生物科技研究对象，不能把AI医疗叙事直接等同Moderna低估。11/6核现金消耗、融资与商业化；历史日线含8/19极端跳变，对回报和年化波动影响显著，已知价格核验不等于事件原因已查清。本次没有新增“已低估”股票。

**行业观察**

11个行业ETF **6涨5跌**，SMH另列。科技与半导体的跌幅显著大于其他行业；这是行业ETF层面的价格分化，不是所有个股广度或资金净流向。

- **XLK−4.89%、SMH−6.98%**：与你的成长敞口直接相关，量能放大仍不能单独确认底部；SOXX的−8.24%也不自动代表与SMH独立分散。
- **XLE+1.91%、XLP+1.41%**：价格相对强，不据单日领涨转换成追买理由；能源仍需核商品周期和估值。
- **XLV+0.45%、XLU+0.67%**：防守方向相对稳定，但医疗行业强势不能直接推导MRNA盈利兑现。

![11行业ETF与半导体单日表现](./sector_daily.png)

{sector_table}

**🔎 Reddit 投资与信息差观察**

**未完成24小时扫描**：六社区RSS403，可读New／Top仍有旧缓存；不把访问失败说成“没有新讨论”。昨日Google两帖已去重。本次只保留一项72小时内旧事件的新研究核验：Oracle10/28关于未来现金流和融资的管理层展望，原帖绝对时间未核、只读正文和一条反方评论，不称社区共识。

对GOOG／QQQM更有价值的问题是：客户预付款、供应商融资与实际项目现金回报，分别改善了什么。提前收钱或延期付款并不自动证明终端盈利；反证是合同覆盖投入且持续回款兑现。[原帖与原始公司公告核对](./reddit_digest.md) · [读取范围及缺口](./reddit_sources.json)

FiNews本次读到10/30日报，更新为UTC22:10:49（北京10/31 06:10:49）；S&P的Meta展望和Okta11/4盘前替换Kenvue入标普已回查原始来源。Okta是指数维护事件，不构成VOO低估或必涨依据。其非农北京时间22:30有一小时偏差，本版采用BLS／冬令时换算的**11/6 21:30**。[聚合内容核验](./finews_digest.md)

**距观察档还有多远**

{levels}
QQQM离13%接近区间还差3.52个百分点；从284.34到266.99的15%观察价需约**−6.10%**。百分点衡量回撤差额，百分比衡量当前价格到目标价的变动，不能混用。它是继续观察已有仓位的信号，不是首笔或自动加仓命令。

BRK.B10/30高点Yahoo550.30、StockAnalysis550.47，均较此前549.96高，但精确高点有差异。两个来源都为第三方且可能共用上游，未取得交易所有效历史表；图表保留Yahoo统一口径，本次**不推进BRK.B提醒状态日期或新高阈值**，防止未核数据替换最后有效记录。QQQM／VOO已完成收盘交叉核验，阶段均未变。[本次报价核验](./quote_verification.json)

**利率与未来一周事件**

财政部10/30：**2年4.56%、10年4.94%**，较前日−5／−4基点；为参考曲线，不是可成交收益。VIX统一日线19.42、+12.91%，Cboe日期摘要一致；其独立时钟模块时区不明、官方CSV尚未覆盖10/30，不称16:00同步逐笔。[财政部](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value=2026) · [Cboe](https://www.cboe.com/tradable-products/vix/)

ECI已于10/30发布：民用总薪酬季调环比+0.8%，同比未季调+3.4%；没有核一致预期，不写超预期，也不把它作为继续等待的门槛。下周JOLTS11/3北京23:00、生产率11/5 21:30、非农11/6 21:30；AMD11/3美东盘后、电话会北京11/4 06:00；Moderna电话会11/6北京21:00。RRX11/3、CGNX11/4美东盘后财报／11/5北京21:30电话会沿用近期已核官方日历。本周末结束夏令时后所有美股常规开盘为北京时间22:30。[本次官方日历与缺口](./macro_research.md)

SGOV本次未重核收益率；最近核验为**10/28的30日SEC收益率3.79%**，仅历史参考，未来收入随短端利率和费用变化，不是当前可锁定收益或总回报。[发行人](https://www.ishares.com/us/products/314116/ishares-0-3-month-treasury-bond-etf)

**完整表现与趋势数据**

{trends}

{index_table}

**口径、核验和缺口**

- 行情为本次新取的10/30完整日线，共33项（17研究标的、额外实际证券GOOG、行业与指数去重后）。18个股票／ETF常规收盘已与带日期的第二来源页面核对一致；直接HTTP403的访问失败另存，公开网页工具读到的内容与时间独立留证，未绕过登录或访问限制。来源可能共用上游，不等于官方交易所逐笔审计。
- QQM相关统一采用QQQM，不重新引入QQQ。提醒范围仅QQQM／VOO／BRK.B；BRK本日高点缺口保留有效旧状态，其余两项可更新。QQQM高点一美分差异照常披露。
- 60个连续日收盘观察为8/7—10/30，跨59个价格间隔；逐日回撤仅用当时可见364日盘中高点，曲线未使用今天高点回填历史。价格曲线不含分红；在线一年／两年／三年累计收益等使用复权总回报代理，二者分别标清。
- MA50／200使用拆股调整Close；量比为当日量／此前20日均量，不含当天。DRAM不足52周／200交易日留空；SOXX11/5拆股后须统一序列。全市场成分股广度、指数盈利估值分母、候选完整低估模型仍有缺口。
- 时段采集于UTC23:29:30／北京时间07:29:30，所有最新分钟参考为零量；与第二来源不同报价时点的价格差异保留。采集时盘后尚未结束，不是最终收盘、不更新提醒。11/2盘前尚未开始。[盘前盘后详情](./extended_detail.md) · [时段原始来源](./extended_quotes.json) · [时段交叉核验](./extended_verification.json)
- Google／SOFI／机器人陈述注明是新事实、本次追加核验或历史条件模型；Reddit扫描覆盖失败与没有新内容分开。所有持仓数量仍沿用10/30授权基线，未自动读取嘉信或操作订单。个性化日报未发布到公开站点。
- 两张PNG已打开核对中文、日期、正负号、末值。HTML沿用现有模板并核对资源与关键数字，未重复声称手机／桌面实机验收。在线站点此前已完成独立交互验收，此结论不替代本次本地日报的浏览器检查。

[完整日线指标](./metrics.json) · [原始清单](./manifest.json) · [本次最终核验](./verification.json) · [分类表数据](./watchlist_table.json)
'''
report=report.replace('QQM相关统一采用QQQM','纳斯达克100相关统一采用QQQM')
(P/'report.md').write_text(report)
print('report words',len(report),'held securities change',round((market/cost-1)*100,2),'Google direct known-stock weight',round(google_weight,2))
