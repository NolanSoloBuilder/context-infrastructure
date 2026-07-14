# Cloudflare VPN 旧方案回溯与当前账号审计

日期：2026-07-11

## 结论

之前调研的 Cloudflare 方案是 `Cloudflare Workers/Pages + KV + Edgetunnel2.0`，提供 VLESS/Trojan/Shadowsocks 一类代理节点。它不是 WireGuard/OpenVPN 意义上的 VPN。

当前 Cloudflare 账号没有部署这套方案，因此不存在“已经通过审核”的结论。账号里没有 KV namespace；现有 Worker 代码和绑定也没有出现 `vless`、`trojan`、`shadowsocks`、`edgetunnel`、`wireguard`、`proxyip`、WebSocket upgrade 等实现信号。

Cloudflare 当前 Self-Serve Subscription Agreement 的 2.2.1(j) 仍明确限制使用 Services 提供 VPN 或类似 proxy service。即便技术上能把 Edgetunnel 部署成功，成功 deployment 也不等于 Cloudflare 对该用途完成审核或授权。对当前自助账号，不应继续采用这条路径作为长期自用 VPN。

## 历史方案

2026-05-25 的历史会话比较了两套教程：

1. `Cloudflare Tunnel + Railway + nodejs-argo + VLESS`
2. `Cloudflare Workers/Pages + KV + cmliu/edgetunnel`

当时的判断是第二套链路更短、配置更集中，适合技术试验；两套都把边缘/PaaS 平台用于代理出口，平台条款和长期稳定性不可控。长期使用更适合允许自建 VPN 的正规 VPS，按大陆线路质量选择日本或新加坡节点，WireGuard 作为主通道，必要时准备独立的备用方案。

## 当前 Cloudflare 账号事实

账号 ID：`6405adf943731500c9f0e5401d421722`

### Workers

当前只有 3 个 Worker：

- `cited-alpha-api-proxy`：路由 `api-cited-alpha.forgepane.com/*`
- `forgepane-site`：路由 `forgepane.com/*`、`www.forgepane.com/*`、`xuhao.forgepane.com/*`
- `waffo-cited-alpha-verification`：Waffo challenge 文件验证路由

三个 Worker 的代码和 settings 均未命中代理协议相关关键词，也没有 KV binding。

### Pages

当前只有 `cited-alpha-web`。production deployment 状态为 `success`，自定义域名是 `cited-alpha.forgepane.com`。这是 Cited Alpha Web 部署，与 VPN 方案无关。

### KV

KV namespace 数量为 0。Edgetunnel2.0 教程要求使用 KV 保存管理配置，这一项直接证明该方案未按教程完成部署。

### Cloudflare Tunnel

当前只有 `devspace-context-infra`，状态为 `healthy`。Ingress 为：

- `devspace.forgepane.com` -> `http://127.0.0.1:7676`
- `devspace-read.forgepane.com` -> `http://127.0.0.1:7677`
- fallback -> `http_status:404`

这是 DevSpace MCP 的公网入口，不是 VPN 或代理出口。

## 公网探测

2026-07-11 从当前机器实测：

- `https://forgepane.com/` -> HTTP 200
- `https://cited-alpha.forgepane.com/` -> HTTP 200
- `https://devspace.forgepane.com/healthz` -> HTTP 200
- `https://devspace-read.forgepane.com/healthz` -> HTTP 200
- `https://api-cited-alpha.forgepane.com/` 首次探测 15 秒超时；随后常见 health 路径均快速返回 HTTP 404，说明 Cloudflare 路由和 Worker 能响应，但这些路径不是后端有效 health endpoint。不能用根路径超时单独判定整个 API 部署失败。

## 平台和大陆网络边界

Cloudflare China Network 针对的是把网站内容和安全能力部署到中国大陆，并不是帮助大陆客户端访问境外互联网。官方资料显示它是 Enterprise 单独订阅，由 JD Cloud 运营，并要求每个接入域名具备有效 ICP 备案或许可证。它与 Edgetunnel/WARP/自建代理是不同产品方向。

参考：

- [Cloudflare Self-Serve Subscription Agreement](https://www.cloudflare.com/terms/)
- [Cloudflare China Network](https://developers.cloudflare.com/china-network/)
- [Cloudflare China Network available products](https://developers.cloudflare.com/china-network/reference/available-products/)

## 后续建议

如果目标仍是从中国大陆稳定使用 OpenAI 等 AI 工具，继续沿用此前的正规 VPS 方向：日本或新加坡的独享 VPS、明确允许 VPN、自建 WireGuard、DNS 走隧道，并通过晚高峰多轮实测判断线路。Cloudflare 保留给现有网站、API proxy 和 DevSpace Tunnel，不混入代理用途，避免账号连带风险。

## Google Cloud 自建 WireGuard 可行性补充

2026-07-11 对当前 `gcloud` 账号做了只读核验：

- active account 为 `webxuhao00@gmail.com`。
- active project 为 `cited-alpha-20260701`。
- 该项目已绑定 billing，`compute.googleapis.com` 已启用。
- 当前账号可见的所有 active project 中均没有正在运行的 Compute Engine VM。
- `cited-alpha-20260701` 在东京 `asia-northeast1` 和新加坡 `asia-southeast1` 均有充足的 CPU、实例、static address 和 in-use address quota。
- 当前 default VPC 只有默认 firewall rules，没有 WireGuard UDP 端口规则；默认 SSH/RDP rule 对 `0.0.0.0/0` 开放，不适合作为新 VPN 主机的安全基线。

因此，可以在 Google Cloud 新建 Compute Engine VM 来运行 WireGuard，但不能复用一台现成服务器。架构上应新建独立项目和独立 VPC，不与 `cited-alpha-20260701` 的生产服务共享项目、网络和账单边界。

推荐第一版：

- Region：东京 `asia-northeast1`；新加坡作为后续备份节点。
- VM：Ubuntu 24.04，`e2-small` 起步；只有少量设备和低流量时可降为 `e2-micro`。
- Network：独立 custom VPC，静态公网 IPv4，创建 VM 时启用 `--can-ip-forward`，guest OS 启用 `net.ipv4.ip_forward=1`。
- Firewall：只开放 WireGuard 的单个 UDP 端口；SSH 优先走 IAP，或把 TCP 22 限制到自己的来源 IP。
- Tunnel：WireGuard 地址段使用独立私网 CIDR，例如 `10.66.0.0/24`，服务端做 NAT/MASQUERADE。
- Client：Mac 上建立按需启用的 AI full-tunnel profile。由于本机还存在 REDpass/Yunshu、OpenVPN 和其他 Network Extension，不应让 WireGuard 与公司 VPN 常驻叠加。

优势是拥有独立出口 IP、完整三层隧道、配置和日志可控，并且不依赖 Cloudflare Workers/Pages 的 proxy 用法。限制是 WireGuard 只走 UDP，在中国大陆不同运营商和晚高峰可能受到丢包或 QoS 影响；Google Cloud 的公网 IP 也不等于线路优化节点。

Google Cloud Managed Cloud VPN 只支持 site-to-site IPsec，不支持 Mac/iPhone 这类 client-to-gateway 拨入。本场景应使用 Compute Engine VM 自建 WireGuard，而不是购买 Cloud VPN gateway。

成本的主要部分往往是流量，不是 VM。Google Cloud Premium Tier 发往中国大陆的前 1 TiB 当前标价约为 `$0.23/GiB`，100 GiB 下行约 `$23`，另加 VM、磁盘和公网 IPv4。它适合 OpenAI、Claude、GitHub、Codex 等中低流量用途，不适合把视频和大文件下载全部长期走全隧道。

## 如果坚持使用 Cloudflare

Cloudflare 路径需要分成三类判断：

1. Consumer WARP：技术上会加密设备流量，但出口会匹配用户的近似地理位置，也不能让用户选择日本、新加坡等国家。它不是用于改变访问地区的传统 VPN，因此不能可靠解决“大陆出口访问 OpenAI”这个目标。
2. Cloudflare Zero Trust + dedicated egress IP：官方支持固定出口和选择出口位置，但 egress policies、dedicated egress IP、user-selectable egress IP 均只向 Enterprise 提供。大陆稳定接入还需要 WARP Global Acceleration 和预签协议，属于企业销售方案。
3. Workers/Pages + Edgetunnel/VLESS：技术成本低，但属于把自助 Cloudflare 服务用于 VPN 或类似 proxy。Cloudflare Self-Serve Subscription Agreement 2.2.1(j) 明确限制该用途，deployment success 也不代表 Cloudflare 授权。

当前账号实时状态为 standard account；Zone 使用 Cloudflare Free Plan，另有 R2 Paid subscription，不是 Enterprise。因此当前可执行的官方 CF 路径只有普通 WARP，无法指定受 OpenAI 支持的境外出口；能够实现指定出口的官方 Enterprise 路径需要联系 Cloudflare sales，成本和合同复杂度明显高于一台 Google Cloud VM。

结论：个人自用和 AI 工具访问不选 CF。若企业团队未来需要统一设备策略、固定出口、审计和大陆稳定接入，再评估 Cloudflare One Enterprise + dedicated egress IP + WARP Global Acceleration。

### Edgetunnel2.0 教程复核

2026-07-11 重新读取了教程的 2026-06-20 更新版本和 `cmliu/edgetunnel` 仓库。教程要求：

- 新建 Cloudflare Pages direct-upload 项目。
- 配置 `ADMIN` 管理员变量。
- 创建 Workers KV namespace，并以变量名 `KV` 绑定到 Pages Functions。
- 上传 `edgetunnel-main.zip` 到 production deployment。
- 通过 `/admin` 配置 VLESS/Trojan/SS、ProxyIP、SOCKS5/HTTP 链式代理、优选 IP 和订阅。
- 可向面板填写 Cloudflare Account ID/API Token 读取请求额度。
- 教程还建议使用多个账号叠加免费请求额度。

这些功能明确构成 VPN 或类似 proxy service，不属于普通 Pages 网站或反向代理。当前 Cloudflare Self-Serve Subscription Agreement 2.2.1(j) 与该用途直接冲突；多账号叠加额度还会增加规避平台限制的风险。因此不应在承载 Cited Alpha、Forgepane、DevSpace 和 R2 的现有账号中执行，也不应把换一个账号当成合规解决办法。

## StrongVPN 当前慢速问题的现场基线

2026-07-11 只读采样时，WireGuard 网络服务 `str-lax311` 处于 disconnected，默认路由走 Wi-Fi `en0`。直连出口定位在新加坡，Cloudflare colo 为 `SIN`，`warp=off`。五轮请求中：

- OpenAI API 未鉴权探测总耗时约 `0.41-0.52s`。
- ChatGPT 首页首包和总耗时约 `0.20-0.21s`。
- Claude 首页总耗时约 `0.22-0.27s`。

`str-lax311` 的节点标识指向 Los Angeles。当前网络本身已经从新加坡出口，开启洛杉矶 StrongVPN 会让亚洲到 AI/CDN 的流量绕行美国西海岸。因此当前高概率瓶颈是 StrongVPN 节点选择和跨太平洋路径，而不是 WireGuard 协议本身。

下一步应先在 StrongVPN 中改用日本东京或新加坡 WireGuard 节点，再按相同的 DNS、TCP connect、TLS、TTFB、total 指标做 A/B。只有东京/新加坡节点仍然显著慢，才值得新建 Google Cloud WireGuard；Cloudflare Edgetunnel 不能解决底层节点和线路质量问题。
