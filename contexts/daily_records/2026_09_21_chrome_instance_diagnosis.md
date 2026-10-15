# Chrome 默认打开实例排查

2026-09-21 本机只读检查：HTTP、HTTPS 与默认浏览器关联均为 `com.google.chrome`。同时存在正式资料目录的 Chrome，以及运行约四天、由 Playwright `cliDaemon.js marketing --headed` 启动的 Chrome；后者使用临时 `playwright_chromiumdev_profile-*` 目录。

已通过 Chrome 可执行文件指定 `--profile-directory=Default chrome://newtab/`，返回“正在现有的浏览器会话中打开”。未关闭测试实例、未改系统关联。多实例导致链接选错是候选原因，尚未验证实际外部链接落在哪个实例；不能据此宣称默认打开问题已修复。

随后用户明确要求关闭测试实例。重新校验 PID 与临时资料目录后，向测试 Chrome 发送 SIGTERM；进程回读确认测试 Chrome 已退出，主账号 Chrome 仍在运行。未删除任何资料目录。
