# OKX AI Task Marketplace 截图核验

日期：2026-07-17

## 结论

截图展示的是 OKX AI Task Marketplace 上的一次卖方 Agent 接单记录。任务内容为一份“X Layer 稳定币链上研究报告”，报价 1 USDT。截图所述流程包括收到任务、申请、买方接受、生成报告、提交交付物、审核通过、资金到账和双方评分。

它属于需要协商、交付和验收的 A2A 任务。OKX 官方把这类复杂工作设计为 escrow-based task；标准化、按调用付费的服务走 A2MCP / x402。两条路径共享 Agent 的链上身份和声誉记录。

## AI 如何完成这类接单

普通 LLM 只负责理解和生成内容。真正让 Agent 可以接单的是外部执行层：

1. 在 Codex、Claude Code、OpenClaw 等 MCP-compatible client 中安装 OKX Onchain OS skills。
2. 创建并绑定 Agentic Wallet 与链上 Agent identity，设置预算、allowlist 和签名权限。
3. Agent 通过 Task Marketplace 的工具发现任务、判断能力和报价、发起申请。
4. 买方接受后，Agent 使用搜索、浏览器、代码和文档工具完成报告，并调用 marketplace API 提交 deliverable。
5. 买方验收后，escrow contract 释放 USDT；双方再提交链上评分，累计 reputation。

因此，截图所说的“无人类介入”只能表示这次运行过程中没有逐步人工点击。Agent 的部署、钱包初始化、权限范围、资金准备、任务策略和异常处理仍由人预先配置。

## 截图证据边界

截图公开的交易哈希 `0x8d40860e6d42b2504252d0a16763eca2a3eff60611ee22d661d1fa7c38c50e3d` 被作者标注为“已上链评分 tx”。这条哈希即使核验成功，也只直接证明评分交易。1 USDT 到账应由另一笔 USDT transfer 或 escrow release 交易证明；截图没有给出对应收款哈希，所以目前不能独立确认收款金额和收款地址。

任务时间线还存在一处轻微不一致：截图顶部文案称“3 分钟前”，任务表中却写了 2026-07-10 至 2026-07-13。它更像作者在 7 月 13 日发布的任务复盘截图，不影响机制判断，但不应据此认定全部过程实时连续发生。

## 产品判断

这类系统真正新增的能力不是“AI 会写报告”，而是把任务发现、合同状态、托管付款、交付物和声誉接到机器可调用的协议上。现阶段更接近链上 Upwork + Agent 工具协议。低价、标准化、可机器验收的数字交付适合自动化；高价值任务仍受制于交付质量、争议判定、私钥安全和真实需求密度。

## 本机复现进度

2026-07-17 已按 OKX 官方 Codex 安装方式完成本机部署：

- 仓库：`~/.codex/onchainos-skills`
- Codex 发现链接：`~/.agents/skills/onchainos-skills`
- CLI：`~/.local/bin/onchainos`，安装版本 `4.2.5`，SHA256 校验通过
- Skill checkout：commit `93a2841`，预检返回 integrity `ok`
- 卖方业务门禁实测：CLI 可达；当前阻塞在 Agentic Wallet 未登录，因此尚未创建 ASP 身份或读取可接任务

下一步需要用户选择邮箱验证码登录或 OKX API Key 登录。登录后依次创建 ASP 身份、配置“金融投研报告”服务、读取公开任务、筛选低风险任务并申请。创建身份、签名、接单和付款均保留显式确认门。

## 本机访问限制诊断

2026-07-17 在本机 Chrome 访问 `www.okx.com/en-us/learn/agentic-wallet` 时导航超时，访问 `web3.okx.com/onchainos/dev-portal` 明确返回 `ERR_ADDRESS_UNREACHABLE`。系统 DNS 证据如下：

- `www.okx.com` 和 `web3.okx.com` 均被当前企业 DNS `10.48.255.25` 解析为 `169.254.0.2`
- 公共 DNS `8.8.8.8` 返回正常 Cloudflare 地址 `104.18.43.174` / `172.64.144.82`
- 当前默认路由为 `en0`，系统代理关闭；`169.254.0.2` 没有可达路由
- `github.com` 仍能正常解析和访问，说明不是整机断网

因此这次失败发生在本机/企业网络的 DNS sinkhole 层，而不是 OKX 网页返回的地区或账号权限页。当前机器同时运行 YunshuManager、REDpass 和 Microsoft Defender；只凭进程列表不能把责任归给其中某一个组件。不要通过 `/etc/hosts` 或私设 DoH 绕过受管网络策略。合规路径是改用允许访问该服务的个人网络/设备，或请企业网络管理员确认 OKX 域名策略。

## 来源

- [OKX AI: A Marketplace for the Agent Economy](https://www.okx.com/en-us/learn/okx-ai)
- [OKX AI Agent Marketplace User Agreement](https://www.okx.com/en-gb/help/okx-ai-agent-marketplace-user-agreement)
- [X Layer RPC endpoints](https://web3.okx.com/vi/onchainos/dev-docs/xlayer/developer/rpc-endpoints/rpc-endpoints)
- 用户提供的两张截图，2026-07-17
