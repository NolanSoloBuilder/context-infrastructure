# AI FDE 技术栈速查

日期：2026-09-08。此处 FDE 按 Forward Deployed Engineer 理解，尚未由用户确认缩写含义。

当前官方招聘样本：OpenAI 要求使用 Python、JavaScript 或类似技术栈交付生产级前后端；Anthropic 要求 Python，其他语言如 TypeScript、Java 加分，并要求 LLM 生产经验、提示工程、Agent 开发、评估和规模化部署。

据此可概括为：全栈工程 + AI 应用工程 + 企业系统集成与生产交付。具体框架随客户环境变化，不能从这些岗位推导出统一框架或市场份额。

用于理解的一套代表性组合（工程建议，非行业统计）：React/TypeScript 前端，Python/FastAPI 后端，模型 SDK 与工具调用，PostgreSQL/SQL 与按需检索，Docker/云部署，以及评估、日志、权限和审计。企业已有 Java 等后端时需要适配现有系统。

来源：
- https://openai.com/careers/forward-deployed-engineer-%28fde%29-seattle-seattle/
- https://job-boards.greenhouse.io/anthropic/jobs/5302966008

## 公开采用证据补充：技术负责人交付视角

用户明确要查实际团队在用什么，不接受以语言清单、泛化交付流程或个人推荐替代采用证据。检索日期 2026-09-08。以下属于定向公开样本，不是随机抽样，不能计算行业采用率；招聘中要求熟悉某工具不等于已在所有客户项目使用。

| 团队 | 公开技术组合 | 证据性质与来源 |
|---|---|---|
| Palantir | Foundry 数据与 Ontology、AIP Agent 与 Evals、Apollo 持续交付 | 自家标准交付架构：https://www.palantir.com/docs/foundry/architecture-center/platforms |
| Growth Protocol | GCP、Docker、FastAPI、LangChain/LangGraph、Elasticsearch、Snowflake、BigQuery | FDE 招聘要求：https://jobs.ashbyhq.com/growthprotocol/8369b38a-bb4f-4a5f-a43d-6c465b892c54 |
| NextLink Labs | Claude Agent SDK/LangGraph；Airflow、Snowflake、BigQuery、Databricks；REST/GraphQL、事件流、AWS/Azure/GCP | 客户 AI 交付岗位列出的工作内容和工具：https://jobs.ashbyhq.com/nextlinklabs/cb0bf55f-055a-489e-b982-4aa321036423 |
| Nextdata | Nextdata OS、LangChain/LangGraph、多步骤状态与审批、MCP-compatible endpoints | FDE 客户项目岗位：https://jobs.ashbyhq.com/nextdata/4feeb725-13e9-440b-984b-b173f943317b |
| Titan AI | Titan 平台；LangGraph/DeepAgents、Claude SDK/OpenAI Agents SDK | FDE 招聘要求，不能解读成全部同时部署：https://jobs.ashbyhq.com/titan-ai/9a2e4f06-a63f-4f31-b0b7-e8049bc070e9/ |
| Plain | AWS、Cloudflare、多模型供应商、GraphQL、Terraform、GitHub Actions、Datadog | FDE 岗位明确列为 Our tech stack：https://jobs.ashbyhq.com/plain/8952a4fb-6c96-4a68-9b4c-b2fb1f6329f4 |
| LangChain | LangGraph/LangSmith；Terraform、Helm、多区域 HA/DR、CI/CD | Deployed Architect 招聘：https://jobs.ashbyhq.com/LangChain/fc868832-3865-4f4a-8222-33422a7d3d96 |
| Productboard | Productboard/Spark、Jira、Salesforce、Zendesk、Azure DevOps、Slack；REST/webhooks | 偏售前与集成交付的 FDE 岗位：https://www.productboard.com/careers/open-positions/forward-deployed-engineer/am9icG9zdDrGzXHkHXO_5g3L_czSenEr/ |

企业生产案例（不能直接视为 FDE 团队采用统计）：
- Uber 2025-05-29 工程文章：Genie on-call 助手使用内部 Langfx（基于 LangChain）与 LangGraph 构建 Agentic RAG，并建立评估。https://www.uber.com/us/en/blog/enhanced-agentic-rag/
- Replit 2024 案例：LangGraph 编排 + LangSmith 观测，来源为供应商与客户合作案例，非当前完整栈审计。https://blog.langchain.dev/customers-replit/
- Dify 官方案例称 Maersk 使用 Dify Enterprise 做客服、邮件和发票审计，并称截至 2025 年末约 90 个生产应用。属于厂商披露，未独立验证数量。https://dify.ai/solutions/logistics-and-supply-chain

结论：定向样本中 LangGraph 和模型 SDK 反复出现，企业数据平台、云部署、身份与业务系统集成也是核心。Palantir 等围绕自家平台交付。不能把此前建议的 Dify + LiteLLM + pgvector + Langfuse + vLLM 全套称为 FDE 通用标准；本次没有足够证据支持这类普及程度断言。

## X 平台原帖核验

2026-09-08 使用本地 Chrome 的 X 站内搜索，打开下列原帖全文。搜索引擎对 X 的收录非常有限，原生站内搜索发现更多结果。阅读仅用于研究，未发帖、回复或互动。

- 余温 @gkxspace，2026-08-26：https://x.com/gkxspace/status/2092574593588556242 。第一人称比较 Dify 与腾讯云 ADP 4.0，作者称使用模拟企业资料、18 条测试及相同模型。描述 Agent 处理普通问题、受控 Workflow 处理退款审批和 CRM 超时，开放式分析交给云端沙箱；接口通过 Connector/MCP 接入。属于作者测试自述而非客户生产审计，文末有产品推广与追踪链接，不能将其测评结论视为独立产品排名。
- Kabir Sial @kabirsial，2026-07-17：https://x.com/kabirsial/status/2077998453213598207 。文章 Don’t touch the weights until necessary。作者资料自述投资人、曾在 Palantir，属于行业观点与工具地图而非自己的部署清单。列出编排 LangChain/LangGraph、Crew；观测 LangSmith/Raindrop；评估 Braintrust/LangChain；数据处理 Unstructured/Reducto/LlamaIndex；模型托管 Together/Baseten/Fireworks。建议先构建 Agent，再优化 harness，最后按需优化权重。
- Mike Fishbein @mfishbein，2026-05-30：https://x.com/mfishbein/status/2060733155535929752 。资料显示 Atherial 创始人，作者自述 40 多个 FDE engagements，提到 Claude Code/Cursor，以及语音 Agent 做需求访谈、云端 Agent 做原型与反馈。可用于说明交付工具与过程，未披露数据库、部署云或完整生产技术栈，不能补写。
- MindfulReturn @MindfulReturn，2026-09-08 搜索结果：https://x.com/MindfulReturn/status/2097202898447081651 。直接提问给 FDE 客户用 Claude/GPT、定制 OpenClaw/Hermes、Pi/Mastra/dsh 或工作台类产品。仅问题帖，不能当作采用证据或社区共识。

本轮结论：X 上确有相关分享，但需要区分作者实测（且可能有推广）、从业者经验自述和投资人选型观点。尚未核验出跨团队完整生产栈共识；不将学习清单、转型课程或岗位介绍当作实际使用数据。
