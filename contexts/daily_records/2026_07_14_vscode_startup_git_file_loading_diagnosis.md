# VS Code 初始化、Git 与文件加载缓慢诊断

日期：2026-07-14

## 现场结论

本次问题由三个因素叠加造成，磁盘健康和仓库规模不是主因。

1. VS Code 用户配置中的 `git.path` 指向已经不存在的 `/Users/xuhao/.git-ai/bin/git`。内置 Git 日志出现 `Git installation not found`，因此 Source Control 的 Git model 无法创建；GitHub Actions 等依赖 Git model 的扩展也随之失败。
2. 当前窗口打开 `/Users/xuhao/Documents/Basic/vibe-marketing-rn` 后，extension host 在激活 `TypeScriptTeam.native-preview` 与 `Wscats.eno` 的阶段停顿约 8 分钟。renderer 在 `11:08:47` 标记 extension host unresponsive，直到 `11:16:48` 才恢复。`TypeScriptTeam.native-preview` 同时存在缺失中文 l10n bundle 的错误。现有日志只能把停顿范围缩小到这两个同期激活的扩展；单独归因仍需逐个禁用做 A/B。
3. 整机负载长期超过正常范围。现场 `load average` 为 `31/23/16`；Microsoft Defender 的 `wdavdaemon`、`epsext`、EDR 进程合计持续占用约 `130%–200% CPU`，两个 Mindspace Python 服务合计约 `80% CPU`。Defender 实时防护处于 managed enabled，`mdatp health` 为 unhealthy，并继续报告 `YunshuManager` 冲突。文件事件发生积压后，VS Code 的 FSEvents client 连续丢事件，被迫对 `vibe-marketing-rn` 反复全量重扫。

## 排除项

- APFS SSD 的 SMART 状态为 `Verified`，容器仍有约 `136.7 GB` 空闲空间。
- `vibe-marketing-rn` 约 `1.3 GB`，其中 `node_modules` 约 `992 MB`；Git 仅跟踪约 `906` 个文件。
- 使用系统 Git 执行完整 `git status --untracked-files=all` 约 `0.15–0.33s`，仓库自身不会造成分钟级等待。
- 当前 VS Code 安装 46 个扩展、约 `634 MB`。扩展数量会增加初始化成本，但本次有更直接的无效 Git 路径、extension host 停顿与系统级资源争用证据。

## 后续处理顺序

1. 删除无效的 `git.path`，让 VS Code 自动使用 PATH 中的 Git；或明确改为当前存在的 `/opt/homebrew/bin/git`。Reload Window 后先验收 Source Control 与 Git 日志。
2. 以单变量方式分别禁用 `TypeScriptTeam.native-preview`、`Wscats.eno` 后冷启动相同 workspace，比较 extension host 到 `Eager extensions activated` 的时间。不要同时禁用多个扩展，否则无法归因。
3. 关闭当前不需要的 Mindspace backend / ML 进程后重采一次 CPU、load average 和 VS Code 冷启动时间。
4. Defender 属于 managed 配置时，优先向管理侧申请对开发目录和高频生成目录的实时扫描排除；如果本机权限允许，再单独做实时防护 A/B。网络过滤器状态与文件实时扫描是两个子系统，不能用 network filter 已停用推断文件扫描也已停用。
5. 如果仍出现 FSEvents dropped，再根据 `hammer dev` 的生成目录补充 workspace 级 `files.watcherExclude`，每次只增加一类目录并复测。

本次仅执行只读诊断，没有修改 VS Code 配置、扩展状态、安全软件或后台进程。
