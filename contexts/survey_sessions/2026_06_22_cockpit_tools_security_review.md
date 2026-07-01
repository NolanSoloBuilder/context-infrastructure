# Cockpit Tools 安全初查

调查时间：2026-06-22  
对象：`/Applications/Cockpit Tools.app`  
Bundle ID：`com.jlcodes.cockpit-tools`  
版本：`0.26.5`  
源码：`https://github.com/jlcodes99/cockpit-tools`  
本次源码快照：`d5ad5cea22d647453f6d8eea88676a6480bffc63`

## 结论

没有在源码和当前运行态里发现典型恶意行为证据，例如隐藏 C2、定期外传本地文件、任意远程命令执行、混淆 payload、强制持久化启动项、键盘监听等。

但它不是低风险工具。它本质上是一个 AI IDE 账号、token、本地网关和备份管理器，默认安全边界偏宽；在当前版本里，最值得关注的是本地 WebSocket 无认证导出 token、明文自动备份默认开启、发布包缺少 Developer ID 签名/公证。

## 本机证据

- 已安装 App 为 `/Applications/Cockpit Tools.app`，bundle id 为 `com.jlcodes.cockpit-tools`。
- `codesign` 显示 `Signature=adhoc`、`TeamIdentifier=not set`；`spctl --assess` 返回 rejected。该结果说明它不具备 Apple Developer ID 公证信任链，不等于恶意，但会放大 macOS TCC 权限身份不稳定的问题。
- 当前运行进程只看到 `cockpit-tools` 监听 `TCP *:19528 (LISTEN)`，未看到当前保持中的对外 TCP 连接。
- 本机配置中：
  - `ws_enabled=true`
  - `ws_port=19528`
  - `auto_backup_enabled=true`
  - `auto_backup_include_accounts=true`
  - `auto_backup_include_config=true`
  - `webdav_sync_enabled=true`
  - `webdav_sync_username=""`
  - `webdav_sync_password=""`
  - `report_enabled=false`
- `~/.antigravity_cockpit/backups/` 下存在 `cockpit_auto_backup_full_*.json/.zip`，权限为普通用户可读写、同组/其他可读；内容按源码逻辑会包含账号导出的敏感数据。

## 源码发现

### 1. WebSocket 默认可导出 token

`src-tauri/src/modules/websocket.rs` 中定义了 `request.get_accounts_with_tokens`，响应 `response.accounts_with_tokens` 会返回账号列表及 `refresh_token`、`access_token`、`project_id` 等字段。

服务启动时实际绑定 `0.0.0.0:{port}`，日志显示为 `127.0.0.1`。连接接入后会通过 `is_allowed_remote_client` 过滤非本机来源；这能挡住局域网客户端，但仍意味着本机任意进程无需认证即可连接 `127.0.0.1:19528` 请求 token。

同时 `src-tauri/src/lib.rs` 在启动时无条件调用 `modules::websocket::start_server().await`。源码里没有看到启动前检查 `ws_enabled` 的逻辑，因此“设置里关闭 WebSocket”未必能阻止下次启动监听，需要实测验证。

### 2. 自动备份默认包含账号

`src-tauri/src/modules/config.rs` 默认：

- `default_auto_backup_enabled() -> true`
- `default_auto_backup_include_accounts() -> true`
- `default_auto_backup_include_config() -> true`
- `default_webdav_sync_enabled() -> true`

`src/services/scheduledBackupService.ts` 每次自动备份会调用 `exportDataTransferJson` 写本地备份；若 WebDAV 配置了用户名和密码，会再上传 zip。当前本机 WebDAV 没有凭据，因此未看到具备上传条件。

### 3. 远程配置和公告不是任意代码执行

`src-tauri/src/modules/remote_config.rs` 每小时从 GitHub raw 拉 `remote-config.json`，字段主要用于隐藏平台入口。

公告中心支持 `tab`、`url`、`command` action，但 `command` 只走前端白名单：`update.check`、`announcement.forceRefresh`、`page.navigate`。本次没有看到通过公告执行任意 shell 命令的路径。

### 4. 发布和更新信任链较弱

Tauri updater 使用 GitHub release `latest.json` 和 minisign 公钥。Homebrew cask 指向 GitHub release DMG，并在 postflight 中执行 `xattr -cr` 移除 quarantine。发布包当前不是 Developer ID 签名/公证产物。

### 5. 第三方 API 中转站较多

源码预置了多个 Codex/Claude provider preset 和赞助链接，例如 `chongcodex.cn`、`apikey.fun`、`packyapi`、`cubence`、`sssaicode`、`dmxapi.cn` 等。它们只有在用户选择或配置对应 provider 时才会成为请求目标，但这类功能会把 API 请求和 key 暴露给对应第三方。

## 频繁请求权限的解释

比较合理的解释是功能需求和签名问题叠加：

- 它需要管理多个 AI IDE/CLI 的账号、实例、配置、应用数据目录，因此会访问 `~/Library/Application Support`、`~/.codex`、`~/.gemini`、`~/.antigravity_cockpit`、项目目录等。
- 发布包是 ad-hoc 签名且未公证，macOS TCC 对这种 app 的身份稳定性较差，升级、重签、移动 app 后可能反复请求权限。
- 源码中存在一些“避免 macOS TCC 弹窗”的实现注释，说明开发者知道这个问题，并做过局部规避。

## 建议

如果只是偶尔管理账号，不建议让它长期高权限常驻。优先做：

1. 关闭或退出 Cockpit Tools，并确认 `19528` 不再监听。
2. 关闭自动备份，或至少关闭“包含账号”；清理已有 `cockpit_auto_backup_full_*.json/.zip`，或者移到加密存储。
3. 收紧 `~/.antigravity_cockpit` 权限为仅当前用户可读写。
4. 不使用不信任的第三方 provider preset；API key 只放官方或自己完全信任的服务。
5. 给 upstream 提 issue：WebSocket 应绑定 `127.0.0.1`、尊重 `ws_enabled`、加入随机认证 token 或改用权限受控的 Unix socket；账号和备份文件应使用 `0600/0700`；敏感备份应默认关闭或加密；macOS 发布应使用 Developer ID 签名和 notarization。

