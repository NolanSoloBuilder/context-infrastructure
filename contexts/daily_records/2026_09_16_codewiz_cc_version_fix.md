# codewiz-cc 版本拒绝排查

2026-09-16，本机请求被服务端以 403 拒绝，提示客户端 0.0.34 过低。重新登录不能消除版本门禁。

## 实测证据

- `/opt/homebrew/bin/codewiz-cc` 指向 Homebrew 全局 `@xhs/codewiz-cc`，原版本 0.0.34。
- 交互式登录 zsh 优先解析 fnm Node v22.22.0 的全局命令，原版本 0.0.46，安装前缀为 `/Users/xuhao/.local/share/fnm/node-versions/v22.22.0/installation`。
- 公司 npm 源查询到 `latest` 与 `release` 均为 0.0.53。
- 包源码将自身 VERSION 写入 `X-Adapter-Source-Version`，默认适配器来源为 `codewiz-cli`。因此错误中的 codewiz-cli 不意味着应安装另一个同名包。

## 修复及验收

对两套 Node 全局前缀安装 `@xhs/codewiz-cc@0.0.53`，避免不同 shell 调用不同版本。保留现有配置及用户会话。

Homebrew 与 fnm 两个入口版本均回读为 0.0.53，随后分别在 `/tmp` 使用 `--safe-mode --tools '' --no-session-persistence` 发起最小请求，均返回 `OK`，`is_error=false`，`api_error_status=null`。该检查证明两个入口的版本门禁和模型请求已恢复；未验收原会话中的三个 MCP setup warnings。

复用步骤：先比较非交互 shell 与 `zsh -lic 'whence -a codewiz-cc; npm prefix -g'`，再对实际前缀升级，最后启动新进程发起真实请求。已经运行的旧进程需要退出后重新启动。
