# Clash 当前分流检查

2026-10-16，通过当前内核 Unix socket 的只读 API 与 `scutil --proxy` 核查；未修改设置或生成节点。

- 内核运行于 rule 模式，StrongVPN 选择新加坡 str-sin303，共 12 节点。
- UU 的四条进程名与三条域名后缀 DIRECT 规则排列在最前，已加载；当前命中计数为 0，不能证明真实 UU 会话已命中。
- MetaCubeX meta-rules-dat 的 private-domain/private-ip/cn-domain/cn-ip 四个 HTTP MRS 规则集已加载，规则数依次为 130、18、110821、10008；更新间隔 86400 秒，最近更新时间为 2026-10-15 19:55（北京时间）。
- 国内域名及 IP 规则已有运行期命中，其他流量由末尾 MATCH 交给 StrongVPN；MATCH 也已有命中。
- 当前系统代理、PAC、TUN 均关闭。故上述策略适用于实际进入 Clash 的流量，不能宣称整机其他流量已全部经过 StrongVPN。

如用户希望普通应用遵循该策略，需要开启系统代理；不遵循系统代理的应用还需单独配置或另行决定是否采用 TUN。此次仅检查，没有代为开启。
