# 本地准备、原生配置导出与只读订阅验收

这些命令不会调用 StrongVPN 生成接口、切换节点、修改当前订阅源/清单、上传 VPS 或刷新客户端。实际发布仍按 [订阅工作流](subscription_workflow.md)。不要把候选生成成功当成网络可用或部署完成。

入口是 Skill 内 `scripts/strongvpn_subscription.py`，依赖 Python 3.10+、PyYAML。可用 `uv run --script` 读取脚本内依赖声明，无需向当前项目安装依赖。已有 Node 下载工具仍只提供原来的 `servers/download` 等命令，不把下面子命令传给 `.mjs`。

```zsh
strongvpn_skill="$HOME/.codex/skills/strongvpn-node-optimizer"
strongvpn_data="$HOME/.local/share/strongvpn-node-optimizer"
# 实际 file 字段以当前私人清单为准；不要打印清单正文或 URL。
strongvpn_current="$strongvpn_data/subscriptions/unified-2026-10-15/strongvpn.yaml"
strongvpn_run_dir="$strongvpn_data/runs/$(date -u +%Y%m%dT%H%M%SZ)-local-tools"
umask 077
mkdir -p "$strongvpn_run_dir"
```

## 单节点替换候选

输入是**当前统一 YAML**、用户指定的完整节点 ID、已经下载成功的新 `.conf`，输出必须是新的私人路径。

```zsh
uv run --script "$strongvpn_skill/scripts/strongvpn_subscription.py" prepare-replacement \
  --current "$strongvpn_current" --node str-sin303 \
  --conf "$strongvpn_run_dir/str-sin303.conf" \
  --output "$strongvpn_run_dir/strongvpn.candidate.yaml"
```

工具只替换唯一匹配的 WireGuard 条目的连接字段，保留名称、其他节点、组引用、DNS/分流等非 proxies 设置；拒绝复用已有私钥、多 Peer、钩子/未知字段、同地址族多个地址、非法端口/密钥和已有输出（含符号链接）。新配置未提供的 IPv6、MTU、PSK、keepalive 不会从旧身份错误继承。输出 `0600`，JSON 只有路径、哈希及保留范围摘要。

本命令不证明输入来自目标服务器；操作者必须先从实时目录选择正确 ID，并使用该 ID 的实际生成结果。命令不会自行注册密钥，也不会更新 `node-sources.json`。通过隔离内核验证、原子发布并确认现网后，再更新两份私人清单、源文件、该覆盖表和配置包。单节点维修保留其余节点，不套用“剔除全量未通过节点”的范围。

## 导出当前节点的原生 `.conf`

用户要“当前可访问节点”的文件时，先从运行中 Mihomo 读取实际选择，按需验证该节点，再传入对应 ID。不能用静态列表首项代替选择，也不能调用 `download` 来满足文件复制请求。

```zsh
uv run --script "$strongvpn_skill/scripts/strongvpn_subscription.py" export-conf \
  --current "$strongvpn_current" --node str-sin303 \
  --sources "$strongvpn_data/subscriptions/unified-2026-10-15/node-sources.json" \
  --original-dir "$strongvpn_data/exports/all-nodes-2026-10-15T07-04-02-021Z" \
  --output "$strongvpn_run_dir/str-sin303.conf"
```

未建立覆盖表时省略 `--sources`。工具优先采用 `overrides[节点ID]` 的文件并核对 SHA-256；该项存在但缺文件/哈希错误/字段过期时停止，**不回退旧导出**。没有该项时查原始目录；源文件必须与当前 YAML 的连接字段唯一匹配。最终逐字节复制，不猜测 YAML 中丢失的 WireGuard CIDR 前缀，也不生成新密钥。原生 WireGuard 文件不包含 Clash 的域名/进程分流规则，仍与对应节点共享身份。

覆盖表位于 Git 外，格式为：

```json
{
  "overrides": {
    "str-sin303": {
      "file": "/私人目录/最新节点.conf",
      "sha256": "该文件的64位小写SHA-256"
    }
  }
}
```

## 只读 HTTPS 预检与发布后验收

```zsh
uv run --script "$strongvpn_skill/scripts/strongvpn_subscription.py" verify-subscription \
  --manifest "$strongvpn_data/deployment-20261015/subscription-manifest.json" \
  --mirror "$strongvpn_data/deployment-20261015/unified-manifest.json"
```

在发布前先对现网运行，发现证书/下载通道问题先修验收通道，不要先改线上文件才发现无法验证。工具校验两份清单一致、本地源哈希、GET/HEAD 200、下载字节、节点数、现有私人响应头。macOS 默认用系统 `/usr/bin/curl` 原生信任并要求 `ssl_verify_result=0`；其他平台用 Python 默认 TLS 验证。可显式 `--transport curl|python`，没有关闭验证或自动跟随重定向的选项。

私有 URL 从清单读入后只经 curl 标准输入传递；禁用 `.curlrc`，不打印 URL、响应正文或 curl 原始错误。返回的 JSON 不含私钥和令牌。网络通道沿本机现有路由访问，工具不切换 REDpass 或其他 VPN。

远端替换后、提交本地清单前，可追加 `--expected-file "$strongvpn_run_dir/strongvpn.candidate.yaml"` 验证新候选字节；它只覆盖本次预期哈希，不修改清单。验证成功后仍要提交本地源/清单/覆盖表/ZIP、刷新 Clash，并完成工作流的未授权路径、业务保护、服务未重启和真实流量检查。此命令不负责 SSH、原子发布、回滚或这些额外验收，也不证明 WireGuard 节点当前可连接。

任何发布重试使用同一个已验证候选和新的发布批次；远端历史目录不可覆盖，不能因验收重试再调用生成接口。回滚前先比较目标哈希，遇到并发更新停止覆盖。文件回滚不会恢复提供方已淘汰的服务端身份。
