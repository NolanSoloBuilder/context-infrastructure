# MCP 禁用复查

2026-10-15 用户询问当前状态。只读检查发现生信进程重新出现：NGS 三类共 74 个，Rosalind/sequence/structure/slide 共 92 个，共 166 个快照实例。Creem 与 OpenClaw 未发现运行进程。CPU 约 99.5%，Swap 约 21.3 GiB。RSS 受压缩与 swap 影响，不代表完整内存占用。

纠正上轮结论：上轮 config.toml 将生信插件写到 @openai-curated，但 codex plugin list --json 确认实际来自 @openai-curated-remote；改为真实标识后，CLI 仍显示远端插件 enabled=true，所以本地 plugin.enabled=false 仍不能作为成功禁用证据。Creem 普通 MCP enabled=false 有效。

未尝试重启 Codex，未结束浏览器/开发任务。按已有用户授权清理生信工具进程：{'sequence-viewer': 16, 'ngs-analysis-workbench': 71, 'structure-viewer': 24, 'rosalind': 24, 'slide-viewer': 24}。远端持久停用仍待确认；已询问是否卸载对应 7 个插件。安装文件之外的工作区数据不在清理范围。

## 卸载与重复实例诊断

用户明确授权卸载生信插件、独立 Codex CLI 和 Warp。

- 插件管理连接器用名称卸载返回 not_installed，与本机 CLI 的远端安装真源不一致；改用客户端内置 codex plugin remove <name>@openai-curated-remote --json，7 项全部退出码 0。再次 plugin list --json 未发现 7 个生信插件。
- 使用对应 prefix 的 npm uninstall --global --ignore-scripts 卸载 4 份 @openai/codex：/opt/homebrew、~/.nvm/versions/node/v22.22.0、fnm v20.19.4、fnm v18.20.1。全部退出码 0，package.json 均不存在。客户端内置 Codex 二进制保留，当前运行中的 Codex 进程来自客户端目录。
- 本轮首次检查 Warp.app 在 /Applications，执行应用移入废纸篓步骤时已不存在；最终两个 Applications 目录及废纸篓均无 Warp。没有足够证据将 Warp 的实际移除归因于本轮脚本，未删除其用户数据。
- 客户端在本轮前后换成新主进程 PID 1297；旧主进程 49580 已不存在。当前有 3 个 active 聊天，对 codex-app-tools 与 codex-security 的进程各采样到 3 份，均由同一个客户端 app-server 管理；生信插件进程不再存在。
- 证据支持同一客户端对多个聊天各自创建 MCP 实例的解释；独立 CLI 的多个磁盘安装本身不能解释旧主进程下 25 份 MCP。旧进程曾累积大量实例，但尚未完成逐线程生命周期映射，不能断言已证实泄漏或某个客户端 bug。
