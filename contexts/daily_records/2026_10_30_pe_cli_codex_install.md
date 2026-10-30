# PE CLI 与 Codex 接入

2026-10-30，用户授权在当前机器安装 PE CLI 并接入 Codex。

- 使用全局 npm 安装 `@xhs/pe@2.0.5`，公司 Artifactory registry；安装退出码 0。
- 安装器迁移到稳定入口 `/Users/xuhao/.pe/bin/pe`，内置 Node 24.15.0；`~/.zshrc` 已加入 PATH。
- `pe --version` 返回 2.0.5；`pe info` 成功识别 promotion-ark 为 Formula/Vue/TypeScript 前端项目。
- `codex plugin list --marketplace xhs-pe --json` 确认 `pe@xhs-pe` 2.0.5 installed=true、enabled=true。
- 新启动的 Codex app-server 经 initialize 与 skills/list(forceReload) 返回 34 个启用的 PE 技能，来源为 `~/.codex/plugins/cache/xhs-pe/pe/2.0.5`，errors 为空。仅做运行时技能发现，没有启动模型任务；旧聊天技能上下文没有热加载证明。
- `pe doctor` 为 warning：PE 内容验证通过、activation=pending；内部 xhs-git-ai 未找到，org-spec 有 16 个待信任 hooks。
- 安装器自动同步 Claude/CodeWiz/Cursor 并附带安装 org-spec、Git-AI、更新服务。配套 org-spec DataHub Worker 缺依赖，Claude 缓存解析失败；Git-AI 安装遇到 `.bash_profile` 权限错误；第二轮同步还遇到公司 Git 域名 DNS 失败。未把这些附带组件报告为成功，也未重启其他聊天或扩大修复。
- 业务系统认证与真实 APM/部署调用未验证。

## 冗余安装清理

用户随后要求清理旧 PE。未发现历史旧版本或重复 Codex PE 插件；发现本次 npm 安装迁移后同时保留全局 bootstrap 包与受管 2.0.5。用 `npm uninstall -g @xhs/pe --ignore-scripts` 删除冗余全局包，再将 `/opt/homebrew/bin/pe` 链接至 `/Users/xuhao/.pe/bin/pe`，保留当前终端全局入口。受管 CLI、运行时、更新服务和插件均保留。回读版本 2.0.5，`pe info` 成功，Codex 插件仍 installed/enabled。

## 用户要求清除钩子

- 使用 Git-AI 官方 `uninstall-hooks` 移除安装器写入各 Agent 的 Git-AI hooks。注意该 CLI 的 `uninstall-hooks --help` 也会直接执行卸载，并非只显示帮助。
- 通过 Codex app-server `hooks/list` 精确发现 org-spec 插件的 16 个 hooks，通过 `config/value/write` 将各 hook 的 `enabled` 设为 false；未更改插件缓存内容，PE/org-spec 技能保留。
- 用 `pe daemon disable` 停止并禁用自动更新/同步服务，防止后台重装 hooks；稳定入口及 CLI 保留。
- 新 Codex app-server 回读 hooks：16 个定义、启用 0；Git-AI Codex hook 定义已不存在。PE 2.0.5 插件仍 installed/enabled。
- 配置修改前备份：`~/.codex/config.toml.before-pe-hook-disable-20261030`（Git-AI 卸载后、org-spec hook 禁用前）。当前旧聊天 UI 可能需要刷新或新开聊天。
