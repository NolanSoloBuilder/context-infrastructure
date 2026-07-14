# Search Manifest

日期：2026-07-14

## 产出文件索引

| 文件 | 路径 | 说明 |
|---|---|---|
| Scratchpad | `tmp/cited_alpha_target_email_research_20260714/scratchpad.md` | Claim extraction 与研究边界 |
| Search Manifest | `tmp/cited_alpha_target_email_research_20260714/search_manifest.md` | 研究覆盖与 Agent 索引 |
| 自动化行业路线 | `tmp/cited_alpha_target_email_research_20260714/industry_automation_landscape.md` | 自动抓取工作流、产品边界、开源组件、许可证与长期代码架构 |
| 最终报告 | `contexts/survey_sessions/cited_alpha_target_email_acquisition_survey_20260714.md` | 邮箱发现、验证、合规与工具选择 |

## 研究覆盖

- 第一方公开联系方式发现路径
- 姓名 + 域名的工作邮箱推断与验证
- Hunter、Apollo、Prospeo、Clay 等工具的能力、成本与适用边界
- 单一供应商与 waterfall enrichment 的覆盖率、可解释性和风险
- Opt-in 获取方式及 CRM 字段、suppression 和人工审批
- n8n、Clay、Apollo、Hunter、FullEnrich、BetterContact、Apify 的自动化边界
- Crawlee、Scrapy、Crawl4AI、Firecrawl、Activepieces、Reacher、Mautic、listmonk 的许可证与维护状态

## Subagent 原始产出

| Agent | Agent path | 范围 | 状态 |
|---|---|---|---|
| email_providers | `/root/email_providers` | 邮箱发现与供应商对比 | completed |
| email_validation | `/root/email_validation` | 验证、投递与独立行为证据 | completed |
| email_compliance_optin | `/root/email_compliance_optin` | 合规、数据来源与 opt-in 获取 | completed |
