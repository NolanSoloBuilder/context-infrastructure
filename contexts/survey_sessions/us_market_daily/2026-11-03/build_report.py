from pathlib import Path
from datetime import datetime,timezone
import json
P=Path(__file__).resolve().parent
m={r['symbol']:r for r in json.loads((P/'metrics.json').read_text())}
f=lambda x:f'{x:+.2f}%'
portfolio=json.loads((P.parent/'portfolio_private/latest.json').read_text());positions=portfolio['positions'];cost=sum(p['broker_cost_basis_usd'] for p in positions);market=sum(p['quantity']*m[p['symbol']]['close'] for p in positions);gweight=next(p['quantity']*m['GOOG']['close'] for p in positions if p['symbol']=='GOOG')/market*100
held='| 实际代码 | 基线券商均价／美元 | 11/2收盘／美元 | 相对均价参考变化 |\n|---|---|---|---|\n'
for p in positions:held+=f"|{p['symbol']}|{p['average_cost_usd']:.4f}|{m[p['symbol']]['close']:.2f}|{f((m[p['symbol']]['close']/p['average_cost_usd']-1)*100)}|\n"
sector=list(['XLK','XLC','XLY','XLP','XLV','XLF','XLI','XLE','XLU','XLB','XLRE','SMH']);sector.sort(key=lambda s:m[s]['day_pct'],reverse=True)
st='| 行业／ETF | 当日 | 近5交易日 | 近21交易日 | 当日相对VOO（百分点） | 近21日相对VOO（百分点） |\n|---|---|---|---|---|---|\n'
for s in sector:
 r=m[s];st+=f"|{r['label']} {s}|{f(r['day_pct'])}|{f(r['five_session_pct'])}|{f(r['twenty_one_session_pct'])}|{r['day_pct']-m['VOO']['day_pct']:+.2f}|{r['twenty_one_session_pct']-m['VOO']['twenty_one_session_pct']:+.2f}|\n"
tr='| 标的 | 当日 | 近5交易日 | 近21交易日 | MA50 | MA200 | 当日量／此前20日均量 |\n|---|---|---|---|---|---|---|\n'
for s in ['VOO','QQQM','GOOG','GOOGL','BRK-B','RRX','CGNX','ATS','SOFI','NVDA','SMH','SOXX','SPMO','MAGS','VGT','DRAM','MRNA','SGOV']:
 r=m[s];ma200=f"{r['ma200']:.2f}" if r['ma200'] is not None else '不足200交易日';tr+=f"|{s}|{f(r['day_pct'])}|{f(r['five_session_pct'])}|{f(r['twenty_one_session_pct'])}|{r['ma50']:.2f}|{ma200}|{r['volume_vs_prior20']:.2f}倍|\n"
ix='| 指数 | 收盘（点） | 当日 | 近5交易日 | 近21交易日 |\n|---|---|---|---|---|\n'
for s in ['^GSPC','^IXIC','^NDX']:
 r=m[s];ix+=f"|{r['label']}|{r['close']:,.2f}|{f(r['day_pct'])}|{f(r['five_session_pct'])}|{f(r['twenty_one_session_pct'])}|\n"
levels='| 标的 | 收盘／美元 | 本次Yahoo高点／日期 | 回撤 | 15%观察价 | 25%观察价 | 距15%差额（百分点） | 当前价至15%需变动 |\n|---|---|---|---|---|---|---|---|\n'
for s in ['QQQM','VOO','BRK-B']:
 r=m[s];levels+=f"|{s}|{r['close']:.2f}|{r['high_52w']:.2f}／{r['high_date']}|{-r['drawdown_pct']:.2f}%|{r['level_15']:.2f}|{r['level_25']:.2f}|{15+r['drawdown_pct']:.2f}|{r['additional_drop_to_15_pct']:+.2f}%|\n"
watch=(P/'watchlist_table.md').read_text();watch+='\nBRK.B本次Yahoo盘中高点557.41，第二来源557.59；新观察价仅供同源图表展示、尚未核定，不写入提醒状态。最后有效状态仍为10/29、高点549.96及467.47／412.47两档。QQQM高点314.11与第二源314.12差一美分，沿用Yahoo统一口径。\n'
qma=m['QQQM']['ma200'];qdev=(m['QQQM']['close']/qma-1)*100
report=f'''# 美股观察｜2026-11-03 北京时间

采用**美东2026-11-02（周一）常规收盘**，对应北京11/3 05:00；股票／ETF为美元，指数为点。下一常规交易日11/3，北京时间**22:30开盘**。已结束夏令时，本文按EST换算；盘后另列实际时刻，不当最终收盘。[NYSE交易日与时段](https://www.nyse.com/trade/hours-calendars)

**今日判断：已有VOO／QQQM／GOOG仓位，后续分批暂不加速，尤其暂缓叠加半导体与Google个股风险。** 标普500{f(m['^GSPC']['day_pct'])}，纳斯达克综合{f(m['^IXIC']['day_pct'])}，纳斯达克100{f(m['^NDX']['day_pct'])}。QQQM距52周盘中高点回撤10.70%，尚未进入13%接近档，今天没有已核的新跨档提醒；BRK.B新高的精确数值仍待核。

**今天对你最重要的事**

1. **Google新融资要看回报和净债务，不能把借来的钱当经营改善。** 11/2新增SEC债券定价文件：**60亿欧元高级无担保债，预计11/5交割**。用途为一般公司用途，可能偿还原债；不能认定是AI专项或全额净新增杠杆，也未核实现金到账。六档固定票息年现金义务合计约**2.33亿欧元**，另有浮动档。你已有GOOG，直接占已知股票市值约{gweight:.1f}%，另有VOO／QQQM间接暴露，本次未重核穿透权重。因此融资消息不支持加速增加同公司敞口。最强反证是替代更高成本旧债、后续交付与现金回报覆盖新增成本；下一项核11/5交割与资金用途、TPU回款及2027投入。旧Google买价继续暂停。[SEC定价](https://www.sec.gov/Archives/edgar/data/1652044/000119312526443857/d134038dfwp.htm) · [公司研究与资本桥边界](./company_research.md)
2. **QQQM已接近200日均线，继续下跌时先控制追加速度。** 收280.49，MA200为{qma:.2f}，仅高{qdev:.2f}%；当日量为此前20日均量{m['QQQM']['volume_vs_prior20']:.2f}倍。SMH−2.71%、SOXX−3.79%、DRAM−3.52%，日跌幅或高点回撤都不能替代盈利估值。按你3–5年、尽量控制回撤的目标，维持已有观察；下一批若考虑执行，先核总股票上限与既定额度，研究顺序偏宽基VOO，暂不叠加多只科技／半导体产品。反证是成长盈利兑现、趋势快速反转；观察常规收盘与量能，不用盘后价格宣布200日线已守住或已跌破。均线是风险参照，不是保证或自动卖出线。[QQQM同日行情](https://stockanalysis.com/etf/qqqm/history/) · [SMH行情](https://stockanalysis.com/etf/smh/history/)
3. **SGOV−0.30%主要对应除息，不能读成短债突然大亏。** 官方确认11/2除息，每股收益分配**0.328581美元**，11/5支付。用前收100.73、本收100.43加应收分配估算，税前简单单日变化约**+0.0284%**，尚未包含税费与买卖价差，不是未来收益预测；仅看价格会漏掉该分配。最新可读30日SEC收益率**3.79%，截至10/30**，不冒充11/2的新收益率，不把派息率当总回报。你尚未确认持有SGOV，仍是暂存／防守候选，不是已执行55%配置。[发行人分红与SEC口径](https://www.ishares.com/us/products/314116/ishares-0-3-month-treasury-bond-etf) · [本次核验](./macro_research.md)

**对你当前状态的建议**

持仓数量沿用**10/30 09:37北京时间**授权核验的本地基线，未重新登录嘉信、未核定后续成交或已结算资金。本次只用11/2新收盘估算：已知股票市值约**{market:,.2f}美元**，相对基线券商成本约**{(market/cost-1)*100:+.2f}%**。它不是账户总回报，不含分红、税费、现金流与未确认的新交易。

{held}
GOOG相对自身52周盘中高点回撤31.26%，相对你的基线均价约{(m['GOOG']['close']/281.91-1)*100:+.2f}%，参照不同。真实GOOG使用278.04；GOOGL278.99只作公司研究，价格和成本不混算。

计划预算30,000美元、期限3–5年、暂时亏损约6,000美元的承受程度保持；20%不能保证为最大亏损，45%股票／55%SGOV仍未获采用。境外资金无急用不代表应全部持有股票，也不能由预算差额推断可用现金。**本日不给已有仓位机械止盈或自动加仓指令；后续按时间分批的金额与总股票上限仍需你明确采用。** 新主题和个股共用同一股票预算，已有Google与科技指数重叠时尤其需要约束。

[固定在线观察台](https://nolan-market-watch.choice-calf-0415.chatgpt.site/)继续提供一／二／三年联动收益、波动、最大回撤与固定MA50／200。历史已改按**已完成美股交易日**归档，周末／休市不新增重复日档；本篇为私人的北京时间日报，包含持仓参考，不上传公开站点。

{watch}

![近60交易日价格与当时可见回撤](./watchlist_curves.png)

**Google估值结果**

11/2GOOG278.04（−0.06%）、GOOGL278.99（−0.30%）。新债券文件是新增融资事实，未产生新的经营季度，不能把发行额当FCF。承销折价后、其他费用前募集现金约59.755075亿欧元；原文没有明确全部偿债比例，交割后净现金／净债务与用途需同时更新，不能只增现金不增债务或重复扣融资成本。

本次推进了旧模型的TPU营运资金问题：官方递延收入可包含“已收或已到期应收”，不能把全公司合同负债都当TPU实收预付款。归一化硬件现金周期算例显示，预付款与库存／回款天数足以显著改变占款；它是研究假设，不是新业绩预测或新合理股价。完整Q3 10-Q已读，不再称尚未公布。没有把旧三情景68.25／216.28／402.11美元恢复为买价，也未声称现价已低估。[新融资、票息算术与TPU情景](./company_research.md) · [原资本桥](../2026-10-30/google_update/google_update.md)

**SOFI研究观察**

SOFI16.60（−0.95%）。以2027管理层调整EPS0.90的未来展望作简单参照约**{m['SOFI']['close']/0.9:.2f}倍**，不是TTM已实现GAAP盈利估值，更非完整低估结论。此次SEC recent仍未见新Q3完整10-Q，业绩8-K已于10/27发布；继续核贷款销售与留存、公允价值、逾期核销、资金成本、监管资本及稀释。银行存款是经营资金，不能套用工业公司净现金DCF。[实际读取范围](./company_research.md) · [此前资本回报检验](../2026-10-30/sofi_research.md)

**机器人供应链筛选**

RRX160.93（+2.35%）、CGNX56.41（+0.46%）、ATS18.97（+3.15%）保持研究候选。RRX **11/3美东盘前发稿、北京23:00电话会**；CGNX **11/4美东盘后发稿、11/5北京21:30电话会**。当前没有新Q3实际利润与回款，不因单日相对强势认定低估。旧RRX摊销恢复／17倍EPS情景仍只是条件模型，新增订单必须核交付、现金转化和去杠杆；ATS此次未深读新披露，明确保留估值缺口。[官方日历及研究边界](./company_research.md)

BRK.B收556.11、+2.51%，两源均显示新高，但精确盘中高点不同。所读IR／SEC目录未核到11/2新增Q3经营公告，不能把上涨归因于财报、回购或保险改善；单一公司仍需独立估值，不套用ETF首次仓位比例。

MRNA220.83（−0.40%），11/6北京21:00电话会关注现金消耗与商业化；临床、审批、商业收入和盈利分开。历史8/19极端跳变价格曾核对，原因未查清，不把高历史收益作为预期回报。本次没有新“已低估”入选股票。

**行业观察**

11行业ETF **8涨3跌**，SMH另列；这种分化只反映行业ETF价格，不等于个股全市场广度或资金净流入。

- **科技XLK−2.95%、半导体SMH−2.71%**：与你现有成长敞口最相关，QQQM只略高于MA200，继续保持追加纪律；SOXX与SMH不是两份独立分散。
- **可选消费XLY+2.41%、金融XLF+1.86%、工业XLI+1.38%**：表现比科技强，不能从单日轮动直接得出应卖科技买这些行业。
- **能源XLE−3.96%**：当日拖累较大，商品价格／供需与估值需另核，不能把全日跌幅简单归因于某条早盘新闻。

![11行业ETF与半导体单日涨跌](./sector_daily.png)

{st}

**🔎 Reddit 投资与信息差观察**

本次**没有日期核验通过、可新增报道的原帖**。六社区RSS403，可读New／Top仍有旧缓存；这是过去24小时扫描的覆盖缺口，不能说“Reddit没有新讨论”，不据零条结果确认市场一致看法。没有编造多空共识、热度或“市场未定价”的机会，不推进成功扫描游标。[实际来源与读取时间](./reddit_sources.json) · [筛选说明](./reddit_digest.md)

FiNews首页本次仍是10/30、UTC22:10:49更新，未读到11/2新日报；不把旧Meta展望／Okta维护事件当今日新信息，也不拿聚合行情作独立交叉核验。[FiNews实际范围](./finews_digest.md)

**距观察档还有多远**

{levels}
QQQM离13%接近区间差**2.30个百分点**，从当前价到15%观察价266.99需约**−4.81%**；两种百分比含义不同。VOO回撤3.78%，亦未接近。今日没有新13%／15%／23%／25%档提醒，15%和25%仍是评估条件，不是确定买点。

BRK.B本次高点Yahoo557.41、StockAnalysis557.59，较前值都更高，但精确高点再次不一致。曲线和表格沿Yahoo统一序列，**BRK.B持久提醒仍保留10/29最后有效状态**；只把本次尝试写入deferred_checks。QQQM／VOO有新有效收盘可推进至11/2。QQQM高点314.11与第二源314.12差一美分，观察价分别266.99／267.00，披露而不制造重复提醒。[当前交叉核验](./quote_verification.json)

**利率与未来一周事件**

VIX日线**21.15、+8.91%**，为统一提供方常规日线，尚未完成同步官方逐笔核定。财政部11/2参考曲线**2年4.59%、10年4.91%**，较10/30分别+3／−3基点，不是可直接成交收益率。

ISM官方10月制造业PMI **55.5**，生产59.0、新订单55.5；价格指数75.2，虽较前月下降，仍表示价格上涨。它不是CPI，也不能单凭一项调查推导已衰退或日内股价因果。本周关键是**11/3 23:00 JOLTS、11/6 21:30非农**；11/5生产率21:30。AMD11/3美东盘后、北京11/4 06:00电话会；Google债券11/5预计交割；Moderna11/6北京21:00电话会。本周无FOMC，CPI为11/10北京21:30，不错放到本周。[官方宏观日历与收益率](./macro_research.md) · [公司事件](./company_research.md)

**完整表现与趋势数据**

{tr}

{ix}

**口径、核验和缺口**

- 新取11/2完整日线共33项；18个股票／ETF常规收盘均与带日期的StockAnalysis历史表核对一致。它是第三方核验，可能与Yahoo共享上游，未称交易所逐笔审计。BRK精确高点保留缺口，QQQM／VOO高点日期已本次重读。
- 60个连续交易日收盘为8/10—11/2，共59个价格间隔；逐日滚动高点仅用当时可见364日盘中high，不使用今天高点回填。图为价格表现、不含分红；SGOV的当日价格与含分配近似分开。MA50／200使用拆股调整Close，量比为当天量／此前20日均量。DRAM148条历史，无MA200／完整52周；SOXX后续拆股需统一序列。
- 时段采集UTC11/2 23:31:35，即北京11/3 07:31:35、美国18:31:35EST。11/2盘后仍在进行，所有最新分钟为零量，不确认真实新成交；有17项第二来源带明确时刻参考，时刻不同的差异不隐去，不更新收盘提醒。11/3盘前尚未开始。[详细时刻与差异](./extended_detail.md) · [时段来源](./extended_verification.json)
- Google融资是新事实，TPU现金周期是基于已发布10-Q的研究算例；未重算新合理股价。SOFI完整信用资料、候选完整估值、指数盈利估值分母与穿透持仓权重仍缺；因此不把低表面PE或大回撤升级为低估。
- Reddit覆盖受限与无新增已核线索分别说明。持仓数量核验仍为10/30，不自动访问券商／执行交易。QQQ已从当前清单移除，不重新引入。两张PNG已打开核对日期、正负号与末值，HTML沿用模板做资源和关键数字检查，不重复宣称实机版式验收。

[日线完整数据](./metrics.json) · [来源清单](./manifest.json) · [最终核验](./verification.json) · [分类表](./watchlist_table.json)
'''
(P/'report.md').write_text(report)
print('Report generated',len(report),'chars; portfolio reference',round(market,2))
