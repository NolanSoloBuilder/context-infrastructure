# macOS 三屏 Dock 固定到中间屏幕

用户要求：当前三个屏幕同时连接时，底部 Dock 固定在中间屏幕，避免随鼠标换屏。

## 已执行

本机系统为 macOS 27.0，build `26A5425a`。屏幕排列从左到右为内置屏、横向 U27P10、竖向 U27P10。中间横向屏本来就是主屏，因此保留显示器排列和主屏选择。

修改前导出 Dock 偏好，备份及本机检查脚本保存在 `/Users/xuhao/.local/state/macos-dock-lock/20261010/`，完整偏好不写入仓库。

应用并重启 Dock：

```sh
defaults write com.apple.dock allow-display-switching -bool false
killall Dock
```

保留 `orientation=bottom`、`autohide=false`、`com.apple.spaces spans-displays=false`，即三个显示器继续各有独立 Spaces。无需注销，也没有安装后台守护程序。

## 验证与实现依据

本机 Dock 二进制读取 `com.apple.dock` 域的 `allow-display-switching`，将其作为 `allowDockDisplaySwitching`。值为 `false` 时，`DockBar.updateDigTrackingRects(deferred:)` 跳过跨屏底边触发区域计算。该设置来自本机实现核查，并非 Apple 公开支持的界面选项。

读回偏好为 `false`，两次重启 Dock 后均读取到中间主屏底部的 Dock。最终 Accessibility `AXList` 位置为 `(471, 1019)`，尺寸为 `978 × 51`；中间主屏逻辑范围为 `(0, 0, 1920, 1080)`。`NSScreen.visibleFrame` 显示中间屏幕底部预留 57 点，两侧均为 0。最终快照位于上述本机目录的 `after.json`。

底边鼠标压力测试未完成：Computer Use 获取 Dock 与桌面的可操作窗口失败，窗口截图也未提供足以持续停留各副屏底边的输入能力。因此完成证据为偏好持久化、当前系统迁移路径的静态核查和重启后实际 Dock 位置；不将它记成底边交互测试通过。电脑整机重启与屏幕断开重接也未测试。

适用范围为当前三屏连接及当前系统实现。隐藏偏好在后续系统升级后需复核；屏幕断开后系统重新选择主屏属于另一种情况。

## 恢复默认行为

原先该键不存在，恢复时只删除新增键，保留之后可能新增的其他 Dock 偏好：

```sh
defaults delete com.apple.dock allow-display-switching
killall Dock
```

## 备用方案依据

[Apple 的桌面与程序坞说明](https://support.apple.com/en-gb/guide/mac-help/mchlp1119/mac)说明：关闭独立 Spaces 后 Dock 只在主屏，而副屏 Split View、Stage Manager 依赖独立 Spaces。此次保留该选项。

[AeroSpace 官方指南](https://github.com/nikitabobko/AeroSpace/blob/main/docs/guide.adoc)指出关闭独立 Spaces 需要注销，并会影响多屏原生全屏行为。此次没有采用此方案。

[Apple Dock 配置 schema](https://github.com/apple/device-management/blob/release/mdm/profiles/com.apple.dock.yaml)中的 `position-immutable` 对应上下左右的朝向设置，不能据此承诺锁定指定显示器。
