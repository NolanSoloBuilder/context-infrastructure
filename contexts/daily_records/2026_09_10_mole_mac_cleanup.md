# 2026-09-10 Mac 缓存清理

用户确认后使用本机 Mole 1.47.1 清理缓存、日志和临时文件。预览估算 14.32 GB；执行正常结束，Mole 统计 1021 项、40 类，直接跟踪删除 5.80 GB，磁盘可用空间净增加约 12.02 GB，从约 44.55 GB 增至 56.57 GB。包管理器内部清理不完全计入逐项统计；磁盘净变化也可能包含并发系统活动。

保留现有白名单，并增加 Maven 本地仓库、CoreSimulator、XCTestDevices、iOS DeviceSupport 和启动项目录保护。执行后回读 Maven 约 1.5 GiB、CoreSimulator 系统缓存约 7.3 GiB，废纸篓存在。Codex 日志明确显示会话和凭据保留。

本次加载 Mole 原有 clean.sh 后，仅在本次 shell 中禁用管理员清理、移动端资源、AI 工具旧版本、应用残留、LaunchServices 清理、虚拟化资源、固件及失败备份清理，再调用原 main；未修改安装的 CLI 文件。后续直接运行 mo clean 不会继承这些临时禁用项，只有持久白名单会继续生效。

白名单：`/Users/xuhao/.config/mole/whitelist`。
原白名单备份：`/Users/xuhao/.config/mole/whitelist.backup-20260910-114025`。
执行日志：`/tmp/mole-clean-20260910.log`（临时文件）。

未修改代码、切换分支或提交；仅新增本记录。
