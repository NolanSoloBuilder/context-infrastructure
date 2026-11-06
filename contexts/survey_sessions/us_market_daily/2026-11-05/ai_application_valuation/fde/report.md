# FDE：AI 落地的交付模式，还是新行业？

复核截至：2026-11-05 北京时间 10:54。仅研究公开上市公司的业务，不构成买入或已低估结论。以下金额均为美元；ARR、ACV、订单与已确认营业收入分别列示。

## 结论

**FDE（Forward Deployed Engineering，前线／驻场部署工程）首先是一种交付与销售模式，现阶段还不能当成财报独立可比的“新行业”。** 它解决的不是再训练一个基础模型，而是把模型接入客户的数据、权限、旧系统与真实工作流程，完成生产部署、评估、监控和持续迭代。研究到的六家公司均有相应产品或工程交付证据，但本轮读取的财报没有单列 FDE 收入或利润。

这条逻辑最关键的投资分界是：**工程师离场后，谁仍拥有可重复收费的软件、数据工作流和客户关系？** Palantir、ServiceNow、Salesforce 更接近“以工程服务促成平台使用和订阅扩张”；Accenture、EPAM、Globant 则更多依靠客户项目、工程交付及托管服务，也在尝试用可复用资产和订阅改变按人时收费。后者不能仅因招聘 FDE 就被赋予软件公司的盈利模式。

“产品复用与人力交付比例”没有统一披露。下面的订阅占比、按工时收费占比是财务／合同结构的代理，**不是复用代码比例、FDE 人数比例或 AI 收入占比**。

## 六家有实质证据的上市公司

### 1. Palantir｜PLTR：平台与 FDE 结合最直接的研究样本

- **营业范围与怎么落地：** Foundry／Ontology 连接企业数据与业务动作，AIP 接入模型和智能体，Gotham 服务政府客户，Apollo 支持软件部署。官方 FDSE 岗位描述明确由工程师进入客户现场，在自身平台上进行数据整合、定制应用和端到端部署；岗位存在证明组织模式，不证明某笔 AI 收入。[官方岗位，读取 11/05](https://jobs.lever.co/palantir/7ea66860-ae93-4139-9388-b7284cb33f37)
- **谁付款、怎样收费：** 企业／政府支付云订阅，或本地部署的期限许可加维护支持，并可能购买专业服务；实际由合同决定。年报说明专业服务包括支持、界面配置、培训和数据建模；部分实施与许可高度关联，不能简单把全部工程成本视为单独的咨询生意。[2025 年 10-K，2026-02-17 申报](https://www.sec.gov/Archives/edgar/data/1321655/000132165526000011/pltr-20251231.htm)
- **付费证据：** 2026Q3 收入 **23.134 亿**，同比 **+96%**；美国商业收入 **9.84 亿**，同比 **+148%**。总毛利／收入复算约 **83.43%**。这些证明平台整体已经规模收费，不能归为全部 AIP 或 FDE 收入。[11/02 财报](https://www.sec.gov/Archives/edgar/data/1321655/000132165526000045/a2026q3ex991pressrelease.htm)
- **复用与反证：** 公司财报按政府／商业划分，未单列 FDE；试点人员及云成本也可能进入销售费用，因此高毛利本身不能证明每个 FDE 项目经济性优良。下一步检验商业客户扩张是否持续转化为收入与现金流，以及交付费用和获客费用是否快于收入增长。

### 2. ServiceNow｜NOW：企业工作流平台加联合驻场工程

- **营业范围与部署证据：** IT、客服、员工、风险等企业工作流及 AI 智能体。2026-05-06 与 Accenture 发布联合 FDE 项目，在客户环境中组队实施，并提供 **300 多项预构建智能体技能／工作流**；这是可复用平台资产加行业交付的明确实例。[官方联合公告](https://newsroom.servicenow.com/press-releases/details/2026/ServiceNow-and-Accenture-launch-forward-deployed-engineering-program-to-scale-agentic-AI-across-the-enterprise/default.aspx)
- **谁付款、怎样收费：** 客户支付平台／产品订阅，实施工作可能由 ServiceNow 或伙伴承接。Now Assist 的 assists 是合同约定的使用计量单位，额度和超额费用依合同确定；不能把计量单位直接当独立收入。[官方使用条款，2026-08-24 生效](https://www.servicenow.com/content/dam/servicenow-assets/public/en-us/doc-type/legal/sn-assist-overview.pdf)
- **付费证据：** 2026Q3 总收入 **41.06 亿**、订阅收入 **39.88 亿**，约占 **97.13%**；专业服务及其他收入 **1.18 亿**。年末 AI ACV **17 亿**是管理层目标，AI 生产使用量增长是使用指标，均不等于当季 AI 营业收入。[10/28 财报](https://newsroom.servicenow.com/press-releases/details/2026/ServiceNow-Reports-Third-Quarter-2026-Financial-Results/default.aspx)
- **复用与反证：** 平台收费主体明确，但全部订阅并非 AI。该季度专业服务及其他成本约 **1.57 亿**，高于其收入；实施可以是促进订阅的成本中心。要追踪 AI 合同转为续费／实际使用、交付补贴是否下降，不宜因 FDE 发布会就认定新增利润已兑现。

### 3. Salesforce｜CRM：把 Agentforce 部署到销售、客服及内部流程

- **营业范围与部署证据：** 销售／客服 CRM、Data 360、Slack 及 Agentforce 智能体。2026-04-15 官方推出 FDE 伙伴网络，包含 Accenture、Deloitte 等 30 家企业，强调生产部署、产品团队协作及上线后采用。[官方网络公告](https://www.salesforce.com/news/stories/salesforce-launches-forward-deployed-engineer-partner-network-announcement/)
- **谁付款、怎样收费：** 企业购买 CRM／Agentforce，实施可向 Salesforce 或伙伴付费。官网列示 Flex Credits **500 美元／10 万 credits**、部分会话计价 **2 美元／次**；这是产品标价示例，不能当所有客户的总实施价格或 FDE 服务费，底层订阅、数据和集成成本另依合同。[官方价格页，读取 11/05](https://www.salesforce.com/agentforce/pricing/)
- **付费证据：** 最新已发布 FY2027Q2（截至 2026-07-31）总收入约 **113 亿**，订阅及支持约 **108 亿**。Agentforce ARR **超过 15 亿**，但本季定义扩展纳入相关 AI 产品、Slackbot 和 Headless 360，不能将其增长全部解释为同口径新增 Agentforce 消费。[08/26 财报](https://www.salesforce.com/news/press-releases/2026/08/26/fy27-q2-earnings/)
- **复用与反证：** 约 95.6% 的订阅及支持收入占比来自四舍五入数据，且包含大量既有业务。FDE 未单列收入；关键是新 AI 收费能否超过旧席位／人工工作被替代后的收入损失，以及 credits 消耗是否带来客户可验证的成本节省和续约。

### 4. Accenture｜ACN：多平台的企业 AI 集成与运营，敞口广但不纯

- **营业范围与部署证据：** 战略咨询、系统集成、应用及业务流程托管、行业转型。除 ServiceNow 联合项目外，2026-03-18 推出 Microsoft FDE practice，10/13 推出 Workday FDE 项目，进入客户的财务、人力和企业流程。[Microsoft 公告](https://newsroom.accenture.com/news/2026/accenture-launches-microsoft-forward-deployed-engineering-practice-to-help-organizations-scale-ai-across-the-enterprise)；[Workday 公告](https://newsroom.accenture.com/news/2026/accenture-launches-forward-deployed-engineering-program-with-workday-to-reinvent-work-for-the-agentic-ai-era)
- **谁付款、怎样收费：** 企业按工时材料、固定价格、交易笔数、混合收费或含奖励／罚则的合同支付。自有工具和行业蓝图能提高复用，但并未披露复用工时比例。固定价格不自动等于按成果收费，失败或超支也由服务商承担更多风险。[FY2026 10-K，期末 08/31](https://www.sec.gov/Archives/edgar/data/1467373/000146737326000049/acn-20260831.htm)
- **付费证据与披露变化：** 最后单列 advanced AI 的季度 FY2026Q1（2025-11-30 截止）收入 **11 亿**、订单 **22 亿**；公司表示以后因 AI 嵌入广泛业务而不再单列，不能将这个旧季度数字当 2026 年最新 AI 收入。[2025-12-18 官方演示稿](https://investor.accenture.com/~/media/Files/A/accenture-v4/investors/earnings-reports/2026/first-quarter-fiscal-2026-earnings-presentation.pdf)
- **规模与反证：** FY2026 收入 **742 亿**；Q4 毛利率 **32.0%**，业务包含约一半咨询、一半托管服务。没有 FDE 独立财务线。AI 项目增加可能抵消而非超越旧服务收入减少；应看收入／员工、固定价项目毛利、利用率及订单转收入。[10/01 年度财报](https://www.sec.gov/Archives/edgar/data/1467373/000146737326000037/q4fy26earnings8-kexhibit.htm)

### 5. EPAM｜EPAM：从软件工程外包转向 AI 原生 FDE，仍主要按人时收费

- **营业范围与部署证据：** 软件产品工程、数据／云平台、应用现代化及测试等。2026Q2 官方财报中 CEO 明确提出建设下一代 FDE 组织。这是经营方向表述，不能据此认定全部工程业务已完成转型。[08/06 Q2 财报](https://investors.epam.com/news/news-details/2026/EPAM-Reports-Results-for-Second-Quarter-2026/default.aspx)
- **谁付款、怎样收费：** 企业客户为工程项目付款。2026Q2 收入 **14.1477 亿**，其中按工时材料收费 **11.0391 亿／78.03%**，固定价格 **3.0549 亿／21.59%**，许可及其他 **0.0537 亿／0.38%**。这是六家中很有价值的模式验证：口头强调 FDE，并未使合同结构马上变为平台订阅。[Q2 10-Q，08/06 申报](https://www.sec.gov/Archives/edgar/data/1352010/000135201026000046/epam-20260630.htm)
- **付费证据与反证：** Q2 总收入同比 **+4.5%**、GAAP 营业利润率 **10.8%**；财报未单列 FDE 收入。本轮未从官方财报正文核得独立 AI 收入金额，不用第三方电话会转录中的 AI-native 数字替代。核心风险是 AI 提高效率后客户购买的工程工时下降，节省未由 EPAM 留存。
- **下一核查条件：** Q3 电话会定于 **11/05 08:00 美东／21:00 北京**，本研究截至时尚未到该发布窗口，不能提前引用 Q3 结果。检查固定价／许可收入占比、单员工收入、AI 业务定义和利润率是否改善。[官方日程](https://investors.epam.com/news/news-details/2026/EPAM-Announces-Date-for-Third-Quarter-Earnings-Release-and-Conference-Call/default.aspx)

### 6. Globant｜GLOB：FDE 人才加 AI Pods，订阅转型尚小

- **营业范围与部署证据：** 数字产品工程、设计、营销、ERP／数据及 AI 转型。官方 FDE Manager 岗位要求进入战略客户现场、交付生产系统，并把通用模式反馈到核心工程团队；此岗位专注国防项目，不能扩展为公司全部客户或业务都采取同一模式。[官方岗位，读取 11/05](https://career.globant.com/job/ForwardDeployedEngineeringManagerspecializedinDefenseProjects/79206)
- **谁付款、怎样收费：** 传统业务主要是客户按人时购买数字工程服务，另有固定价和少量许可；AI Pods 则尝试按输出／消费订阅，结合专家工程服务。两套模式并存，不能把全公司当作订阅软件。[2025 年 20-F](https://www.sec.gov/Archives/edgar/data/1557860/000162828026012910/glob-20251231.htm)
- **付费证据与反证同时存在：** 2026Q2 Glob.AI ARR **5280 万**、环比 **+61%**；同期全公司季度收入 **6.144 亿**、同比基本持平，IFRS 毛利率 **33.9%**，低于去年 **35.4%**。ARR 不是季度已确认收入，不拿 ARR 除季度营收计算“收入占比”。[08/13 Q2 财报](https://investors.globant.com/2026-08-13-Globant-Reports-2026-Second-Quarter-Financial-Results)
- **下一核查条件：** 看 ARR 转营业收入和现金流、续约、交付成本，及能否改变全公司平收入／毛利下滑。管理层的 AI Pods 高毛利判断没有提供单独审计利润表，不能视为已验证的全公司拐点。

## 如何证伪“FDE 是 AI 落地的下一批赢家”

1. **有项目，没有经济性：** 试点及部署数量上涨，却不转付费使用、续约、现金流；工程和云成本增长更快。需要项目毛利与客户续约，不能只看演示、合作公告或招聘。
2. **生产效率提升，收费基数缩水：** 服务商节省工时后，客户同步减少工时采购；软件商新增消费收入不足以抵消旧席位收入。收入／员工与利润率应随复用提升，否则只是换了工程职位名称。
3. **重复劳动没有沉淀为资产：** 每个客户都需要重写数据和流程，实施周期不缩短，FDE 人数随收入近似线性增长；这更接近优质项目制业务，不能直接用软件平台逻辑估值。
4. **模型和平台供应商把功能内置：** 基础模型、ERP 或云平台捆绑相同能力，独立服务商议价权降低；反过来，多平台和复杂监管环境也可能让集成长期有价值。要看客户留存与收费，而不是预设任何一方必然赢。

**研究优先级：** PLTR 适合核验“产品＋FDE”的商业杠杆；NOW／CRM 适合观察既有客户与工作流中的增量变现；ACN／EPAM 是跨平台实施的直接观察窗口；GLOB 是从工时向订阅输出转型的观察样本。这只是证据与业务模式的排序，不是股票收益、便宜程度或买入顺序。

## 核验边界

- 六家均未在本轮读取的财报中单列 FDE 收入／利润；没有可可靠量化的统一“FDE 行业营收”。也没有经官方披露的通用代码／定制人时比例。
- 公司“帮助客户创造价值”的叙述不是独立审计的 ROI。AI 使用、AWU、ARR、ACV、订单和营业收入不互换。
- Palantir 最新 Q3 数字已读 SEC 附件；完整 Q3 10-Q 本轮访问失败，收入确认政策依据 2025 10-K，不宣称读过新的全文。EPAM 仅使用已读 Q2 官方披露，待今夜 Q3 更新。
- 这里只解决“有哪些上市公司实际在做、如何挣钱”。估值、安全边际和与已有 ETF 的持仓重叠尚需下一步；没有将任何公司加入当前清单或自动配置。

机器可读来源、发布日、实际读取范围及披露缺口见同目录 `sources.json`。
