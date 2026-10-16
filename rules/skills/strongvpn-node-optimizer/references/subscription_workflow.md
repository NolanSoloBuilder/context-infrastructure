# StrongVPN 节点下载、转换与 VPS 订阅更新

适用：在当前项目继续维护用户的 StrongVPN → WireGuard `.conf` → Mihomo/Clash YAML → 阿里云 HTTPS 私人订阅。最后核对：2026-10-16。本文记录可复用流程和已验证的部署结构；账号、私钥、令牌与完整订阅 URL 留在 Git 外。

## 下次如何触发

- **“重新下载我的 StrongVPN 节点并更新订阅”**：重新获取当前选定节点的配置，转换、测试、剔除未通过节点、更新现有 VPS 文件，再刷新本机 Clash。
- **“更新 StrongVPN 订阅”**：默认复用现有配置，验证后重新发布；不把“更新”直接解释为重新注册密钥。
- **“只测试现有节点，不要重新生成”**：不调用生成接口，不运行 `download` 或 `benchmark`。

执行上述任务时，沿当前清单与既有服务器继续，不重复询问账号、服务器位置、文件格式或是否拆成四份。缺少凭据或目标与本文不一致时，先完成可做的本地准备，再说明具体缺口。本文本身不是定时任务，不会自动运行。

用户最终选择是：**一份共用订阅，所有客户端看到完整节点列表，保留同一个订阅链接**。不要恢复已取消的四设备拆分。多设备同时用同一节点配置仍可能互相干扰；选择不同节点可以减少冲突，全节点测速也会使用密钥。

## 1. 当前真源与定位顺序

下表是路径和非秘密定位信息，不是需要复制的秘密值。每次先验证文件和资源仍存在。

| 内容 | 位置或标识 |
| --- | --- |
| 项目 Skill 源码 | `rules/skills/strongvpn-node-optimizer/` |
| 全局入口 | `~/.codex/skills/strongvpn-node-optimizer/`，当前链接到项目目录 |
| StrongVPN 凭据 | macOS Keychain service `strongvpn-node-optimizer`；由脚本在进程内读取 |
| 私人数据根目录 | `~/.local/share/strongvpn-node-optimizer/` |
| 当前订阅主清单 | `deployment-20261015/subscription-manifest.json`，`mode=unified`，`subscriptions` 数组只有一项 |
| 当前统一清单镜像 | `deployment-20261015/unified-manifest.json`；含 `host/path/url/file/sha256` |
| 当前本地统一文件 | `subscriptions/unified-2026-10-15/strongvpn.yaml` |
| 当前用户链接说明 | `subscriptions/unified-2026-10-15/订阅链接.md` |
| 单节点更新后的原生配置覆盖表 | `subscriptions/unified-2026-10-15/node-sources.json`，若存在；只记录最新替换 `.conf` 路径及哈希 |
| 原始导出及测试报告 | `exports/all-nodes-2026-10-15T07-04-02-021Z/` 中 `.conf`、`export_report.json`、`existing-node-validation.json` |
| Clash 安装位置 | `/Applications/Clash Verge.app` |
| Clash 数据目录 | `~/Library/Application Support/io.github.clash-verge-rev.clash-verge-rev/` |
| 阿里云 CLI 身份 | 本机 `aliyun` OAuth profile `beamjoin-deploy`，区域 `cn-hongkong` |
| ECS 实例 | `i-j6ccwyr58wuqxn9f8cqi`；公网地址每次从 API 查询 |
| HTTPS 主机 | `beamjoin-origin.forgepane.com`；准确令牌路径从私人清单读取 |
| VPS 当前订阅文件 | `/etc/forgepane/caddy/strongvpn/files/strongvpn.yaml` |
| VPS 路由及说明 | `/etc/forgepane/caddy/strongvpn/routes.inc`、`README.md` |
| Caddy 容器 | `beamjoin-origin-proxy-1`，目前 v2.11.7、host 网络、`admin off`、`persist_config off` |
| Caddy 主文件的实际 bind 源 | `/opt/beamjoin/operations/20261011-shared-pg-2c9028d0b604/infra/vps/Caddyfile`；以本次 `docker inspect` 为准 |

读取私人 JSON 时只输出字段名、节点 ID、数量、路径或校验结果。不要 `cat` 清单、完整 YAML、`.conf`、Keychain、`~/.aliyun/config.json` 或服务器运行环境文件。

链接恢复顺序：主清单 → 统一清单镜像 → 当前 Clash 远程订阅条目的 `url` → 私人链接说明 → 服务器 `routes.inc`。在程序内相互核对。主清单与镜像不一致时，先对照客户端和服务器实际响应，不能凭某个旧文件覆盖现网。`subscription-manifest.four-devices-backup.json`、`four-devices-*` 和服务器 `history/` 都是历史，不能用它们恢复当前链接。

## 2. 准备本次批次

本步骤不改变网络和远端密钥。

1. 读取 [SKILL.md](../SKILL.md) 和 [下载接口契约](download_api.md)，核对本次意图是否允许重新生成。
2. 从当前统一 YAML 读取节点 ID和名称，核对私人清单和线上文件哈希；从运行中 Mihomo 的 `GET /proxies/StrongVPN` 读取并保存 `now` 作为更新前选择。静态 YAML 的节点顺序不是运行态选择。当前基线是 12 节点，后续应以实际文件为准。
3. 在私人根目录建立新的 `runs/<UTC时间戳>/`，保存本次目录、输入配置哈希、目标节点列表、结果和候选文件。不要覆盖原始下载文件。
4. 备份当前本地与服务器已发布文件，记录其 SHA-256。目录 `0700`，文件、报告、ZIP 内文件 `0600`。
5. Node.js 20+ 用于下载；转换/清单可用本机 `uv run --with pyyaml --no-project python`。复用现有 Mihomo，不为配置更新安装或升级客户端，不启动全量构建。

需要重新生成并发布时，先对现有订阅做 [只读 HTTPS 预检](local_tools.md#只读-https-预检与发布后验收)，确认输入/线上哈希、证书信任通道及既有 VPS 身份可用，再注册新密钥。若只要求复制 `.conf` 或维护 Skill，不建立远端临时授权。历史调查/运行记录链接属于当前工作区的证据，安装到其他环境后缺失时不阻塞执行；操作合同仍以本 Skill、私人清单和实时状态为准。

```zsh
strongvpn_skill="$HOME/.codex/skills/strongvpn-node-optimizer"
strongvpn_run_dir="$HOME/.local/share/strongvpn-node-optimizer/runs/$(date -u +%Y%m%dT%H%M%SZ)"
umask 077
mkdir -p "$strongvpn_run_dir"
node "$strongvpn_skill/scripts/strongvpn-node-optimizer.mjs" servers --json > "$strongvpn_run_dir/catalog.json"
```

目录读取先 GET 当前下载网页，再跟随页面实际 module import，允许备用来源但不合并镜像。**网页真实下拉框的可选项决定候选边界**：排除占位项、禁用/隐藏选项和禁用组。每次核对页面结构；页面/目录改变、解析集合有疑问或要全量生成时，读取真实 `select#serverSelect` 的 option values，与 CLI ID 集合逐项对照，不一致先停止生成。相关公开证据见[下拉框与请求核对](../../../../contexts/survey_sessions/2026_10_15_strongvpn_dropdown_audit.md)。

本次目标是下拉框可选集合与用户指定节点/地区的交集；普通订阅维护继承当前统一订阅的选定集合，不因目录有更多节点就默认重新生成全部目录。某个 ID 消失时记录缺失，结合用户指定地区处理，不猜测 IP。记录可选数、目标数、尝试数、生成成功数和最终连接通过数，避免把上次的“53 个选项、47 次生成成功、12 份通过验证”当成同一个数量。

### 单个节点故障与条件重建

用户要求“先看节点是否失效，必要时下载新密钥并更新订阅”时，先对该节点的旧配置测试两个固定 HTTPS 目标，并用一个其他节点作对照。目标失败且对照正常，可以执行用户已授权的单节点重新生成；超时不能证明由多设备共用或密钥撤销导致。目标仍可用时先查设备共用/客户端状态，不无故重新注册。

只对明确的目标 ID 提交一次生成 POST。新的配置通过隔离测试后，从**当前统一 YAML**复制完整候选，仅替换这个节点的连接字段，保留名称、组引用、其他节点、四个 MetaCubeX provider 与 UU 例外。逐字段断言其他节点和非 proxies 顶层配置不变。订阅 URL 保持原值，按正常原子发布与客户端刷新流程完成。

单节点续建后，原全量导出中的同名 `.conf` 可能已是旧密钥。将新 `.conf` 的私人路径/哈希写入 `subscriptions/unified-2026-10-15/node-sources.json` 的 `overrides[节点ID]`；后续交付原生文件先查此表，再查原始导出，最终都必须与当前 YAML 的密钥及连接字段匹配。不能凭旧导出文件名覆盖回已更新节点。表中没有的节点继续沿用原始导出；当前 YAML 及线上哈希仍是订阅内容真源。

换密钥不会为共用订阅产生每设备独立身份；所有设备刷新同一订阅后仍共用对应条目。验证后提示其他设备刷新原链接，并在同时使用时选择不同节点。2026-10-16 新加坡 `str-sin303` 已按本流程单独更新，其他 11 个节点字段保持原值；记录见[新加坡修复](../../../../contexts/daily_records/2026_10_16_strongvpn_singapore_repair.md)。

## 3. 下载节点：仅在要求重新下载时执行

**`download` 会生成新的 X25519 密钥并向 StrongVPN 登记公钥，不是读取已有配置。** 客户端拉取订阅只是 GET 静态文件，不触发这一步。

标准 `wg.*` 入口的 [StrongVPN FAQ](https://support.strongtech.org/hc/en-us/articles/360037444953-WireGuard-FAQ)记载超过 12 份淘汰旧配置。AIO `tools.*` 的适用性没有公开确认；2026-10-15 本账户导出 47 份后，仅最后 12 份通过测试。因此默认只处理当前选定集合，不声称一次导出全目录就能全部长期有效。详见[保留策略调查](../../../../contexts/survey_sessions/2026_10_15_strongvpn_wireguard_config_retention.md)。

重新下载前简短说明可能影响既有配置。用户明确要求重新下载时，继续执行授权的流程，无需对每个节点重复确认。**文件备份不能恢复被提供方淘汰的服务端密钥**，不能承诺生成失败后恢复旧文件就一定恢复连接。

逐节点串行执行，目标 ID 必须来自本次目录：

```zsh
node "$strongvpn_skill/scripts/strongvpn-node-optimizer.mjs" download str-sin303 \
  --output "$strongvpn_run_dir/str-sin303.conf" --json
```

上例只是单节点命令，不代表每次只下载新加坡。按本次目标列表替换节点 ID 和输出路径；脚本默认复用 Keychain，并拒绝覆盖已有输出。凭据缺失时按 Skill 的 Keychain 流程补齐，不把密码放入参数、环境变量、仓库或日志。

接口实际为 `POST /wg-generate`，字段为 `aiouser/aiopass/server/publickey`；细节以下载脚本和接口契约为准。每节点每次只发送一个 POST；不要绕过单次提交逻辑，不跨镜像自动重试。失败或超时先记录并核查，超时表示结果可能未知，不能直接重复注册。

批次报告记录节点 ID、国家/标签、文件路径、开始/完成时间、成功/失败/未尝试状态、输入/输出哈希。不要记录密码、私钥或原始响应。所有生成完成或停止后，重新测试最终合集，不能沿用生成前的可用结论。

## 4. `.conf` 转统一 Mihomo YAML

复用已有模式时，直接从当前 YAML 或原始 `.conf` 构建候选，不产生新密钥。重新下载模式只读取本次成功的非空 `.conf`。用配置解析器处理，不能执行配置中的钩子或用 `eval` 解析远程目录。

当前单 Peer 格式的字段对应如下，依据 [Mihomo WireGuard 文档](https://wiki.metacubex.one/config/proxies/wg/)及本次已验证文件：

| WireGuard 输入 | Mihomo 输出 |
| --- | --- |
| `Interface.PrivateKey` | `private-key`，原值保留 |
| `Interface.Address` 中 IPv4 / IPv6 | `ip` / 节点级 `ipv6`；解析 CIDR 后仅取地址，缺哪类就省略对应字段 |
| `Interface.DNS` | `dns` 数组，并启用 `remote-dns-resolve: true` |
| `Interface.MTU`，若存在 | `mtu` |
| `Peer.Endpoint` | `server`、整数 `port`；正确解析 `[IPv6]:port`，不能简单按冒号拆分 |
| `Peer.PublicKey` | `public-key`，原值保留 |
| `Peer.AllowedIPs` | `allowed-ips` CIDR 数组，保留实际输入 |
| `Peer.PresharedKey`，若存在 | `pre-shared-key` |
| `Peer.PersistentKeepalive`，若存在 | `persistent-keepalive` |
| 目录的国家、标签和 ID | 唯一 `name`，沿用 `国家 · 标签 · str-节点ID` |

每个出站使用 `type: wireguard`、`udp: true`。不要丢弃私钥、DNS、隧道地址或返回的路由范围，不重新生成 Endpoint 端口。多 Peer、同地址族多个隧道地址、未知扩展或与当前解析器不兼容的字段，需要核对格式后再转换，不能静默取第一项或忽略。

整体配置沿用当前已验证设置：`mixed-port: 7897`、`allow-lan: false`、`mode: rule`、`log-level: warning`、全局 `ipv6: true`；一个名为 `StrongVPN` 的 `select` 组，包含本次保留的全部代理。用户已选择 **MetaCubeX 国内直连、其余 StrongVPN**，后续更换节点必须保留下面的 `rule-providers` 和有序 `rules`，并保留 UU 远程的产品例外，不能退回只有 `MATCH,StrongVPN`。不要添加自动测速、自动回退、四设备分组，或顺带开启系统代理/TUN。若用户选定节点仍通过测试，保留选择；否则选择本次通过且延迟较低的节点，并说明变化。

输出候选 `strongvpn.yaml`，核对节点 ID、名称和私钥无意外重复、组引用闭合；生成过程仅输出安全摘要，不打印 YAML 正文。目录元数据用于名称，**连接字段以本次 `.conf` 为准**，不能把目录刚变化的 IP 强行覆盖旧配置。单节点替换用 [prepare-replacement](local_tools.md#单节点替换候选)，提供已有新配置与当前 YAML；工具保留全部非目标设置，不代替网络验证。原生文件交付用 [export-conf](local_tools.md#导出当前节点的原生-conf)，优先核对更新后的源覆盖表。

### 固定分流策略：MetaCubeX

规则源采用 [MetaCubeX/meta-rules-dat](https://github.com/MetaCubeX/meta-rules-dat) 的 `meta` 分支。仅使用国内和私网的域名/IP 四个合集，不叠加其他重复的国内合集，也不加入广告拦截或按服务分组。香港、台湾等沿用该数据源分类，不另外扩展“国内”。

四项均为 `type: http`、`format: mrs`、`interval: 86400`，下载出口指定 `proxy: StrongVPN`，避免依赖国内网络直连 GitHub。路径必须相对 Mihomo 数据目录，不能写本机绝对路径。

| provider 名称 | behavior | URL 后缀（前缀统一为 `https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/`） | path |
| --- | --- | --- | --- |
| `private-domain` | `domain` | `geosite/private.mrs` | `./ruleset/private-domain.mrs` |
| `private-ip` | `ipcidr` | `geoip/private.mrs` | `./ruleset/private-ip.mrs` |
| `cn-domain` | `domain` | `geosite/cn.mrs` | `./ruleset/cn-domain.mrs` |
| `cn-ip` | `ipcidr` | `geoip/cn.mrs` | `./ruleset/cn-ip.mrs` |

```yaml
rules:
  - RULE-SET,private-domain,DIRECT
  - RULE-SET,private-ip,DIRECT
  - RULE-SET,cn-domain,DIRECT
  - RULE-SET,cn-ip,DIRECT
  - MATCH,StrongVPN
```

IP 规则不加 `no-resolve`，让未命中域名合集的域名也能解析后按私网/国内 IP 直连。最终未命中时进入手动选择的 `StrongVPN` 节点。保留现有 DNS 配置，不因这次规则变更顺带启用 DNS 劫持。

必须在 Clash 的“规则”模式使用上述策略；“全局”模式会绕过分流。规则拉取每 86400 秒更新，远程节点订阅仍按客户端现有间隔更新，二者独立。规则分类依赖上游数据，不承诺所有国内服务永远都被正确识别。技术依据：[Mihomo rule-providers](https://wiki.metacubex.one/config/rule-providers/)、[路由规则](https://wiki.metacubex.one/config/rules/)。

### UU 远程专属直连例外

用户额外要求 UU 远程直连。先于上述国内规则放置下面的产品规则，保留 `find-process-mode: strict`。本机 `/Applications/UURemote.app` 的 bundle ID 是 `com.netease.uuremote`；实际运行的主程序及三个辅助进程如下，不要把 UU 加速器或所有网易产品泛化为同一例外。

```yaml
find-process-mode: strict
rules:
  - PROCESS-NAME,UURemote,DIRECT
  - PROCESS-NAME,UURemoteService,DIRECT
  - PROCESS-NAME,UURemoteDaemon,DIRECT
  - PROCESS-NAME,UURemoteServer,DIRECT
  - DOMAIN-SUFFIX,nrd.nie.163.com,DIRECT
  - DOMAIN-SUFFIX,uuyc.163.com,DIRECT
  - DOMAIN-SUFFIX,uuyc.webapp.163.com,DIRECT
  # 接续四条 RULE-SET 和 MATCH,StrongVPN，不能只保留本段。
```

[网易官方入口](https://uu.163.com/)将 UU 远程链接到 `uuyc.163.com`；另外两个产品域名在本机程序二进制中核对。MetaCubeX 国内域名合集目前已涵盖 `163.com`，显式产品规则用于固定用户例外；进程识别成功时，进程规则可覆盖 UU 发往数值 IP、境外 P2P/中继地址的流量。不得据此开放整个 `netease.com`、随意猜测端口或放行所有 UDP。

进程匹配只适用于本机可识别的来源进程，不能识别从另一台设备转发来的应用身份；上述进程名核验范围为 macOS，Windows/移动端仍按产品域名及国内 IP 判断，不能宣称已验证全平台 UU 进程。依据：[Mihomo 进程规则](https://wiki.metacubex.one/config/rules/#process-name)、[进程匹配模式](https://wiki.metacubex.one/config/general/#进程匹配模式)。

验收时保持真实 UU 进程和远控会话不受打断：检查已加载的进程/域名规则与优先级，定向请求产品域名并从 API 确认 `DomainSuffix / DIRECT`；可用私有目录中命名为 `UURemote` 的系统 curl 副本发送受控请求，验证 `ProcessName / UURemote / DIRECT`，并明确其为规则机制测试，不能代称真实远控端到端成功。真实 UU 新连接尚未出现时如实记录，不擅自建立远控会话。 2026-10-15 本机 Mihomo 1.19.32 的 SOCKS 受控测试曾返回空进程信息，故必须检查实际 `ProcessName` 命中，不能把已加载规则等同于所有 UU 数值 IP 已直连；不能仅凭空进程信息归因管理员权限或要求启用 TUN。

## 5. 配置检查和实际连通验证

1. 从应用资源目录定位实际 Mihomo 可执行文件，不写死某个版本名。对候选运行：

   ```zsh
   "$strongvpn_mihomo" -t -f "$strongvpn_run_dir/strongvpn.yaml"
   ```

2. `-t` 仅证明配置可解析。连通测试优先使用隔离的用户态 Mihomo 实例，或在有回退备份时通过既有 Clash 内核测试；不要为测试启用系统代理/TUN，不修改默认路由，不关闭 REDpass。隔离实例使用**测试副本**：将 `mixed-port` 改为已核对未占用的独立端口、仅监听 loopback、独立 controller Unix socket/私有 secret 与数据目录、`tun.enable: false`。不能原样并起占用 7897 的配置，也不能把绑定端口失败算成节点超时。记录自己的 PID，结束后只清理本次实例；测试用端口/控制字段不写回正式发布 YAML。
3. 通过 Mihomo API 对**具体 WireGuard 节点**调用 `/proxies/<URL编码的完整节点名>/delay`，不要测可能回退的代理组。分别请求 `https://1.1.1.1/cdn-cgi/trace` 与 `https://www.gstatic.com/generate_204`，每目标超时 8000 ms，节点并发最多 2。
4. 本次新生成配置在两个目标都成功后才可发布；超时记为“本次未通过”，不能直接定性为过期。报告保存每目标结果、延迟和配置哈希，保留原配置不删。单节点维修只测目标及必要对照，不为刷新界面或格式检查遍历全部节点。测试会使用该客户端身份，其他设备在线时可能受到影响，不无限重复测速。
5. 只有用户本次授权包含全量清理时，才移除已测试且未通过的节点及组引用，再次 `-t`；未测试不等于失败。单节点新配置未通过就停止发布，不顺带删除其他节点。全量验证一个都未通过时不发布空订阅；保留报告，说明文件回滚不能恢复提供方已淘汰的身份。

规则变更还要单独验收分流：隔离实例用全新数据目录进行一次冷缓存启动，确认四个 provider 实际下载、`ruleCount > 0`；不能把 `-t` 已填充的目录当冷缓存。通过实际 SOCKS 请求国内域名、国内 IP 和海外 HTTPS 目标，同时从 `/connections` 捕获对应 `rule`、`rulePayload` 与 `chains`，核对国内为 `DIRECT`，海外包含 `StrongVPN` 及所选节点。`/delay` 指定出站会绕过分流，不能作为规则验收。发布后本机实际运行内核重复定向验收。

当前 Clash 内核 API 走 Unix socket。进程内读取 `clash-verge.yaml` 的 `external-controller-unix` 和 `secret`；HTTP 头使用 `Authorization: Bearer ...`。socket 路径会随运行变化，不写死 `/var/folders/...`，不把 secret 打进日志或命令参数。只读验证可以用 CLI；需要应用界面操作时使用可用的原生应用工具。

## 6. 接入已授权的阿里云 ECS

读取 [阿里云接入 Skill](/Users/xuhao/.codex/skills/alibabacloud-workbench-cli/SKILL.md)。本机已有 `aliyun` OAuth，Workbench 可能没有独立配置；不为一次更新创建新的长期 AK 或扩大全局权限。

```zsh
aliyun ecs DescribeInstances --profile beamjoin-deploy --RegionId cn-hongkong \
  --InstanceIds '["i-j6ccwyr58wuqxn9f8cqi"]'
```

在程序内解析状态和公网地址。复用有效、已授权的 SSH；若无登录凭据，可沿本次已验证的方法临时接入：

1. 在私人运行目录创建仅本次使用的 ed25519 密钥；私钥 `0600`，不放入云助手脚本。
2. 用 `aliyun ecs RunCommand --profile beamjoin-deploy` 向目标实例安装带唯一标记的临时公钥，授权行使用 `restrict` 前缀；只追加缺失的完整公钥，保留其他授权行。所有阿里云命令显式固定此 profile 和 `cn-hongkong`，不依赖当前默认身份。云助手只传公钥和只读诊断命令，不传订阅文件、令牌或密码。
3. `RunCommand` 的 `--CommandContent` 若为 Base64，必须同时带 `--ContentEncoding Base64`；返回成功仅表示已接受，随后通过 InvokeId 查询 `DescribeInvocationResults`，核对执行状态与 ExitCode。
4. 经云助手读取服务器 SSH host 公钥，写本次私有 `known_hosts`，SSH 开启 `StrictHostKeyChecking yes`、`IdentitiesOnly yes`。不能跳过主机校验。
5. 通过 SSH stdin / SCP 传输私人文件。不要把 YAML、令牌或密码放进远程命令参数、云助手正文或工具输出。

每次接入后确认目标、当前服务、订阅路径与权限，保留现有 API/Auth/Billing/PostgreSQL/Caddy。服务器运行文件优先于本机 BeamJoin 仓库模板，不部署或重建任何无关服务。

## 7. 更新现有订阅文件：保留 URL

正常更新**只换 `strongvpn.yaml` 内容**，不改令牌、`routes.inc`、域名、Caddy 主配置或开放端口，不需要重载 Web 服务。

1. 记录 VPS 当前文件 SHA-256，把旧文件以 `0600` 存到私人 `history/<本次批次>/`；确认备份可读。
2. 上传已通过验证的候选为 `/etc/forgepane/caddy/strongvpn/files/strongvpn.yaml.next-<批次>`，同目录、普通文件、`0600`，拒绝符号链接和目录替代。
3. 比较上传文件与本地候选 SHA-256，检查目标旧文件哈希仍与步骤 1 一致；有并发更新时停止覆盖并核对。
4. 写入并 fsync 候选，再用同目录原子 rename/`os.replace` 替换 `strongvpn.yaml`，必要时 fsync 父目录。避免直接截断线上文件，也不要用跨文件系统 `mv` 充当原子发布。
5. 在内存从私人清单中的**原 URL**做 HTTPS GET/HEAD：GET 200、字节哈希与本地候选一致、节点数正确，HEAD 200；保留 `private, no-store`、YAML Content-Type、no-referrer/noindex/nosniff。不要打印 URL 或正文。
6. 错误令牌、目录、直接文件路径仍 404，原 origin `/api/health` 缺凭据仍 403，服务器 loopback API health 应 200。只检查状态，不携带或转储业务秘密。
7. 若下载内容错误或状态不符，把备份复制成同目录回滚候选并原子替换，再验原 URL。保留失败候选与报告供核查，不覆盖可恢复的备份。

本机候选、VPS 下载内容与客户端缓存必须能用哈希闭环。发布后更新私人主清单 `subscription-manifest.json` 的 `subscriptions[0].file/sha256`，保留 `mode=unified` 和单项数组；更新镜像 `unified-manifest.json` 顶层的 `file/sha256`。二者对应的 `url/path` 保持原值，不能把数组主清单改成扁平对象或恢复四设备结构；先写新文件再原子替换，避免更新半份清单。同时更新本地 `strongvpn.yaml`、私人链接说明、ZIP 和本次脱敏结果，清楚标记当前发布源。

公网验收保留 TLS 验证。若本机 Python/OpenSSL 报 `unable to get local issuer certificate`，不能把它当作订阅文件故障，也不能使用 `verify=False` 或 `curl -k`。macOS 可用系统 `/usr/bin/curl` 的原生证书信任通道，核对 HTTPS 状态、`ssl_verify_result=0` 和下载哈希；秘密 URL 通过 `--config -` 标准输入提供，响应写入 0600 私人文件，不进进程参数/日志。验收失败先按下述回滚流程保护现网，修复验收通道后复用已验证候选，不为重试发布重新生成密钥。

### 只有改路由或轮换 URL 时才处理 Caddy

这不是正常文件更新步骤。当前主 Caddyfile 在 origin 站点内导入 `/etc/caddy/shared/strongvpn/routes.inc`，宿主目录 `/etc/forgepane/caddy` 已只读挂载到容器。

路由必须是精确令牌路径、仅 GET/HEAD、只提供指定文件、无目录浏览；不能削弱原 API 的来源凭据校验。保留全局 URI/敏感头日志过滤与 `persist_config off`。至少使用 32 随机字节令牌，换 URL 不会撤销已经下载的 WireGuard 密钥。

先备份、验证 Caddy 配置并核对无关路由等价，再发 `SIGUSR1` 平滑重载；v2.11.7 的该路径不依赖 admin API，参见 [Caddy 信号说明](https://caddyserver.com/docs/command-line#signals)。不能为了调用 `caddy reload` 开启 admin API或重启共享容器。确认 PID/启动时间不变、重载成功日志、业务状态和订阅 HTTP 验收均通过。

主 Caddyfile 是**单文件 bind mount**：如确需修改，先验证候选，保留原 inode 原地写入并 fsync，再比对容器内文件哈希；宿主机 rename 主文件可能导致容器继续看到旧 inode。`routes.inc` 和订阅文件位于目录挂载下，适合原子替换。后续运维升级需要保留订阅 import。

## 8. 刷新客户端与收尾

1. 当前本机远程订阅名为 `StrongVPN · 12 节点 · 统一订阅`。节点数变化时相应改名；保留一个统一远程条目，不重新导入四份。
2. 正常 URL 不变，点击该订阅“刷新”，必要时“重新激活订阅”。保留客户端现有系统代理、TUN 和更新间隔设置；2026-10-15/16 的历史基线为自动更新 1440 分钟、系统代理/TUN 关闭，但每次先读实时值，不能为了对齐历史而关闭用户已开启的开关。
3. 通过真实代理页和内核 API核对节点数、组引用与选择。更新前保存的节点若仍在通过名单中，通过界面或 `PUT /proxies/StrongVPN`（JSON `name` 字段）恢复它，并再次读取 `now` 确认；否则选择本次通过的节点并说明变化。客户端缓存配置哈希应与线上内容一致；用现有 SOCKS 端口发一次 HTTPS 请求，确认所选节点实际转发成功。UI 仅出现卡片或内核 `-t` 成功不等于已连通。

   遇到 UI 仍显示旧 `Timeout` 时，先对比本地源/VPS/客户端缓存哈希、当前运行文件的目标密钥、API `alive/history` 与真实转发结果。若后台正常，不为界面旧显示再注册密钥；可点击该节点的延迟数值单独重测，必要时重新加载应用 WebView 清除显示缓存，无需重启内核或真实 UU/REDpass。不同测速 URL 的历史可能不同，仍失败时核对具体目标，不直接认定显示缓存。原生菜单点击后以 fresh AX 确认是否真正执行，最终记录实际显示或明确未完成的 UI 验收。
4. 清理本次测试进程和远端暂存副本。临时 SSH 授权按**完整公钥**精确删除，核对其他授权行和 `0600` 权限保留，再移除本次本地私钥。不按通用备注批量清理其他密钥。
5. 本次结果写入 `contexts/daily_records/`：是否新生成、目标/成功/保留/失败数、生成失败是否结果未知、发布前后哈希、HTTP 与客户端实测、URL 是否保留、回滚/清理结果。只记录非秘密摘要。
6. 向用户报告实际结果和当前配置/链接说明文件的绝对路径；不承诺节点长期有效或所有应用均可访问。

## 9. 已验证事实与历史证据

- 2026-10-15：实时目录 53 节点，47 份生成成功，最终仅其中 12 份通过两个 HTTPS 目标；35 份超时没有被逐一认定为撤销。
- 用户曾要求拆成四份，随后明确改回一份；当前唯一有效方案是完整统一订阅，四个历史 URL 已返回 404。
- 统一文件已通过 Mihomo 配置检查、VPS GET/HEAD 与哈希校验、Clash 12 节点载入、SOCKS HTTPS 200；没有更改系统代理/TUN。
- 完整执行记录：[2026-10-15 节点导出与订阅部署](../../../../contexts/daily_records/2026_10_15_strongvpn_node_export.md)。历史日期、节点数量与服务版本是基线，不能替代后续实时核对。

本文给出操作命令、字段映射和验收合同；Node 入口没有 `publish`、`convert` 或 `update-subscription` 子命令。下载使用已经实现的 `servers/download`；本地单节点候选、既有 `.conf` 导出与只读 HTTPS 验收使用独立的 [Python 工具](local_tools.md)。远端原子发布、回滚、清单提交和客户端刷新仍按本文操作，不能假设本地工具代为完成。
