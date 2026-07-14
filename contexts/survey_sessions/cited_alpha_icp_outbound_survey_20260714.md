# Cited Alpha ICP、线索发现与合规外联方案

日期：2026-07-14

模式：Internal decision memo

适用范围：英语公开市场首轮验证；美国优先，英国/欧盟线索需额外经过地区规则检查。

## 结论

Cited Alpha 的第一批客户不应从“金融行业或互联网行业的人”里广泛寻找。行业标签只能扩大名单，无法说明购买动机。真正有价值的信号是：这个人正在把大量外部信源加工成付费研究、客户报告、IC memo、竞争研究或高管决策材料，而且引用、复核和跨期更新会影响收入与职业信誉。

首轮顺序建议是：

1. 独立 equity research 出版者、付费金融 newsletter 和 2–10 人研究团队。
2. 科技 VC/CVC 的 thesis research 与 pre-diligence 团队、Corporate Strategy / Corp Dev。
3. 服务科技客户的 boutique analyst team，以及 B2B SaaS Competitive / Market Intelligence 团队。

当前产品公开定位是把研究问题、选定信源、Agent 过程和带引用产物放在同一个 Deep Work 中，公开用例也已经集中在个人投资者、金融内容创作者和独立分析师。[Cited Alpha 产品说明](https://cited-alpha.forgepane.com/zh/product/source-backed-research) 与这个切入点一致。对外应把产品说成：

> Source-to-memo 可审计研究工作台。

不宜先卖“AI 投资”“自动选股”“Bloomberg 替代”或“通用 AI research”。这些表述会吸引只要交易信号的人，也会让专业研究者先质疑准确率、数据授权和合规责任。

## 为什么先做金融研究出版者

这群人的研究过程公开、交付频率可观察、本人通常就是购买者，首轮产品反馈也能直接映射到来源、引用、memo、版本和复查体验。

- 一位研究从业者把 earnings call 的处理描述为耗时且无法扩展；评论中的 credit analyst 覆盖超过 120 个名称，仍需逐一听 call 或细读 transcript。[Financial Careers 讨论](https://www.reddit.com/r/FinancialCareers/comments/1scs2sg/how_do_you_actually_handle_earnings_calls_in/)
- 另一位投资者明确寻找 official sources、filings、transcripts、peer KPI 和 source-based verifiable outputs 的重复工作流。[Value Investing 讨论](https://www.reddit.com/r/ValueInvesting/comments/1qvsld2/how_do_you_use_chatgpt_or_other_ais_to_find_stock/)
- Hacker News 的 SEC filing 工具讨论把研究劳动概括为反复阅读、取表和形成结论，同时提醒开放式金融生成容易出错。[HN 讨论](https://news.ycombinator.com/item?id=36967205)
- [Aurelion Research](https://read.aurelionresearch.com/p/get-familiar-with-aurelion-research) 是四人团队，每周约发布两份研究；[Whiteout Capital](https://whiteoutcapital.com/) 是独立微盘研究作者；[WhaleQuorum](https://whalequorum.com/) 已经用 AI 处理四类公开市场数据并保留人工审核。它们说明需求已经表现为持续生产流程，而不是一次性的信息问答。

金融侧 P1 画像如下：

| 画像 | 核心任务 | 强购买信号 | 反向信号 |
|---|---|---|---|
| 独立 equity analyst / 付费 newsletter，1–5 人 | 从 filings、transcripts、行业来源写 stock memo、deep dive 和更新 | 付费订阅；每月两篇以上深度报告；公开 research process；有 watchlist 和历史观点 | 只发盘中观点、技术分析、新闻转发；没有完整长文和来源 |
| 5–15 人小型基金的 PM / research lead | 多来源材料形成 IC memo，跨季度续接 thesis | coverage 扩大；earnings season；已有 AI power user；公开讨论 Claude/Deep Research | 强制 on-prem；主要依赖当前无法接入的私有 sell-side 数据；采购周期过长 |
| Source-heavy 金融作者、调查记者 | 把公开记录、监管文件和访谈加工为可信内容 | 付费会员；长文 cadence；corrections policy；反复强调 public record、source、evidence | 主要价值来自娱乐、情绪或快速行情 |
| Boutique / forensic research | 构建 allegation-evidence matrix、客户报告和审计记录 | 连续追踪监管、法院、跨国披露；准备新报告；有公开咨询业务 | 主要依赖机密 tip；不能接受云端处理 |

独立 RIA/CIO 只在明确做个股组合、model portfolio 或 research-file 归档时进入名单。泛财务顾问的大部分 AI 需求在会议记录和客户沟通，并不匹配当前产品。

## 互联网行业只保留重研究角色

互联网行业里，当前匹配点是把碎片信息转成正式决策材料。普通 CTO、产品经理、BizOps 和内容营销并没有稳定的 source-backed research 任务。

| 优先级 | 画像 | 当前可卖的任务 | 当前缺口 |
|---|---|---|---|
| A1 | 科技 VC/CVC Research Analyst、Associate、Principal | market map、investment thesis、IC memo first pass | 私有文件、CRM、数据室、授权数据 |
| A2 | Corp Strategy / Corp Dev / Office of CEO | market entry、build/partner/buy、M&A scouting、董事会 brief | Excel/模型、权限、多人协作 |
| A3 | Boutique technology analyst team | 客户报告、行业扫描、证据审查 | 白标导出、模板、多人 QA |
| B1 | Competitive / Market Intelligence、Senior PMM | competitor deep dive、高风险 claim 验证 | 持续 diff、Gong/CRM/Slack、battlecard 自动更新 |
| B2 | 独立科技分析师 / newsletter | source curation、fact-check、研究档案 | 发布集成、作者语气、prosumer 价格 |

VC 社区已经在用 agent 做 sourcing、founder research、market research、memo 和 initial diligence，但完成后仍要人工找来源复核。[VC 的 LLM research 讨论](https://www.reddit.com/r/venturecapital/comments/1lwvfym/) 与 [VC agent workflow 讨论](https://www.reddit.com/r/venturecapital/comments/1t78poc/ideas_for_claude_agents_in_vc_workflows/) 都支持把 Cited Alpha 限定为 pre-diligence 与 first pass，不能承诺自动完成完整尽调。

Competitive Intelligence 的需求也明确。PMM 使用 NotebookLM 时认为受控输入效果更好，但喂入资料本身繁琐；他们同时采集评论站、产品文档、HN、Reddit、招聘和 sales call，并希望每个 claim 都有来源。[AI competitive analysis 讨论](https://www.reddit.com/r/ProductMarketing/comments/1iyybpn/) 与 [battlecard 讨论](https://www.reddit.com/r/ProductMarketing/comments/1olppf2/) 说明 Cited Alpha 当前可以卖深度验证，完整 CI 平台还需要持续监控和内部数据连接。

互联网侧最容易理解的三个工作包是：

- 48 小时市场地图；
- 可核查的 build/partner/buy 决策 brief；
- 带来源冲突检查的 competitor deep dive。

## 从职位画像转成可观察信号

每条线索按 100 分评分。达到 70 分才进入人工外联，50–69 分只关注内容，低于 50 分不进入名单。

| 维度 | 分值 | 判断方式 |
|---|---:|---|
| 最近 90 天公开暴露具体研究任务或摩擦 | 25 | 提到 filings、transcripts、memo、citations、manual verification、stale battlecard 等 |
| 有重复研究产出 | 20 | 每月两篇以上报告、newsletter、客户 brief 或内部 memo 职责 |
| 输入信源复杂 | 15 | 同时使用监管文件、电话会、行业来源、社区、招聘、数据库等 |
| 结果影响收入或信誉 | 15 | 付费订阅、咨询、基金研究、董事会/IC/客户交付 |
| 团队与预算匹配 | 10 | 1–15 人研究团队、独立业务、正在招聘研究角色 |
| 有公开商务触达入口 | 10 | 官网 Contact、partnership、research、business inquiry、Sales Navigator InMail |
| 最近 30 天活跃 | 5 | 有新文章、新职位、新产品或公开讨论 |

建议的线索字段：

```text
lead_id, account, person, role, segment, region,
profile_url, proof_url, trigger_signal, signal_date,
public_business_contact, contact_source_url,
score, lawful_basis, privacy_notice_status,
last_contacted_at, reply_status, opt_out, notes
```

这里必须同时保留 `proof_url` 和 `contact_source_url`。前者解释为什么联系，后者解释联系方式从哪里来。

## 渠道打法

LinkedIn 和 X 应被当成需求雷达与上下文层，不是联系人数据库。

### LinkedIn

[Sales Navigator](https://business.linkedin.com/en-us/sales-solutions/sales-navigator) 提供 50 多项角色、seniority、公司和活动筛选。[官方搜索说明](https://www.linkedin.com/help/sales-navigator/answer/a106027) 建议用 `Posted on LinkedIn` 找最近活跃的人，[保存搜索](https://www.linkedin.com/help/sales-navigator/answer/a102024) 可以按周提示新匹配对象。

金融筛选：

```text
Title: Founder, Independent Research Analyst, Equity Research Analyst,
Investment Writer, Research Director, Portfolio Manager, Investment Strategist
Company headcount: 1-10, 11-50
Industry: Investment Management, Financial Services, Research, Online Media
Keywords: Substack, deep dive, 10-K, earnings transcript, investment memo,
fundamental research, independent research
Recent update: Posted on LinkedIn in 30 days
```

互联网筛选：

```text
Title: Head/Director of Competitive Intelligence, Market Intelligence Lead,
Corporate Strategy, Corporate Development, VC Research Analyst, Investment Associate
Company headcount: 11-500
Keywords: market map, investment thesis, competitive landscape,
build vs buy, source every claim, AI-first research
Recent update: Posted on LinkedIn in 30 days, Changed jobs in 90 days
```

不要用插件导出 profile，也不要把营销文案写进 connection request。LinkedIn 明确禁止未经授权的 scraping、bot、自动加联系人和自动发消息，违规可能导致账号受限或关闭。[LinkedIn 禁止的软件与扩展](https://www.linkedin.com/help/linkedin/answer/a1341387)

### X

使用原生搜索和人工阅读：

```text
("10-K" OR "10-Q") ("ChatGPT" OR "Claude") (citations OR hallucinations)
"earnings transcript" (workflow OR "time consuming")
"investment memo" (source OR footnote OR "audit trail")
("competitive intelligence" OR "market map") (Perplexity OR Claude OR NotebookLM) (sources OR citations OR verify)
("stale battlecards" OR "competitive research") (manual OR tedious OR hallucination)
```

优先回复对方具体内容，展示一条有用的来源或纠错，再询问是否愿意看样稿。不要批量发相同 DM。X 明禁未经书面许可的 scraping，[X Terms](https://x.com/en/tos) 和 [Automation Rules](https://help.x.com/en/rules-and-policies/x-automation) 也禁止批量或自动发送未经请求的 DM。

### 公开商务联系方式

优先级：

1. Warm intro。
2. 对公开内容作有实质信息的人工回应。
3. Sales Navigator 人工 InMail。
4. 对方官网的 research、partnership、contact form 或公司通用业务邮箱。
5. LinkedIn [Lead Gen Forms](https://business.linkedin.com/en-us/marketing-solutions/native-advertising/lead-gen-ads)、自有 newsletter、webinar 等 opt-in 渠道。

第三方私人邮箱 enrichment 暂缓。公开职业身份可以帮助筛选，公开不等于允许任意处理个人联系方式。

## 首批公开 seed leads

完整可导入表见 `contexts/survey_sessions/cited_alpha_seed_leads_20260714.csv`。这些是画像匹配种子，不代表已经表达购买意向。外联前需要人工阅读最近 3–5 篇内容，并重新确认联系入口仍然有效。

| 优先级 | 对象 | 匹配证据 | 公开触达入口 |
|---|---|---|---|
| A | [Aurelion Research](https://read.aurelionresearch.com/p/get-familiar-with-aurelion-research) | 四人团队、每周约两份、模型与管理层访谈 | `contact@aurelionresearch.com` |
| A | [Whiteout Capital](https://whiteoutcapital.com/) | Solo 微盘研究、公开 writeups 和 Substack | 官网公开邮箱、[X](https://x.com/whiteoutcapital) |
| A | [The Scarcity Trade](https://scarcitytrade.com/) | 独立分析师，本地语言 filings、NAV/SOTP、向基金提供 memo | 官网预约、LinkedIn、X、Substack |
| A | [Value Don't Lie](https://www.valuedontlie.com/p/vdl-home-base) | 周度 watchlist、research process、10-K process | [X](https://x.com/Valuedontlie) |
| A | [P Equity Research](https://sidestack.io/directory/substack/pequityresearch) | 1K+ 免费、100+ 付费，deep dive 与 financial modeling | About 页公开商务入口 |
| A | [AI Weekly](https://aiweekly.co/about) | 每天扫描数百来源，每条链接 primary source | `alexis@aiweekly.co` |
| A | [The Applied Layer](https://appliedlayer-ai.com/contact) | 独立 enterprise AI research，公开接受 research collaboration | `hello@appliedlayer-ai.com` |
| B | [The Bowser Report](https://thebowserreport.com/contact-us/) | 小团队、月度 PDF、周度更新、长期微盘研究 | 官网联系表单 |
| B | [Sakonnet Research](https://sakonnetresearch.com/about/) | 独立 Substack、定制数据研究与 consulting | 官网公开邮箱 |
| B | [WhaleQuorum](https://whalequorum.com/) | 新近上线的 AI-assisted 研究 newsletter，四类公开数据、人工审核 | 官网 Contact |
| B | [Lighthouse Macro](https://lighthousemacro.com/) | 多频率付费研究、固定模板、图表和客户服务 | `research@lighthousemacro.com` |
| B | [AI Adjacent](https://aiadjacent.com/about) | 已公开自建 agentic research pipeline，适合访谈和 benchmark | `hello@aiadjacent.com` |
| B | [SemiAnalysis](https://newsletter.semianalysis.com/about) | Newsletter、机构研究和咨询同时存在 | 官方业务入口 |
| B | [Fundamental Edge](https://www.fundamentedge.com/about-us) | 直接服务 buy-side，并公开讨论基金 AI adoption gap | 更适合渠道伙伴 / design partner |

## 外联文案

第一封邮件不先介绍全部功能，也不直接要求注册。它只做三件事：指出一条具体研究行为，提出一个可验证的摩擦假设，提供一份小样或一次短访谈。

金融研究作者：

```text
Subject: A cited source pack for your [company/topic] research

Hi [Name] — I read your [specific report]. You are pulling together
[filings/transcripts/industry source], and I suspect the expensive part is
keeping each claim mapped to evidence while the thesis changes over time.

I’m building Cited Alpha, a source-to-memo research workspace. I can recreate
one section of that report as a cited brief using only public sources, so you
can judge the output against work you already know. Useful if I send it?

If this is not relevant, reply “no” and I won’t follow up.
```

VC / Strategy / CI：

```text
Subject: Source-backed first pass on [market / competitor]

Hi [Name] — your recent [role/post/job opening] suggests the team is building
[market map / competitive research / build-vs-buy] capability.

Cited Alpha keeps the question, controlled source set, research steps and
cited decision brief in one workspace. I can prepare a 2-page first pass on
[specific market/competitor], including conflicting evidence and open questions.
Would that be useful for a 20-minute workflow review?

If not, I’ll close the loop here.
```

不要使用“AI 五分钟分析股票”“提前发现别人不知道的信号”等承诺。首轮 demo 应带一个真实标的或竞争问题，呈现最近四期材料、关键变化、bull/bear/未确认假设和逐条引用。

## 四周验证方案

### 第 1 周：名单与样稿

- 美国市场先建立 60 个 account，不先建大规模个人库。
- 金融出版者、VC/Strategy、CI 各 20 个；按评分选出每组 10 个。
- 做三份可公开审阅的样稿：earnings memo、market map、competitor deep dive。

### 第 2 周：人工外联

- 每天 5–10 条逐条审核的消息，每人只发一封初始消息。
- 优先 warm intro、公开内容回应、InMail、官网商务联系入口。
- 每条消息引用对方一个具体 artifact，不群发相同内容。

### 第 3 周：设计伙伴验证

- 目标是完成 5 次 workflow interview、3 次真实 source pack 导入、3 个完整 Deep Work。
- 观察对方是否愿意提供当前材料、是否能独立完成、是否会复查引用、是否在 7 天内再次使用。

### 第 4 周：决定 ICP

先使用以下实验阈值，不把它们当作行业基准：

| 指标 | 继续投入阈值 |
|---|---:|
| 高度个性化外联回复率 | ≥ 20% |
| 回复转 workflow interview | ≥ 40% |
| Interview 转真实试用 | ≥ 50% |
| 完成首个 Deep Work | ≥ 60% |
| 7 天内第二次使用 | ≥ 30% |
| 明确愿意付费或进入 design partner | 至少 2 个 |

如果金融出版者能达到第二次使用，而 VC/CI 只愿意访谈，就继续聚焦金融。若 CI 明确要求持续 diff、Gong/CRM 和 battlecard 更新，应把它记录为产品扩展证据，不能用销售话术提前承诺。

## 合规和数据最小化

这部分只用于运营设计，不构成法律意见。

- 美国 [CAN-SPAM](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) 同样适用于 B2B。邮件需要真实发件信息、非误导主题、商业性质说明、实体邮寄地址、清晰退出方式，并在 10 个工作日内处理退出。
- 英国 [ICO B2B marketing guidance](https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/business-to-business-marketing/) 区分 corporate subscriber 与 sole trader；实名工作邮箱仍可能属于个人资料，必须有 lawful basis、透明告知和退出机制。
- 欧盟从公开来源取得职业联系资料时，[GDPR Article 14](https://eur-lex.europa.eu/eli/reg/2016/679/art_14/oj/eng) 要求最迟在首次沟通说明来源、目的、法律基础、保留期限和权利；[Article 21](https://eur-lex.europa.eu/eli/reg/2016/679/art_21/oj/eng) 赋予 direct marketing 的绝对反对权。

Pilot 阶段关闭 tracking pixel。维护统一 suppression list，对方拒绝、退订或表示无关后立即停止。CRM 只保留完成筛选、联系和防止再次触达所需的最少字段；每 90 天重新核验一次是建议的内部保守规则，不是法定期限。

## Claim 验证结果

| Claim | 结果 |
|---|---|
| 独立研究出版者、小型研究团队优于泛金融人群 | 已获得多组公开工作流与持续生产证据，仍需真实外联验证转化 |
| 行为信号优于职位名称 | 产品推断得到案例支持；转化优势需通过四周 pilot 验证 |
| 互联网行业只应先做 VC/Strategy/CI 等重研究角色 | 公开职位与社区工作流支持；当前产品缺口已明确 |
| LinkedIn/X 抓取和自动私信风险高 | 官方平台条款已验证 |
| 公开商务联系页优于私人联系方式补全 | 平台规则与监管指引支持 |
| 20–30 个高信号人工外联适合作为首轮规模 | 这是实验设计，不是已验证行业结论 |

最重要的下一步不是继续扩充名单，而是拿 30 个高分目标跑完一次完整实验。回复、真实 source pack、第二次使用和付费意愿会决定 Cited Alpha 的实际 ICP。
