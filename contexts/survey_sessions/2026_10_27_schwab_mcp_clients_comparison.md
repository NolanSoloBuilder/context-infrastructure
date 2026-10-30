# Schwab MCP / CLI / SDK 选型

核验日期：2026-10-27。范围为公开仓库、GitHub API 元数据、README 和部分关键代码静态阅读；未安装、未接入账户、未做实盘验证，不构成完整安全审计。用户关注嘉信 API 与 ETF 定投路径。

## 社区与维护快照

数据来自 GitHub REST API；主分支最后提交与 pushed_at 区分，后者也可能反映其他分支推送，不能直接视为主分支更新。

| 仓库 | Stars / Forks | 主分支最后提交 | 本次读取 SHA |
| --- | --- | --- | --- |
| jkoelker/schwab-mcp | 66 / 24 | 2026-10-23 | 491960670d98dad9ed26f6631536b2db656f51be |
| sudowealth/schwab-mcp | 83 / 45 | 2025-06-02 | 9c8e32f2e53d2ce28ca7fff55a433d4193570c41 |
| weig/schwab_cli | 2 / 0 | 2026-10-26 | e66c392e290114e791d4d29e3e4a3d8d5b191f55 |
| alexgolec/schwab-py | 480 / 132 | 2025-08-04 | 43c4614965bdc434bd87fcd49f959db66338185e |
| tylerebowers/Schwabdev | 882 / 285 | 2026-08-11 | ab15d10f75b96cfa7508f04d6a2b96bba5996360 |

Stars 仅为关注度代理，不等于活跃用户、稳定性或安全性。未声称全面覆盖全部同类项目。

## 用户提供的 jkoelker/schwab-mcp

- Python MCP，默认 stdio，支持 Streamable HTTP；行情、账户、订单、期权与技术指标工具。
- CLI 未配置审批且未开启 bypass 时不注册写工具；配置 Discord 或 Signal 审批可以启用写入。显式 bypass 开关会使用自动批准管理器。
- 当前版本是 preview_equity_order 等预览工具产生 preview_id，再用 place_previewed_order 提交缓存的原始订单。源码 orders.py 使用 ctx.previews.pop 消耗预览后审批、提交，避免模型在确认后重新组织订单参数。
- equity preview 的 quantity 为 int，未见直接按美元金额买入的工具契约；每月固定美元与固定股数定投须区分，也不能把 UI 零股功能直接推定为该封装支持。
- pyproject.toml 依赖 schwab-py；uv 来源配置指向作者自己的 schwab-py fork 的 proxy_support 分支。uv 与 pip 安装的依赖解析路径应在真正安装前核对并锁定版本。
- token 使用本地 YAML/JSON 保存，创建文件权限 0600；这是文件权限控制，不是加密存储。
- 结论：作为本地账户查询和人工审批交易的 MCP 候选值得继续验证，不是完整的无人值守定投系统。

## 其他路径

- sudowealth/schwab-mcp：TypeScript、Cloudflare Workers / Durable Objects / KV 路线，README 将下单、改单、撤单标为 Experimental。关注度略高，但主分支最后提交较久，不因 Star 数高就优先采用。README 关于 Cloudflare 付费要求属于该项目描述，本次未独立核验平台最新资费。
- weig/schwab_cli：CLI + MCP，近期维护，但社区规模很小。README 所谓跨七日持续续期依赖无头浏览器自动登录，属于重新 OAuth 授权，并非官方提供永久 refresh token；不能将其描述成 API 原生延长授权。
- Schwabdev：本次比较中关注度最高的 Python SDK，覆盖认证、交易、实时流与同步/异步等。适合固定规则执行器的候选底座；API 权限、零股和金额下单需单独验证。
- schwab-py：另一个较大的 Python SDK，文档较完整，也是 jkoelker MCP 的依赖来源。主分支最后提交时间较旧，须区分其较新的 pushed_at。

## 推荐方向

用户希望用自然语言查询账户、分析行情时，优先继续验证 jkoelker MCP 的只读模式。若核心需求是按固定日期与预算定投，则优先 SDK + 确定性调度与执行，MCP 作为查询和配置入口；固定规则无需每次让 LLM 重新决定交易。执行器需要处理交易日、现金、授权过期、订单回查、重复执行与成交记录。

这些社区封装均不能代替用户申请 Schwab Developer App 与 OAuth 授权；国际账户实际资格仍待用户账户授权结果确认。schwab-py 维护者文档说明 access token 约 30 分钟、refresh token 约 7 天，后者到期需重新授权；自动刷新 access token 与重新登录是不同流程。

## 来源

## 补充：没有美国手机号的注册限制

用户追问没有美国手机号能否使用。2026-10-27 查询发现一名用户于 2026-06-30 在 Reddit 转述嘉信客服回复，称开发者注册要求美国号码、不再接受新增外国号码；2026 年另有用户报告无法选择墨西哥区号。这是用户一手经历及客服回复转述，尚非可独立核验的官方政策公告。官方注册页为动态页面，本次文本抓取未读到国家代码字段，无法确认当日表单是否仍如此。

因此应明确提示：已有证券账户和 thinkorswim 不代表能注册 Developer Portal；没有美国号码可能卡在注册，MCP/SDK 无法绕过。优先通过现有嘉信客服渠道询问是否支持 +86 或人工注册，以及非美国居民账户的 Trader API 资格；未确认前不建议为了此事直接购买号码。官方产品页面此前公开列出 API 联系邮箱 TraderAPI@Schwab.com。不得把社区报告当作全面已证实政策，也不得保证虚拟号码一定通过验证。

- 用户经历：https://www.reddit.com/r/Schwab/comments/1uhpc08/i_dont_have_a_us_phone_number_how_do_i_apply_for/
- 官方注册入口（本次动态表单未能读取）：https://developer.schwab.com/register

## 仓库与文档链接

- 用户入口：https://mcpservers.org/zh-TW/servers/jkoelker/schwab-mcp
- https://github.com/jkoelker/schwab-mcp
- https://github.com/jkoelker/schwab-mcp/blob/491960670d98dad9ed26f6631536b2db656f51be/src/schwab_mcp/tools/orders.py
- https://github.com/jkoelker/schwab-mcp/blob/491960670d98dad9ed26f6631536b2db656f51be/pyproject.toml
- https://github.com/sudowealth/schwab-mcp
- https://github.com/weig/schwab_cli
- https://github.com/tylerebowers/Schwabdev
- https://github.com/alexgolec/schwab-py
- https://github.com/alexgolec/schwab-py/blob/43c4614965bdc434bd87fcd49f959db66338185e/docs/auth.rst
- 元数据请求模式：https://api.github.com/repos/{owner}/{repo} 和 /commits?per_page=1
