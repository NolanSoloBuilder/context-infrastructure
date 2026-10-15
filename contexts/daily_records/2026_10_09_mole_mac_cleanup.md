# 2026-10-09 Mole CLI 更新与 Mac 缓存清理

用户要求更新 Mole CLI 并清理本机。通过 Homebrew 将 Mole 从 `1.47.1` 升至 `1.58.0`，随后完成限定范围的预览和实际清理，退出码为 `0`。执行后 `mo --version` 回读版本 `1.58.0`、安装来源 `Homebrew`；官方最新稳定版核对来源为 [Mole V1.58.0](https://github.com/tw93/Mole/releases/tag/V1.58.0)。

## 结果

以下 `GB` 使用十进制单位，数据来自本机当次执行；磁盘净变化会受到并发系统活动影响。

| 指标 | 结果 |
| --- | --- |
| 筛选后的 dry-run 估算 | 9.80 GB |
| Mole 跟踪清理量 | 9.81 GB |
| Mole 处理项目数 | 306 |
| 执行前 `df` 可用空间 | 23.031 GB |
| 执行后 `df` 可用空间 | 32.537 GB |
| `df` 可用空间净增加 | 9.506 GB，约 8.85 GiB |

主要处理应用缓存约 4.56 GB、npm 下载缓存约 4.16 GB、GoogleUpdater CRX 缓存约 769 MB、应用日志约 267 MB，以及部分系统应用临时缓存；运行了 uv 的原生 `cache prune`。这些分类存在包含关系，不能简单相加作为磁盘净释放量。

## 执行范围与保护

沿用 2026-09-10 的缓存、日志、临时文件范围。读取新版真实源码后，在独立临时 shell 中加载 Mole 的原始 `clean.sh`，覆盖范围外的清理函数，再调用其原 `main`。没有修改安装的 CLI 源码或持久白名单，也没有启用测试模式或绕过删除保护。

本次关闭管理员级清理、APFS 快照处理、项目目录扫描、移动开发资源清理、AI 工具及编辑器旧版本清理、自动化浏览器终止、应用残留清理、虚拟机清理、固件、备份及 Homebrew Cellar 旧版本清理。保留浏览器的 Service Worker/offline 状态、最近项目列表、下载文件和废纸篓。

开发工具部分只调用明确的 npm/tnpm/pip 下载缓存、pyenv 下载缓存、uv prune、全局前端缓存和 Homebrew 下载缓存清理。这里的 Homebrew API/bootsnap 缓存仍属于原生用户缓存扫描范围；本次未调用 `brew cleanup` 或 `brew autoremove`。

临时保护整个 Documents、Desktop、Downloads、Codex 数据与 runtime、OpenCode 数据及 Puppeteer 下载的浏览器。本次没有触碰项目的 `node_modules`、源码或工作区 Git 改动。

npx 缓存初始预览约 18.12 GB，共 573 个目录；检测到三个正在使用的缓存目录。候选必须超过七天，并在删除前重复确认进程及完整 lsof 视图无占用。当前完整占用视图无法确认，候选全部保留；执行后仍为 573 个目录，三个活跃目录存在。

执行后回读 Maven、系统/用户 CoreSimulator、XCTestDevices、iOS DeviceSupport、Trash 和 Codex 关键目录/数据库均存在且 inode 未变化。Codex 凭据及持久白名单内容校验一致；仅记录校验结论，不保存凭据明文或哈希。已有 tracked 工作区状态与执行前一致。

## 命令与临时证据

升级：

```bash
HOMEBREW_NO_AUTO_UPDATE=1 HOMEBREW_NO_INSTALL_CLEANUP=1 HOMEBREW_NO_INSTALLED_DEPENDENTS_CHECK=1 brew upgrade mole
```

清理使用临时 wrapper，依次执行 `--dry-run` 和实际运行。wrapper 仅适配本次核对过的 `1.58.0`，后续应重新核对版本、源码和范围。直接运行 `mo clean` 不会继承临时禁用项。

- 临时 wrapper：`/tmp/mole-scoped-clean-20261009.sh`
- 范围预览日志：`/tmp/mole-scoped-preview-20261009.log`
- 保存的预览清单：`/tmp/mole-scoped-clean-list-20261009.txt`
- 执行日志：`/tmp/mole-clean-20261009.log`
- 保护项和磁盘核验结果：`/tmp/mole-verification-20261009.json`

最初的全范围 dry-run 在开发工具阶段停止，随后以修正后的同范围预览作为执行依据。预览数字与实际清理数字分别记录，不把全范围潜在空间当成已释放空间。
