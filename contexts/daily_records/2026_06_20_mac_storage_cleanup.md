# 2026-06-20 Mac Storage Cleanup

## Context

使用 `storage-analyzer` skill 做了一次 macOS 存储清理分析。原始全量扫描在 `~/Library/Containers` 和 `~/Downloads` 上耗时过长，改为定向只读扫描：开发缓存、常见应用缓存、Xcode 缓存、应用数据目录和应用本体。

交互报告服务：

- `http://127.0.0.1:51148/`

报告文件：

- `/tmp/storage_analysis.json`
- `/Users/xuhao/Desktop/storage-report.html`

## Findings

绿灯可优先处理项，估算可释放约 `31.4 GB`：

- `~/Library/pnpm/store`：约 `13.9 GB`
- `~/Library/Developer/Xcode/iOS DeviceSupport`：约 `5.6 GB`
- `~/.npm/_cacache` + `~/.npm/_npx`：约 `3.0 GB`
- `~/Library/Caches/Google/Chrome`：约 `2.2 GB`
- `~/Library/Caches/CocoaPods`：约 `1.7 GB`
- `~/Library/Caches/Codex` + `~/.cache/codex-runtimes`：约 `3.0 GB`
- `~/Library/Caches/pnpm`、`ms-playwright`、`Homebrew`、`node-gyp`、`electron-builder`：约 `2.0 GB`

橙灯人工判断项：

- `~/Library/Application Support/Google`：约 `8.5 GB`，含 Chrome Profile 和站点数据，优先应用内清理。
- `~/Library/Developer/CoreSimulator`：约 `3.5 GB`，可能含模拟器状态，优先用 Xcode 或 `xcrun simctl delete unavailable`。
- `~/Library/Application Support/LarkShell`：约 `2.1 GB`，优先应用内清缓存。
- `~/Library/Application Support/Cursor`：约 `1.7 GB`，先检查缓存子目录和工作区状态。
- `~/Downloads` 与 `~/Library/Containers`：命令行扫描超时，建议用访达或 DaisyDisk 类工具交互式审查。

红灯谨慎项：

- `/Applications/Xcode.app`：约 `4.7 GB`
- `/Applications/IntelliJ IDEA.app`：约 `4.1 GB`

这些是应用本体，只有确认不用时才卸载。

## Next Priority

1. 先运行 `pnpm store prune`，再视情况从报告页移动 `~/Library/pnpm/store`。
2. 关闭 Xcode 后清理 `~/Library/Developer/Xcode/iOS DeviceSupport`。
3. 关闭 Chrome、Codex 和相关 dev server 后清理 npm/CocoaPods/Codex/Chrome/Playwright/Homebrew 缓存。
4. 用访达按大小排序检查 `~/Downloads`，用应用内入口处理 Chrome/Lark/Cursor 数据。
