# Search Manifest

## 产出文件索引

| 文件 | 路径 | 说明 |
|---|---|---|
| Scratchpad | `tmp/app_store_web_niche_20260717/scratchpad.md` | claim、数据覆盖和矛盾记录 |
| Search Manifest | `tmp/app_store_web_niche_20260717/search_manifest.md` | 本文件 |
| 工作流 | `adhoc_jobs/app_store_web_niche_pipeline/` | 采集、补全、评分、评论与报告脚本 |
| 计划 | `contexts/survey_sessions/2026_07_17_app_store_mid_rank_web_niche_plan.md` | 30 天执行计划 |
| 首轮报告 | `contexts/survey_sessions/2026_07_17_app_store_web_niche_first_scan.md` | 第一轮 live 数据与机会判断 |

## Subagent 原始产出

| Agent | 定位 | 状态 |
|---|---|---|
| `/root/chart_data_research` | 实测 Apple v2/legacy/Lookup，核对 AppTweak/Appfigures 官方合同与降级顺序 | completed |
| `/root/web_feasibility_rules` | Browser API capability matrix 与 hard reject | completed |
| `/root/live_candidate_scan` | 独立复核 Productivity 免费榜前 20；确认榜首被大型平台占据，应转向 paid 30–100 | completed |

## 数据覆盖

- Market：US iPhone
- Date：2026-07-17
- Charts：free、paid、grossing
- Categories：overall、Business、Utilities、Reference、Productivity、Photo & Video、Music、Health & Fitness、Education、Graphics & Design
- Public depth：每个榜单最多 100；更深榜单 adapter 尚未接入付费数据源
- Integrity：free/paid 分类按 `feed.title` 校验；legacy grossing 分类标记 `legacy_unverified_category`
- Generated data：本地 `adhoc_jobs/app_store_web_niche_pipeline/data/`，由 `.gitignore` 排除，可重跑
