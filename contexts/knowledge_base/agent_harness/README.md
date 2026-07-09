# Agent Harness Knowledge Base

日期：2026-07-06

这个目录不是原始资料归档，而是对 Agent Harness 相关资料理解后的结构化知识库。原始 OpenBook 成书版在 `contexts/source_materials/openbook/`；外部资料的 URL 记录在 `reference_cards.md`。

## 文件

| 文件 | 用途 |
|---|---|
| `reference_cards.md` | 外部资料的理解卡片：每条资料解决什么 Harness 问题、适合什么时候用、对应 OpenBook 哪些章节 |
| `harness_primitives.md` | 从资料中抽象出来的 Harness 设计原语：状态、工具、权限、记忆、观测、恢复等 |

## 使用方式

当讨论 Agent runtime、工具系统、记忆、多 Agent、MCP、权限或云上 sandbox 时：

1. 先读 `harness_primitives.md`，确认要讨论的是哪类设计原语。
2. 再读 `reference_cards.md`，选择 2-3 个最贴近问题的外部资料。
3. 需要具体章节时，回到 `contexts/source_materials/openbook/openbook_zh.md` 或对应官方文档。

## 入库边界

- 这里只存理解后的摘要和判断，不复制外部网页正文。
- 时间敏感信息仍以官方文档当前版本为准。
- OpenBook 当前 license 边界未确认；内部检索可以使用，外部发布或改编前要重新确认许可。
