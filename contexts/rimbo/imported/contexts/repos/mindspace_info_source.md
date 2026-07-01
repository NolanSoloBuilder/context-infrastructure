---
repo: mindspace_info_source
url: https://github.com/Mindspace-ai/mindspace_info_source
role: 基于 Codex CLI 的信源发现工具（actor/prune 循环）
status: archived
language: python
owner: unknown
last_reviewed: 2026-05-18
---

# mindspace_info_source

## 角色

**已归档。** 基于 Codex CLI 的小工具，从自然语言 prompt 出发做 actor / prune 循环，发现并清洗候选源 URL。不调独立搜索 API，纯 `codex exec` shell-out。

## 技术栈

- Python 3.11+ + uv + Hatchling 打包
- 提供 CLI：`mindspace-info-loop` / `mindspace-info-prune` / `milooop`
- prompts：`src/.../prompts/{actor,prune}.md`

## 入口

`uv tool install .` 后通过 CLI 使用。

## 归档原因（推测）

疑似被 [`mindspace_local_sql`](./mindspace_local_sql.md) 的 `zsearch` 发现流取代。最后推送 2026-05-12。

## Open questions

- 归档时间与确切原因
- 是否还有线下还在用的工作流依赖它
