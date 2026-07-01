# anysearch-ai/anysearch-skill 分析

日期：2026-06-17

对象：`https://github.com/anysearch-ai/anysearch-skill`

本次分析基于 GitHub 当前元数据、本地浅克隆代码，以及匿名 API smoke test。仓库临时克隆位置：`adhoc_jobs/tmp_anysearch_skill/`。

## 结论

`anysearch-skill` 是一个面向 AI agent 的搜索 skill 壳，核心能力不在本地代码，而在远端 `https://api.anysearch.com/mcp`。本地仓库提供的是 `SKILL.md`、安装说明，以及 Python / Node.js / PowerShell / Bash 四套 CLI wrapper。它能覆盖通用搜索、垂直领域搜索、批量搜索和 HTML 页面提取。

对 Codex 这类本地 agent 来说，它的价值在于补一个“可由 agent 直接调用的搜索入口”，尤其是 finance / academic / legal / health / code 等垂直域。它不是一个可自托管搜索引擎，也不是 MCP server；更准确的定位是“远端搜索 API 的 skill 化客户端”。

我的判断：可以作为个人工具安装试用，但不适合直接作为高信任、敏感查询或生产级研究链路的唯一搜索后端。原因是本地代码很薄，API 后端不可审计，隐私声明主要来自仓库文案；同时多 runtime 的一致性和测试治理仍处在早期阶段。

## 当前项目状态

GitHub API 返回的仓库状态：

- 创建时间：2026-04-30
- 默认分支：`main`
- 最新 push：2026-06-12
- Stars：3361
- Forks：241
- Open issues / PR 总数：8
- 最新 release：`v2.1.0`，发布时间 2026-06-02
- License：Apache-2.0
- 主要贡献者：`morecry` 20 commits，其他贡献者多为 1-3 commits

仓库文件非常少，核心文件是：

- `SKILL.md`：agent-facing 使用规则
- `README.md`：安装、配置和验证说明
- `scripts/anysearch_cli.py`
- `scripts/anysearch_cli.js`
- `scripts/anysearch_cli.ps1`
- `scripts/anysearch_cli.sh`
- `scripts/shared/doc_spec.md`
- `scripts/shared/constants.json`
- `TEST_PLAN.md`

没有看到 `.github/workflows`，说明当前主分支没有 CI。打开的 PR 里有一个专门补 CI 和修 Bash doc 占位符的 PR，但截至本次分析未合并。

## 技术实现

四套 CLI 都调用同一个 JSON-RPC endpoint：

```text
POST https://api.anysearch.com/mcp
method: tools/call
```

请求形态是：

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "search",
    "arguments": {}
  }
}
```

认证是可选的 `Authorization: Bearer <ANYSEARCH_API_KEY>`。没有 key 时可以匿名调用，但额度更低。

支持的命令：

- `search`
- `get_sub_domains`
- `batch_search`
- `extract`
- `doc`

支持的垂直 domain：

```text
general, resource, social_media, finance, academic, legal, health, business,
security, ip, code, energy, environment, agriculture, travel, film, gaming
```

`SKILL.md` 明确要求 domain-specific 查询默认先调用 `get_sub_domains`，再选择 `sub_domain` 和 required params。这个设计对 agent 有价值，因为它把“先发现垂直 schema，再发起查询”的流程写进 skill 规则里，减少 agent 瞎填参数。

## Smoke Test

本机环境：

- `python3 --version`：Python 3.12.1
- `node --version`：v25.2.1
- Python runtime 失败，因为当前 Python 没有 `requests`
- Node runtime 成功
- Bash runtime 能搜索，但 `doc` 输出有模板占位符残留

实际验证命令和结果：

```bash
node scripts/anysearch_cli.js doc
```

成功输出 Node.js 版 interface specification。

```bash
node scripts/anysearch_cli.js search "OpenAI GPT-5 release date" --max_results 2
```

成功返回 2 条结果，第一条是 OpenAI 官方 GPT-5 页面，耗时约 10000ms。

```bash
node scripts/anysearch_cli.js get_sub_domains --domain finance
```

成功返回 6 个 finance 子域：`finance.screen`、`finance.quote`、`finance.calendar`、`finance.macro`、`finance.news`、`finance.fundamental`。

```bash
node scripts/anysearch_cli.js search "AAPL stock quote" --domain finance --sub_domain finance.quote --sdp type=stock,symbol=AAPL,cn_code= --max_results 2
```

成功返回 Apple quote，耗时约 1081ms。

```bash
node scripts/anysearch_cli.js batch_search --queries '[{"query":"OpenAI GPT-5 release date","max_results":1},{"query":"AAPL stock quote","domain":"finance","sub_domain":"finance.quote","sub_domain_params":"type=stock,symbol=AAPL,cn_code=","max_results":1}]'
```

成功返回一个通用搜索和一个 finance quote 查询。

```bash
node scripts/anysearch_cli.js extract https://example.com
```

成功返回 Markdown 内容。

```bash
bash scripts/anysearch_cli.sh doc
```

能运行，但输出里保留了 `{{LANG_INVOKE}}`，这是已由 PR #12 指出的未合并问题。

## 主要优点

第一，它确实能跑。匿名 API 可以完成通用搜索、finance 垂直查询、batch search 和 HTML extract。这比很多只有 `SKILL.md` 的 demo 更接近可用工具。

第二，Node CLI 无外部依赖，适合本机 Codex 使用。本机 Python 缺 `requests` 时，Node 仍然可用。

第三，垂直 domain 的 schema discovery 设计对 agent 友好。`get_sub_domains` 返回参数说明后，agent 能按 required params 发起查询。对于 finance / academic / legal 这类领域，比只给一个通用搜索框更有用。

第四，Apache-2.0 license 已补齐，基本许可问题较清楚。

## 主要问题

第一，核心能力完全依赖远端 API。仓库本身没有 index、crawler、ranker 或 provider 接入实现。任何结果质量、可用性、额度、日志策略和隐私承诺，都必须信任 `api.anysearch.com`。

第二，多 runtime 一致性不够。当前主分支上 Python CLI 在没有 `requests` 时连 `doc` 都不能跑，因为 `requests` 在文件顶层导入；Bash `doc` 输出有未替换模板；打开的 PR 还指出 Bash 参数缺值可能死循环、HTTP 错误可能被当成成功、PowerShell 可能泄露 Authorization 到 redirect 目标。这些问题不一定影响 Node 路径，但说明项目治理还在补基础坑。

第三，README 的安装建议与“pin release”不一致。README 注释说 pin 到具体 release，但示例命令拉的是 `main.zip`。打开的 PR #15 已指出这一点，也说明文档和真实安装链路存在漂移。

第四，安全边界写得不够强。`SKILL.md` 里有隐私说明，但 `SECURITY.md` 明确把 AnySearch API backend 排除在仓库 security policy 范围外。对用户来说，真正需要信任的恰好是后端。

第五，社区热度需要谨慎看。3k+ stars 和 241 forks 是强信号，但仓库创建时间只有一个多月，主贡献者集中，open PR 里也有推广型 README chart。这个项目更像增长较快的早期工具，而不是经过长期验证的基础设施。

## 对 Codex 全局安装的建议

如果只是个人探索，可以安装，但建议只把 Node runtime 写入 `runtime.conf`：

```text
Runtime: Node.js
Command: node ~/.codex/skills/anysearch/scripts/anysearch_cli.js
```

不要优先走 Python，除非 skill 目录或全局 Python 环境显式安装了 `requests`。也不要把 Bash 作为首选 runtime，直到 PR #12/#13 这类问题合并。

使用边界建议：

- 可以用于公开信息搜索、网页提取、非敏感 finance quote / news / academic 查询
- 不要用于公司内部信息、未公开项目、密钥、个人隐私、交易策略等敏感查询
- 高价值结论仍需要用官方来源二次验证
- 如果安装到 Codex 全局，应先做真实 smoke test，而不是只看 `doc`

## 后续动作

如果后续决定安装，建议流程是：

1. clone 或下载 release tag，而不是 rolling `main`
2. 放到 `~/.codex/skills/anysearch`
3. 写入 Node runtime 的 `runtime.conf`
4. 跑 `doc`、通用 `search`、`get_sub_domains --domain finance`、finance quote、`extract https://example.com`
5. 记录匿名额度和失败模式

如果要把它纳入长期研究链路，建议再补一轮横向对比：AnySearch vs 当前 web.run / Tavily / Exa / Perplexity / Google CSE，重点看金融新闻、官方文档、学术论文、中文页面和引用质量。
