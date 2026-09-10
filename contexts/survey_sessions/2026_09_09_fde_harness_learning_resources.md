# 企业级 FDE 与 Agent Harness 学习资料

检索日期：2026-09-09。用户纠正缩写为 FDE，按 Forward Deployed Engineer 整理。本次只新增学习笔记，不修改代码或既有笔记。

学习目标：把客户业务问题转成可验收的 Agent 应用，再理解支撑它持续执行的工具、状态、权限、恢复和评测机制。以下排序是学习建议，不代表行业采用率。

## 企业交付与 FDE

1. [Anthropic FDE 岗位说明](https://job-boards.greenhouse.io/anthropic/jobs/5302966008)：用于校准工作范围，关注客户协作、生产部署和把交付经验反馈到产品。它是岗位说明，不是教程，也不能代表所有公司的 FDE。
2. [Palantir Ontology Overview](https://www.palantir.com/docs/foundry/ontology/overview)：学习把企业数据映射成业务对象、关系、动作及权限。练习把订单、客户、审批状态和可执行动作画成业务模型。页面提供官方学习课程入口；平台概念可借鉴，产品 API 属于 Palantir。
3. [Uber：Enhanced Agentic-RAG](https://www.uber.com/us/en/blog/enhanced-agentic-rag/)：2025-05-29 的第一方工程案例。重点读文档解析、表格保真、混合检索、专家构建的测试集及评测迭代。文章明确使用内部 Langfx 与 LangGraph；这是当时的案例，不是当前完整生产栈审计。
4. [12-Factor Agents](https://github.com/humanlayer/12-factor-agents)：作者提供的生产工程原则，关注控制流、上下文、工具调用、执行状态与暂停恢复。适合把原则改写为项目验收项。

## Agent Harness

5. [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)：先理解 Workflow、Agent、工具反馈循环，以及何时增加编排复杂度。
6. [Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)：理解跨上下文窗口的任务交接、初始化、增量推进和进度产物。不要把特定编码实验直接视为所有企业 Agent 的固定架构。
7. [Claude Agent SDK Overview](https://code.claude.com/docs/en/agent-sdk/overview)：用官方 SDK 对照工具执行、会话及运行控制机制；沿文档继续读 permissions、hooks 和 sessions。先做一个单 Agent 小任务。
8. [LangGraph JavaScript Persistence](https://docs.langchain.com/oss/javascript/langgraph/persistence)：学习检查点、状态保存和恢复；结合中断文档设计人工介入。重点验证恢复是否重复触发业务副作用。
9. [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)：学习任务、轨迹、结果和评分器的分工。业务写入成功应依赖系统回执和状态检查；语义质量可以结合人工或模型评审。
10. [Harness Design for Long-Running Application Development](https://www.anthropic.com/engineering/harness-design-long-running-apps)：进阶读物，研究 planner、generator、evaluator 的分工和成本取舍。先完成单 Agent 练习，再评估是否需要多 Agent。

官方课程补充：[Introduction to Agent Skills](https://academy.claude.com/courses/introduction-to-agent-skills)。适合把企业流程与操作知识整理成可复用资源，不能替代运行时和生产交付课程。未实测课程注册及账号访问条件。

## 中文材料

仓库已有 [OpenBook 中文 Markdown](../source_materials/openbook/openbook_zh.md)。通过本地 OpenBook Agent Harness 索引核对了目录与使用边界。建议读 Part I、Part II–IV、Appendix D，再按需补多 Agent 与云部署章节。它是设计模式和伪代码参考，书中具体产品内部实现与 API 状态需由当前官方文档或代码验证。

## 建议阅读顺序与练习

第一阶段：FDE 岗位说明 → Palantir 业务建模 → Building Effective Agents。产物是一页业务任务说明：当前流程、用户角色、数据来源、成功标准、人工接管位置。

第二阶段：Uber 案例 → 12-Factor Agents → Claude Agent SDK。产物是一个运营活动助手教学 Demo：检索制度、查询实时资格、生成草稿；用 mock 数据起步时明确标注。

第三阶段：LangGraph Persistence → 长运行 Harness → Evals。为同一 Demo 增加中断恢复、工具超时处理、幂等、权限校验和审计轨迹；准备约 20 条正常与异常任务。这个数量是起步练习建议，不是生产质量门槛。

第四阶段：阅读进阶 Harness 文章，检查多 Agent 是否确实解决已观察到的问题。记录成功率、延迟、成本及人工介入率，区分验收目标与实测结果。

同一案例同时训练 FDE 与 Harness：FDE 决定问题、业务价值、系统约束和验收方式；Harness 实现执行循环、状态、权限与恢复。权限隔离、幂等、重试和业务回读属于本笔记提出的实践要求，不声称任意 SDK 默认自动提供。
