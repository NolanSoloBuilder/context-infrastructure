# 安卓手机投屏

## 启动

```bash
/Users/xuhao/Documents/Other/context-infrastructure/adhoc_jobs/android_control/start_scrcpy.sh
```

默认连接本次授权的 OPPO PFFM10；更换设备时将 `adb devices` 中确认的序列号作为第一个参数传入。

## 当前配置

- 桌面入口：`~/Applications/Android投屏.app`，可在 Finder 的用户“应用程序”目录打开。
- 入口包装 Homebrew 的 scrcpy 二进制，便于 macOS 桌面控制工具识别；bundle ID 为 `local.xuhao.scrcpy`。
- scrcpy 5.0.1，Homebrew 安装在 `/opt/homebrew/bin/scrcpy`。
- 复用已有 SDK ADB：`~/Library/Android/sdk/platform-tools/adb`，通过 `ADB` 环境变量传给 scrcpy。
- USB，视频最长边 1440，最高30帧，关闭音频，窗口标题 `Android-PFFM10`。
- 关闭自动剪贴板同步；按需使用 scrcpy 的显式粘贴快捷键。普通键盘注入和剪贴板粘贴不是同一路径，中文需实机核验。
- 不修改全局 PATH，不重复安装 ADB，不增加开机自启。

2026-10-28 已实机验证：投屏显示、鼠标切换页面、右键返回、将“机器人”完整粘贴到雪球搜索框。纯 CLI 进程未被当前桌面控制工具识别，使用上述 App 入口后已能绑定和操作。后续升级 Homebrew scrcpy 时需同步桌面入口内的二进制与版本信息，不能仅升级 CLI 就假定包装入口也已更新。

## 日常操作

手机先解锁。用鼠标点击、滚轮滚动；右键返回，鼠标中键回到桌面。默认 Cmd/Alt 是 scrcpy 的快捷键修饰键，Cmd+V 执行显式剪贴板同步与粘贴，Cmd+Q 关闭投屏窗口。以已安装版本 `scrcpy --help` 和官方快捷键文档为准。

一次只让一个操作者写入手机界面。后续控件自动化尚未在本任务安装或接入。

官方文档：https://github.com/Genymobile/scrcpy

本次安装与实机核验记录：`contexts/survey_sessions/2026_10_28_scrcpy_setup/`。
