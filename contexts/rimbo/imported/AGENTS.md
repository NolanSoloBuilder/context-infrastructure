# AGENTS.md - rimbo Workspace

> **首次进入？** 先看 `setup_guide.md` 和 `docs/RIMBO_REDESIGN.md`。

这是 rimbo 团队的 work context。共享 workspace、各自 AI 客户端：每个人在本机用自己的 Codex / Claude Code / OpenCode / Cursor 打开，git 是同步协议，PR 是协作机制。没有常驻 agent 服务。

## 每次 session 的入口

按这个顺序加载 L3 全局约束：

1. `rules/SOUL.md` — rimbo AI 的人格基调
2. `rules/IDENTITY.md` → 读本机 `.me` → 解析当前 caller handle
3. `rules/members/<handle>.md`（若存在）— 当前 caller 的 profile
4. `rules/TEAM.md` — 团队画像
5. `rules/COMMUNICATION.md` — 沟通风格
6. `rules/WORKSPACE.md` — 目录路由表
7. `rules/skills/INDEX.md` — 能力总览

不要问权限，直接读。

## 找文件

**先查 `rules/WORKSPACE.md`，再 grep / glob。** 路由表覆盖绝大多数场景。如果发现新目录 / 项目没被收录，顺手 PR 更新。

找"团队有没有现成的能力做 X" → 先查 [`contexts/capabilities/INDEX.md`](contexts/capabilities/INDEX.md)。

## 写入

任何写入前先想清楚是哪一类：

- **个人区域**（`contexts/memory/people/<我>/`、`adhoc_jobs/<我>/`、`.me`、`.env`）→ 直接 commit
- **共享区域**（`contexts/products/`、`contexts/planning/`、`contexts/research/`、`contexts/glossary/`、`contexts/capabilities/<x>/changelog`/`examples/`、`contexts/lark_mirror/`，且 owner 是自己或不需要 owner）→ 走发布 skill auto-merge
- **敏感区域**（`rules/`、`contexts/capabilities/<x>/CAPABILITY.md` 创建 / frontmatter / `interface.md` 契约、`tools/lark/`、`periodic_jobs/` 等）→ 走发布 skill，PR + review

发布流程见 [`rules/skills/workflow_publish.md`](rules/skills/workflow_publish.md)。完整规则见 [`docs/COLLAB_PROTOCOL.md`](docs/COLLAB_PROTOCOL.md)。

## Skills

**遇到"怎么做 X"时，先查 skill 再查系统工具。** 顺序：
1. [`rules/skills/INDEX.md`](rules/skills/INDEX.md)
2. 系统工具（grep / glob / bash 等）

**协作流程类 skill 必读**：`workflow_publish.md`（发布）和 `capability_use.md`（用 capability）。涉及任何写入前都要读。

## Capabilities

`contexts/capabilities/` 是 rimbo 团队对外声明的、有契约的、可调用的能力。AI 在做"用某能力"或"提议新能力"的工作时，从 `capabilities/INDEX.md` 出发，按 [`rules/skills/capability_use.md`](rules/skills/capability_use.md) 的指引操作。

## Memory（记忆系统）

三层：

- **L3（全局约束）**：`rules/` 下所有文件，每次 session 被动加载
- **L1/L2 团队全局观察**：`contexts/memory/OBSERVATIONS.md`，append-only，按需检索
- **L1/L2 个人私域**：`contexts/memory/people/<handle>/`，**只在和该 handle 对话时**加载

由 `periodic_jobs/ai_heartbeat/observer.py`（每日，写自己 people）和 `reflector.py`（每周，蒸馏 + 提议晋升，走 PR）自动维护。

## Sub-agent 模型路由

参考上游约定（如使用 OpenCode）：
- `category="artistry"` — Gemini 3 Pro，创意、brainstorm
- `category="deep"` / `unspecified-high"` — Sonnet，执行、调研、代码
- `category="quick"` — Haiku，轻量任务
- `category="ultrabrain"` — Opus，最难的逻辑/架构

实际使用什么 sub-agent 取决于团队成员各自配置，AI 应根据本机环境推断或问用户。

## Opus 工作模式

如果当前模型 ID 包含 `opus`：context window 很宝贵，**调研、写脚本、关键词检索全部 delegate 给 sub-agent**。Opus 的两个主要任务：(1) 设计与拆任务；(2) 写作与质量把关。设计时默认考虑并行性。

## Safety

- 不外泄团队私密数据（用户数据、商业敏感、未公开决策）
- 不运行破坏性命令前先问
- 不假冒他人身份 commit
- Lark 写回必须经过 git
- 不确定时，问

## 不做的事

详见 `docs/RIMBO_REDESIGN.md` 第六节。摘要：

- 不做 Lark ↔ git 双向自动同步
- 不部署常驻 agent 服务
- 不让 AI 直接修改 `rules/`（必须 PR + review）
- 不在 `OBSERVATIONS.md` 编辑历史条目（append-only）
