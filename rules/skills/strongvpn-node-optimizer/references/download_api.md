# StrongVPN WireGuard 下载接口

2026-10-15 从用户提供的两个公开下载页源码核对，并通过真实日本节点下载验证。脚本为 `scripts/strongvpn-download.mjs`，共享入口为 `scripts/strongvpn-node-optimizer.mjs` 的 `servers` / `download` 命令。

## 来源

- https://tools.strongvpn.asia/share/strong-wg/strong-wg.html
- https://tools.strongtech.org/share/strong-wg/strong-wg.html

两个站点使用相同路径和字段；不需要浏览器 session 或 Cookie。

## 节点目录

`GET /share/strong-wg/servers.js`

这是 JavaScript 数据模块，包含 `servers`（国家到节点 ID / label 列表）和 `serverMapping`（节点 ID 到 `atob(...)` 编码 IP）。用有限语法解析器读取，禁止 `eval` 或直接执行远端模块。节点目录可能变化，每次下载先读取实时目录。

## 生成接口

`POST /wg-generate`，位于站点根路径，`Content-Type: application/json`。

请求结构（占位符，不填写真实凭据到文档）：

```json
{
  "aiouser": "<AIO username>",
  "aiopass": "<AIO password>",
  "server": "<server ID from servers.js>",
  "publickey": "<locally generated X25519 public key in base64>"
}
```

成功响应读取：

| 字段 | 类型 | 用途 |
| --- | --- | --- |
| `success` | boolean | 必须为 `true` |
| `config.Interface.Address` | string | 隧道地址，可为逗号分隔的 CIDR |
| `config.Interface.DNS` | string[] | DNS IP 地址 |
| `config.Peer.PublicKey` | string | 服务端 WireGuard 公钥 |
| `config.Peer.AllowedIPs` | string[] | 路由 CIDR，遵循返回值 |

本机生成 X25519 密钥对，只发送公钥；私钥留在最终 `.conf` 中。页面和脚本均以目录 IP 及随机 `55000–60000` 端口构造 Endpoint，不使用响应中的 Endpoint。脚本校验地址、公钥和 CIDR，防止返回内容插入配置指令。

生成请求可能登记新的服务端公钥关联；公开源码未说明对已有配置的影响。禁止自动重复提交或跨镜像重试 POST；超时属于结果未知，先核查再决定是否重试。错误只输出固定说明和 HTTP 状态码，不回显响应正文、凭据或完整配置。

配置下载成功仅证明接口可用和文件已保存；连接质量、握手和 AI 服务可达性需要另行测速。

## 重复生成与保留策略（2026-10-15 核查）

官方 [WireGuard FAQ](https://support.strongtech.org/hc/en-us/articles/360037444953-WireGuard-FAQ)（2021-05-14 更新）写明标准生成器超过 12 份配置会删除最旧一份，与节点地区无关。但该文使用 billing 凭据和 `wg.*` 入口，不能直接认定它覆盖 AIO `tools.*` 接口。

官方 [AIO Android 设置指南](https://support.strongtech.org/hc/en-us/articles/36398492287771-Setting-Up-VPN-on-Android-via-WireGuard-App-in-China)（2026-09-24 更新）明确两个入口、凭据不同，允许不同服务器的多个配置；没有说明 AIO 配置上限、固定过期时间或同节点重复生成是否替换旧公钥。

当前 `download` 每次都会创建新密钥并注册公钥。优先复制或复用已有配置；批量生成前核对当前保留政策。不能承诺全量导出文件同时有效，也不能未经确认将 AIO 配置套用为只保留最后 12 份。完整证据见工作区 `contexts/survey_sessions/2026_10_15_strongvpn_wireguard_config_retention.md`。
