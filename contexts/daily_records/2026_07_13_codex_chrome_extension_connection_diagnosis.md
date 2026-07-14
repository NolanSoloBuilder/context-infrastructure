# Codex Chrome Extension 连接诊断

日期：2026-07-13

## 现象

Codex 通过 Browser 插件选择本机 Chrome 时返回：

```text
Browser is not available: extension
```

等待 2 秒后重试，结果相同。

## 诊断结果

- Google Chrome 已安装，版本为 `150.0.7871.115`。
- Google Chrome 正在运行。
- Chrome Native Messaging Host manifest 缺失：
  `~/Library/Application Support/Google/Chrome/NativeMessagingHosts/com.openai.codexextension.json`
- 扩展安装状态检查读取 Chrome `Local State` 时收到 macOS `EPERM`。这是需要后续复核的次要问题；manifest 缺失已经足以导致当前连接失败。

重装后再次检查，manifest 仍未生成。ChatGPT/Codex Desktop 日志持续记录：

```text
bundled_plugins_chrome_extension_sync_state_read_failed
EPERM: operation not permitted, scandir '~/Library/Application Support/Google/Chrome'
```

终端可以读取同一目录，而桌面 App `com.openai.codex` 无法读取。由此确认：macOS 对其他 App 数据目录的隐私保护阻断了 Codex 的 Chrome profile 检测和插件安装流程。缺失 manifest 是结果，桌面 App 没有 Chrome 数据目录访问权限才是根因。

## 正确处理方式

不要手工创建 manifest，也不要直接运行插件内部的 manifest 安装脚本。Native Messaging Host 必须由 ChatGPT/Codex 的 Chrome 插件安装流程配置，以保证扩展 ID、host 名称和安装版本一致。

在 macOS `系统设置 → 隐私与安全性 → 完全磁盘访问权限` 中允许 `/Applications/ChatGPT.app`，完整退出并重新打开 ChatGPT/Codex Desktop。随后从 ChatGPT/Codex 插件界面再次安装 Chrome 插件，保持目标 Chrome profile 的窗口打开，再执行 Browser 连接 smoke。

这里必须在授权并重启桌面 App 后重新安装一次。授权前的那次重装已经因 `EPERM` 失败，不会自动补写 manifest。成功标准是 manifest 检查通过、能够取得 Chrome binding，并列出当前打开的标签页。

## 可复用排查顺序

1. 通过 Browser runtime 连接 `extension`，失败后等待 2 秒重试一次。
2. 检查 Chrome 是否安装并正在运行。
3. 检查 ChatGPT Chrome Extension 是否安装、启用，并确认选中的 Chrome profile。
4. 检查 `com.openai.codexextension.json` 是否存在且允许预期扩展 origin。
5. 如果 manifest 缺失或无效，从 ChatGPT/Codex 插件界面重装；不要手工修复。
6. 如果桌面 App 日志出现读取 Chrome 目录的 `EPERM`，先授予 ChatGPT/Codex 完全磁盘访问权限，完整退出并重启 App，再执行插件重装。
7. 重装后进行真实标签页列举 smoke，不能只看文件存在或扩展页面状态。
