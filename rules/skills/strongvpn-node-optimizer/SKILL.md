---
name: strongvpn-node-optimizer
description: 在 macOS 上安全测试、比较和切换 StrongVPN WireGuard 节点。用户提到 StrongVPN 变慢、WireGuard 节点测速、选择最快 VPN、关闭其他 VPN 后切换、恢复上一个代理，或要求检查当前 StrongVPN 优选结果时使用。
---

# StrongVPN Node Optimizer

通过真实 AI 服务访问质量选择节点，不以单次 ping 代替实际体验。凭据只进入 macOS Keychain，配置只进入本机权限受控的数据目录；切换失败必须恢复原 VPN 状态。

## 命令入口

```bash
node scripts/strongvpn-node-optimizer.mjs status
node scripts/strongvpn-node-optimizer.mjs credentials set <StrongVPN用户名>
node scripts/strongvpn-node-optimizer.mjs benchmark --force
node scripts/strongvpn-node-optimizer.mjs benchmark
node scripts/strongvpn-node-optimizer.mjs switch best
node scripts/strongvpn-node-optimizer.mjs restore
```

从全局 skill 目录调用时，先定位本文件所在目录，再使用其中的 `scripts/strongvpn-node-optimizer.mjs`，不要复制脚本到临时目录。

## 工作流

### 首次设置

1. 运行 `status`，确认 `wg`、`wg-quick` 和凭据状态。
2. 缺少依赖时安装全局 Homebrew 公式：`brew install wireguard-tools`。
3. 凭据缺失时运行 `credentials set <用户名>`。密码必须由 `security` 的隐藏提示读取，禁止放入命令参数、环境变量、仓库文件或对话输出。
4. 运行 `benchmark --force` 做首次完整测试。

### 选择并切换最快节点

1. 普通切换先运行 `benchmark`；24 小时内有有效结果时复用缓存。
2. 用户明确要求重新测试、当前体验变慢或网络环境变化时运行 `benchmark --force`。
3. 脚本预检新加坡、日本、台湾、美西节点，最多对 6 个候选建立真实隧道。
4. 每个候选测试 OpenAI API、ChatGPT、Claude、GitHub、Gemini 和 Cloudflare 小文件，共 3 轮。
5. 只有三轮全部成功、核心服务可达、WireGuard 握手和 DNS 都正常的节点才有资格获选。
6. 成功后保持最佳隧道连接，原 VPN 保持关闭；失败时由事务回滚恢复切换前状态。

### 快速重连与恢复

- 已有合格排名且只需重连：运行 `switch best`。
- 新节点体验异常或需要回退：运行 `restore`，切回上一个成功配置。
- 每次操作后运行 `status`，并检查 `latest.winner`、测试时间和排名。

## 安全边界

- 不读取、打印或总结 Keychain 中的密码。
- 不打印 WireGuard private key、完整配置或本机公网 IP。
- 不把 `~/.local/share/strongvpn-node-optimizer` 纳入 Git、云同步或调研文档。
- 不降低 90% 成功率、三轮成功、核心服务、握手或 DNS 合格门槛来强行选出节点。
- macOS 管理员授权弹窗只能用于 `wg` / `wg-quick` 的隧道和路由操作；不要扩展到其他命令。
- 不创建常驻进程、LaunchAgent、cron 或自动后台切换任务。

## 数据位置

- Keychain service：`strongvpn-node-optimizer`
- 本机数据：`~/.local/share/strongvpn-node-optimizer`
- 当前配置：`configs/current.conf`
- 上一配置：`configs/previous.conf`
- 脱敏排名：`latest.json`

目录权限必须保持 `0700`，配置和结果文件保持 `0600`。只保留 current、previous 和 latest ranking。

## 故障处理

- `credentials are invalid`：重新运行 `credentials set`，不要从 Keychain 输出密码排查。
- `generator unavailable`：核对两个来源；服务器目录位于 `/share/strong-wg/servers.js`，生成接口位于站点根路径 `/wg-generate`。
- `No node passed`：保留失败结论，检查管理员授权、WireGuard 握手和核心服务连通性，不选择未合格节点。
- `rollback incomplete`：立即运行 `scutil --nc list` 与 `wg show` 检查真实状态，并明确告知用户哪些原 VPN 未恢复。
