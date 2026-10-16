# StrongVPN 新加坡单节点修复

用户报告可能多设备共用新加坡配置导致节点失效，授权先检查，必要时重新生成并更新原订阅。使用既有 Skill，未更改系统代理/TUN、REDpass、其他任务或远控会话。

## 核验与替换

- 当前订阅源和线上旧版本 SHA-256 为 `fd24f4aa559294d4e6ee639b652a8c8ccfe1e736b1d680454716214980d6c9c3`。运行选择为新加坡 `str-sin303`，系统代理/TUN 均关闭。
- 旧新加坡分别访问 Cloudflare trace 与 gstatic generate_204，均返回内核 504；首尔对照分别通过，159/184 ms。只能证明新加坡这份配置本次未通过，不能认定多设备共用或服务端撤销为原因。
- 实时目录仍有可选新加坡 `str-sin303`，直接读取网页实际 import 的目录；仅对该 ID 提交一次生成 POST，成功得到新 `.conf`，没有重试或重新下载其他节点。
- 将新 `.conf` 连接字段转换到当前统一 YAML 中的同一条目，名称和组引用保持；其他 11 个节点逐字段一致，四 MetaCubeX provider、12 条国内/私网/UU规则和其他顶层设置均一致。新加坡私钥已变化。
- 隔离 Mihomo `-t` 通过，两个 HTTPS 目标均成功，321/327 ms；测试实例已精确结束。最终候选 SHA-256 为 `1dd9863512462b005e926b2f2d4d8a8b18bd14b4d9f6c6b00aa06766e6365c1f`。

## 发布和本机验收

首次远端原子替换后的 Python HTTPS 验收遇到本机 OpenSSL 根证书链缺失（unable to get local issuer certificate），流程自动恢复旧文件，未修改本地主清单。随后以 macOS 系统 `/usr/bin/curl` 原生信任通道确认恢复的旧文件 GET 200、TLS verify result 0、哈希正确；在新的发布批次复用同一新加坡候选再次发布，没有第二次注册密钥，没有绕过证书校验。

最终原 URL 的 GET/HEAD 均 200，下载哈希、私人源、两个私人清单和当前 Clash 缓存完全一致。private/no-store、no-referrer、noindex、nosniff 响应头保留；错误令牌/目录/直接文件404、原 origin API 无来源凭据403、VPS loopback health200。路由及主Caddyfile哈希和5个容器PID/启动时间均未变化，无服务重启或Caddy重载。

本机通过真实订阅“刷新”加载新内容，保留新加坡选择和12节点。新加坡最终两目标延迟81/86 ms；首尔复查160/186 ms。经实际SOCKS请求gstatic获得HTTPS204且系统证书校验通过；另一存续连接的API证据为 `Match → StrongVPN → 新加坡`。系统代理/TUN仍关闭，12条规则与4个provider仍载入。UI旧Timeout属于前端测速显示缓存；单独重测后重新加载界面，真实代理页最终显示新加坡80 ms。未发起全节点测速。

私人README、固定链接说明和三文件ZIP同步更新，ZIP CRC和逐文件字节校验通过。新增私人 `node-sources.json` 指向本次最新新加坡 `.conf`，避免后续从原47份导出取回旧密钥。原始文件与两次服务器发布前文件均保留为历史；文件备份不承诺恢复提供方淘汰的服务端身份。

私人批次位于 `~/.local/share/strongvpn-node-optimizer/runs/20261016T075039Z-singapore-check/`，原生证书通道发布回执位于同级 `20261016T075039Z-singapore-check-native-publish/`。账号、私钥、完整URL与配置正文不写入仓库。临时SSH公钥按完整公钥精确移除，其他授权行保留，本机临时SSH私钥删除，服务器无本次遗留发布候选。临时curl与隔离内核均已结束。

其他设备刷新原订阅链接即可获取新配置；换密钥并未拆分设备身份，同时使用仍应选不同节点。
