from pathlib import Path
from datetime import datetime,timezone
import json
P=Path(__file__).resolve().parent
m={x['symbol']:x for x in json.loads((P/'metrics.json').read_text())}
WATCH=['QQQ','QQQM','VOO','BRK-B']
sectors={'XLK':'科技','XLC':'通信服务','XLY':'可选消费','XLP':'必需消费','XLV':'医疗','XLF':'金融','XLI':'工业','XLE':'能源','XLU':'公用事业','XLB':'原材料','XLRE':'房地产','SMH':'半导体'}
def table(head,rows):return '| '+' | '.join(head)+' |\n| '+' | '.join(['---']*len(head))+' |\n'+''.join('| '+' | '.join(map(str,row))+' |\n' for row in rows)
def fmt(x):return f'{x:,.2f}'
def pct(x):return f'{x:+.2f}%'
watch=table(['标的','常规收盘（美元）','当日','距52周高点回撤','15%观察价','25%观察价'],[[m[s]['label'],fmt(m[s]['close']),pct(m[s]['day_pct']),f"{-m[s]['drawdown_pct']:.2f}%",fmt(m[s]['level_15']),fmt(m[s]['level_25'])] for s in WATCH])
levels=table(['标的','52周盘中高点（美元）','高点日期','距15%还差（百分点）','当前价到15%档所需变动','阶段'],[[m[s]['label'],fmt(m[s]['high_52w']),m[s]['high_date'],f"{15+m[s]['drawdown_pct']:.2f}",pct(m[s]['additional_drop_to_15_pct']),'回撤不足13%'] for s in WATCH])
trend=table(['标的','当日','近5交易日','近21交易日','50日均线（美元）','200日均线（美元）','当日/前20日均量'],[[m[s]['label'],pct(m[s]['day_pct']),pct(m[s]['five_session_pct']),pct(m[s]['twenty_one_session_pct']),fmt(m[s]['ma50']),fmt(m[s]['ma200']),f"{m[s]['volume_vs_prior20']:.2f}倍"] for s in WATCH+['GOOGL']])
index=table(['指数','收盘（点）','当日','近5交易日','近21交易日','52周高点/日期','距高点回撤'],[[m[s]['label'],fmt(m[s]['close']),pct(m[s]['day_pct']),pct(m[s]['five_session_pct']),pct(m[s]['twenty_one_session_pct']),f"{fmt(m[s]['high_52w'])} / {m[s]['high_date']}",f"{-m[s]['drawdown_pct']:.2f}%"] for s in ['^GSPC','^IXIC','^NDX']])
sector_table=table(['行业/ETF','当日','近5交易日','近21交易日','当日相对VOO（百分点）','近21日相对VOO（百分点）'],[[f'{sectors[s]} {s}',pct(m[s]['day_pct']),pct(m[s]['five_session_pct']),pct(m[s]['twenty_one_session_pct']),f"{m[s]['day_pct']-m['VOO']['day_pct']:+.2f}",f"{m[s]['twenty_one_session_pct']-m['VOO']['twenty_one_session_pct']:+.2f}"] for s in sorted(sectors,key=lambda s:m[s]['day_pct'],reverse=True)])
google_url='https://www.sec.gov/Archives/edgar/data/1652044/000165204426000080/googexhibit991q32026.htm'
msft='https://www.microsoft.com/en-us/Investor/earnings/FY-2027-Q1/press-release-webcast'
rrx='https://investors.regalrexnord.com/investors/ir-news/press-release-details/2026/REGAL-REXNORD-REPORTS-SECOND-QUARTER-2026-FINANCIAL-RESULTS/default.aspx'
text=f'''# 美股观察｜2026-10-29 北京时间

采用 **2026-10-28（周三）美股常规收盘**，对应北京时间10月29日04:00。股票/ETF单位为美元，指数为点。该日正常交易，下一交易日为美东10月29日，北京时间今晚21:30开盘。[NYSE交易日历](https://www.nyse.com/trade/hours-calendars)

⏳ **今日判断：QQQM准备首笔，先看今晚PCE与财报后首个完整交易日；Google暂缓，机器人候选继续估值核验。** 标普500 +0.28%，纳斯达克综合 +0.27%，纳斯达克100 +0.55%。四个原观察标的均未进入13%的接近区间，没有新的跨档提醒。你已说明期限3–5年、希望控制回撤，仍未确认持仓与预算。

⚠️ Google、微软财报均在上述收盘后公布，今天的收盘表尚未完整反映新财报。本日报将经营事件单列，盘后快照不混入曲线、阈值或常规收盘涨跌。

**今天对你最重要的事**

1. **Google：经营增长成立，现金回报仍需等待，昨天的入场档暂停沿用。** Q3营业利润同比约+30%，但自由现金流 **−90.65亿美元**，当季普通股净融资 **123.71亿美元**、回购为零。对你来说，关键是未来3–5年每股现金回报能否覆盖今天的价格；仅凭财报后下跌不足以认定低估。下一步先补三季度投资资产、债务与租赁的资本桥，再给新研究价格；最强反证是云增长持续转成高现金回报。[Alphabet原始财报]({google_url}) · [本次财报与模型检查](./google_update/google_update.md)
2. **QQQM：不用一直等跌15%，但今天不适合因反弹加速。** 收盘298.71，50日线298.70，只高约0.003%；这点差距不构成有效突破证据。微软Azure同比+48%，而经营现金流减现金固定资产支出的FCF同比约−27.4%，说明增长与股东现金回报可能分化。今晚20:30的GDP/PCE及10/29完整交易日将提供一次有限的事件复核；**10/30晨报必须按结果更新首笔判断**，不自动把等待顺延到下一场财报。[微软原披露]({msft}) · [BEA日历](https://www.bea.gov/news/schedule)
3. **机器人供应链：RRX的便宜程度高度依赖盈利调整。** 161.09的收盘只比昨日主观165.07基准低2.41%。恢复部分收购摊销成本后，参考价值会明显降低，现价缺少充分安全边际；11/3季报重点看现金转化与负债。最强反证是收购摊销高于实际经济损耗、增长和去杠杆继续兑现。今天没有新增已低估股票。[RRX价格](https://stockanalysis.com/stocks/rrx/history/) · [公司调整表]({rrx}) · [本次压力检查](./robotics_update.md)

**Google估值结果**

GOOGL常规收盘 **324.89（+1.34%）**，距52周盘中高点408.61（5/18）回撤20.49%；50/200日均线341.51/341.20。价格低于高点和均线只说明位置，不能证明低估。[报价核验](https://stockanalysis.com/stocks/googl/history/)

Q3 Search收入633.50亿美元、同比约+12%；Cloud收入307.09亿美元、同比约+103%，分部利润111.21亿美元。Cloud包含TPU系统销售，分部利润也未承担全部集团AI研发费用。经营现金流422.90亿美元，小于现金资本开支513.55亿美元。GAAP EPS2.12含股权投资损失影响约0.55美元；两者相加仅剔除单项，不叫公司全面调整EPS，也不假定可直接与分析师预期比较。[财报、分部与现金流原表]({google_url})

本次已把TTM收入/营业利润更新到4711.01/1569.76亿美元，9月底实际普通股数更新到122.94亿股。保留六月资本桥的隔离变量检查约为基准217美元，**它只是部分敏感性，不能当新合理价**。完整Q3证券分拆、租赁和索偿仍待核验，因此旧180–195及后续档暂停机械沿用；今天不发布新的精确买入区间。[部分模型输入](./google_update/google_model_inputs_partial.json) · [可复算敏感性](./google_update/google_operating_sensitivity.json)

**主观察表**

{watch}
收盘由本次Yahoo日线与Stock Analysis的[QQQ](https://stockanalysis.com/etf/qqq/history/)、[QQQM](https://stockanalysis.com/etf/qqqm/history/)、[VOO](https://stockanalysis.com/etf/voo/history/)、[BRK.B](https://stockanalysis.com/stocks/brk.b/history/)交叉一致。高点与观察档各用自身序列；本次高点均未变，QQQM跨源一美分差异继续保留披露。Google不纳入这四个标的的提醒合同。

![近60个交易日走势与逐日滚动回撤]({P}/watchlist_curves.png)

**行业观察**

11个行业ETF为 **6涨5跌**，SMH另列；这是ETF层面广度，不能代替全部成分股统计。

- **SMH +1.74%、XLK +0.80%**：半导体继续领涨，但近21交易日SMH仍−6.46%、XLK−1.80%。修复尚不足以证明便宜；财报后需重新核对盈利与投入。
- **通信XLC −0.42%，近21日−7.47%**：它包含互联网平台风险，价格弱于指数；Google盘后新披露尚未反映在这组常规收盘中，不能据此推断市场已经消化结果。
- **公用事业XLU −0.84%**：当日最弱，近21日仍+7.00%。电力需求与买入估值是两项判断，行业名称也不提供回撤保证。
- **能源XLE +0.35%，近21日+11.23%**：有相对强势，但不是机器人或AI供应链价值的替代证明。价格变化不等于资金净流入。

上述来自同一Yahoo日线，各行业完整相对比较见折叠指标表。[行情来源清单](./manifest.json)

![行业当日涨跌排行]({P}/sector_daily.png)

**🔎 Reddit 投资与信息差观察**

本次只保留 **两条扩展日期研究更新**，未认证最新24小时全覆盖；列表缓存陈旧，RSS被网络策略阻止，精确发帖北京时间缺失。这与没有新讨论是不同情况。

1. **微软｜已核验财报事实＋待检验观点。** 10/26的[r/MSFT研究帖](https://www.reddit.com/r/MSFT/comments/1xg87kw/microsoft_msft_monetizing_massive_ai_investments/)在10/28新财报后有了可核实分母：现金FCF186.33亿美元，同比−27.4%。最强反证是投入产能未来产生较高现金回报，单季受营运资本影响；融资租赁全口径仍待核。本次未读到实质评论，不归纳社区共识。[官方现金流表]({msft})
2. **买入倍数｜待核验观点与情景检查。** 10/27的[r/stocks Costco讨论](https://www.reddit.com/r/stocks/comments/1xgfw9k/costco_valuation_how_much_eps_growth_offsets_a/)提醒：假设50倍入场、盈利年增12%、5年后28倍退出，年化价格回报约−0.3%（不含股息税费）。倍数不是当前报价或目标价，反方认为商业质量可能支持高倍数。对你有用的是把退出估值压力检查用于Google/RRX，COST未因此进入机会池。

FiNews实际最新页为10/28、更新北京时间10/29 **06:08:46**，读取16条新闻外链及摘要；受限的CNBC原文未绕过，关键公司事实回查官方。Oracle未来营收与FCF是管理层目标，融资上限还排除再融资，未据此新增低估候选。[FiNews最新页](https://finews.fyi/) · [FiNews核验](./finews_digest.md) · [Reddit完整反证与范围](./reddit_digest.md) · [Reddit来源](./reddit_sources.json) · [FiNews来源](./finews_sources.json)

**机器人供应链筛选**

今天深入RRX，CGNX、ATS继续作为有条件研究候选，未把昨日价格冒充今日行情；也没有因为机器人题材认定整个行业低估。

RRX的9.71美元参考EPS剔除了0.57退税并恢复0.32股权薪酬，但仍全额加回3.92的收购摊销。保持主观17倍，若假设恢复25%/50%摊销为经济成本，参考值分别为 **148.41/131.75**，低于161.09现价；这不证明恢复比例正确，说明低估结论依赖哪些成本假设。昨日115.50保守情景相对现价仍有约28.3%下行。产品关系成立，人形机器人单独收入/订单占比尚缺，不能把整个运动控制分部当人形机器人收入。[RRX Q2原披露]({rrx}) · [压力情景、反证与日历](./robotics_update.md)

RRX报价只有Stock Analysis明确标注常规收盘；另一报价接口虽同价但时点/涨跌分母不同，未认作独立收盘核验通过。本次不以它触发价格提醒。[来源与算式](./robotics_sources.json)

**对你当前状态的建议**

**QQQM：准备首笔，有限等待一次事件后复核；Google：暂缓；RRX：等待新季报与价值余量。** 不需要把跌15%作为首次入场必要条件。当前首笔10%、随后每月5%、股票40%/防守60%仍是[未确认草案](../2026-10-27/staged_entry_plan_draft.md)，没有视为你已批准或已执行。

今晚GDP/PCE后，先看10/29常规交易日如何吸收Google、微软财报。若没有出现新增盈利恶化、融资风险扩散和广度明显收窄，可在原拟定股票总预算内重新评估小额时间分批；若出现这些反证，则具体说明哪项风险上升及复核条件。10/30日报给结果判断，避免只因为又有下一场财报就持续延期。均线和量能是辅证，不新增机械阈值；分批只能分散买入时点，股票总比例才是控制组合回撤的主要工具。

QQQM仍需约下跌10.62%才到266.99的15%观察价，按时间准备首笔与这档提醒可并行。VOO高于50日线705.82约0.58%，QQQM仅略高于50日线；QQQ/QQQM/VOO量能约为前20日的0.79/0.80/0.83倍，跨源成交量差异使结论更谨慎。最强反证是盈利继续超预期、指数持续上涨，等待本身也有机会成本；不把反弹或均线一美分变化当确认。

单独买Google，会与QQQM/VOO内的Alphabet间接暴露叠加；本次未核验持仓生效日与精确权重，故不报实时占比。个股预算应从股票总预算内划分。BRK.B本日−0.49%，所读[公司公告目录](https://www.berkshirehathaway.com/news/2026news.html)没有新的10/28披露，不能据价格归因于回购或保险损失，也不等于完整SEC扫描。

**距观察档还有多远**

{levels}
回撤差值用百分点，当前价到目标价用百分比，两者不能混用。原四标的阶段均未改变；高点变化将更新观察价，触发观察档也不能证明见底。

**利率与未来一周事件**

美联储10/28以10–2票维持 **3.75%–4.00%**，两位异议者希望加息25基点。维持利率不能直接解读成降息转向；对3–5年资金，折现率和现金回报要求仍重要。[FOMC原声明](https://www.federalreserve.gov/newsevents/pressreleases/monetary20261028a.htm)

财政部10/28平价曲线：**2年4.67%（−3基点）、10年5.05%（+6基点）**。它们是参考曲线，不能当作嘉信可成交报价。[财政部原表](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value=2026) · [本次提取行](./treasury_rows.json)

VIX为 **16.91**，较前值−0.61（−3.48%）；Cboe标注截至10/28，未假定与股票16:00逐秒同步。[Cboe](https://www.cboe.com/tradable-products/vix/)

| 事件 | 美国时间 | 北京时间 | 对你要核查的条件 |
| --- | --- | --- | --- |
| Google Q3 / 微软FY27 Q1 | 10/28盘后，已公布 | 10/29凌晨，已公布 | 按实际现金流、融资与盈利更新，不再写成待公布 |
| GDP Q3初值、9月PCE | 10/29 08:30 EDT | **10/29 20:30** | 通胀与增长是否抬高利率/盈利风险 |
| 亚马逊Q3电话会 | 10/29 17:00 EDT | **10/30 05:00** | AWS利润、资本投入与现金转化 |
| Q3雇佣成本指数 | 10/30 08:30 EDT | **10/30 20:30** | 工资成本压力 |
| RRX Q3发布 / 电话会 | 11/3盘前 / 10:00 EST | 11/3晚间盘前 / **23:00** | 非一次性盈利、FCF、去杠杆 |
| 9月JOLTS | 11/3 10:00 EST | **11/3 23:00** | 职位空缺与用工需求 |
| CGNX Q3发布 / 电话会 | 11/4盘后 / 11/5 08:30 EST | 11/5凌晨 / **11/5 21:30** | RealSense支出、留任与稀释 |

日历来源：[BEA](https://www.bea.gov/news/schedule)、[BLS 10月](https://www.bls.gov/schedule/2026/10_sched.htm) / [11月](https://www.bls.gov/schedule/2026/11_sched.htm)、[亚马逊](https://www.aboutamazon.com/news/company-news/amazon-earnings-q3-2026-report)、[RRX公告](https://investors.regalrexnord.com/investors/ir-news/press-release-details/2026/Regal-Rexnord-Corporation-to-Host-Third-Quarter-2026-Earnings-Conference-Call-on-Tuesday-November-3rd-2026/default.aspx)、[Cognex公告](https://investor.cognex.com/news/news-details/2026/Cognex-Announces-Third-Quarter-2026-Earnings-Release-and-Conference-Call-Dates/default.aspx)。11/1起美国冬令时，已调整时差。未来一周没有月度CPI或非农：下一次非农11/6、CPI11/10；苹果日期未取得官方明确明细，未补猜。

SGOV官网最新可读为 **10/27的30日SEC年化收益率3.78%**。是扣基金费用、个人税前的可变收入参考，不能当总回报或承诺年收益；仍仅为暂存候选。[iShares](https://www.ishares.com/us/products/314116/ishares-0-3-month-treasury-bond-etf)

**完整表现与趋势数据**

{trend}
{index}
指数最新收盘与[AP当日摘要](https://apnews.com/article/7864eac2e13db75f07758ed9c39ad96b)、[纳斯达克100历史表](https://ca.investing.com/indices/nq-100-historical-data)分别核对。纳斯达克综合仅作环境参考，QQQ/QQQM跟踪纳斯达克100。

{sector_table}

**口径、核验和缺口**

- 价格为Yahoo拆股一致OHLC收盘，不计现金分红再投资。5/21交易日对应周/月观察；60个收盘观测点覆盖8/5–10/28，跨59个价格间隔。归一化最新QQQM101.137628、VOO100.325049、BRK.B104.141862。各历史点回撤以当日之前364日盘中最高价计算，重算180个点通过，无未来高点回填。
- 52周窗口是(当日−364日, 当日]，50/200日均线同一价格序列，量比以此前20日均量、不含当日。高点展示到美分后按十进制四舍五入观察价；回撤仍用原精度。QQQM另一来源314.12与Yahoo314.11差一美分，15%价分别267.00/266.99，不据此重复触发。
- 五个收盘跨源一致，成交量有差异：QQQ约−4.36%、QQQM−1.30%、VOO−0.05%、BRK.B−0.06%、GOOGL−12.90%（Yahoo相对第二来源）。尤其Google量比仅供低置信度参考，不写成放量确认。指数估值分母、全成分股广度、Google完整Q3资本桥与官方电话会仍缺，结论相应降低强度。
- Reddit精确发帖时间与新鲜度覆盖不足、FiNews部分外链受限已在各自记录说明。图像已打开检查，中文、日期、正负号和末值可读。HTML沿用模板，未公开托管，不操作账户或自动交易。

[指标及来源](./metrics.json) · [原始行情文件清单](./manifest.json) · [数值与图像验证](./verification.json) · [宏观来源与读取状态](./market_context.json) · [Google证据](./google_update/google_sources.json) · [机器人证据](./robotics_sources.json)
'''
(P/'report.md').write_text(text)
context={'report_date_beijing':'2026-10-29','session':'2026-10-28','updated_at_utc':datetime.now(timezone.utc).isoformat(),'calendar_check':{'source':'https://www.nyse.com/trade/hours-calendars','read_via':'web','session_open':True,'next_session':'2026-10-29'},'fed':{'publication_date':'2026-10-28','target_pct':[3.75,4.0],'vote':'10-2','dissent':'preferred raise25bp','source':'https://www.federalreserve.gov/newsevents/pressreleases/monetary20261028a.htm'},'treasury':{'session':'2026-10-28','two_year_pct':4.67,'ten_year_pct':5.05,'two_year_change_bp':-3,'ten_year_change_bp':6,'raw_rows':'treasury_rows.json'},'vix':{'asof_date':'2026-10-28','value':16.91,'change':-.61,'source':'https://www.cboe.com/tradable-products/vix/'},'sgov':{'yield_date':'2026-10-27','yield_30_day_sec_pct':3.78,'basis':'after fund fees before investor tax; annualized income reference, not total return','source':'https://www.ishares.com/us/products/314116/ishares-0-3-month-treasury-bond-etf'},'primary_calendar_sources':['https://www.bea.gov/news/schedule','https://www.bls.gov/schedule/2026/10_sched.htm','https://www.bls.gov/schedule/2026/11_sched.htm','https://www.aboutamazon.com/news/company-news/amazon-earnings-q3-2026-report'],'read_failures_and_web_fallbacks':'context_source_manifest.json','news_cutoff':'2026-10-28T23:35:00Z','not_traded':True}
(P/'market_context.json').write_text(json.dumps(context,ensure_ascii=False,indent=2)+'\n')
# Avoid promising a separate after-hours quote when the main report excludes it.
gp=P/'google_update/google_update.md';s=gp.read_text().replace('盘后价格由主线程另列时间和来源，不替换收盘表。','本次主行情表不纳入盘后快照，不替换常规收盘。');gp.write_text(s)
print('report.md and market_context.json written',len(text))
