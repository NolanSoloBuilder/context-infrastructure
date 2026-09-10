# 163 邮箱 MCP

## 用途

通过本机 MCP 连接个人 `@163.com` 邮箱，支持搜索、读取、发信、保存草稿、移动、归档、标记、删除和附件下载。

## 选型

- 实现：[`Wh1isper/mcp-email-server`](https://github.com/Wh1isper/mcp-email-server)
- 当前固定版本：`1.3.2`
- 安装方式：`uv tool install mcp-email-server==1.3.2`
- 本机入口：`/Users/xuhao/.local/bin/mcp-email-server`
- Codex MCP 名称：`netease-mail`

选择依据：该项目使用真实 IMAP/SMTP，具备持续 release、测试、安全文档、macOS Keychain、MCP tool annotations、IMAP ID、结果大小限制和明确的失败状态。不要使用 `guangxiangdebizi/email-mcp` 作为 163 收信方案；该仓库的读取、搜索和删除实现依赖 Gmail API，163 配置只覆盖 SMTP 发信。

MCP 官方没有发布通用 IMAP/SMTP 邮箱服务器。MCP 官方 Registry 收录的是社区发布物，收录本身不代表安全审计。

## 首次配置

1. 在 163 网页邮箱中开启 IMAP/SMTP，并生成独立客户端授权码。聊天中出现过的授权码应立即撤销。
2. 运行：

   ```bash
   mcp-email-server ui
   ```

3. 只在本机管理页面输入完整邮箱地址和新授权码。macOS 下凭证必须进入系统 Keychain，不写入仓库、Codex 配置、shell history 或聊天。
4. 保存后执行 `mcp-email-server config doctor`，再通过 MCP 调用 `list_available_accounts`。
5. 分别做 IMAP 只读 smoke 和 SMTP 发信 smoke。测试邮件只发给用户自己；删除测试只操作专门创建的测试邮件。
6. 163 会在服务器端自动保存已发送邮件。将账户的 `save_to_sent` 设为 `false`，避免 MCP 再追加一份而产生重复留档。

## Codex 配置

全局配置位于 `/Users/xuhao/.codex/config.toml`：

```toml
[mcp_servers.netease-mail]
command = "/Users/xuhao/.local/bin/mcp-email-server"
args = ["stdio"]
startup_timeout_sec = 20
```

修改 MCP 配置后需要重启 Codex，并在新任务中确认工具可见。当前任务看不到工具时，依次核对：固定版本是否安装、stdio 握手与 `tools/list`、Codex 配置、重启后的任务可见性。

## 操作边界

- 搜索、列目录、读取正文默认属于只读操作；读取正文时保持 `mark_as_read=false`，除非用户要求改为已读。
- 发信、回复、转发会产生对外影响。执行前核对收件人、主题、正文和附件，并以用户当前请求作为授权边界。
- 删除、移动、覆盖附件属于破坏性操作。先用元数据搜索锁定准确的邮箱目录和 `email_id`，再向用户确认当次目标。
- 不自动重试结果不明确的发送、保存草稿、移动或删除操作，避免重复邮件和重复副作用。
- 附件默认只列元数据。下载时使用用户指定的精确目录，并避免覆盖现有文件。

## 更新与卸载

更新前先检查 GitHub release、PyPI 版本、变更说明和 credential/storage 迁移要求。确认后固定到明确版本：

```bash
uv tool install --force mcp-email-server==<version>
```

更新后重新执行 stdio `initialize`、`tools/list`、`config doctor` 和最小 IMAP/SMTP smoke。

卸载前先从 Codex 配置移除 `mcp_servers.netease-mail`，再运行项目提供的账户/凭证清理流程，确认 Keychain 中没有遗留凭证，最后执行：

```bash
uv tool uninstall mcp-email-server
```
