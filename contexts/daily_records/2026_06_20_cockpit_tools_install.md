# 2026-06-20 Cockpit Tools 本机安装记录

## 结论

`Cockpit Tools` 已安装到 `/Applications/Cockpit Tools.app`，版本 `0.26.5`。旧的同名 app bundle 已移到废纸篓，命名形如 `Cockpit Tools.app.broken-<timestamp>`。这次安装不是 Homebrew-managed cask；失败的临时 tap 已清理。

## 现象

旧 bundle 带有 `com.apple.quarantine` 属性，`spctl --assess --type execute` 还报：

```text
code has no resources but signature indicates they must be present
```

这说明问题不只是 macOS quarantine，bundle 本体也可能不完整。

## 安装路径

官方 README 推荐：

```bash
brew tap jlcodes99/cockpit-tools https://github.com/jlcodes99/cockpit-tools
brew install --cask cockpit-tools
```

但当前本机的 Homebrew `6.0.2` 已不接受 README 中的 `--no-quarantine` 参数。官方 cask 的 `postflight` 还会强制执行：

```bash
sudo xattr -cr "/Applications/Cockpit Tools.app"
```

在 Codex 非交互环境里无法输入 sudo 密码，因此 cask 安装会回滚。

当前采用的可复用路径：

```bash
curl -L -o SHA256SUMS.txt https://github.com/jlcodes99/cockpit-tools/releases/download/v0.26.5/SHA256SUMS.txt
curl -L -o Cockpit.Tools_universal.app.tar.gz https://github.com/jlcodes99/cockpit-tools/releases/download/v0.26.5/Cockpit.Tools_universal.app.tar.gz
shasum -a 256 Cockpit.Tools_universal.app.tar.gz
tar -xzf Cockpit.Tools_universal.app.tar.gz
xattr -cr "Cockpit Tools.app"
ditto "Cockpit Tools.app" "/Applications/Cockpit Tools.app"
xattr -cr "/Applications/Cockpit Tools.app"
open "/Applications/Cockpit Tools.app"
```

验证点：

- `defaults read "/Applications/Cockpit Tools.app/Contents/Info" CFBundleShortVersionString` 返回 `0.26.5`
- `xattr -lr "/Applications/Cockpit Tools.app"` 不再出现 `com.apple.quarantine`
- `open "/Applications/Cockpit Tools.app"` 后能看到 `/Applications/Cockpit Tools.app/Contents/MacOS/cockpit-tools` 进程

## Codex 多实例历史清理

本机当前有一个默认 Codex 实例和一个 Cockpit 自建实例 `Rimbo`。默认实例使用 `/Users/xuhao/.codex`，`Rimbo` 使用：

```text
/Users/xuhao/.antigravity_cockpit/instances/codex/8911c39b188fd6d2
```

`Rimbo` 初始化时继承了默认实例的旧会话历史，因此旧对话列表看起来和默认实例一致。清理时不要动 `/Users/xuhao/.codex`，只处理 `Rimbo` 的实例目录。

这次采用非破坏性移动：保留仍被当前 app-server 写入的活动会话文件，其余旧历史先移到：

```text
/Users/xuhao/.antigravity_cockpit/backups/codex_rimbo_history_20260620-214347
```

随后按用户确认，该备份目录已删除。

清理后计数：

- 默认实例历史：`682`
- `Rimbo` 剩余历史：`1`（当前活动会话）
- 已删除备份中的旧历史：`682`

## macOS 文稿权限反复弹窗

现象：即使系统设置里已经给了 `Cockpit Tools` 访问权限，macOS 仍反复弹出：

```text
"Cockpit Tools" 想访问 "文稿" 文件夹中的文件。
```

原因：手动安装的 upstream app bundle 只有 ad-hoc/linker 签名，最初 `codesign` 显示：

```text
Identifier=cockpit_tools-8d9a6397575f5cd4
Info.plist=not bound
Sealed Resources=none
```

这会让 macOS TCC 权限记录和实际 app 身份不稳定。

处理：

```bash
osascript -e 'quit app "Cockpit Tools"'
codesign --force --deep --sign - "/Applications/Cockpit Tools.app"
tccutil reset SystemPolicyDocumentsFolder com.jlcodes.cockpit-tools
open "/Applications/Cockpit Tools.app"
```

处理后 `codesign` 显示：

```text
Identifier=com.jlcodes.cockpit-tools
Info.plist entries=15
Sealed Resources version=2
```

`spctl` 仍会拒绝，因为这是本地 ad-hoc 签名，不是 Apple Developer ID 公证签名；但 TCC 识别身份已经稳定。

## macOS App Data 权限反复弹窗

后续又出现新的 macOS 权限弹窗：

```text
"Cockpit Tools" 想访问其他 App 的数据。
```

这不是前面的 `SystemPolicyDocumentsFolder`，而是 `SystemPolicyAppData`。检查后发现两个触发因素：

- `Cockpit Tools` 会启动并管理 Codex App，使用自定义 Electron app data 路径：`/Users/xuhao/.antigravity_cockpit/instances/codex-app-data/<id>`。
- 内置辅助程序 `Contents/MacOS/cockpit-cliproxy` 最初是裸 Mach-O ad-hoc 签名，identifier 形如 `cockpit-cliproxy-<hash>`，没有稳定 bundle identity。

处理步骤：

```bash
pkill -f "/Applications/Cockpit Tools.app/Contents/MacOS/cockpit-tools" || true
codesign --force --sign - --identifier com.jlcodes.cockpit-tools.cliproxy "/Applications/Cockpit Tools.app/Contents/MacOS/cockpit-cliproxy"
codesign --force --sign - "/Applications/Cockpit Tools.app"
tccutil reset SystemPolicyAppData com.jlcodes.cockpit-tools
```

同时为了止住循环弹窗，做了可回滚的配置隔离：

- 备份 `~/.antigravity_cockpit/config.json` 到 `config.json.bak_before_appdata_popup_20260620_*`。
- 将 `auto_refresh_minutes` 和各平台 `*_auto_refresh_minutes` 临时设为 `0`。
- 关闭 `auto_backup_enabled`、`webdav_sync_enabled`、`codex_launch_on_switch`、`ghcp_launch_on_switch`。
- 备份 `~/.antigravity_cockpit/codex_instances.json` 到 `codex_instances.json.bak_before_appdata_popup_20260620_*`。
- 临时清空 `codex_instances.json` 里的 `instances`，并把 `defaultSettings.bindAccountId`、`defaultSettings.lastPid` 置空，`launchMode` 改为 `cli`。

验证：

- 重启后 `Cockpit Tools` 进程存在。
- 20 秒内 `lsof -p <cockpit_pid>` 只显示自己的日志文件和系统资源，没有再持有 Codex/Cursor/Windsurf/Gemini 等 app data 文件。
- 日志里没有新的 `Codex Start`，也没有新的高频 `Codex Instances` 轮询写入。

恢复方式：

```bash
cp ~/.antigravity_cockpit/config.json.bak_before_appdata_popup_20260620_<time> ~/.antigravity_cockpit/config.json
cp ~/.antigravity_cockpit/codex_instances.json.bak_before_appdata_popup_20260620_<time> ~/.antigravity_cockpit/codex_instances.json
open "/Applications/Cockpit Tools.app"
```

2026-06-21 07:53 已按用户要求恢复 Cockpit 对 Codex instance 的管理能力。恢复前先备份了临时降噪配置：

```text
~/.antigravity_cockpit/config.json.bak_disabled_before_restore_20260621_075312
~/.antigravity_cockpit/codex_instances.json.bak_disabled_before_restore_20260621_075312
```

随后恢复：

```text
~/.antigravity_cockpit/config.json.bak_before_appdata_popup_20260620_224929 -> ~/.antigravity_cockpit/config.json
~/.antigravity_cockpit/codex_instances.json.bak_before_appdata_popup_20260620_230115 -> ~/.antigravity_cockpit/codex_instances.json
```

验证点：

- `auto_refresh_minutes=10`
- `codex_auto_refresh_minutes=10`
- `codex_launch_on_switch=true`
- `codex_instances.json` 中恢复 1 个 instance：`Rimbo`，`launchMode=app`，`userDataDir=/Users/xuhao/.antigravity_cockpit/instances/codex/8911c39b188fd6d2`
- `open "/Applications/Cockpit Tools.app"` 后 `cockpit-tools` 进程已启动。
