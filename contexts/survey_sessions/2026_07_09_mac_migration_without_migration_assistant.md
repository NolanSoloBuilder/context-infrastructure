# Mac 迁移计划：不用 Migration Assistant

日期：2026-07-09

## 判断

这次迁移不适合走整机复制。你的环境里有大量开发工具、AI agent 配置、公司/个人 App、SSH/GCP/GitHub/1Password/Codex 等认证状态。Migration Assistant 的问题不是能不能搬过去，而是它会把旧机器的缓存、登录态、历史残留和机器绑定状态一起搬过去，后续问题难以定位。

更合理的做法是把新 Mac 当成一台干净机器，用声明式清单恢复可重复部分，用手动登录恢复认证部分，用仓库和外部硬盘恢复数据部分。这里的底座不是单一工具，而是：

- Homebrew Bundle 管系统 CLI、开发依赖和 cask。
- npm global manifest 管全局 Node CLI，并安装到当前全局 Node 环境。
- editor extension manifest 管 VS Code/Cursor 扩展。
- git-backed context repo 管 AI 工具 rules、skills、MCP 模板和非敏感配置。
- 1Password / 服务商控制台 / 手动登录管 secrets 和 auth。

你提到的 `Bravery` 本机没有发现对应配置或命令。我先按可验证的 Homebrew/Brewfile 路线落地；如果你指的是另一个工具，可以把它作为外层编排，但底层仍建议保留这些 manifest。

## 当前机器观察

### Codex 环境

Codex 不能只靠重新登录恢复完整工作环境。当前机器需要单独保留三类内容：

1. 可审计清单：全局 Skills、共享 Agent Skills、已启用插件和 MCP server 名称。
2. 私有可迁移内容：`config.toml`、全局规则、hooks、Skills、memories、automations 和 OpenCode 配置。
3. 重建内容：Codex App、CLI、插件缓存、浏览器控制运行时和登录态。

具体通过 `scripts/backup_codex_environment.sh` 和 `scripts/restore_codex_environment.sh` 完成。私有归档默认写入仓库外的 `~/Documents/CodexMigration/`，不得提交到 Git。`auth.json`、App 状态、附件、日志、插件缓存和运行中的 SQLite 文件不进入默认归档；本地历史会话仅在 `INCLUDE_HISTORY=1` 时额外包含。

已确认：

- Homebrew 在 `/opt/homebrew/bin/brew`。
- Node/npm 在 `/opt/homebrew/bin/node` 和 `/opt/homebrew/bin/npm`，全局 npm prefix 是 `/opt/homebrew`。
- 全局 npm 包包括 `@openai/codex`、`@larksuite/cli`、`@xdevplatform/xurl`、`wrangler`、`eas-cli`、`agent-browser` 等。
- Homebrew formula 约 122 个，核心包括 `git`、`gh`、`node`、`opencode`、`pyenv`、`redis`、`ripgrep`、`watchman`、`cocoapods`、`fastlane`、`gcloud-cli` 等。
- `/Applications` 里有 Codex、Cursor、Google Chrome、Ghostty、iTerm、Warp、Xcode、Figma、Obsidian、LarkSuite、WeChat、Proxyman、MongoDB Compass、Beekeeper Studio、WireGuard、OpenVPN Connect 等。
- `brew list --cask --versions` 当前会因为 `xdevplatform/tap/xurl` 未 trust 报错。新机器上需要显式确认这个 tap 是否可信，再执行 `brew trust xdevplatform/tap`。

需要保护的敏感状态：

- `~/.ssh` 里有多把私钥和 host 记录。
- `~/.codex/auth.json`、`~/.codex/config.toml`、`~/.config/gcloud`、`~/.config/op`、`~/.npmrc` 都可能含 token 或认证状态。
- `~/.codex/sessions`、`~/.codex/memories`、`~/.codex/skills` 有迁移价值，但应按 context asset 迁移，不应把整个 `~/.codex` 当作普通文件夹无脑复制。

## 迁移分层

第一层是系统与工具链。用 `adhoc_jobs/mac_migration_kit/manifests/Brewfile` 恢复 Homebrew formula/cask，用 `manifests/npm-global.txt` 恢复全局 Node CLI。新 Mac 上先装 Xcode Command Line Tools，再跑 `scripts/bootstrap_new_mac.sh`。

第二层是 App。Homebrew cask 能装的 App 交给 Brewfile。Mac App Store、公司 MDM、微信、Lark、Office、TestFlight、Xcode、内部 App 等需要手动安装或登录。这里不要追求全自动，因为很多 App 和设备绑定、账号登录、公司策略相关。

第三层是代码和工作区。`~/Documents/Basic`、`~/Documents/Other`、`~/Documents/Codex` 先恢复目录结构，再按仓库 clone。已有 GitHub/GitLab 远端的项目走 `git clone`；没有远端、包含本地-only 资料或大文件的目录，用外置硬盘或 `rsync` 单独迁移。迁移前用 `scripts/export_inventory.sh` 生成 `git_repositories.txt` 和 `git_repositories.tsv` 作为清单，其中 TSV 包含路径、当前分支和脱敏后的 `origin`。

第四层是 AI 工具上下文。Codex、Claude、OpenCode、Cursor、Windsurf、Gemini 的 rules、skills、MCP 模板、memory 摘要适合进入 git-backed context repo；auth、session、browser state、SQLite runtime 状态不默认迁移。已有 `context-vault` 产品思路里定义过 `context export/import/doctor`，这次可以先用脚本实现最小版本。

第五层是 secrets 和认证。统一原则是新机器重新授权。SSH key 优先重新生成并加到 GitHub/GitLab/GCP；必须保留旧 key 时，用 1Password document 或加密介质迁移。GCP、GitHub、Codex、npm、Lark、Cloudflare、Vercel、OpenAI、1Password 都在新机器重新登录。`.env` 和 `*.secrets.yaml` 从 1Password 或服务商重新生成。

## 执行顺序

旧 Mac：

```bash
cd /Users/xuhao/Documents/Other/context-infrastructure/adhoc_jobs/mac_migration_kit
./scripts/export_inventory.sh
```

然后 review `inventory/<timestamp>/RESTORE_NOTES.md`、`WARNINGS.txt`、`Brewfile.generated`、`npm-global.txt`、`git_repositories.txt`。确认后把长期清单更新到 `manifests/`。

数据备份建议分三份：

- 代码仓库：能 push 的全部 push 到远端。
- 本地-only 数据：外置硬盘或 NAS，用 `rsync -aHAX --info=progress2` 复制指定目录。
- secrets：1Password 或服务商重新授权，不放进 rsync 目录。

新 Mac：

```bash
git clone <context-infrastructure-repo-url> ~/Documents/Other/context-infrastructure
cd ~/Documents/Other/context-infrastructure/adhoc_jobs/mac_migration_kit
./scripts/bootstrap_new_mac.sh
./scripts/clone_repositories.sh
./scripts/doctor_migration.sh
```

如果遇到 `xdevplatform/tap`：

```bash
ALLOW_UNTRUSTED_TAPS=1 ./scripts/bootstrap_new_mac.sh
```

这一步只应在确认 tap 来源可信后执行。

`clone_repositories.sh` 默认是 dry-run。确认 `manifests/git_repositories.current.tsv` 后，再执行：

```bash
DRY_RUN=0 ./scripts/clone_repositories.sh
```

## 验收标准

迁移完成不以 App 都能打开为准，而以关键工作链路能跑通为准：

- `git`、`gh auth status`、`ssh -T git@github.com` 正常。
- `node -v`、`npm -v`、`npm ls -g @openai/codex --depth=0` 正常。
- `codex`、`opencode`、`wrangler`、`eas`、`lark-cli`、`xurl` 至少能执行 `--help` 或登录检查。
- `gcloud auth list` 能看到目标账号。
- `op account list` 能看到 1Password 账号。
- `code --list-extensions` / `cursor --list-extensions` 与旧机清单大体一致。
- `~/Documents/Basic`、`~/Documents/Other`、`~/Documents/Codex` 的核心仓库可打开，当前重点仓库可跑 `git status`。
- Codex / OpenCode 能读取全局规则、skills 和项目 `AGENTS.md`。

## 已生成文件

- `adhoc_jobs/mac_migration_kit/README.md`
- `adhoc_jobs/mac_migration_kit/scripts/export_inventory.sh`
- `adhoc_jobs/mac_migration_kit/scripts/bootstrap_new_mac.sh`
- `adhoc_jobs/mac_migration_kit/scripts/clone_repositories.sh`
- `adhoc_jobs/mac_migration_kit/scripts/doctor_migration.sh`
- `adhoc_jobs/mac_migration_kit/scripts/backup_codex_environment.sh`
- `adhoc_jobs/mac_migration_kit/scripts/restore_codex_environment.sh`
- `adhoc_jobs/mac_migration_kit/manifests/Brewfile`
- `adhoc_jobs/mac_migration_kit/manifests/npm-global.txt`
- `adhoc_jobs/mac_migration_kit/manifests/vscode_extensions.txt`
- `adhoc_jobs/mac_migration_kit/manifests/cursor_extensions.txt`
- `adhoc_jobs/mac_migration_kit/manifests/applications.txt`
- `adhoc_jobs/mac_migration_kit/manifests/git_repositories.current.tsv`
