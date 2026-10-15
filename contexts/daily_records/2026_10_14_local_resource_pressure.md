# 本机 CPU 与内存压力检查

检查时间：2026-10-14 15:04，Asia/Shanghai。仅执行只读系统检查，没有终止进程或修改配置。

- 机器：16 GiB 内存，10 个逻辑 CPU。
- 峰值采样：CPU 空闲约 0.1%，load average 34.61；物理内存约 15 GiB 已用，压缩内存约 6.5 GiB；swap 从约 8.8 GiB 增至 10.5 GiB。
- 同时观察到：Codex 下多批 MCP 启动进程、BeamJoin Vitest 与 TypeScript 检查，以及 Codex Node runtime tar.xz 解包。Node/npm 61 个进程的瞬时 CPU 合计约 456%（进程 CPU 百分比按单核计）。
- 后续采样（15:04:29）：CPU 空闲回升至 39.24%，内存压力级别由 2 回落至 1，未用内存约 1.8 GiB，压缩内存约 2.3 GiB；采样区间 swapouts 增量为 0，但已用 swap 仍约 10.5 GiB。部分测试/启动进程自然退出，不能认为已永久解决。
- 后续 CPU 主要占用：Microsoft Defender 多进程、runtime 解包、YunshuManager。安全软件是否因安装/测试文件活动触发扫描尚未证实。
- 没有记录到温控或性能警告，磁盘可用约 166 GiB。

建议先降低同时运行的 Codex 任务与测试数量，避免并行启动多套 MCP；若启动活动结束后仍持续高压，再定位残留进程和插件实例。需区分 RSS、top MEM 与压缩内存，不能用 RSS 排名认定完整内存占用；swap 存量不能独立证明当前仍在持续换页。

## 15:06 至 15:10 清理与 MCP 检查

用户要求清理不用的重复/残留 MCP，保护正在运行的任务；随后明确确认 OpenClaw 不再使用，停止并关闭自启。

- OpenClaw 是独立 Telegram 网关，不是 Codex MCP。cron/jobs.json 无定时任务，配置启用 Telegram，检查时存在 Telegram TLS 连接。执行 launchctl disable 与 bootout；回读服务未加载、PID 1121 退出、18789 端口不再监听。保留 plist、配置和凭据。恢复方式为 launchctl enable gui/<uid>/ai.openclaw.gateway，随后 bootstrap 对应 LaunchAgent plist。
- 清理旧版 154.0.8037.98 的 crashpad handler：PID 4456 的 stdin/stdout 指向 /dev/null，未发现 PIPE/unix/网络连接；发送 SIGTERM。配对进程 4458 随后也退出，未操作当前 155 版本进程。
- 快照中 ngs_workbench_mcp、ngs_app_mcp、ngs_compute_mcp、邮件与 Creem 测试 MCP 各 7 份；Playwright、Fedith、XcodeBuildMCP 也出现各 7 份（数量随任务变化）。共同父进程为当前 Codex app-server 49580。
- 对 6 份较早启动的 ngs_workbench_mcp 逐一核对 stdin/stdout 管道地址，两端对端均被当前 Codex app-server 持有。因此不能将同名/闲置实例当作残留直接 kill。本次没有结束这些 MCP，没有修改 Codex MCP 配置或卸载插件。
- 任务状态回读：参考实拍图任务已 idle，示例资料格式任务仍 active。未向其他任务发送消息，也未终止其测试、浏览器或开发服务。
- 15:08:51 CPU 再次接近满载（空闲 0.26%），说明停止 OpenClaw 不能解决全部压力；当时内存压力级别 1，未用内存约 2.1 GiB，swap 约 10.8 GiB。负载波动与持续启动活动仍需区分。

## 关闭暂时不用的生信与 Creem 工具

用户明确授权关闭生信相关工具与 Creem 测试 MCP。对 config.toml 设置以下插件 enabled=false：ngs-analysis-workbench, life-sciences-databases, life-sciences-literature, rosalind, sequence-viewer, structure-viewer, slide-viewer；对 mcp_servers.creem-test 设置 enabled=false。保留安装文件、数据与原有配置，修改前保存权限 0600 的配置备份。TOML 解析通过。

精确核对命令与插件 cwd 后向工具进程发送 SIGTERM：{'creem-test': 5, 'ngs-analysis-workbench': 15, 'rosalind': 5, 'sequence-viewer': 5, 'slide-viewer': 5, 'structure-viewer': 5}，共 40 个。未重启 Codex，未操作邮件、浏览器、铝构服务或其他工具。

清理后回读：7 个生信插件与 Creem 均 enabled=false；NGS/Creem 命令进程为零；全机 lsof cwd 未发现上述生信插件进程残留。15:18:34 CPU 空闲率约 38%，压缩内存仍约 5.6 GiB；只记录即时采样，不据此认定压力永久解决。
