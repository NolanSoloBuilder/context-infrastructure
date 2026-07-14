# Cited Alpha 联系人获取自动化：行业路线与已实现项目

日期：2026-07-14

模式：Internal decision memo

## 结论

业界没有一个长期可靠的“全网联系人抓取器”。成熟系统实际是多层流水线：

```text
账户/需求信号发现
  -> 人物、机构与官网域名确认
  -> 官网公开联系入口抓取
  -> Finder / 联系人数据库 / Waterfall 补全
  -> 邮箱验证与当前任职检查
  -> 来源、平台、法域、suppression 门禁
  -> CRM 去重
  -> 人工审批或获批官方 API 触达
  -> 回复、退信、退出结果回写
```

这里的“联系人”不应只等于邮箱。对 Cited Alpha，更实用的 contact endpoint 包括：

- 官网公开的工作邮箱与职能邮箱；
- 作者明确公布用于商务合作的 creator email；
- 官方 Contact form；
- Calendly、Cal.com 等预约入口；
- 官网明确链接出的 LinkedIn/X 主页；
- 用户通过 demo、样稿、newsletter、webinar、Lead Gen Form 主动提交的邮箱；
- 经审计数据商返回并验证的工作邮箱。

首版代码项目已经实现：给出机构域名后，自动读取 robots.txt、抓取同域公开页面、提取上述公开入口；没有公开邮箱时可调用 Hunter；最后按来源、邮箱类型、验证结果与法域分流为 `eligible_for_manual_review / hold / reject`。它不会抓 LinkedIn/X 页面，也不会自动发送邮件或私信。

## 业界目前的七类获取手段

| 路线 | 常见产品/技术 | 自动化输入 | 输出 | 适用边界 |
|---|---|---|---|---|
| B2B 联系人数据库 | Apollo、ZoomInfo、RocketReach、ContactOut | 行业、公司、职位、seniority | 人物与可能的邮箱/电话 | 适合中大型机构角色发现；任职和邮箱会过期 |
| 姓名 + 域名 Finder | Hunter、Prospeo、Snov | 姓名、公司域名 | 公开或推断工作邮箱 | 适合已经确认目标人的精确补全 |
| Waterfall enrichment | FullEnrich、BetterContact、Clay | 姓名、域名、可选合法 profile URL | 多 provider 依次查询的结果 | 提高覆盖，不会自动提高任职正确率或营销许可 |
| 官网 crawler | Crawlee、Scrapy、Apify、Firecrawl、自研 | canonical domain | 邮箱、表单、预约、官方社交链接 | 最适合独立作者、小研究机构和 newsletter |
| Intent / trigger signal | Apollo Intent、Clay Signals、RSS、招聘与内容监控 | 公司、关键词、访问或事件 | 高优先级账户/任务 | 只决定先处理谁，不代表个人同意被营销 |
| 原生社交触达 | LinkedIn InMail/Lead Gen、X 原生互动/DM | 平台内目标或主动提交 | 平台消息、Lead webhook | 不能用 scraper 代替官方权限；自动 DM 受严格限制 |
| 第一方 opt-in | 样稿、demo、newsletter、webinar、referral link | 用户提交 | 邮箱、用途、consent context | 最可持续，必须区分一次履约与持续营销 |

### 联系人数据库

Apollo 的优势是先从行业、公司与职位发现企业角色。其 People Search 本身不返回邮箱，仍需继续调用 People Enrichment 或 waterfall，并消耗 credits。[Apollo People Search API](https://docs.apollo.io/reference/people-api-search) 与 [People Enrichment](https://docs.apollo.io/reference/people-enrichment)

这一类产品适合 VC、Corporate Strategy、Competitive Intelligence 等机构化角色；对独立研究作者和 2–10 人小团队，官网、newsletter 和 creator page 通常更接近真实联系方式。

### Finder 与验证

Hunter 提供 Domain Search、Email Finder 与 Verifier。Finder 可以返回公开来源；没有公开来源时可能按域名邮件模式推断，必须保留 `public/inferred` 区别。[Hunter API](https://help.hunter.io/en/articles/1970956-hunter-api) 与 [public/inferred 说明](https://help.hunter.io/en/articles/2085802-are-the-emails-found-in-the-email-finder-publicly-sourced)

Verifier 只能判断 syntax、MX、SMTP、catch-all 等技术信号，不能证明收件人身份、当前任职、inbox placement 或营销授权。系统必须把 `verification_status` 与 `authorization_status` 分开。

### Waterfall

Waterfall 的做法是按成本和覆盖顺序依次调用多个 provider，命中后停止。FullEnrich 与 BetterContact 都提供异步 batch API 和 webhook，适合只处理 Hunter 未命中的高价值目标。[FullEnrich API](https://docs.fullenrich.com/api/v2/general/introduction) 与 [BetterContact API](https://doc.bettercontact.rocks/quickstart)

供应商的“80% find rate”“97% accuracy”不能直接作为采购依据。需要在 Cited Alpha 自己的三个 cohort——独立研究作者、小研究机构、VC/Strategy——分别测：

- incremental find rate；
- 当前任职正确率；
- 公开来源覆盖率；
- 二次验证结果；
- hard bounce；
- positive reply；
- cost per usable contact。

### 官网 crawler

官网抓取器适合找目标自己公开的业务入口，包括 `mailto:`、页面正文、Contact 表单、预约链接和官网社交链接。生产实现必须遵守 [RFC 9309](https://www.rfc-editor.org/rfc/rfc9309.html)，限制域名、页数、深度、响应体、请求间隔和重定向，并阻止 SSRF、私网地址、登录、验证码与访问控制绕过。

托管方案可以用 Apify 官方 Website Content Crawler；社区 Contact Scraper Actor 的维护、评分和来源质量差异很大，不应因为名字匹配就直接进入生产。[Apify Website Content Crawler](https://apify.com/apify/website-content-crawler)

长期 TypeScript crawler 可使用 Apache-2.0 的 [Crawlee](https://github.com/apify/crawlee)；Python 高吞吐方案可用 BSD-3-Clause 的 [Scrapy](https://github.com/scrapy/scrapy)。Firecrawl API 更完整，但自托管和 AGPL 义务需要额外评估。

### 社交私信与官方 API

LinkedIn 可以通过获批 Lead Sync API 接收用户主动提交的 Lead Gen Form；普通 OAuth 只允许读取当前明确授权的登录成员，不能当成目标联系人数据库。[LinkedIn Lead Sync](https://learn.microsoft.com/en-us/linkedin/marketing/lead-sync/leadsync) 与 [LinkedIn OAuth](https://learn.microsoft.com/en-us/linkedin/shared/authentication/authorization-code-flow)

LinkedIn User Agreement 禁止用 crawler、browser plugin、script 或 bot 抓取 profiles、自动导出联系人、批量发送消息或加好友。[LinkedIn User Agreement](https://www.linkedin.com/legal/user-agreement)

X 可以通过官方 Search Posts API 自动发现公开需求信号，但不提供批量读取他人邮箱的接口。X 的 automation rules 只允许在用户事先请求或明确希望收到 DM 时自动私信，并要求退出方式；未经请求的批量自动 DM 不适合作为增长流水线。[X Search Posts](https://docs.x.com/x-api/posts/search/introduction) 与 [X Automation Rules](https://help.x.com/en/rules-and-policies/x-automation)

所以代码项目只自动发现并输出官网确认的社交主页，不登录、不抓 profile、不代发 DM。触达可以在平台原生界面完成；未来接官方 API 时再针对已授权场景增加 adapter。

## 两种可运行方案

### 方案 A：可视化 pilot

```text
n8n Schedule/Webhook
  -> seed CSV / Apollo People Search / RSS 信号
  -> Postgres 查 target fingerprint 与 suppression
  -> Apify 官方 Website Content Crawler
  -> 提取公开邮箱、表单、预约与官方社交链接
  -> 无公开邮箱：Hunter
  -> 高分未命中：FullEnrich/BetterContact webhook
  -> Bouncer 验证
  -> source/jurisdiction/platform gate
  -> HubSpot/Attio upsert
  -> Slack/飞书审批
```

n8n 适合内部 pilot，但其 Sustainable Use License 是 source-available，并非 OSI 开源；把它嵌入 Cited Alpha 产品或代客户托管需要重新检查商业许可。[n8n License](https://github.com/n8n-io/n8n/blob/master/LICENSE.md)

这个方案上线快，但核心状态、来源与 policy 逻辑容易散落在节点中。建议 n8n 只承担调度、webhook 和审批，crawler、provider adapters 与 policy gate 保留在自己的服务中。

### 方案 B：本次已实现的代码项目

项目位置：`adhoc_jobs/cited_alpha_lead_pipeline/`

当前模块：

```text
src/core             input、target fingerprint、pipeline
src/discovery        官方网站 crawl
src/extract          email/form/booking/social endpoint 提取
src/net              robots、DNS pinning、SSRF 与响应大小限制
src/providers        Hunter Finder/Domain Search/Verifier
src/policy           contact type、验证与法域门禁
src/runtime          JSONL event store、文件锁、checkpoint
test                 unit + local HTTP integration tests
schedule             cron 示例
```

核心控制流：

```text
trigger
  -> acquire lock
  -> load prior events
  -> validate source and target domain
  -> skip recently completed fingerprint
  -> robots + official-site crawl
  -> extract contact endpoints
  -> no public email ? Hunter : skip provider
  -> verify work emails
  -> policy gate
  -> write three queues + evidence + manifest
  -> append target/run completion events
  -> release lock
```

目前支持：

- 输入机构域名或姓名 + 域名；
- 官网公开邮箱、Contact form、booking、LinkedIn/X 官方外链；
- Hunter Finder、Domain Search、Verifier；
- `robots.txt`、同域限制、DNS pinning、SSRF 私网阻断、响应体与 redirect 限制；
- EU/UK/US 基础 policy gate；
- 可审计的一方 consent/inbound event 证据门禁；
- Red acquisition source 拒绝；
- suppression 显式缺失时 fail-closed，邮箱验证证据独立按 7 天过期；
- JSONL checkpoint，30 天内默认不重复处理；
- cron 周期运行；
- 每次 run 独立输出，不覆盖上次结果；
- `0600/0700` 本地文件权限。

输出：

```text
eligible_for_manual_review.csv
holds.csv
rejected.csv
page_evidence.json
manifest.json
events.jsonl
```

不存在 `send_ready`。`eligible_for_manual_review` 只代表来源明确、通过基础机器门禁，仍需审批或后续受控系统决定如何触达。

## 实际验收

25 项本地测试全部通过，覆盖 CSV、HTML 解析、邮箱分类、表单/预约/社交链接提取、robots 最长匹配、SSRF 私网/NAT64 阻断、EU/UK/US gate、一方 consent/inbound 证据、suppression fail-closed、验证 TTL、输出队列和重复运行 checkpoint。依赖审计结果为 0 个已知漏洞。

使用三个已有公开 seed 做了只读 dry-run：

- 抓取 12 个官方页面；
- 自动发现 7 个可人工审核的公开触达入口：1 个 X 主页、3 个 LinkedIn 主页、3 个 Contact form；
- 自动发现 3 个公开邮箱候选，由于没有提供法域/验证授权信息，全部进入 hold；
- 0 个 reject，0 个 provider API call，0 个错误；
- 相同配置重复运行复用 checkpoint，结果仍为 7/3/0，耗时 0.38 秒；
- 没有发送邮件、提交表单或发私信。

这次 smoke 的意义是验证真实网络、robots、DNS/HTTPS、页面解析、来源记录与输出分流，不把 3 个样本的覆盖率外推为行业命中率。

## 下一阶段

合理的升级顺序：

1. 配置 Hunter 免费 key，跑现有 16 个 seed，得到公开入口与 Finder incremental coverage。
2. 增加 Bouncer adapter，只验证 Hunter 与官网得到的邮箱。
3. 对 Hunter 未命中的高分目标增加 FullEnrich 或 BetterContact，默认关闭 personal email 和 phone。
4. 增加全局 suppression store；任何 opt-out、complaint、hard bounce、Hunter 451 都先于 provider 查询生效。
5. 选择 HubSpot 或 Attio，加入幂等 CRM upsert 与审批状态回写。
6. 用 n8n/cron 负责 schedule、webhook、通知；核心规则继续由当前代码维护。
7. 如果以后确实需要平台自动触达，只为获批 LinkedIn Lead Sync、X 用户请求 DM 或其他明确授权场景增加官方 adapter。

在首批 30–300 个目标阶段，不需要先采购 Clay。达到每月 5,000–10,000 个候选、provider 和 CRM 规则需要由运营频繁配置时，再比较 Clay、n8n 与自研服务的总成本。

## Loop 契约

### 触发方式

手动 CLI、工作日 cron 或未来 webhook。每次运行使用稳定 input CSV 和持久 output directory。

### 输入

目标机构域名、可选目标人姓名、国家/实体类型、发现渠道、ICP proof URL、来源类型与营销许可字段。

### 状态

`events.jsonl` 保存 target fingerprint、run、阶段与计数；每次 run 保存 config、page evidence、错误与三类输出。30 天内完成的 fingerprint 默认跳过。

### 停止与升级规则

- 达到 max targets、max pages/domain、max runtime 或 API budget；
- robots 5xx/超时、访问控制或 SSRF 命中；
- API key 缺失或 provider schema/认证失败；
- 法域、subscriber type、来源或验证状态不明确；
- 同一个输出目录已有运行锁；
- 需要自动发送、CRM 写入或扩大数据类型时，先取得新的明确授权。

### 风险护栏

- discovery channel 与 acquisition source 分开记录；
- 不把 deliverable 当成 marketing allowed；
- 不把社交主页 URL 当成自动私信许可；
- 不使用 personal data 数量作为唯一成功指标；
- 优先衡量 `usable endpoint / target`、来源透明度、当前任职、正向回复、退出与投诉；
- 每个 provider 都通过 adapter 接入，避免把数据和策略锁在单一供应商。
