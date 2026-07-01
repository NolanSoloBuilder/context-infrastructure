# rimbo-work-context

rimbo 团队的工作上下文空间。多人协作场景下的 context infrastructure：沉淀产品规划、决策、调研、能力交付物，并能与 Lark 知识库联通。

## 形态

**共享 workspace + 各自 AI 客户端**。仓库本身是单一事实源，每个人在本机 clone，用自己的 Codex / Claude Code / OpenCode / Cursor 打开。git 是同步协议，PR 是协作机制，没有常驻 agent 服务。

详见 [`docs/RIMBO_REDESIGN.md`](docs/RIMBO_REDESIGN.md)。

## Quick Start（10 分钟）

```bash
git clone git@github.com:Mindspace-ai/rimbo-work-context.git
cd rimbo-work-context

# 1) 标识自己
cp .me.example .me
$EDITOR .me                          # 填写 handle

# 2) 配置凭据（按需）
cp .env.example .env
$EDITOR .env

# 3) 建自己的 profile
cp rules/members/_template.md rules/members/<handle>.md
$EDITOR rules/members/<handle>.md
# 然后走发布 skill 提交 PR (敏感清单, 团队 review)

# 4) 用 AI 客户端打开
# Codex / Claude Code / OpenCode / Cursor 任选,会自动读 AGENTS.md
```

详细步骤见 [`setup_guide.md`](setup_guide.md)。

## 目录速览

```
rimbo-work-context/
├── AGENTS.md                  # AI 每次 session 的入口指令
├── docs/
│   ├── RIMBO_REDESIGN.md      # 改造方案总文档
│   ├── COLLAB_PROTOCOL.md     # 协作协议(分支/PR/敏感清单/冲突处理)
│   └── ...
│
├── rules/                     # L3 全局约束(被动加载)
│   ├── SOUL.md                # rimbo AI 的人格基调
│   ├── TEAM.md                # 团队画像
│   ├── IDENTITY.md            # AI 怎么识别 caller
│   ├── COMMUNICATION.md       # 沟通风格
│   ├── WORKSPACE.md           # 目录路由表(找文件先查这里)
│   ├── members/               # 每个成员的 profile
│   ├── axioms/
│   │   ├── team/              # 团队公理(从空累积)
│   │   └── _reference_grapeot/   # 上游 grapeot 公理(默认不加载)
│   └── skills/
│       ├── workflow_publish.md   # 核心:AI 怎么发布
│       ├── capability_use.md     # 核心:AI 怎么用 capability
│       ├── ...                   # 通用 skills
│       └── _reference_grapeot/   # 个人创作者向(默认不加载)
│
├── contexts/                  # 产物与记忆
│   ├── products/<product>/    # PRD / RFC / decisions
│   ├── planning/              # OKR / 周报 / 管理决策
│   ├── research/              # 用研 / 实验 / 反馈
│   ├── glossary/              # 术语表与命名约定
│   ├── capabilities/          # 项目阶段交付的"能力"(对内契约)
│   ├── lark_mirror/           # Lark 文档的本地镜像(只读)
│   └── memory/
│       ├── OBSERVATIONS.md    # 团队全局观察(append-only)
│       └── people/<handle>/   # 每个人的私域记忆
│
├── periodic_jobs/             # 定时任务(每人本机配 cron)
├── tools/                     # 通用工具
│   ├── lark/                  # Lark 集成(Phase 2)
│   └── semantic_search/
└── adhoc_jobs/<handle>/       # 个人临时项目
```

## 三个核心概念

**身份**：通过 `.me` → `rules/IDENTITY.md` → `rules/members/<handle>.md`，让每个人本地的 AI 知道当前 caller 是谁。

**发布**：所有共享区域写入走 `rules/skills/workflow_publish.md` 定义的分支 + PR + 自动 merge / review 流程。AI 是和人开发一样的 contributor，不能直接 force push main。

**能力（capability）**：项目阶段交付出来的、对内可调用的有契约能力（如信源基础设施、内容打分服务），落在 `contexts/capabilities/` 下。AI 通过 `rules/skills/capability_use.md` 学会发现和使用。

## 关键文档

- [`docs/RIMBO_REDESIGN.md`](docs/RIMBO_REDESIGN.md) — 改造方案总文档（设计决定、目录、工作流、capabilities）
- [`docs/COLLAB_PROTOCOL.md`](docs/COLLAB_PROTOCOL.md) — 协作协议
- [`AGENTS.md`](AGENTS.md) — AI 入口
- [`rules/WORKSPACE.md`](rules/WORKSPACE.md) — 目录路由表
- [`rules/skills/workflow_publish.md`](rules/skills/workflow_publish.md) — 发布流程
- [`rules/skills/capability_use.md`](rules/skills/capability_use.md) — capability 使用

## License

MIT
