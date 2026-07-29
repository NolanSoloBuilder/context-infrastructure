# Codex Desktop 误报 GitHub CLI 未安装诊断

日期：2026-07-13（2026-07-15 补充持久化修复）

## 现象

Codex Desktop 页面提示 `GitHub CLI (gh) is not installed`，但任务终端中可以正常执行 `gh`。

## 结论

`gh` 已正确安装并完成 GitHub 认证。误报来自 Codex Desktop 的 GitHub 集成直接启动 `gh` 时使用 App Server 进程的 `PATH`，其中缺少用户级 CLI 目录。任务终端会读取 zsh 启动文件并补齐这些目录，因此同一个 App 中出现两种不同结果。

## 证据

- `command -v gh` 返回 `/Users/xuhao/.local/bin/gh`。
- `/Users/xuhao/.local/bin/gh` 指向本地安装的 `gh 2.92.0`；Homebrew 同时提供 `/opt/homebrew/bin/gh`，版本相同。
- `gh auth status` 显示 GitHub 账户已登录，Git 协议为 SSH。
- Codex Desktop 版本为 `26.707.61608`。
- GUI 主进程的 `PATH` 是 `/usr/bin:/bin:/usr/sbin:/sbin`。
- Codex App Server 进程的 `PATH` 只包含 Codex 自带 runtime 目录和系统目录，没有 `~/.local/bin`、`/opt/homebrew/bin` 或 `/usr/local/bin`。
- App bundle 中的检测逻辑会直接启动 `gh --version`；执行失败后把状态映射为 `GitHub CLI (gh) is not installed`。这条路径不会启动 login shell，也不会读取 `.zshenv`、`.zprofile` 或 `.zshrc`。
- 使用 App Server 的原始 `PATH` 直接执行 `gh --version`，结果为 `exit 127`；加入 `~/.local/bin:/opt/homebrew/bin` 后立即成功。

## 本机环境差异

用户 shell 已在以下文件中配置 CLI 路径：

- `~/.zshenv`：加入 `~/.local/bin`、`/opt/homebrew/bin` 等目录。
- `~/.zprofile`：执行 Homebrew `shellenv` 并加入 `~/.local/bin`。
- `~/.zshrc`：再次加入 `~/.local/bin`。

这些配置能保证任务终端找到 `gh`，无法改变已经由 macOS GUI 会话启动的 Codex 主进程环境。

## 处理建议

优先把 `~/.local/bin:/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin` 注入当前用户的 GUI launchd 环境，然后完整退出并重新打开 Codex Desktop。这样可以同时覆盖本地独立安装和 Homebrew 安装。

这项修改会影响之后启动的所有 GUI 应用。单纯重装 `gh` 或继续修改 zsh 启动文件无法解决这条检测路径。

## 2026-07-15 复发与持久化修复

复发时再次确认：shell 中 `gh 2.92.0` 正常，Codex GUI 进程仍只有 `/usr/bin:/bin:/usr/sbin:/sbin`，同时 `launchctl getenv PATH` 为空。说明 7 月 13 日执行的 `launchctl setenv PATH ...` 只修复了当次登录会话，重新登录或重启后不会保留。

已新增用户级 LaunchAgent：`~/Library/LaunchAgents/com.xuhao.gui-path.plist`。它在每次图形登录时执行一次 `launchctl setenv PATH ...`，持久补齐 `~/.local/bin`、Homebrew 和系统 CLI 目录；无需管理员权限，也不修改 Codex App 包。安装后通过 `launchctl bootstrap gui/$(id -u) ...` 立即加载，之后仍需完整退出并重开 Codex，让新进程继承修复后的环境。
