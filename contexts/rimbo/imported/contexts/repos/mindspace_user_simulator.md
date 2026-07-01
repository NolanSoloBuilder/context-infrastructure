---
repo: mindspace_user_simulator
url: https://github.com/Mindspace-ai/mindspace_user_simulator
role: 本地用户模拟器 —— 用 persona 模拟用户消费信息并提出后续问题
status: active
language: python
owner: ?qihang
last_reviewed: 2026-05-18
---

# mindspace_user_simulator

## 角色

本地评测 / 研发用工具。用 Markdown 定义的 persona 模拟用户如何消费信息并提出后续问题，输出对 Codex 或 fake backend 的多轮交互记录。

## 技术栈

- Python 3.12 + uv + Typer + Pydantic
- 外部依赖：`langwatch/scenario`（vendored）
- 通过符号链接引用：`vendor/mindspace_ml_backend`、`vendor/mindspace_local_sql`

## 入口

- CLI：`mindspace-user-simulator` / `musim`
- 拉外部仓：`./scripts/vendor_setup.sh`
- 数据存储：本地 SQLite（runs / consumption / questions / turns / interactions）

## 与其他仓库的关系

- vendor 引用 [`mindspace_ml_backend`](./mindspace_ml_backend.md) 与 [`mindspace_local_sql`](./mindspace_local_sql.md)
- 不直接调用业务后端

## Open questions

- 是测试 / 评估工具还是研发阶段产品的一部分
- 与 `mindspace_local_sql` 的运行时耦合度（仅 vendor 引用还是会写共享 DB）
- 主要维护人是否仅 qihang
