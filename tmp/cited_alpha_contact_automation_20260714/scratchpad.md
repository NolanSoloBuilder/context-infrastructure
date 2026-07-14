# Cited Alpha 联系人邮箱自动化调研 Scratchpad

日期：2026-07-14

## 目标契约

### 目标

交付一个可运行的 Node.js 项目：输入已确认的目标机构域名或目标人姓名 + 公司域名，自动从官方公开网页和可选服务商 API 获取带来源证据的 contact endpoint，包括公开商务/创作者邮箱、官方联系表单、预约页和官网明确链接的社交主页；随后完成验证、来源/法域/渠道门禁、去重与可审计导出，并可由 cron 周期运行。

### 完成标准

- `node src/cli.mjs run --input <csv> --output <dir>` 能用本地 fixtures 完整跑通。
- 公开网页 crawler 尊重 robots.txt、域名边界、页数上限、超时和请求间隔。
- 每条 contact endpoint 都保留 `contact_type`、`contact_value`、`source_url`、`source_type`、获取时间、provider 与验证状态。
- 自动识别官网 contact form、booking URL，以及官网明确链接的 LinkedIn/X 等社交主页；只生成平台内人工触达队列，不自动发送 DM。
- 可选支持 Hunter Finder、Domain Search、Verifier；未配置 API key 时仍能完成公开页面流程。
- 未公开的 personal/free-mail、Red 来源、invalid/disposable、欧盟非 opt-in 等记录不会进入 eligible 输出；本人在官方页面明确公布的 creator contact email 进入 hold。
- 输出 `eligible_for_manual_review`、`holds`、`rejected` 三类 CSV 和持久 JSONL 状态；重复运行不会重复处理同一来源。
- `node --test` 覆盖解析、robots、去重、分类、法域门禁和端到端 fixture。
- README、`.env.example`、示例输入和 cron 示例可让下一轮直接运行。

### 已检查证据

- `contexts/survey_sessions/cited_alpha_target_email_acquisition_survey_20260714.md` 已确定公开商务入口 → Hunter → 补缺 → 验证的顺序。
- `contexts/survey_sessions/cited_alpha_seed_leads_20260714.csv` 现有 16 条 seed 中 7 条有明确公开商务邮箱，全部有官方触达路径。
- 当前 Node.js 为 v25.2.1；项目只引入 `parse5` 与 `csv-parse` 两个解析库，其余使用标准库。
- `rules/WORKSPACE.md` 要求一次性代码项目放在 `adhoc_jobs/`。

### 待确认问题

- 生产使用哪个 enrichment provider、CRM 和调度平台尚未选择；首版以可插拔 provider contract 和本地 CSV/JSONL 为准。
- 是否要把 eligible 联系人自动写入现有 CRM 尚未授权；首版只导出，不自动发送、不写外部系统。

### 边界

- 禁止 LinkedIn/X scraping、浏览器插件导出、登录后页面抓取和自动私信。
- 禁止私人邮箱、手机号、泄露数据、批量邮箱排列、SMTP spray 与来源不明数据包。
- 不自动发营销邮件或平台私信；`eligible_for_manual_review` 仅表示通过机器门禁，发送仍需人工或后续受控官方 API 决定。
- 不修改或清理当前工作区已有未提交文件，不使用 worktree。

### 资源

- Node.js 标准库、公开网站、robots.txt、可选 Hunter API。
- 当前仓库调研报告、seed CSV、深度调研与 loop design skills。

### 失败处理

- 同一域名连续两次网络失败则记录错误并跳过，不无限重试。
- 达到 max targets、max pages/domain、max runtime 或 API budget 时停止并保留 checkpoint。
- 缺 API key 时降级到公开网页抓取，不伪造 enrichment 结果。
- 法域、subscriber type、来源或验证状态不明确时进入 hold，不自动放行。

### 需要记录的状态

- 每次 run 的配置快照、开始/结束时间、处理数量、跳过原因、API credit 估算与错误。
- 每个 source URL 的抓取时间、HTTP 状态、robots 决策与内容 hash。
- 每个邮箱候选的来源、provider、验证、法域门禁、最终决策和原因。

## Claim Extraction

| Claim | 来源层级 | 独立验证通道 | 状态 |
|---|---|---|---|
| 业界已从单一数据库迁移到 multi-provider waterfall | Vendor / workflow product | 开源 workflow、迁移记录、同名单测试 | 机制与采用方向已验证；Cited Alpha 增量命中率待自有样本验证 |
| 公开官网 crawler + Finder API 能覆盖小型研究机构与企业域名联系人 | 产品推断 + vendor | 用现有 seed 与 fixture 跑通；记录覆盖缺口 | crawler 已用 3 个 seed live smoke；Finder 待 API key |
| LinkedIn/X profile scraping 是不适合长期运行的来源 | 平台条款 | 官方条款、封禁/迁移行为证据 | 官方条款已验证；实现已禁止平台抓取 |
| Verifier 可以自动做门禁，但不能判断营销授权与 inbox placement | RFC + vendor | RFC、多个 verifier 状态模型、实际失败证据 | 已验证并拆分 verification/authorization gate |
| 低依赖本地 pipeline 比直接采购 Clay 更适合首批 30–300 人 | 成本推断 | 运行成本、维护成本、工具定价与自有 pilot | 首版已零 provider 成本跑通；规模阈值需后续 pilot 校准 |
