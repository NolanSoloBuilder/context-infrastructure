<!-- lark-mirror obj_token=VqtcdtJwCo9BZNxa6Dqjv7wrpUd space=产品调研 synced=2026-05-18T07:54:44Z -->

# 信源库建设PRD

## 信源库的作用

信源库（Source Catalog）的目标是**沉淀一套与目标用户最相关、可解释的高质量信源集合**，用于两个场景：

**场景一：冷启动默认给源**  
 用户输入“我关心的事情/问题/主题”后，系统能：

- 快速定位该主题覆盖所需的“信源集合”
- 默认输出一组**结构全面**的信源（而不是单独的零散链接）
- 并能用可解释方式说明：“为什么这些源值得看、带上信源分类，体现全面的抓取信源的视角”**示例种子信源**

  <callout emoji="🎁">
  示例case
  **Input**：我关心 AI Agent 投资机会  
  **Output**：我已经为「AI Agent 投资机会」配了一套信源池（共 **68** 个）：
  1. **证据层（18 个）**
  **用来回答**：Agent 这条路技术上到底行不行？现在突破点在哪？  
  **典型信源**：顶会论文 / 研究报告 / 评测与基准（论文库、开放评审、研究机构）
  1. **落地层（16 个）**
  **用来回答**：谁在做？做到什么程度？哪些组件已经能拼成“可用的产品”？  
  **典型信源**：开源社区 / 开发者工具 / 产品榜单 / 大厂工程博客
  1. **生意层（14 个）**
  **用来回答**：这件事怎么被切成赛道？怎么收费？投资人现在最看哪几种商业模式？  
  **典型信源**：VC/基金观点、操盘手 memo、创业项目观察
  1. **硬约束层（8 个）**
  **用来回答**：现实会卡在哪？合规怎么过？成本算不算得过账？企业采购是不是很慢？  
  **典型信源**：官方披露/监管与标准、成本与商业化信号、风险提示
  1. **风向层（12 个）**
  **用来回答**：哪里开始冒头？大家在吵什么？有哪些早期机会线索？  
  **典型信源**：社区讨论、趋势聚合（我会默认标注噪声风险）
  是否要开始follow？也可以把你更偏好信源类型、或者具体的信源站点告诉我\~
  </callout>

  - **证据层（18）**：顶会/论文/行业研究，帮你判断“Agent 真在解决什么问题、拐点在哪”。arXiv（论文预印本）— https://arxiv.org/OpenReview（ICLR/NeurIPS 等开放评审与论文）— https://openreview.net/ACL Anthology（NLP 顶会/期刊论文库）— https://aclanthology.org/Hugging Face Papers（论文聚合与趋势）— https://huggingface.co/papersHugging Face Trending Papers（趋势论文，常能看到 agent 方向）— https://huggingface.co/papers/trendingStanford HAI（研究与报告入口）— https://hai.stanford.edu/NIST AI（美国 NIST AI 相关资源入口）— https://www.nist.gov/artificial-intelligencePapers with Code（论文+代码聚合，找可落地方向）— https://paperswithcode.com/Google Research Blog（研究解读）— https://research.google/blog/Microsoft Research Blog（研究解读）— https://www.microsoft.com/en-us/research/blog/
  - **落地层（16）**：开源、开发者工具、产品榜单，帮你看到“谁在做、怎么落地、有哪些可用组件”。GitHub Trending（快速看生态热点）— https://github.com/trendingGitHub Topics: arxiv-papers（围绕论文/实现的生态入口）— https://github.com/topics/arxiv-papersProduct Hunt（新产品/新工具发现）— https://www.producthunt.com/OpenAI Developer Blog（API/工具链与最佳实践）— https://developers.openai.com/blog/OpenAI News（产品发布与能力更新）— https://openai.com/news/LlamaIndex（数据/Agent 应用框架生态）— https://github.com/run-llama/llama_indexLangChain（Agent/工作流框架生态）— https://github.com/langchain-ai/langchainHugging Face（模型与工具生态）— https://huggingface.co/Cloudflare Blog（AI/推理/边缘部署等工程实践）— https://blog.cloudflare.com/Netflix TechBlog（大规模系统/工程实践）— https://netflixtechblog.com/Uber Engineering（工程实践）— https://www.uber.com/en-US/blog/engineering/
  - **生意层（14）**：VC/基金/操盘手的框架与项目观察，帮你把“机会”落到可投赛道。SEC EDGAR（美股法定披露检索）— https://www.sec.gov/edgar/search/HKEXnews（港交所披露入口）— https://www.hkexnews.hk/index.htmHKEXnews Title Search（更适合检索公司公告）— https://www1.hkexnews.hk/search/titlesearch.xhtmlSGX Company Announcements（新交所披露）— https://www.sgx.com/securities/company-announcements巨潮资讯 CNINFO（中国法定披露聚合）— https://www.cninfo.com.cn/上交所公告（中国披露入口之一）— https://www.sse.com.cn/disclosure/listedinfo/announcement/NIST AI（标准/风险治理参考）— https://www.nist.gov/artificial-intelligence欧盟 AI Act 官方入口（法规文本与进展）— https://artificialintelligenceact.eu/  （如果你们不想用民间站点，可只保留欧盟官网入口）
  - **硬约束层（8）**：公开披露、政策监管、成本与商业化信号，帮你排雷。SEC EDGAR（美股法定披露检索）— https://www.sec.gov/edgar/search/HKEXnews（港交所披露入口）— https://www.hkexnews.hk/index.htmHKEXnews Title Search（更适合检索公司公告）— https://www1.hkexnews.hk/search/titlesearch.xhtmlSGX Company Announcements（新交所披露）— https://www.sgx.com/securities/company-announcements巨潮资讯 CNINFO（中国法定披露聚合）— https://www.cninfo.com.cn/上交所公告（中国披露入口之一）— https://www.sse.com.cn/disclosure/listedinfo/announcement/NIST AI（标准/风险治理参考）— https://www.nist.gov/artificial-intelligence欧盟 AI Act 官方入口（法规文本与进展）— https://artificialintelligenceact.eu/  （如果你们不想用民间站点，可只保留欧盟官网入口）
  - **风向层（12）**：社区讨论/趋势聚合，速度最快，但我会默认标注噪声风险。Hacker News（讨论密度高，早期信号强）— https://news.ycombinator.com/Reddit r/LocalLLaMA（开源/生态变化信号很快）— https://www.reddit.com/r/LocalLLaMA/Reddit r/MachineLearning（研究&工程社区）— https://www.reddit.com/r/MachineLearning/Techmeme（媒体线索聚合）— https://techmeme.com/Hugging Face Trending Papers（研究热点的“趋势信号”）— https://huggingface.co/papers/trendingSmol AI News / AINews（AI 资讯聚合）— https://news.smol.ai/Lobsters（偏工程师社区，质量较稳定）— https://lobste.rs/



**场景二：按信源形态做阅读交互适配**  
 信源的内容形态不同（公告/财报PDF/论文/博客/Newsletter/论坛/Repo等），决定了：

- 采集方式、展示方式（单集阅读体验要走不同的交互模版）、从单集中结构化提炼信息的逻辑都不同，因此信源库中需要把信源形态作为一个必须字段

---

## 怎么定义一个“好的信源库”

“好”拆成三个维度：**全面 / 高质量 / 可信** 。每项都需要可被量化评估，才知道对于用户而言，我们推荐出来的信源体验如何，并且长期可以根据量化评估持续性地改善信源库的数据质量。

#### 2.1 全面（Coverage）

**定义**：面对目标用户的常见主题输入，信源库能提供覆盖充分的信源集合，并且覆盖不是“数量大”，而是结构上“该有的都有”。  
**量化评估**：

- 测试的主题集合（30-50个主题的例子）下，**每个主题至少覆盖以下4个维度的信源分类**：

  - 官方一手（披露/公告/标准/公司官方）
  - 专业解读（研究机构/头部媒体/行业智库）
  - 产业一线（工程/产品/开源/团队博客）
  - 发现&早期信号（社区/聚合/榜单）
- **每个维度下至少 N 个活跃信源（例如 ≥30）**，且有“不同机构、不同形态”的组合

#### 2.2 高质量（Quality）

**高质量**：信源在目标主题上可持续提供“有信息增量的信号”，即对目标用户的问题有用，并且稳定。

- **负向体验-可用性**：如该信源频繁反爬、不可访问，会直接降低用户体验（没更新/断流）。评估视角，用该信源的接口返回更新内容的成功率来衡量。
- **正向体验-信息增量**：在同一主题下，该信源在近一周内提供的“新增观点/新增事实/新增数据点”对比同占比更高。评估视角，后续需要人工来抽样验证是该信源对主题来说“有增量”，在主题下一周内的更新的信源中，这个信源有增量的单条item的比例占多少
- **正向体验-权威性**：该信源是实体（人、产品、公司、机构）的官方信源，是为1，否为0；当用户关注的对象直接为一个实体时，这一得分当大大加权
- **正向体验-时效性**：在不同信源中都提炼出了相同的主题更新时，谁更新时间越早，谁就得分越早，时效性就更高
- **正向体验-最相关**：在同一主题下，该信源对比其他信源，最近3天的更新内容全部围绕着主题  
在实现层，我们需要定义一个信源质量分 **“Source Quality Score”，是针对不同的主题计算的，这样，更有概率推出最相关的、让人体感非常高质量的信源，得分如下：**  
`SQ = 可用性X(0.35*信息增量 + 0.25*最相关 + 0.2*权威性 + 0.2*时效性`）![](https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=YWMzNDI4MTE3ZDZlYmQ5ZDVkNDZjNGYwODQ5NzczYjFfNTc3ZTExZGU0ZjdlODlhOWE5ZmUwYjEzY2FmYTdhZTBfSUQ6NzU4NjMxNDI0MDI2NTQ1NzE3M18xNzc5MDkwOTg5OjE3NzkwOTQ1ODlfVjM)

#### 2.3 可信（Trust）

**定义**：用户能够理解信源的发布者是谁，信源主要是什么立场输出什么样的内容的  
**落地要求**：

- 信源能被解释：主体是谁、为何发布、内容是什么类型
- 官方一手的信源，必须是官方权威的站点



---

## 信源库的生产与治理

#### 3.1 生产链路

待讨论<cite type="user" user-id="ou_155693910c32212e24f818a8a7b982d1"></cite><cite type="user" user-id="ou_e31dc3cd719d183d6f466669258247fc"></cite>，初步的想法：基于分类对应的种子信源，进行扩展抓取；然后计算出质量分后过滤出较好的信源，同时需要设计出信源的状态，如果失效的需要做下线、如果是网站点长久不更新，但原本的更新频率就很低的，不需要下线，但一定要保留手动纠错的能力，比如对已下线的进行复活；也要看是否要对类似的信源站点出合并。更结构化的方案由技术来产出

#### 3.2 字段需求

字段要服务两个目标：**冷启动推荐与解释**、**未来形态化阅读适配**，以及第三个隐性目标：**扩容治理**。

<table><colgroup><col/><col/><col/><col/></colgroup><tbody><tr><td><b>序号</b></td><td><b>字段名</b></td><td><b>字段说明</b></td><td><b>字段分类作用说明</b></td></tr><tr><td>1</td><td><code>source_id</code></td><td>唯一ID</td><td rowspan="7"><b>信源的基础字段，唯一ID、归一化、类型</b></td></tr><tr><td>2</td><td><code>name</code></td><td>展示名</td></tr><tr><td>3</td><td><code>logo_url</code></td><td>信源图标</td></tr><tr><td>4</td><td><code>canonical_url</code></td><td>信源页面</td></tr><tr><td>5</td><td><code>source_type</code></td><td>信源类型，有限可穷举值<br/>website / blog / newsletter / podcast / filing_feed / paper_repo / forum / repo / aggregator</td></tr><tr><td>6</td><td><code>formats</code></td><td>html / pdf / filing / paper / newsletter / forum / repo / dataset / api</td></tr><tr><td>7</td><td><code>reading_template</code></td><td>按信源类型做成不同的默认阅读模版类型</td></tr><tr><td>8</td><td><code>theme_tags</code></td><td>主题标签多个</td><td rowspan="7"><b>对于信源的理解，用于匹配与解释</b></td></tr><tr><td>9</td><td><code>audience_fit</code></td><td>适用人群，值为：<br/>internet_practitioner / investor / both</td></tr><tr><td>10</td><td><code>source_summary</code></td><td>一句话描述，谁（主体）出于什么目的，做什么主题，什么内容形态</td></tr><tr><td>11</td><td><code>publisher_name</code></td><td>信源发布者，主体名（人/公司/机构/平台）</td></tr><tr><td>12</td><td><code>publisher_type</code></td><td>person / company / institution / platform / community</td></tr><tr><td>13</td><td><code>recent_topic_snapshot</code></td><td>基于最近3条内容的主题标签+权重（例如：{AI Agent 0.6, Infra 0.3, 投资 0.1}）</td></tr><tr><td>14</td><td><code>snapshot_generated_at</code></td><td>最近这3内容的主题标签的生成时间</td></tr><tr><td>15</td><td><code>authority_signals</code></td><td>信源的权威性字段<ul><li>是否官方（is_official）</li><li>是否同行评审/顶会（is_peer_reviewed / venue_tier）</li><li>机构类型（institution_type）</li><li>历史年限（years_active）</li></ul></td><td rowspan="3"><b>信源质量相关</b></td></tr><tr><td>16</td><td><code>perspective_type</code></td><td><u>official_primary / academic / thinktank_research / operator_vc / media / aggregator / community</u></td></tr><tr><td>17</td><td><code>source_quatity_score </code></td><td>信源质量分</td></tr><tr><td>18</td><td><code>last_success_at</code></td><td>最近一次成功抓取时间</td><td rowspan="2"><b>抓取与可用性</b></td></tr><tr><td>19</td><td><code>status</code></td><td>active / degraded / blocked / dead</td></tr><tr><td>20</td><td><code>seed_source</code></td><td>从哪里发现（种子信源/扩展/用户提交）</td><td><b>用于未来的分类</b></td></tr></tbody></table>

---

## 信源种子库（真实链接，按人群组织）

> 这份种子库的目标不是“全量”，而是做 **高权威 + 高覆盖 + 可扩展** 的种子信源。后续扩容可以从这些源的 sitemap/RSS/友情链接/引用网络继续滚雪球。



### 4.1 金融投资人（Investor）种子库

**公司披露 / 交易所公告（官方一手）**

- SEC EDGAR： [https://www.sec.gov/edgar/search/](https://www.sec.gov/edgar/search/?utm_source=chatgpt.com)
- HKEXnews： [https://www.hkexnews.hk/index.htm](https://www.hkexnews.hk/index.htm?utm_source=chatgpt.com)
- HKEXnews 标题检索： [https://www1.hkexnews.hk/search/titlesearch.xhtml](https://www1.hkexnews.hk/search/titlesearch.xhtml?utm_source=chatgpt.com)
- SGX Company Announcements： [https://www.sgx.com/securities/company-announcements](https://www.sgx.com/securities/company-announcements?utm_source=chatgpt.com)
- 上交所公告： [https://www.sse.com.cn/disclosure/listedinfo/announcement/](https://www.sse.com.cn/disclosure/listedinfo/announcement/?utm_source=chatgpt.com)
- 巨潮资讯： [https://www.cninfo.com.cn/](https://www.cninfo.com.cn/?utm_source=chatgpt.com)

**宏观与数据（数据门户）**

- FRED： [https://fred.stlouisfed.org/](https://fred.stlouisfed.org/?utm_source=chatgpt.com)
- IMF Data： [https://www.imf.org/en/data](https://www.imf.org/en/data?utm_source=chatgpt.com)  （以及 [https://data.imf.org/](https://data.imf.org/?utm_source=chatgpt.com) ）
- World Bank Open Data： [https://data.worldbank.org/](https://data.worldbank.org/?utm_source=chatgpt.com)
- BIS Data Portal： [https://data.bis.org/](https://data.bis.org/?utm_source=chatgpt.com)

**研究与工作论文（证据链补强）**

- SSRN： [https://www.ssrn.com/](https://www.ssrn.com/?utm_source=chatgpt.com)
- NBER Papers： [https://www.nber.org/papers](https://www.nber.org/papers?utm_source=chatgpt.com)

**投资/操盘手视角（判断与框架）**

- a16z： [https://a16z.com/](https://a16z.com/?utm_source=chatgpt.com)
- Sequoia Stories： [https://www.sequoiacap.com/stories/](https://www.sequoiacap.com/stories/?utm_source=chatgpt.com)
- YC Blog： [https://www.ycombinator.com/blog](https://www.ycombinator.com/blog?utm_source=chatgpt.com)
- Oaktree Insights： [https://www.oaktreecapital.com/insights](https://www.oaktreecapital.com/insights?utm_source=chatgpt.com)

**聚合与商业分析（快速扫盘）**

- Techmeme： [https://techmeme.com/](https://techmeme.com/?utm_source=chatgpt.com)
- Stratechery： [https://stratechery.com/](https://stratechery.com/?utm_source=chatgpt.com)
- Benedict’s Newsletter： [https://www.ben-evans.com/newsletter](https://www.ben-evans.com/newsletter?utm_source=chatgpt.com)

---

### 4.2 互联网从业者（Internet Practitioner）种子库

**论文/评审/索引（源头创新）**

- arXiv： https://arxiv.org/
- OpenReview： [https://openreview.net/](https://openreview.net/?utm_source=chatgpt.com)
- Semantic Scholar： [https://www.semanticscholar.org/](https://www.semanticscholar.org/?utm_source=chatgpt.com)
- OpenAlex： [https://openalex.org/](https://openalex.org/?utm_source=chatgpt.com)

**大厂工程实践（官方工程博客）**

- Netflix TechBlog： [https://netflixtechblog.com/](https://netflixtechblog.com/?utm_source=chatgpt.com)
- Uber Engineering： [https://www.uber.com/en-US/blog/engineering/](https://www.uber.com/en-US/blog/engineering/?utm_source=chatgpt.com)
- Cloudflare Blog： [https://blog.cloudflare.com/](https://blog.cloudflare.com/?utm_source=chatgpt.com)
- OpenAI News： [https://openai.com/news/](https://openai.com/news/?utm_source=chatgpt.com)
- OpenAI Developer Blog： [https://developers.openai.com/blog/](https://developers.openai.com/blog/?utm_source=chatgpt.com)

**社区与趋势（发现与早期信号）**

- Hacker News： [https://news.ycombinator.com/](https://news.ycombinator.com/?utm_source=chatgpt.com)
- GitHub Trending： [https://github.com/trending](https://github.com/trending?utm_source=chatgpt.com)
- Hugging Face Papers： [https://huggingface.co/papers](https://huggingface.co/papers?utm_source=chatgpt.com)
- Hugging Face Trending Papers： [https://huggingface.co/papers/trending](https://huggingface.co/papers/trending?utm_source=chatgpt.com)

**产品/创业发现**

- Product Hunt： [https://www.producthunt.com/](https://www.producthunt.com/?utm_source=chatgpt.com)
- YC Requests for Startups： [https://www.ycombinator.com/rfs](https://www.ycombinator.com/rfs?utm_source=chatgpt.com)

---

## 信源的分类

### 5.1 三个字段的关系

<sheet sheet-id="TnMVq8" token="F7yws1IAZh8O2jtAW6njGHlIp9X"></sheet>

source_tier 判断可信层级

source_origin 判断具体出处类别

source_type 判断信息载体形式

每一个具体的信源我们需要展示source_type 和 origin

### 5.2 source_type：信源的形态

`source_type` 不决定一手程度，它只描述载体形态。

<sheet sheet-id="C2QsEq" token="F7yws1IAZh8O2jtAW6njGHlIp9X"></sheet>

### 5.3 source_tier：信源层级

<sheet sheet-id="84a2mB" token="F7yws1IAZh8O2jtAW6njGHlIp9X"></sheet>

### 5.4 source_origin：信源出处 

提取规则有名的标记具体的公司名称，不知名的标记 分类名称

比如openAI官网标记：OpenAI Website，其他公司官网标记 Company Website

<sheet sheet-id="jhTDgF" token="F7yws1IAZh8O2jtAW6njGHlIp9X"></sheet>

### 5.5 三个字段组合示例

<sheet sheet-id="iAPAMq" token="F7yws1IAZh8O2jtAW6njGHlIp9X"></sheet>

#### 5.5.1 对一级市场投资人的意义

一级市场投资人使用 Rimbo，不是为了看更多新闻，而是为了更早发现机会、更快判断真假、更系统地做赛道跟踪。

他们关心的问题通常是：

```Plain Text
这个方向有没有投资机会？
哪些公司正在冒头？
谁在融资？
技术是否真的成熟？
市场是不是已经开始验证？
团队和组织有没有变化？
这个信号是事实、观点，还是噪音？
```

因此，三个标签对投资人的交付价值如下。

---

##### source_tier：帮助投资人区分“投资证据强弱”

对投资人来说，最重要的是区分：

<sheet sheet-id="eUxC1l" token="F7yws1IAZh8O2jtAW6njGHlIp9X"></sheet>

对投资人的具体价值

`source_tier` 可以帮助投资人避免把不同层级的信息混在一起。

<sheet sheet-id="DeBGhg" token="F7yws1IAZh8O2jtAW6njGHlIp9X"></sheet>

所以对投资人来说，`source_tier` 的交付意义是：

> 帮他们判断一个信号在投资决策中的证据权重。

---

##### source_origin：帮助投资人知道“信号来自哪类出处”

投资人不会只问“信息可信吗”，还会问：

```Plain Text
这个信号是从融资数据库来的？
是从公司官网来的？
是从招聘平台来的？
是从专业媒体来的？
还是从社区讨论来的？
```

<sheet sheet-id="OAYYLl" token="F7yws1IAZh8O2jtAW6njGHlIp9X"></sheet>

对投资人的具体价值

`source_origin` 让 Rimbo 的交付从“新闻列表”变成“证据结构”。

比如用户问：

```Plain Text
AI Agent 投资机会怎么看？
```

Rimbo 交付时可以用标签保证信源池覆盖：

<sheet sheet-id="EhU69U" token="F7yws1IAZh8O2jtAW6njGHlIp9X"></sheet>

所以对投资人来说，`source_origin` 的交付意义是：

> 帮他们看到一个投资主题的证据链是否完整，而不是只看到单一类型的信息。

---

##### source_type：帮助投资人拿到适合尽调的提取结果

投资人面对不同载体时，需要的提取方式不同。

<sheet sheet-id="MI7Li0" token="F7yws1IAZh8O2jtAW6njGHlIp9X"></sheet>

所以对投资人来说，`source_type` 的交付意义是：

> 让 Rimbo 用不同阅读模板，把不同类型信源转换成可用于投资判断的要点。

---

#### 5.5.2 对互联网从业者的意义

互联网从业者使用 Rimbo，核心不是做投资决策，而是跟踪产品、技术、竞品、用户反馈和行业变化。

他们关心的问题通常是：

```Plain Text
这个产品/技术有没有新变化？
竞品发布了什么？
开发者社区怎么看？
这个工具是否真的被采用？
用户吐槽点是什么？
哪些能力可以借鉴到自己的产品里？
```

因此，三个标签对互联网从业者的交付价值不同。

---

##### source_tier：帮助从业者判断“信息应该怎么用”

对互联网从业者来说，`source_tier` 的意义不是投资证据权重，而是帮助他们判断这条信息的使用方式。

<sheet sheet-id="ynypJT" token="F7yws1IAZh8O2jtAW6njGHlIp9X"></sheet>

对从业者的具体价值

比如一个从业者关注：

```Plain Text
AI coding agent
```

不同 `source_tier` 的意义是：

<sheet sheet-id="WJMgQC" token="F7yws1IAZh8O2jtAW6njGHlIp9X"></sheet>

所以对从业者来说，`source_tier` 的交付意义是：

> 帮他们区分“正式发布、专业解释、真实采用、用户反馈”四种不同信息价值。

---

##### source_origin：帮助从业者知道“从哪里观察产品和技术变化”

互联网从业者非常依赖具体出处，因为不同出处代表不同观察角度。

<sheet sheet-id="h3cPUV" token="F7yws1IAZh8O2jtAW6njGHlIp9X"></sheet>

对从业者的具体价值

`source_origin` 能让 Rimbo 给出的 Channel 更像一个工作流，而不是信息流。

比如用户创建：

```Plain Text
Developer Tools Channel
```

系统可以按 origin 组织来源：

<sheet sheet-id="yruO9d" token="F7yws1IAZh8O2jtAW6njGHlIp9X"></sheet>

所以对从业者来说，`source_origin` 的交付意义是：

> 帮他们按工作场景观察产品、技术、生态和用户反馈。

---

##### source_type：帮助从业者获得更可读的产品/技术摘要

从业者对不同载体的阅读需求也不同。

<sheet sheet-id="qxBkRk" token="F7yws1IAZh8O2jtAW6njGHlIp9X"></sheet>

所以对从业者来说，`source_type` 的交付意义是：

> 让 Rimbo 根据内容形态输出更适合工作的摘要，而不是把所有来源都压成同一种新闻摘要。

---

### 5.6 两类用户的差异总结

<sheet sheet-id="cbJFbg" token="F7yws1IAZh8O2jtAW6njGHlIp9X"></sheet>





6.旧表（作废）

<table><colgroup><col/><col/><col/><col/><col/><col/><col/><col/><col/></colgroup><tbody><tr><td>类别</td><td>优先级</td><td>对应具体信源名称</td><td>举例</td><td>覆盖率</td><td>免费可获取比例</td><td>技术问题</td><td>特点</td><td>用户需求</td></tr><tr><td rowspan="4">一手原始数据层（最高可信）</td><td>P0</td><td><ul><li>公司官方文件（Official Filings）<ul><li>Earnings Call </li><li>重大事件披露（Corporate Announcements）</li><li>财务报表（Financial Report）</li></ul></li></ul></td><td></td><td>季度，每年4次</td><td>美股免费（SeekingAlpha等），A股交易所官网免费</td><td></td><td>一手，高信号，管理层的真实意图</td><td><ol><li>利用模型识别管理层在回答中的语气波动，回避和潜台词</li><li>对比历次 Earnings Call 的措辞变化，判断战略转向</li></ol></td></tr><tr><td>P0</td><td>监管披露（Regulatory Disclosures）</td><td>FRED、SEC（8-K/13F/S-1）、FOMC声明原文</td><td>实施 月度</td><td>免费</td><td></td><td>强制披露，法定一手，时效性强</td><td><ol><li>不经媒体过滤，直接读原始文件自己判断</li></ol></td></tr><tr><td>P0</td><td>研究论文（Research &amp; Papers）</td><td>ArXiv、SSRN Pre-print</td><td>实时</td><td>免费</td><td></td><td>领先大众1-3个月，前瞻性、未经媒体二次加工</td><td><ol><li>论文太长太专业，希望直接提炼"这个研究对我的决策意味着什么"</li></ol></td></tr><tr><td>P0</td><td>专家访谈（Podcast）</td><td>深度采访类节目Acquired、The Knowledge Project 嘉宾直接表达一手经验，未经加工过的内容</td><td>实时</td><td>免费</td><td></td><td>长内容、专家级</td><td><ol><li>嘉宾的一手经验判断 &gt; 媒体报道，但埋在大量对话里</li></ol></td></tr><tr><td rowspan="2">聚合层（高可信，有门槛）</td><td>P2</td><td>官方新闻 （Premium News）</td><td>WSJ、Semaphore</td><td>实时</td><td>部分付费</td><td></td><td>专业、有门槛、经过编辑把关</td><td><ol><li>阅读门槛高，希望直接获取核心结论而不用全文阅读</li></ol></td></tr><tr><td>P0</td><td>专业评述（Professional Commentary）</td><td>深度分析的文章/播客Stratechery、The Information </td><td>每周</td><td>部分付费</td><td>是否可以一个人订阅然后中心抓取？</td><td>独立视角、战略层判断、作者有长期信誉背书</td><td><ol><li>内容密度高但篇幅长，希望快速提取核心框架</li><li>付了钱但看不完，希望兑现订阅价值</li></ol></td></tr><tr><td rowspan="4">社区信号层（早期但需过滤）</td><td>P0</td><td>投融资动态（Deal Tracker）</td><td>AI费道、Crunchbase、IT桔子、PitchBook</td><td>实时</td><td>免费</td><td></td><td>一级市场信号、比媒体报道早</td><td><ol><li>第一时间知道谁融了钱、谁投的、估值多少</li><li>识别连续出现的投资方——某个 LP 反复出现意味着什么趋势</li><li>中美市场融资信号交叉对比</li></ol></td></tr><tr><td>P2</td><td>从业者动态（Industry Insiders）</td><td>LinkedIn 招聘岗位变化 → 反推公司战略方向<br/>Glassdoor 评分骤降 = 内部有问题的早期预警<br/>Blind 上的匿名讨论往往比官方声明早3-6个月</td><td>实时</td><td>部分付费</td><td></td><td>组织内部信号、反映真实战略意图</td><td><ol><li>某公司核心团队大量离职是重要预警；人才从大厂流向某赛道 = 新兴机会信号</li><li>关注发布在这些平台上的重要言论</li></ol></td></tr><tr><td>P0</td><td>独立观点（Independent Voices）</td><td>Substack KOL、X列表</td><td>实时</td><td>部分付费</td><td></td><td>无机构立场、判断灵活、早于主流媒体</td><td><ol><li>筛选真正有判断力的 KOL，而不是跟风转发的噪音</li><li>同一事件多个独立观点聚合</li><li>X列表需要用户自己维护，希望 Rimbo 帮助管理和更新</li></ol></td></tr><tr><td>P0</td><td>技术社区（Developer Community）</td><td>GitHub Stars、Reddit、X上的知名科技社区</td><td>实时</td><td>部分付费</td><td></td><td>早期信号、情绪化但方向真实</td><td><ol><li>需要过滤情绪噪音，提取真实的方向性判断</li><li>新技术不希望还需要自己进一步执行</li><li>判断一项技术是否真的在被工程师采用，而不只是媒体炒作</li></ol></td></tr><tr><td>个人资产层（用户独有）</td><td>个性化agent层面</td><td>私有信源（My Sources）</td><td>用户自己的 Notion 数据库，用户付费订阅的 Newsletter（The Information、Stratechery）用户已有的 RSS 订阅列表</td><td></td><td></td><td></td><td>高度个性化、用户已付费、与用户关注方向强匹配</td><td><ol><li>已经订了很多但分散，希望统一管理</li><li>不同 Newsletter 之间的观点冲突需要帮助识别</li><li>更加个性化，且把已经付费的内容价值真正兑现</li></ol></td></tr><tr><td></td><td>个性化agent层面</td><td>收藏（Saves）</td><td>用户标记的高价值条目、保存的信号、评论</td><td></td><td></td><td></td><td>用户主动确认的高质量信号，是个人判断的显式表达</td><td><ol><li>标注过的信号应该影响后续推送方向</li><li>积累成个人的"信号数据库"，可以回溯和检索，与 Notion 双向同步——在 Rimbo 标注 = 自动写入 Notion 对应条目</li></ol></td></tr></tbody></table>