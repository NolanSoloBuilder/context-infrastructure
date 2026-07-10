# Mac Migration Kit

目标：不用 macOS Migration Assistant，把当前开发环境拆成可审计、可重复执行的恢复流程。

这套 kit 的边界是工具链、App、AI 工具上下文、代码仓库和恢复检查。它不复制 Keychain、浏览器 session、SSH 私钥、`~/Library` 全量数据，也不把 secrets 写入仓库。

## 文件结构

- `scripts/export_inventory.sh`：在旧 Mac 上生成当前环境清单。
- `scripts/bootstrap_new_mac.sh`：在新 Mac 上按清单安装 Homebrew、Brewfile、npm global 包和编辑器扩展。
- `scripts/clone_repositories.sh`：在新 Mac 上按仓库 manifest dry-run 或 clone。
- `scripts/doctor_migration.sh`：在新 Mac 上检查恢复缺口。
- `scripts/backup_codex_environment.sh`：把筛选后的 Codex Skills、规则、MCP 配置、记忆和自动化打成私有迁移包。
- `scripts/restore_codex_environment.sh`：在新 Mac 上预览或恢复 Codex 私有迁移包。
- `manifests/`：可提交的声明式清单。
- `inventory/`：本机扫描产物，默认按时间戳生成。
- `prompts/`：按迁移层拆分、可直接交给新电脑 Codex 执行的 Prompt 与决策表。

分层执行入口：

- `prompts/01_system_toolchain_install.md`：第一层系统工具链的迁移决策表和安装 Prompt。
- `prompts/01b_oh_my_zsh_setup.md`：第一层完成后，重建干净 Oh My Zsh 配置的 Prompt。
- `prompts/02_codex_skills_migration.md`：Codex Skills 专项盘点、旧机导出和新机恢复 Prompt。
- `prompts/03_codex_environment_restore_from_repo.md`：让另一台 Codex 从当前 repo 内迁移包恢复 Codex 环境的 Prompt。
- `manifests/codex-skills-migrate.txt`：Codex Skills 干净迁移名单，包含实体 Skill、软链接和排除项。

## 旧 Mac 执行

```bash
cd /Users/xuhao/Documents/Other/context-infrastructure/adhoc_jobs/mac_migration_kit
./scripts/export_inventory.sh
```

扫描完成后，先 review `inventory/<timestamp>/RESTORE_NOTES.md`，再把需要长期维护的清单复制或整理到 `manifests/`。

退出 Codex App 和正在运行的 Codex CLI 后，再生成 Codex 私有迁移包：

```bash
./scripts/backup_codex_environment.sh
```

默认输出到 `~/Documents/CodexMigration/`，不进入 Git 仓库。归档包含：

- `~/.codex/config.toml`、全局 `AGENTS.md`、hooks 和 rules。
- 按 `manifests/codex-skills-migrate.txt` 精确筛选后的 `~/.codex/skills` 和 `~/.agents/skills`。
- `~/.codex/superpowers`、memories、memory sqlite、automations 和 Codex 可迁移配置。
- 本地 Claude/CodeWiz companion 配置。

归档明确排除 OpenCode、登录态、插件缓存、App 本地状态、附件、日志、生成媒体、shell snapshot、运行中的 SQLite WAL/SHM 文件、Lark Skills、官方插件重复 Skills 和手动排除的 handoff/plugin-installer Skills。确实需要保留本地历史会话时，可显式执行：

```bash
INCLUDE_HISTORY=1 ./scripts/backup_codex_environment.sh
```

该归档仍可能包含私有规则、记忆或 MCP 配置，只能放在加密存储中，不能提交到 Git。

## 新 Mac 执行

先把本仓库 clone 到新机器，再执行：

```bash
cd /Users/xuhao/Documents/Other/context-infrastructure/adhoc_jobs/mac_migration_kit
./scripts/bootstrap_new_mac.sh
./scripts/clone_repositories.sh
./scripts/restore_codex_environment.sh ~/Documents/CodexMigration/codex-environment-<timestamp>.tar.gz
./scripts/doctor_migration.sh
```

Codex 恢复脚本默认只预览。先安装并登录一次 Codex，然后完全退出 Codex App，再执行实际恢复：

```bash
DRY_RUN=0 ./scripts/restore_codex_environment.sh ~/Documents/CodexMigration/codex-environment-<timestamp>.tar.gz
```

恢复脚本会先把新机器上已有的目标文件备份到 `~/Documents/CodexMigration/pre-restore-<timestamp>/`。插件缓存不复制；Codex 重新打开后会根据 `config.toml` 中的插件启用状态重新同步。若新旧机器用户名不同，需要 review `~/.codex/config.toml` 中的旧绝对路径。

如果需要恢复 `xdevplatform/tap` 里的 cask，先确认来源可信，再设置：

```bash
ALLOW_UNTRUSTED_TAPS=1 ./scripts/bootstrap_new_mac.sh
```

`clone_repositories.sh` 默认只 dry-run。确认 manifest 后再执行：

```bash
DRY_RUN=0 ./scripts/clone_repositories.sh
```

## Secrets 恢复原则

secrets 的 source of truth 应该是 1Password、服务商控制台、GitHub/GitLab SSH key 配置、Google Cloud auth 或各 App 自己的登录流程。迁移脚本只做缺口检查，不读取、不复制、不提交 secrets。

需要手动恢复的典型项：

- `~/.ssh` 私钥：优先在新机器重新生成并添加到 GitHub/GitLab/GCP；确需迁移时走加密介质或 1Password document。
- `~/.codex/auth.json`、`~/.config/gcloud`、浏览器登录态：新机器重新登录。
- `.env`、`*.secrets.yaml`、`~/.npmrc` token：从 1Password 或对应平台重新写入。
