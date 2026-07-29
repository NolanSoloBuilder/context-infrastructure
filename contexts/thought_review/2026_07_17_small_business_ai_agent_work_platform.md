# Shared Agent Workspace：产品方向与架构底稿

> 状态：讨论底稿 v0.4  
> 日期：2026-07-17  
> 目标：定义一个供单一业务方向的产品研发团队共同使用、以共享职责 Agent 为协作节点的 AI-native Workspace。

## 核心判断

这个产品的中心不是多 Agent，而是团队共享的工作上下文。多 Agent 只是把不同职责的知识、工具和权限带入协作的一种实现方式。

它也不是 Agent Builder、群聊 Bot 集合或另一套项目管理工具。产品要解决的是个人 Agent 无法解决的组织问题：每个人与自己的 Agent 合作时，信息、判断和执行历史仍然分散；Shared Agent Workspace 让团队围绕同一份上下文、同一组职责能力和同一条工作状态共同推进。

更准确的初始品类是：

> 面向产品、设计和研发团队的 Shared Agent Collaboration Workspace。

初期以产品研发团队为垂直切口，因为前端仓库、后端仓库、需求、设计和测试天然形成跨职责上下文，并且交付结果可以用代码、设计稿、测试和发布记录验证。底层架构可以支持其他业务团队，但产品首屏、概念和默认流程先围绕这一类团队设计。

## 产品边界

这个平台服务于公司内部某一个业务方向，不是公司级经营系统。现有团队仍由产品、设计、前端、后端等真实成员组成。平台在团队协作之上增加一层共享 Agent：每个职责可以创建一个由团队共同使用的 Agent，人既可以单独使用它，也可以在群聊里 `@` 它，让职责知识与执行能力进入人与人的协作过程。

这里的职责 Agent 不应被设计成人类成员的替身。产品、设计、前端、后端是便于团队理解和治理的所有权边界；Agent 内部仍应按任务依赖关系、上下文范围、工具权限和失败模式选择执行方式。一个前端 Agent 可以在一次任务中独立完成，也可以临时调用代码检索、视觉检查和测试能力。

## 暂定产品定义

这是一个面向小型业务团队的 Shared Agent Workspace。它把代码仓库、知识库、会议记录、群聊记录、工作项和执行证据组织成同一个 Workspace 的受控上下文；把职责 Agent 作为团队共享资产放进群聊和个人工作入口；把沟通结论转换成可审批、可执行、可验证的工作项。

它的核心交付是四类可核对对象：

1. 决策：目标、优先级、约束和选择理由。
2. 工作项：责任人或责任 Agent、依赖、期限、状态和阻塞原因。
3. 产物：需求、设计、代码、测试结果和发布记录。
4. 证据：来源、审批、执行 trace、diff、测试和人工反馈。

## 产品形态

产品不应该从“创建几个 Agent”开始，而应该从“创建一个业务 Workspace”开始。用户连接团队已有的协作空间、代码仓库、文档与设计资产，系统据此建立共享 Context；职责 Agent 是 Workspace 内可配置、可版本化的协作者。

### 1. Team Room

这是人与人、人与 Agent 共同工作的空间，可以嵌入飞书或 Slack，也可以在产品内提供原生界面。用户讨论、`@` 职责 Agent、引用仓库或文档，并把讨论提升为正式工作。它承担协作入口，不承担全部状态存储。

### 2. Workboard

这是产品的任务与运行界面。它显示从讨论和会议中形成的工作项、依赖、当前执行者、Agent Run、待人判断的节点、产物和验证结果。它与传统看板的差别在于：卡片不仅记录人要做什么，也承载 Agent 正在执行的真实状态与上下文。

### 3. Context Space

这是 Workspace 的共同认知层。用户能够看到已连接的仓库、文档、会议、群聊、决策和正式记忆，并知道哪些 Agent 可以读取哪些内容。Context Space 同时负责来源、时效性、权限和冲突管理，不等于一个只提供语义搜索的知识库。

### 4. Agent Studio

这是职责 Agent 的管理面。团队为产品、设计、前端、后端等共享 Agent 配置职责说明、Skills、Tools、Context Policy、权限和验收方式，并管理版本。它是平台的重要组成部分，但不应成为普通成员每天工作的首页。

### 5. Artifact & Evidence View

每次 Agent 执行都应沉淀可核对的交付物和证据，例如需求变更、设计稿、代码 diff、测试结果、浏览器截图和发布回执。用户可以从结果追溯到工作项、讨论来源、Agent 版本和工具调用。

产品的日常路径由 Team Room、Workboard 和 Artifact View 构成；Context Space 与 Agent Studio 提供配置和治理。

## 顶层技术架构

### 1. Channel Plane

连接飞书、Slack、产品内群聊、会议逐字稿和个人入口。它统一用户、群、消息、`@mention`、thread 和事件语义，不把第三方平台的数据结构直接扩散到内部系统。

### 2. Workspace Context Plane

负责连接仓库、文档、设计资产、会议、聊天和工作状态，并维护来源、权限、版本和索引。内部应保留原始对象与引用关系，再为不同 Agent Run 动态组装 Context，而不是先把所有内容压成一份公共 Prompt 或一个向量库。

这一层至少包含 Connector、Canonical Object Store、Content/Metadata Index、Relationship Graph、Permission-aware Retrieval、Memory Promotion 与 Context Assembly。

### 3. Agent Definition Plane

负责职责 Agent 的声明与版本：模型策略、instructions、Skills、Tools、Context Policy、Permission Policy、Verification Policy 和 Owner。Agent Definition 是配置资产，不等于某一次会话，也不等于正在运行的进程。

### 4. Work Orchestration Plane

负责把消息、会议和外部事件转为候选工作，把正式 Work Item 组织成有依赖的执行图，并驱动 Agent Run、等待、人类判断、重试和续接。它需要 durable state 与 event log，不能依赖一个持续不断的聊天上下文维持状态。

### 5. Agent Runtime Plane

负责真正运行 Harness：组装 Context、调用模型与 Tools、保存 checkpoint、控制 token 和工具结果预算、处理失败与恢复。一次 Run 可以由一个职责 Agent完成，也可以按任务拓扑临时创建 worker；产品无需把内部 worker 全部暴露成人类角色。

### 6. Execution Plane

提供代码 sandbox、仓库读写、浏览器、CI、数据库和第三方 SaaS 等真实执行环境。它与 Agent Runtime 分开，所有操作通过 Tool Contract、身份凭据和策略引擎进入，避免模型直接拥有长期高权限。

### 7. Trust Plane

横跨所有层，负责 Identity、RBAC/ABAC、审批策略、Secrets、Audit Log、Trace、Evaluation、Artifact Provenance 与成本计量。权限和完成判定由确定性系统执行，模型可以提出建议，但不承担最终裁决。

## 核心领域对象

第一版架构应围绕少量稳定对象建立，而不是围绕页面或 Prompt 建表：

- `Workspace`：业务团队及其资源、成员和规则边界。
- `AgentDefinition`：团队共享职责 Agent 的版本化声明。
- `Conversation` / `Meeting`：原始协作上下文和事件来源。
- `ContextObject`：仓库、文件、文档、设计、决策、消息等规范化对象。
- `WorkItem`：经过确认、可以被跟踪和执行的工作合同。
- `Run` / `Checkpoint`：Agent 一次可暂停、续接和恢复的执行。
- `Artifact`：需求、设计、代码、报告、截图等正式产物。
- `Evidence`：验证结果、来源引用和外部系统回执。
- `PolicyDecision`：访问、执行、审批和放行的确定性记录。

这些对象构成产品真正的长期资产。聊天消息只是输入之一，Agent 也只是运行这些对象的一种参与者。

## 需要避免的三个方向偏差

第一，做成通用 Agent Builder。用户可以创建 Agent，但创建能力本身不是产品价值；团队共享上下文和跨人协作才是。

第二，做成飞书或 Slack 里的多个角色 Bot。群聊是入口，缺少 Workboard、durable execution、Artifact 和 Evidence 时，它仍然只是问答增强。

第三，做成披着 AI 外壳的 Jira。工作项只是控制面的一部分。产品差异来自 Agent 能读取共同上下文、真实执行并把结果重新写回团队认知。

## 第一版系统骨架

### 1. 协作入口

平台至少接收三类输入：群聊中的人和 Agent 消息、会议逐字稿，以及用户直接发起的工作。群聊负责共同讨论，个人入口负责准备和深度执行；两者调用的是同一个团队 Agent 和同一套受控业务知识，不再为每个人复制一个彼此隔离的助手。

### 2. Workspace Context

Workspace 登记前端仓库、后端仓库、设计资产、产品文档、知识库、会议、群聊、工作项、决策、产物和执行证据。它们属于同一个上下文空间，但不会在每次调用时全部塞入模型。Context Assembly 根据 Agent、当前工作项、访问权限和 token 预算动态选择内容，并保留来源引用。

上下文至少分四层：

- Workspace Shared：团队共同认可的仓库、规则、决策和知识。
- Responsibility Scope：产品、设计、前端、后端各自长期需要的资料与 Skill。
- Work Item Context：本次任务的讨论、相关文件、依赖、审批与运行状态。
- Personal Overlay：个人草稿、偏好和未共享信息；只有主动发布后才进入团队上下文。

这个分层避免把共享 Agent 误解为所有信息对所有人和所有 Agent 无条件可见。

### 3. Shared Responsibility Agent

每个职责 Agent 都是团队版本化管理的 Harness，至少包含 `instructions`、`skills`、`tools`、`context_policy`、`permission_policy`、`verification_policy` 和运行状态。团队成员共同使用同一个 Agent 定义和职责记忆；具体会话和未发布草稿保持隔离。

职责 Agent 明确采用团队共享模式，不与真实成员建立一对一映射。前端 Agent、后端 Agent、产品 Agent 和设计 Agent 都是 Workspace 资产：由团队指定 Owner 维护定义和权限，所有获授权成员可以调用；成员加入或离开不会改变 Agent 身份，也不会带走 Agent 积累的职责知识。

共享范围包括 Agent Definition、正式职责记忆、Skills、Tools、权限策略、执行历史与验证经验。个人对话中的临时内容默认不进入共享记忆；只有经用户发布、由工作项确认，或通过既定记忆写入规则审核后，才提升为 Workspace 资产。

群聊里的人和 Agent 使用统一身份与 `@mention` 路由。Agent 回答时需要显示依据来自哪个仓库、文档、会议或决策，并明确它是在提供信息、提出工作项，还是请求执行权限。Agent 代表某项团队能力，不冒充对应岗位的真实成员作出最终承诺。

### 4. Work Item 控制平面

会议和群聊里的每一段话都属于原始 Context。只有被识别为明确行动，并经人确认后，才提升为正式 Work Item。这样可以避免 Agent 把讨论、反问或尚未达成共识的观点直接变成代码修改。

第一版状态机可以是：

`captured → proposed → clarified → approved → executing → verifying → ready_for_review → done`

每个 Work Item 保留原始讨论位置、目标、范围、责任 Agent、依赖、验收标准、审批记录、执行 checkpoint、修改内容和验证证据。审批通过后，平台才创建 Agent Run；代码类任务完成后仍需测试和代码审查，不能把 Agent 已修改当作完成。

### 5. Skill 与工具层

Skill 表达可复用的工作方法，包括触发条件、输入、步骤、工具、输出格式和验收标准。Tool 负责连接飞书、设计平台、代码仓库、浏览器、CI 和数据库。职责名称用于所有权和协作路由，Skill 是系统能够真正执行的能力单位。跨职责 Skill 可以被多个 Agent 复用，不需要复制实现。

### 6. 验收与授权

系统把查询、建议、草稿、代码修改和高影响外部操作分级。读取与分析通常可以自动运行；修改仓库必须绑定获批 Work Item，并在隔离执行环境中进行；合并、部署、删除数据等动作需要独立审批策略。任务完成必须由产物与证据共同证明，不能由 Agent 自报成功。

## 建议的 MVP 闭环

第一版只选择一条高频研发协作链路，从输入一直做到真实结果：

`会议/群聊进入 → AI 提议 Work Item → 人确认范围和验收标准 → 指派职责 Agent → Agent 修改仓库 → 自动测试 → 人工 Review → 合并并写回 Workspace`

MVP 可以先包含一个群聊、一个 Workspace、前端与后端两个仓库、四个职责 Agent，以及一个统一 Work Item 状态机。暂不追求 Agent 自由对话、复杂组织图或自动跨职责决策。

先验证四个指标：讨论转成有效 Work Item 的准确率；从审批到可 Review 产物的完成率；人需要修正 Agent 的次数；团队能否从来源和 trace 还原 Agent 为什么这样做。

## 当前待定问题

团队已经确认职责 Agent 采用团队公共角色 Agent，而不是每位成员拥有一个可被团队调用的个人代理。个人偏好和未发布草稿继续通过 Personal Overlay 隔离。

下一步需要确定一个产品决策：

第一条执行链路从哪种工作项开始。当前建议选择已明确范围的小型前端或后端修改，因为它有清楚的 diff、测试和 review 证据；跨前后端的大需求放到下一阶段。

这两个决策确定后，再定义 `AgentDefinition`、`WorkspaceContextRegistry`、`WorkItem`、`Run`、`Approval` 和 `Evidence` 的第一版数据合同。
