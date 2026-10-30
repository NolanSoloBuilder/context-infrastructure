from pathlib import Path
from datetime import datetime,timezone
import json
P=Path(__file__).resolve().parent
sources=[
 {'id':'note','url':'https://xhslink.cn/o/8KgDdPGJA8R','kind':'original_social_post','read_scope':'Public HTML embedded body/title/date plus sole attached cover; comments not read','published_beijing':'2026-07-04T18:21:25+08:00','read_date_beijing':'2026-10-30','status':'read_and_archived'},
 {'id':'FDA_devices','url':'https://www.fda.gov/medical-devices/artificial-intelligence-enabled-medical-devices/list-artificial-intelligence-enabled-medical-devices','kind':'primary_regulator','read_scope':'List scope/limits, premarket authorization and recent entries','finding':'AI-enabled medical devices already marketed; list is not comprehensive and not a commercial-revenue/profit ranking'},
 {'id':'FDA_EMA','url':'https://content.govdelivery.com/accounts/USFDA/bulletins/4045c84','kind':'primary_regulator','publication_date':'2026-01-14','read_scope':'Joint release of10 guiding principles','finding':'Supports evidence standards and development potential, not universal approval relaxation or guaranteed profitability'},
 {'id':'CMS_prices','url':'https://www.cms.gov/newsroom/fact-sheets/medicare-drug-price-negotiation-program-negotiated-prices-initial-price-applicability-year-2026','kind':'primary_payor_regulator','read_scope':'First10PartDselected drugs and effective date','finding':'Negotiated prices effectiveJan1,2026; policy clarity is not equivalent to favorable manufacturer margins'},
 {'id':'ISRG','url':'https://isrg.intuitive.com/news-releases/news-release-details/intuitive-announces-third-quarter-earnings-6','kind':'primary_company_release','publication_date':'2026-10-20','quarter':'2026Q3','read_scope':'Revenue/procedures/consumables/GAAP and adjusted profit/litigation','facts':{'revenue_USD_B':3.05,'revenue_yoy_pct':22,'daVinci_procedure_yoy_pct':14,'instruments_accessories_revenue_USD_B':1.80,'GAAP_net_income_USD_M':523,'GAAP_EPS_USD':1.49,'adjusted_EPS_USD':3.00,'litigation_pretax_expense_USD_M':450},'limits':'Robotic-assisted procedures are not automatically autonomous AI surgery; no current valuation completed'},
 {'id':'TEM','url':'https://www.tempus.com/news/pr/tempus-reports-second-quarter-2026-results/','kind':'primary_company_release','publication_date':'2026-07-30','quarter':'2026Q2','read_scope':'Segment revenue, GAAP profit and equity gains, acquisition/guidance limits','facts':{'revenue_USD_M':382.5,'diagnostics_revenue_USD_M':289.3,'data_applications_revenue_USD_M':93.2,'GAAP_net_income_USD_M':5.6,'unrealized_market_security_gains_USD_M':98.5,'SBC_and_related_payroll_tax_USD_M':55.6},'limits':'Do not call all revenue AI software or subtract pretax equity gain from net income as a fully normalized after-tax profit'},
 {'id':'NTRA','url':'https://investor.natera.com/news/news-details/2026/Natera-Reports-Second-Quarter-2026-Financial-Results/default.aspx','kind':'primary_company_release','quarter':'2026Q2','read_scope':'Test-volume andSignatera/MRDcommercial/coverage discussions','finding':'Illustrative MRD operator; not an original article pick and not all revenue attributable toAI'},
 {'id':'XLV','url':'https://stockanalysis.com/etf/xlv/history/','kind':'third_party_cross_check','session':'2026-10-29','read_scope':'Dated daily table and prior21session close','facts':{'close_USD':184.04,'day_pct':2.40,'Sept30_close':168.42,'Oct29_intraday_high':184.80},'local_calculation_source':'../metrics.json andraw/XLV.json','local_yahoo_high_52w':184.83,'local_yahoo_high_date':'2026-10-29','high_difference_USD':.03,'notes':'Keep Yahoo rolling52week source consistent; disclosure rather than treating high differences as signals'}
]
claims=[{'claim':'AI医疗可产生真实产品与商业价值','status':'direction_supported_but_company_economics_separate','sources':['FDA_devices','FDA_EMA','ISRG','TEM']},{'claim':'医疗是华尔街确定的下一轮主线','status':'unverified_market_forecast','reason':'No falsifiable timing, flows or positioning evidence'}, {'claim':'机构已在低位吸筹','status':'unverified','reason':'Article supplies no primary positions/flows; currentXLVnearhigh does not establish every constituent valuation'}, {'claim':'2026FDA环境支持整个医疗板块','status':'partially_supported_narrow_AI_guidance_only','sources':['FDA_EMA'],'reason':'Technical evidence guidance does not quantify overall approval rates or company profits'},{'claim':'药价改革清晰所以医疗利润改善','status':'not_established','sources':['CMS_prices'],'reason':'Negotiated prices may improve access while constraining manufacturer revenue; effects differ by business'}, {'claim':'M&A活动回升','status':'not_verified_in_this_review','reason':'Article gives no comparable deal count/value/time window; no inference of premiums for all stocks'}]
(P/'claims_sources.json').write_text(json.dumps({'checked_at_utc':datetime.now(timezone.utc).isoformat(),'sources':sources,'claim_checks':claims,'scope':'article interpretation and initial primary checks; not full sector or company valuations','portfolio_action':'none; no watchlist or automation changes'},ensure_ascii=False,indent=2)+'\n')
text='''# AI医疗文章：内容与投资判断｜2026-10-30

**方向值得研究，但文章没有证明医疗会成为下一轮主线，也没有证明现价低估。** 对你3万美元、3–5年、约20%暂时亏损承受度，我会优先研究已经有收入、回款和盈利基础的医疗应用，再看AI带来的增量，谨慎对待只靠研发里程碑和融资维持的题材公司。

已实际读到Azzurro的[原分享](https://xhslink.cn/o/8KgDdPGJA8R)全文与唯一封面图。原帖发布时间为**北京时间2026年7月4日18:21**，不是10月底新事件。封面仅提出主题；正文没有推荐医疗股票清单，提到莫德纳、Zoom是历史主题交易例子。未读取评论。[读取记录](./source_summary.md)

**原文在说什么**

作者认为，AI基础设施之后可能轮到行业应用，医疗中的研发、诊断、手术与运营存在效率改善空间；再叠加行业此前受压和政策/并购变化，可能形成新的交易叙事。这个推理适合产生研究问题，缺少公司估值、资金持仓和兑现时间证据。

**哪些部分有依据**

FDA已有AI医疗器械市场授权清单，说明产品落地已在发生；FDA和EMA也于1月发布药物开发AI良好实践原则。但器械授权、研发证据标准、医院采购、保险支付和公司盈利是不同环节。不能把一项技术进展直接当作全行业利润改善。[FDA器械清单与范围](https://www.fda.gov/medical-devices/artificial-intelligence-enabled-medical-devices/list-artificial-intelligence-enabled-medical-devices) · [FDA／EMA原则](https://content.govdelivery.com/accounts/USFDA/bulletins/4045c84)

我会按现金兑现过程区分：

| 方向 | 需要验证的商业问题 | 对你更重要的风险 |
|---|---|---|
| 医院流程、影像辅助、医疗数据 | 谁付费，是否真正节省医生时间，合同续费和利润是否改善 | 节省的价值可能被医院/支付方拿走，软件未必有定价权 |
| 基因检测、早筛、MRD监测 | 检测量、回款单价、保险覆盖、单次毛利和临床使用范围 | 检测量上升不等于回款或利润同比上升；也不等于纯AI收入 |
| 手术机器人 | 装机后实际手术量、耗材与服务收入、医院资本预算 | 商业成熟度与估值分开；机器人辅助不等于AI自主手术 |
| AI药物发现与研发 | 已签合作的现金付款、临床里程碑、现金消耗和稀释 | 技术提高筛选效率后，药物仍有试验失败、监管及商业化风险 |

这张表是我的研究框架，不是对任何产品临床效果的诊断，也不是已完成的行业估值排序。

**文章跳过的三个问题**

**第一，7月的“低位”不能直接用于10月底。** 最新完成交易日10/29，医疗ETF XLV收184.04、当日+2.40%；相对9/30的168.42，21个交易日价格表现约+9.27%。本次统一Yahoo序列的52周盘中高点184.83，最新收盘距它仅约0.43%。这不能证明医疗已经昂贵，也不能代表所有biotech；它足以提醒我们，不能用旧文章一句行业受压就认定现在是低位。[第二来源历史表](https://stockanalysis.com/etf/xlv/history/)

第二来源当日高点184.80与Yahoo184.83相差0.03，本文保留口径差异。没有按几美分差别生成交易信号，价格曲线也不能替代盈利估值。

**第二，政策清晰不自动增加药企利润。** CMS首批10种药谈判价格从2026年1月1日起生效。对患者支出、治疗可及性和药企利润可能有不同影响，不能把医保、药价变化统称为医疗股利好。[CMS原文](https://www.cms.gov/newsroom/fact-sheets/medicare-drug-price-negotiation-program-negotiated-prices-initial-price-applicability-year-2026)

**第三，资金叙事与公司价值需要分别验证。** 原文没有机构持仓/净流入证据，也没有提供M&A宗数、金额和可比区间。因此本次没有确认“机构正在吸筹”“下一轮主线”或“并购会抬升所有相关股票”。这些是待检验的市场判断，不据此给出入场价。

**用实际公司检验：以下是我补充的样本**

这些公司并非原文推荐，尚未完成当前价格估值或建议购买。

| 公司 | 能核验的经营事实 | 尚不能推出什么 |
|---|---|---|
| Intuitive Surgical（ISRG） | 10/20公布Q3收入30.5亿美元、同比+22%，da Vinci手术量+14%，器械耗材收入18亿美元 | 手术机器人商业化已成立，但增长不能全部归因AI，当前股价未核算是否便宜 |
| Tempus AI（TEM） | 已读取Q2收入3.825亿美元，诊断2.893亿、数据与应用0.932亿 | 公司总收入不等于AI软件收入；业务增长与可持续盈利需分开 |
| Natera（NTRA） | 原Q2披露可研究Signatera/MRD检测业务的增长、临床与支付进展 | MRD需求增长不等于全部收入来自AI，也不等于利润和估值已合适 |

ISRG有已兑现的手术与耗材商业模式，我会优先研究它的盈利质量与估值；同时Q3 GAAP EPS1.49与调整EPS3.00差距很大，其中有4.5亿美元税前诉讼费用，也有股权薪酬等调整。不能随便选最便宜的表面PE分母。[ISRG原始Q3](https://isrg.intuitive.com/news-releases/news-release-details/intuitive-announces-third-quarter-earnings-6)

TEM尤其值得警惕表面盈利：Q2 GAAP净利润560万美元，但包含9850万美元证券未实现收益。两项税前/税后口径不同，不能简单相减就称“正常化利润”；足以说明要重建经营利润和现金流，而不能把当季转盈当AI模式已成熟。所读Q2结果是7/30发布，晚于原帖，属于本次更新证据。[TEM原始Q2](https://www.tempus.com/news/pr/tempus-reports-second-quarter-2026-results/)

NTRA继续看单次回款、毛利、保险覆盖、研发支出与稀释，尚不放进已低估名单。[Natera原始Q2](https://investor.natera.com/news/news-details/2026/Natera-Reports-Second-Quarter-2026-Financial-Results/default.aspx)

**对你当前状态的建议**

**把AI医疗作为新增研究假设，先选现金兑现路径清楚的公司，再核估值。** 研究优先级可从ISRG这类已有手术/耗材收入的模式开始，再研究TEM／NTRA的数据或诊断经济性。纯研发型AI制药的临床、融资与单一项目风险，不适合仅凭主题叙事作为你的核心配置。

文章可能说对方向，但股票收益仍取决于你付出的价格、未来每股现金回报与稀释。对你的三万美元，医疗个股若最终选入，应与Google、SOFI、机器人候选共用个股风险预算；45/55及个股5%目前仍为未采用草案，不额外叠加一套预算。本次不改日报观察名单和原有15%／25%提醒，也没有任何账户操作。

下一项有价值的工作是完成1–2家公司的正常化盈利、自由现金流及价格情景；本文还没做到这一步，因此没有发布买入价或声称谁已低估。

**口径、核验和缺口**

原帖公开HTML和封面已读并保存；没有执行网页脚本、没有绕过登录或访问限制，没有读取评论。7月文章与10月研究时点分开；ISRG用Q3、TEM/NTRA只引用本次读到的Q2，后两者未声称完成最新全部申报扫描。公司事实来自IR，监管/支付事实来自FDA和CMS；研究框架、资金分配与风险排序属于我的判断。

[逐项核验与来源](./claims_sources.json)。本次没有完成行业资金流、M&A统计、全行业估值或个股完整估值，因此不把这些缺口包装成利好结论。
'''
(P/'report.md').write_text(text)
print('article review and source checks written')
