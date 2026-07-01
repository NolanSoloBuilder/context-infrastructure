# AI Context Portability and Personal Environment Sync

日期：2026-06-17

## 背景

AI 工具已经从单个聊天窗口变成工作环境。一个高频用户长期积累的不只是对话历史，还包括个人偏好、项目规则、skill、MCP 配置、本地文件索引、浏览器和终端习惯、历史决策、工具链配置和运行环境上下文。

如果换电脑时只迁移代码仓库，真正让 agent 好用的上下文会丢掉一大块。这个问题的核心不是某个垂直业务场景，而是 AI 工具链本身已经形成了个人环境：Codex、Claude Code、Cursor、Windsurf、OpenCode、Cline、Gemini CLI、MCP servers、skills、rules 和 memory 都需要跨设备恢复。

## 当前市场信号

已有产品在处理相邻问题，但还没有形成一个完全覆盖个人 AI 工作环境迁移的标准形态。

ChatGPT 有 memory、project memory、chat/data export，但更偏账号内个性化和合规导出。Claude 已经提供 memory import/export，这是一个明确信号：memory portability 正在成为用户需求。

开发工具侧更接近这个方向。Cursor 有 persistent rules / `AGENTS.md`，Windsurf 有 memories/rules，Cline Memory Bank 用 markdown 文件维持项目上下文。Pieces、memories.sh、OpenMemory MCP 则把长期记忆做成独立上下文层，通过 MCP 接入不同 AI 工具。

这些产品说明需求真实存在。不过多数产品仍停留在“记忆层”或“规则同步层”，还没有把工作环境、工具配置、skill、密钥引用、项目决策和可审计产物统一成一个可迁移的 context source of truth。

## 2026-06-17 外部产品扫描

这次搜索后，可以把相邻产品分成几类。

第一类是大模型平台自带的 memory / project / export。ChatGPT 支持数据导出、memory、project memory 和 file library，但这些能力主要在 ChatGPT 账户体系内生效，导出更偏合规和备份。Claude 已经提供 memory import/export，并明确支持从其他 AI provider 迁移 memory，不过它迁移的是 memory，不是完整 conversation history。这说明大厂已经确认了 memory portability 的需求，但它们的默认方向仍是把 memory 留在各自平台内。

参考：

- [OpenAI: export ChatGPT history and data](https://help.openai.com/en/articles/7260999-how-do-i-export-my-chatgpt-history-and-data)
- [OpenAI: Memory FAQ](https://help.openai.com/articles/8590148-memory-faq)
- [Claude: import and export your memory](https://support.claude.com/en/articles/12123587-import-and-export-your-memory-from-claude)

第二类是 AI coding 工具里的规则和项目记忆。Cursor 有 persistent rules / `AGENTS.md`，Cline 有 Memory Bank，Windsurf 有 memories/rules。这类方案验证了 markdown/rules 是有效载体，但通常绑定在某个工具或某个 repo 内，跨机器、跨工具、跨账户迁移仍需要额外层。

参考：

- [Cursor Rules](https://cursor.com/docs/rules)
- [Cline Memory Bank](https://docs.cline.bot/best-practices/memory-bank)
- [Cline Rules](https://docs.cline.bot/customization/cline-rules)

第三类是跨工具 memory / config layer。`memories.sh` 已经非常接近我们讨论的方向：local-first CLI、MCP、生成各工具的 instruction files，并能导入 `.claude/skills`、`.codex/skills` 这类配置。它还支持 Claude Code、Cursor、OpenCode、Windsurf、Codex 等多工具集成。`memoir` 也直接把定位写成“every tool, every machine, one memory”，强调文件所有权、E2E encryption、local + git backup、跨工具注入和 session continuity。`Memorix` 则是开源 cross-agent memory layer，通过 MCP 支持 Cursor、Claude Code、Codex、Windsurf、Gemini CLI、GitHub Copilot 等。

参考：

- [memories.sh documentation](https://memories.sh/docs)
- [memories.sh CLI reference](https://memories.sh/docs/cli)
- [memories.sh Claude Code integration](https://memories.sh/docs/integrations/claude-code)
- [memories.sh OpenCode integration](https://memories.sh/docs/integrations/opencode)
- [memoir](https://memoir.sh/)
- [memoir GitHub](https://github.com/camgitt/memoir)
- [Memorix GitHub](https://github.com/AVIDS2/memorix)

第四类是 git-backed agent memory。Letta Code 的 Context Repositories 已经明确把 agent context 放到本地 filesystem，并用 git-based versioning 管理。Letta 后续博客还提到把 legacy server memory tools 转向 filesystem operations on git-backed context repositories。Beads 也用 Git 仓库里的 versioned JSONL 文件解决 coding agent 在 branch 切换、长任务和上下文窗口变化时的记忆连续性。

参考：

- [Letta: Context Repositories](https://www.letta.com/blog/context-repositories/)
- [Letta: Our Next Phase](https://www.letta.com/blog/our-next-phase/)
- [Letta: Context Constitution](https://www.letta.com/blog/context-constitution/)
- [Beads: Git-Backed Memory for AI Agents](https://yuv.ai/blog/beads-git-backed-memory-for-ai-agents-that-actually-remembers)

第五类是 vault / typed memory infrastructure。CtxVault 把 memory 分成 semantic vault 和 skill vault：前者保存 agent 知道什么，后者保存 agent 如何行动。这和我们把 context 分成 knowledge、skill、tool、secret、private scope 的思路接近。它的价值在于把隔离做成结构边界，而不是只靠 metadata filter。

参考：

- [CtxVault GitHub](https://github.com/Filippo-Venturini/ctxvault)

这轮扫描后的结论是：类似方向已经出现，而且速度很快。`memories.sh`、`memoir`、Letta Code Context Repositories 是最接近的参照物。它们验证了三个判断：context 需要跨工具；Git / filesystem 是合理的真相源；MCP 是当前最现实的接入层。

不过仍有明显空位：现有产品大多各自覆盖一段，比如 memory、rules、MCP、git-backed context、skills import、instruction file generation，但还没有形成一个统一的跨工具 AI environment sync layer。我们的机会不在“第一个做 AI memory sync”，而在把 rules、memory、skills、MCP config、tool manifests、secret references 和设备恢复流程放进同一个可迁移系统。

## 产品判断

值得做，但不能按“还有没有人做”来判断。这个方向已经有人正面在做，说明需求真实；真正要判断的是能不能在定位、体验、安全和迁移覆盖面上做出差异。

但不应该做成简单的聊天记录同步。更合理的产品抽象是 AI Environment Passport / Context Vault：把个人 AI 工作环境抽象成可迁移、可审计、可选择同步的一组资产。

这个产品不应该绑定 Rimbo、金融或任何单一业务。它应该服务所有重度 AI 工具用户：换电脑、换 IDE、同时使用多个 agent 工具时，用户希望自己的 rules、skills、memory、MCP 配置和工具上下文可以像 dotfiles 一样迁移，但比 dotfiles 更懂 AI agent 的运行时语义。

最接近这个定位的产品是 `memories.sh` 和 `memoir`。

`memories.sh` 已经覆盖“一个 memory store 给所有 AI coding tools”，能同步 `.agents`、`.claude`、`.cursor`、`.codex`、`.windsurf`、`.cline`、`.gemini`、`.roo`、`.opencode` 等配置目录，包含 instructions、commands、skills、rules、tasks、MCP config。它还提供 generated files 和 MCP server 两种接入方式。它的 npm 包声明 `Apache-2.0`，代码仓库 `webrenew/memories` 公开可访问。也就是说，如果只做“跨工具配置文件同步”，`memories.sh` 已经非常正面，而且不是闭源竞品。

`memoir` 更偏“跨工具、跨机器的一份 AI memory”，强调 MCP、E2E encryption、local + git backup、session handoff、decision registry 和 cross-machine sync。它支持 Claude Code、Cursor、Windsurf、Gemini、ChatGPT、Codex、Copilot、Zed、Cline、Continue、Aider 等工具。它已经把“every tool, every machine, one memory”作为核心叙事。

`Memorix` 是开源 cross-agent memory layer，覆盖 Cursor、Claude Code、Codex、Windsurf、Gemini CLI、GitHub Copilot、OpenCode 等工具，重点在 MCP memory、workspace sync、multi-agent orchestration 和 dashboard。

`Pieces` 是另一个强参照，但它更像 OS-level long-term memory 平台，通过 PiecesOS + MCP 把本地工作流上下文接入 Cursor、Claude Code、Windsurf、Codex CLI、Gemini CLI 等工具。它不是以“配置和 skill 同步”为主，而是以“捕获和召回工作流上下文”为主。

`Letta Context Repositories` 验证了 git-backed context/memory 的架构方向，但它主要是 Letta Code 里的 agent memory 设计，不是面向所有热门 AI 工具的配置迁移产品。

因此这个方向仍然可以做，但切入点要更尖锐：不要做另一个泛 memory MCP server，而要做“AI tool environment sync”。核心卖点是把各工具的上下文资产做成可审计、可恢复、可跨设备迁移的个人仓库，并且提供比竞品更好的 import / doctor / conflict / secret reference / restore UX。

## 基于 memories.sh 开源版本的设计判断

`memories.sh` 的开源版本可以作为高价值参照，但不建议简单 fork 后换皮。

它已经解决了很多脏活：工具检测、不同工具配置格式生成、`.agents/` 中间层、MCP server、skills/rules ingestion、文件同步目标枚举、dry-run/apply 这类操作语义。直接从零做这些 adapter 成本不低，而且每个工具的目录和配置格式都在变化，维护成本会持续存在。

但它的产品中心仍然是 memory store：本地 SQLite 保存 memory，生成各工具配置；文件同步能力也是围绕它的 store 和可选 cloud sync 展开。我们想做的中心应该是 AI environment repo：个人 Git 仓库是上下文真相源，平台/CLI/desktop 负责导入、索引、校验、恢复和注入。

更合理的路线是三层复用：

1. 参考或复用 adapter 层：Codex、Claude Code、Cursor、Windsurf、OpenCode、Cline、Gemini CLI 等工具的路径识别、文件格式生成、MCP config 写入、skills/rules 扫描。
2. 重做 source-of-truth 层：不要以 SQLite/cloud 为最终真相源，而是以用户自己的 Git repo 为真相源。SQLite 只作为本地索引和缓存。
3. 重做 product workflow：重点不是 `add memory -> generate config`，而是 `scan -> normalize -> commit -> sync -> import -> doctor -> restore`。

可以把 `memories.sh` 理解成“rules/memory generator”，而我们的产品要做“AI 工具环境迁移器”。这两个东西会重叠，但成功标准不同。

如果基于开源版本推进，建议先做一个 spike，而不是马上 fork 成产品：

- 克隆 `webrenew/memories`，跑通 CLI 和 test。
- 读 `packages/cli/src/lib` 和 tool adapters，确认 adapter 边界是否清楚。
- 跑 `memories files ingest --dry-run` 扫当前机器，评估它能识别多少真实 Codex/Claude/Cursor/Windsurf 配置。
- 设计一个 `context repo` 输出层，把 scan 结果写成 Git repo 目录，而不是写回 memories 的 store。
- 做 `context doctor`：检查缺失工具、缺失 secret、路径漂移、配置冲突、无法恢复项。

fork 的好处是启动速度快，可以沿用现成工具覆盖面。代价是产品心智容易被原项目牵引，最后变成另一个 memory CLI。长期更好的结构是“借 adapter，不借产品中心”：保留工具兼容层，重新设计仓库 schema、同步模型、安全模型和恢复体验。

Apache-2.0 许可证允许商业使用、修改和分发，但需要保留 license/copyright/NOTICE 等要求。真正采用前还要检查依赖许可证、cloud sync 相关代码、品牌命名和服务端组件边界。

## 2026-06-17 memories.sh spike

本次在 `adhoc_jobs/tmp_ai_context_sync_spike/` 做了一个轻量 spike，目标是验证 `memories.sh` 开源版本是否适合作为基础。

执行动作：

- 克隆 `https://github.com/webrenew/memories.git`。
- 阅读 `packages/cli` 结构、许可证、CLI 入口、文件同步和工具 adapter。
- 在隔离目录安装发布包 `@memories.sh/cli@0.7.9`，使用 `--ignore-scripts` 避免 postinstall 修改全局工具配置。
- 因 `--ignore-scripts` 导致 `sharp` native binary 缺失，在隔离目录执行 `npm rebuild sharp --foreground-scripts` 修复。
- 使用独立 `MEMORIES_DATA_DIR` 运行 `memories --help`、`memories doctor --local-only` 和 `memories files ingest --global --dry-run`。

真实命令示例：

```bash
mkdir -p adhoc_jobs/tmp_ai_context_sync_spike
git clone https://github.com/webrenew/memories.git adhoc_jobs/tmp_ai_context_sync_spike/memories

cd adhoc_jobs/tmp_ai_context_sync_spike/runner
npm init -y
npm install @memories.sh/cli@0.7.9 --ignore-scripts
npm rebuild sharp --foreground-scripts

MEMORIES_DATA_DIR=$PWD/.memories-data ./node_modules/.bin/memories --help
MEMORIES_DATA_DIR=$PWD/.memories-data ./node_modules/.bin/memories doctor --local-only
MEMORIES_DATA_DIR=$PWD/.memories-data ./node_modules/.bin/memories files ingest --global --dry-run > ../global_files_ingest_dry_run.txt
```

源码结构观察：

- `packages/cli/src/commands/files-constants.ts` 定义 `SYNC_TARGETS` 和 `OPTIONAL_CONFIG_TARGETS`，是跨工具文件同步的核心清单。
- `packages/cli/src/commands/files.ts` 实现 `files ingest/list/show/apply`，负责把工具配置读入 SQLite，再从 SQLite 写回磁盘。
- `packages/cli/src/commands/files-helpers.ts` 实现路径扫描、optional config redact、Vault push/fetch 和 scope 选择。
- `packages/cli/src/lib/tool-adapters.ts` 实现从 `.agents/` 生成 Claude、Cursor、Windsurf、Cline、Roo、Gemini 等工具格式。
- `packages/cli/src/lib/setup-tools.ts` 定义工具检测、MCP 配置路径和工具级 setup hint。
- `packages/cli/src/lib/setup.ts` 负责给检测到的全局工具写入 `SKILLS.md` 使用指南。

本机 dry-run 结果：

```text
Would import 1768 files
Cursor   832
Codex    562
Agents   274
Claude    94
Openclaw   6
```

开启 `--include-config` 后，增加到 1770 行 dry-run 输出，额外识别：

```text
.config/opencode/opencode.json [Config]
.openclaw/openclaw.json [Openclaw]
```

这个结果说明它已经能真实识别本机大量 AI 工具上下文，尤其是 `~/.codex/skills`、`~/.cursor`、`~/.claude`、`.agents`。但也暴露出一个问题：它会递归同步 skill 目录下的依赖和参考文件，甚至包括某些 skill 自带的 `node_modules`、`package-lock.json`、大量 reference 文档。作为 memory/config sync 这可以接受，作为“跨设备环境恢复”则需要更细的 manifest 和 ignore 策略。

可复用价值：

- 工具覆盖面值得借：`.agents`、`.claude`、`.cursor`、`.codex`、`.windsurf`、`.cline`、`.gemini`、`.roo`、`.opencode`、`.factory`、`.openclaw`、`.amp` 等都已经进入 `SYNC_TARGETS`。
- 工具检测模型值得借：`TOOLS` 里同时记录 project detect paths、global detect paths、MCP config path、instruction file 和 generate target。
- dry-run/apply 操作语义值得借：所有破坏性写入前都可以先展示会导入/写出的文件。
- optional config 默认排除值得借：敏感 app-level config 需要显式 `--include-config`。
- redact 思路值得借：它按 key 名识别 `token`、`secret`、`password`、`api_key`、`cookie` 等字段并替换为 `[REDACTED]`。

主要限制：

- 真相源是 SQLite + 可选 cloud sync，不是用户拥有的 Git repo。
- optional config secrets 走它自己的云端 Vault，和我们想要的 1Password/Keychain/Vault reference 不同。
- `files ingest --project` 默认仍带 global，CLI 没有 `--no-global`，project-only 体验不够清晰。
- `Codex` 在 setup tool 里更多通过 `Agent Harness (.agents)` 处理，原生 `~/.codex` 作为一等工具的产品语义还可以加强。
- 当前同步粒度偏文件级，缺少“这个文件为什么同步、如何恢复、依赖是否可安装、secret 是否已授权”的 doctor 语义。
- 递归同步 skill 目录会把运行时依赖和大量参考材料带入，后续需要 `sync_policy`：source-only、with-references、with-runtime、exclude-generated。

设计结论：

不要直接 fork 成一个新产品。更好的路线是借 adapter 和 target registry，重做 source-of-truth 和恢复流程。

推荐结构：

```text
memories.sh 可借部分
  tool registry
  sync targets
  config scanner
  adapter generator
  dry-run/apply interaction

我们重做部分
  Git-backed context repo schema
  import/export manifest
  context doctor
  secret reference model
  restore state
  conflict resolution
  tool install/dependency check
```

第一版 spike 后的产品切入点更明确：做 `AI tool environment sync`，不是做另一个 `memory add/search/generate` CLI。核心命令应该围绕：

```text
context scan
context export
context import
context doctor
context restore
context sync
```

`memories.sh` 证明跨工具配置和 skill 扫描有真实需求，也证明 adapter 维护成本高。基于它设计是合理的，但产品中心必须从 memory store 转向 device restore。

## memoir 的定位判断

`memoir` 比 `memories.sh` 更接近“跨工具、跨机器的一份 AI memory”。它公开定位是 every tool, every machine, one memory，支持 Claude Code、Cursor、Windsurf、Gemini、ChatGPT、Codex、Copilot、Zed、Cline、Continue、Aider 等工具。它通过 MCP 给各工具提供共享 memory，并强调 AES-256-GCM / E2E encryption、local + git backup、cross-machine sync、merge-not-overwrite、session handoff、decision registry。

这说明 `memoir` 正面解决了两个我们关心的问题：

- 跨机器同步：不是单机 local memory，而是多设备共享。
- 跨工具读取：通过 MCP 让多个 AI 工具读写同一份 memory。

但它的中心仍然是 memory continuity，而不是 tool environment restore。它保存 goals、decisions、rationale、next actions、history 这类 agent 记忆；它的 install 流程是创建/使用私有 repo 备份 memory，再把 MCP 接入各工具。它不以同步和恢复各工具的原生配置目录为主，也不是专门处理 `~/.codex/skills`、`.claude/skills`、`.cursor/rules`、`.windsurf/rules`、`.opencode`、MCP manifests、tool permissions、secret references、依赖安装状态这些环境资产。

所以 memoir 是更强的 memory 竞品，不是完整的 environment sync 竞品。

对我们设计的启发：

- 需要有 E2E encryption 和用户持有密钥，否则跨设备记忆同步的安全叙事不够强。
- 需要支持 conflict-free / merge-not-overwrite，因为多设备同时写 memory 很常见。
- 需要 session handoff 和 decision registry，因为这是真正提升跨工具连续性的核心能力。
- 需要把 Git backup 做成用户可理解的资产，而不是隐藏实现细节。

我们和 `memoir` 的差异应该放在“从 memory continuity 扩展到 environment portability”：

```text
memoir
  shared memory
  decisions / goals / rationale
  MCP recall/write
  encrypted cross-machine sync

我们的方向
  shared memory
  tool config sync
  skills/workflows sync
  MCP manifest sync
  secret reference restore
  device doctor
  dependency/install status
  native tool config import/export
```

如果只做 memory sync，`memoir` 已经非常接近，而且产品叙事很清楚。要继续做，必须把第一版定位成“热门 AI 工具上下文和配置的跨设备恢复”，memory 只是其中一类资产。

## 2026-06-17 memoir 源码 spike

本次在 `adhoc_jobs/tmp_memoir_spike/` 拉取了 `https://github.com/camgitt/memoir.git`，阅读源码并跑了最小验证。

执行动作：

- 克隆 `camgitt/memoir`。
- 阅读 `src/adapters`、`src/providers`、`src/security`、`src/session`、`src/workspace`、`src/mcp.js` 和 CLI 入口 `bin/memoir.js`。
- 执行 `npm install --ignore-scripts`，避免 postinstall 做额外动作。
- 跑 `node bin/memoir.js --help` 和 `node bin/memoir.js doctor`。
- `doctor` 触发默认 telemetry disclosure，在 `~/.config/memoir/` 写入 `telemetry-disclosed` 和 `telemetry-id`。确认时间戳后已删除。后续再跑 memoir 命令应加 `DO_NOT_TRACK=1`。

真实命令示例：

```bash
mkdir -p adhoc_jobs/tmp_memoir_spike
git clone https://github.com/camgitt/memoir.git adhoc_jobs/tmp_memoir_spike/memoir

cd adhoc_jobs/tmp_memoir_spike/memoir
npm install --ignore-scripts
DO_NOT_TRACK=1 node bin/memoir.js --help
DO_NOT_TRACK=1 node bin/memoir.js doctor
```

源码结构观察：

- `src/adapters/index.js` 定义工具 adapter 和过滤规则，负责从各工具目录提取可同步内容。
- `src/adapters/restore.js` 负责把备份目录写回各工具目录，并处理 Claude project path remap 和 `MEMORY.md` index reconcile。
- `src/providers/index.js` 实现 local/git provider。Git provider 会临时 clone 远端 repo、清空非 `.git` 内容、复制 staging、commit、push。
- `src/security/encryption.js` 实现 AES-256-GCM + scrypt，目录级加密会把文件名 HMAC hash，并加密 manifest。
- `src/security/scanner.js` 实现 secret pattern 扫描和 redact。
- `src/session/state.js` 用 `~/.config/memoir/session.json` 保存 goal、next actions、open questions、decisions、history 和 machine ids，并支持跨机器 merge。
- `src/session/inject.js` 把 session block 注入 Claude、Cursor、Windsurf、Gemini 等工具的全局 instruction 文件。
- `src/workspace/tracker.js` 扫描 home 下项目，记录 git remote、branch、last commit、dirty patch，restore 时 clone repo 并尝试 apply patch。
- `src/mcp.js` 提供 MCP tools：recall、remember、list/read、consolidate、status、goal/next/decision/session 等。

最小验证结果：

```text
memoir doctor
Config: not initialized
Git: installed
Claude CLI: 6 files, 5.8kb
OpenAI Codex: 0 files, 0B
Cursor: 2 files, 4.5kb
Windsurf: 2 files, 4.0kb
Total backup size: 14.4kb across 10 files
```

这个结果和源码一致：`memoir` 的 adapter 默认更保守。它会检测 `~/.codex`，但 Codex 过滤规则只允许根级 `config.json`、`settings.json`、`instructions.md`，不会同步 `~/.codex/skills`。因此在这台机器上 `OpenAI Codex` 显示 0 files。相比之下，`memories.sh` 的 `SYNC_TARGETS` 会递归扫 `~/.codex/skills`，覆盖更强但噪声更大。

`memoir` 实际比官网 memory sync 叙事更进一步：它已经有 workspace 和 session restore。

- Session：`session.json` 是当前 goal、next action、decision、history 的 source of truth，带 machine id，merge 时按文本去重、按时间取新。
- Workspace：扫描 git projects，保存 remote、branch、last commit、dirty patch；restore 时 clone remote 并尝试 apply patch。非 git 小项目可以打 tar.gz bundle。
- Tool config：按 adapter 抽取工具配置，再 restore 到本机目录。
- Handoff：从 Claude session 里提取 handoff，保存到 backup 和本地 `~/.config/memoir/handoffs`。

不过它和我们目标仍然有几个关键差异：

- Git repo 是 backup destination，不是用户可编辑、可审查的 context source-of-truth schema。每次 push 会临时 clone 并清空远端非 `.git` 内容再复制 staging。
- 工具环境覆盖不完整，尤其 Codex skills、Claude skills、MCP manifests、tool permission policy、provider/model routing 都没有作为一等恢复对象。
- Restore 是按 adapter 直接写回工具目录，缺少我们想要的 `context doctor` 级别说明：哪些工具未安装、哪些 secret 未授权、哪些依赖需要安装、哪些配置存在冲突。
- Secret 模型是扫描/redact 或加密 backup，不是 secret reference。我们要的是 `1password://`、Keychain、Vault、env template 这类可恢复引用。
- MCP recall 是关键词搜索工具目录文件，不是结构化 context repo 查询，也不是 embedding/RAG。
- 默认 telemetry 是 opt-out，并会在首次命令写 `~/.config/memoir/telemetry-id`。如果借代码，需要调整默认安全姿态。

可借部分：

- Session state schema：goal、next actions、open questions、decisions、history、machine ids。
- Session merge 逻辑：跨机器 union + dedupe + cap。
- Pinned session block 注入：用 marker 替换，不碰 marker 外内容。
- AES-256-GCM + scrypt 的本地加密实现。
- Secret scanning pattern。
- Claude project path remap 和 `MEMORY.md` reconcile 经验。
- Workspace restore 的 git remote/branch/dirty patch 思路。

不建议直接借的部分：

- Git provider 的“清空 repo 后复制 staging”模型。我们需要 Git repo 自身就是稳定 schema 和用户可审查资产。
- 当前 adapter coverage。需要合并 `memories.sh` 的更完整 target registry，尤其 skills、MCP、rules。
- 默认 telemetry。我们的本地工具应默认不发送，至少首次运行前明确 opt-in。

综合判断：

`memoir` 是更强的跨机器 memory/session 参考，`memories.sh` 是更强的跨工具 config/skills adapter 参考。我们的实现如果推进，最合理的组合是：

```text
memoir 可借
  session continuity
  encrypted backup
  machine-aware merge
  workspace dirty patch
  pinned block injection

memories.sh 可借
  tool registry
  sync target coverage
  generated config adapters
  files ingest/apply dry-run

我们重做
  Git-backed context repo schema
  native AI tool environment manifest
  secret reference restore
  dependency/install doctor
  conflict resolution
  source-of-truth workflow
```

## 目标工具范围

第一版应该明确覆盖热门 AI agent / coding 工具，而不是只做抽象的 memory store。

优先级最高的是：

- Codex：`~/.codex/skills`、全局 instructions、MCP/tool 配置、会话摘要、项目级 `AGENTS.md`。
- Claude Code：`.claude/`、Claude skills、project memory、MCP 配置、permission/tool policy。
- Cursor：`.cursor/rules`、project rules、user rules、MCP 配置、IDE 内 agent 偏好。
- Windsurf：memories、rules、Cascade 相关配置、MCP 配置。
- OpenCode：agent instructions、tool config、provider/model routing、MCP 配置。
- Cline / Roo Code：Memory Bank、rules、MCP 配置、tool permission。
- Gemini CLI：全局/项目 instructions、MCP 配置、provider credentials reference。

同步对象分成几类：

- Rules / instructions：`AGENTS.md`、`.cursor/rules`、`.clinerules`、Claude/Codex/OpenCode instruction files。
- Skills / workflows：Codex skills、Claude skills、用户自定义 workflow、脚本依赖和 smoke test。
- Memory：用户偏好、项目记忆、工具生成的 memories、压缩后的 session summaries。
- MCP / tools：MCP server manifest、tool enablement、permission policy、环境变量模板。
- Secrets references：API key、OAuth token、cookie、SSH key 只保存引用和恢复状态，不保存明文。
- Device restore state：哪些工具已安装、哪些配置已恢复、哪些 secret 需要重新授权。

产品的核心体验应该是：用户在 A 电脑配置好 Codex、Claude Code、Cursor、Windsurf 等工具后，在 B 电脑 clone 个人 context repo，运行一次 import/doctor，就能知道哪些上下文已经恢复，哪些工具缺依赖，哪些 secret 需要重新授权。

## 双层架构

安全上可以分成两层：user-owned storage 和 platform capability。

### 第一层：基于 Git 的个人仓库

个人 Git 仓库作为上下文的真相源。它存放可迁移、可审计、可 diff 的上下文资产。平台不拥有这份数据，只提供读写、加密、同步和校验能力。

适合进入 Git 仓库的内容：

- `profile/`：沟通风格、长期偏好、工作方式。
- `workspaces/`：项目规则、架构说明、常用命令、测试方式、历史踩坑。
- `skills/`：个人 skill、workflow、触发说明、依赖和 smoke test。
- `tools/`：MCP 配置模板、工具 manifest、环境变量模板。
- `memories/`：经过提炼的 memory summaries、decision logs、open questions。
- `manifests/`：设备清单、导入记录、索引状态、恢复检查结果。

一个可能的目录结构：

```text
ai-context/
  profile/
    communication.md
    preferences.md
  workspaces/
    example_project/
      AGENTS.md
      architecture.md
      commands.md
      memories.md
      decisions.jsonl
  skills/
    defining-goals/
    report-builder/
  tools/
    mcp.manifest.json
    env.template
  manifests/
    devices.json
    import_log.jsonl
```

密钥不应明文进入 Git。仓库里只保存 secret reference：

```json
{
  "name": "openai",
  "type": "api_key",
  "secret_ref": "1password://Private/OpenAI API Key",
  "required_scopes": ["responses", "embeddings"]
}
```

换电脑时，用户 clone 仓库并 import。平台检查缺失 secret、缺失依赖和失效路径，再引导用户重新授权 1Password、Keychain、Vault 或企业 SSO。

### 第二层：平台提供的能力

平台层负责把 Git 中的静态资产变成可用的 agent runtime context。

核心能力包括：

- 文件级加密：普通 rules/skills 可明文，个人记忆、私有项目配置、敏感 tool manifest 可加密。
- 敏感信息扫描：每次写入 Git 前扫描 API key、cookie、SSH private key、access token、客户 PII、内部 URL。
- Context permission model：按 `global`、`workspace`、`tool`、`secret`、`private` 控制注入范围。
- 可解释召回：记录每次 agent 使用了哪些 memory、文件和规则，以及为什么相关。
- 语义索引与召回：本地优先，云端索引作为 opt-in。
- 冲突合并：Git 处理版本，平台处理语义冲突，尤其是规则文件和偏好文件。
- 跨工具注入：把同一份 context 暴露给 Codex、Claude Code、Cursor、Windsurf、MCP client。
- 迁移体检：新设备导入后检查 skill 依赖、MCP server、secret reference、工作区路径和索引状态。

平台的默认立场应是 local-first, git-backed, cloud-assisted。用户可以只用本地 Git，也可以打开平台同步。这样安全叙事比“把你的 AI memory 全传到我们云上”更可信。

## Context Scope Model

上下文不应该无差别注入给所有 agent。可以先按下面的 scope 设计：

```text
global     个人偏好、沟通风格、长期原则
workspace  当前项目规则、架构、决策、常用命令
tool       某个 MCP/tool 的配置说明和使用边界
secret     只能通过 secret_ref 调用，不能直接读取值
private    需要用户确认后才能注入
```

这里还需要补一个 provenance 维度：每条 memory、rule、skill 或 tool config 应尽量带来源、日期、适用范围和失效条件。这样 agent 使用历史上下文时，用户能知道它来自哪个工具、哪台设备、哪个项目或哪次导入。

## MVP

第一版可以很小，重点验证迁移价值。

1. `context init`：创建本地 context repo。
2. `context export`：扫描 Codex/Cursor/Claude/Windsurf 配置和 skills，生成 manifest。
3. `context import`：新电脑 clone 后恢复 rules、skills、MCP 配置模板。
4. `context doctor`：检查缺失 secret、缺失依赖、失效路径和不可恢复项。
5. `context sync`：commit/push/pull，并执行 secret scan。
6. Desktop UI：展示哪些上下文已迁移，哪些需要重新授权。

第一版成功标准不是同步所有聊天历史，而是换电脑后 agent 仍然知道用户的项目规则、个人 skill、历史决策、常用资料目录和最近工作状态。

## 需要避免的方向

不要把 Git 仓库当成简单备份盘。它应该是用户拥有的 context source of truth。

不要默认同步明文密钥。secret 应通过 reference 和本地授权恢复。

不要无差别导入全量聊天记录。全量对话体积大、噪声高、隐私风险高。更好的方式是提炼 decisions、facts、open questions、source links 和 run summaries。

不要把平台云端设计成唯一真相源。平台的价值在于把用户拥有的上下文安全地变成 agent 可用的运行时上下文。

## 下一步

如果继续推进，可以先做一个本地 prototype：

- 扫描当前机器的 `~/.codex/skills`、workspace `AGENTS.md`、`rules/`、MCP 配置。
- 生成 `ai-context/` 仓库结构和 `manifest.json`。
- 跑一次 secret scan。
- 在临时目录模拟新设备 import。
- 输出一份 `context doctor` 报告，列出可恢复项、需授权项和不可恢复项。

这能快速验证真实迁移链路，也能暴露哪些上下文现在只存在于对话里、没有稳定落盘位置。
