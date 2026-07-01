# Codex 与 Claude CLI Agent 连接参考

日期：2026-06-18

## 问题

本机已有 `codewiz-cc --dangerously-skip-permissions --append-system-prompt "跟我使用中文进行交互"`，公司内 `codewiz-cc` 可视为 Claude Code 等价入口。目标是让 GPT Codex 能把部分任务、调研、实现或 review 交给这个 Claude 系 Agent，并能拿回可审计结果。

## 业界相近模式

目前更成熟的模式不是两个交互式 CLI Agent 直接互联，而是上层 orchestrator 把另一个 Agent 当成可调用 worker：

- Claude Code Agent SDK：Anthropic 官方把 Claude Code 的 agent loop、工具、权限、session、MCP、subagents 暴露成 Python / TypeScript SDK，适合生产化编排。
- Codex CLI / Codex SDK：OpenAI 官方支持 headless `exec`、本地 `/review`、结构化输出和 CI code review 流程，适合让 Codex 作为 reviewer 或实现 worker。
- OpenCode：开源、多模型、支持 primary agents / subagents，并提供 server / API 形态，适合做中立 agent bus。
- SWE-agent / mini-swe-agent：更偏 benchmark / GitHub issue 自动修复，可作为“从 issue 到 patch”的简洁实现参考。
- Claude Code GitHub Actions / Code Review：把 Agent 接到 PR / issue / review 的工程化路径已经比较成熟。
- A2A / MCP / OpenAI Agents handoffs：协议层有方向，但用于本机两个 CLI 编程 Agent 的交付链路时，MCP 更适合工具接入，A2A 仍偏生态互操作，短期落地成本高于直接 CLI/SDK 编排。

## 对当前机器的建议

先做最小可用桥接层，而不是直接上 A2A：

1. Codex 保持主控，新增一个本地 worker 命令包装 `codewiz-cc`。
2. 所有任务输入先写入文件，worker prompt 只传“读取哪个文件、把结果写到哪个文件”。
3. worker 输出必须包含结构化 JSON：`status`、`summary`、`files_touched`、`findings`、`commands_run`、`next_actions`。
4. review 类任务默认只读，要求引用精确文件和行号；实现类任务允许改文件，但最后用 `git diff --stat` 和测试命令回报。
5. 上层保留审计目录，比如 `tmp/agent_handoff_runs/<run_id>/prompt.md`、`result.json`、`stdout.log`、`stderr.log`。
6. Codex 只消费 worker 的最终文件和 git diff，不把 worker 的全过程灌回主上下文。

## 第一版可以实现的接口

```bash
agent-handoff claude-review --repo /path/to/repo --diff-base origin/main --prompt prompt.md
agent-handoff claude-task --repo /path/to/repo --prompt prompt.md --write
```

底层实际调用类似：

```bash
codewiz-cc \
  --dangerously-skip-permissions \
  --append-system-prompt "跟我使用中文进行交互" \
  "Read task from /abs/run/prompt.md and write JSON result to /abs/run/result.json"
```

## 判断

这件事值得做。它的价值不在于“Codex 和 Claude 互相聊天”，而在于给 Codex 增加一个可审计、可替换的强 worker。第一阶段用文件协议和 CLI wrapper 就够了；等交付链路跑通后，再考虑把它做成 MCP tool、OpenCode server worker，或接到 GitHub review / issue 自动化里。
