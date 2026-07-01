# 使用教程 — 这个 workspace 平常装什么

写给徐昊本人的使用指南。比 setup_guide 更进一步，回答的是「配好之后我每天到底用它做什么」。

## 心智模型

**所有让 AI 参与的工作都放进来跑。**

不是「重要的工作才放这里」，而是反过来：只要 AI 介入，就在这个目录里开工。Context infrastructure 的价值来自数据沉淀——你不在这里干活，系统就没东西可积累，AI 永远只懂 USER.md 那点静态信息。

判断一件事要不要进 workspace 的标准只有一个：**会不会让 AI 参与？** 会，就进来。

## 四类工作 + 对应路径

### 一、写代码 / 跑脚本

任何一次性项目、临时脚本、试验性代码：`adhoc_jobs/<project_name>/`。

- 临时性的加 `tmp_` 前缀（例如 `tmp_scrape_test/`）
- 命名一律 snake_case
- 即便只是「试一下某个库」也开个目录，别散到电脑各处

理由：未来 AI 要参考「上次怎么做的」时，它在这个目录下搜，搜得到才能复用。散在 `~/Desktop` 或随机文件夹的代码等于丢失。

### 二、调研 / 写报告

让 AI 查资料、深度调研、写分析文章：产物进 `contexts/survey_sessions/`。

这一类是 ROI 最高的场景。配套两个 skill：

- `rules/skills/workflow_deep_research_survey.md` —— 多 Agent 并行调研
- `rules/skills/workflow_analytical_writing.md` —— 把素材转成有判断的分析

用法范式：直接告诉 AI「我想调研 X，按 deep research workflow 走」。它会读 skill、拆维度、派多个 subagent 并行、交叉验证、最后写报告。一旦报告在 `survey_sessions/` 里，未来任何相关问题 AI 都能引用。

### 三、思考 / 复盘 / 方法论

工作中冒出来的判断、踩过的坑、形成的方法：`contexts/thought_review/`。

把易逝的「想法」变成可检索资产的地方。

- 「这次 A/B test 我学到了什么」
- 「这个架构决策的真正考量」
- 「这次和团队的分歧本质上是什么」

写一篇丢进去。三个月后翻出来，是判断力的累积。

### 四、个人信息与任务管理

- 日常碎片、日志：`contexts/daily_records/`
- 方法层的总结：`contexts/thought_review/`

## 系统建设：什么时候动 rules/

`rules/` 是 AI 的「操作系统」，但**不是想到什么就往里塞**。判断信号是：**这条指令会不会反复用？**

| 反复发生的事 | 应该写进 |
|---|---|
| 反复纠正同一类沟通方式 | `USER.md` 或 `COMMUNICATION.md` |
| 反复教 AI 同一个工作流 | `rules/skills/workflow_xxx.md` |
| 反复做同一类 API 调用 | `rules/skills/api_xxx.md` |
| 形成了反复用的决策原则 | `rules/axioms/xxx.md` |

一次性的扔 `adhoc_jobs/`；反复的提到 `rules/`。

## 关于继承自原作者的 axioms 和 skills

repo 里那 43 条公理和 25+ 个 skill 是 grapeot 一年沉淀的，**不是你的**。处理方式：

1. 当背景知识扫一遍，留个印象
2. 看到共鸣的标注下来
3. 不适用的（天文摄影、咖啡、原作者的特定判断）该删就删
4. 你自己的从真实工作中积累，参考它们的格式而非内容

不要直接套用。原作者的认知不能替代你的认知。

## 一个典型工作日的样子

> 上午想到一个产品 idea，让 AI 帮忙做竞品调研。
> → `contexts/survey_sessions/2026-05-15_competitor_research.md`

> 下午写一个数据处理脚本试 idea。
> → `adhoc_jobs/idea_data_pipeline/`

> 调试时发现 AI 反复在某个错误模式上栽坑，纠正了三次。
> → 写一条进 `rules/skills/bestpractice_xxx.md` 或更新 USER.md

> 晚上复盘今天的判断，记下「为什么这个 idea 我决定不做」。
> → `contexts/thought_review/2026-05-15_idea_kill_reasoning.md`

一天下来，repo 里多了 4 个文件。下周 AI 就能引用这些做更深入的判断。

## 多久能感受到价值

- **当下**：USER.md 已经在生效，AI 沟通风格立刻不一样
- **2-3 周**：`contexts/` 开始有内容，AI 能引用上下文
- **1-2 月**：如果配了 observer/reflector，开始自动识别工作模式
- **6+ 月**：系统真正了解你的判断逻辑

不要追求一开始就完美。先用，让数据流起来，rules 反过来从使用中长出来。

---

_最后更新：2026-05-15。这份指南本身也会随实际使用方式迭代。_
