# Codex 操作 Charles Schwab 的 Skill / MCP 调研

日期：2026-08-12

## 结论

本机与当前项目没有已安装的 Schwab 交易 Skill。`skills.sh` 能搜到 `theneoai/awesome-skills@charles-schwab`，但源码显示它是 `kind: persona` 的角色提示词，只提供嘉信业务与投顾知识，不连接账户，也不能买入、卖出或撤单。

真正可执行的方案主要是 MCP。当前首选候选是本地自托管的 [`jkoelker/schwab-mcp`](https://github.com/jkoelker/schwab-mcp)：默认可用只读模式；交易采用“预览订单 → 使用 `preview_id` 提交同一订单”的两阶段流程，并默认要求 Discord 审批。它通过嘉信官方 Developer Portal 申请的 App Key / Secret 和 OAuth 登录，不需要把 Schwab 登录密码交给模型。

第二候选是远程 [`Trade It MCP`](https://github.com/trade-it-inc/trade-it-mcp)：支持 Charles Schwab，采用 `create_trade` 生成 draft、展示完整订单、用户明确确认后才允许 `execute_trade`。代价是账户授权经过第三方远程服务，并需要 Trade It Pro，因此隐私与供应商依赖高于本地自托管方案。

[`Open Stocks MCP`](https://github.com/Open-Agent-Tools/open-stocks-mcp) 也暴露 Schwab 股票、期权与订单工具，但仓库 README 同时写明 Schwab journey tests 和 live trading validation 尚未完成。当前不建议用于真实嘉信账户下单。

## 建议接入顺序

1. 先接 `jkoelker/schwab-mcp` 的只读模式，只开放账户、持仓、行情和订单查询。
2. 完成 OAuth、token 本地存储权限和只读 smoke test，再考虑开放订单预览。
3. 真实下单工具继续保持禁用；确需启用时，坚持“订单预览内容人工核对 + 每次明确确认 + 固定金额上限 + 禁止期权/融资融券”的门禁。
4. 不启用 `--jesus-take-the-wheel`；该参数会绕过交易审批。

Codex 官方文档确认，本地 Codex 客户端支持 STDIO 与 Streamable HTTP MCP，并可通过 `~/.codex/config.toml` 或 `codex mcp add` 配置。因此上述 MCP 在技术上可以接入 Codex；是否允许写操作取决于 MCP 暴露的工具和本地审批设计。

## 已核对来源

- [Codex MCP 官方文档](https://learn.chatgpt.com/docs/extend/mcp?surface=cli)
- [Schwab Developer Portal: Trader API - Individual](https://developer.schwab.com/products/trader-api--individual)
- [`jkoelker/schwab-mcp`](https://github.com/jkoelker/schwab-mcp)
- [`trade-it-inc/trade-it-mcp`](https://github.com/trade-it-inc/trade-it-mcp)
- [`Open-Agent-Tools/open-stocks-mcp`](https://github.com/Open-Agent-Tools/open-stocks-mcp)
- [`theneoai/awesome-skills@charles-schwab`](https://skills.sh/theneoai/awesome-skills/charles-schwab)

