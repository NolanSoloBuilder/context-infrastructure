# Archify 调研：适合 Agent 的技术图表交付工具

调研日期：2026-09-20。对象按技术背景暂定为 [tt-a1i/archify](https://github.com/tt-a1i/archify)，与建筑设计平台等同名产品区分。方法：官方文档、源码、GitHub 问题报告，以及本地 CLI 正向与失败路径实测。未安装全局 Skill，未进行浏览器视觉验收。

## 判断

Archify 适合做架构讲解、技术评审和交付展示，可以作为 Agent 的图表输出能力。它把语义理解交给 Agent，把结构检查、部分布局约束、渲染和交付交给确定性程序。这种分工比要求模型自由生成整页 SVG 更容易维护。

需要保留的边界：它能检查图中引用和几何是否成立，但无法证明业务关系符合实际系统；它提供代码出处校验，但不等于自动完成代码架构分析。建议先用于单条业务链路的解释，控制图的规模，再评估批量自动化。

## 产品与技术路径

它以 Agent Skill 分发，可供 Codex、Claude Code、Cursor、OpenCode 调用，运行时要求 Node.js >=18。源码采用 MIT，品牌素材另有第三方许可说明。核心流程是：自然语言或仓库取证 → Agent 编写 typed JSON IR → 校验与修复 → 编译成独立 HTML/SVG。Agent 与渲染器职责分离，JSON 可以存入 Git 持续迭代。[package.json](https://github.com/tt-a1i/archify/blob/main/archify/package.json)、[Skill](https://github.com/tt-a1i/archify/blob/main/archify/SKILL.md)

支持 architecture、workflow、sequence、dataflow、lifecycle 五种图。查看器提供搜索、路径追踪、语义筛选、章节展示、主题切换及多种导出。Architecture Delta 比较两个已校验的 JSON 快照，呈现增删改和路由变化；它不从 PR 自动推导运行时影响或合并安全性。[项目说明](https://github.com/tt-a1i/archify)

通用自动布局、所见即所得编辑、托管分享，以及自动 Mermaid 解析未列入当前范围。Mermaid 输入通过 Agent 理解后重写成 JSON。需要避免另一种误解：workflow v2 已有受约束布局编译器，基于泳道、逻辑列和文本尺寸计算几何，不能概括为“完全没有自动布局”。[Workflow 合同](https://github.com/tt-a1i/archify/blob/main/archify/renderers/workflow/README.md)

## “可验证”覆盖什么

| 层次 | 已提供的检查 | 仍需谁负责 |
|---|---|---|
| 图表结构 | schema、节点引用、端点和图形约束 | Agent 提供真实关系 |
| 图形交付 | 布局、连线、标签间距，HTML/SVG 检查与哈希回执 | 浏览器行为和视觉判断另验 |
| 代码出处 | origin、固定 commit、文件对象、行范围存在性 | 人或 Agent 判断引用是否支持结论 |
| 架构事实 | 展示已写入 JSON 的节点与关系 | 代码、配置、运行证据与人工复核 |

源码 `verifyRepositoryEvidence` 校验本地 Git 对象与行范围，未对引用内容做语义证明；这一能力目前只支持 architecture。内部 Git 服务可以用 `local-only` 保留出处信息但不生成网页链接，仍要求 origin 身份匹配。[实现](https://github.com/tt-a1i/archify/blob/1aa1db9f9c32bcdedf6c9e9260d6162820a5d8a3/archify/renderers/shared/repository-evidence.mjs)、[作者合同](https://github.com/tt-a1i/archify/blob/main/archify/references/authoring-contract.md)

上游也明确区分交付与浏览器验证：

> “This is deterministic artifact evidence; it does not exercise the Viewer in a browser.”

来源：[Skill 的 Delivery 章节](https://github.com/tt-a1i/archify/blob/main/archify/SKILL.md)。因此 CLI 通过不能写成实际视觉效果已验收。

## 本地实测

拉取 main，固定提交 `1aa1db9f9c32bcdedf6c9e9260d6162820a5d8a3`，版本 `2.17.0-dev.1`；本机 Node.js `v25.2.1`。运行前阅读 CLI 入口，未运行依赖安装，设置 `ARCHIFY_UPDATE_CHECK_DISABLED=1`。

1. `doctor` 检查通过。
2. 用仓库自带的 `agent-tool-call.workflow.json` 执行 `deliver --quality showcase --json`：9/9 检查通过，0 错误、0 警告，生成 819,631 字节 HTML；源文件与产物均返回 SHA-256。
3. 将首条边的目标改为不存在的节点，再向同一目标文件执行交付：退出码 1，返回 `workflow/unknown-edge-endpoint` 和准确字段 `/edges/0/to`；原 HTML 逐字节保留。

这证明当前环境下基本渲染、结构化失败诊断和保留上次成功产物机制可用。输入是官方示例，不构成真实仓库自动分析能力、复杂图成功率、浏览器导出或视觉质量的验证。

证据位于 `tmp/archify_20260920/`：`delivery.json`、`failure.json`、`invalid.workflow.json`、`agent-tool-call.html` 与上游源码快照。

## 成熟度与成本

截至调研时，稳定发布清单为 `v2.16.0`，发布时间 2026-08-30；主分支为 `v2.17.0-dev.1`。本文实测与源码分析针对开发快照，不能视作稳定版的全量能力承诺。[稳定清单](https://tt-a1i.github.io/archify/skill-updates/archify/stable.json)、[稳定发布](https://github.com/tt-a1i/archify/releases/tag/v2.16.0)

独立用户在 2026-09-18 提交的 [issue #468](https://github.com/tt-a1i/archify/issues/468) 报告：某 lifecycle 图的结构校验要求增大 viewBox 高度，浏览器 containment 又要求收缩；Agent 在 98 轮中调用了 29 次 validate。报告针对 `2.17.0-dev.1`，调研时仍开放。这个案例尚未本地复现，也不能代表平均性能，但直接说明自动修复可能反复消耗模型调用。

所以成本应同时计算模型读代码、编写 JSON、修复布局的时间和 token。零运行时依赖与免费源码并不意味着端到端生成零成本。当前证据足以支持小范围试用，尚不足以声称复杂图可稳定一次生成。

## 选型

以下是基于产品合同的使用建议，并非对照性能测试：

| 需求 | 建议 |
|---|---|
| README 中简短流程、时序图，强调文本维护 | Mermaid |
| 在 Agent 对话中生成可交互、可演示、可独立分享的技术图 | Archify |
| 长期维护统一架构模型，并从模型生成多个 C4 视图 | Structurizr DSL |

[Mermaid](https://mermaid.js.org/intro/) 以文本定义和文档集成为重点；[Structurizr DSL](https://docs.structurizr.com/dsl) 以架构模型和多个视图为重点。Archify 的优势集中在 Agent 工作流、图形诊断和独立交付物，而长期架构模型治理仍需另外设计。

对当前工作，建议试点一张 Agent 工具调用链或 Workspace run 生命周期图：8–12 个主节点，输入来自已核验代码，JSON 与 HTML 一起保留。事实复核先于布局优化；连续修复不改善时停止并报告诊断。正式集成应固定版本，再验证真实案例和模型成本。

## 可借鉴的设计

最有价值的是三点：模型产出受约束中间表示；工具返回可定位、可修复的诊断；仅在完整检查通过后替换交付物。这些机制同样适用于报告、页面和工作流生成。另一方面，图表的事实正确性与展示正确性必须保持独立验收，检查数量不能替代业务证据。
