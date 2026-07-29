# Codex 启动后发热诊断（2026-07-23）

## 结论

这次现场采样没有复现 Codex renderer 在空闲时持续占用一个完整 CPU 核的状态。Codex 页面有输出或刷新时，renderer / GPU helper 会短时升到约 25%–45%；静置采样时，Codex 主进程、renderer、GPU helper 和 app-server 通常合计低于约 7%。

机器当前持续发热的主要 CPU 来源是 Microsoft Defender、WindowServer 和 Spotlight。Codex 启动会刷新本地会话索引、插件 cache、bundled marketplace 和 Git vendor imports，同时启动多组 Node MCP server。这些文件读取、写入和进程加载会触发 Defender 与 Spotlight，使用户感受到“打开 Codex 后立刻升温”。Codex 是触发器和增量负载，Defender 的长期高占用与系统已有的内存压力决定了升温幅度。

本机的第二个放大因素是 Codex 历史体积。当前 active session 约 2.0 GiB，共 468 个 rollout；archived session 约 161 MiB，共 126 个 rollout。最大单文件约 225 MiB。`state_5.sqlite` 记录了 594 个 thread。Codex 启动后仍打开了一个约 84 MiB 和一个约 11 MiB 的旧 rollout 文件，说明启动后的 thread/state 恢复确实会读取大历史。

## 当前环境

- 时间：2026-07-23 17:06–17:12 CST
- 设备：`Mac14,9`，Apple Silicon，16 GiB 内存
- 系统：macOS 27.0，build `26A5378j`
- Codex Desktop：`26.715.72359`，build `5718`
- macOS thermal 状态：没有记录 thermal warning 或 performance warning
- swap：总计 11 GiB，已用约 10.0 GiB
- 采样期间压缩内存：约 6.1–7.0 GiB
- 可用内存：多次只有约 100–250 MiB

## 现场证据

### 1. 持续 CPU 主要来自系统服务

30 秒静置采样中：

- `wdavdaemon_unprivileged` 多次处于约 25%–91% CPU。
- `WindowServer` 多次处于约 28%–45% CPU。
- `mds` / `mds_stores` 会在约 10%–86% 间波动。
- 同一时段 Codex `app-server` 多数处于约 0.3%–6.4%，renderer 多数处于约 0.5%–3.4%，GPU helper 多数接近 0%。

Defender 的 unprivileged 进程在首次采样时已经运行约 2 小时 28 分，累计 CPU 时间约 107 分钟，折算长期平均约占一个 CPU 核的 72%。它的高负载早于本次 Codex 启动，属于独立存在的背景异常。

### 2. Codex 启动和页面输出存在短时图形峰值

有大量工具输出进入页面时：

- renderer 最高采到约 45.3% CPU；
- GPU helper 最高采到约 24.9% CPU；
- app-server 最高采到约 14.7% CPU。

静置后这些进程明显回落，所以当前现场更符合输出渲染和启动 hydration 峰值，而不是持续 renderer busy loop。上游已有 renderer 长时间 85%–120% 的报告；如果后续空闲 2–3 分钟仍稳定超过 50%，应按该独立问题继续取样。

### 3. 启动时刷新了大量本地状态

启动后 30 分钟内发生变化的目录和文件包括：

- `~/.codex/vendor_imports/skills` 的 Git pack、index 和 `FETCH_HEAD`；
- `~/.codex/plugins/cache` 与 `.plugin-appserver`；
- `~/.codex/.tmp/bundled-marketplaces`；
- `state_5.sqlite-wal`、`memories_1.sqlite-wal`、`session_index.jsonl`；
- bundled browser / Chrome / computer-use plugin 文件。

目录体积：

- `~/.codex/plugins`：约 435 MiB；
- `~/.codex/.tmp`：约 845 MiB；
- `~/.codex/vendor_imports`：约 8 MiB；
- 单个 plugin app-server binary：约 253 MiB。

这类文件活动会同时触发 Spotlight metadata 处理和 Defender real-time protection。上游 issue #12644 记录了 Codex 高频文件 I/O 使 endpoint security 占用明显上升的同类机制。

### 4. MCP 有启动成本，当前没有孤儿泄漏证据

`config.toml` 当前配置了 13 个 MCP section。现场看到 4 组 Playwright、Fedith、tracking-kit、XcodeBuildMCP 和 `node_repl` 实例，它们都由当前 Codex `app-server` 持有，静置 CPU 为 0。没有发现这些实例被 re-parent 到 `launchd`（PPID 1）。

它们不是当前持续 CPU 的主要来源。不过每组都要执行 Node / `npm exec` 包加载，启动阶段会增加文件扫描、内存占用和 Defender 工作量。Codex 相关主进程与工具进程 RSS 在一次采样中合计约 1.1 GiB；renderer 另一次采样约为 460 MiB。对已经使用约 10 GiB swap 的 16 GiB 机器，这部分增量会明显增加内存压缩与换页成本。

### 5. 日志增长不是这次发热的主因，但观测仍受本地 trigger 限制

`logs_2.sqlite` 仍存在 `codex_block_logs_insert` trigger，`logs` 表为 0 行，`PRAGMA quick_check` 为 `ok`。`logs_2.sqlite-wal` 约 467 KiB，没有出现 GB 级日志增长。

这个 trigger 会阻止日志写入，因此当前可以排除可见的巨大日志文件，但无法使用 SQLite trace 还原精确的启动调用链。它属于本机 workaround，不能作为上游日志问题已经修复的证据。

## 与公开问题的对应关系

- [#12644：Codex 高频文件 I/O 会放大 endpoint security CPU](https://github.com/openai/codex/issues/12644)
- [#20435：Desktop renderer 在 MCP 空闲时持续高 CPU](https://github.com/openai/codex/issues/20435)
- [#24510：大量 thread metadata / 本地历史处理导致 Desktop 高 CPU](https://github.com/openai/codex/issues/24510)
- [#18467：macOS 更新后 renderer、WindowServer 和主进程共同升高](https://github.com/openai/codex/issues/18467)
- [#21008：MCP helper 遗留到 PPID 1 的泄漏问题](https://github.com/openai/codex/issues/21008)

本机与 #12644、#24510 的触发条件高度吻合。#20435 的持续 renderer 自旋本轮没有复现。#21008 的孤儿进程本轮没有发现。

## 下一步单变量验证

建议按以下顺序执行，每次完整退出 Codex 后复测 2–3 分钟：

1. 先处理 Defender 的长期高 CPU。由公司安全策略允许的管理员核对 Defender 当前扫描任务和排除策略；不要直接关闭实时防护。优先确认 `~/.codex/plugins/cache`、`~/.codex/.tmp`、`~/.codex/vendor_imports`、`~/.npm/_npx` 和 Codex application support 是否被反复扫描。
2. 把旧 session 做可恢复的隔离实验，而不是删除。完整退出 Codex，备份后把较老月份和 archived sessions 移到 Codex 不扫描的临时目录，只保留近期会话，再比较启动后 Defender、Spotlight、renderer 和 app-server 的 3 分钟平均 CPU。
3. 临时只保留实际需要的 MCP。把长期使用的 Node MCP 安装到全局 Node 环境，并让 Codex 直接调用固定版本 binary，减少多个 worker 反复执行 `npm exec ...@latest` 带来的包解析和扫描。复测时记录实例数、启动耗时和 Defender CPU。
4. 如果 renderer 在无输出、无滚动状态下连续 2–3 分钟仍高于 50%，单独采 renderer sample，并按 #20435 处理；完整重启 Codex 只能作为临时缓解。
5. 若要验证日志写入相关上游修复，必须先备份并完整退出 Codex，再做受控的 trigger 移除实验。本轮没有修改该 trigger。

本轮只做了只读检查，没有终止进程、清理 cache、迁移 session、修改 MCP 配置、改变 Spotlight 索引或 Defender 策略。

## 补充检查（17:25 CST）

Defender 的实时防护、enforcement level、计划扫描和 Tamper Protection 都由 MDM 管理。最近一次 on-demand quick scan 在 02:00 开始、02:01:33 结束，共扫描 8,470 个文件；当前高占用不是这次计划扫描仍在运行。

新的瞬时采样显示：

- `wdavdaemon_unprivileged`：约 223% CPU；
- Defender privileged daemon：约 42% CPU；
- Defender enterprise EDR：约 40% CPU；
- Defender Endpoint Security extension：约 37% CPU；
- `YunshuManager`：约 76% CPU；
- `YunshuPluginService`：约 30% CPU；
- Codex 主进程、app-server、renderer 和 GPU helper 合计约 97% CPU，其中当前页面持续接收诊断输出。

机器同时运行 Defender、Yunshu / REDpass 等企业终端组件。现有证据不能直接证明它们发生冲突，但多套终端组件会共同消费同一批文件与进程事件，可能放大 Codex 启动时的扫描成本。Microsoft 的 macOS 性能排查文档也要求先确认是否同时运行其他安全产品。

当前 swap 已用约 10.9 GiB。无论最终调整哪套安全策略，重启后做一次“只打开 Codex”的干净基线都有必要；否则历史换页压力会干扰所有 CPU 对比。
