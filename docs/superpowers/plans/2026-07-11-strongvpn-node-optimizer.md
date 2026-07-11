# StrongVPN Node Optimizer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建并全局安装一个 macOS Codex skill，安全获取 StrongVPN WireGuard 配置，按真实 AI 服务访问质量选择最快节点，自动关闭冲突 VPN、切换节点，并在失败时恢复原网络状态。

**Architecture:** 仓库内 `rules/skills/strongvpn-node-optimizer/` 是 source of truth，`~/.codex/skills/strongvpn-node-optimizer` 通过符号链接完成全局安装。单一 Node.js CLI 暴露纯函数与系统适配器；纯函数负责服务器解析、配置生成、评分、缓存和脱敏，系统适配器负责 Keychain、命令执行、VPN 快照、WireGuard 生命周期和事务回滚。

**Tech Stack:** Node.js 22+ ESM、Node 内置 test runner、macOS `security/scutil/networksetup/route/curl`、Homebrew `wireguard-tools/wireguard-go`、Agent Skills YAML/Markdown。

## Global Constraints

- 凭据只存 macOS Keychain，service 固定为 `strongvpn-node-optimizer`。
- 数据目录固定为 `~/.local/share/strongvpn-node-optimizer`，目录权限 `0700`，配置权限 `0600`。
- 主下载源为 `https://tools.strongvpn.asia/share/strong-wg`，备用源为 `https://tools.strongtech.org/share/strong-wg`。
- 默认候选地区顺序为新加坡、日本、台湾、美国西海岸；真实隧道测试最多 6 个候选节点。
- 每个候选节点执行 3 轮 OpenAI、ChatGPT、Claude、GitHub、Google/Gemini 和 Cloudflare 小文件探测。
- 评分权重：稳定性 50%，延迟 35%，吞吐 15%；成功率低于 90% 或核心验证失败时淘汰。
- 切换前自动关闭其他 VPN；成功后保持关闭；失败或中断时恢复切换前状态。
- 最终配置使用 `AllowedIPs = 0.0.0.0/0, ::/0`。
- 只保留 current、previous 和 latest ranking；不创建 cron、LaunchAgent 或后台任务。
- 不记录 StrongVPN 凭据、WireGuard private key、完整配置或本机公网 IP。

---

## File Map

- Create: `rules/skills/strongvpn-node-optimizer/SKILL.md` — Codex 触发条件和执行工作流。
- Create: `rules/skills/strongvpn-node-optimizer/agents/openai.yaml` — Skill UI metadata。
- Create: `rules/skills/strongvpn-node-optimizer/scripts/strongvpn-node-optimizer.mjs` — CLI、纯函数、系统适配器和 benchmark orchestration。
- Create: `rules/skills/strongvpn-node-optimizer/scripts/strongvpn-node-optimizer.test.mjs` — Node 内置测试。
- Modify: `rules/skills/INDEX.md` — 增加 skill 索引。
- Create symlink: `~/.codex/skills/strongvpn-node-optimizer` — 指向仓库 source of truth。

### Task 1: 初始化 Skill 并实现服务器解析

**Files:**
- Create: `rules/skills/strongvpn-node-optimizer/SKILL.md`
- Create: `rules/skills/strongvpn-node-optimizer/agents/openai.yaml`
- Create: `rules/skills/strongvpn-node-optimizer/scripts/strongvpn-node-optimizer.mjs`
- Test: `rules/skills/strongvpn-node-optimizer/scripts/strongvpn-node-optimizer.test.mjs`

**Interfaces:**
- Produces: `parseServersModule(source: string): Server[]`
- Produces: `classifyPreferredRegion(server: Server): string | null`
- Produces: `Server = { id, label, country, ip, region }`

- [ ] **Step 1: 使用 skill-creator 初始化骨架**

```bash
python /Users/xuhao/.codex/skills/.system/skill-creator/scripts/init_skill.py \
  strongvpn-node-optimizer --path rules/skills --resources scripts \
  --interface display_name='StrongVPN Node Optimizer' \
  --interface short_description='测速并切换最快的 StrongVPN WireGuard 节点' \
  --interface default_prompt='测试 StrongVPN 最快节点并安全切换，失败时恢复原 VPN。'
```

Expected: skill 目录、`SKILL.md`、`agents/openai.yaml` 和 `scripts/` 创建成功。

- [ ] **Step 2: 写服务器解析失败测试**

```js
import test from 'node:test';
import assert from 'node:assert/strict';
import { parseServersModule, classifyPreferredRegion } from './strongvpn-node-optimizer.mjs';

const fixture = `
export const servers = {
  "Singapore": [{ label: "Singapore 301", value: "str-sin301" }],
  "Japan": [{ label: "Tokyo 302", value: "str-tyo302" }],
  "United States": [{ label: "Los Angeles 311", value: "str-lax311" }]
};
export const serverMapping = {
  "str-sin301": { ip: "203.0.113.10" },
  "str-tyo302": { ip: "203.0.113.11" },
  "str-lax311": { ip: "203.0.113.12" }
};`;

test('parses catalog without executing remote code', () => {
  const parsed = parseServersModule(fixture);
  assert.deepEqual(parsed.map(({ id, ip }) => ({ id, ip })), [
    { id: 'str-sin301', ip: '203.0.113.10' },
    { id: 'str-tyo302', ip: '203.0.113.11' },
    { id: 'str-lax311', ip: '203.0.113.12' },
  ]);
  assert.equal(classifyPreferredRegion(parsed[0]), 'singapore');
  assert.equal(classifyPreferredRegion(parsed[1]), 'japan');
  assert.equal(classifyPreferredRegion(parsed[2]), 'us-west');
});

test('rejects executable expressions', () => {
  assert.throws(() => parseServersModule('export const servers = {}; fetch("x")'), /unsupported/i);
});
```

- [ ] **Step 3: 运行测试并确认 RED**

Run: `node --test rules/skills/strongvpn-node-optimizer/scripts/strongvpn-node-optimizer.test.mjs`

Expected: FAIL，module 或解析函数不存在。

- [ ] **Step 4: 实现安全解析和地区分类**

不得使用 `eval`、`Function` 或动态 import。只接受对象/数组/字符串字面量；拒绝函数调用、额外语句、缺失 IP、重复 ID 和非法 IP。地区模式固定为：

```js
const REGION_PATTERNS = [
  ['singapore', /singapore|\bsin\b/i],
  ['japan', /japan|tokyo|osaka|\btyo\b|\bnrt\b|\bkix\b/i],
  ['taiwan', /taiwan|taipei|\btpe\b/i],
  ['us-west', /los angeles|san jose|seattle|\blax\b|\bsjc\b|\bsea\b/i],
];
```

- [ ] **Step 5: 运行测试并确认 GREEN**

Run: `node --test rules/skills/strongvpn-node-optimizer/scripts/strongvpn-node-optimizer.test.mjs`

Expected: PASS。

- [ ] **Step 6: 提交**

```bash
git add rules/skills/strongvpn-node-optimizer
git commit -m "feat: parse StrongVPN server catalog"
```

### Task 2: 实现 Keychain、配置 API 与脱敏

**Files:**
- Modify: `rules/skills/strongvpn-node-optimizer/scripts/strongvpn-node-optimizer.mjs`
- Modify: `rules/skills/strongvpn-node-optimizer/scripts/strongvpn-node-optimizer.test.mjs`

**Interfaces:**
- Produces: `readCredentials(runner): Promise<{ username, password }>`
- Produces: `generateConfig(options): Promise<{ server, config, publicKey }>`
- Produces: `redactSensitive(value, secrets): unknown`

- [ ] **Step 1: 写主备源、schema 和脱敏失败测试**

```js
test('falls back and builds full-tunnel config', async () => {
  const fetchImpl = async (url, options) => {
    if (String(url).includes('strongvpn.asia') && !options) throw new Error('primary down');
    if (!options) return new Response(fixture);
    return Response.json({ success: true, config: {
      Interface: { Address: '10.0.0.2/32', DNS: ['1.1.1.1'] },
      Peer: { PublicKey: 'peer-key', AllowedIPs: ['0.0.0.0/0', '::/0'] },
    }});
  };
  const result = await generateConfig({
    baseUrls: ['https://tools.strongvpn.asia/share/strong-wg', 'https://tools.strongtech.org/share/strong-wg'],
    server: { id: 'str-sin301', ip: '203.0.113.10' },
    credentials: { username: 'a000000', password: '0123456789' },
    keyPair: { privateKey: 'private-key', publicKey: 'public-key' },
    fetchImpl,
    randomPort: () => 55001,
  });
  assert.match(result.config, /AllowedIPs = 0\.0\.0\.0\/0, ::\/0/);
  assert.match(result.config, /Endpoint = 203\.0\.113\.10:55001/);
  assert.equal(JSON.stringify(redactSensitive(result, ['private-key', '0123456789'])).includes('private-key'), false);
});

test('rejects malformed API response', async () => {
  await assert.rejects(() => generateConfig({
    baseUrls: ['https://example.test'], server: { id: 'x', ip: '203.0.113.10' },
    credentials: { username: 'a000000', password: '0123456789' },
    keyPair: { privateKey: 'private-key', publicKey: 'public-key' },
    fetchImpl: async () => Response.json({ success: true, config: {} }),
    randomPort: () => 55001,
  }), /schema/i);
});
```

- [ ] **Step 2: 运行测试并确认 RED**

Expected: FAIL，配置函数不存在。

- [ ] **Step 3: 实现 Keychain 和配置生成**

Keychain 只用 service `strongvpn-node-optimizer`；`security -g` stderr 必须在适配器内部解析并丢弃，不能传到 CLI 输出。key pair 使用 `wg genkey`/`wg pubkey`。API 必须校验 Interface Address/DNS、Peer PublicKey/AllowedIPs；最终强制全隧道并使用 `55000-60000` 随机 UDP port。

- [ ] **Step 4: 运行测试并确认 GREEN**

Expected: PASS，测试输出不含 fixture password/private key。

- [ ] **Step 5: 提交**

```bash
git add rules/skills/strongvpn-node-optimizer/scripts
git commit -m "feat: generate protected StrongVPN configs"
```

### Task 3: 实现评分、排名和缓存

**Files:**
- Modify: `rules/skills/strongvpn-node-optimizer/scripts/strongvpn-node-optimizer.mjs`
- Modify: `rules/skills/strongvpn-node-optimizer/scripts/strongvpn-node-optimizer.test.mjs`

**Interfaces:**
- Produces: `scoreCandidate(samples): CandidateScore`
- Produces: `rankCandidates(results): CandidateResult[]`
- Produces: `isFreshCache(testedAt, now): boolean`

- [ ] **Step 1: 写失败测试**

```js
test('stable node outranks one-off fast node', () => {
  const stable = scoreCandidate([
    { ok: true, ttfb: .20, total: .30, throughput: 8 },
    { ok: true, ttfb: .21, total: .31, throughput: 8 },
    { ok: true, ttfb: .22, total: .32, throughput: 8 },
  ]);
  const flaky = scoreCandidate([
    { ok: true, ttfb: .10, total: .20, throughput: 12 },
    { ok: false },
    { ok: true, ttfb: 1.20, total: 2.00, throughput: 3 },
  ]);
  assert.ok(stable.score > flaky.score);
  assert.equal(flaky.eligible, false);
});

test('cache expires at 24 hours', () => {
  const base = Date.parse('2026-07-11T00:00:00Z');
  assert.equal(isFreshCache('2026-07-11T00:00:00Z', base + 86_399_999), true);
  assert.equal(isFreshCache('2026-07-11T00:00:00Z', base + 86_400_000), false);
});
```

- [ ] **Step 2: 运行测试并确认 RED**

Expected: FAIL，评分函数不存在。

- [ ] **Step 3: 实现确定性评分**

稳定性包含成功率和波动；延迟使用 TTFB/TLS/total 中位数；吞吐使用中位数；最终 `score = stability*0.50 + latency*0.35 + throughput*0.15`。三轮未全部成功或核心探测失败时 `eligible=false`。

- [ ] **Step 4: 运行测试并确认 GREEN，然后提交**

```bash
node --test rules/skills/strongvpn-node-optimizer/scripts/strongvpn-node-optimizer.test.mjs
git add rules/skills/strongvpn-node-optimizer/scripts
git commit -m "feat: rank StrongVPN nodes by stability"
```

### Task 4: 实现 macOS VPN 事务和回滚

**Files:**
- Modify: `rules/skills/strongvpn-node-optimizer/scripts/strongvpn-node-optimizer.mjs`
- Modify: `rules/skills/strongvpn-node-optimizer/scripts/strongvpn-node-optimizer.test.mjs`

**Interfaces:**
- Produces: `snapshotNetworkState(adapter): Promise<NetworkSnapshot>`
- Produces: `stopConflictingVpns(snapshot, adapter): Promise<void>`
- Produces: `restoreNetworkState(snapshot, adapter): Promise<RestoreResult>`
- Produces: `withNetworkTransaction(adapter, operation): Promise<unknown>`

- [ ] **Step 1: 写成功提交和失败回滚测试**

```js
test('commits success without restoring conflicts', async () => {
  const events = [];
  await withNetworkTransaction(fakeNetworkAdapter(events), async () => {
    events.push('new-tunnel-up');
    return { committed: true };
  });
  assert.deepEqual(events, ['snapshot', 'stop-conflicts', 'new-tunnel-up']);
});

test('restores state on switch failure', async () => {
  const events = [];
  await assert.rejects(() => withNetworkTransaction(fakeNetworkAdapter(events), async () => {
    events.push('new-tunnel-failed');
    throw new Error('handshake timeout');
  }), /handshake timeout/);
  assert.deepEqual(events, ['snapshot', 'stop-conflicts', 'new-tunnel-failed', 'cleanup-new', 'restore']);
});
```

- [ ] **Step 2: 运行测试并确认 RED**

Expected: FAIL，transaction 函数不存在。

- [ ] **Step 3: 实现快照、关闭和恢复**

快照使用 `scutil --nc list`、`route -n get default`、`scutil --dns`、`ifconfig` 和相关 `pgrep`。关闭顺序固定为系统 VPN stop、正常退出 App、等待 10 秒、最后终止仍持有 `utun` 的相关进程。快照只保存 service ID/name、app name、默认接口和 DNS resolver 摘要。

- [ ] **Step 4: 运行测试并确认 GREEN，然后提交**

```bash
node --test rules/skills/strongvpn-node-optimizer/scripts/strongvpn-node-optimizer.test.mjs
git add rules/skills/strongvpn-node-optimizer/scripts
git commit -m "feat: add transactional VPN switching"
```

### Task 5: 实现真实 benchmark 和 CLI

**Files:**
- Modify: `rules/skills/strongvpn-node-optimizer/scripts/strongvpn-node-optimizer.mjs`
- Modify: `rules/skills/strongvpn-node-optimizer/scripts/strongvpn-node-optimizer.test.mjs`

**Interfaces:**
- Produces: `selectCandidates(servers, preflightResults, limit=6): Server[]`
- Produces: `benchmarkCandidate(server, context): Promise<CandidateResult>`
- Produces: `runBenchmark(context): Promise<BenchmarkReport>`
- Produces CLI: `status`、`benchmark`、`switch --best`、`restore`、`credentials set`

- [ ] **Step 1: 写候选上限和配置保留失败测试**

```js
test('selects at most six candidates', () => {
  const selected = selectCandidates(makeServers(20), makePreflight(20), 6);
  assert.equal(selected.length, 6);
  assert.deepEqual([...new Set(selected.map(s => s.region))].slice(0, 3), ['singapore', 'japan', 'taiwan']);
});

test('keeps current and previous configs only', async () => {
  const fs = new MemoryStore();
  await promoteWinningConfig(fs, 'winner');
  await promoteWinningConfig(fs, 'new-winner');
  assert.equal(await fs.read('configs/current.conf'), 'new-winner');
  assert.equal(await fs.read('configs/previous.conf'), 'winner');
  assert.deepEqual(await fs.list('configs'), ['current.conf', 'previous.conf']);
});
```

- [ ] **Step 2: 运行测试并确认 RED**

Expected: FAIL，selection/retention 函数不存在。

- [ ] **Step 3: 实现 benchmark orchestration**

每个候选依次执行 `wg-quick up`、轮询 latest handshake、Cloudflare trace 验证出口、route/DNS 验证、六目标各三轮 curl 指标、`wg-quick down`。每个请求必须设置 connect/total timeout；Cloudflare 下载固定小文件并限制总量。

CLI 退出码：成功 `0`，无可用节点 `2`，凭据错误 `3`，依赖缺失 `4`，回滚不完整 `5`。`--json` 只输出脱敏结果。

- [ ] **Step 4: 实现 signal cleanup**

注册 `SIGINT`/`SIGTERM`；handler 幂等执行 tunnel cleanup 和 network restore，再按原 signal 退出。重复 signal 不并行恢复。

- [ ] **Step 5: 运行测试并确认 GREEN，然后提交**

```bash
node --test rules/skills/strongvpn-node-optimizer/scripts/strongvpn-node-optimizer.test.mjs
git add rules/skills/strongvpn-node-optimizer/scripts
git commit -m "feat: benchmark and switch StrongVPN nodes"
```

### Task 6: 完成 Skill、索引、验证和全局安装

**Files:**
- Modify: `rules/skills/strongvpn-node-optimizer/SKILL.md`
- Modify: `rules/skills/strongvpn-node-optimizer/agents/openai.yaml`
- Modify: `rules/skills/INDEX.md`

- [ ] **Step 1: 写 Skill 指令**

Frontmatter：

```yaml
---
name: strongvpn-node-optimizer
description: Use when testing, comparing, switching, restoring, or diagnosing StrongVPN WireGuard nodes on this macOS machine, especially for OpenAI, ChatGPT, Claude, GitHub, Gemini, slow VPN, high latency, packet loss, or conflicting VPN tunnels.
---
```

正文固定流程：先 `status`；benchmark/switch 前说明会关闭其他 VPN；凭据缺失时运行 `credentials set`；switch 使用事务回滚；禁止读取或回显 private key；完成后报告 winner、出口国家、成功率、中位 TTFB 和 restore 状态。

- [ ] **Step 2: 更新 INDEX**

增加：

```markdown
- [StrongVPN 节点测速与切换](./strongvpn-node-optimizer/SKILL.md) — 测试、排名、切换和恢复 macOS StrongVPN WireGuard 节点
```

- [ ] **Step 3: 验证**

```bash
python /Users/xuhao/.codex/skills/.system/skill-creator/scripts/quick_validate.py rules/skills/strongvpn-node-optimizer
node --check rules/skills/strongvpn-node-optimizer/scripts/strongvpn-node-optimizer.mjs
node --test rules/skills/strongvpn-node-optimizer/scripts/strongvpn-node-optimizer.test.mjs
```

Expected: validator、syntax、tests 全部成功。

- [ ] **Step 4: 安装全局 symlink**

```bash
ln -s /Users/xuhao/Documents/Other/context-infrastructure/rules/skills/strongvpn-node-optimizer \
  /Users/xuhao/.codex/skills/strongvpn-node-optimizer
```

目标已存在且不是同一 source 时停止，不覆盖。

- [ ] **Step 5: 提交**

```bash
git add rules/skills/strongvpn-node-optimizer rules/skills/INDEX.md
git commit -m "feat: add StrongVPN node optimizer skill"
```

### Task 7: 安装依赖并执行真实 smoke

**Files:**
- Runtime only: macOS Keychain、Homebrew、`~/.local/share/strongvpn-node-optimizer`

- [ ] **Step 1: 安装依赖**

```bash
brew install wireguard-tools wireguard-go
```

Expected: `wg --version`、`wg-quick --help`、`wireguard-go --version` 可运行。

- [ ] **Step 2: 隐藏输入写入 Keychain**

```bash
node /Users/xuhao/.codex/skills/strongvpn-node-optimizer/scripts/strongvpn-node-optimizer.mjs credentials set
```

Expected: password 不回显，Keychain 条目存在，最终报告不展示内容。

- [ ] **Step 3: 状态 smoke**

```bash
node /Users/xuhao/.codex/skills/strongvpn-node-optimizer/scripts/strongvpn-node-optimizer.mjs status --json
```

Expected: JSON 不含凭据/private key/public IP，正确报告 VPN、默认接口、cache 和依赖状态。

- [ ] **Step 4: 真实 benchmark**

```bash
node /Users/xuhao/.codex/skills/strongvpn-node-optimizer/scripts/strongvpn-node-optimizer.mjs benchmark --force --json
```

Expected: 最多测试 6 节点并生成排行榜；全部失败时恢复原 VPN，exit code 2。

- [ ] **Step 5: 切换 winner 并验证**

```bash
node /Users/xuhao/.codex/skills/strongvpn-node-optimizer/scripts/strongvpn-node-optimizer.mjs switch --best --json
curl -sS -o /dev/null --max-time 15 -w 'openai=%{http_code} ttfb=%{time_starttransfer} total=%{time_total}\n' https://api.openai.com/v1/models
curl -sS -o /dev/null --max-time 15 -w 'chatgpt=%{http_code} ttfb=%{time_starttransfer} total=%{time_total}\n' https://chatgpt.com/
curl -sS -o /dev/null --max-time 15 -w 'github=%{http_code} ttfb=%{time_starttransfer} total=%{time_total}\n' https://github.com/
```

Expected: 出口变化，OpenAI 401 可达，ChatGPT 可建立 TLS，GitHub 200。

- [ ] **Step 6: 验证 restore，再切回 winner**

```bash
node /Users/xuhao/.codex/skills/strongvpn-node-optimizer/scripts/strongvpn-node-optimizer.mjs restore --json
node /Users/xuhao/.codex/skills/strongvpn-node-optimizer/scripts/strongvpn-node-optimizer.mjs switch --best --json
```

Expected: restore 恢复原网络；第二条命令让 winner 成为最终连接状态。

- [ ] **Step 7: 最终验证**

```bash
node --test rules/skills/strongvpn-node-optimizer/scripts/strongvpn-node-optimizer.test.mjs
python /Users/xuhao/.codex/skills/.system/skill-creator/scripts/quick_validate.py rules/skills/strongvpn-node-optimizer
git status --short
```

Expected: tests/validator 全绿；凭据、临时配置和测速产物没有进入 git。
