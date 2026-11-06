"""Public-only research sections. All prices USD, model assumptions explicit."""
def src(title, url): return {"title": title, "url": url}

CGNX_SOURCES = [
src("Cognex 11/4 Q3财报与现金流", "https://www.prnewswire.com/news-releases/cognex-reports-third-quarter-2026-results-302929644.html"),
src("9/22 RealSense交易条款", "https://investor.cognex.com/news/news-details/2026/Cognex-to-Acquire-RealSense-Expanding-Machine-Vision-Leadership-into-High-Growth-Robotic-Perception-Market/default.aspx"),
src("SEC近期申报清单", "https://data.sec.gov/submissions/CIK0000851205.json"),
src("CGNX第二行情与时间", "https://stockanalysis.com/stocks/cgnx/history/")]
NOW_SOURCES = [
src("NOW Q3 10-Q", "https://www.sec.gov/Archives/edgar/data/1373715/000137371526000096/now-20260930.htm"),
src("NOW 2025 10-K", "https://www.sec.gov/Archives/edgar/data/1373715/000137371526000007/now-20251231.htm"),
src("NOW Q3官方财报", "https://investor.servicenow.com/news/news-details/2026/ServiceNow-Reports-Third-Quarter-2026-Financial-Results/default.aspx"),
src("NOW第二行情", "https://stockanalysis.com/stocks/now/history/")]
CRM_SOURCES = [
src("CRM FY27 Q2 10-Q", "https://www.sec.gov/Archives/edgar/data/1108524/000110852426000190/crm-20260731.htm"),
src("CRM FY26 10-K", "https://www.sec.gov/Archives/edgar/data/1108524/000110852426000060/crm-20260131.htm"),
src("CRM Q2官方财报及指引", "https://investor.salesforce.com/news/news-details/2026/Salesforce-Delivers-Record-Second-Quarter-Fiscal-2027-Results/default.aspx"),
src("Fin完成收购", "https://www.salesforce.com/news/press-releases/2026/09/10/salesforce-completes-acquisition-of-fin/"),
src("Contentful交易及完成更新", "https://www.salesforce.com/news/stories/salesforce-signs-definitive-agreement-to-acquire-contentful/"),
src("10/20拟收购Braze", "https://www.salesforce.com/news/press-releases/2026/10/20/salesforce-signs-definitive-agreement-to-acquire-braze/"),
src("CRM第二行情", "https://stockanalysis.com/stocks/crm/history/")]

NOW = {"title": "四股估值①｜NOW：业务增长快，扣除SBC后价格要求仍高", "paragraphs": [
"营业范围：IT服务、客户服务、员工服务与跨部门流程订阅，AI智能体嵌入已有流程。2026-11-04常规收盘108.81美元，Yahoo与第二来源一致；股价、EPS和10.43011亿Q3稀释股统一为2025年12月一拆五之后口径。",
"最新2026Q3截至9/30、10/28发布：总收入41.06亿美元，GAAP营业利润3.85亿（按未四舍五入收入复算约9.38%），调整营业利润13.38亿（约32.59%）。差额包括SBC6.33亿、并购摊销1.98亿、并购相关0.35亿、遣散0.87亿；GAAP净利2.77亿、EPS0.27。不能用调整利润率直接推导股东能拿走同额现金。",
"前三季标准FCF＝CFO30.96亿−现金capex3.46亿＝27.50亿；公司展示的31.21亿FCF还加回3.71亿并购现金成本。过去12个月按全年＋本年累计−去年同期复算：CFO53.34亿、capex5.84亿，标准FCF47.50亿；减SBC23.23亿后24.27亿。报告FCF收益率约4.19%，扣SBC后的股东现金代理约2.14%，这比只看非GAAP利润更能暴露定价要求。",
"DCF资本桥：TTM已付利息0.50亿、利息收入3.32亿，用23.5%假设税率剔除净投资利息，独立经营现金流锚22.1127亿美元。基准再加回50%的税后并购现金成本，锚23.6542亿；保守不加回，乐观全部加回，锚分别22.1127/25.1957亿。现金及有价证券69.61亿、有息本金约76亿，净债务约6.39亿。战略投资账面20.50亿不计基准；若可按全部账面实现，价格敏感性约+1.97美元/股，不是认定它们毫无价值。",
"十年DCF假设：前五年现金流增速12%/20%/24%，后五年6%/10%/12%，折现率11.5%/10%/9%，永续2.5%/3%/3.5%；首年＝上述起始现金流×(1+增速)，第10年计算终值。经营价值减净债务，再除稀释股，保守/基准/乐观约38.64/83.30/141.66美元。终值占企业价值约49%/61%/70%，均不是官方目标价。利息收入是现金利息代理、精确税效及租赁拆分未完全核定，结果存在模型误差。",
"判断：108.81高于基准，未确认低估。基准价值八折66.64美元，严格保守八折30.91美元；后者是严苛压力条件，不预测必然出现。维持基准其他假设，现价需要前五年扣SBC后的经营现金流年增约26.97%，高于基准20%，不是要求收入本身必须以同速增长。若更快增长、利润率提升或更低资本成本成立，现价仍可被支持。",
"证伪与下次条件：AI ACV目标/使用量不等于收入；检查有机订阅增长、续费、扣SBC后每股现金、并购整合费是否下降。若现金流增长持续低于保守12%、SBC占比不降或GAAP成本恶化，原折扣价要重估；若明显经营杠杆兑现，则上调模型而非机械等待旧价。",
], "sources": NOW_SOURCES}
GEHC_SOURCES = [
src("GEHC Q3财报与全年指引", "https://investor.gehealthcare.com/news-releases/news-release-details/ge-healthcare-reports-third-quarter-2026-financial-results"),
src("GEHC完整Q3 10-Q（IR镜像）", "https://investor.gehealthcare.com/node/12596/html"),
src("2025年报业绩公告", "https://investor.gehealthcare.com/news-releases/news-release-details/ge-healthcare-reports-fourth-quarter-and-full-year-2025"),
src("拟收购SOFIE公告", "https://gehealthcare.gcs-web.com/news-releases/news-release-details/ge-healthcare-acquire-sofie-biosciences-establishing-final-mile"),
src("GEHC带时刻第二行情", "https://stockanalysis.com/stocks/gehc/statistics/")]

GEHC = {"title": "四股估值③｜GEHC：盈利法约90，现金流基准约69，不能平均成便宜", "paragraphs": [
"营业范围：MRI/CT、超声、患者监护、影像软件、维护服务与诊断药物。AI能通过设备功能、软件订阅和临床流程产生收费，但公司没有单列AI收入，不能给全部业务纯软件估值。行情为2026-11-04常规收盘85.81美元、+6.38%，Yahoo与第二来源一致；估值不混用盘后。",
"最新已公布2026Q3（截至9/30，10/28发布）：收入55.13亿美元、同比+7.2%，有机+6.2%；GAAP EPS1.36、调整EPS1.34。Q3调整EPS+25%，但前三季调整EPS3.46只约+10%；Q3调整EBIT率改善180基点，其中官方桥图约90基点来自关税影响，不能全归功于AI。",
"2026管理层调整EPS指引4.95–5.05美元，FCF为16亿美元以上的下限式指引，不能当精确预测。前三季CFO13.65亿−capex3.92亿＝FCF9.73亿；现金关税退款1.62亿、SBC1.16亿。以前年度关税利润收益已从调整EPS扣除，不再把现金退款从EPS重复扣。库存及合同/递延资产前三季合计占用约6.95亿现金。",
"盈利倍数法：从5.00指引中点扣持续整合/重组及已知当年关税收益，得到约4.61正常化盈利锚（仍非GAAP）。未来年度EPS假设4.40/5.00/5.40×主观P/E14/18/21＝保守61.60/基准90.00/乐观113.40美元。2027官方指引未公布；基准需盈利较该锚再增长约8.6%。倍数非已核同行均值或历史分位。EPS已扣利息，价格不再减净债务。",
"现金流交叉检验：截至Q3的TTM CFO24.15亿−capex5.26亿＝FCF18.89亿；扣现金退款1.62亿和SBC1.52亿后剩15.75亿，按当日市值现金流收益率约4.06%。再回补净融资费用4.37亿×(1−20.5%)，约19.22亿企业现金流锚；这是研究者FCFF代理，现金净利息未完整拆分，存在误差。",
"五年DCF假设（均为研究情景）：未来12个月FCFF16.5/20/24亿美元，随后四年增长4%/7%/10%，WACC9.5%/8.5%/8%，永续2%/2.5%/3%。终值＝第5年FCFF×(1+永续增长)/(WACC−永续增长)，逐年折现后减本金净债务73.36亿、少数权益2.51亿、已披露融资租赁0.52亿，再除4.53亿稀释股。结果约35/69/117美元，终值占企业价值71%/77%/81%，对假设敏感。养老金及经营租金已在现金流，不再重复扣负债。",
"资本桥：不受限现金28.26亿；借款账面99.73亿，本金101.62亿，模型用本金。Intelerad已完成收购反映在报表；SOFIE拟9.45亿现金交易预计2027上半年完成，主模型既不扣未来付款也不加未披露协同，只付现金不产生价值的压力影响约−2.09美元/股。",
"安全边际：盈利基准90打八折为72美元，现金流基准68.68打八折为54.94美元。55–60只能叫基准DCF约13%–20%折扣研究区；72只有盈利法支持，不能说两法都便宜。更严格的保守DCF八折约28美元，仅为压力条件，不是下跌预测。当前85.81尚无现金流确认的20%折扣；维持基准增长/折现假设，要支持现价首年FCFF需约24亿，接近乐观首年水平。",
"证伪与更新条件：如果回款改善、剔除退款的FCF持续提升，DCF可能过于保守；如果连续两季有机订单转负、订单收入比低于1，或库存/合同资产继续快于收入增长，应下调估值。AI付费附加率/续费、SOFIE资本桥、2027指引仍待核，不因获批直接提高估值。",
], "sources": GEHC_SOURCES}

CGNX = {"title": "四股估值④｜CGNX：53美元已接近乐观现金流情景", "paragraphs": [
"营业范围：机器视觉、传感器、工业读码及检测软件，面向制造与物流的识别、定位、质检和自动化。2026-11-04常规收盘53.06美元、当日−8.69%；该收盘在16:30美东财报发布之前。Yahoo与本次重新打开的StockAnalysis历史页收盘一致，早晨第二源53.09的旧快照已被本次读数替代。",
"Q3截至10/4：收入3.134亿美元、同比+13%；GAAP EPS0.50、调整EPS0.53。上年税率异常高，GAAP EPS跳升不能当可持续增速。2026全年调整EPS指引1.68–1.72，中点1.70对应收盘约31.21倍；这是管理层展望，不是TTM盈利。Cognex调整EPS保留常规SBC，倍数法不能重复扣股权激励。",
"现金流锚：前三季CFO2.20661亿−capex0.06928亿＝FCF2.13733亿美元；减SBC0.34291亿，再减投资收益0.13285亿×80%税后代理，乘4/3得到约2.251亿独立主营股东现金流锚。9个月年化仅用于正常化参照，不是公司全年预测；税率20%是假设，投资收益与现金回款时间仍有误差。常规SBC作为成本扣除后，不再机械追加同等未来稀释。",
"十年独立主营DCF：起始正常化现金流2.05/2.25/2.50亿美元；前五年增长6%/10%/15%，后五年4%/5%/8%，折现率11%/10%/9.5%，永续2.5%/3%/3.5%。首年＝起始现金流×(1+前五年增速)，终值按第10年现金流计算并折现。主营现金流不含RealSense未来利润。",
"RealSense资本桥单列：10/4现金及投资8.45984亿、无有息债务；拟收购价5亿，另有三年目标现金留任0.565亿及约0.50亿RSU。为避免把收购当无偿损失，另对取得业务设2.5/5/7.5亿价值敏感性（购买价0.5/1/1.5倍），而非声称已完成其独立估值。保守一次扣足留任与RSU经济成本；RSU不再同时加股数。交割未确认、目标利润未披露，因此该项高度不确定。",
"主营DCF加上述资本桥，除Q3稀释股1.71027亿，得到保守约20.31/基准31.98/乐观53.30美元。终值占主营价值约48%/56%/63%。这组结果比早晨仅按EPS×终值PE的敏感性更谨慎：扣了SBC、保留收购代价，且没有把机器人增长无限外推；此前31.59/45.68/67.53美元不是完成估值或已批准买价，本次专题取代其作为主要研究口径。",
"判断：当前53.06不能确认低估，接近乐观DCF；财报后约51美元也仍需要较好长期增长。基准价值八折约25.58美元，严格保守八折约16.25美元；均为模型条件价，不能改写成必然会到或触发即买。下一步看电话会/完整10-Q、RealSense交割与独立利润、扣SBC后现金流；若主营增长长期低于6%或收购兑现弱，原条件价也要下调。",
"截至本次SEC近期清单，Q3财报已经发布，完整Q3 10-Q尚未列出；最新完整10-Q仍是Q2。11/5美东08:30电话会对应北京21:30，尚未发生。不得把财报未发布、电话会已听完或目标收入预测当事实。",
], "sources": CGNX_SOURCES}

FDE = {"title": "FDE上市公司地图｜谁靠软件复用，谁仍靠工程师工时", "paragraphs": [
"这里FDE指Forward Deployed Engineering：工程师进入客户场景，把模型接到数据、权限、旧系统和工作流程，完成生产部署与迭代。它首先是交付模式，而非财报已独立可比的新行业。以下六家有官方产品/合作/岗位证据，但本次读取的财报均没有单列FDE收入或利润；招聘不能证明财务规模。",
"PLTR（Palantir）｜Foundry/Ontology/AIP连接数据与业务动作，Gotham服务政府、Apollo负责部署。官方FDSE岗位明确数据整合、客户应用与端到端交付；收入来自平台订阅、期限许可、维护及专业服务。是‘自有平台＋FDE’最直接的样本。2026Q3总收入23.134亿美元、美国商业收入9.84亿不是全部FDE/AIP收入；试点成本可能在销售费用，高毛利不证明每个项目赚钱。本次未完成PLTR估值，业务贴合不等于股票便宜。",
"NOW（ServiceNow）｜IT、客服、员工等企业流程订阅；5/6与ACN启动联合FDE，含300多项预构建技能/工作流。Q3订阅收入39.88亿、占总收入约97.1%，说明收费主体是平台；但专业服务及其他收入1.18亿、成本1.57亿，实施可能是带动订阅的成本中心。须核AI增购、续约、交付补贴，不能将全部订阅视为AI。",
"CRM（Salesforce）｜销售/客服CRM、Data 360、Slack与Agentforce。4/15推出含30家公司的FDE伙伴网络，实施后继续推动生产采用；客户支付软件订阅/消费、实施另依合同。最新Agentforce ARR超15亿，但口径已扩展，不是同口径新增消费或当期收入。要看新收费能否超过旧席位减少与打包折扣。",
"ACN（Accenture）｜战略咨询、系统集成、行业转型与托管运营，已推出Microsoft、ServiceNow、Workday的FDE项目，属于跨平台落地。合同含工时、固定价、交易量和奖罚，不把所有固定价都叫结果付费。FY2026收入742亿美元、Q4毛利率32%；最新单列advanced AI收入仍是FY2026Q1旧季度11亿，此后不再单列，不冒充最新AI规模。",
"EPAM（EPAM Systems）｜软件工程、数据/云、应用现代化与测试。Q2官方提出建设下一代FDE组织，但该季收入14.1477亿美元中78.03%按工时材料收费，固定价21.59%，许可及其他仅0.38%。这直接反证‘叫FDE就自动变成软件公司’。Q3官方电话会11/5美东08:00/北京21:00，本次仍用已发布Q2；观察单员工收入、项目毛利及按工时比例。",
"GLOB（Globant）｜数字产品、设计、营销、ERP/数据与AI工程。官方FDE岗位要求在客户现场交付并沉淀可复用工具（所读岗位专注国防，不外推所有客户）；AI Pods尝试按输出/消费订阅。Q2 Glob.AI ARR5280万美元、环比+61%，同时公司收入6.144亿美元基本持平、毛利率由35.4%降至33.9%。ARR非营业收入，不把ARR除季度收入算占比；需验证续费、真实收入与交付利润。",
"研究分组：平台型优先看PLTR、NOW、CRM；跨平台工程型看ACN、EPAM；GLOB看从工时转向输出订阅能否兑现。最重要的证伪问题是：工程师离开后谁继续收费？如果项目越多，人头与云成本同比例上升，或效率提升让客户减少购买工时，FDE可能只是更好的服务生意，并没有软件式经营杠杆。这是业务研究排序，不是股票收益或买入排序。",
], "sources": [
src("PLTR官方FDSE职责", "https://jobs.lever.co/palantir/7ea66860-ae93-4139-9388-b7284cb33f37"),
src("PLTR最新Q3 SEC附件", "https://www.sec.gov/Archives/edgar/data/1321655/000132165526000045/a2026q3ex991pressrelease.htm"),
src("NOW与ACN联合FDE公告", "https://newsroom.servicenow.com/press-releases/details/2026/ServiceNow-and-Accenture-launch-forward-deployed-engineering-program-to-scale-agentic-AI-across-the-enterprise/default.aspx"),
src("CRM官方FDE伙伴网络", "https://www.salesforce.com/news/stories/salesforce-launches-forward-deployed-engineer-partner-network-announcement/"),
src("ACN Microsoft FDE", "https://newsroom.accenture.com/news/2026/accenture-launches-microsoft-forward-deployed-engineering-practice-to-help-organizations-scale-ai-across-the-enterprise"),
src("ACN年度财报", "https://www.sec.gov/Archives/edgar/data/1467373/000146737326000037/q4fy26earnings8-kexhibit.htm"),
src("EPAM Q2官方转型与财报", "https://investors.epam.com/news/news-details/2026/EPAM-Reports-Results-for-Second-Quarter-2026/default.aspx"),
src("EPAM合同收费结构10-Q", "https://www.sec.gov/Archives/edgar/data/1352010/000135201026000046/epam-20260630.htm"),
src("GLOB官方FDE岗位", "https://career.globant.com/job/ForwardDeployedEngineeringManagerspecializedinDefenseProjects/79206"),
src("GLOB Q2官方财报", "https://investors.globant.com/2026-08-13-Globant-Reports-2026-Second-Quarter-Financial-Results") ]}
