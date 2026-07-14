# WORKSPACE.md - 目录路由速查

目标：让 AI 每轮 session 都能快速知道"去哪里找/放什么"。**找任何文件前先查这里。**

## 路由规则

### 项目与代码
- 写代码 / 跑脚本 / 一次性项目：`adhoc_jobs/<project>/`
- 工具脚本（邮件、语义搜索、分享报告等）：`tools/`
- 定时任务：`periodic_jobs/`

### 知识与记录
- 通用调研报告：`contexts/survey_sessions/`
- 外部原始资料 / 本地文档归档：`contexts/source_materials/`
- 二次理解后的结构化知识卡片：`contexts/knowledge_base/`
- Rimbo 归档上下文：`contexts/rimbo/`
- 思考 / 复盘 / 方法论：`contexts/thought_review/`
- 每日日志：`contexts/daily_records/`

### 系统与规则
- 可复用技术方案 / Skill：`rules/skills/`
- 核心公理（Axioms）：`rules/axioms/`
- 记忆系统：`contexts/memory/` + `periodic_jobs/ai_heartbeat/`

## 命名规则
- 目录和文件名：小写 + 下划线 (snake_case)
- 临时一次性项目：`tmp_<name>/`

## Python 环境
- 根目录 `.venv/` 为工作区级环境，用 `uv pip install` 管理依赖
- 需要隔离时在 `adhoc_jobs/<project>/.venv/` 建独立环境

## 快速查询

<!-- 随着你的项目增长，在这里添加活跃项目的快捷路由 -->
<!-- 格式：- `project-name` → `adhoc_jobs/project_name/` (说明) -->
- `rimbo` / `rimbo-work-context` → `contexts/rimbo/README.md`（原 `rimbo-work-context` 已迁入当前空间；迁移清单见 `contexts/rimbo/MIGRATION_MANIFEST.md`）
- `chrome-bookmark-cleanup` → `adhoc_jobs/chrome_bookmark_cleanup/`（Chrome 书签整理脚本、备份和整理预览）
- `cited-alpha-lead-pipeline` → `adhoc_jobs/cited_alpha_lead_pipeline/`（公开联系人入口抓取、Hunter enrichment、验证与法域门禁）
- `china-metro-typing` → `adhoc_jobs/tw_metro_typing_china/`（基于 tw-metro-typing fork 的中国 41 城地铁站名打字游戏）
- `context-vault` / `AI Tool Environment Sync` → `/Users/xuhao/Documents/Basic/context-vault/`（独立 GitHub 仓库；不要放入当前 workspace 的 `adhoc_jobs/`）
- `xuhao-personal-site` → `adhoc_jobs/xuhao_personal_site/`（徐昊个人网站原型；全屏横向叙事、作品集与近况）
