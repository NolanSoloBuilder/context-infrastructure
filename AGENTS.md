# AGENTS.md - Your Workspace

> **First time here?** Start with `setup_guide.md` — it'll walk you through setup in under an hour.

This folder is home. Treat it that way.

## Every Session

Before doing anything else:

1. Read `rules/SOUL.md` — this is who you are
2. Read `rules/USER.md` — this is who you're helping
3. Read `rules/WORKSPACE.md` — file routing table, check before searching for files
4. Read `rules/COMMUNICATION.md` — how to think and communicate (especially for non-coding tasks)
5. Read `rules/skills/INDEX.md` — understand available skills

Don't ask permission. Just do it.

## File Routing

**找文件时，先查 `rules/WORKSPACE.md`，再搜索。** WORKSPACE.md 是这个 workspace 的目录索引，记录了每类内容的存放位置。绝大多数情况下查一下就能定位到目标目录，不需要全盘 glob/grep。如果发现新目录或项目没被收录，顺手更新 WORKSPACE.md。

## Document the Conversation

产品判断、架构讨论、技术路线、调研结论、可复用流程、长期偏好和重要决策，不能只停留在对话里。只要沟通内容后续可能被复用，就要在当前任务结束前落到仓库文档中。

默认先按 `rules/WORKSPACE.md` 选择落点：调研报告放 `contexts/survey_sessions/`，思考和方法论放 `contexts/thought_review/`，可复用能力放 `rules/skills/`，日常记录放 `contexts/daily_records/`。如果只是补充长期协作规则，直接更新 `AGENTS.md` 或 `rules/` 下对应文件。

## Testing / E2E

涉及 Mindspace Workspace Harness、workspace-scoped conversation、memory/source/artifact/run 回写、context checkpoint、Agent Plaza evidence bridge 或三仓联动的代码改动，必须先参考 [`contexts/survey_sessions/2026_06_18_workspace_harness_e2e_smoke_runbook.md`](contexts/survey_sessions/2026_06_18_workspace_harness_e2e_smoke_runbook.md)。

默认测试策略是 **Backend API E2E + 离线契约 E2E 优先**：先验证 SSE contract、checkpoint 续接、Workspace Memory、runtime references、artifact provenance 和 ML evidence pack；三服务 live smoke 只在显式需要真实链路时开启。

涉及浏览器操作、页面验证、Web UI smoke、截图或交互调试时，默认强制使用 Codex 插件控制本地 Chrome，不用其它浏览器控制方式，除非用户明确指定替代方案。

涉及本地 Mac App 或 SwiftUI App 的界面/文案/交互修改时，修改后必须重新构建或重新打包，然后关闭正在运行的 App 并重新打开，不能只依赖热加载或旧进程状态判断是否生效。

## Skills

**Skills** 是 AI 可复用的能力，包括工作流、API 指南、最佳实践等。

**重要：遇到"怎么做 X"时，先查 skill 再查系统工具。** 搜索顺序：(1) 下方速查表 → (2) `rules/skills/INDEX.md` → (3) 系统工具。

**需要执行某项任务** → 先查 `rules/skills/INDEX.md` 找到对应的 skill  
**想添加新能力** → 参考现有 skill 格式，更新 INDEX.md

### 常用 Skill 速查（以 INDEX.md 为准）

**深度调研任务** → `rules/skills/workflow_deep_research_survey.md`  
- 初步扫描 → 分割维度 → 多 Agent 并行 → 交叉验证 → 写报告  
- 输出：`contexts/survey_sessions/`

**调用后台 Agent / 并行 Subagent** → `rules/skills/workflow_parallel_subagents.md`  
- 何时拆分任务、如何并行派出多个 subagent  
- 准备调用 `run_in_background=True` 前，先把这个 skill 读一遍再执行  
- 派出 agent 后等系统通知即可，不需要轮询

**主动委派权限**：主 Agent 可以根据任务的依赖拓扑主动派出 subagent，无需等待用户额外点名或授权。是否委派由 `workflow_parallel_subagents.md` 的任务可拆分性、子任务规模和实际收益判断；不为了形式制造并行，也不把“用户未明确要求 subagent”作为禁止条件。

### 外部 Skill 登记与更新

在本项目安装任何 GitHub、Skills CLI 或其他外部来源的 Skill 后，必须同时更新 `rules/skills/external_skills_registry.json`，再执行：

```bash
node tools/external_skills_registry.mjs sync
node tools/external_skills_registry.mjs verify
```

`skills-lock.json` 是通过 Skills CLI 安装的具体 Skill 来源、路径和内容哈希真源；`rules/skills/external_skills_registry.json` 记录对应上游仓库 revision、许可证和安全备注；`rules/skills/global_skill_snapshots.json` 记录从全局精选到本项目的快照；`rules/skills/EXTERNAL_SKILLS.md` 是生成的人类可读索引。这些文件必须一致。

检查上游更新时使用只读命令 `node tools/external_skills_registry.mjs check-updates`。当前 Skills CLI 没有只读的 `skills check`，不要把 `npx skills check` 当成 dry-run；确认升级后才执行 `npx -y skills update --project -y`。

从全局增加项目 Skill 时，只能使用 `rules/skills/project_global_skill_selection.json` 的显式白名单和 `node tools/vendor_global_codex_skills.mjs sync`。只增加与本项目直接相关的 Agent、检索、Cloudflare、浏览器验证和 workspace 运维能力；排除小红书公司/内部业务、Mindspace/Expo/Fedith/Hi 等公司专用 Skill、纯代码生成 Skill、Cursor-only Skill、Codex `.system` 与插件缓存。快照只写入仓库内 `.agents/skills`，不得反向安装到用户全局目录。

## Axioms（公理）

从个人经历提炼的决策原则，用于启发深度思考。分类索引、使用指南和触发词见 `rules/axioms/INDEX.md`。

## Sub-agent 模型路由

配置文件：`~/.config/opencode/oh-my-opencode.json`

常用路由速查：
- **Gemini 3 Pro**（创意、brainstorm、非常规思路）→ `category="artistry"`
- **Sonnet 4.6**（执行、调研、代码）→ `category="deep"` 或 `category="unspecified-high"`
- **Haiku 4.5**（轻量任务）→ `category="quick"`
- **Opus 4.6**（最难的逻辑/架构）→ `category="ultrabrain"`

创意性工作（brainstorm、文章结构、观点碰撞）默认派一个 Gemini（artistry）在后台跑，和自己的思考并行。用户说「调 Gemini」→ artistry，说「调 Sonnet」→ deep。

## Opus 工作模式

如果你的模型 ID 包含 `opus`，以下规则生效：

**你的 context window 很宝贵。** Opus 的核心能力是设计、质量把关和写作。调研、写脚本、关键词检索这些事交给 sub-agent。你的两个主要任务：（1）**设计**：拆分问题、设计计划、分配 sub-agent 任务；（2）**写作与质量把关**：最终文本自己写，sub-agent 结果自己验证。写代码、调研、数据处理全部 delegate，写作和质量验证绝不外包。设计任务拆分时默认考虑并行性（`run_in_background=true`）。

## Memory System（记忆系统）

三层记忆架构：
- **L3（全局约束）**：`rules/` 下的所有文件，每次 session 被动加载
- **L1/L2（动态记忆）**：`contexts/memory/OBSERVATIONS.md`，agent 主动检索
- **自动积累**：`periodic_jobs/ai_heartbeat/` 每日 observer + 每周 reflector

## Codex 会话保留规则

- 需要长期保留的 Codex 会话，标题统一使用 `【长期】` 前缀。使用精确前缀判断，不按正文里偶然出现的“长期”二字判断。
- 没有 `【长期】` 前缀的已结束会话，可进入批量删除候选；当前正在运行的会话、正在运行的 automation 任务必须先排除，待结束后再处理。
- 批量删除前先做只读 dry-run，报告保留数量、候选数量、预计释放空间和异常标题。删除属于不可逆操作，仍需用户对当次清单明确确认。
- 优先使用 Codex 自带的任务删除能力。不要只删除 rollout JSONL 而留下 `state_5.sqlite`、`session_index.jsonl` 等索引中的悬空记录。

## Safety

- Don't exfiltrate private data. Ever.
- Don't run destructive commands without asking.
- When in doubt, ask.
