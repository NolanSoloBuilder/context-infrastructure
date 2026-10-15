# CPU 高占用只读诊断

2026-10-15 11:17 至 11:20，Asia/Shanghai。全程只读，没有暂停、终止进程或修改配置。10 个逻辑 CPU，系统 11:09:39 重启。

PID 14082 的 log show --last 30d 查询 mdmclient / ManagedClient；父进程 bash 13418，祖先进程为 IntuneMdmDaemon 795。属于企业管理任务。

PID 1677 执行 tar -czf ~/.cc-mirror/codewiz-cc/config/shared-dirs-backup.tar.gz -C ~/.claude agents commands plugins skills；备份约 102 MiB 且 mtime 更新，未终止。

App Store 进程打开 storeSystem/storeUser/Cache 数据库，尚不能确定正在执行的具体业务。Defender 高 CPU，但未确定其扫描对象。Spotlight、Siri 等重启后服务也在活动。Codex Renderer 有明显波动。

较早采样内存压力级别 1，Swap 约 2.1 GiB；没有温控或性能警告记录。当前两项铝构任务与本聊天均 active，未中断。

进程 CPU 100% 表示一个逻辑核，连续采样结果：

{
  "global": [
    "25.81% user, 9.38% sys, 64.79% idle ",
    "19.24% user, 13.63% sys, 67.12% idle ",
    "28.30% user, 7.69% sys, 64.0% idle "
  ],
  "top_processes": [
    {
      "pid": 299,
      "name": "mds_stores",
      "average_cpu": 81.3,
      "peak_cpu": 84.8
    },
    {
      "pid": 17299,
      "name": "log",
      "average_cpu": 33.1,
      "peak_cpu": 99.2
    },
    {
      "pid": 14082,
      "name": "log",
      "average_cpu": 27.9,
      "peak_cpu": 83.7
    },
    {
      "pid": 957,
      "name": "Codex (Service)",
      "average_cpu": 26.7,
      "peak_cpu": 29.6
    },
    {
      "pid": 0,
      "name": "kernel_task",
      "average_cpu": 18.7,
      "peak_cpu": 25.3
    },
    {
      "pid": 179,
      "name": "WindowServer",
      "average_cpu": 16.2,
      "peak_cpu": 23.8
    },
    {
      "pid": 10589,
      "name": "Codex (Renderer)",
      "average_cpu": 15.8,
      "peak_cpu": 17.6
    },
    {
      "pid": 240,
      "name": "lsd",
      "average_cpu": 7.7,
      "peak_cpu": 23.0
    },
    {
      "pid": 17062,
      "name": "Google Chrome He",
      "average_cpu": 6.7,
      "peak_cpu": 11.6
    },
    {
      "pid": 376,
      "name": "YunshuManager",
      "average_cpu": 5.2,
      "peak_cpu": 8.7
    },
    {
      "pid": 1298,
      "name": "Codex (Renderer)",
      "average_cpu": 4.1,
      "peak_cpu": 5.2
    },
    {
      "pid": 11213,
      "name": "wdavdaemon_unpri",
      "average_cpu": 3.7,
      "peak_cpu": 4.0
    },
    {
      "pid": 1775,
      "name": "TG Pro",
      "average_cpu": 3.6,
      "peak_cpu": 6.1
    },
    {
      "pid": 17281,
      "name": "top",
      "average_cpu": 3.1,
      "peak_cpu": 3.4
    },
    {
      "pid": 17035,
      "name": "Google Chrome",
      "average_cpu": 2.9,
      "peak_cpu": 4.7
    }
  ]
}

最终复查：全机 CPU 使用率自然回落至约 33% 至 36%，空闲率 64% 至 67%。Defender 合计约 8.4% 单核口径；主要持续进程为 mds_stores 约 81% 单核口径。Codewiz tar PID 1677 与第一条日志查询 PID 14082 自然退出，App Store CPU 回落至 0%。Intune 同一脚本又启动 PID 17299，查询过去 30 天 storedownloadd/appstored 日志，说明企业诊断脚本在连续扫描不同类别日志。没有终止这些任务。

## 重启后的优化优先级

11:21:48 复查：CPU 约 22.7%，内存压力级别 1，Swap 约 2.35 GiB，压缩内存约 5 GiB。高峰已自然下降，16 GiB 内存余量仍有限。当前启用三十多个插件，另有 Fedith、tracking-kit、Playwright、网易邮件等手动 MCP 配置。插件安装数不等于常驻进程数，不能按安装数直接估算收益。

建议按优先级：先精简暂时不用且会启动本地服务的工具；重型本地构建/测试分时运行，不要求关闭所有并行聊天；对 Intune 30 天日志采集和 Defender 扫描请 IT 评估频率/时机，不擅自更改企业安全配置；Redis、DevSpace/cloudflared 按需决定是否自启，当前 CPU 低，优先级较低。保留的 codewiz-cc 备份机制可检查是否重复打包共享插件目录，之前 gzip/tar 活动真实存在，尚未确认其调度入口。未执行额外配置修改。

## 14:55 资源复查

连续两段有效 CPU 采样约 30.9%、18.8%；10 核机器 load average 约 3.84/4.18/3.92。16 GiB 物理内存约 15 GiB 已用，压缩内存约 6.6 GiB，Swap 已用约 3.0 GiB，内存压力级别 2。采样区间 swapouts 增量为 0，swapins 少量增加。结论：CPU 当前余量充足，内存压力偏高但没有观察到持续大量换出，不能只因 swap 存量断言正在严重抖动。全程只读，无进程终止或配置修改。
