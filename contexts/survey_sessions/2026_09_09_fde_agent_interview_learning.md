# FDE Agent Demo 面试学习计划

日期：2026-09-09。用户希望基于个人画像快速学习，并准备讲解 Agent Demo。FDE 暂按 Forward Deployed Engineer 理解；面试时间、岗位描述、Demo 项目待确认。

## 个性化起点

基于用户提供的工作区画像：已有前端/RN、业务 API、配置与发布、真实链路验证经验。教学从这些经验映射到 Agent 应用工程，不预设用户已经具备模型训练或 Agent 生产经验。既有业务经历可以解释设计判断；教学案例不得包装为已完成的 AI 项目。

## 学习顺序

1. Agent 原理：模型提出工具调用，运行时校验并执行，结果回传模型；区分 Workflow、Agent、RAG。
2. 工具与状态：参数契约、错误语义、授权、幂等、超时后回读、检查点、恢复与停止条件。
3. 企业知识：混合检索、重排序、版本和 ACL、原文引用、结构化实时数据直接访问业务 API。
4. 质量与交付：真实任务集、业务结果、失败分类、调用轨迹、延迟与成本、试点及回退。
5. 面试演练：业务问题、架构选择、正常与失败路径演示、证据与限制、生产差距。

教学方法：每轮一个关键概念，用业务例子解释，再给面试表达模板和一道追问。根据用户回答纠正概念，不一次堆积框架名词。

## 第一课：运营活动助手（仅教学案例）

任务：检查商家是否具备活动资格，依据制度和实时接口解释原因，满足条件时生成活动草稿，按产品授权规则提交。

RAG 检索活动制度；API 查询商家与资源当前状态；Agent 根据结果选择下一步；Workflow 固定提交前校验、必要确认和结果回读。运行时负责身份权限与工具调用，模型不直接拥有数据库执行权。

自然语言含糊、证据不齐的部分可以使用模型；预算、库存、资格硬规则、幂等和权限由业务系统执行。停止条件包含完成、需用户澄清、不可恢复错误、调用和时间预算耗尽。

关键面试表达：模型负责理解目标并提出行动，执行层负责校验和执行；用真实环境回执确认业务成功。自动程度由风险和产品授权设计决定。

第一道练习：用户要求直接创建活动时，哪些步骤适合模型判断，哪些必须由确定性代码或业务接口控制？

## Demo 讲解结构（建议）

以十分钟为例：业务与指标 1 分钟，架构与取舍 2 分钟，正常路径 3 分钟，失败处理 2 分钟，评测与生产差距 2 分钟。没有实测的数据只能称为验收目标；mock、真实接口和生产能力明确区分。

## 原理来源

Anthropic, Building effective agents：https://www.anthropic.com/engineering/building-effective-agents 。用于 Workflow/Agent 区分及工具反馈循环等基础原理。原文提醒工具生态已经变化，不据此声称某框架是当前标准。

关联笔记：2026_09_09_fde_enterprise_knowledge_retrieval.md。2026_09_08_fde_tech_stack.md 的招聘与采用样本仅为历史参考，本轮未重新核验，不作当前岗位要求断言。

## Muse Demo 页面核验

用户提供 https://muse.devops.xiaohongshu.com/chat/20303 ，本轮通过本地 Chrome 查看。

已观察：需求文字及 Figma 圈选导出附件；构建过程展示 pipeline 路由、设计稿概览、Skill 读取、页面结构与组件实例读取、RN 组件和图标搜索、组件详情与用法召回、项目文件读写和目录查看；右侧成功渲染移动端双列内容页；存在版本选择及下载、发布入口，未执行下载或发布。文档明确部分页面流程待补充，轨迹包含 mock 文件。

证据边界：工具名称和执行列表不能证明底层使用 MCP、向量检索、具体模型或某种沙箱；未确认构建测试命令、自动错误修复、真实业务 API、完整交互与发布闭环。浏览器预览不等于原生 RN 真机验证。

教学重点：用设计稿和组件库理解上下文工程与企业资产接入；用读写轨迹理解工具契约与 Agent 执行循环；用文档、代码和预览的一致性理解验收；面试需要区分系统展示能力与用户本人负责的实现。

操作异常：检查时误将建议按钮“关闭 Doc”作为收起面板点击，实际触发关闭 Doc 共创，页面提示现有文档仍保留。已向用户说明，未继续操作相关按钮。

## REDoc 代码库入口核验

通过 redoc Skill 与 hi CLI 搜索并读取《Muse 开发手册》：https://docs.xiaohongshu.com/doc/e66584be62e2e9fbc8d42e7a29f815ec 。文档明确列出前端 fe/shopping/ai-sdk（应用目录 apps/code-preview-2）、服务端 modular/moduxserver、底层框架 fe/devinfra/modux（packages/agent，包 @xhs/modux-core）。这是文档中的仓库映射，本轮尚未读取远端源码。

仓库地址：
- https://code.devops.xiaohongshu.com/fe/shopping/ai-sdk
- https://code.devops.xiaohongshu.com/modular/moduxserver
- https://code.devops.xiaohongshu.com/fe/devinfra/modux

手册顶部与正文的服务端分支记录不一致：顶部写 master 为 prod，正文仍有 feat-init-v2 和 630/830 存档信息；不能直接当作当前有效分支或本会话修改绑定。

相关但不能冒充 Muse 主仓：codewiz-subagent-node。其治理文档 https://docs.xiaohongshu.com/doc/cf78dad38e88aeb7bcc50955aa2b39c6 记录业务 Agent、运行时拆分、Codewiz 桥接，并列出 RN Agent Owner 为南冬。实际迁移状态待源码核验。Modux 开发指南 https://docs.xiaohongshu.com/doc/6c49260395fdcca793084e2d72a95f51 包含 Muse Workflow 示例，适合后续理解编排与工具机制。
