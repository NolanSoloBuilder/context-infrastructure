# Codex 渲染进程只读检查

2026-10-15 14:56 至 15:00。用户要求定位渲染进程并只释放确认闲置的实例，不影响运行任务。

当前有 11 个 Codex Renderer，均由当前客户端主进程 PID 793 管理。命令行暴露 renderer-client-id，但这不是 webContentsId，不能直接按相同数字绑定窗口。

客户端当前主日志记录最近已知窗口角色：webContentsId 1 为可见 primary 主窗口；4 为隐藏 primary；3 与 8 为隐藏 globalDictation；5 为隐藏 avatarOverlay。日志也显示同一运行任务事件会被发送到多个窗口。以上是日志中的最近状态，不是已确认的实时 PID 对照。

没有发现可靠的 OS PID 与 webContents/窗口的一一映射接口。当前聊天的内置浏览器 tab 列表为空；持久化 browser-sidebar-page-states.json 含历史页面，不能把历史条目当作当前打开页面，更不能直接删除状态文件释放内存。电脑控制工具不允许直接操作 Codex 本身，未尝试绕过此限制。

正在运行的聊天包括本诊断、StrongVPN 节点下载与铝构界面评审。尚未确认任何渲染进程已断开/无功能依赖，未向任何渲染进程发送信号，未关闭、重载窗口或改写浏览器状态文件。

当前 top 内存口径（包含与 RSS 不同的内存统计，不等于可立即释放的物理内存）：

[
  {
    "pid": 1298,
    "memory": "1484M"
  },
  {
    "pid": 2644,
    "memory": "603M"
  },
  {
    "pid": 3437,
    "memory": "404M"
  },
  {
    "pid": 2650,
    "memory": "396M"
  },
  {
    "pid": 36090,
    "memory": "254M"
  },
  {
    "pid": 4337,
    "memory": "246M"
  },
  {
    "pid": 1296,
    "memory": "126M"
  },
  {
    "pid": 3416,
    "memory": "109M"
  },
  {
    "pid": 2080,
    "memory": "52M"
  },
  {
    "pid": 4290,
    "memory": "36M"
  },
  {
    "pid": 2881,
    "memory": "36M"
  }
]
