# WORKSPACE.md - 目录路由速查

让 AI 每轮 session 都能快速知道"去哪里找 / 放什么"。**找任何文件前先查这里。**

## 顶层

| 路径 | 作用 | 改动规则 |
|---|---|---|
| `AGENTS.md` | AI session 入口指令 | PR + review |
| `README.md` | 仓库定位与 quick start | PR |
| `setup_guide.md` | 新成员 onboarding | PR + review |
| `.me.example` | 个人 handle 模板 | PR |
| `.env.example` | 凭据模板 | PR + review |
| `.gitignore` | 不入 git 的路径 | PR + review |

## rules/ — L3 全局约束（被动加载）

| 路径 | 作用 |
|---|---|
| `rules/SOUL.md` | rimbo AI 的人格基调 |
| `rules/TEAM.md` | 团队整体画像 |
| `rules/IDENTITY.md` | AI 怎么识别当前 caller |
| `rules/COMMUNICATION.md` | 沟通风格指南 |
| `rules/WORKSPACE.md` | 本文件 |
| `rules/members/INDEX.md` | 当前成员清单 |
| `rules/members/<handle>.md` | 单个成员 profile（按需加载） |
| `rules/members/_template.md` | 新成员 profile 模板 |
| `rules/axioms/team/` | 团队公理（从空累积） |
| `rules/axioms/_reference_grapeot/` | 上游 grapeot 公理（**默认不加载**） |
| `rules/skills/` | 可复用能力指南 |
| `rules/skills/INDEX.md` | skill 总览 |
| `rules/skills/_reference_grapeot/` | 上游 grapeot skills（**默认不加载**） |

`rules/` 任何文件修改必须走发布 skill + review。

## contexts/ — 产物与记忆

按"产物语义"分目录，不按"创建者"分。

| 路径 | 作用 | 写入 |
|---|---|---|
| `contexts/products/<product>/prd/` | 产品需求文档 | owner 直接 / 非 owner PR |
| `contexts/products/<product>/rfc/` | 设计提案 | 同上 |
| `contexts/products/<product>/decisions/` | 产品 ADR | 同上 |
| `contexts/planning/okr/<quarter>/` | OKR | 个人段直接 / 团队 PR |
| `contexts/planning/weekly/<yyyy-ww>/` | 周报、周会纪要 | 个人段直接 / digest PR |
| `contexts/planning/decisions/` | 管理类决策 | PR + review |
| `contexts/research/user_research/` | 用研报告 | PR auto-merge |
| `contexts/research/experiments/` | 实验记录 | PR auto-merge |
| `contexts/research/feedback/` | 用户反馈 | PR auto-merge |
| `contexts/glossary/` | 术语表 | PR auto-merge |
| `contexts/capabilities/<cap>/CAPABILITY.md` | 能力卡片 | 创建/frontmatter 变更必须 review |
| `contexts/capabilities/<cap>/interface.md` | 调用契约 | 契约变更必须 review |
| `contexts/capabilities/<cap>/changelog.md` / `examples/` | 版本/示例 | PR auto-merge |
| `contexts/repos/INDEX.md` | Mindspace org 仓库速查表 | PR auto-merge |
| `contexts/repos/<repo>.md` | 单仓库速览卡片（角色/栈/owner/关系） | PR auto-merge |
| `contexts/team_config.yml` | 团队级运行时配置（默认通知群、wiki space 等） | PR + review（敏感） |
| `contexts/lark_mirror/<space>/<doc>.md` | Lark wiki 文档镜像（只读） | 仅 lark_sync 写 |
| `contexts/lark_mirror/chats/<chat_alias>/<since>_<until>.md` | Lark 群聊历史镜像（只读） | 仅 `tools/lark_cli/chat_pull.sh` 写 |
| `contexts/memory/OBSERVATIONS.md` | 团队全局观察（append-only） | reflector PR |
| `contexts/memory/people/<handle>/` | 个人私域记忆 | 单作者直接 commit |
| `contexts/survey_sessions/` | 深度调研（来自 deep research workflow） | PR auto-merge |
| `contexts/thought_review/` | 团队复盘 | PR auto-merge |
| `contexts/daily_records/` | 日常记录 | 单作者直接 |

## periodic_jobs/ — 定时任务

每个人在自己机器上配 cron。

| 路径 | 频率 | 输出 |
|---|---|---|
| `periodic_jobs/ai_heartbeat/observer.py` | 每日 | 写 `contexts/memory/people/<handle>/`，直接 commit |
| `periodic_jobs/ai_heartbeat/reflector.py` | 每周（错峰） | 提议追加 `OBSERVATIONS.md` 和 `axioms/team/`，走 PR |
| `periodic_jobs/lark_sync/run.py` | 每 6h（带 stale 检查） | 同步 `contexts/lark_mirror/`，走 PR |
| `periodic_jobs/digest/run.py` | 每周 / 每日 | 推 Lark 群（不写 git，骨架） |
| `periodic_jobs/_lib/` | — | 共享:`.me` 解析、本机 AI CLI 调用、`workflow_publish` 包装 |
| `periodic_jobs/ai_heartbeat/src/v0/` | — | grapeot 上游实现，仅参考 |

错峰约定见 `docs/COLLAB_PROTOCOL.md`。

## tools/ — 通用工具

| 路径 | 作用 |
|---|---|
| `tools/semantic_search/` | 语义检索（覆盖 contexts + lark_mirror） |
| `tools/lark/lark_client.py` | Lark 自建应用 client（token + Wiki/Docs/IM API） |
| `tools/lark/lark_doc_pull.py` | 拉单篇 docx 为 markdown（CLI） |
| `tools/lark/lark_doc_push.py` | 把本地 markdown 写回 docx（前置:repo clean + push 到 main） |
| `tools/lark/lark_im_send.py` | 发送 IM 文本消息（CLI，应用身份） |
| `tools/lark/lark_sync.py` | 同步 wiki space → `contexts/lark_mirror/`（带 stale check） |
| `tools/lark_cli/chat_pull.sh` | **拉群聊历史**为 markdown 镜像（OAuth 个人身份；落 `contexts/lark_mirror/chats/`） |
| `tools/lark_cli/{pull,push,im_send,whoami}.sh` | lark-cli 主路径包装器（PRD 拉/推、IM、身份验证） |
| `tools/_reference_grapeot/` | 上游个人创作者向工具（**不调用**） |

## adhoc_jobs/ — 个人临时项目

`adhoc_jobs/<handle>/<project>/` — 单作者，直接 commit。长大后再决定升级到 `tools/` 或 `contexts/products/`。

## docs/ — 元文档

| 文件 | 作用 |
|---|---|
| `docs/RIMBO_REDESIGN.md` | 改造方案总文档 |
| `docs/COLLAB_PROTOCOL.md` | 协作协议 |
| `docs/EXTERNAL_REPOS.md` | 外部仓库本地镜像协议（`external_repos/` 怎么 fetch / 读） |
| `docs/CRONTAB.md` | 各人本机 cron 配置范例 |
| `docs/ARCHITECTURE.md` | 架构图与数据流（Phase 2 完善） |
| `docs/ONBOARDING.md` | 新成员上手（Phase 2 完善） |

## external_repos/ — 外部仓库本地镜像（不入 git）

| 路径 | 作用 |
|---|---|
| `external_repos/<repo>/` | Mindspace-ai 组织代码仓库的本地工作镜像，按需 clone |

**AI 使用规则**：涉及某仓库源码时按需 clone，已存在则只 `git fetch`（**不 merge / 不 pull**），读取统一用 `origin/main`。完整协议见 `docs/EXTERNAL_REPOS.md`。

## 命名规则

- 目录与文件名：snake_case（小写 + 下划线）
- 临时项目：`adhoc_jobs/<handle>/tmp_<name>/`
- 时间相关：日期 `YYYY-MM-DD`，季度 `YYYYqN`，周 `YYYY-w<NN>`，时段 `YYYY-MM-DD-HH`
- 分支：`feat/<purpose>-<handle>-<timestamp>`（详见 `docs/COLLAB_PROTOCOL.md`）

## 找文件的标准动作

1. 先看本路由表
2. 路由表里没有 → 看 `contexts/capabilities/INDEX.md`（找能力时）/ `contexts/repos/INDEX.md`（找代码仓库时）
3. 还没有 → grep / glob，但**先告诉 AI 你在找什么类别**避免乱翻
4. 找到位置但发现新增了未登记的子目录 → 顺手更新本路由表（chore PR）

## 关键问题速查

| 问题 | 第一站 |
|---|---|
| 团队是谁、在做什么、当前阶段 | [`rules/TEAM.md`](./TEAM.md) |
| 当前 caller 是谁、怎么写归属 | [`rules/IDENTITY.md`](./IDENTITY.md) + [`rules/members/`](./members/) |
| Rimbo.ai 产品文档怎么找 | [`contexts/products/rimbo/README.md`](../contexts/products/rimbo/README.md) |
| 团队最近在群里讨论什么 | [`contexts/lark_mirror/chats/`](../contexts/lark_mirror/chats/)（用 `tools/lark_cli/chat_pull.sh` 增量拉新窗口） |
| 飞书 wiki 上的 PRD / 调研 | [`contexts/lark_mirror/产品调研/`](../contexts/lark_mirror/产品调研/) + `研发部门/` |
| Mindspace org 代码仓库速查 | [`contexts/repos/INDEX.md`](../contexts/repos/INDEX.md) |

## Python 环境

- 根目录 `.venv/` 工作区级环境，用 `uv pip install` 管理依赖
- 需要隔离时在 `adhoc_jobs/<handle>/<project>/.venv/` 建独立环境
