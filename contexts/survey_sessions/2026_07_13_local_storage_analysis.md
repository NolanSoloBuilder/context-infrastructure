# 本机存储空间分析

扫描时间：2026-07-13（Asia/Shanghai）

扫描方式：使用 `storage-analyzer` 对用户目录、`~/Library`、应用、开发缓存、容器和项目目录执行只读 `du`、`df`、`stat` 与元数据检查。完整扫描耗时 589.9 秒，没有执行删除、移动、清空缓存或修改权限。

交互报告的数据源见 [`2026_07_13_local_storage_analysis.json`](./2026_07_13_local_storage_analysis.json)。Codex 目录的专项分析见 [`2026_07_13_codex_storage_cache_analysis.md`](./2026_07_13_codex_storage_cache_analysis.md)。

## 磁盘基线

- 系统盘：`Macintosh HD`，APFS
- 总容量：约 460.4 GB
- 已用：约 369.4 GB
- 可用：约 91.0 GB
- 扫描未遇到权限拒绝目录

## 结论

当前并非磁盘即将写满的应急状态，但开发工具链积累了大量可再生数据。明确可回收项估算约 **47.0 GB**，主要来自：

- `~/Library/pnpm/store`：约 14.1 GB
- `~/Library/Caches`：约 11.4 GB
- `~/.nvm/.cache`：约 8.6 GB
- `~/.npm` 下载和 `npx` 缓存：约 4.4 GB
- Xcode `iOS DeviceSupport`：约 5.6 GB
- Codex runtime、Browser Cache 和临时同步目录：额外约 2.9 GB，其中 `~/Library/Caches/Codex` 已计入通用缓存，不重复计数

另有约 **15.6 GB** Node 运行时需要人工治理。本机同时配置 NVM 与 FNM：NVM 安装 15 个 Node 版本，FNM 安装 6 个版本，v14、v16、v18、v20、v22 存在重复。由于全局 CLI 可能分散在不同 Node 版本中，正确顺序是先选定一个版本管理器、盘点全局 CLI 和项目版本约束，再通过 `nvm uninstall` / `fnm uninstall` 逐个卸载。

## 建议顺序

1. 先清 NVM 下载缓存与 npm/npx 缓存，预计释放约 13.0 GB，对现有 Node 版本和项目代码影响最低。
2. 执行 `pnpm store prune`；如果接受之后重新下载依赖，再处理完整 pnpm store。
3. 完全退出微信、Chrome、Codex、Xcode、Lark 等应用后清理 `~/Library/Caches`。
4. 近期不做真机调试时再处理 Xcode `iOS DeviceSupport`。
5. 最后统一 NVM/FNM，并迁移全局 CLI 后卸载旧 Node 版本。

## 优化策略

理论可清理上限约 47.0 GB，不等于应该一次全部清掉。当前可用空间约 91.0 GB，首轮以释放 25–35 GB 为目标，可把可用空间提高到约 116–126 GB。达到这一范围后，继续删除当前开发运行时的边际收益下降，重新下载和环境失效的成本开始上升。

第一阶段处理低风险缓存：清理 NVM 下载缓存、npm/npx 缓存，并执行 `pnpm store prune`。`~/Library/pnpm/global` 只有约 43 MB，应该保留；14.1 GB 的大头位于 content-addressable store。日常维护应使用 `pnpm store prune`，完整删除 store 只适合急需空间且接受重新下载依赖时使用。

第二阶段处理应用缓存：完全退出微信、Chrome、Codex、Lark、Xcode 等应用后，再清理 `~/Library/Caches`。Codex 的会话 JSONL、`state_5.sqlite`、`session_index.jsonl` 和 memories 不属于缓存，不应混入这一阶段。Codex 任务历史需要遵循 `【长期】` 标记、运行状态排除、dry-run 和应用原生删除的一致性流程。

第三阶段统一 Node 环境。本机同时存在 Homebrew Node、NVM 和 FNM，`.zshrc` 又同时初始化 NVM/FNM，导致交互 shell、脚本和全局 CLI 可能指向不同运行时。现有 workspace 和自动化已经广泛使用 `NVM_DIR` 与 `nvm.sh`，建议把 NVM 作为唯一版本管理器：默认保留 v22.22.0，扫描活跃仓库的 `.nvmrc` 和 `package.json engines` 后保留必要兼容版本，把全局 CLI 迁入默认版本，再删除 FNM 初始化和重复版本。预计可额外释放约 10–14 GB。

Xcode `iOS DeviceSupport` 当前只有一份 `iPhone16,1 26.5 (23F77)`，说明它更可能是正在使用的真机调试支持，而不是多个历史版本残留。近期仍做 iOS 真机开发时应保留这 5.6 GB。Android SDK、CoreSimulator、REDcity 与项目仓库同理，只在对应开发或应用内入口确认不用后处理。

建议采用容量阈值触发巡检，而不是固定日期无差别清理：NVM cache 或 npm cache 超过 2 GB、pnpm store 超过 8 GB、`~/Library/Caches` 超过 15 GB、Codex 总占用超过 8 GB、模拟器与 Android SDK 合计超过 10 GB时再检查。系统盘长期保持至少 20% 可用空间；本机对应约 92 GB，首轮清理后的目标可设为 120 GB 以上。

## 需要人工判断的内容

- `~/Documents` 已识别项目约 15.4 GB，包含源码、未提交改动、依赖和本 workspace 的长期资料。只能按仓库逐个审查。
- `~/Library/Application Support/REDcity` 约 6.3 GB，其中 IM 数据约 4.3 GB。优先使用应用内存储管理。
- Android SDK 约 6.4 GB，其中 NDK 与 system images 约 4.6 GB。通过 Android Studio SDK Manager 删除不用版本。
- CoreSimulator Devices 约 3.5 GB。通过 Xcode Devices and Simulators 或 `xcrun simctl delete unavailable` 处理。
- Lark 本地数据约 3.6 GB，其中 `update` 约 1.8 GB；其余数据库与 `aha` 目录应由应用管理。

## 已确认的重复应用

`/Applications/WeChat.app` 与 `/Applications/WeChat 2.app` 的 bundle identifier 都是 `com.tencent.xinWeChat`。前者版本为 4.1.11，后者为 4.1.10。确认新版可正常使用后，可从访达卸载旧版 `WeChat 2.app`，预计释放约 660 MB；不要同时删除微信的容器和聊天数据。

## 安全边界

本次只生成报告。交互页面的删除接口绑定 `127.0.0.1`，使用随机端口、随机 token、Host 校验与路径白名单；绿灯项才允许直接删除，橙灯项最多允许移入废纸篓，红灯项只允许在访达中定位。页面上的每次操作仍需要人工确认。
