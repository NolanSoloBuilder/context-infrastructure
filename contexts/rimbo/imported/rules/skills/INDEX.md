# Skills Index

skills 是 AI 可调用的工具、流程和最佳实践。

- **想用某个能力** → 浏览下方分类，找到对应的 skill 文件
- **想加新 skill** → 参考现有文件格式，添加到对应分类，走发布 skill PR + review

## 加载策略

`rules/skills/` 下的 skills 是给 rimbo 团队 AI 默认可见的能力库。

`rules/skills/_reference_grapeot/` 是上游个人创作者向 skills（typefully、kit、ga4、个人邮件等），**默认不加载**。详见 `_reference_grapeot/README.md`。

## 协作流程类（必读）

跨人协作的核心 skill。在涉及写入 / 提议 / 改动 capability 前**必须读**。

- [`workflow_publish.md`](./workflow_publish.md) — AI 怎么走分支 + PR + 自动 merge / review。所有非个人区域的写入都从这里走。
- [`capability_use.md`](./capability_use.md) — AI 怎么发现和使用 `contexts/capabilities/` 下的能力，怎么提议新建、升级、退役。

## Workflow（工作流）

特定任务的完整流程。

- [`workflow_parallel_subagents.md`](./workflow_parallel_subagents.md) ✅ — 调用后台 agent、并行执行多个 subagent。**初次使用并行 subagent 前必读**。
- [`workflow_deep_research_survey.md`](./workflow_deep_research_survey.md) ✅ — 多 agent 并行 + 交叉验证（phase 1-3）的调研工作流。
- [`workflow_analytical_writing.md`](./workflow_analytical_writing.md) ✅ — 把调研素材转化为有判断力的分析文章。深度调研 + 写文章时两个 skill 都要读。

## BestPractice（最佳实践）

通用的工程方法论。

- [`bestpractice_ai_programming_mindset.md`](./bestpractice_ai_programming_mindset.md) ✅ — 70% 问题、成功标准、可验证性。
- [`bestpractice_ai_debugging_diagnosis.md`](./bestpractice_ai_debugging_diagnosis.md) ✅ — "代码改不好"的根因诊断决策树。
- [`bestpractice_ai_product_design.md`](./bestpractice_ai_product_design.md) ✅ — AI 产品设计原则：线性聊天 vs 知识工作、感知规则解耦。
- [`bestpractice_api_key_management_1password_cli.md`](./bestpractice_api_key_management_1password_cli.md) ✅ — 用 1Password CLI 安全管理密钥，团队 vault 共享。
- [`bestpractice_interview_evaluation.md`](./bestpractice_interview_evaluation.md) ✅ — 面试评估框架：trait > skill、AI 作弊识别、技术深度探测。
- [`bestpractice_markdown_html_conversion.md`](./bestpractice_markdown_html_conversion.md) ✅ — markdown → html 实践。
- [`bestpractice_temporal_info_verification.md`](./bestpractice_temporal_info_verification.md) ✅ — 时间敏感信息验证。
- [`bestpractice_staged_approach.md`](./bestpractice_staged_approach.md) ✅ — 分阶段工作法：隔离-处理-验证闭环，破坏性操作前 dry run。
- [`bestpractice_multi_agent_analysis.md`](./bestpractice_multi_agent_analysis.md) ✅ — 多 agent 并行 analysis，topic 分割与交叉验证。

## 检索类

- [`semantic_search.md`](./semantic_search.md) ⚙️ — 利用向量相似度检索深层背景与观点演变。覆盖 `contexts/` 与 `contexts/lark_mirror/`。

## Lark 集成（Phase 2）

- [`lark_read.md`](./lark_read.md) ✅ — AI 怎么读 Lark 文档（镜像 → lark-cli → fallback 三段路径、隐私边界）
- [`lark_write.md`](./lark_write.md) ✅ — AI 怎么写回 Lark（必须先经过 git 的约束）

## PRD 流程

PRD 起草 → 评审 → 状态切换 → 归档，都依赖 lark-cli（见 setup_guide Step 2.5）。

- [`prd_draft_from_lark.md`](./prd_draft_from_lark.md) ✅ — Lark 拉草稿到本地、迭代、推回 Lark
- [`prd_review.md`](./prd_review.md) ✅ — 本地写完 → 推 Lark → IM 通知评审群
- [`prd_status_change.md`](./prd_status_change.md) ✅ — draft / review / approved / shipped / superseded 切换 + 群通知
- [`prd_archive.md`](./prd_archive.md) ✅ — Lark 上已定稿 PRD 镜像到 `contexts/lark_mirror/`

## 记忆写入（Phase 3）

- [`memory_write.md`](./memory_write.md) ✅ — AI 怎么把观察写到自己 `people/<handle>/`、团队 `OBSERVATIONS.md`、提议 L3 改动

## 待补充（Phase 4+）

- `embedding_index.md` — 向 lark_mirror 和 contexts 灌 embedding,服务 semantic_search
- `digest_compose.md` — 把仓库变化抽成 Lark 群消息(目前由 `periodic_jobs/digest/` 直接调 AI,等需求稳定再沉成 skill)

## 添加新 skill 的格式

```markdown
# Skill: 名称

## When to Use
什么情况下触发

## Prerequisites
需要什么工具/配置

## 步骤
1. ...
2. ...

## 示例
具体命令或代码

## 关联
其他相关 skill / 协议
```

加完后在本 INDEX.md 对应分类下加一行。skills 目录修改属敏感清单，PR + review。

## 状态图例

- ✅ 直接可用，最多 15 分钟即可上手
- ⚙️ 需要额外配置，不配不影响其他能力
- 🚧 在做，未完成
