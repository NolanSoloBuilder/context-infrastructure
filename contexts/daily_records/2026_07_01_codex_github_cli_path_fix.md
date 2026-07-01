# 2026-07-01 Codex GitHub CLI PATH 修复

## 现象

Codex 显示 GitHub CLI 不可用，但登录 shell 中 `gh` 正常：

- `gh --version`：`2.92.0`
- `gh auth status -h github.com`：已登录 `WebXuHao`
- `gh repo view`：可解析当前仓库

## 原因

Codex app-server 进程的 PATH 只有：

```text
/Users/xuhao/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin:/usr/bin:/bin:/usr/sbin:/sbin:/Applications/Codex.app/Contents/Resources
```

这里不包含 `~/.local/bin` 或 `/opt/homebrew/bin`，所以 GUI 进程环境里可能找不到 `gh`。Shell 可用不代表 Codex app-server 可用。

## 修复

把现有 `gh` 暴露到 Codex runtime 已经包含的 `dependencies/bin`：

```sh
ln -s /Users/xuhao/.local/bin/gh /Users/xuhao/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/gh
```

同时设置当前用户 GUI app 的启动 PATH，供后续 Codex 重启后使用：

```sh
launchctl setenv PATH /Users/xuhao/.local/bin:/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
```

## 验证

用 Codex app-server 的原始 PATH 模拟检测：

```sh
PATH=/Users/xuhao/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin:/usr/bin:/bin:/usr/sbin:/sbin:/Applications/Codex.app/Contents/Resources command -v gh
PATH=/Users/xuhao/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin:/usr/bin:/bin:/usr/sbin:/sbin:/Applications/Codex.app/Contents/Resources gh --version
PATH=/Users/xuhao/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin:/usr/bin:/bin:/usr/sbin:/sbin:/Applications/Codex.app/Contents/Resources gh auth status -h github.com
```

三项均通过。

如果 Codex UI 仍显示旧状态，通常是检测结果被当前进程缓存。重启 Codex 后应读取新的 GUI PATH；当前进程也可以通过 runtime symlink 找到 `gh`。
