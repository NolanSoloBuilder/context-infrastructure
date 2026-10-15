---
name: strongvpn-node-optimizer
description: 通过 StrongVPN 接口下载 WireGuard 配置、转换并更新 Clash/VPS 私人订阅，或在 macOS 上测试、比较和切换节点。用于下载节点、更新 StrongVPN 订阅、提取 strong-wg 接口、测速、切换或恢复节点。
---

# StrongVPN Node Optimizer

根据用户目标选择下载或测速流程。下载直接调用官方页面使用的接口；测速通过真实 AI 服务访问质量选择节点。持久化凭据只进入 macOS Keychain，配置进入本机权限受控的目录；REDpass 是受保护的基础网络，测速和切换不得关闭它，其他切换失败时恢复原 VPN 状态。

## 命令入口

```bash
node scripts/strongvpn-node-optimizer.mjs servers 日本
node scripts/strongvpn-node-optimizer.mjs download str-nrt301
node scripts/strongvpn-node-optimizer.mjs status
node scripts/strongvpn-node-optimizer.mjs credentials set <StrongVPN用户名>
node scripts/strongvpn-node-optimizer.mjs benchmark --force
node scripts/strongvpn-node-optimizer.mjs benchmark
node scripts/strongvpn-node-optimizer.mjs switch best
node scripts/strongvpn-node-optimizer.mjs restore
```

从全局 skill 目录调用时，先定位本文件所在目录，再使用其中的 `scripts/strongvpn-node-optimizer.mjs`，不要复制脚本到临时目录。

## 工作流

### 统一订阅完整更新

用户说“更新 StrongVPN 订阅”“重新下载节点并更新订阅”，或要求 WireGuard → Clash YAML → VPS 发布时，先读[完整订阅工作流](references/subscription_workflow.md)。当前用户选择一份包含全部保留节点的共用订阅，不拆四份；正常发布保留原 URL，只原子替换服务器文件。只说“更新”默认复用配置，明确“重新下载”才注册新密钥；没有 `publish/convert/update-subscription` 现成子命令，不要混用会生成并切网的 `benchmark`。

### 查看和下载节点文件

1. 运行 `servers 日本` 或 `servers japan` 获取实时节点列表；省略筛选词会列出全部节点。支持 `--json`。
2. 运行 `download <节点ID>`，复用 Keychain 凭据。可带 `--username <用户名>` 核对账号，避免误用已有账号。
3. 输出下载文件的绝对路径，默认位于本机数据目录的 `downloads/`，文件权限 `0600`，不会输出配置正文或私钥。
4. 需要指定目标时用 `--output /绝对路径/节点.conf`，父目录须存在；现有文件不覆盖。`--source strongvpn|strongtech` 可指定来源。目录 GET 可自动备用，生成 POST 每次只发送一次，失败或超时停止。

纯下载只依赖 Node.js 20+ 的内置模块，无需浏览器、`wg`、管理员授权。下载流程不运行测速，不导入或连接 VPN，不修改本地 `current` / `previous` 配置。生成操作会在服务端登记新公钥；公开页面未说明这是否影响已有服务端公钥关联，不承诺既有远端配置一定不受影响。

每次 `download` 都是重新生成密钥和配置。优先复用已有文件；批量或重复生成前先核对提供方保留政策。官方标准 WireGuard FAQ 记载超过 12 份淘汰最旧配置，但该规则对 AIO 专用入口的适用性尚未确认，不能断言 AIO 全量导出仍全部有效或只剩最后 12 份。证据与范围见 [下载接口契约](references/download_api.md)。

若只想单次使用密码，可用 `--username <用户名> --password-stdin` 从管道传入一行密码；不保存该密码。交互式 zsh 示例：

```zsh
read -r -s 'strongvpn_password?StrongVPN 密码：'
print
print -r -- "$strongvpn_password" | node scripts/strongvpn-node-optimizer.mjs download str-nrt301 --username <用户名> --password-stdin
unset strongvpn_password
```

密码不放进命令参数、环境变量、文件或日志；Agent 传入密码时只能使用无回显的标准输入，不把密码展开到 shell 命令文本中。若需接口字段与构造规则，读取 [下载接口契约](references/download_api.md)。

### 验证已经导出的配置

用户要求验证现有 `.conf`，尤其明确禁止重新生成时，不运行 `download` 或 `benchmark`，两者都会创建新密钥并调用生成接口。只读取既有文件；优先通过现有 Mihomo WireGuard 出站或用户态客户端发送定向测试流量，保留系统路由和 REDpass，不开启系统代理或 TUN。

HTTPS 成功可以证明该配置在测试时能够完成加密通信并转发流量；超时只记录为本次未验证，不能直接证明配置已过期。保存逐节点结果和原文件哈希，勿保存私钥或完整配置到日志。2026-10-15 的 AIO 实测中，47 份旧配置的最后 12 份通过两个 HTTPS 目标，较早 35 份超时；这是特定账户和时点的证据，不作为跨账户固定规则。

### 测速工具首次设置

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
6. REDpass 全程保持运行，在其上叠加候选 StrongVPN 隧道；成功后保持最佳隧道连接，失败时由事务回滚恢复切换前状态。

### 快速重连与恢复

- 已有合格排名且只需重连：运行 `switch best`。
- 新节点体验异常或需要回退：运行 `restore`，切回上一个成功配置。
- 每次操作后运行 `status`，并检查 `latest.winner`、测试时间和排名。

## 安全边界

- 不读取、打印或总结 Keychain 中的密码。
- 不停止、退出、强杀或重启 REDpass；它是当前网络的受保护底座。
- 不打印 WireGuard private key、完整配置或本机公网 IP。
- 不把 `~/.local/share/strongvpn-node-optimizer` 或下载的 `.conf` 纳入 Git、云同步或调研文档。
- 不降低 90% 成功率、三轮成功、核心服务、握手或 DNS 合格门槛来强行选出节点。
- macOS 管理员授权弹窗只能用于 `wg` / `wg-quick` 的隧道和路由操作；不要扩展到其他命令。
- 不创建常驻进程、LaunchAgent、cron 或自动后台切换任务。

## 数据位置

- Keychain service：`strongvpn-node-optimizer`
- 本机数据：`~/.local/share/strongvpn-node-optimizer`
- 当前配置：`configs/current.conf`
- 上一配置：`configs/previous.conf`
- 脱敏排名：`latest.json`
- 下载文件：`downloads/<节点ID>-<时间>.conf`（独立保存，保留私钥；不覆盖已有文件）

默认数据目录权限保持 `0700`，配置和结果文件保持 `0600`。测速状态只保留 current、previous 和 latest ranking；独立下载文件由用户按需保留。

## 故障处理

- `credentials are invalid`：重新运行 `credentials set`，不要从 Keychain 输出密码排查。
- `generator unavailable`：核对两个来源；服务器目录位于 `/share/strong-wg/servers.js`，生成接口位于站点根路径 `/wg-generate`。
- `No node passed`：保留失败结论，检查管理员授权、WireGuard 握手和核心服务连通性，不选择未合格节点。
- `rollback incomplete`：立即运行 `scutil --nc list` 与 `wg show` 检查真实状态，并明确告知用户哪些原 VPN 未恢复。
