# FDE 企业知识库检索与准确性

日期：2026-09-09。FDE 按 Forward Deployed Engineer 理解。本文是公开资料核验后的架构建议，未测试客户语料，不代表任何企业实际采用情况。

企业知识问答可使用 RAG；工程基线是权限和版本治理、混合检索、重排序、原文证据生成与持续评测。复杂问题按需增加 Agentic RAG。任何架构都不能承诺所有开放问题百分之百正确。

## 建议链路

问题与用户身份 → 权限范围、业务域与时间约束 → 查询路由 → BM25 与向量混合召回 → 去重和重排序 → 读取父章节、表格或相邻段落 → 检查证据完整性 → 引用原文回答，或补查、澄清、拒答。

入库时保留文档标题、章节、业务实体、来源、版本、生效时间和 ACL；维护增量更新、删除同步与索引新鲜度。模型生成的 chunk 背景仅用于检索辅助，不升级为原始事实。

实时金额、订单状态、库存等由受权限控制的 API 或 SQL 查询获得；文档负责解释规则。跨文档比较和多步问题可使用 Agentic RAG，但应设置调用次数、延迟和停止条件。全库主题总结或复杂关系探索再评估 GraphRAG，其索引构建与更新有额外成本。

## 准确性验收

先建设业务专家标注的真实问题集，覆盖精确编号、跨文档、表格、旧版规则、无答案和越权问题。分别测量证据 Recall@K、重排序质量、答案事实正确率、引用支持率、拒答精确率与召回率、可回答问题覆盖率、权限泄漏、更新延迟、P95 延迟和单次成本。LLM 评分需以人工抽样校准。不能用向量相似度作为答案正确概率，也不能靠大量拒答抬高表面准确率。

FDE 的关键交付是确认客户的权威来源、实体与业务术语、权限、生效规则和验收集，然后用评测选择检索配置。

## 核验来源

- Anthropic Contextual Retrieval：https://www.anthropic.com/engineering/contextual-retrieval 。支持 BM25 + embedding、补充 chunk 上下文及 reranking。其测试中 top-20 检索失败率从 5.7% 降至 1.9%，该指标不等于最终答案错误率，不能直接推广到客户数据。
- Azure AI Search RAG overview：https://learn.microsoft.com/en-us/azure/search/retrieval-augmented-generation-overview 。区分经典和 agentic retrieval。
- Azure 多租户 RAG 架构：https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/secure-multitenant-rag 。支持权限过滤设计。
- Microsoft GraphRAG：https://microsoft.github.io/graphrag/ 。用于理解图索引与图增强检索的适用方向。
