<!-- lark-mirror obj_token=IRxRdOfEXoSUOVxyZNaj6zITptc space=产品调研 synced=2026-05-18T07:54:44Z -->

<title>Skills 广场设计prd</title>

定位：冷启方案 重点是叉乘场景和人群

# 基本信息

| **时间** | **版本号** | **负责人** | **更新内容** |
|-|-|-|-|
| Apr/28/2026 | V1.0 | 产品 + 后端 | Skills 广场分类、筛选、详情页说明与示例 |

# 功能清单

| **功能模块** | **功能点** | **说明** |
|-|-|-|
| Skills   广场 | 浏览与搜索 skill | 搜索栏独占一行；按精选和主分类分组展示 skill 卡片。 |
| Skills   广场 | 分类与标签筛选 | 每个   skill 只有一个主分类，可同时拥有多个 tags；顶部 chips 用于快速筛选。 |
| Skills   广场 | 添加 / 已添加状态 | 未添加显示 +；已添加显示蓝色 check；支持默认开启 skill。 |
| 管理入口 | 右上角更多菜单 | 点击「⚙️」进入管理页面，用于管理已添加 skill。 |
| Skill   详情页 | 说明页结构 | 展示使用场景、Rimbo 关注点、示例提问和结果形式。 |
| Skill   详情页 | 试用与开关 | 支持开启/关闭 skill，并可从详情页直接在对话中试用。 |

# 详细规格说明

<table><colgroup><col/><col/><col/></colgroup><tbody><tr><td><b>功能模块</b></td><td><b>预览图</b></td><td><b>说明</b></td></tr><tr><td><b>Skills   广场</b></td><td><img name="image.png" crop="[0.000000,0.000000,1.000000,0.825000]" href="https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=MTY5NTc5YjYxYWEzNTg3NWFiYzFhZmVhY2RjMzgxYmFfZTYyOWY5ZGFhZmFiYTZkNTIxNzRiMGEyNjdkYzJmYmVfSUQ6NzYzMzc2NDUwMzkwMTIyODU2OF8xNzc5MDkxMDI2OjE3NzkwOTQ2MjZfVjM" mime="image/png" scale="0.163122" src="EvKubgzVEo8uSgxtYk1jQV7sp9e"/><img name="image.png" href="https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=YjRiZTI5NjI3NWM4ZWFjNTdhOWFmMDBkNDMwNjA0NzdfYmQzNDdkOWQ0M2VlMzY5MmU2Yjc0MDMwODUxMDNhMzRfSUQ6NzYzMzc1NjcxNjE5MDIwNzUxMl8xNzc5MDkxMDI2OjE3NzkwOTQ2MjZfVjM" mime="image/png" scale="1.000000" src="OrMPb92rlokJzExA1PfjjxippWg"/></td><td><ul><li>页面标题：让 Rimbo 按你的方式工作。</li><li>搜索栏：搜索栏单独占一行，placeholder   为「搜索 skill」。</li><li>顶部推荐卡：展示当前推荐的skill，包含名称，短描述和在对话中试用按钮，</li><li>右上角「⚙️」作为管理入口，跳转skills管理页面。</li><li>右上角上传标志是添加skills的入口，直接跳转本地的显示：</li></ul><img name="image.png" href="https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=ODZlNDI5NGEyOTk0Nzg2ODgxOWY4MWU1M2NiZmQzMTJfZDhkZGIxNjkzNGY2Y2U1ZTZkMWRkODIyNzI2M2YzYzdfSUQ6NzYzMzc2MTA4NTEwMjgwNDUwM18xNzc5MDkxMDI2OjE3NzkwOTQ2MjZfVjM" mime="image/png" scale="1.000000" src="Qh8ibuSNco2Li5xcplYjPrZFpQr"/><ul><li>列表按分组展示：精选、信息获取、尽调分析、管理层分析、研究报告、工作流辅助。</li><li>卡片右侧状态：已添加为蓝色 check，未添加为 +。</li></ul></td></tr><tr><td><b>Skill   详情页</b></td><td><img name="image.png" href="https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=MDkyODg0MWQzMzQ4MzI1YjY1YWJkMjQ3MjAxOWVkY2JfNWQ4MzdhN2Y4MDUxNGM1YWNmZWI5NDM2NDM4ZGRlZjJfSUQ6NzYzNDA5MjQ3NTI1NDA5OTQ4Ml8xNzc5MDkxMDI2OjE3NzkwOTQ2MjZfVjM" mime="image/png" scale="1.000000" src="C85lbor2boU18dxPrzJjDFBdpzg"/></td><td><ul><li>入口：用户点击任意 skill 卡片后，打开对应的 Skill 详情页 / 弹窗。 </li><li> Header 包含 skill 图标、skill 名称、skill 类型标签、一句话简介、启用开关、更多菜单和关闭按钮。 </li><li> Header 中的一句话简介用于快速说明该 skill 的核心用途，需用自然语言描述其解决的问题、依赖的信息和适用对象，避免写成内部配置说明。 </li><li> 内容模块固定顺序为：技能简介、核心能力、使用场景、快速开始、执行流程、输出结果。 </li><li> 「技能简介」用于说明该 skill 解决什么问题、主要依赖哪些信息、适合哪些用户或业务场景，建议使用一段完整文字，不使用分点。 </li><li> 「核心能力」用于展示 skill 的能力边界，使用编号列表展示 3–6 个核心能力，重点说明它能完成哪些明确任务，避免泛泛描述“智能分析”“深度洞察”。 </li><li> 「使用场景」用于说明用户在什么情况下应该使用该 skill，使用 bullet 展示具体触发场景，例如公司研究、产品定位、市场进入、竞品分析、内容整理等。 </li><li> 「快速开始」用于告诉用户如何调用该 skill，包括调用方式、输入要求和推荐问题格式。该模块需包含「如何调用」和「推荐问题格式」两个区域，帮助用户直接复制或改写后使用。 </li><li> 「执行流程」用于说明 Rimbo 在调用该 skill 后的工作步骤，以横向流程或步骤卡片展示，包括识别目标、收集信息、分析校验、结构化整理和输出结论等环节。 </li><li> 「输出结果」用于说明用户最终会得到什么，不写成笼统的“分析报告”，而是展示具体输出结构，例如主要玩家清单、对比表、格局地图、机会与风险分析、关键结论与建议。 </li><li> 页面底部左侧为「卸载 / 移除」按钮，右侧为主按钮「在对话中试用」。 </li><li> 用户点击「在对话中试用」后，可将该 skill 的推荐问题格式或示例 prompt 自动填入聊天输入框，也可直接进入对应 skill 的对话流程。 </li><li> 详情页文案应面向真实使用场景，保持专业、清晰、可执行；避免过度口语化、儿童化，也避免使用过多内部技术术语。 </li><li> 对于工具型 skill，可在「快速开始」中增加角色识别、配置要求和初始化步骤；对于分析型 skill，应重点展示分析维度、执行流程和输出结构；对于内容生成型 skill，应重点展示输入要求、生成格式和可交付结果。 </li><li> 若 skill 信息较多，详情页支持纵向滚动；核心模块仍需保持固定顺序，保证不同 skill 的阅读结构一致。 </li></ul></td></tr><tr><td><b>Skills 管理页面</b></td><td><img name="image.png" href="https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=N2Q1NTIxMjdmNjU0MzIxN2EzMzlmOTYxYjlmZThmNDBfNWIwNjBjYjI5MWFiOTJhN2VlZjU5Y2I5ZGM2MWFlZDhfSUQ6NzYzMzc0NjMxOTAwMjk2MzQ3OV8xNzc5MDkxMDI2OjE3NzkwOTQ2MjZfVjM" mime="image/png" scale="1.000000" src="JEyZbOYDEo9G5yxEgncjsYHRpjd"/><br/>这个是codex的图 可参考</td><td><ul><li>入口：用户在 Skills 广场右上角点击「⚙️」进入管理页面。</li><li>页面顶部保留搜索框，支持按 skill 名称和描述搜索。</li><li>顶部 tab 展示分组和数量，例如：插件 7、应用 0、MCP 0、技能 27；当前需求重点落在「技能」管理。</li><li>列表项包含 skill 图标、名称、简短描述和右侧启用开关。</li><li>开关打开表示该 skill 已启用，可在对话和侧边栏相关入口中使用；关闭表示暂时停用，但不删除配置。</li><li>用户点击列表项可进入 skill 详情页，查看使用说明、示例提问和试用入口。</li><li>管理页主要服务于已添加/已启用 skill 的集中维护，不承担新 skill 发现；新 skill 发现仍在 Skills 广场完成。</li></ul></td></tr></tbody></table>

# 分类定义



| **分类** | **用户意图** | 用户在做什么 | **覆盖用户群** |
|-|-|-|-|
| **CAT-A** | **信息追踪** | 我想实时了解某个领域 / 人物 /   公司的最新动态 | 科技爱好者、媒体人、投资人、研究人员 |
| **CAT-B** | **深度分析** | 我想搞清楚一件事的来龙去脉，形成自己的判断 | 研究人员、分析师、媒体人、投资人 |
| **CAT-C** | **信号识别** | 我想从信息噪音中找到真正重要的、别人没注意到的信号 | 投资人、记者、资深分析师 |
| **CAT-D** | **内容生产** | 我需要把信息整理成可以发出去 / 交付的东西 | 媒体人、研究人员、分析师、产品经理 |
| **CAT-E** | **工作流** | 我需要在日常工作中更高效，不针对特定分析任务 | 所有用户 |

# 核心设计原则

分类的目的是帮助用户找到正确的 skill，而不是给 skill 贴标签。因此分类标准以用户的使用动机（intent）为第一判断维度，而非 skill 的技术实现方式或内容主题。

- P1 · 唯一主分类：每个 skill 有且仅有一个 primary_category，主列表中只在一个分类下出现。
- P2 · 分类基于 intent，不基于 output：判断分类时看用户在什么场景下需要它，而不是它生成什么内容。



## 分类判定逻辑

## 新 Skill 上架判断流程

新 Skill 进入评审

        │

        ▼

Q1: 主要功能是「持续监控 / 实时追踪」某个对象的动态变化？

        │

    YES  ──────────────► CAT-A · 信息追踪

        │

       NO

        ▼

Q2: 核心价值是从语言/行为中识别隐藏信号（回避、矛盾、异常）？

        │

    YES  ──────────────► CAT-C · 信号识别

        │

       NO

        ▼

Q3: 主要价值是生成「可对外交付的文档或报告」？

        │

    YES  ──────────────► CAT-D · 内容生产

        │

       NO

        ▼

Q4: 对特定对象做结构化深度分析，形成判断？

        │

    YES  ──────────────► CAT-B · 深度分析

        │

       NO

        ▼

                          CAT-E · 工作流



### **精选（Featured）— 6 个**

人工挑选使用频率最高的 6 个，在广场顶部常驻展示，不受分类筛选影响。

|   | **Skill 名称** | **所属分类** | **适合谁用 / 一句话说明** |
|-|-|-|-|
| ⭐ | 行业扫描 | CAT-A | 科技爱好者、媒体人、投资人 — 快速了解一个行业今天发生了什么 |
| ⭐ | 竞争地图 | CAT-B | 产品经理、分析师、投资人 — 快速看清一个赛道里谁在做什么、各自优劣势 |
| ⭐ | 深度分析 | CAT-B | 研究人员、媒体人 — 对一个话题做系统性梳理，形成有结构的判断 |
| ⭐ | 管理层访谈分析 | CAT-C | 投资人、记者 — 听完一段采访/电话会，找出表面之下真正的信号 |
| ⭐ | 事件追踪 | CAT-A | 所有用户 — 持续监控某  <br/>**CAT-A · 信息追踪 — 4 个**  <br/>   <br/>个人/公司/话题的最新动态，不错过重要更新 |
| ⭐ | 长文报告 | CAT-D | 研究人员、媒体人、分析师 — 把调研结果整理成结构清晰的长篇报告 |

### **CAT-A 信息追踪 — 4 个**

| **Skill 名称** | **一句话说明** |
|-|-|
| 行业扫描 | 输入一个行业关键词，Rimbo 帮你扫描今天这个领域最值得关注的动态 |
| 事件追踪 | 持续监控某个人/公司/话题，有新动态时自动整理成摘要 |
| 政策雷达 | 追踪某个领域的政策动向，适合需要了解监管环境的用户 |
| 技术趋势追踪 | 追踪某项技术（如 AI、量子计算）的最新研究和产品进展，适合科技爱好者和研究人员 |

### **CAT-B 深度分析 — 5 个**

| **Skill 名称** | **一句话说明** |
|-|-|
| 竞争地图 | 输入一个赛道或公司，快速看清主要玩家、各自定位和竞争格局 |
| 深度分析 | 对一个话题或公司做系统性深度梳理，适合需要形成完整判断的场景 |
| 商业模式拆解 | 拆解一家公司的商业模式，理解它怎么赚钱、护城河在哪、风险是什么 |
| 风险评估 | 系统性识别某个标的/方向的主要风险，并按严重程度排序 |
| 技术验证 | 验证一项技术的真实成熟度，区分媒体炒作和实际落地进展 |

###  **CAT-C 信号识别 — 5 个**

| **Skill 名称** | **一句话说明** | **Tags** | **原对应** |
|-|-|-|-|
| 管理层访谈分析 | 听完一段采访或电话会，找出表面表述背后真正的信号和隐藏意图 | 信号识别, 定性判断 | 管理层访谈分析 |
| 回避与矛盾识别 | 分析一段对话或文本，找出被刻意回避的问题和前后矛盾的表述（合并原「结构性回避识别」+「数字一致性校验」） | 信号识别, 对比分析 | 合并2个 |
| 叙事结构拆解 | 拆解一段表述的叙事逻辑，识别信息优先级和刻意强调/淡化的内容 | 信号识别, 定性判断 | 叙事结构拆解 |
| 承诺兑现追踪 | 追踪某人/机构历史上做出的承诺，对比实际兑现情况，评估可信度趋势 | 对比分析, 投后管理 | 承诺兑现追踪 |
| 创始人画像 | 基于公开信息和一手表述，形成对一位创始人能力、性格和决策风格的立体判断 | 定性判断, 人物分析 | 创始人画像 |

### **CAT-D 内容生产 — 4 个**

| **Skill 名称** | **一句话说明** |
|-|-|
| 长文报告 | 把调研信息整理成结构清晰的长篇报告，适合需要对外输出的场景 |
| 竞对分析报告 | 生成一份结构化的竞品对比报告，适合产品、投资、媒体等多种场景使用 |
| 观点文章 | 基于你提供的信息和观点，生成一篇结构清晰、有立场的分析文章，适合媒体人和独立作者 |
| 摘要与简报 | 把长篇内容（报告、采访、文章）压缩成关键信息摘要，适合快速消化大量资料 |

### **CAT-E 工作流 — 2 个**

| **Skill 名称** | **一句话说明** |
|-|-|
| 追问 | 在任意对话中激活，帮你从不同角度追问同一个问题，找到你没想到的切入点 |
| 定期行业简报 | 设置一个行业或话题，Rimbo 按你设定的频率自动生成最新简报 |

**灰色地带处理规则**

- 如果一个 skill 在 Q3 和 Q4 都答 YES（既做信息收集也做尽调判断），看哪个环节占 skill prompt 的比重更大，比重大的为主分类。
- 如果一个skills运行不了，



# Skill 详情说明页内容规范

### 设计原则

Skill 详情页不是简单的功能介绍，也不是面向用户的教学卡片。它的目标是让用户快速判断：

1.  这个 skill 解决什么问题 
2.  它有什么核心能力 
3.  适合什么场景使用 
4.  用户应该如何启动它 
5.  Rimbo 会按什么流程执行 
6.  最终会生成什么结果 

### 模块定义

<sheet sheet-id="IRHIA5" token="B8phs3ceQhDPzgtJF8Cjm8MUpqh"></sheet>

详情页文案应保持专业、清晰、可执行，避免过度口语化，也避免堆砌内部技术实现。

Skill 详情页示例：竞争地图

![](https://internal-api-drive-stream-sg.larksuite.com/space/api/box/stream/download/authcode/?code=NTVkMGRhYzgxODBiYjQyNTg1ZmNlZDI2ODVjN2Y2MWJfMGEyMWZlNTQzMDBjY2UxZjU0OWExZDgyMGFhY2VmMzVfSUQ6NzYzNDA5Mjg2MTgwMTMzNjM0Nl8xNzc5MDkxMDI2OjE3NzkwOTQ2MjZfVjM)

**竞争地图**

帮助你快速识别一个行业或市场中的主要玩家、竞争关系、差异化位置和机会空白，适用于公司研究、产品策略、市场进入等场景。

---

技能简介

该技能通过收集公开信息、行业数据和产品资料，帮助用户快速梳理目标市场中的主要玩家、核心竞争关系与差异化位置，并在此基础上识别市场中的机会空白。它适用于创业者、产品经理、投资人、战略与市场团队，用于建立对竞争格局的整体认知。

---

核心能力

1. **主要玩家识别**：梳理目标市场中的核心公司、产品或替代方案。 
2. **竞争维度对比**：从用户、产品、商业模式、价格、渠道、增长方式等维度进行比较。 
3. **差异化定位分析**：识别各玩家的优势区域、空白带和潜在威胁。 
4. **机会空白发现**：发现尚未被充分满足的需求与可切入方向。 
5. **结构化输出**：将竞争格局整理为表格、分层地图和结论摘要。 

---

使用场景

-  想快速了解一个行业或赛道的竞争格局 
-  准备进入一个新市场，需要评估竞争强度和机会 
-  做竞品研究、产品定位、投资分析或战略规划 
-  需要把零散信息整理成清晰的竞争关系与对比结论 

---

快速开始

**如何调用**

在对话中直接描述你的研究对象和关注重点，Rimbo 会自动启动该技能。

**推荐问题格式**

帮我做一个【行业 / 产品 / 公司】的竞争地图，重点比较【主要玩家 / 维度 / 关注点】。

**示例问题**

帮我做一个 AI 搜索产品的竞争地图，对比 Perplexity、ChatGPT Search、Google AI Mode 和 You.com，重点看目标用户、产品能力、商业模式和差异化定位。

**输入建议**

建议尽量说明研究对象、关注维度和时间范围。例如：行业名称、目标市场、主要竞品、比较维度、是否需要最新信息。

---

执行流程

**理解研究目标**  
 Rimbo 会先识别你要研究的是行业、市场、产品方向，还是具体公司，并确认分析范围。 

**收集与筛选信息**  
 Rimbo 会从公开信息、行业资料与产品内容中提取相关玩家和关键线索。 

**分析与对比**  
 Rimbo 会建立合适的比较维度，分析不同玩家之间的竞争关系、定位差异和优劣势。 

**机会识别**  
 Rimbo 会识别市场中的空白区域、潜在威胁和可能的切入点。 

**输出结论**  
 Rimbo 会生成结构化结论和关键判断，帮助用户快速理解竞争格局。 

---

输出结果

你将得到一份结构化的竞争地图，通常包括：

**主要玩家清单**：列出市场中的核心玩家及简要信息 

**竞争对比表**：按关键维度对各玩家进行对比分析 

**竞争格局地图**：可视化呈现市场结构与玩家关系 

**机会与风险分析**：识别机会空白、潜在威胁与风险点 

**关键结论与建议**：总结核心洞察，并提出可执行建议 





# 前端实现注意事项

- 每个分类默认展示 6 个 skill（3 行 × 2 列），超出后点击「查看更多」展开；精选分组始终全部展示。
- enabled_by_default 的 skill 在用户首次进入时默认出现在侧边栏或已添加列表中。
- Skill 详情页的 example_prompt 后续可支持一键复制或直接填入聊天输入框。
- 详情页文案字段建议由后端下发，前端只负责固定模块渲染。