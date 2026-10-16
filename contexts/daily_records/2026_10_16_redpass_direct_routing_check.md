# RedPass 与 Clash DIRECT 的只读检查

2026-10-16：未改动配置，未启停 RedPass、Clash 或隧道。

系统 HTTP/HTTPS/SOCKS/PAC 均关闭；RedPass 主程序及 Daemon/Agent 正在运行。系统存在活动 utun0、大量指定目标路由与补充 DNS；普通默认路由仍在物理网络接口。表现为按目标接管的隧道/路由分流，而不是仅依赖系统 HTTP 代理。没有取得 utun0 与 RedPass 守护进程的直接文件描述符归属证据，进程共存本身不作为归属证明。

通过系统解析 www.xiaohongshu.com，并对返回 IPv4 地址执行 route get，实际出口为 utun0；百度作为对照走 en0。当前 Clash 运行文件没有强制 interface-name 或自定义 DNS 配置。因此该域名的 DIRECT 连接按当前系统解析与路由仍可进入现有公司隧道路径，不会因 DIRECT 自动绕过它。

边界：只覆盖当前 www.xiaohongshu.com 的解析结果，未证明所有小红书 CDN/内部域名都走同一接口；未验证公司内部鉴权、页面登录或应用身份策略。若后续使用 TUN、强制网卡或不同 DNS，应重新验证实际路径。
