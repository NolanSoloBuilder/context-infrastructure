---
repo: rimbo-work-context
url: https://github.com/Mindspace-ai/rimbo-work-context
role: 团队上下文系统 —— 规则、记忆、技能、定时任务
status: active
language: mixed
owner: xu
last_reviewed: 2026-05-18
---

# rimbo-work-context

## 角色

本仓库自身。给 AI coding agent 用的「上下文与记忆系统」：持久记忆、个人规则、技能、定时观察。

> 仓名用产品品牌名 `rimbo-` + 连字符，与组织其他 `mindspace_` 蛇形仓库不一致 —— 因为面向 AI agent 而非 Mindspace 产品本身。

## 技术栈

- Python（`periodic_jobs/`、`tools/`）
- Markdown（规则、上下文、文档）
- 无独立服务，按文件 + git 流转

## 关键路径

详见 [`rules/WORKSPACE.md`](../../rules/WORKSPACE.md)。要点：

- `rules/` — L3 全局约束（SOUL / TEAM / IDENTITY / WORKSPACE / members / axioms / skills）
- `contexts/` — 产物与记忆（products / planning / research / capabilities / lark_mirror / memory / repos）
- `periodic_jobs/` — 定时任务（ai_heartbeat / lark_sync / digest）
- `tools/lark/` — Lark 自建应用 client
- `docs/` — 元文档

## 与其他仓库的关系

不调用任何 Mindspace 业务仓库代码；通过本目录 (`contexts/repos/`) 维护对它们的速查信息。

## Open questions

- 何时把 `mindspace_*` 仓库的实际依赖关系（capability 卡片）开始落到 `contexts/capabilities/`
