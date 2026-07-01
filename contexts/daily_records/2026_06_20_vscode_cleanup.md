# 2026-06-20 VS Code 清理记录

## 背景

VS Code 出现卡顿，怀疑扩展和缓存积累过多。诊断范围包括 `~/.vscode/extensions`、`~/Library/Application Support/Code`、VS Code `workspaceStorage` 和当前 extension host 进程。

## 诊断结论

- `~/.vscode/extensions` 原始占用约 `4.1G`，存在多组旧版本扩展目录。
- 大头来自 `openai.chatgpt`、`rednote.rednote-codewiz`、`anthropic.claude-code`、`typescriptteam.native-preview` 的旧版本残留。
- `~/Library/Application Support/Code/User/workspaceStorage` 原始占用约 `440M`，其中约 `201M` 指向已经不存在的项目目录。
- 当时还看到从旧扩展目录启动的 extension host 进程，说明 VS Code 更新后没有完整重启。

## 已执行清理

移动到废纸篓的内容约 `2.9G`，包括：

- 旧版 `openai.chatgpt` 扩展目录，保留 `openai.chatgpt-26.616.41845-darwin-arm64`。
- 旧版 `rednote.rednote-codewiz-1.10.4`，保留 `rednote.rednote-codewiz-1.10.5`。
- 旧版 `anthropic.claude-code-2.1.145-darwin-arm64`，保留 `anthropic.claude-code-2.1.183-darwin-arm64`。
- 旧版 `typescriptteam.native-preview`，保留 `typescriptteam.native-preview-0.20260620.1-darwin-arm64`。
- VS Code `CachedExtensionVSIXs`、`Crashpad`、`logs`、`CachedData`、`Cache`、`GPUCache` 等可再生缓存。
- 指向缺失项目路径的 VS Code `workspaceStorage`。

## 清理后状态

- `~/.vscode/extensions` 降到约 `1.7G`。
- `~/Library/Application Support/Code` 降到约 `450M`。
- 缺失项目的 `workspaceStorage` 降到 `0`。
- `code --list-extensions --show-versions` 显示当前默认 profile 仍有 42 个扩展。
- 复查时没有发现长期驻留的 VS Code / extension host 进程。

## 下次复查命令

```bash
du -sh "$HOME/.vscode" "$HOME/.vscode/extensions" "$HOME/Library/Application Support/Code" "$HOME/Library/Application Support/Code/User/workspaceStorage" 2>/dev/null
du -sh "$HOME/.vscode/extensions"/* 2>/dev/null | sort -hr | head -50
code --list-extensions --show-versions | sort
pgrep -fl 'Visual Studio Code|Code Helper|\\.vscode/extensions|codex app-server|codewiz-ls|rednote-codewiz' || true
```
