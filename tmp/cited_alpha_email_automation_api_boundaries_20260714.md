# Cited Alpha 联系人工作邮箱自动化：官方 API 与平台边界

调研日期：2026-07-14  
范围：B2B 工作邮箱发现、验证、公开网站抓取和平台合规边界。本文不包含任何具体个人邮箱。

## 工程结论

这套自动化应把“目标发现”“独立来源确认”“邮箱查询”“验证”“法域与退订门禁”建成五个不同阶段。LinkedIn/X 只负责发现信号或接收用户主动提交的 Lead；工作邮箱由公司官网等独立公开页面、Hunter 或 waterfall enrichment 服务获取。平台 profile scraping、自动导出联系人和未经请求的批量私信不能进入实现范围。

MVP 可以使用 Hunter 作为首个 Finder，Bouncer 作为统一 Verifier，FullEnrich 或 BetterContact 只处理 Hunter 未命中的高价值联系人。每条记录都要保存 `source_url`、`source_type`、`source_observed_at`、`provider`、`provider_status`、`verification_status`、`jurisdiction`、`lawful_basis`、`article14_notice_at` 和 suppression 状态。

## 1. Hunter API

官方参考：[Hunter API Reference V2](https://hunter.io/api-documentation/v2)、[Hunter API help](https://help.hunter.io/en/articles/1970956-hunter-api)、[rate limits](https://help.hunter.io/en/articles/1971004-is-there-a-request-per-second-limit)

### 鉴权

API key 可以放在：

- `X-API-KEY: <key>`；
- `Authorization: Bearer <key>`；
- `api_key` query parameter。

生产环境应使用 header，避免 key 进入 URL、访问日志与分析系统。`test-api-key` 可验证 Finder、Verifier、Domain Search 的参数，但只返回固定测试数据。

### Endpoint 与合同

| 用途 | Endpoint | 关键输入 | 关键输出/状态 | 限速 |
|---|---|---|---|---|
| Domain Search | `GET https://api.hunter.io/v2/domain-search` | `domain` 或 `company`；可用 `limit`、`offset` | 域名下邮箱、type、position、sources；分页 | 15 req/s，500 req/min |
| Email Finder | `GET https://api.hunter.io/v2/email-finder` | `domain/company` + `first_name,last_name` 或 `full_name`；API 也接受 `linkedin_handle` | email、score、sources、verification | 15 req/s，500 req/min |
| Email Verifier | `GET https://api.hunter.io/v2/email-verifier` | `email` | `valid/invalid/accept_all/webmail/disposable/unknown`，以及 SMTP/MX/source 字段 | 10 req/s，300 req/min |
| Account | `GET https://api.hunter.io/v2/account` | 无 | 当前账号与额度 | 免费调用 |

Verifier 最长运行约 20 秒；暂时无法完成时返回 HTTP `202`，后续可查询同一 endpoint，官方说明这一轮重试只计一次。HTTP `403` 表示触发速率限制；Data Plan 用量耗尽时可能返回 `429`。Finder 对已经提出停止处理的数据主体可能返回 `451 claimed_email`，这类记录必须永久停止 enrichment 和营销处理。

### 计费

All-in-one/标准计划的官方帮助页当前写法是：Domain Search 每返回 1–10 个地址消耗 1 credit，Email Finder 成功结果 1 credit，Verifier 0.5 credit。Data Platform 计划把额度拆成 Search 与 Verification credit：Domain Search 1 Search credit/1–10 结果，Finder 1 Search credit，Verifier 1 Verification credit。项目应把计费模型做成 provider config，不能把 `0.5` 写死。

Hunter 不提供这些核心 endpoint 的 bulk API，一次只处理一个 contact/domain/email。工作流需要队列、token bucket、幂等缓存和指数退避。

### 数据门禁

- Finder 的 `sources` 非空：保存 URL 与 `extracted_on/last_seen_on`。
- Finder 没有公开来源时，结果可能是根据域名模式推断；必须保留 inferred 标记，不能改写为 public。
- `valid` 可进入后续法域门禁；`accept_all` 与 `unknown` 不自动发送；`invalid/disposable` 直接拒绝；`webmail` 在本项目中按个人/免费邮箱拒绝。
- 虽然 Hunter Finder 接受 `linkedin_handle`，该参数并不授予抓取或导出 LinkedIn profile 的权利。MVP 只传 `name + independently confirmed company domain`。

## 2. Bouncer API

官方参考：[API introduction](https://docs.usebouncer.com/introduction)、[real-time verification](https://docs.usebouncer.com/api-reference/real-time/verify-email)、[batch API](https://docs.usebouncer.com/api-reference/batch/batch-create)、[status terminology](https://docs.usebouncer.com/terminology)、[pricing](https://www.usebouncer.com/pricing/)

### 鉴权与 endpoint

统一使用 `x-api-key: <key>`。

| 模式 | Endpoint | 规模/限速 | 适用场景 |
|---|---|---|---|
| 单条实时 | `GET https://api.usebouncer.com/v1.1/email/verify?email=...&timeout=10` | 默认 1000 req/min；最长约 30 秒 | 表单实时检查、少量联系人 |
| 异步 batch 创建 | `POST https://api.usebouncer.com/v1.1/email/verify/batch` | 单批最多 100,000，推荐 1,000–10,000；创建最多 60 batch/min | 夜间批处理、大名单 |
| batch 状态 | `GET /v1.1/email/verify/batch/{batchId}?with-stats=true` | related endpoints 200 req/min | 低频轮询 |
| batch 下载 | `GET /v1.1/email/verify/batch/{batchId}/download?download=all` | JSON；`Accept: text/csv` 可下载 CSV | 结果导入 |
| 同步 batch | `POST /v1.1/email/verify/batch/sync` | 最多 10,000 条/请求；默认 100 req/min | 队列消费者 |

异步 batch 也支持 `callback=<URL>`，可在完成时回调。项目优先使用 callback，轮询间隔控制在 10–30 秒或更低频。

### 状态模型

顶层状态为 `deliverable/risky/undeliverable/unknown`。`reason` 进一步区分 `accepted_email`、`low_deliverability`、`low_quality`、`invalid_email`、`invalid_domain`、`rejected_email`、`dns_error`、`unavailable_smtp`、`unsupported`、`timeout` 等；还有 `domain.acceptAll/disposable/free`、`account.role/disabled/fullMailbox`、`score` 与 toxicity 字段。

建议门禁：

- `deliverable` 且不是 disposable/free：通过邮箱质量门禁；仍需再过营销法域门禁。
- `risky`、`unknown`：隔离，禁止自动发送。
- `undeliverable`：拒绝并记录验证时间。
- `account.role=yes`：可以保留为机构职能邮箱，但营销个性化不能假装写给具体个人。

Bouncer 当前按量价格：1000=$8、5000=$35、10000=$60；credits 不过期，重复项与 `unknown` 不收费，注册提供 100 free credits。这些是厂商当前页面价格，应在采购时重新读取。

## 3. FullEnrich API

官方参考：[bulk enrichment](https://docs.fullenrich.com/api/v2/contact/enrich/bulk/post)、[get result](https://docs.fullenrich.com/api/v2/contact/enrich/bulk/get)、[authentication](https://docs.fullenrich.com/api/v2/general/authentication)、[rate limit](https://docs.fullenrich.com/api/v2/general/ratelimit)、[webhooks](https://docs.fullenrich.com/api/v2/general/webhooks)、[credits](https://docs.fullenrich.com/api/v2/general/credit)、[email statuses](https://docs.fullenrich.com/api/v2/general/email-status)

### 合同

- 鉴权：`Authorization: Bearer <token>`。
- 创建：`POST https://app.fullenrich.com/api/v2/contact/enrich/bulk`。
- 查询：`GET https://app.fullenrich.com/api/v2/contact/enrich/bulk/{enrichment_id}`。
- 输入：最多 100 contacts；每条提供 `first_name + last_name + domain/company_name`，或者 `linkedin_url`。本项目只请求 `enrich_fields: ["contact.work_emails"]`，不请求 personal emails 和 phones。
- 输出：创建后返回 `enrichment_id`；结果状态为 `CREATED/IN_PROGRESS/CANCELED/CREDITS_INSUFFICIENT/FINISHED/RATE_LIMIT/UNKNOWN`。
- 限速：全 API 合计 60 calls/min；每批最多 100 contacts，理论提交上限 6000 contacts/min；workspace 默认 100 个并发 enrichments。

Enrichment 是异步操作，通常 30–90 秒。应设置 `webhook_url` 和可选的 `webhook_events.contact_finished`。官方 webhook 用 `X-Signature-SHA1`，其值是以 API key 为 secret、对原始 request body 计算的 HMAC-SHA1；应在 JSON 解析前做 constant-time comparison。非 2xx 时官方每分钟重试，最多 5 次。轮询会消耗 API 限额，官方建议必须轮询时每 5–10 分钟一次。

### 计费与门禁

找到 `DELIVERABLE`、`HIGH_PROBABILITY` 或 `CATCH_ALL` 工作邮箱时使用 1 credit；无结果不收费。三个月内相同 contact 通常可命中 dedupe，但同一 bulk 内不去重，输入差异和并发重复请求也可能重复计费。结果由 FullEnrich 保存三个月。

官方状态是 `DELIVERABLE/HIGH_PROBABILITY/CATCH_ALL/INVALID`。其中厂商页面对 bounce rate 的数字属于供应商自述，不能直接作为系统 SLA。建议只让 `DELIVERABLE` 自动通过；其他状态送 Bouncer 二次验证或隔离。

## 4. BetterContact API

官方参考：[quickstart](https://doc.bettercontact.rocks/quickstart)、[create enrichment](https://doc.bettercontact.rocks/api-reference/endpoint/create)、[get results](https://doc.bettercontact.rocks/api-reference/endpoint/get)、[rate limits](https://doc.bettercontact.rocks/api-reference/api_rate_limits)、[pricing](https://www.bettercontact.co/pricing/)

### 合同

- 鉴权：`X-API-Key: <key>`。
- 创建：`POST https://app.bettercontact.rocks/api/v2/async`，单次 1–100 leads。
- 查询：`GET https://app.bettercontact.rocks/api/v2/async/{request_id}`。
- 只设置 `enrich_email_address=true`；必须设置 `enrich_phone_number=false`。
- 可传 `webhook`，创建成功返回 HTTP `201` 与 request id。
- 全 endpoint 共用 60 req/min/account；超限返回 `429`。
- 查询结果含任务 `status`、`credits_consumed/credits_left`、`summary.valid/catch_all/catch_all_safe/catch_all_not_safe/undeliverable/not_found` 和 `contact_email_address_status`。

官网当前定价是成功找到 1 个已验证 email 消耗 1 credit，phone 为 10 credits；Starter 为 $15/月 200 credits，免费 50 credits。状态枚举的完整正式定义在公开 API 文档中没有充分说明，项目不能只凭 `summary` 猜测其含义。MVP 只接受明确的 `deliverable`，其余状态进入 Bouncer 或隔离。

## 5. LinkedIn 官方能力与边界

官方允许的自动化主要有三类：

1. 经申请的 [Lead Sync API](https://learn.microsoft.com/en-us/linkedin/marketing/lead-sync/leadsync) 可以读取用户主动提交的 Lead Gen Form responses，并用 webhook 接收新 Lead。需要单独申请，scope 是 `r_marketing_leadgen_automation`；创建/管理 Lead Gen Forms 属于 Advertising API 和 `rw_ads`。
2. 经审批的 [Community Management API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/community-management-overview) 可以管理自己的 Page/profile 内容与互动。读取 member social 内容的 scope 是 restricted，组织数据也限于已授权组织。
3. OAuth/OpenID Connect 只能获取已登录并明确授权的当前成员资料/邮箱，不能充当目标联系人数据库。[LinkedIn OAuth](https://learn.microsoft.com/en-us/linkedin/shared/authentication/authorization-code-flow) 与 [Profile API](https://learn.microsoft.com/en-us/linkedin/shared/integrations/people/profile-api) 明确限制 API 和数据存储范围。

[LinkedIn User Agreement](https://www.linkedin.com/legal/user-agreement) 禁止用 crawlers、浏览器插件、scripts 或 bots 抓取/复制 profiles 与其他服务数据，也禁止未经授权自动下载联系人、发送消息、加好友或制造互动。可实现的发现流程是 Sales Navigator/LinkedIn 原生人工搜索，或者获批 API 内的 Page/Lead Gen 数据；不能写 headless browser 去批量拉取 profile，也不能从 LinkedIn HTML/GraphQL 接口生成目标名单。

FullEnrich/Hunter 等第三方接受 LinkedIn URL 作为输入，不改变上述边界。项目要么使用用户在 CRM 中合法提供的 URL，要么改用姓名 + 独立官网确认的公司域名；不能让 crawler 自动从 LinkedIn 取得 URL。

## 6. X 官方能力与边界

[X API Search Posts](https://docs.x.com/x-api/posts/search/introduction) 提供：

- `GET /2/tweets/search/recent`：最近 7 天，最多 100 Posts/请求；
- `GET /2/tweets/search/all`：全历史，pay-per-use/Enterprise，最多 500 Posts/请求。

两者使用 `Authorization: Bearer <token>`，适合通过关键词、bio/内容信号发现公开账号与需求信号。X API 不提供“查目标人的工作邮箱”这一营销接口；公开 profile 的 `url/description/entities` 可以作为跳转到独立官网的线索，不能把 `confirmed_email` 等字段理解为可批量读取的他人邮箱。

[X Terms](https://x.com/en/tos) 要求自动访问只能走 X 当前公开接口，任何目的的 crawling/scraping 都需要事先书面同意。[X automation rules](https://help.x.com/en/rules-and-policies/x-automation) 禁止未经请求的批量或自动 DM；自动 DM 只有在收件人事先请求或清楚表达希望被 DM 联系、并且有退出方式时才允许。

## 7. 官网抓取器与 RFC 9309

[RFC 9309](https://www.rfc-editor.org/rfc/rfc9309.html) 是 Robots Exclusion Protocol 的正式标准。实现要求：

- 每个 authority 先请求根路径 `/robots.txt`，使用可识别且说明用途的 `User-Agent`。
- 成功读取时必须服从可解析的 `Allow/Disallow`；使用最长匹配，等长冲突优先 `Allow`。
- robots 发生 HTTP 4xx 时，标准允许访问其他资源；5xx 或网络错误时必须视为 complete disallow。工程上可以采取更保守策略：401/403 一律不抓，429 遵守 `Retry-After` 并暂停域名。
- robots cache 不应超过 24 小时，除非源站不可达。
- robots 规则不是访问授权，也不能替代网站 ToS、登录、版权、隐私和营销法要求。

本项目的 crawler 只处理无需登录的公司官网、作者官网、公开报告/Press/About/Team/Contact 页面，提取明确展示的 `mailto:` 或正文商务邮箱以及姓名、职位、公司域名和 source URL。遇到登录、CAPTCHA、paywall、401/403、访问控制、反自动化挑战、LinkedIn/X 域名立即停止。禁止绕过限制、轮换代理规避封禁、抓取个人邮箱数据集、按字典生成邮箱或对域名做 SMTP spray。

建议默认每域名并发 1、请求间隔至少 2 秒、尊重 `Retry-After`，限制抓取深度与页数，并保存 robots 决策、HTTP 状态、抓取时间和内容哈希。具体速率还要服从目标网站 ToS 与响应。

## 8. 营销法律门禁

### 美国

[FTC CAN-SPAM compliance guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) 明确覆盖 B2B commercial email。每封邮件都要使用真实 header 与主题、标识广告性质、提供有效实体邮寄地址和明确退出方式；退出机制至少保持 30 天有效，10 个工作日内执行。委托第三方发送不能转移责任。FTC 还把 address harvesting 与 dictionary attack 列为加重违规情形，因此公开页面抓取不能直接等同于发送许可，更不能与猜测地址、批量试投组合使用。

### 英国

[ICO B2B marketing guidance](https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/business-to-business-marketing/) 区分 corporate subscriber 与 sole trader/部分 partnership。对 corporate subscriber，PECR 的 email consent 要求通常不适用，但必须表明身份并提供退出；若实名工作邮箱能识别个人，UK GDPR 仍适用，需要 lawful basis、透明告知并执行其反对权。sole trader/相关 partnership 通常需要 consent 或满足 soft opt-in；实体类型不确定时应按 individual subscriber 处理。

### 欧盟/EEA

[GDPR Article 14](https://eur-lex.europa.eu/eli/reg/2016/679/art_14/oj/eng) 要求间接取得个人数据时告知 controller 身份、目的与 lawful basis、数据类别、保存期、权利和具体来源/是否来自公开来源；若用于沟通，最迟在首次沟通时完成。[GDPR Article 21](https://eur-lex.europa.eu/eli/reg/2016/679/art_21/oj/eng) 规定个人可随时反对 direct marketing，反对后不得继续为该目的处理。电子营销还要通过成员国落实的 [ePrivacy Directive Article 13](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02002L0058-20091219)，不能把 GDPR legitimate interest 当作全欧盟冷邮件许可。

### 系统强制规则

- `jurisdiction=EU/EEA`：默认只接受明确 opt-in；其他依据须经法律审核后以配置打开。
- `jurisdiction=UK` 且无法证明 corporate subscriber：要求 consent/soft opt-in。
- `jurisdiction=US`：通过 CAN-SPAM 合规检查并有与职位直接相关的业务理由后，才可进入人工批准或限量发送。
- 任何 `opt_out/objected/claimed_email`：立即写入全局 suppression；Finder、导入与后续批次都先查 suppression，不能删除后重新获取。
- `source_url`、具体来源说明和 privacy notice 链接要能够生成 Article 14 首次沟通说明。

## 9. 推荐的统一 provider 状态

供应商状态不能直接驱动发送，先归一化：

| 统一状态 | Hunter | Bouncer | FullEnrich | BetterContact | 自动动作 |
|---|---|---|---|---|---|
| `verified_work` | `valid` 且非 webmail | `deliverable` 且非 disposable/free | `DELIVERABLE` | `deliverable` | 进入法域/来源门禁 |
| `risky` | `accept_all` | `risky` | `HIGH_PROBABILITY/CATCH_ALL` | catch-all variants | 隔离或 Bouncer 二次验证 |
| `unknown` | `unknown`/202 超时 | `unknown` | `UNKNOWN/RATE_LIMIT` | 未终态/不明 | 重试队列，不发送 |
| `rejected` | `invalid/disposable/webmail` | `undeliverable` 或 disposable/free | `INVALID` | `undeliverable/not_found` | 拒绝 |
| `suppressed` | HTTP 451 / opt-out | N/A | N/A | N/A | 永久停止营销处理 |

最后还要单独判断 `authorization_status = allowed/review/blocked`。只有 `verified_work + allowed` 才能进入外联队列；邮箱可投递不等于可以营销。
