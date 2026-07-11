# StrongVPN 节点测速与自动切换 Skill 设计

日期：2026-07-11

## 目标

创建全局 Codex skill `strongvpn-node-optimizer`，在 macOS 上完成 StrongVPN WireGuard 节点配置获取、分层测速、节点排名、自动切换、状态检查和失败回滚。

首要成功标准是选出对 OpenAI、ChatGPT、Claude、GitHub 和 Google/Gemini 实际访问更快、更稳定的节点，而不是只比较 ICMP 延迟。切换成功后，默认路由和 DNS 必须由选中的 WireGuard 隧道接管。

## 安装位置与文件布局

Skill 安装到：

```text
~/.codex/skills/strongvpn-node-optimizer/
├── SKILL.md
├── agents/openai.yaml
└── scripts/
    ├── strongvpn-node-optimizer.mjs
    └── strongvpn-node-optimizer.test.mjs
```

运行数据放到：

```text
~/.local/share/strongvpn-node-optimizer/
├── configs/
│   ├── current.conf
│   └── previous.conf
├── results/
│   └── latest.json
└── state/
    └── switch-transaction.json
```

数据目录权限为 `0700`，WireGuard 配置权限为 `0600`。Skill 本身不包含账号、密码、private key 或生成后的配置。

## 交互接口

Codex 根据用户意图调用脚本：

```bash
node scripts/strongvpn-node-optimizer.mjs status
node scripts/strongvpn-node-optimizer.mjs benchmark
node scripts/strongvpn-node-optimizer.mjs benchmark --force
node scripts/strongvpn-node-optimizer.mjs switch --best
node scripts/strongvpn-node-optimizer.mjs restore
```

对应自然语言触发：

- 测试 StrongVPN 最快节点
- 重新测试所有候选节点
- 切换到最快代理
- 查看当前 StrongVPN 状态
- 恢复切换前的 VPN

`switch --best` 使用 24 小时内的缓存结果；缓存不存在或过期时先执行 benchmark。`benchmark --force` 忽略缓存。

## 凭据与配置获取

StrongVPN 用户名和密码保存在 macOS Keychain，service 名固定为 `strongvpn-node-optimizer`。脚本通过 `security find-generic-password` 在运行时读取，不把凭据传入命令行参数、日志或结果文件。

配置获取流程：

1. 从 `https://tools.strongvpn.asia/share/strong-wg/servers.js` 获取服务器清单和 server-to-IP 映射。
2. 主站失败时切换到 `https://tools.strongtech.org/share/strong-wg/servers.js`。
3. 本地生成 WireGuard Curve25519 key pair。
4. 向对应站点的 `/wg-generate` 提交用户名、密码、server ID 和 public key。
5. 使用响应中的 Interface/Peer 数据和服务器映射生成临时 WireGuard 配置。
6. 不记录请求体、密码、private key 或完整响应配置。

页面当前使用随机 `55000-60000` UDP endpoint port。脚本沿用服务端页面的生成规则，保证与官方生成器一致。

## 节点筛选与测速

### 第一阶段：低成本预筛

默认地区顺序：新加坡、日本、台湾、美国西海岸。解析服务器列表后，对这些地区的节点做 DNS/IP 可达性、路由和有限次数的网络延迟采样。预筛只用于缩小范围，不直接决定最终排名。

每个地区保留表现靠前的节点，合并后最多选 6 个进入真实隧道测试。

### 第二阶段：真实 WireGuard 测试

每个候选节点执行：

1. 生成独立临时配置。
2. 建立 WireGuard 隧道。
3. 在限定时间内确认 latest handshake。
4. 验证公网出口已经变化。
5. 验证默认路由和 DNS 走新隧道。
6. 对以下目标执行 3 轮请求：
   - OpenAI API 未鉴权探测
   - ChatGPT 首页
   - Claude 首页
   - GitHub 首页/API
   - Google/Gemini 可达性
   - Cloudflare 固定小文件下载
7. 记录 DNS、TCP connect、TLS、TTFB、total、HTTP 状态、成功率和小文件吞吐。
8. 关闭该测试隧道，再进入下一个节点。

单项失败允许重试一次。整个 benchmark 预期耗时 5-10 分钟。

### 评分

总分由三部分组成：

- 连通成功率、握手稳定性和多轮波动：50%
- TTFB、TLS 和总延迟：35%
- 小文件吞吐：15%

硬性淘汰条件：无法 handshake、出口未变化、OpenAI API 不可达、默认路由/DNS 验证失败，或三轮综合成功率低于 90%。

所有延迟使用中位数；波动使用离散程度参与稳定性评分，避免单次最快节点获胜。

## WireGuard 运行方式

通过 Homebrew 全局安装 `wireguard-tools` 和 `wireguard-go`，使用 CLI 管理测试与最终隧道。现有 WireGuard App 和 `str-lax311` 配置保持不变，不读写 App 内部配置数据库。

最终隧道使用全隧道配置：

```text
AllowedIPs = 0.0.0.0/0, ::/0
```

这样可以覆盖 AI 服务的动态域名和 CDN。脚本负责验证 DNS 没有留在原始网络。

## VPN 关闭、切换与回滚事务

切换开始前记录：

- `scutil --nc list` 中已连接的 VPN service
- 默认路由、DNS 和活动 `utun*`
- REDpass、Yunshu、OpenVPN、WireGuard 和其他 VPN 相关进程
- 当前由 optimizer 管理的 WireGuard 节点

随后按顺序关闭其他 VPN：

1. 调用系统 VPN stop 接口。
2. 正常退出对应 App。
3. 等待默认路由释放。
4. 超时后才终止残留进程。

切换视为一个事务：

- 新 StrongVPN 节点通过全部成功标准后提交事务，其他 VPN 保持关闭。
- handshake、出口、路由、DNS 或目标可达性任一失败时，关闭新隧道并恢复切换前的 VPN/应用状态。
- 进程已恢复但隧道无法恢复时，报告明确的人工恢复项，不把任务标记为成功。

`restore` 使用最近一次 `switch-transaction.json` 恢复切换前状态。事务文件不得包含凭据或 WireGuard 密钥。

## 配置保留策略

测速结束后删除所有失败、落选和临时节点配置，只保留：

- 当前最快节点配置 `current.conf`
- 上一个已验证节点配置 `previous.conf`
- 最近排行榜 `latest.json`

排行榜保存节点 ID、地区、出口国家、Cloudflare colo、各项时延、成功率、吞吐、评分、测试时间和错误类型。隐藏用户名、密码、private key、完整配置和本机公网 IP。

## 依赖与权限

脚本启动时检查：

- Node.js
- Homebrew
- `wireguard-tools`
- `wireguard-go`
- `curl`
- `security`
- `scutil`
- `networksetup`

缺失的 WireGuard CLI 通过 Homebrew 全局安装。修改隧道、路由和 DNS 时允许 macOS 请求管理员密码，但不保存 sudo 密码。

## 错误处理

- 下载主站失败：自动切换备用站；两者均失败时不改变当前 VPN。
- StrongVPN 鉴权失败：停止任务，提示更新 Keychain，不回显凭据。
- server list 或 API schema 变化：拒绝生成配置，保留当前网络状态。
- 某节点失败：记录脱敏错误，清理临时配置，继续下一个节点。
- 所有节点失败：恢复测速前 VPN 状态，不生成最佳节点。
- benchmark 被中断：使用 signal handler 清理测试隧道并恢复事务快照。
- DNS/默认路由未恢复：输出具体接口和手动恢复命令。

## 测试策略

代码采用 Node.js 内置 test runner，先测试后实现。

自动化测试覆盖：

- `servers.js` 解析和地区分类
- 主站/备用站 fallback
- API 响应转 WireGuard 配置
- 凭据、private key 和公网 IP 脱敏
- 中位数、波动、成功率和评分排序
- 24 小时缓存规则
- 候选节点淘汰条件
- VPN 状态快照、成功提交和失败回滚
- signal 中断清理
- 配置保留与权限

系统命令通过依赖注入测试，避免单元测试真实切换网络。自动化测试通过后再执行真实 smoke：下载配置、测试候选节点、切换最佳节点、验证 OpenAI/ChatGPT/GitHub，最后验证 `restore`。

## 默认运行和非目标

Skill 只按用户指令运行，不创建 cron、LaunchAgent 或后台定时测速。结果缓存 24 小时。

本版本不实现：

- 自动购买或管理其他 VPN 服务
- Cloudflare Edgetunnel
- 公共 Skill 发布
- 长期后台监控
- 基于域名的 split tunnel
- 修改 StrongVPN 或 WireGuard App 的私有数据格式

## 凭据轮换

当前 StrongVPN 密码已在对话中出现。完整验证完成后，应在 StrongVPN 后台轮换密码，并用新密码更新 macOS Keychain。仓库文档和运行日志不得记录旧密码或新密码。
