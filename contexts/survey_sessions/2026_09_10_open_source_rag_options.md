# 开源 RAG 方案初筛

日期：2026-09-10。针对已学习的解析、分块、向量、BM25、混合检索、融合、重排、上下文、生成、验证链路。依据官方仓库及文档当前页面进行能力初筛，未部署、压测或用公司语料对照评测。不能把项目自述的质量宣传当成效果证明。

| 项目 | 类型 | 适合用途 | 需要明确的边界 |
|---|---|---|---|
| [RAGFlow](https://github.com/infiniflow/ragflow) | 可自部署的 RAG 引擎/产品 | 观察文档解析、分块、检索、引用问答的完整流程 | 业务级验证、REDoc 同步与权限仍需核查和适配；主仓库 Apache-2.0 |
| [Dify](https://github.com/langgenius/dify) | 可视化 AI 应用平台 | 将知识检索、模型、业务 API 和 Agent 编成应用 | Dify Open Source License 带附加条件，不可直接按纯 Apache-2.0 理解 |
| [Haystack](https://github.com/deepset-ai/haystack) | Python 组件框架 | 显式组合检索、排序、上下文、生成及 Agent 流程；适合学习和可控定制 | 是需要编码组装的框架，不是开箱即用的公司知识库产品 |
| [LlamaIndex](https://github.com/run-llama/llama_index) | 数据/文档与 Agent 框架 | 连接知识源、自定义索引与 retriever、接 Agent tools | 开源框架与 LlamaCloud 等托管产品不能混为一谈 |
| [LightRAG](https://github.com/HKUDS/LightRAG) | 图增强 RAG 引擎，带服务/WebUI | 实验实体关系检索、图与文本融合、跨文档关系场景 | 不是给普通混合检索换一个名称；涉及抽取与图维护成本，无统一优越性结论 |

选择判断：快速理解和体验文档 RAG，优先 RAGFlow；主要目标是业务工作流与 API 编排，考虑 Dify；要亲自掌控十个环节并做消融实验，优先 Haystack，亦可评估 LlamaIndex；明确存在跨文档关系检索需求再考虑 LightRAG。

映射十环节时，应区分提供现成能力、提供集成接口、需要业务定制。尤其 Hybrid 不必都采用 RRF，不能看到支持 hybrid 就认为底层算法一致；引用功能与逐结论事实支持验证也不是同一能力。

内网接入应验证 REDoc 变更和删除同步、逐用户授权、源版本定位和工具结果追溯。业务 API 提供实时状态，文档提供规则；这些需要与应用交付一起设计，不由通用知识库产品名称自动保证。

建议起步实验：用公开或自造语料建立十几到几十个诊断问题，包含例外、冲突和无答案；保持问题、语料、模型一致，记录命中片段、最终答案与耗时。本文只提出选型顺序，未执行部署或向外部上传内部文档。

## 官方补充来源

- [Dify LICENSE](https://github.com/langgenius/dify/blob/main/LICENSE)
- [Haystack QdrantHybridRetriever](https://docs.haystack.deepset.ai/docs/qdranthybridretriever)
- [RAGFlow DeepDoc](https://github.com/infiniflow/ragflow/blob/main/deepdoc/README.md)

与此前材料的关系：内部选型已提及 RAGFlow 与 LightRAG，但当前自建服务被描述为 SQLite+TOC+BM25+摘要向量+RRF。三者不可直接视为同一个已运行系统。
