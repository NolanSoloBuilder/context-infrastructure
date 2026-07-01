# Rimbo Work Context Overview

更新日期：2026-06-17

来源：`/Users/xuhao/Documents/Other/rimbo-work-context` 本地仓库。2026-06-17 已将原仓关键上下文迁入 `contexts/rimbo/`。本文是调研型总览；后续工作入口以 `contexts/rimbo/README.md` 为准。

## 一句话

Rimbo.ai 是 Mindspace-ai 旗下 rimbo 团队正在做的 AI 个人信息助手。核心形态是用户用 `Channel` 定义关注问题或任务，系统跨平台 follow `Source`，捕捉 `Change`，解释 `Importance`，保留 `Evidence`，最后沉淀为 `Memory`。

当前阶段是 MVP / 阶段一 Track：先验证 AI + 订阅 > 订阅，让用户不再错过关键变化，能 follow，能在频道中持续沉淀。

## 原仓入口

- 当前入口：`contexts/rimbo/README.md`
- 迁移清单：`contexts/rimbo/MIGRATION_MANIFEST.md`
- 原仓路径：`/Users/xuhao/Documents/Other/rimbo-work-context`（deprecated source）
- AI 入口：`AGENTS.md`
- 团队画像：`contexts/rimbo/imported/rules/TEAM.md`
- 目录路由：`contexts/rimbo/imported/rules/WORKSPACE.md`
- 产品入口：`contexts/rimbo/imported/contexts/products/rimbo/README.md`
- 仓库速查：`contexts/rimbo/imported/contexts/repos/INDEX.md`
- Lark 镜像：`contexts/rimbo/imported/contexts/lark_mirror/`
- Lark CLI：`contexts/rimbo/imported/tools/lark_cli/README.md`

后续处理 Rimbo 事项时，从当前 `contexts/rimbo/` 读上下文。原仓规则已作为历史快照保留；新增长期上下文应写入当前空间。

## 产品模型

核心对象：

- `Channel`：用户定义的长期跟进容器，围绕一个问题、项目或任务组织信息。
- `Source`：频道订阅的内容来源，包括 RSS、邮件订阅、播客、YouTube、Twitter、公众号、自定义站点等。
- `Change`：信源中出现的、相对频道目标值得告知用户的信息增量。
- `Importance`：系统解释为什么这条变化值得看。
- `Evidence`：重要性判断背后的可回溯原文、引用或出处。
- `Memory`：频道长期沉淀下来的判断和上下文。

用户闭环：Define -> Follow -> Track -> Explain -> Confirm -> Memory。其中 MVP 阶段主要做前四步，`Memory` 是后置能力。

## 阶段边界

Rimbo 的产品规划分三段：

1. Track：围绕用户的主题、问题或任务创建频道，接入信源并持续产出更新；用频道简报告诉用户发生了什么变化、为什么重要、原文在哪。
2. Archive：把跟进沉淀成判断。除了外部更新，开始融合截图、谈话、链接等用户私域碎片，把零散信息归入频道。
3. Network：频道变成可分享、可共建、可分发的研究资产。

当前只应围绕 Track 做判断。协作、分享、发布和团队级账户不是 MVP 重点。

## 重要产品判断

Rimbo 不是通用搜索引擎，也不是内容平台。它针对的是主动 follow 和长期沉淀：用户不是来问一次性问题，而是围绕一个长期关注对象持续追踪。

它也不是传统 RSS reader 的简单增强版。RSS/Newsletter/Podcast/Twitter/YouTube 只是 `Source` 层，真正的产品价值在于围绕 `Channel` 做跨源聚合、重要性判断、证据链和长期记忆。

目前更明确的切入场景偏专业/高价值信息场景，尤其包括投资人、互联网从业者、AI/技术/产品研究等。文档中反复出现的金融/投资人方向，不是为了做行情终端，而是为了验证高质量一手信源、证据权重和主题追踪的价值。

## 信源系统

信源库是 Rimbo 的关键资产。目标不是尽可能多地列 URL，而是为目标主题提供结构全面、高质量、可信、可解释的信源集合。

信源库需要服务两个场景：

- 频道创建时，给用户一组可解释的默认信源池。
- 阅读与提取时，按信源形态适配不同处理模板。

重要字段包括：

- 基础：`source_id`、`name`、`logo_url`、`canonical_url`
- 形态：`source_type`、`formats`、`reading_template`
- 主题理解：`theme_tags`、`audience_fit`、`source_summary`
- 发布者：`publisher_name`、`publisher_type`
- 权威信号：`authority_signals`、`perspective_type`
- 质量与状态：`source_quality_score`、`last_success_at`、`status`
- 来源治理：`seed_source`

对投资人，`source_tier` 用来区分信号在投资决策中的证据权重，`source_origin` 用来判断证据链是否完整，`source_type` 决定系统应该如何提取和展示。

## 技术与代码仓库

Rimbo 不是一个单仓产品。原仓维护的 Mindspace-ai 仓库拓扑如下：

- `mindspace_web_frontend`：Rimbo 品牌站 + 产品 web app，一体化前端。
- `mindspace_app`：移动端 App，Expo / React Native。
- `mindspace_backend`：主业务后端，处理用户、频道、订阅，并代理 ML 端 HTTP/SSE。
- `mindspace_ml_backend`：AI / 数据侧后端，包含对话、画像、抓取、信源发现、向量检索和第三方集成。
- `mindspace_local_sql`：信源发现和本地 SQL review 工具，写 Azure 源数据库。
- `mindspace_user_simulator`：本地用户模拟器，用 persona 做评测和研发验证。
- `mindspace_info_source`：已归档的 Codex actor/prune 信源发现工具，疑似被 `mindspace_local_sql` 替代。
- `rimbo-work-context`：团队上下文系统，存规则、记忆、技能、Lark 镜像和定时任务。

关键边界：`mindspace_backend` 的业务 MySQL 与 `mindspace_local_sql` 写入的 Azure 源数据库是两套独立数据库。`mindspace_ml_backend` 是事实上的内部公共能力库，被 backend、local_sql、user_simulator 多处复用。

## Rimbo Work Context 本身

`rimbo-work-context` 是一个团队上下文仓，不是常驻服务。它的设计是共享 workspace + 各自 AI 客户端：每个人在本机用 Codex / Claude Code / OpenCode / Cursor 打开同一个仓库，git 是同步协议，PR 是协作机制。

核心目录：

- `rules/`：L3 全局约束，包含团队画像、身份识别、沟通规则、路由表和 skills。
- `contexts/`：产品文档、规划、调研、能力卡片、Lark 镜像、记忆、仓库索引。
- `tools/lark_cli/`：基于 `@larksuite/cli` 的个人 OAuth Lark 操作主路径。
- `periodic_jobs/`：observer、reflector、lark_sync、digest 等定时任务。
- `adhoc_jobs/<handle>/`：个人临时任务。

重要约束：

- `contexts/lark_mirror/` 是 Lark 镜像，只读，手动修改会被同步覆盖。
- Lark 写回必须先经过 git：本地改动 commit、push、merge 后，才能推回 Lark。
- `rules/`、`contexts/team_config.yml`、capability 契约等影响团队 AI 行为的文件要走 review。
- capabilities 目前仍为空骨架，候选方向是 `source_infra`、`lark_bridge` 等。

## Lark 与飞书镜像

原仓已经有大量 Lark 文档镜像：

- `contexts/lark_mirror/产品调研/`：产品规划、MVP、PRD、信源、Prompt、用研、竞品等。
- `contexts/lark_mirror/研发部门/`：后端、架构、API、测试、开发文档等。
- `contexts/lark_mirror/chats/`：`rimbo_core`、`rimbo_dev`、`mindspace`、`deploy` 的近 30 天聊天镜像。

读 Lark 的默认路径是 `tools/lark_cli/pull.sh`，它比裸跑 `lark-cli` 更稳。历史经验里，wiki 主体可能只是外壳，正文可能藏在嵌入 sheet/base 中；看到 `<sheet>`、`<bitable>` 一类块时，要继续下钻，而不是把 wiki markdown 当成完整正文。

## 后续在当前空间里的使用方式

如果要回答 Rimbo 产品方向问题，优先读：

1. 本文。
2. `contexts/rimbo/README.md`。
3. `contexts/rimbo/imported/rules/TEAM.md`。
4. `contexts/rimbo/imported/contexts/products/rimbo/README.md`。
5. `contexts/rimbo/imported/contexts/lark_mirror/产品调研/产品规划.md`。
5. 需要具体模块时再读对应 PRD。

如果要回答代码实现路径，优先读：

1. `contexts/rimbo/imported/contexts/repos/INDEX.md`。
2. 对应 `contexts/rimbo/imported/contexts/repos/<repo>.md`。
3. 如果要看真实代码，先重新校准当前代码仓状态，不要直接凭 repo card 下结论。

如果要处理 Lark 文档，优先读：

1. `contexts/rimbo/imported/tools/lark_cli/README.md`。
2. `contexts/rimbo/imported/rules/skills/lark_read.md` 或 `lark_write.md`。
3. 本机授权状态。

## 待刷新事项

- 原仓仓库卡片的 `last_reviewed` 多数是 2026-05-18，可能已过期；涉及当前真实代码路径时要重新校准。
- `contexts/capabilities/` 仍为空，尚未把 source infra / lark bridge 等能力沉淀成正式契约。
- 团队成员 profile 中多份仍标为 AI 代写骨架，涉及个人偏好时要以本人最新表述为准。
- 若要把 Rimbo 的活跃 PRD 从 Lark 迁移成 repo-native 文档，应在当前 `contexts/rimbo/` 下提炼新文档，不再写回原 `rimbo-work-context`。
