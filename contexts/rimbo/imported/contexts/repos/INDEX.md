# Repos Index

Mindspace-ai 组织下代码仓库速查（截至 2026-05-18 扫描）。详见 [`./README.md`](./README.md) 与各仓库卡片。

## 当前仓库

| 仓库 | 角色 | 技术栈 | owner（推断） | 状态 |
|---|---|---|---|---|
| [mindspace_backend](./mindspace_backend.md) | 主业务后端：用户/频道/订阅 + ML 代理层 | Python · FastAPI · MySQL | unknown | active |
| [mindspace_ml_backend](./mindspace_ml_backend.md) | ML 后端：对话/画像/抓取/检索/MCP | Python · FastAPI · Celery · LiteLLM | unknown | active |
| [mindspace_web_frontend](./mindspace_web_frontend.md) | Rimbo 品牌站 + 产品 web app（一体） | TS · React · Vite · Tailwind | ?bravohenry / ?norahe0304-art | active |
| [mindspace_app](./mindspace_app.md) | 移动端 App（iOS / Android） | TS · React Native · Expo | unknown | active（节奏偏慢） |
| [mindspace_user_simulator](./mindspace_user_simulator.md) | 本地用户模拟器（评测/研发用） | Python · Typer · vendor 多仓 | ?qihang | active |
| [mindspace_local_sql](./mindspace_local_sql.md) | 信源发现的本地 SQL 工具，写 Azure 源 DB | Python · Typer · pyodbc | ?qihang | active |
| [rimbo-work-context](./rimbo_work_context.md) | 本仓库：团队上下文 / 规则 / 周期任务 | Python · Markdown | xu | active |

## 已归档

| 仓库 | 角色 | 状态 |
|---|---|---|
| [mindspace_info_source](./mindspace_info_source.md) | Codex actor/prune 工具，疑似被 local_sql 取代 | archived |

## 拓扑速记

```
       移动端           web 前端
   mindspace_app   mindspace_web_frontend
         \              /
          \            /
       mindspace_backend          ←  业务 MySQL
              │
              ↓ HTTP/SSE 代理
       mindspace_ml_backend       ←  Mongo / ES / Milvus
              ↑
              │ vendor 引用
       mindspace_local_sql  ──→   Azure 源 DB（独立）
              ↑
              │ vendor 引用
       mindspace_user_simulator   ←  本地 SQLite
```

- 业务 MySQL 与 Azure 源 DB **是两套独立数据库**
- `mindspace_ml_backend` 是事实上的内部公共能力库（被 backend、local_sql、user_simulator 三处引用）
- `mindspace_info_source` 已归档，疑似被 `mindspace_local_sql` 的发现流取代

## 命名规律

- 一律 `mindspace_` 前缀 + 蛇形命名 + 单数
- 例外：`rimbo-work-context` 用产品品牌名 + 连字符
- 仓名（开发视角）≠ 产品名（用户视角）：web_frontend 内部 package 名是 `rimbo-landing`

## 待澄清

参见各仓卡片底部「Open questions」段。汇总：

- 各仓库的真实 owner（目前多数是按 commit 作者推断）
- `mindspace_app` 根目录是否真的 commit 了密钥文件（`credentials.json` / GCP service account JSON）—— 风险点，与本上下文任务并行处理
- `mindspace_app` 节奏偏慢（最近推送 2026-05-01，停滞约 17 天）—— 是否仍在主航道
