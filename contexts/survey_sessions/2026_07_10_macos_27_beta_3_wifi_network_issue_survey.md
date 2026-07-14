# macOS 27 Beta 3 更新后网络异常调查

日期：2026-07-10

设备：MacBook Pro（Mac14,9，Apple M2 Pro）

系统：macOS 27.0 Beta 3，Build `26A5378j`

## 结论

公开报告与本机现场状态相互吻合。macOS 27 Beta 3 在 2026-07-06/07 发布后，社区集中报告网络超时、Chromium/Electron/Node 应用卡住，以及 VPN、Content Filter、Network Extension 与新系统组合后连接异常。

本机目前并非 Wi-Fi 无线链路质量差：`RED-ENGINEER` 使用 5 GHz / 802.11ax，信号 `-51 dBm`、噪声 `-88 dBm`、协商速率 573 Mbps，DHCP 地址、网关和企业 DNS 均已取得。异常主要发生在 Wi-Fi 之上的系统网络栈：

- 默认 IPv4 路由由 `utun26` 接管，地址 `100.96.7.0`，VPN server 显示 `127.0.0.1`；系统网络服务中 `str-lax311` 对应 WireGuard。
- DNS 主解析器由 `utun26` 上的 `198.18.0.1`、`198.18.0.2` 接管。
- Microsoft Defender Network Extension `com.microsoft.wdav.netext` 处于 enabled + active。
- `mdatp health` 显示 `network_events_subsystem = network_filter_extension`、Network Protection 已启动，并直接报告 `conflicting_applications = YunshuManager`；Defender 由 MDM 管理。
- OpenVPN、REDpass/Yunshu 和 WireGuard 相关进程同时存在，网络扩展叠加复杂。
- 到 Wi-Fi 网关 `10.21.32.1` 的 12 次探测没有丢包，多数延迟约 4–24 ms；经隧道访问公网时，到 `1.1.1.1` 平均约 303 ms，到 `8.8.8.8` 平均约 270 ms 且出现 25% 丢包。

因此，当前首要嫌疑是 macOS 27 Beta 3 与企业 Network Filter / VPN 扩展的兼容回归，并由本机多层隧道叠加放大。Beta 3 的 IPv6 回归也是已出现的同版本问题，但本机 Wi-Fi 当前没有全局 IPv6 地址或 IPv6 默认路由，所以优先级低于 Network Filter 与 WireGuard 路由冲突。

## 关闭后台隧道后的 A/B 结果

用户关闭后台隧道后再次采样：

- 默认路由从 `utun26` 回到 Wi-Fi `en0`，公网流量经网关 `10.21.32.1` 直接发出。
- `198.18.0.1`、`198.18.0.2` 隧道 DNS 消失，主 DNS 恢复为企业 Wi-Fi 提供的 `10.21.3.63`、`10.21.3.64`、`10.188.0.41`。
- 到 `1.1.1.1` 的平均延迟从约 303 ms 降到约 97 ms；到 `8.8.8.8` 从约 270 ms 降到约 112 ms；两者本轮均为 0% 丢包。
- 到 Wi-Fi 网关仍存在少量瞬时抖动，但 10 次探测没有丢包。

关闭隧道解决了默认路由和隧道 DNS 叠加，但强制 IPv4 HTTPS 请求仍能复现随机 TCP connect timeout，因此继续对 Microsoft Defender Network Filter 做了单变量 A/B：

- Filter enabled：30 次请求成功 27 次，3 次 connect timeout；平均连接时间 107 ms，总耗时 711 ms。
- Filter disabled：30 次请求全部成功；平均连接时间 65 ms，总耗时 475 ms。
- 测试后已经重新 enable Filter，并通过 `systemextensionsctl list` 验证 `com.microsoft.wdav.netext` 为 `activated enabled`。

这个 A/B 支持把剩余异常收敛到 Defender Network Filter 与 Yunshu/macOS 27 Beta 3 的组合。IPv6 不是本轮 TCP timeout 的直接原因，因为失败样本明确使用 `curl -4`，而 Node DNS 查询也只返回 IPv4 地址。

Microsoft AutoUpdate 在线检查显示 Defender 暂无可用更新；Apple `softwareupdate --list` 同样显示没有新系统更新。当前没有来自 Apple 或 Microsoft 的已发布兼容修复。

## 公开证据

1. Apple 的 macOS 27 Beta 3 Release Notes 已确认当前 SDK/系统为 Beta 3，但发布说明目前没有列出上述 Wi-Fi、IPv6 或 Network Extension 连接回归。
   - https://developer.apple.com/documentation/macos-release-notes/macos-27-release-notes
2. `26A5378j` 对应 macOS 27 Golden Gate Beta 3。
   - https://9to5mac.com/2026/07/06/macos-27-golden-gate-beta-3-now-available-heres-whats-to-expect/
3. 2026-07-07 起的集中报告包括：网页和 shell 请求超时、以太网同样受影响、关闭 Tailscale/TripMode/Radio Silence/Microsoft Defender Network Filter 后恢复。这个特征说明故障在系统 Network Extension / Content Filter 层，而不只发生在 Wi-Fi 射频层。
   - https://www.reddit.com/r/MacOSBeta/comments/1uq4ip9/networking_woes_on_macos_27_db3/
4. GitHub 上已经出现针对 Beta 3 的 IPv6 workaround。其诊断是 Wi-Fi 只有 link-local IPv6、没有可用 IPv6 route，导致优先尝试 IPv6 的 Chromium/Electron/Node 长时间等待；workaround 只是暂时关闭 Wi-Fi IPv6。
   - https://github.com/danielchr94/macos27-db3-ipv6-fix
5. GitHub 的 Tailscale issue 记录了 macOS Network Extension 状态卡在 `terminating_for_disable` / `activated_disabled`，并明确提到多套 VPN/Network Extension 共存可能相关。
   - https://github.com/tailscale/tailscale/issues/19203
6. Microsoft 官方当前仅支持 macOS 26、15 和 14，并明确写明 macOS beta 不受支持。因此 macOS 27 Beta 3 + MDM Defender Network Filter 本身就是未受支持组合。
   - https://learn.microsoft.com/en-us/defender-endpoint/microsoft-defender-endpoint-mac

## 建议的验证顺序

不要同时修改多个开关，否则无法确认真正的故障层。按以下顺序做 A/B：

1. 记录当前基线，然后只停用 `str-lax311`，确认默认路由是否从 `utun26` 回到 `en0`，复测同一批地址。
2. 如果异常仍在，在 IT/MDM 允许的范围内临时停用 Microsoft Defender Network Filter，再复测。社区报告和本机 `conflicting_applications` 都支持优先验证这一项。
3. 如果 Chromium/Electron/Node 仍异常而 Safari 正常，再临时执行 `networksetup -setv6off "Wi-Fi"` 验证 Beta 3 IPv6 回归；验证完成后用 `networksetup -setv6automatic "Wi-Fi"` 恢复。
4. 把复现与 A/B 结果提交到 Feedback Assistant。长期方案是安装 Apple 后续修复该回归的 beta，或者回到受 Defender 正式支持的 macOS 26。

本次没有修改 WireGuard、IPv6、DNS 或网络服务配置。为验证根因，曾临时 disable Microsoft Defender Network Filter 并在 A/B 后恢复。随后按用户要求再次执行 `mdatp system-extension network-filter disable`，命令返回 `Success`，用于验证重启后 NetExt 是否保持停用。重启前 `systemextensionsctl` 仍显示扩展已加载；Microsoft 官方说明停用不保证扩展立即终止，但应阻止它在重启后重新加载。重启后的实际状态仍需重新采样确认，同时需要观察 MDM 是否重新启用该扩展。

### 重启后验证

设备于 17:28:40 重启，约 5 分钟后采样：

- `systemextensionsctl` 仍保留 `com.microsoft.wdav.netext` 的 `activated enabled` 注册记录。
- 进程表中不存在 `netext` 实际进程。
- `mdatp health` 显示 `network_events_subsystem = unavailable`、`network_protection_status = enablement_failed_due_to_netext_not_running`，说明网络过滤功能没有运行。
- 默认路由保持在 `en0`，隧道 DNS 未出现。
- 30 次 IPv4 HTTPS 并发探测全部成功，0 次 timeout，平均连接时间 114 ms、平均总耗时 489 ms。

因此，`mdatp system-extension network-filter disable` 的停用状态跨重启生效。扩展仍安装并注册，但不再实际过滤网络。MDM 当前尚未重新启动 NetExt，后续策略刷新仍可能改变这一状态。
