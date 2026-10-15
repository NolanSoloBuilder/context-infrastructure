# StrongVPN 全目录节点配置导出

用户要求导出其账户对应的所有节点文件。本次从 StrongVPN 实时 `servers.js` 读取 53 个节点，覆盖 34 个国家或地区；逐节点串行调用生成接口，每个节点最多一次 POST，未自动重试。

结果：47 个节点成功生成、校验并保存 `.conf`，6 个失败，0 个遗漏或未尝试。失败节点为：

| 节点 | 位置 | 返回状态 |
| --- | --- | --- |
| `str-yul301` | Montreal, Canada | HTTP 400 |
| `str-yul303` | Montreal, Canada | HTTP 400 |
| `str-yvr303` | Vancouver, Canada | HTTP 400 |
| `str-dxb303` | Dubai, UAE | HTTP 400 |
| `str-gla301` | Glasgow, UK | HTTP 400 |
| `str-lon301` | London, UK | HTTP 503 |

私人产物位于 Git 仓库外：`~/.local/share/strongvpn-node-optimizer/exports/all-nodes-2026-10-15T07-04-02-021Z.zip`。压缩包包含 47 份配置、`nodes.csv`、`export_report.json`、使用说明。目录权限 `0700`，配置、报告、ZIP 及其内部文件权限 `0600`。

已核验节点 ID 无重复、总数闭合、47 份非空配置结构与密钥格式、ZIP CRC 及解压字节一致性；失败未留下空配置。未连接或切换 VPN，未验证节点连接质量。生成可能更新服务端公钥关联；接口失败原因未得到进一步证实。

配置和私钥只保留在上述私人数据目录，仓库文档不记录凭据、私钥、配置正文或服务端响应正文。

后续[保留策略核查](../survey_sessions/2026_10_15_strongvpn_wireguard_config_retention.md)发现标准 `wg.*` 生成器有超过 12 份淘汰旧配置的官方规定，但 AIO `tools.*` 是否适用尚未得到公开证据确认。本批 47 份仅确认生成与落盘，不能视为全部仍有效，也不能断言只剩最后 12 份有效。

## 既有配置验证与 Clash Verge 导入

用户随后授权测试上述 47 份既有配置，明确禁止重新生成，并要求导入新安装的 Clash Verge。已完成：

- 原样读取 47 份 `.conf` 转成 Mihomo WireGuard 出站；没有调用生成接口、生成密钥或读取账户密码。原配置测试前后的 SHA-256 全部一致。
- 使用 Clash Verge v2.5.8 / Mihomo v1.19.32，从应用的本地配置入口导入并激活；`mihomo -t`、真实代理页和内核 Unix socket API 均确认 47 个节点已载入。
- 每个节点分别通过内核 URL 测试请求 `https://1.1.1.1/cdn-cgi/trace` 与 `https://www.gstatic.com/generate_204`，每目标超时 8 秒，并发 2。12 个节点均通过两个 HTTPS 目标；其余 35 个均未通过。本次观察为超时，不能仅据此把每个失败都定性为服务端撤销。
- 通过的节点集合恰好等于本次导出顺序的最后 12 份。该结果符合 12 份保留政策的表现，但不取代服务端策略确认。
- Clash 默认 `StrongVPN` 组优先列出通过测试的 12 个节点，选择新加坡 `str-sin303`；另保留 `全部节点（47，含超时）` 分组，未删除其他原配置。
- 激活后经 `127.0.0.1:7897` SOCKS5 请求固定 IP HTTPS，返回 HTTP 200。系统代理和 TUN 均保持关闭，默认出口仍为 `en0`，REDpass 持续运行。

通过的节点为：`str-sin303`、`str-sel302`、`str-lon302`、`str-zrh302`、`str-bhx302`、`str-lax311`、`str-sto303`、`str-man301`、`str-mad301`、`str-mad302`、`str-ist303`、`str-dal301`。

私人数据目录中增加 `existing-node-validation.json`、`节点有效性测试.csv`、`strongvpn-clash-47.yaml`，均为 `0600`。后者包含连接私钥，未进入仓库。Clash 安装配置与运行配置也设为 `0600`。

测试准备期间从 wireproxy 官方 v1.1.3 release 下载并验证 SHA-256，将二进制放在全局 Node prefix 的 `bin`；随后用户安装 Clash，实际测试使用其现有 Mihomo 内核。wireproxy 未启动隧道或代理进程，没有常驻任务。

用户随后要求删除超时节点。已从 Clash 当前配置中移除 35 个未通过节点及含超时的备用组，仅保留 12 个已验证节点；配置名改为 `StrongVPN · 12 可用节点`，重新激活后 UI 和内核 API 均确认只剩 12 个 WireGuard 节点、单个 12 项选择组，当前仍选新加坡。系统代理和 TUN 开关保持原状。原始 47 份导出与删除前配置备份保留在私人目录，另导出 `strongvpn-clash-12.yaml`；未重新生成节点。

用户咨询能否自建订阅链接：Clash Verge 官方支持远程订阅 URL 和本地配置导入；当前安装的是本地配置，尚未部署订阅服务。可由用户自己的 HTTPS 服务提供现有 12 节点 YAML，客户端更新订阅时只读取该文件，避免每次拉取触发 StrongVPN 新密钥注册。订阅文件包含 WireGuard 私钥，应作为私人配置提供；没有授权发布到任何远程服务。依据：[Clash Verge 官方订阅导入文档](https://www.clashverge.dev/guide/profile.html)。此处仅解释能力与方案，没有创建 URL 或修改现有客户端配置。

用户进一步询问能否放在自己的阿里云 VPS。只读检查确认本机已有 `aliyun` CLI、OAuth profile `beamjoin-deploy`，在 `cn-hongkong` 查询到 1 台 Running 且有公网地址的 ECS。尚未登录服务器、检查 Web 服务或上传配置。候选方案是复用该机 HTTPS 服务，提供带随机访问令牌的私人订阅地址，只返回现有 12 节点 YAML；VPS 承担配置分发，实际代理流量仍连接 StrongVPN 节点。现有 HTTPS 域名、Web 服务和准确部署路径仍待确认，不能把候选方案当作已部署服务。

用户随后授权部署私人订阅，并说明客户端会同时使用。方案讨论中需区分订阅拉取与隧道连接：先后拉取同一 YAML 不会产生独立客户端身份；两台设备同时使用同一份 WireGuard 节点配置连接同一服务端，会复用同一公钥身份，服务端记录的最近来源端点可能来回变化，造成连接干扰。[WireGuard 官方机制说明](https://www.wireguard.com/#built-in-roaming)记录了按最近认证端点回包的行为；[StrongVPN FAQ](https://support.strongtech.org/hc/en-us/articles/360037444953-WireGuard-FAQ)明确要求每设备独立配置。同一地点可以使用不同、已注册的配置，地点相同本身不是冲突原因。

集中管理仍可成立：在 VPS 维护一套配置清单，为设备提供不同配置内容。仅更换订阅 URL 而复用同一密钥，不能隔离客户端身份。遵守用户不重新生成的限制，当前只能在现有 12 份有效配置中分配；设备数与分配方式尚未确定，未分配配置、上传私钥或改动 Clash 当前订阅。部署授权已获得，部署尚未完成。

## 四台设备配置与私人订阅上线

用户确认要四份设备配置。已将既有 12 个通过测试的节点按时延排序轮流分成四份，每份 3 个，未调用 StrongVPN 生成接口、未登记新公钥，也未重新导出节点：

| 配置 | 默认节点 | 另两个节点 |
| --- | --- | --- |
| 设备 1（当前 Mac） | `str-sin303` | `str-bhx302`、`str-mad301` |
| 设备 2 | `str-sel302` | `str-lax311`、`str-mad302` |
| 设备 3 | `str-lon302` | `str-sto303`、`str-ist303` |
| 设备 4 | `str-zrh302` | `str-man301`、`str-dal301` |

四份 YAML 均通过 Mihomo `-t`；组引用闭合，合计 12 个节点及 12 个私钥互不重复，源配置哈希未变。私人交付目录是 `~/.local/share/strongvpn-node-optimizer/subscriptions/four-devices-2026-10-15/`，包含 `device-1.yaml` 至 `device-4.yaml`、`README.md`、完整私人链接说明 `订阅链接.md` 和六文件压缩包 `strongvpn-four-devices.zip`。目录为 `0700`，文件和 ZIP 内文件为 `0600`，ZIP CRC 通过。链接、令牌、配置正文不写入仓库。

已在授权的香港 ECS 复用现有 Caddy v2.11.7 HTTPS origin，创建四个独立的 32 随机字节令牌路径，每个路径只支持 GET/HEAD 并返回对应设备文件。静态文件在 `/etc/forgepane/caddy/strongvpn/files/device-N.yaml`，精确路由在同目录上层 `routes.inc`，经现有共享目录只读挂载进入容器。没有新增后端、DNS 或公网端口。

线上主配置实际绑定 `/opt/beamjoin/operations/20261011-shared-pg-2c9028d0b604/infra/vps/Caddyfile`，并非 operations/current 路径。只在 origin 站点内新增一行 `import /etc/caddy/shared/strongvpn/routes.inc`；候选 `caddy validate` 成功，适配配置对比确认除了四个新互斥 handle 及其分组，原有站点、API origin-token 守卫与其他配置等价。保留 bind mount 原 inode 原地写入并 fsync，确认容器内哈希一致后发送 SIGUSR1。Caddy 的 PID 与启动时间均未变化，日志确认从文件重载成功；没有重启业务或代理容器，也没有启用 admin API。

公网验收确认四个 GET/HEAD 均 HTTP 200，GET 字节哈希分别与对应本地 YAML 一致，响应为 YAML 并带 `Cache-Control: private, no-store`、no-referrer、noindex、nosniff。直接文件路径、目录路径、错误令牌、令牌与设备错配均 404；原 origin API 缺少来源凭据仍 403，服务器本机 API health 仍 200。现有全局 URI 日志过滤与 `persist_config off` 保留；配置目录 `0700`、文件 `0600`，未启用目录浏览。

当前 Mac 已通过 Clash Verge 的远程订阅入口导入并激活 `StrongVPN · 设备 1 · 3 节点`。真实代理页和内核 API 均确认只有设备 1 的 3 个节点，选中新加坡；经现有 SOCKS 端口请求固定 IP HTTPS 返回 200。远程 URL 与设备 1 清单一致，客户端自动更新开启、间隔 1440 分钟。系统代理保持关闭；原本地 12 节点配置保留为未激活备份，不应再与其他设备同时启用。

更新文件时，在服务器同目录以 `0600` 写入新文件后原子替换 `device-N.yaml`，客户端更新订阅即可，文件内容变化不需要重载 Caddy。修改令牌路由才需要配置验证及重载；后续运维发布须保留订阅 import 和日志过滤。服务器私人 `README.md` 记录了路径与更新方法；部署前主配置和回执保留在 root 私人备份目录。临时 SSH 公钥通过阿里云云助手下发，仅用于本次部署，完成后按完整公钥精确移除并核对其他授权行保留，本机临时私钥和服务器暂存配置副本均已清除。

## 用户改为单份共用订阅

用户明确取消四份分组，要求合成一份。已恢复为完整 12 节点的单一手动选择组，复用全部原密钥，未调用生成接口。统一 YAML 与原 12 节点源文件逐字节一致，且与四份分组的节点合集逐字段一致；Mihomo `-t` 通过。

当前有效交付目录改为 `~/.local/share/strongvpn-node-optimizer/subscriptions/unified-2026-10-15/`，包含 `strongvpn.yaml`、`README.md`、唯一私人链接说明 `订阅链接.md` 和 `strongvpn-unified.zip`。文件保持 `0600`、目录 `0700`，ZIP CRC 通过。私人主清单标识为 unified，旧清单及四份本地文件作为历史保留，旧链接说明已标记停用。

VPS 当前只服务 `/etc/forgepane/caddy/strongvpn/files/strongvpn.yaml`，使用一个新随机令牌的精确 GET/HEAD 路由。旧四个远程 URL 已撤下并逐个确认返回 404，旧文件与路由保留在服务器私人 `history/four-devices-20261015/`。新 URL 的 GET/HEAD 均 200，下载哈希与本地源一致，private/no-store 响应保留；直接文件、目录和错误令牌均 404，原 API 鉴权仍 403。仅原子替换订阅 routes.inc 并通过验证后 SIGUSR1 重载，主 Caddyfile 无变化、Caddy PID 和启动时间不变、服务器本机 API health 200。

本机现有远程订阅已更新 URL、名称和内容为 `StrongVPN · 12 节点 · 统一订阅`，不额外新增重复远程订阅。刷新并重新激活后，真实代理页和内核 API 都确认 12 个 WireGuard 节点与 12 项选择组；本次保留的选择是首尔 `str-sel302`，SOCKS HTTPS 实测返回 200，客户端缓存配置哈希与统一文件一致。系统代理与 TUN 均保持关闭，自动更新间隔保留 1440 分钟。

统一订阅让各设备看到相同的完整节点列表，并未提供每设备独立密钥。已告知用户多设备同时使用应选不同节点，同一配置并发仍可能互相干扰；私人使用说明补充了全节点测速也会使用密钥。后续只需替换 strongvpn.yaml，客户端更新订阅即可。此次临时 SSH 公钥、私钥与服务器暂存配置副本也已清理，其他登录授权保留。

用户要求沉淀下次可直接触发的完整流程，已新增[StrongVPN 节点下载、转换与 VPS 订阅更新](../../rules/skills/strongvpn-node-optimizer/references/subscription_workflow.md)，并登记到 Skill 入口、技能索引与 WORKSPACE 路由。工作流区分“更新订阅”复用既有配置与“重新下载节点并更新订阅”注册新密钥，覆盖字段转换、最终合集验证、保持原 URL 的原子发布、客户端刷新与回滚/临时授权清理。文档不包含真实账号密码、私钥或订阅令牌；本次仅整理文档，没有再次下载或修改 VPS。
