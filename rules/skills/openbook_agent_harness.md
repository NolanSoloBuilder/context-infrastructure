# OpenBook Agent Harness 上下文索引

## 元数据

- **类型**: BestPractice
- **适用场景**: Agent Harness 架构、Agent runtime、工具系统、权限模型、多 Agent、记忆系统、MCP、Skills、Plugin、云上 sandbox 设计讨论
- **创建日期**: 2026-07-06
- **主要上下文**: `contexts/survey_sessions/2026_06_18_openbook_context_support.md`
- **仓库源文件**: `contexts/source_materials/openbook/openbook_zh.md`
- **仓库验证文件**: `contexts/source_materials/openbook/openbook_zh.pdf`
- **Harness 知识库**: `contexts/knowledge_base/agent_harness/`

---

## 什么时候使用

用户讨论下面这些问题时，先用这个 skill 定位 OpenBook 章节，再回到真实代码、官方文档或当前项目约束做验证：

- Agent runtime / Agent Harness 应该怎么建模
- Agent loop、流式响应、错误恢复、context compaction 怎么设计
- 工具系统的 schema、注册、调度、并发、输出预算怎么设计
- 权限、审批、风险分级、Hook、sandbox 怎么分层
- Subagent / Coordinator / Team / Swarm 怎么隔离和编排
- System Prompt、AGENTS.md、记忆文件、Dream 整合怎么组织
- MCP、Skills、Commands、Plugin 的边界怎么划分
- 云上 Agent 系统如何围绕 `CONSTRAIN / INFORM / VERIFY / CORRECT` 落地

## 使用流程

1. 先读 `contexts/survey_sessions/2026_06_18_openbook_context_support.md`，获取本 workspace 已确认的结论、边界和路由表。
2. 需要先建立设计框架时，读 `contexts/knowledge_base/agent_harness/harness_primitives.md`。
3. 需要找外部参考资料时，读 `contexts/knowledge_base/agent_harness/reference_cards.md`。
4. 需要具体 OpenBook 内容时，以 `contexts/source_materials/openbook/openbook_zh.md` 为主源，用 `rg` 定位章节，再用 `sed` 读相关片段。
5. 需要确认成书版页数、标题、目录或版式时，使用 `contexts/source_materials/openbook/openbook_zh.pdf` 做验证。PDF 是验证源，不是主解析源。
6. 把 OpenBook 当作设计模式索引和问题清单，不把它当作某个闭源产品当前实现的事实来源。
7. 涉及最新 API、官方规范、产品能力或安全边界时，继续查真实代码或官方文档。

## 快速路由

| 当前问题 | 先查章节 |
|---|---|
| `Agent = LLM + Harness`、运行时全景 | Part I，Chapter 1-2 |
| Agent loop、LLM API、流式响应、重试、上下文压缩 | Part II，Chapter 3-5 |
| 工具接口、工具注册、工具巡礼、工具并发和结果预算 | Part III，Chapter 6-8 |
| 权限模型、风险分级、自动审批、Hooks | Part IV，Chapter 9-11 |
| 子 Agent、Coordinator、后台任务、Team/Swarm | Part V，Chapter 12-15 |
| System Prompt、动态上下文、文件型记忆、Dream 前置 | Part VI，Chapter 16-17 |
| MCP、Skills、Commands、Plugin | Part VII，Chapter 18-20 |
| Dream 系统、Agent 设计原则 | Part VIII，Chapter 21-22 |
| OpenHarness、云上 sandbox、自修复、从零部署 | Part IX，Chapter 23-26 |
| 最小 Agent Harness 教学骨架 | Appendix D |

## 常用定位命令

```bash
rg -n "Chapter 18|MCP|Skills|Plugin|四根支柱|AGENTS.md|Dream|记忆系统|权限模型|工具编排" contexts/source_materials/openbook/openbook_zh.md
sed -n '6040,6890p' contexts/source_materials/openbook/openbook_zh.md
sed -n '8670,9560p' contexts/source_materials/openbook/openbook_zh.md
pdfinfo contexts/source_materials/openbook/openbook_zh.pdf
pdftoppm -png -f 1 -l 3 contexts/source_materials/openbook/openbook_zh.pdf tmp/pdfs/openbook_zh_verify/page
```

## 可信边界

- 本书适合做架构问题清单、术语框架和设计模式参考。
- 内容大量来自架构分析和伪代码，不能直接当作可运行框架。
- 书中提到的 MCP、Agents SDK、云服务和模型 API 状态可能过时；时间敏感内容必须重新核验。
- 当前上下文未确认 license，避免把大段原文复制进仓库或对外发布改编内容。
- 引用本书观点时，最好写成“OpenBook 提供了一个可用的设计框架”，再补真实代码或官方文档证据。

## 变更日志

| 日期 | 变更 |
|---|---|
| 2026-07-06 | 基于本地 `OpenBook-zh.md` 和 `OpenBook-zh.pdf` 增加长期上下文索引 |
