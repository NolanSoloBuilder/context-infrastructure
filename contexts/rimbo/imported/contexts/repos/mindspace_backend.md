---
repo: mindspace_backend
url: https://github.com/Mindspace-ai/mindspace_backend
role: 主业务后端 —— 用户系统、频道创建/订阅，并作为 ML 端的代理层
status: active
language: python
owner: unknown
last_reviewed: 2026-05-18
---

# mindspace_backend

## 角色

Mindspace 主业务后端。承担用户/频道/订阅等核心业务逻辑，同时把 AI 相关请求（HTTP / SSE 流）反向代理到 `mindspace_ml_backend`。

## 技术栈

- Python + FastAPI 0.121
- SQLAlchemy 2 + MySQL（asyncmy / PyMySQL）
- Celery / APScheduler — 任务队列与定时
- Elasticsearch / MongoDB（Motor）/ Milvus（pymilvus）
- 对象存储：boto3 + 阿里 OSS
- Jinja 模板

## 入口

- `main.py` + `mindspace/app/`（router / service / dao / handler 分层）
- `Dockerfile` + `deploy/` 用于部署
- 配置：`resources/{ENV}.yaml`

## 数据面

- 业务 MySQL（与 [`mindspace_local_sql`](./mindspace_local_sql.md) 写的 Azure 源 DB **是两套独立数据库**）
- Mongo / ES / Milvus 主要在 ML backend 一侧使用

## 与其他仓库的关系

- 上游：[`mindspace_web_frontend`](./mindspace_web_frontend.md)、[`mindspace_app`](./mindspace_app.md) 调用本仓 API
- 下游：通过 HTTP/SSE 代理调用 [`mindspace_ml_backend`](./mindspace_ml_backend.md)

## Open questions

- 与 `mindspace_ml_backend` 的边界：哪些路由在本仓直接落地、哪些纯透传
- 当前 owner / 主要维护人
