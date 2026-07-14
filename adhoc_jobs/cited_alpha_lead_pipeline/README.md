# Cited Alpha Contact Acquisition Pipeline

这是一个来源可追溯的联系人触达入口采集项目。输入目标机构域名，系统自动查找：

- 官网公开的工作邮箱、职能邮箱与明确用于商务联系的创作者邮箱；
- 官方 Contact 表单和预约链接；
- 官网明确链接出的 LinkedIn/X 主页；
- 可选 Hunter Finder / Domain Search 返回的工作邮箱；
- 邮箱验证状态、来源、法域门禁和最终处理队列。

它不抓取 LinkedIn/X 页面，不绕登录或验证码，不从泄露数据或私人数据包获取信息，也不自动发送邮件或私信。

## 工作流

```text
目标机构 CSV
  -> 输入与来源校验
  -> robots.txt + SSRF 门禁
  -> 官网 Contact/About/Team/Research 页面抓取
  -> 联系表单/预约/邮箱/官网社交链接提取
  -> 没有公开邮箱时调用 Hunter
  -> 工作邮箱验证
  -> 来源、邮箱类型、法域与营销许可门禁
  -> eligible_for_manual_review / holds / rejected
  -> JSONL 审计事件与周期运行 checkpoint
```

社交主页只会生成 `NATIVE_PLATFORM_MANUAL_ONLY` 队列。以后若接入 LinkedIn Lead Sync、X API 或其他官方 API，仍需在平台授权和用户许可范围内发送。

## 环境

- Node.js 22+
- 运行时依赖只有 `csv-parse` 和 `parse5`
- Hunter API 可选；不配置 key 时仍能运行官网采集

安装：

```bash
npm install
cp .env.example .env
```

把 `.env` 中的 `BOT_CONTACT` 改成真实、可监控的产品联系页。需要 Hunter 时再配置 `HUNTER_API_KEY`。

## 输入

参考 [examples/targets.csv](./examples/targets.csv)。核心字段：

| 字段 | 必填 | 用途 |
|---|---|---|
| `target_id` | 否 | 稳定业务 ID；缺失时自动生成 |
| `company` | 否 | 机构名称 |
| `domain` | 是 | 只允许机构官网域名，不能填 LinkedIn/X |
| `website_url` | 否 | 官网入口；不填时使用 `https://<domain>` |
| `person_name` | 否 | 有值时 Hunter 使用 Finder；无值时使用 Domain Search |
| `input_email` | 否 | 已经合法取得的候选邮箱 |
| `email_source_url` | 有邮箱时 | 邮箱真实来源 |
| `country` | 建议 | `US`、`UK/GB`、EU 国家代码等 |
| `subscriber_type` | UK 建议 | `corporate/sole_trader/partnership/unknown` |
| `discovery_channel` | 建议 | 发现线索的渠道；不等于邮箱来源 |
| `proof_url` | 建议 | 为什么这个目标属于 ICP |
| `acquisition_source_type` | 是 | 如 `official_company_website/first_party_optin/inbound` |
| `marketing_permission` | 建议 | `opt_in/inbound/corporate_rule/unknown` |
| `consent_event_id` / `consented_at` / `consent_text_version` | opt-in 必填 | 一方同意事件、发生时间和当时的同意文本版本 |
| `inbound_event_id` / `inbound_at` | inbound 必填 | 一方入站事件和发生时间 |
| `can_spam_ready` | US | 发件身份、实体地址、退出和 suppression 是否就绪 |
| `privacy_notice_ready` | UK/EU | 透明告知是否就绪 |

明确禁止的 `acquisition_source_type` 会直接拒绝，包括 `linkedin_scraped`、`x_scraped`、`browser_extension_export`、`bulk_email_permutation`、`smtp_spray`、`breach_or_dump` 和 `broker_without_provenance`。

## 使用

先验证输入：

```bash
node src/cli.mjs validate --input examples/targets.csv
```

只运行官网流程，不消耗 provider credits：

```bash
node src/cli.mjs run \
  --input examples/targets.csv \
  --output data/pilot \
  --dry-run
```

配置 Hunter 后运行完整流程：

```bash
node src/cli.mjs run \
  --input examples/targets.csv \
  --output data/pilot \
  --max-targets 100 \
  --max-api-calls 100
```

每次运行生成独立目录：

```text
data/pilot/
  events.jsonl
  latest.json
  runs/<run_id>/
    eligible_for_manual_review.csv
    holds.csv
    rejected.csv
    page_evidence.json
    manifest.json
```

文件默认使用 `0600`，运行目录使用 `0700`。`events.jsonl` 只保存 target fingerprint、计数和状态，不保存联系人明文。

## 决策含义

- `eligible_for_manual_review`：入口来源明确并通过基础机器规则，但仍然不能自动发送。
- `hold`：验证、法域、实体类型、来源或许可不完整。
- `reject`：私人/无效邮箱、域名不匹配、禁止来源或明确不可投递。

公开联系表单、预约页和官网链接的社交主页可以进入人工触达审核；社交私信只能在平台原生界面或获批官方 API 内完成。邮箱则必须同时通过可投递性与地区规则。

## 周期运行

[schedule/cron.example](./schedule/cron.example) 提供工作日定时示例。同一个输出目录会复用 `events.jsonl`；默认 30 天内完成过的 target 会跳过，避免重复抓取和重复消耗 API credits。每次运行仍生成新的 run 目录，不覆盖上一次结果。

停止条件可以通过环境变量或 CLI 控制：

- `MAX_TARGETS`
- `MAX_PAGES_PER_DOMAIN`
- `MAX_RUNTIME_SECONDS`
- `MAX_API_CALLS`
- `REQUEST_DELAY_MS`
- `REFRESH_AFTER_DAYS`
- `PROVIDER_CACHE_DAYS`
- `VERIFICATION_CACHE_DAYS`

任何 robots 5xx/超时、SSRF 命中、API budget 耗尽和未知法域都不会被系统静默放行。

## 测试

```bash
npm test
```

当前测试覆盖 CSV、HTML 联系入口提取、外域职能邮箱、newsletter/外站表单误判、robots 最长规则与编码路径、SSRF 私网/NAT64 阻断、法域/来源门禁、可审计同意事件、suppression fail-closed、验证 TTL、锁恢复、文件权限、输出队列和重复运行 checkpoint。

## 尚未实现

- Bouncer、FullEnrich、BetterContact adapter；
- CRM upsert 与全局 suppression 服务；
- LinkedIn Lead Sync / X Search Posts 等获批官方 API；
- provider 级 webhook、异步任务和 circuit breaker；
- 自动发送。自动发送不是这个项目默认目标。
