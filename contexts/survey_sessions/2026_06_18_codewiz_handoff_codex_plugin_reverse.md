# Codewiz Handoff Codex Plugin Reverse

日期：2026-06-18

## 背景

本机 Claude Code 已安装 `codex@openai-codex` 插件。它的架构不是单个 skill，而是 plugin + slash commands + subagent + Node companion + hooks：

- slash command 负责入口和交互模式选择；
- Node companion 负责 app-server 调用、后台 job、status/result/cancel；
- subagent 只做薄转发，避免中间 agent 改写任务；
- hook 可做 stop-time review gate；
- 状态按 workspace 写入插件数据目录。

Codex 当前也支持 plugin，但 Codex plugin 的暴露形态主要是 `.codex-plugin/plugin.json`、skills、scripts、MCP/apps 和 hooks；没有直接等价 Claude slash command 的机制。因此反转实现应以 Codex skill 为入口，以脚本提供 job 生命周期。

## 已实现

创建本地 Codex plugin：

```text
/Users/xuhao/plugins/codewiz-handoff/
  .codex-plugin/plugin.json
  skills/codewiz-handoff/
  scripts/codewiz-companion.mjs
```

同时创建 CLI 可识别的本地 marketplace：

```text
/Users/xuhao/.agents/codewiz-marketplace/
  .agents/plugins/marketplace.json
  plugins/codewiz-handoff -> /Users/xuhao/plugins/codewiz-handoff
```

并在 Codex 配置中启用：

```toml
[marketplaces.codewiz-local]
source_type = "local"
source = "/Users/xuhao/.agents/codewiz-marketplace"

[plugins."codewiz-handoff@codewiz-local"]
enabled = true
```

## Companion 能力

入口：

```bash
node ~/plugins/codewiz-handoff/scripts/codewiz-companion.mjs inspect --repo /path/to/repo
node ~/plugins/codewiz-handoff/scripts/codewiz-companion.mjs scenario review-diff --repo /path/to/repo --base origin/main
node ~/plugins/codewiz-handoff/scripts/codewiz-companion.mjs scenario second-opinion --repo /path/to/repo --prompt /path/to/prompt.md
node ~/plugins/codewiz-handoff/scripts/codewiz-companion.mjs scenario implement-subtask --repo /path/to/repo --prompt /path/to/prompt.md
node ~/plugins/codewiz-handoff/scripts/codewiz-companion.mjs status --repo /path/to/repo --all
node ~/plugins/codewiz-handoff/scripts/codewiz-companion.mjs result --repo /path/to/repo
node ~/plugins/codewiz-handoff/scripts/codewiz-companion.mjs cancel --repo /path/to/repo <job-id>
```

状态目录：

```text
~/.codex/codewiz-companion/state/<workspace-slug-hash>/
  state.json
  jobs/<job-id>.json
  jobs/<job-id>.log
```

底层仍复用已验证的：

```text
skills/codewiz-handoff/scripts/codewiz_handoff.sh
```

可信交付物仍是：

```text
~/.codex/agent_handoff_runs/<timestamp>_<mode>/result.json
git status / git diff
```

## 验证

- `node --check scripts/codewiz-companion.mjs` 通过。
- `bash -n skills/codewiz-handoff/scripts/codewiz_handoff.sh` 通过。
- `validate_plugin.py /Users/xuhao/plugins/codewiz-handoff` 通过。
- `inspect` smoke 通过，解析到 `/opt/homebrew/bin/codewiz-cc`，版本 `0.0.34 (codewiz-cc)` / `2.1.174 (Claude Code)`。
- `codex plugin marketplace add /Users/xuhao/.agents/codewiz-marketplace` 成功。

## 后续升级

下一步可继续补齐：

- Codex hook review gate；
- 更严格的 background worker 进程树取消；
- `review/result/status` 的 UI 友好输出；
- 如果 `codewiz-cc` 未来暴露 app-server/MCP/JSON-RPC，则替换当前文件协议；
- 将插件发布到团队 marketplace，而不是只放在个人本机。

## Skill 分享包

如果接收方已有 skill 分享/安装链路，不需要使用 Codex plugin marketplace。已生成独立 skill 包：

```text
/Users/xuhao/Downloads/codewiz-handoff-skill.zip
```

包内结构：

```text
codewiz-handoff/
  SKILL.md
  agents/openai.yaml
  scripts/codewiz-companion.mjs
  scripts/codewiz_handoff.sh
  scripts/result_schema.json
```

`codewiz-companion.mjs` 已兼容两种布局：

- standalone skill：`codewiz-handoff/scripts/codewiz_handoff.sh`
- plugin 内嵌 skill：`codewiz-handoff/skills/codewiz-handoff/scripts/codewiz_handoff.sh`

安装到 Codex 全局 skill 目录：

```bash
unzip codewiz-handoff-skill.zip
mkdir -p ~/.codex/skills
cp -R codewiz-handoff ~/.codex/skills/
```

前置依赖仍是全局 `codewiz-cc`：

```bash
npm config set @xhs:registry http://npm.devops.xiaohongshu.com:7001
npm install -g @xhs/codewiz-cc@latest
codewiz-cc -version
```

## Plugin Installer Skill

更推荐的分发方式是分享一个“安装器 skill”，插件文件放在 skill 的 `references/` 中。接收方先安装这个 skill，然后让 Codex 运行安装脚本，把内置 marketplace/plugin 安装到本机。

已生成：

```text
/Users/xuhao/Downloads/codewiz-handoff-plugin-installer-skill.zip
```

包内结构：

```text
codewiz-handoff-plugin-installer/
  SKILL.md
  agents/openai.yaml
  scripts/install_codewiz_handoff_plugin.sh
  references/codewiz-handoff-marketplace/
    .agents/plugins/marketplace.json
    plugins/codewiz-handoff/
```

安装器执行：

```bash
~/.codex/skills/codewiz-handoff-plugin-installer/scripts/install_codewiz_handoff_plugin.sh
```

安装器会：

1. 将 `references/codewiz-handoff-marketplace/` 复制到 `~/.agents/codewiz-marketplace/`；
2. 执行 `codex plugin marketplace add ~/.agents/codewiz-marketplace`；
3. 在 `~/.codex/config.toml` 启用 `[plugins."codewiz-handoff@codewiz-local"]`；
4. 验证 marketplace/plugin/companion/skill/handoff/schema 文件完整；
5. 执行 `node --check` 和 `bash -n`；
6. 验证 marketplace 注册和 config 启用状态；
7. 检查 `codewiz-cc` 版本探测；
8. 运行轻量 `inspect` smoke（可用 `--skip-smoke` 跳过）。

2026-06-22 完整测试补充：

- installer 真实安装通过，`codex plugin marketplace add` 对已存在 marketplace 能正常返回；
- 安装后验证全部通过，`warnings=0`；
- 已安装插件的 `inspect` smoke 通过；
- 已安装插件的最小 `task read-only` 真实调用 `codewiz-cc` 通过，返回 `summary=hi`；
- 后台 `inspect --background`、`status`、`result` 通过；
- `cancel` 初测发现只更新 job 状态但未杀掉 worker/子进程，已修复为按 worker pid 递归终止进程树；
- 修复后用 fake long-running worker 复测，`cancel` 返回 `terminatedPids` 且无残留进程。

2026-06-22 大任务与超时测试补充：

- 用真实 `codewiz-cc` 跑较大的 read-only review 任务，目标为 `codewiz-handoff-plugin-installer` 及其内置 plugin 文件，`CODEWIZ_HANDOFF_TIMEOUT_SEC=120`；
- 任务在 120 秒触发 timeout，job 进入 `failed`，`result.summary=worker 超时。timeout=120s`，`handoffExitCode=124`，`metadata.exit_code=124`；
- timeout 后未发现本次 job 相关残留进程；
- 发现 companion 原先记录的 `exitCode` 使用 Node 子进程退出码，可能显示为 `0`；已修复为优先使用 handoff 输出中的 `exit_code`；
- 用 fake long-running worker 复测 3 秒 timeout，修复后 `exitCode=124`、`handoffExitCode=124` 一致。

## Community Edition: Claude Code Handoff

已从内部 `codewiz-handoff` 派生出社区版 `claude-code-handoff`，默认调用真正的 Claude Code CLI：`claude`，不依赖公司 npm 源或 `codewiz-cc`。

本机源码：

```text
/Users/xuhao/plugins/claude-code-handoff/
```

本地 marketplace：

```text
/Users/xuhao/.agents/claude-code-marketplace/
  .agents/plugins/marketplace.json
  plugins/claude-code-handoff/
```

安装器 skill 分享包：

```text
/Users/xuhao/Downloads/claude-code-handoff-plugin-installer-skill.zip
```

安装器 skill 结构：

```text
claude-code-handoff-plugin-installer/
  SKILL.md
  agents/openai.yaml
  scripts/install_claude_code_handoff_plugin.sh
  references/claude-code-handoff-marketplace/
    .agents/plugins/marketplace.json
    plugins/claude-code-handoff/
```

社区版前置依赖：

```bash
npm install -g @anthropic-ai/claude-code@latest
claude --version
```

安装执行：

```bash
~/.codex/skills/claude-code-handoff-plugin-installer/scripts/install_claude_code_handoff_plugin.sh
```

安装器会复制 marketplace、执行 `codex plugin marketplace add ~/.agents/claude-code-marketplace`、启用 `[plugins."claude-code-handoff@claude-code-local"]`、检查 `claude`、运行 `inspect` smoke。

本机验证结果：

- `claude --version` 返回 `2.1.142 (Claude Code)`。
- `validate_plugin.py /Users/xuhao/plugins/claude-code-handoff` 通过。
- `quick_validate.py /Users/xuhao/.codex/skills/claude-code-handoff-plugin-installer` 通过。
- 安装器真实安装通过，`inspect` smoke 解析到 `/Users/xuhao/.local/bin/claude`。
