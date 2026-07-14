# Cited Alpha 目标用户工作邮箱获取方案

日期：2026-07-14

模式：Internal decision memo

适用范围：已经通过 X、LinkedIn 原生功能、行业媒体或公开内容发现目标账户，再从独立公开来源确认目标人与机构的首轮外联；美国优先，英国、欧盟及其他地区需单独检查当地规则。

## 结论

Cited Alpha 首批 30–100 个目标人，不应先买 Apollo、Clay 或一份现成联系人库。最合理的顺序是：

1. 在目标人自己控制的官网、newsletter、作者页和公司 Contact/Team/Press/Partnership 页面找公开商务邮箱或联系表单。
2. 只有找不到时，才用 Hunter 的姓名 + 公司域名查询工作邮箱，并保存它展示的来源、`public/inferred` 标记和验证状态。
3. Hunter 未命中的高分目标，才交给 FullEnrich 或 BetterContact 做第二层补缺，默认关闭 personal email 与手机号。
4. 发出前只放行近期验证为 `valid/deliverable` 的工作邮箱。`catch-all/accept-all/unknown` 不进入首批主名单。
5. LinkedIn 和 X 用于发现人和阅读上下文，不抓取 profile、不批量导出、不自动私信。

这里的“发现”与“邮箱获取”必须分层：不能把平台 profile 导出后直接喂给 Finder 或数据商。若线索最早来自 LinkedIn/X，进入邮箱流程前，应从公司官网、作者页、公开报告或其他独立页面重新确认姓名、当前职位与机构，并把这个独立页面作为 enrichment 的输入依据。

现有 16 个公开 seed leads 的抽样已经说明这条路可行：7 个能从官网或作者控制页面直接确认到明确的公开商务邮箱；其余 9 个也都有官方联系表单、预约、公司通用入口或公开社交触达路径。首轮的瓶颈并不是“没有任何联系方式”，而是是否愿意逐条确认目标匹配度、来源和发送依据。

首轮推荐的最小工具栈：

| 任务 | 工具 | 预算 |
|---|---|---:|
| 公开页面查找 | 浏览器 + 搜索引擎 | $0 |
| 姓名 + 公司域名找工作邮箱 | Hunter Free | $0，50 credits/月 |
| 已有候选邮箱的第二次验证 | Bouncer Free | $0，100 credits |
| 少量高价值未命中补缺 | FullEnrich Free；需要时 $29/500 | $0–29 |
| 大规模工作流编排 | 暂不采购 Clay | $0 |

Hunter 的主要优势不是宣称的命中率，而是能把公开来源 URL、发现时间、推断状态和验证结果交给操作者判断；其 Finder 结果会自动验证。[Hunter Email Finder](https://help.hunter.io/en/articles/1844277-email-finder-find-the-email-of-a-specific-person) 与 [Hunter 数据说明](https://hunter.io/our-data) 对这些字段有明确说明。Hunter 免费计划当前每月 50 credits，Finder 每个成功结果消耗 1 credit，Verifier 每条消耗 0.5 credit。[Hunter pricing](https://hunter.io/pricing/) 与 [credits 说明](https://help.hunter.io/en/articles/1911617-how-do-credits-work-in-hunter)

## 边界：获取的是业务入口，不是人的私人身份数据

本方案只接受：

- 目标人或其机构在官网、newsletter、公开作者页明确公布的商务邮箱；
- 官方联系表单、预约页、研究合作或 press/business inquiry；
- 姓名 + 当前公司域名推断并验证的工作邮箱；
- 用户通过样稿申请、newsletter、webinar 或 Lead Gen Form 主动提交的邮箱。

默认拒绝：

- 数据商返回的个人 Gmail、Outlook、Yahoo 等私人邮箱；
- 手机号、家庭地址或与当前工作无关的历史邮箱；
- 绕过登录、验证码或平台限制抓取 LinkedIn/X profile；
- 从泄露数据、address harvesting 列表或无法说明来源的数据包获得的邮箱；
- 已退出、已投诉、hard bounce 或明确反对营销的人。

邮箱“公开可见”不等于“可以无条件营销”，邮箱“技术上可投递”也不等于“对方愿意接收”。CRM 必须分别记录为什么联系、邮箱从哪里来、验证状态、地区规则和退出状态。

## 从目标人到工作邮箱的操作流程

### 第 1 层：查目标人控制的公开页面

对每个高于 70 分的目标，先确认当前公司或个人品牌的 canonical domain，再依次查：

1. 官网页脚、About、Contact、Team、作者 bio；
2. Research、Press、Media、Partnership、Speaking、Consulting；
3. Newsletter About、welcome email、公开 archive 页和作者主页；
4. 公司招聘页与公开 PDF 报告中的作者联系信息；
5. 官网联系表单或预约页。

可复用搜索式：

```text
site:example.com "@example.com"
site:example.com (contact OR about OR team OR press OR partnership)
site:example.com filetype:pdf "Name"
"Full Name" (email OR contact OR newsletter)
"Full Name" "Company Name"
```

如果找到明确邮箱，保存准确的 source URL、页面标题和发现日期，不只把地址复制进表格。对于独立研究作者和 Substack 型出版者，这一步往往比企业数据库更有效，因为很多人没有标准企业域名或正式 HR 记录。

### 第 2 层：姓名 + 公司域名查找

第一方页面没有明确邮箱时，把以下三个字段交给 Hunter：

```text
first_name, last_name, company_domain
```

Hunter 的 Email Finder 会先找公开来源；没有公开来源时，可能根据同域名已有地址模式推断，再做技术验证。推断结果会标为 `Inferred`，不应伪装成公开邮箱。[Hunter Finder 说明](https://help.hunter.io/en/articles/1844277-email-finder-find-the-email-of-a-specific-person)

放行规则：

- `public source + valid`：可进入人工外联审批；
- `inferred + valid`：只有人、公司、职位都能从近期公开资料确认时才进入审批；
- `accept-all / unknown / blocked`：不进入首批主名单；
- `invalid / disposable`：永久拒绝。

Domain Search 适合先确认机构的邮件模式和公开职能邮箱，也会展示来源、职位与 `Valid/Accept-all/Unknown` 标签。[Hunter Domain Search](https://help.hunter.io/en/articles/1830792-domain-search-find-emails-from-companies)

### 第 3 层：只对高价值未命中目标做 waterfall 补缺

Hunter 没有结果，不代表应该立刻切换到私人邮箱。先确认这个人确实是高分 ICP、仍在当前职位，并且存在可解释的业务理由。满足这些条件后：

- 优先 FullEnrich：免费 50 credits，Starter 当前 $29/500；只请求 work email。[FullEnrich pricing](https://fullenrich.com/pricing)
- 预算更低时用 BetterContact：免费 50，Starter 当前 $15/200；用于 Hunter 未命中的小批量补缺。[BetterContact pricing](https://www.bettercontact.co/pricing/)
- Apollo 只在还需要从 VC、Corporate Strategy、CI 等中大型机构数据库里发现人时加入。已经人工选好名单时，它的数据库、sequencer 和 personal email 能力都偏重。[Apollo pricing](https://www.apollo.io/pricing?solution=enrichment)
- Clay 只在需要把信号采集、打分、多供应商 enrichment、研究和 CRM 同步编排为持续流程时使用。当前 Free 只有 100 data credits；付费方案已经超过首轮人工实验所需。[Clay pricing](https://www.clay.com/pricing)

供应商宣称的“97%”“98%”不能横向比较。至少要拆成四个指标：`find rate`、验证状态、当前任职正确率、真实发送后的 hard bounce。Anymail Finder 发布过同一批 5,000 个联系人跨工具测试，结果支持 waterfall 通常提高覆盖，但发布方本身也是竞品、测试不是真实发送，不能把排名直接外推到 Cited Alpha 的小型研究机构与独立作者画像。[2026 email finder benchmark](https://anymailfinder.com/email-finder-benchmark)

### 什么时候才升级到付费 waterfall

同时满足以下条件再升级：

- 连续两批各 50 个高分目标中，第一方公开入口 + Hunter 的 work-email 命中率都低于 70%；
- 已人工确认未命中者确实属于 ICP，而不是名单质量差；
- 每月处理量达到 300–500 人，人工补缺开始成为瓶颈；
- 有效回复或会议的价值足以覆盖额外工具与合规成本。

## 验证不是授权，也不是送达保证

Verifier 通常检查 syntax、域名与 MX、SMTP 响应、disposable、role-based 和 catch-all。Hunter 的官方说明列出了 format、MX、SMTP、webmail、disposable 与 accept-all 等检查。[Hunter Verifier checks](https://help.hunter.io/en/articles/1935168-what-checks-are-performed-on-an-email-with-the-email-verifier)

但它不能证明：

- 邮箱背后就是目标本人；
- 对方仍在当前职位；
- 邮件一定进入 inbox；
- 对方同意接收营销；
- 当前处理和发送符合目标所在地区的法律。

SMTP 协议允许服务器接受消息后再产生 delivery failure，也允许返回“无法验证用户，但会接受并尝试投递”。所以 verifier 本质是风险分类器，不是事实证明。[RFC 5321](https://datatracker.ietf.org/doc/html/rfc5321)

首轮状态门禁：

| 验证状态 | 动作 |
|---|---|
| `valid / deliverable` | 人、公司、来源均确认且验证不超过 7 天时，允许进入人工审批 |
| `invalid / undeliverable` | 禁止发送，写入 suppression |
| `disposable` | 禁止发送 |
| `unknown / blocked` | 24–72 小时后复验；仍未知则暂缓 |
| `catch-all / accept-all` | 不进入主名单；仅当官网近期明确公开该地址且目标价值很高时逐条决定 |
| `role-based` | 只有组织公开把它作为相关业务入口，而且诉求确实面向该职能时使用 |
| 多家结果冲突 | 采用更保守状态，等待新证据 |

已有公开邮箱、只需要验证时，Bouncer 的免费 100 credits 足够首批 pilot；付费 1,000 条当前为 $8，`unknown` 与重复项不收费。[Bouncer pricing](https://www.usebouncer.com/pricing/) 其状态分为 `deliverable/risky/undeliverable/unknown`，并单列 accept-all、role 与 disposable 等属性。[Bouncer terminology](https://docs.usebouncer.com/terminology)

发送实验从 10 条全 Safe 开始，24–48 小时观察 hard bounce、reply、opt-out 和 complaint，再扩到 30 和 100。首 30 封出现 1 个 hard bounce 就是 3.3%，此时应暂停同一来源或同一推断模式，而不是继续消耗名单。任何 hard bounce、投诉或退出都立即进入 suppression。

## 合规最小线

### 美国

美国 CAN-SPAM 同样适用于 B2B 商业邮件。必须保证发件人与主题不误导、说明广告性质、提供有效实体邮寄地址和清晰退出方式，并在 10 个工作日内执行退出。FTC 还把 address harvesting 列为加重违规情形。[FTC CAN-SPAM compliance guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business)

这不表示“任何买来的美国邮箱都值得发”。首轮仍只使用与职业任务高度相关、来源可解释的一对一工作邮箱，并给出简单退出方式。

### 欧盟

欧盟需要同时过 GDPR lawful basis 与 ePrivacy 电子营销许可两道门。Legitimate interest 不能替代 ePrivacy 所要求的 consent；法人 B2B 的具体保护由各成员国法律落实，并不存在一套可覆盖全欧盟的冷邮件规则。[EU ePrivacy Directive Article 13](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02002L0058-20091219)

所以 Cited Alpha 的默认政策应是：欧盟目标只走 opt-in。除非未来为具体国家建立并由专业法律顾问复核的规则矩阵，否则不把官网实名邮箱、推断邮箱或数据商邮箱直接用于冷邮件。

### 英国

英国 ICO 指南区分 corporate subscriber 与 sole trader/partnership。确认属于 limited company、LLP 等 corporate subscriber 时，B2B email 在 PECR 下可能不需事先同意，但必须表明身份并提供有效退订；涉及实名工作邮箱时 UK GDPR 仍适用，需要 lawful basis、透明告知和反对权。sole trader 和部分 partnership 必须有 consent 或满足 soft opt-in。实体类型或国家不明时，按 individual subscriber / opt-in 处理。[ICO B2B direct marketing](https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/business-to-business-marketing/)

从官网、Finder 或数据商间接获得个人工作邮箱时，需要按适用地区检查透明告知。GDPR Article 14 要求说明数据类别、具体来源、处理目的与依据，通常最迟在首次沟通时完成；Article 21 赋予个人反对 direct marketing 的权利，反对后不得继续处理用于该目的。[GDPR Article 14](https://eur-lex.europa.eu/eli/reg/2016/679/art_14/oj/eng) 与 [Article 21](https://eur-lex.europa.eu/eli/reg/2016/679/art_21/oj/eng)

因此，英国/欧盟名单不能仅凭“工具标成 verified”就发送。需要确认地区、企业实体类型、合法基础、电子营销许可、隐私告知、数据商合同、删除与 suppression 链路；不确定时改用公开联系表单、人工 InMail 或 opt-in。

### 平台边界

LinkedIn 和 X 只用于人工发现与上下文阅读。LinkedIn 禁止未经授权的 scraping、bot、自动加联系人和自动发消息，其 User Agreement 也禁止用插件等方式复制 profiles 和其他数据。[LinkedIn 禁止的软件与扩展](https://www.linkedin.com/help/linkedin/answer/a1341387) 与 [LinkedIn User Agreement](https://www.linkedin.com/legal/user-agreement) X 也禁止未经许可的 scraping 和批量或自动发送未经请求的 DM。[X Terms](https://x.com/en/tos) 与 [X Automation Rules](https://help.x.com/en/rules-and-policies/x-automation)

安全替代是使用平台原生 InMail、Lead Gen Forms、广告和内容互动，把有兴趣的人导向自有表单；或者在独立官网重新找到并确认公开商务入口。CRM 需要分开记录 `discovery_channel=LinkedIn` 与 `acquisition_source=official_company_website`，不能用后者掩盖平台导出行为。

## 长期可扩展的 opt-in 获取方式

冷邮箱只能验证早期 ICP，不应该成为唯一获客系统。更干净且可规模化的路径是让目标人主动提交商务邮箱：

1. **免费 source pack**：提交一个标的或市场问题，获得一份带引用的 2 页 memo。
2. **样稿下载**：earnings memo、market map、competitor deep dive 三类模板各建独立 landing page。
3. **研究 newsletter**：每周展示一个“结论—证据—冲突来源”的完整例子。
4. **小型 webinar / teardown**：邀请目标作者带一篇已发布报告，现场展示 source-to-memo 重建。
5. **LinkedIn Lead Gen Forms**：对匹配职位投放内容型广告，让平台预填职业信息并由用户提交。[LinkedIn Lead Gen Forms](https://business.linkedin.com/en-us/marketing-solutions/native-advertising/lead-gen-ads)
6. **newsletter sponsorship / 合作作者**：广告链接回自有 opt-in 表单，不要求合作方交出订阅者名单。

每个表单只收完成下一步需要的字段，并明确用途、隐私说明和退出方式。若用户只申请一次样稿，不自动把它解释为无限期 newsletter 或销售邮件同意。

## CRM 字段与可审计性

建议字段：

```text
lead_id, account, person, current_role, domain, jurisdiction,
org_legal_name, subscriber_type, country_evidence,
profile_url, proof_url, trigger_signal, signal_date,
email, email_type, acquisition_method, source_url, source_date,
finder_provider, finder_result_type, verifier, verification_status,
verified_at, lawful_basis_or_consent, eprivacy_permission, lia_id,
consent_text_version, privacy_notice_at, article14_due_at,
last_contacted_at, bounce_type, reply_status, opt_out,
suppression_reason, suppression_at, owner, notes
```

其中：

- `proof_url`：解释为什么这个人可能需要 Cited Alpha；
- `source_url`：解释邮箱从哪里获得；
- `acquisition_method`：限定为 `public / finder / broker / optin / contact_form`；
- `email_type`：限定为 `person_work / role_business / personal`，首轮拒绝 `personal`；
- `privacy_notice_at` 与 `opt_out`：不能藏在 notes；
- suppression 必须跨工具同步，不能更换发送工具后重新联系。

### 来源白名单

| 等级 | 来源 | 系统动作 |
|---|---|---|
| Green | 第一方 newsletter/asset/demo opt-in、webinar registration、LinkedIn Lead Gen 提交、inbound business request | 可进入 CRM，仍需按授权用途和地区发送 |
| Yellow | 官方 generic/named work email、business card、经审计 B2B vendor、明确点名各方的联合表单 | 必须人工确认国家、实体类型、来源、lawful basis 与电子营销许可 |
| Red | LinkedIn/X scraping、浏览器插件导出、批量排列猜测、SMTP spray、personal-email people search、泄露数据、无 provenance 数据商、第三方代填邮箱、suppressed re-import | 禁止导入与发送 |

对数据商不能只接受“GDPR compliant”的宣传。导入前至少要求底层来源、采集日期与上下文、当时的 privacy notice/consent、是否点名 Cited Alpha 与 email 渠道、更新和 opt-out 传递、删除/异议 SLA、DPA 与跨境传输机制。ICO 明确要求使用数据商的组织自己做尽调，不能只依赖供应商保证。[ICO data broker guidance](https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/organisations-using-marketing-services-of-data-brokers/)

可用以下“邮箱可用性分”帮助人工排序，但不能替代法律判断：

| 证据 | 分数 |
|---|---:|
| 官网近期公开的 person-level 工作邮箱，来源可追溯 | 100 |
| 官方相关职能邮箱或联系表单 | 90 |
| `inferred + valid` 工作邮箱，当前任职有近期证据 | 70 |
| 数据商工作邮箱，任职已确认但无原始来源 | 60 |
| `catch-all / unknown` | 20 |
| 私人邮箱、来源不明或无关历史数据 | 0 |

只有 60 分以上才进入人工审核；达到分数不代表自动发送。

## 首批 100 人执行方案

### 第 1 批：10 人

- 从现有 seed leads 选 10 个 80 分以上对象；
- 逐个查官网与 newsletter；
- 找不到时用 Hunter；
- 只发送 `public + valid` 或证据充分的 `inferred + valid`；
- 每封邮件引用对方一篇具体内容，只发一封初始消息。

### 第 2 批：补到 30 人

- 复盘第一批的命中来源、hard bounce、回复、退出和正向回复；
- 仅把 Hunter 未命中的高分目标放入 FullEnrich 或 BetterContact；
- `catch-all/unknown/role-based` 单独统计，不与 Safe 结果混合。

### 第 3 批：补到 100 人

- 只有前 30 人没有出现来源或退信系统性问题才扩量；
- 比较各路径的 `verified work email / 人工分钟` 与 `positive reply / 100 contacts`；
- 同时上线 source-pack opt-in 页面，开始降低对冷邮箱的依赖。

建议实验表：

| 指标 | 定义 |
|---|---|
| Public contact coverage | 通过目标控制页面获得邮箱或相关联系表单的人数 / 高分目标人数 |
| Finder hit rate | Finder 返回工作邮箱人数 / 进入 Finder 人数 |
| Current-role accuracy | 邮箱对应人仍在当前职位的人数 / Finder 命中人数 |
| Safe rate | `valid/deliverable` 且通过来源审核人数 / 所有候选邮箱人数 |
| Hard bounce rate | hard bounce / delivered attempts |
| Positive reply rate | 表示愿意看样稿、访谈或试用 / delivered attempts |
| Opt-out / complaint rate | 退出或投诉 / delivered attempts |
| Cost per safe contact | 工具成本 + 人工成本 / Safe 联系人 |

## 最终采购判断

现在采购：无。

先注册并使用免费额度：Hunter、Bouncer、FullEnrich。第一阶段不要开 personal email，不采集手机号，不导出 LinkedIn/X profile。

达到 300–500 人/月、公开入口 + Hunter 连续两批低于 70% 命中，并且正向回复已经证明 ICP 成立时，再决定购买 FullEnrich/BetterContact 或把流程迁入 Clay。Apollo 只在第二 ICP 的企业角色发现成为主要任务时采购。

工具选择的首要顺序应是：来源可解释性 > 当前任职正确率 > 真实安全命中率 > 单条价格 > 厂商宣传覆盖率。
