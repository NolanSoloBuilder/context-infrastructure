# Skill: Codex 环境迁移

## When to Use

当需要把 Codex / OpenCode / 本机 agent 工作环境迁移到新电脑，或判断哪些配置是否跟随账号同步时使用。

## 核心判断

Codex 账号只解决身份和云端可见资源，不等于完整环境同步。本机行为主要由本地目录、系统依赖、repo 文件和 secrets 决定。换新电脑后，默认需要重新安装应用和 CLI，并迁移或重建本机配置。

## 本机优先迁移项

- `~/.codex/config.toml`：模型、sandbox、MCP、插件和默认行为配置。
- `~/.codex/AGENTS.md`、`~/.codex/skills/`、`~/.codex/superpowers/`、`~/.codex/rules/`：全局规则和 skills。
- `~/.codex/memories/`、`~/.codex/memories_*.sqlite`：本地记忆与索引。
- `~/.codex/automations/`：本机自动化任务定义。
- `~/.codex/plugins/`、`~/.codex/cache/`：插件缓存。可迁移，也可以在新机器重新安装。
- `~/.config/opencode/`：OpenCode 路由、模型和工具配置。
- 各 workspace 的 `AGENTS.md`、`rules/`、`contexts/`：项目级长期约束，通常跟随 git repo。
- shell、Node、Python、Homebrew、Chrome extension、1Password CLI、GitHub CLI、Cloudflare/Vercel 等外部工具链。

## 不建议直接复制的项

- `~/.codex/auth.json`、`.cockpit_codex_auth.json` 等登录态文件：优先在新电脑重新登录。
- secrets、token、cookie：优先从 1Password、平台控制台或正式 secret manager 重新注入。
- 正在写入的 SQLite `*-wal` / `*-shm` 文件：复制前先退出 Codex App 和相关 CLI。

## 推荐迁移流程

1. 旧电脑退出 Codex App、OpenCode 和相关 agent 进程。
2. 新电脑安装全局 Node 环境、Codex App、Codex CLI、OpenCode、GitHub CLI、1Password CLI 和常用系统依赖。
3. 克隆常用 workspace，让项目级 `AGENTS.md`、`rules/`、`contexts/` 跟随 git 恢复。
4. 迁移 `~/.codex/config.toml`、全局 `AGENTS.md`、`skills/`、`memories/`、`automations/` 和 `~/.config/opencode/`。
5. 在新电脑重新登录 OpenAI / Codex、GitHub、1Password、Vercel、Cloudflare、Lark 等外部账号。
6. 跑 smoke：`codex` 能启动、Codex App 能开 thread、MCP / plugin 能发现、常用 workspace 能读取规则、浏览器插件能控制 Chrome。

## 快速打包示例

```bash
cd "$HOME"
tar --exclude='.codex/auth.json' \
  --exclude='.codex/.cockpit_codex_auth.json' \
  --exclude='*.sqlite-wal' \
  --exclude='*.sqlite-shm' \
  -czf codex_env_migration.tgz \
  .codex/config.toml \
  .codex/AGENTS.md \
  .codex/skills \
  .codex/superpowers \
  .codex/rules \
  .codex/memories \
  .codex/automations \
  .config/opencode
```

恢复后先检查路径引用。很多 MCP、workspace、Node、Python、Chrome native host 配置里会写绝对路径，新电脑用户名或目录不同会导致工具可见但运行失败。
