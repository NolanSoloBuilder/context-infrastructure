# OpenBook Source Materials

日期：2026-07-06

这里归档 `OpenBook: 构建 AI Agent 的 Harness 工程学` 的本地成书版材料。

## 文件

| 文件 | 用途 | 原始路径 | sha256 |
|---|---|---|---|
| `openbook_zh.md` | 主阅读源 | `/Users/xuhao/Downloads/OpenBook-zh.md` | `23c189c725eb417e65f5c3946c141d15edaa6476130565b579353bf428cce487` |
| `openbook_zh.pdf` | 页数、目录和版式验证源 | `/Users/xuhao/Desktop/OpenBook-zh.pdf` | `7e7a0f8af76d3bde8aee87e161b53643180a9df6fd73cf853c09124a3947f92c` |

## 使用方式

默认读 Markdown，PDF 只用于验证成书版标题、页数、目录和版式。

```bash
rg -n "Chapter 18|MCP|Skills|Plugin|四根支柱|AGENTS.md|Dream|记忆系统|权限模型|工具编排" contexts/source_materials/openbook/openbook_zh.md
pdfinfo contexts/source_materials/openbook/openbook_zh.pdf
```

## 相关上下文

- `contexts/survey_sessions/2026_06_18_openbook_context_support.md`
- `rules/skills/openbook_agent_harness.md`

## 边界

当前未确认 OpenBook 的可再分发 license。内部检索和上下文索引用这个目录；对外引用或改编时，先重新确认许可。
