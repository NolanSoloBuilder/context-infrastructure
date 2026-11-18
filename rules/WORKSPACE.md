# 工作区路由

需要定位资料或确定新内容落点时，从这里进入对应主题或项目。具体做法、当前状态和历史版本由对应入口维护。

## 可复用知识

- [知识库主题索引](../contexts/knowledge_base/README.md)收录 Agent Harness、铝型材 DIY、产品设计、工程与跨境账户等主题。
- [Codex 执行经验启动卡](../contexts/thought_review/codex_execution_experience_review.md)负责会话启动和专题分流。[思考与复盘](../contexts/thought_review/)记录判断形成和经验提炼过程。
- [技能索引](skills/INDEX.md)列出通用流程和技术操作。全局和项目级安装见[作用域治理](skills/skill_scope_management.md)，本机登记见 `~/.local/share/agent-skill-scopes/manifest.json`。
- [个人公理](axioms/INDEX.md)用于查长期判断原则。[动态观察](../contexts/memory/OBSERVATIONS.md)和[历史记忆任务](../periodic_jobs/ai_heartbeat/)用于追溯观察和复盘。

## 当前项目与工具

- 一次性项目和脚本进入 `adhoc_jobs/<project>/`。通用工具在 [tools/](../tools/)，周期任务在 [periodic_jobs/](../periodic_jobs/)。
- [A 股晨报](../adhoc_jobs/a_share_daily/README.md)和[美股日报](../adhoc_jobs/us_market_daily/README.md)的项目 README 各自指向现行流程、日期归档和站点发布说明。站点源码分别维护在独立 Git 仓库 `adhoc_jobs/a_share_site/` 与 `adhoc_jobs/us_market_site/`。
- [地铁打字 Web 版](../adhoc_jobs/tw_metro_typing_china/)和[打字游中国](../adhoc_jobs/china_route_typing_prototype/)是两个独立项目。小红书小工具的正式入口是 [xhs-minitools](https://github.com/NolanSoloBuilder/xhs-minitools)，本机在 `/Users/xuhao/Documents/Other/xhs-minitools/`。
- BeamJoin 的实现、规格和发布文档在 [agent-native-aluminum-platform](https://github.com/NolanSoloBuilder/agent-native-aluminum-platform)，本机在 `/Users/xuhao/Documents/Other/agent-native-aluminum-platform/`。
- 多问卷集合站的正式入口是 [quiz-hub](https://github.com/NolanSoloBuilder/quiz-hub)。原本机路径 `/Users/xuhao/Documents/Other/quiz-hub/` 当前不可用。
- `context-vault`（AI Tool Environment Sync）是独立仓库，登记路径 `/Users/xuhao/Documents/Basic/context-vault/` 当前不可用。内部 Runway API proxy 位于 `/Users/xuhao/Documents/Basic/claude-code-proxy/`，凭据和发布规则见项目说明。
- 企业 Agent 定制候选底座见 [mkagent](https://github.com/NolanSoloBuilder/mkagent)，本机在 `/Users/xuhao/Documents/Other/mkagent/`。[个人网站原型](../adhoc_jobs/xuhao_personal_site/)在本工作区。
- 项目工具见 [Chrome 书签整理](../adhoc_jobs/chrome_bookmark_cleanup/)、[Cited Alpha 联系人线索](../adhoc_jobs/cited_alpha_lead_pipeline/)和 [StrongVPN 订阅维护](skills/strongvpn-node-optimizer/references/subscription_workflow.md)。

## 调研与历史证据

- [调研记录](../contexts/survey_sessions/)保存专题结论、日期报告和核验证据。[原始资料](../contexts/source_materials/)保存外部文档、转录和附件。按主题找可复用结论时，先看知识库主题索引。
- [Cited Alpha 研究 Agent 总方案](../contexts/survey_sessions/cited_alpha_agent_redesign/README.md)和[爱室丽选品 Agent 访谈底稿](../contexts/survey_sessions/2026_09_18_ashley_assortment_discovery.md)是专题研究的入口。
- [2026 上半年绩效资料](../contexts/source_materials/2026_09_16_h1_performance/README.md)按业务域索引原文，个人总结见[本期复盘](../contexts/thought_review/2026_09_16_h1_okr_review.md)。
- [Anthropic 路演资料](../contexts/source_materials/anthropic_roadshow_2026_11_10/README.md)保留字幕、来源和编码核验记录。
- [Rimbo 归档](../contexts/rimbo/README.md)负责旧工作上下文和迁移记录。[Love User Manual 实现快照](../adhoc_jobs/love_user_manual/)保留迁移前实现，[铝型材编辑器旧 Demo](../adhoc_jobs/aluminum_editor_demo/)保留早期原型。
- [Shared Agent Workspace 内容产物](../adhoc_jobs/xhs_shared_agent_post/)保留正文、视觉规格和成图。[Mac 磁盘清理记录](../adhoc_jobs/storage_analysis_20261009/)保留快照和执行证据，[每日日志](../contexts/daily_records/)保留日期线索。

## 新文件与环境

- 新项目目录优先使用小写下划线命名。临时一次性项目可放 `adhoc_jobs/tmp_<name>/`。
- 项目依赖和运行环境以项目说明为准。需要单独的 Python 环境时，可以在项目目录建立 `.venv/`。
