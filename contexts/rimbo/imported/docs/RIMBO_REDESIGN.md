# Rimbo Work Context 改造方案

本文档记录把这个仓库从 grapeot 个人 context infrastructure 改造为 rimbo 团队多人协作上下文空间的设计决定。改造形态是**共享 workspace + 每人各自 AI 客户端**：仓库本身是单一事实源，每个人在自己机器上 clone，用 Codex / Claude Code / OpenCode / Cursor 打开它工作。git 是同步协议，PR 是协作机制，没有常驻 agent 服务。

下面分六节：目录结构与各自作用、文件更新工作流（多人写入怎么不打架）、个人日常工作流（一个人一天怎么用这个仓库）、改造执行顺序、能力交付物（capabilities）的设计、明确不做的决定。

---

## 一、目录结构与作用

仓库分四层：身份与规则（`rules/`）、产物与记忆（`contexts/`）、定时任务（`periodic_jobs/`）、工具与代码（`tools/` + `adhoc_jobs/`）。每一层的设计意图不同，下面逐个说。

### 顶层

`AGENTS.md` 是 AI 每次 session 的入口指令。任何 AI 客户端打开仓库都先读这个文件，从而被引导去读 `rules/IDENTITY.md`（弄清当前 caller 是谁）、`rules/SOUL.md`（人格基调）、`rules/TEAM.md`（团队画像）、`rules/WORKSPACE.md`（路由表）、`rules/skills/INDEX.md`（能力清单）。

`README.md` 给人读，说明仓库定位、quick start 入口、整体架构链接。

`setup_guide.md` 是新成员的 onboarding 路径，从 clone 到能用起来分步骤走。配套 `.me.example` 和 `.env.example`：每个人本地 `cp .me.example .me` 填自己的 handle，`cp .env.example .env` 填自己的密钥（或者用 1Password CLI 走团队 vault）。两个文件都不入 git。

### `rules/` ——L3 全局约束

这一层是被动加载的硬性约束，每次 session 启动 AI 都会读。改动这一层影响所有人，所以 `rules/` 下的任何修改都必须走 PR + review，不允许 AI 直接 commit 到 main（细节在第二节工作流里讲）。

`SOUL.md` 是 rimbo 这个 AI 的人格基调——直接、有观点、不说废话、协作而非服从。这是团队层面的共识，不是个人风格。

`TEAM.md` 替代了原来的 `USER.md`，描述 rimbo 团队整体：在做什么产品、价值观是什么、术语习惯、对 AI 输出的期待。新成员加入时第一个看的就是它。

`IDENTITY.md` 是新增的关键文件，告诉 AI 怎么识别"现在和我对话的是谁"。流程是读本地 `.me` 文件拿到 handle，然后加载对应的 `rules/members/<handle>.md` 和 `contexts/memory/people/<handle>/`。识别失败按 guest 处理，不加载个人画像。

`members/` 是每个核心成员的 profile 目录。一人一份 markdown，写明：负责什么、技术偏好、沟通风格、避雷点。这个文件由本人维护，别人不动。`INDEX.md` 列出当前所有成员，新人入职时往这里加一条。

`COMMUNICATION.md` 是沟通风格指南，主要用于非编程任务（写 PRD、调研报告、群聊回复）。原仓库这部分已经很完整，保留，只去掉 grapeot 个人化的反例。

`WORKSPACE.md` 是路由表：找文件之前先查这里，知道每类内容放哪。多人协作下这个文件比单人时更重要，因为一个不熟悉仓库的人的 AI 如果到处 glob/grep，很容易把错的位置当成"应该在这里"，污染产物。

`axioms/` 是从经历中蒸馏的决策原则。改造后分两个子目录：`_reference_grapeot/` 装上游 43 条公理，**默认不加载**，只在显式问"鸭哥怎么看"或想找参考时查阅；`team/` 由 rimbo 团队从空开始累积，由 reflector 提议、人 review 通过后晋升。`INDEX.md` 顶部明确写清这个分层。

`skills/` 是 AI 可复用能力。同样分两层：通用的 `bestpractice_*` 和工程类 `workflow_*` 留在原位（这些真的可复用），创作者向的（typefully、kit、ga4_metrics、share_report、send_email_to_myself）下沉到 `_reference_grapeot/`。新增三个核心 skill：

- `workflow_publish.md`——AI 改东西后怎么走分支 + PR + 自动 merge，是整个协作流的关键。
- `lark_read.md` / `lark_write.md`——AI 怎么实时读写 Lark 文档。
- `memory_write.md`——AI 怎么把今日观察写到自己的 `people/<handle>/`。

### `contexts/` ——产物与记忆

这一层是团队真正的资产沉淀，绝大多数日常工作都落到这里。按"产物的语义"分目录，不按"创建者"分。

`memory/` 装动态记忆。`OBSERVATIONS.md` 是团队全局观察池，**严格 append-only**——任何人（包括 AI）不允许编辑历史条目，只能追加新条目，整理工作由每周 reflector 统一做（删旧 + 写晋升后的新条目，git history 留痕）。`people/<handle>/` 是每个人的私域记忆，由本人的 AI 写、本人负责。AI 在和某人对话时只加载这一份，不加载别人的，避免上下文污染。如果未来需要按产品维度的累积观察，可以加 `products/<product>/observations.md`，但 Phase 1 先不上。

`products/<product>/` 装产品规划相关的结构化文档：`prd/` 放产品需求、`rfc/` 放设计提案、`decisions/` 用 ADR 风格一条决策一个文件。每个文件 frontmatter 标 `owner`，owner 是默认的修改人。

`planning/` 装管理向产物：`okr/<quarter>/`、`weekly/<yyyy-ww>/`、`decisions/`（管理类决策，比如人事、资源、方向，与 products/decisions 区分）。

`research/` 装数据与调研产物：`user_research/`（用研报告）、`experiments/`（AB 实验记录）、`feedback/`（用户反馈）。

`glossary/` 是术语表和命名约定，多人协作必备，避免大家口里的"用户"指向不同对象。

`lark_mirror/` 是从 Lark 拉下来的 markdown 镜像，**只读**——任何人手改这里的内容会被下次同步覆盖。`_meta.json` 记录每个文件对应的 Lark obj_token、版本号、最后同步时间。这份镜像主要服务于 semantic_search 和离线检索。任何 AI 需要某份 Lark 文档的最新版本时，直接调 `tools/lark/lark_doc_pull.py` 实时拉，不依赖镜像新鲜度。

`capabilities/<capability>/` 装项目阶段交付出来的"能力"（capability）。例子：信源基础设施 v1（能从 RSS / Lark / API 拉取并去重）、用户画像服务 v0、内容打分模型 v2。这是新增的核心目录，第六节专门展开。简单说，每个 capability 是一份"对内的能力卡片"，记录这个能力当前能做什么、怎么调用、谁维护、版本到了哪、依赖了什么。实现代码可能在 `tools/<capability>/`、其他仓库、甚至外部 SaaS——`contexts/capabilities/` 是它的目录入口和契约。AI 和团队成员都通过这里发现和组装能力。

`survey_sessions/`（调研报告）、`thought_review/`（团队复盘）、`daily_records/`（日常记录）从原仓库继承，语义从个人迁到团队。

### `periodic_jobs/` ——定时任务

每个人在自己机器上配 cron 跑这些任务。任务都通过发布 skill 走分支 + PR。

`ai_heartbeat/observer.py`——每日扫描当日变化的文件，AI 做语义抽取写到 `contexts/memory/people/<我的 handle>/` 下。因为是单作者目录，可以直接 commit 到 main，不走 PR。

`ai_heartbeat/reflector.py`——每周从 `people/*/` 和近期产物里蒸馏出有跨人价值的观察，**必须走 PR**：写到 `feat/reflect-<handle>-<yyyy-ww>` 分支，对全局 `OBSERVATIONS.md` 的追加和对 `axioms/team/` 的提议都打包进同一个 PR。

`lark_sync/`——同步选定的 Lark wiki space 到 `lark_mirror/`。任何人都能跑，但**跑前先看 `_meta.json` 的 `last_synced_at`**，超过阈值（比如 6 小时）才真正调 API，否则直接退出。同步结果走 `feat/lark-sync-<yyyy-mm-dd-HH>` 分支 + 发布 skill。如果两人几乎同时跑，第二个发现 meta 已经新鲜就退出。

`digest/`——按需，给团队产出每日/每周变化摘要，可以推到 Lark 群机器人。

### `tools/` ——通用工具

`lark/` 是新增组件：`lark_client.py`（封装 tenant_access_token、Wiki API、Docs API、IM API）、`lark_doc_pull.py`（CLI 拉单文档）、`lark_doc_push.py`（CLI 推单文档）、`lark_im_send.py`（发消息到群/个人）。这层是所有 Lark 相关 skill 的底层。

`semantic_search/` 从原仓库继承，但 index 范围扩到 `lark_mirror/` 和 `contexts/*` 的所有产物。

原仓库的 typefully、kit、ga4 等创作者向工具移到 `tools/_reference_grapeot/` 或直接删除。

### `adhoc_jobs/` ——个人临时项目

每个人按自己习惯放临时脚本、一次性数据处理、调试用 notebook。约定 `adhoc_jobs/<handle>/<project>/`，单作者，直接 commit 到 main。如果项目长大到需要团队协作，再决定迁移到 `tools/` 或 `contexts/products/` 下。

### `docs/` ——元文档

`ARCHITECTURE.md`：整体架构图、数据流、为什么这么设计。
`COLLAB_PROTOCOL.md`：协作协议——分支命名、PR 流程、敏感清单、冲突处理（在第二节展开）。
`ONBOARDING.md`：新成员怎么用，配套 setup_guide.md。
`CRONTAB.md`：每个人各自机器的 cron 范例。
`RIMBO_REDESIGN.md`：本文档。

---

## 二、文件更新工作流（多人写入怎么不打架）

核心原则：**让 AI 走和人开发一样的协作流程**——改东西就开分支、发布通过 skill 走 PR、main 始终干净。具体规则按写入区域不同分三类。

### 直接 commit 到 main 的区域

这些区域单作者或天然不冲突，AI 可以不走 PR：

`contexts/memory/people/<我>/`——本人的 AI 写本人的私域记忆，没人会和你争。
`adhoc_jobs/<我>/`——个人临时项目，单作者目录。
`.me`、`.env`——根本不入 git。

### 必须走分支 + PR 的区域（自动 merge）

大多数共享产物都属于这一类。流程是 AI 读 `rules/skills/workflow_publish.md`，按里面定义的步骤走：

1. `git pull --rebase` 确保 base 在最新 main 上。
2. 起分支 `feat/<purpose>-<handle>-<timestamp>`，purpose 用约定前缀（`reflect`、`lark-sync`、`digest`、`prd-<name>`、`decision-<topic>`、`research-<topic>` 等）。
3. 完成改动并 commit，每个 commit 描述清楚意图，禁止 "update" 这种空消息。
4. dry-run merge 到 main，预测冲突。有冲突先解决再继续。
5. push 分支，用 `gh` CLI 开 PR，PR 模板自动填好。
6. PR 描述包含：why（解决什么）、what（改了什么）、scope（影响哪些下游）、AI 自审清单、reviewer。
7. 自审通过且不在敏感清单 → 自动 squash merge，merge 后立刻删本地和远端分支。

适用区域：`contexts/products/<product>/`（owner 之外的人改）、`contexts/planning/`、`contexts/research/`、`contexts/memory/OBSERVATIONS.md`、reflector 产出、lark-sync 产出、digest 产出。

### 必须走 PR 且禁止自动 merge 的区域（敏感清单）

这些区域改动会影响所有人或别人的工作，必须人 review：

- `rules/SOUL.md` / `TEAM.md` / `IDENTITY.md` / `COMMUNICATION.md`——L3 全局约束。
- `rules/axioms/team/` 任何新增或修改——团队公理是慢沉淀产物，AI 提议、人审核。
- `rules/members/<别人>.md`——别人的 profile，本人维护。
- `rules/skills/`——能力库，影响所有人的 AI 行为。
- `contexts/products/<product>/`——非 owner 改 owner 的产物。
- `tools/lark/`、其他凭据相关代码——安全敏感。

发布 skill 在自审环节会先扫一遍 diff，命中敏感清单就在 PR 描述里 `Reviewer:` 字段填具体的人，不开 auto-merge。

### 冲突处理

`OBSERVATIONS.md` 的 append-only 冲突——总是 keep both，按 caller + date 排序。约定每条新观察前后留空行，单条不超过一段，把行级冲突概率压到接近零。

其他文本冲突——AI 先尝试三方合并，能解决就解决；不能解决就在文件里标 `[conflict]` 标记并在 PR 里 @owner，等人介入。

reflector PR 的"假冲突"——多人 reflector 几乎同时开 PR，第二个 PR base 在第一个 merge 前的 main 上，merge 时会 rebase 出大量历史变化。`COLLAB_PROTOCOL.md` 里建议错开运行时间（周一/周三/周五早 8 点轮转）。

### 分支清理

merge 后发布 skill 自动删本地和远端分支。如果运行任务的机器没在 PR merge 时清理，下次跑同类任务的步骤 1 会顺手清理上次的残留。

### Lark 写回的特殊约束

任何对 Lark 文档的写回（`lark_doc_push.py`）必须**先 commit 到仓库 + push + merge**，再触发推送。不允许 AI 跳过仓库直接写 Lark。理由是仓库才是版本权威，Lark 是发布面，否则 git 和 Lark 会渐行渐远。具体实现是 `lark_write.md` skill 在调用 push CLI 前先检查本地无未提交改动，且 HEAD 已经 push 到 origin/main。

---

## 三、个人日常工作流

下面用一个具体例子串一遍：xu（handle 是 xu）一天的典型流程。

### 上午：开始一段工作

打开 AI 客户端（Codex/Claude Code/OpenCode/Cursor 任选），它读 `AGENTS.md`，进而读 `IDENTITY.md`，再读本地 `.me` 拿到 `handle: xu`，加载 `rules/members/xu.md` 和 `contexts/memory/people/xu/` 下最近的观察记录。SOUL/TEAM/COMMUNICATION 这些 L3 也都被加载。Agent 现在知道：自己在 rimbo 团队、当前 caller 是 xu、xu 上周在做什么、xu 偏好什么沟通方式。

xu 说"帮我看看新功能 Foo 的 PRD 写得怎么样"。AI 查 `rules/WORKSPACE.md`，定位到 `contexts/products/foo/prd/`，读完文档给反馈。这个过程不写任何文件，纯 inference。

### 中午：写一份 PRD

xu 让 AI 起草 `contexts/products/foo/prd/v1.md`。AI 先看这个产物有没有 owner——frontmatter 里 owner 是 xu 本人，那直接走发布 skill 即可（如果是别人的产物，发布 skill 在自审环节会发现并标记需要 reviewer）。

AI 调发布 skill：`git pull --rebase` → 起分支 `feat/prd-foo-xu-2026-05-16` → 写文件 → commit → 开 PR → 自审通过 → squash merge → 删分支。整个过程对 xu 透明，xu 收到的反馈是"PR #42 已 merge 到 main"。

### 下午：要参考一份 Lark 文档

xu 说"上次产品会的会议纪要里关于定价的部分是怎么说的"。AI 查 `WORKSPACE.md`，发现会议纪要在 Lark 里。两条路径选一个：

- 如果 `lark_mirror/` 里有这份文档且足够新（meta 显示几小时内同步过），AI 直接读镜像。
- 否则 AI 调 `tools/lark/lark_doc_pull.py --doc_id <xxx>` 实时拉，临时文件用完即丢，不入仓库。

需要写回 Lark 时（比如修订定价部分），AI 先把改动 commit 到仓库 + merge 到 main，再调 `lark_doc_push.py`。

### 晚上：cron 自动跑 observer

xu 机器上的 cron 在晚上 11 点跑 `periodic_jobs/ai_heartbeat/observer.py`。observer 扫描当日仓库变化（新 PRD、新决策、新调研、xu 自己的 commit history），调 AI 做语义抽取，把"今天 xu 推动了 Foo PRD v1，关键决策是 X，遗留疑问是 Y"这类条目追加到 `contexts/memory/people/xu/observations.md`。直接 commit 到 main，不走 PR。

### 周末：cron 自动跑 reflector

周日早 8 点 cron 跑 `reflector.py`。reflector 读 xu 这周在 `people/xu/` 累积的所有观察，找出有跨人价值的（"原来 Lark API 在某个边界条件下要这么处理"、"产品 Foo 决策时有个共性框架"），生成一个 PR：`feat/reflect-xu-2026-w20`。

PR 内容：往 `contexts/memory/OBSERVATIONS.md` append 几条全局观察，提议在 `rules/axioms/team/` 加一条新公理。因为修改了 `axioms/team/`，发布 skill 在自审时识别为敏感清单，自动 merge 关掉，PR 描述里 `Reviewer:` 字段标 yan 或团队某个人。等 reviewer 看完 merge。

如果只 append 了 `OBSERVATIONS.md` 没有动 axioms，发布 skill 直接 auto-merge。

### Lark 同步什么时候发生

xu 不需要主动跑 lark_sync。任何人下次跑（cron 里 xu 自己也配了一份 lark_sync）会先检查 `_meta.json`，新鲜就跳过，过期就同步。多人 cron 时间错开 + stale 检查，保证 lark_mirror 大致每几小时就有新鲜版本。

### 协作场景：和 yan 同时改同一份 PRD

PRD owner 是 xu，但 yan 也想改一段。yan 的 AI 走发布 skill 时，自审发现 owner 不是 yan，PR 描述里自动 `Reviewer: @xu`，不 auto-merge。xu 这边收到 PR 通知，AI 帮他读 diff 给意见，xu 决定 merge 或 request changes。

### 一句话总结

每个人的体感是：自己机器上正常用 AI 客户端，AI 一直在帮你读、写、commit、开 PR。别人的产出通过 git pull 流到你这里。不需要值班、不需要中心服务、也不需要常驻 agent。git history 里能看到"xu 的 AI 在 2026-05-16 reflect 出了哪些观察"、"yan 改了 Foo PRD 的定价段并经 xu review 通过"——所有协作都有审计痕迹。

---

## 四、改造执行顺序回顾

**Phase 1（3-5 天）：身份骨架 + 发布 skill**
改 README/AGENTS/SOUL，新建 `rules/TEAM.md`、`rules/IDENTITY.md`、`.me.example`，下沉 grapeot 内容到 `_reference_grapeot/`，新建 contexts 子目录骨架。**核心交付：`workflow_publish.md` 和 `COLLAB_PROTOCOL.md`**。

**Phase 2（1 周）：Lark 工具 + 凭据**
`tools/lark/` 三个 CLI，1Password vault 集成（团队共用一个 Lark 自建应用，密钥走 `op read`）。AI 能用 skill 实时拉/推 Lark 单篇文档。

**Phase 3（3-5 天）：定时任务自动 PR**
改造 `observer.py` 写入 `people/<.me 的 handle>/`、`reflector.py` 产出走发布 skill、`lark_sync/` 加 stale 检查 + 走发布 skill。每个人在自己机器上配 cron。

**Phase 4（持续）**
embedding（覆盖 lark_mirror + contexts）、digest 推群、axioms 慢沉淀。

---

## 五、能力交付物（Capabilities）

前面四节解决的是"产物"和"记忆"怎么沉淀。但 rimbo 的工作还有一类输出特别重要——**项目阶段交付出来的能力**。比如做信源基础设施这件事，不是只交付一份 PRD 和一份调研报告就结束了，而是最终落出"能从多源拉取、去重、打标签的信源服务"这么一个**可被复用的能力**。这类东西如果只散落在 PRD/RFC 里，新成员（包括 AI）很难知道"团队现在有哪些能力可以用"，会重复造轮子。所以单独切一层 `contexts/capabilities/`。

### 5.1 capability 的定义

一个 capability 是团队对外（其他项目、其他成员、AI agent）声明的、有契约的、可调用的能力。判断标准三条同时成立：

1. **可被复用**——不是某个一次性项目的内部实现，而是设计上就准备给至少一个下游使用。
2. **有契约**——输入、输出、SLA、错误模式都明确，下游可以按契约调用，不需要读实现。
3. **有维护者**——有个 owner（个人或小组）对它的稳定性和演进负责。

例子：信源基础设施、内容打分模型、用户画像服务、Lark 文档双向同步引擎、内部 embedding 服务。反例：某个 PRD 里临时跑的数据处理脚本（不打算复用就不算）、个人 adhoc_jobs（没契约也没维护承诺）。

### 5.2 目录结构

```
contexts/capabilities/
├── INDEX.md                          # 所有 capability 的总览,AI 读这个找能力
├── source_infra/                     # 一个 capability 一个目录
│   ├── CAPABILITY.md                 # 能力卡片(主文件)
│   ├── interface.md                  # 调用契约:CLI / HTTP / SDK / skill 的具体形态
│   ├── changelog.md                  # 版本演进记录
│   ├── decisions/                    # 这个能力相关的 ADR(为什么这么设计)
│   └── examples/                     # 调用示例
├── user_profile/
│   └── ...
└── ...
```

### 5.3 `CAPABILITY.md` 的标准结构

每个 capability 必须有这一份文件，AI 和人通过它对齐"这个能力当前是什么样"。frontmatter + 正文：

```yaml
---
name: source_infra
display_name: 信源基础设施
status: stable                  # experimental | beta | stable | deprecated
version: v1.2
owner: xu                       # handle,对应 rules/members/<owner>.md
contributors: [yan, li]
since: 2026-03-10
last_reviewed: 2026-05-12       # 每月强制 review 一次,过期会被 INDEX 标黄
implementation:
  primary_repo: Mindspace-ai/source-infra
  paths:
    - tools/source_infra/        # 本仓库内的 CLI 入口
deps:
  - lark_sync                    # 依赖另一个 capability,形成依赖图
  - external: redis              # 外部依赖
exposes:
  - cli: source-pull
  - skill: rules/skills/source_pull.md
  - http: https://internal.../sources    # 如果有
---

# 信源基础设施 (source_infra)

## 它是什么
一两段话讲清楚:这个能力解决什么问题,边界在哪,典型的下游是谁。

## 怎么用
列举主要调用形态(CLI / skill / HTTP),每种给一两个最小示例。详细契约在 interface.md。

## 当前能力清单
- ✅ 从 RSS 拉取去重
- ✅ 从 Lark wiki 拉取
- ✅ 关键词标签
- 🚧 语义聚类(beta)
- ❌ 视频源(未支持)

## 已知限制 / 不适用场景
明确写出"如果你想做 X,别用这个能力"。避免下游误用。

## 维护与升级
谁负责、bug 怎么报、版本怎么升、deprecate 怎么处理。
```

`status` 字段语义：`experimental` 表示在实验，下游用要承担 breaking change；`beta` 表示契约基本稳定但仍可能小调；`stable` 表示有兼容性承诺；`deprecated` 表示在被替代，配合 `replaced_by:` 字段指向继任者。

### 5.4 `INDEX.md` 的作用

`contexts/capabilities/INDEX.md` 是所有 capability 的总览表，AI 在 session 启动时不主动加载（避免上下文撑爆），但在用户问"我们有什么能力可以做 X"或"信源相关的工作有没有现成的"时，AI 第一步就读这个 INDEX。格式：

```markdown
# Capabilities Index

## 数据与信源
- [source_infra](./source_infra/CAPABILITY.md) v1.2 ✅ stable — 多源拉取、去重、打标签
- [user_profile](./user_profile/CAPABILITY.md) v0.3 🟡 beta — 用户画像服务

## 内容处理
- [content_scoring](./content_scoring/CAPABILITY.md) v2.0 ✅ stable — 内容质量打分
- ...

## 基础设施
- [lark_bridge](./lark_bridge/CAPABILITY.md) v1.0 ✅ stable — 仓库与 Lark 双向桥接
- ...
```

约定：deprecated 用 ⚠️、experimental 用 🧪、beta 用 🟡、stable 用 ✅。`last_reviewed` 超过 90 天的自动标 ⏰。

### 5.5 capability 与其他目录的关系

`contexts/capabilities/` 是**契约层**，是对外的"门面"。它和别的目录的边界要划清楚，否则会重复：

- 与 `contexts/products/<product>/`：products 装"我们要做什么产品"（PRD/RFC/decisions），capabilities 装"我们已经做出了什么能力"。一个产品的几个迭代可能产出多个 capabilities；一个 capability 可能服务多个产品。两者多对多。
- 与 `tools/`：tools 装实现代码，capabilities 装契约和说明。如果 capability 的实现就在本仓库 `tools/` 下，CAPABILITY.md 的 `implementation.paths` 指过去；如果在别的仓库，指 `primary_repo`。
- 与 `rules/skills/`：skill 是 AI 用某个能力的具体步骤指南。如果一个 capability 暴露了 skill 形态，CAPABILITY.md 的 `exposes` 字段指向对应的 skill 文件，但 skill 文件本身仍在 `rules/skills/` 下，不要复制到 capabilities 目录。
- 与 `contexts/products/<product>/decisions/`：单个产品内部的实现决策放产品下；影响整个 capability 的设计决策（比如"为什么 source_infra 选 RSS 优先而不是直接爬"）放 `capabilities/<cap>/decisions/`。

### 5.6 capability 的生命周期与发布流程

一个 capability 不是一开始就在 `capabilities/` 里出现，而是经历四个阶段：

1. **构想期**——还在 PRD/RFC 阶段，只在 `contexts/products/<product>/` 里讨论，不进 capabilities 目录。
2. **首次落地**——第一版实现完成、有了下游真实使用意图，**这时候才创建 `contexts/capabilities/<cap>/`**，状态 `experimental`。owner 通过发布 skill 提交一个 PR，PR 标题约定 `capability: introduce <name>`。
3. **稳定期**——实测一段时间、契约不再频繁变动，owner 提议升 `stable`。状态变更必须走 PR + review，不允许 auto-merge（属于敏感清单）。
4. **退役**——被替代或不再维护，状态改 `deprecated`，`replaced_by:` 指向继任者，保留至少 90 天再考虑删除。`INDEX.md` 在 deprecated 区域单列。

每次版本号跳变（v1.0 → v1.1 / v2.0）必须更新 `changelog.md`，写清这一版改了什么、是否 break 了契约、迁移指南。breaking change 必须 major 版本号 +1 且在 INDEX 上加 ⚠️ 标记一周以上。

### 5.7 capability 在协作工作流里的位置

把 capability 视为"敏感清单的一部分"。前面第二节定义的发布 skill 在自审时新增几条规则：

- 创建新 capability（新增 `contexts/capabilities/<cap>/CAPABILITY.md`）→ 必须 PR + review，不 auto-merge。
- 修改 `CAPABILITY.md` 的 frontmatter 中的 `status`、`version`（major）、`owner`、`exposes`、`deps` → 必须 PR + review。
- 修改 `interface.md` 的契约（输入/输出/错误模式）→ 必须 PR + review，标 `breaking-change` label。
- 修改 `examples.md`、`changelog.md`、正文非 frontmatter 内容 → auto-merge OK。

AI 在做任何"用某能力"的工作前，应该先读对应 `CAPABILITY.md`，特别是"已知限制 / 不适用场景"段，避免按 PRD 里描绘的理想形态调用、却踩了实际限制。这一条写进 `rules/skills/capability_use.md`（新增）。

### 5.8 为什么要单独切这一层

不切的话，能力会散落在三处：PRD 里的"我们要做"、tools 里的实现代码、个人记忆里的"那个东西怎么调"。结果是新成员（包括 AI）问"信源服务能做什么"时，要把三处都拼起来才知道——而且很可能拼出过期信息。

切出来之后：team 任何人想找能力先看 INDEX，AI 同理。任何对外承诺都集中在 `CAPABILITY.md`，对外契约和实现解耦。版本演进有 changelog，下游可以放心依赖。capability 之间的依赖图（`deps` 字段）能让团队看到"我们的能力栈是什么样的"，避免盲目重复造。

---

## 六、几个明确不做的决定

不做 Lark 与仓库的双向自动同步——冲突合并几乎必然出错。Lark 是发布面，git 是权威；要么单向写回 Lark，要么单向镜像到仓库，不混合。

不做中心化常驻 agent——每个人用自己的 AI 客户端就够了，git + PR 是协作协议。规模到 5+ 人觉得 PR 流程太重再考虑。

不做"值班人统一跑 cron"——每个人自己跑、走发布 skill 自动 PR，分布式更符合协作的本质。

不在 Phase 1 上 embedding——内容还没到，先把结构和流跑起来，2 个月后再开。

不让 AI 直接修改 `rules/`——必须 PR + review，避免人格被慢慢腐蚀。

不在 `contexts/memory/OBSERVATIONS.md` 编辑历史条目——append-only，整理走 reflector PR。
