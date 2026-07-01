---
repo: mindspace_local_sql
url: https://github.com/Mindspace-ai/mindspace_local_sql
role: 信源发现的本地 SQL 暂存与维护工具，写 Azure 源 DB
status: active
language: python
owner: ?qihang
last_reviewed: 2026-05-18
---

# mindspace_local_sql

## 角色

Operator 工具（不是常驻服务）。完整流程：

1. 用 zeepbot 的 `zsearch` 找候选 URL
2. 调用 vendored 的 ML backend 做 RSS / feed 发现
3. 本地 SQLite review
4. `msync` 显式发布到 **Azure 源数据库**

## 技术栈

- Python 3.12 + uv + Typer
- SQLAlchemy + pyodbc（Azure SQL）+ pymysql + feedparser + httpx + Pydantic

## 入口

- CLI：`mindspace-local-sql`、`msync`
- 脚本：`./scripts/init_local_sql.sh`、`bootstrap_local.sh`、`smoke_local.sh`

## 数据面

写入 **Azure 源数据库**，与 [`mindspace_backend`](./mindspace_backend.md) 的业务 MySQL **是两套独立数据库**。

## 与其他仓库的关系

- vendor 引用 [`mindspace_ml_backend`](./mindspace_ml_backend.md) 复用 RSS / feed 发现逻辑
- 被 [`mindspace_user_simulator`](./mindspace_user_simulator.md) vendor 引用
- 疑似取代了已归档的 [`mindspace_info_source`](./mindspace_info_source.md)

## Open questions

- "approved" 流程是单人审核还是团队流
- 与 `mindspace_info_source` 的接力关系是否完成
- 主要维护人是否仅 qihang
