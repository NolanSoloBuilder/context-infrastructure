# 用 Muse 证明企业 Agent 与 FDE 交付能力

核验日期：2026-09-09。用户明确为 Muse 研发负责人，目标是通过 Demo 证明企业 Agent 开发能力与复杂问题处理水平，并联系业界方案；源码作为证据，不做逐文件讲解。

## 证据范围

只读本地克隆：ai-sdk/main/fa268825，moduxserver/master/4777a648，modux/main/6a9e3d4。未启动服务或执行测试，不能将代码存在解释成线上版本或业务收益已验证。

## 主叙事

建议主张：围绕设计与开发业务，组织企业资产、模型决策、执行反馈和产物状态，使生成过程可以控制、恢复和验收。每个主题按业务困难、朴素方案失败方式、实际设计、取舍、指标、迁移到其他企业场景六项讲述。

### 1. 控制权与编排

源码：moduxserver/src/app/agentInstance/workflows/rn-product-v2.workflow.ts:318,2684。输入对应不同 Pipeline；Hub 的 route_to_pipeline 使用枚举 schema，执行时更新状态并跳到首节点；Hub 配置禁用 shell 工具。

可证明：模型路由和程序化执行约束组合。不能仅凭节点数量证明多 Agent 或自主性。取舍：受限路径更可控，但新增场景需要维护节点契约。

### 2. 企业资产与上下文

源码：moduxserver/src/app/material/services/delight-search-recall.service.ts:153。存在 Figma 组件实例上下文优先路径，以及消息、BDD、页面关键词与技术栈共同组装召回上下文。不可把代码中的 hybrid 标签直接解释成 BM25 + 向量算法。

可证明：将企业组件资产和设计证据组织成模型可用的信息。可迁移到客户产品目录、合同条款、SOP 和业务实体访问；不等同于已经构建 Palantir Ontology。

### 3. 版本与执行恢复

源码：moduxserver/src/app/task/controllers/task.controller.ts:2085；src/app/chatVersion/services/chat-version.service.ts:1288。恢复会检查有效基线与缓存运行时是否一致；代码版本沿 active path 查找祖先。

可证明：恢复需要对齐运行状态与产物分支，不能只重放聊天记录。可联系 LangGraph persistence，不能宣称同等 durable execution 保证或外部副作用自动回滚。

### 4. 有限自动修复

源码：moduxserver/src/app/chatVersion/services/chat-version.service.ts:4270。链路根版本计数条件更新、第二次修复必须有第一次已落库产物、新协议预占 pendingTurnId，旧前端仍只允许一次。

注意根 AGENTS.md 的“一次修复”描述不足以覆盖当前新协议，讲解应以源码为准。可证明的复杂度是并发、修复身份、预算、协议兼容与人工处理边界，而非“模型会自我反思”。

## 业界联系（能力类比，不是采用声明）

- Anthropic Managed Agents 将 session、harness、sandbox 分开：https://www.anthropic.com/engineering/managed-agents 。用来讨论执行环境、调度与持久化的职责；本轮未核验 Muse 沙箱安全隔离。
- LangGraph persistence：https://docs.langchain.com/oss/python/langgraph/persistence 。用于对比状态保存与恢复问题；不是宣称 Muse 使用 LangGraph。
- Palantir AIP：https://www.palantir.com/docs/foundry/aip/overview 。其产品以 Ontology 连接数据与 AI 应用；Muse 的企业组件资产接入可在客户业务语义层面类比，但能力范围不同。
- Anthropic Agent Evals：https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents 。用于区分执行轨迹和最终业务结果，评测应覆盖完成质量、稳定性与成本。

## 面试中还需用户真实数据

团队/个人职责、用户群、使用规模、业务基线、原型至验收时间、人工修改量、首次预览成功率、修复后成功率、P95 延迟、单次有效任务成本。没有数据的项目只作为待衡量指标，不编造收益。

建议演示顺序：业务任务→设计及组件上下文→生成预览→约束下增量修改→经验证的失败恢复或版本切换→评测与生产边界。只演示确认可复现的能力。

下一步教学按案例展开：先控制权分配，其次上下文工程、状态恢复、质量评测，最后客户需求澄清与交付经济性。避免堆术语与框架名称。
