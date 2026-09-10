> 适用场景：面向 EU/US 用户设计个性化广告与个性化推荐功能时的合规框架
> 整理日期：2026-06-26
> 来源：agentic-rag 知识库 + 外部官方法规

---

## 一、核心法规全景

| 法域 | 法规 | 对个性化广告/推荐的核心约束 |
| --- | --- | --- |
| **欧盟** | GDPR | 处理个人数据需合法依据；画像与自动化决策受限；用户享有反对权 |
| **欧盟** | ePrivacy Directive | 追踪技术（Cookie/设备ID）需事先同意 |
| **欧盟** | DSA | 推荐系统透明度 + VLOP 必须提供非个性化选项；广告标识与信息库 |
| **欧盟** | DMA | 守门人跨服务合并数据须用户明确选择 |
| **欧盟** | AI Act | 推荐系统一般为有限风险，需透明度义务；特定场景可能升级为高风险 |
| **美国（加州）** | CCPA/CPRA | 用户有权退出"出售"和"共享"（跨上下文行为广告）；须响应 opt-out 信号 |
| **美国（联邦）** | COPPA | 13岁以下儿童：定向广告须家长同意；2025修订规则进一步限制 |
| **美国（联邦）** | FTC Act | 不得以不公平/欺骗性方式开展行为广告 |

---

## 二、用户数据处理阶段

### 2.1 合法处理依据（Legal Basis）

#### 欧盟（GDPR）

**结论：个性化广告/推荐涉及个人数据处理，必须具备 GDPR Art.6(1) 下的合法依据；实践中以"同意"为主流选择。**

| 要求 | 具体内容 | 判断 |
| --- | --- | --- |
| 同意标准 | 必须满足"自由给出、具体、知情、明确"四要素；同意请求须与其他事项明确区分 | ✅ 强制 |
| 撤回同意 | 用户可随时撤回，撤回与给出同等便捷 | ✅ 强制 |
| 合法利益替代 | GDPR Art.6(1)(f) 合法利益理论上可用于部分处理，但 EDPB 及多国 DPA 倾向于认为行为定向广告难以通过合法利益测试 | ⚠️ 高风险 |
| 画像（Profiling） | GDPR Art.4(4) 定义画像；Art.22 限制纯自动化决策；个性化推荐/广告通常构成画像 | ⚠️ 需评估 |

> **法条/原文出处**：GDPR Art.6 Lawfulness of processing &#124; [https://gdpr-info.eu/art-6-gdpr/](https://gdpr-info.eu/art-6-gdpr/)
> **原文**：Processing shall be lawful only if and to the extent that at least one of the following applies: (a) the data subject has given consent... **(f) processing is necessary for the purposes of the legitimate interests pursued by the controller...**

> **法条/原文出处**：EDPB Guidelines 1/2024 on legitimate interest &#124; [https://www.edpb.europa.eu/system/files/2024-10/edpb_guidelines_202401_legitimateinterest_en.pdf](https://www.edpb.europa.eu/system/files/2024-10/edpb_guidelines_202401_legitimateinterest_en.pdf)
> **原文**：Article 6(1)(f) GDPR provides a legal basis for the processing of personal data to the extent that **"processing is necessary for the purposes of the legitimate interests..."**

#### 美国（CCPA/CPRA）

**结论：加州采"退出"（opt-out）模式而非"选择加入"（opt-in）；但须提供明确的退出机制并响应自动化退出信号。**

| 要求 | 具体内容 | 判断 |
| --- | --- | --- |
| 退出权 | 用户有权退出个人信息的"出售"（sale）和"共享"（sharing） | ✅ 强制 |
| "共享"定义 | 特指为跨上下文行为广告（cross-context behavioral advertising）向第三方共享个人信息 | ✅ 强制 |
| Opt-out 信号 | 须响应浏览器/设备发出的 Global Privacy Control (GPC) 等退出偏好信号 | ✅ 强制 |
| "Do Not Sell or Share" 链接 | 首页须提供清晰可识别的退出链接 | ✅ 强制 |
| 16岁以下用户 | 13-16岁须 opt-in（本人或家长同意）；13岁以下须家长同意 | ✅ 强制 |

> **法条/原文出处**：CCPA/CPRA &#124; [https://oag.ca.gov/privacy/ccpa](https://oag.ca.gov/privacy/ccpa)
> **原文**：Consumers have the **right to opt-out of the sale or sharing of their personal information**. Sharing refers specifically to sharing **for cross-context behavioral advertising**.

---

### 2.2 追踪技术同意（Cookie / 设备ID / SDK）

**结论：欧盟 ePrivacy Directive 要求追踪技术须事先同意；美国 CCPA/CPRA 通过退出机制约束；COPPA 对13岁以下儿童严格限制。**

| 法域 | 要求 | 判断 |
| --- | --- | --- |
| **EU** | ePrivacy Directive Art.5(3)：除"绝对必要"cookie 外，所有追踪技术须获用户同意后方可设置 | ✅ 强制（opt-in） |
| **EU** | 同意须可在 cookie 墙上逐类别接受/拒绝，"全部拒绝"与"全部接受"同等显著 | ✅ 强制 |
| **US (CPRA)** | 追踪技术收集的个人信息纳入"共享"范围，适用退出机制 | ✅ 强制（opt-out） |
| **US (COPPA)** | 13岁以下：禁止第三方广告SDK从儿童设备采集数据；2025修订规则要求定向广告须家长 opt-in | ✅ 强制 |

> **法条/原文出处**：ePrivacy Directive Art.5(3) &#124; [https://gdpr.eu/cookies/](https://gdpr.eu/cookies/)
> **原文**：Receive users' consent before you use any cookies **except strictly necessary cookies**. Provide accurate and specific information about the data each cookie collects.

> **法条/原文出处**：FTC COPPA Final Rule (2025) &#124; [https://www.ftc.gov/news-events/news/press-releases/2025/01/ftc-finalizes-changes-childrens-privacy-rule-limiting-companies-ability-monetize-kids-data](https://www.ftc.gov/news-events/news/press-releases/2025/01/ftc-finalizes-changes-childrens-privacy-rule-limiting-companies-ability-monetize-kids-data)
> **原文**：The final rule **requires parents to opt in to third-party advertising** and includes other changes to address the emerging ways that consumers' data is collected and used.

---

### 2.3 数据最小化与目的限制

| 要求 | EU (GDPR) | US (CCPA/CPRA) |
| --- | --- | --- |
| 目的限制 | Art.5(1)(b)：收集时声明的目的限定，禁止二次利用 | 未直接要求，但数据保留最小化原则通过"合理必要"标准间接约束 |
| 数据最小化 | Art.5(1)(c)：仅收集达成目的所必需的数据 | CPRA 要求收集"与收集目的合理相关且必要比例"的数据 |
| 敏感数据 | Art.9：健康/宗教/种族等敏感数据原则上禁止用于广告定向 | CPRA 敏感个人信息须提供额外退出权 |

**内部知识库佐证**：

> **法条/原文出处**：《国际化未成年人数据收集使用政策》&gt; 三、数据处理 &gt; 3.1 处理目的限制 &#124; node_id=fd2c1dbfc23544ca8611a8d996a3491b
> **原文**：对未成年人数据，**只能基于收集时声明的目的进行处理**，禁止二次利用。&#124; 敏感数据用于广告定向（健康/宗教/种族等） &#124; ❌ **禁止** &#124;
> **链接**：[REDoc 原文](https://docs.xiaohongshu.com/doc/83a57dcefa2d36b45f37caacd1ea6b8a)

---

### 2.4 数据本地化与跨境传输

**结论：EU/US 用户行为数据与用户画像严禁回传中国服务器，必须本地闭环处理。**

> **法条/原文出处**：《用户数据跨境基本原则》&gt; 二、数据传输、访问原则 &gt; 5. EU/US绝对红线：严禁回传清单 &#124; node_id=46a9710b32b443f59336a94a47d79216
> **原文**：以下数据属于"高风险敏感资产"，严禁回传至中国服务器：**底层行为痕迹：** 搜索记录、点击流（Clickstream）、浏览历史、停留时长等能够构建个人画像的细节。**用户画像与标签：** 分析生成的偏好标签、宗教/政治倾向、消费能力评估。
> **链接**：[REDoc 原文](https://docs.xiaohongshu.com/doc/29f61e75b4e15daf57094752dd545457)

> **法条/原文出处**：《用户数据跨境基本原则》&gt; 五、已评估的具体业务场景规则 &gt; 搜推场景 &#124; node_id=9e44b664f41545138aad509477f14764
> **原文**：**算法无限制，但用户UBT数据必须本地存储，不得跨境。** 用户的原始行为明文必须存储在本地。严禁回传原始行为 Log。**用户画像禁止跨境传输存储，必须本地闭环。**
> **链接**：[REDoc 原文](https://docs.xiaohongshu.com/doc/29f61e75b4e15daf57094752dd545457)## 三、实际推送功能阶段

### 3.1 推荐系统透明度（DSA Art.27）

**结论：所有在线平台均须在条款中以通俗语言披露推荐系统主要参数；VLOP（&gt;4500万 EU 月活）须提供至少一种非个性化推荐选项。**

| 要求 | 适用对象 | 具体内容 | 判断 |
| --- | --- | --- | --- |
| 参数披露 | 所有在线平台 | 在条款中以通俗易懂的语言说明推荐系统使用的主要参数 | ✅ 强制 |
| 非个性化选项 | VLOP/VLOSE | 须提供至少一种非基于画像的推荐系统选项 | ✅ 强制（VLOP） |
| 用户控制 | 所有在线平台 | 用户可修改影响推荐的参数 | ✅ 强制 |

> **法条/原文出处**：DSA Art.27 Recommender systems &#124; [https://www.eu-digital-services-act.com/Digital_Services_Act_Article_27.html](https://www.eu-digital-services-act.com/Digital_Services_Act_Article_27.html)
> **原文**：Providers of online platforms that use recommender systems shall set out in their terms and conditions, **in plain and intelligible language**, the main parameters used... For very large online platforms... they shall offer **at least one option which is not based on profiling**.

> **法条/原文出处**：European Commission - DSA &#124; [https://digital-strategy.ec.europa.eu/en/policies/digital-services-act](https://digital-strategy.ec.europa.eu/en/policies/digital-services-act)
> **原文**：On large platforms with over 45 million monthly users in the EU, you can now **opt for non-personalised feeds**.

---

### 3.2 广告透明度（DSA Art.26 + Art.39）

**结论：在线平台须标识广告、披露广告主身份及投放参数；VLOP 须建立可公开访问的广告数据库。**

| 要求 | 适用对象 | 具体内容 | 判断 |
| --- | --- | --- | --- |
| 广告标识 | 所有在线平台 | 每条广告须清晰标识为"广告" | ✅ 强制 |
| 广告主披露 | 所有在线平台 | 须披露广告主身份 | ✅ 强制 |
| 投放参数 | 所有在线平台 | 须披露用于定向的主要参数 | ✅ 强制 |
| 广告数据库 | VLOP/VLOSE | 须建立可公开访问的广告存储库（Ad Repository），不含用户个人数据 | ✅ 强制（VLOP） |

> **法条/原文出处**：DSA Art.26 Advertising &#124; [https://www.admonsters.com/how-the-eus-digital-services-act-promotes-greater-ad-transparency/](https://www.admonsters.com/how-the-eus-digital-services-act-promotes-greater-ad-transparency/)
> **原文**：Clearly labeling advertisements. Disclosing the identity of the advertiser. Revealing the main parameters used to target the ad.

> **法条/原文出处**：DSA Art.39 Ad repository &#124; [https://www.eu-digital-services-act.com/Digital_Services_Act_Article_39.html](https://www.eu-digital-services-act.com/Digital_Services_Act_Article_39.html)
> **原文**：They shall ensure that the repository **does not contain any personal data** of the recipients of the service to whom the advertisement was or could have been shown.

---

### 3.3 守门人数据合并限制（DMA Art.5）

**结论：若被认定为"守门人"（Gatekeeper），跨服务合并个人数据用于个性化广告须获得用户明确选择。**

> **法条/原文出处**：DMA Art.5 &#124; [https://www.eu-digital-markets-act.com/Digital_Markets_Act_Article_5.html](https://www.eu-digital-markets-act.com/Digital_Markets_Act_Article_5.html)
> **原文**：Gatekeepers shall not combine personal data from the relevant core platform service with personal data from other services... **unless the end user has been presented with the specific choice** and has given consent.

---

### 3.4 个性化定义的灰色地带

**结论：DSA/ICO 立场是"任何使用个人历史行为数据的推荐均构成画像"，即使以"内容标签推荐"形式呈现。**

> **法条/原文出处**：《法律合规审查意见》&gt; 四、操作层面风险 &gt; 4.3 Early Teens的推荐系统"非个性化"定义需界定 &#124; node_id=b42b606f6fd04b3da53bb8ad3c69cba4
> **原文**：**DSA/ICO的立场是：任何使用个人历史行为数据的推荐均构成画像**，即使是"内容标签推荐"形式。**建议：** 不得使用该用户的任何历史行为数据，仅可使用当前会话的即时信号。
> **链接**：[REDoc 原文](https://docs.xiaohongshu.com/doc/27aaa860ba17c24b024c857b6e7f82ca)

---

### 3.5 AI 个性化功能风险分级

**结论：基于对话历史/行为数据的 AI 个性化属于最高风险，须控制数据使用范围，对未成年人默认关闭。**

> **法条/原文出处**：《国际化未成年AI功能合规意见》&gt; 四、各产品类型分析 &gt;（六）基于对话历史的个性化 &#124; node_id=338bead6f4054edf944917cbcc071353
> **原文**：**风险评级：最高。** 平台基于用户历史对话数据对AI的回答/交互进行个性化调整；属于对用户数据的二次利用。**建议：** 对未成年人默认关闭；历史对话数据不得用于模型训练。
> **链接**：[REDoc 原文](https://docs.xiaohongshu.com/doc/92ca4b4895a973344c7a8b94e760d31d)

> **法条/原文出处**：EU AI Act 风险分类 &#124; [https://artificialintelligenceact.eu/high-level-summary/](https://artificialintelligenceact.eu/high-level-summary/)
> **原文**：推荐引擎在 AI Act 下通常被归类为**有限风险**（Minimal/Limited risk），但须履行透明度义务；若涉及可能影响基本权利的关键决策场景，可能被归类为**高风险**。## 四、后续链路阶段

### 4.1 用户权利保障

| 权利 | EU (GDPR) | US (CCPA/CPRA) |
| --- | --- | --- |
| 知情权 | Art.13/14：收集时告知处理目的、合法依据、数据接收方等 | 须在隐私政策中披露收集类别、目的、接收方 |
| 访问权 | Art.15：用户可请求获取其个人数据副本 | 消费者有权知道收集了哪些个人信息 |
| 删除权 | Art.17：用户可请求删除其个人数据 | 消费者有权删除个人信息 |
| 反对/退出权 | Art.21：用户可反对基于合法利益的处理（含直接营销） | 消费者有权退出"出售"和"共享" |
| 撤回同意 | Art.7(3)：随时撤回，与给出同等便捷 | 13-16岁 opt-in 可撤销 |
| 自动化决策反对权 | Art.22：用户有权不受纯自动化决策约束（含画像） | CCPA 限制自动化决策中使用敏感信息 |

> **法条/原文出处**：GDPR Art.22 &#124; [https://gdpr.algolia.com/gdpr-article-22](https://gdpr.algolia.com/gdpr-article-22)
> **原文**：The data subject shall have the right not to be subject to a decision based solely on **automated processing, including profiling**, which produces legal effects concerning him or her.

### 4.2 数据保留与删除

| 要求 | EU | US |
| --- | --- | --- |
| 保留期限 | 不得超过实现处理目的所必需的时间 | 保留期限应与收集目的合理相关 |
| 删除义务 | 目的实现后或用户撤回同意/反对后须删除 | 用户行使删除权后须删除并通知下游 |
| 画像数据 | 用户退出个性化后，基于行为数据构建的画像须停止使用/删除 | 用户退出后须停止共享用于行为广告的数据 |

> **法条/原文出处**：《rednote 隐私协议版本管理表》&gt; 20260323 更新记录 &gt; 6. 数据保留期限 &#124; node_id=325e425c6dcc41bcb0f8f2204d5cb181
> **原文**：账号存续期间保留数据；**无合法目的后尽快删除/匿名化**。

### 4.3 第三方数据共享与供应商管理

| 要求 | EU | US |
| --- | --- | --- |
| 数据处理协议 | 所有接收个人数据的第三方须签署含 GDPR 级义务的 DPA | 须在合同中限制服务提供商的数据使用 |
| RTB 竞价数据 | 严禁将用户行为数据传入广告竞价系统（未成年人场景绝对禁止） | 跨上下文行为广告共享须提供退出机制 |
| 供应商背景审查 | EU 数据：优先选择与中国无关联的供应商 | US 数据：禁止使用中国背景供应商（须穿透性背调） |

> **法条/原文出处**：《用户数据跨境基本原则》&#124; node_id=46a9710b32b443f59336a94a47d79216
> **原文**：**美国数据：禁止使用中国背景供应商，要求合作方美国本地存储、本地闭环处理。EU数据：欧洲本地供应商 &gt; 新加坡本地供应商 &gt; ROW供应商。**

### 4.4 隐私协议透明度披露

**结论：隐私协议须明确披露个性化推荐/广告的数据使用目的，并提供个性化功能说明链接。**

> **法条/原文出处**：《rednote 隐私协议版本管理表》&gt; 20260323 更新记录 &gt; 3. 信息使用目的 &#124; node_id=325e425c6dcc41bcb0f8f2204d5cb181
> **原文**：信息使用目的包括：**个性化推荐、好友推荐**、AI 搜索/训练、**广告投放**等。**提高个性化推荐/广告透明度，同步 link Notice on Personalization Feature。**

---

## 五、未成年人特殊保护（跨法域红线）

| 维度 | EU (GDPR + DSA) | US (COPPA + CPRA) | 内部政策 |
| --- | --- | --- | --- |
| 同意年龄 | 16岁为默认（成员国可降至13岁），以下须家长同意 | 13岁以下须家长同意 | 13岁以下不得注册 |
| 行为定向广告 | ❌ 禁止 | ❌ 禁止（须家长 opt-in） | ❌ 禁止（13-17岁全部禁止） |
| 用户画像（广告） | ❌ 禁止 | ❌ 限制 | ❌ 禁止 |
| 个性化推荐 | DSA 要求 VLOP 提供非个性化选项 | COPPA 情境广告豁免 | 13-17岁：非个性化推荐 |
| RTB 竞价 | ❌ 禁止 | ❌ 禁止 | ❌ 禁止 |
| 第三方广告SDK | ❌ 禁止 | ❌ 禁止 | ❌ 禁止 |

> **法条/原文出处**：《国际化未成年人数据收集使用政策》&gt; 3.3 广告系统处理规则 &#124; node_id=82a02facaa024e96b3e2257a6975cf6f
> **原文**：&#124; 随机通投广告（Generic Ads）&#124; ✅ 允许 &#124; &#124; 行为定向广告 &#124; ❌ **禁止** &#124; &#124; 再营销（Retargeting）&#124; ❌ **禁止** &#124;
> **链接**：[REDoc 原文](https://docs.xiaohongshu.com/doc/83a57dcefa2d36b45f37caacd1ea6b8a)

> **法条/原文出处**：《TikTok & Instagram 儿童内容推荐 Feed 调研》&#124; node_id=aeea66a988c94092bc6c2c9f5c7b43e1
> **原文**：**13岁以下（COPPA）：若做个性化推荐，须满足 COPPA 情境广告豁免（仅用当前会话上下文，不用历史行为数据），否则须获取家长同意。** 13-17岁：rednote 政策规定"非个性化推荐：推荐 Feed 不使用用户历史行为数据"——比竞品更严格。

---

## 六、合规设计 Checklist（按功能阶段）

### 📥 阶段一：用户数据处理

- [ ] **合法依据确立**：EU 用户须获取明确同意（GDPR Art.6(1)(a)）；US 用户提供退出机制（CPRA opt-out）

- [ ] **Cookie 同意墙**：EU 须实现 ePrivacy 合规的 cookie consent banner

- [ ] **数据最小化**：仅收集推荐/广告所需的最小数据集；敏感数据禁止用于广告定向

- [ ] **数据本地化**：EU/US 用户 UBT 数据和用户画像须本地存储，严禁回传中国

- [ ] **未成年人识别**：部署年龄验证机制（如 k-ID）；识别后自动切换至未成年人保护策略

- [ ] **隐私协议更新**：明确披露个性化推荐/广告的数据使用目的

### 📤 阶段二：实际推送功能

- [ ] **推荐系统参数披露**：在条款中以通俗语言说明推荐系统主要参数（DSA Art.27）

- [ ] **非个性化选项**：若为 VLOP，须提供至少一种非基于画像的推荐选项

- [ ] **广告标识**：所有广告须清晰标识为"广告"，披露广告主身份和定向参数（DSA Art.26）

- [ ] **广告数据库**：若为 VLOP，建立可公开访问的广告存储库，不含用户个人数据（DSA Art.39）

- [ ] **"非个性化"边界明确**：非个性化推荐不得使用用户任何历史行为数据

- [ ] **未成年人广告限制**：13-17岁仅允许通投广告（Generic Ads）

- [ ] **GPC 信号响应**：US 版本须响应 Global Privacy Control 等退出偏好信号

- [ ] **"Do Not Sell or Share" 链接**：US 版本首页须提供退出链接

### 🔄 阶段三：后续链路

- [ ] **用户权利通道**：提供访问/删除/更正/反对/撤回同意的行权入口

- [ ] **退出后画像处理**：用户退出个性化后，停止使用/删除基于行为数据的画像

- [ ] **数据保留期限**：设定合理保留期，目的达成后删除/匿名化

- [ ] **第三方 DPA**：所有广告/推荐技术供应商签署含 GDPR 级义务的数据处理协议

- [ ] **供应商背景审查**：US 数据排除中国背景供应商；EU 数据优先非中国关联供应商

- [ ] **广告主数据传递约束**：向广告主/DSP 传递的定向数据须脱敏/令牌化

- [ ] **透明度报告**：定期发布推荐系统透明度报告（DSA Art.42，VLOP 强制）

---

## 七、EU vs. US 核心差异对比

| 维度 | 欧盟 | 美国（加州） |
| --- | --- | --- |
| **同意模式** | Opt-in（事先同意） | Opt-out（事后退出） |
| **法律依据** | GDPR + ePrivacy + DSA + DMA + AI Act | CCPA/CPRA + COPPA + FTC Act |
| **推荐系统透明度** | DSA 强制参数披露 + VLOP 非个性化选项 | 无专门联邦法律要求 |
| **广告透明度** | DSA Art.26 标识 + Art.39 广告库 | 无专门法律（FTC truth-in-advertising） |
| **未成年人保护** | GDPR 16岁默认 + DSA 额外保护 | COPPA 13岁以下 + CPRA 13-16岁 opt-in |
| **数据跨境** | GDPR Chapter V 传输保障 | 无一般性限制（EO14117 针对中国背景） |
| **自动化决策** | GDPR Art.22 反对权 | CCPA 限制敏感信息自动化决策 |
| **守门人限制** | DMA 禁止跨服务合并数据 | 无对应法规 |

---

## 🔗 来源清单

### agentic-rag 知识库

1. 《国际化未成年人数据收集使用政策》&gt; 3.1 处理目的限制 &#124; node_id=fd2c1dbfc23544ca8611a8d996a3491b → [REDoc](https://docs.xiaohongshu.com/doc/83a57dcefa2d36b45f37caacd1ea6b8a)

2. 《国际化未成年人数据收集使用政策》&gt; 3.3 广告系统处理规则 &#124; node_id=82a02facaa024e96b3e2257a6975cf6f → [REDoc](https://docs.xiaohongshu.com/doc/83a57dcefa2d36b45f37caacd1ea6b8a)

3. 《法律合规审查意见》&gt; 4.3 推荐系统非个性化定义 &#124; node_id=b42b606f6fd04b3da53bb8ad3c69cba4 → [REDoc](https://docs.xiaohongshu.com/doc/27aaa860ba17c24b024c857b6e7f82ca)

4. 《TikTok & Instagram 儿童内容推荐 Feed 调研》&#124; node_id=aeea66a988c94092bc6c2c9f5c7b43e1 → [REDoc](https://docs.xiaohongshu.com/doc/23cbd659637d836be80c65c90780805c)

5. 《国际化未成年AI功能合规意见》&gt;（六）基于对话历史的个性化 &#124; node_id=338bead6f4054edf944917cbcc071353 → [REDoc](https://docs.xiaohongshu.com/doc/92ca4b4895a973344c7a8b94e760d31d)

6. 《rednote 隐私协议版本管理表》&gt; 3. 信息使用目的 &#124; node_id=325e425c6dcc41bcb0f8f2204d5cb181 → [REDoc](https://docs.xiaohongshu.com/doc/0f43ff0134476061c45b9071710c4781)

7. 《用户数据跨境基本原则》&gt; EU/US 严禁回传清单 &#124; node_id=46a9710b32b443f59336a94a47d79216 → [REDoc](https://docs.xiaohongshu.com/doc/29f61e75b4e15daf57094752dd545457)

8. 《用户数据跨境基本原则》&gt; 搜推场景 &#124; node_id=9e44b664f41545138aad509477f14764 → [REDoc](https://docs.xiaohongshu.com/doc/29f61e75b4e15daf57094752dd545457)

### 外部官方信息

- [GDPR Art.6](https://gdpr-info.eu/art-6-gdpr/) &#124; [Art.22](https://gdpr.algolia.com/gdpr-article-22)

- [EDPB Guidelines 1/2024 on legitimate interest](https://www.edpb.europa.eu/system/files/2024-10/edpb_guidelines_202401_legitimateinterest_en.pdf)

- [ePrivacy Directive - Cookie consent](https://gdpr.eu/cookies/)

- [DSA Art.27](https://www.eu-digital-services-act.com/Digital_Services_Act_Article_27.html) &#124; [Art.39](https://www.eu-digital-services-act.com/Digital_Services_Act_Article_39.html)

- [EC - DSA](https://digital-strategy.ec.europa.eu/en/policies/digital-services-act)

- [DMA Art.5](https://www.eu-digital-markets-act.com/Digital_Markets_Act_Article_5.html)

- [AI Act Summary](https://artificialintelligenceact.eu/high-level-summary/)

- [CCPA - California AG](https://oag.ca.gov/privacy/ccpa)

- [FTC COPPA Final Rule (2025)](https://www.ftc.gov/news-events/news/press-releases/2025/01/ftc-finalizes-changes-childrens-privacy-rule-limiting-companies-ability-monetize-kids-data)