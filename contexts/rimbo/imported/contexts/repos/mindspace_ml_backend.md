---
repo: mindspace_ml_backend
url: https://github.com/Mindspace-ai/mindspace_ml_backend
role: ML 后端 —— 对话/画像、内容抓取、信源发现/匹配、第三方集成、向量检索、MCP server
status: active
language: python
owner: unknown
last_reviewed: 2026-05-18
---

# mindspace_ml_backend

## 角色

Mindspace 的 AI / 数据侧后端，七仓中事实上的「内部公共能力库」（被 backend、local_sql、user_simulator 三处引用）。

承担：

- 对话与用户画像
- 内容抓取（RSS / 播客 / 第三方源）
- 信源发现与匹配
- 第三方集成：Gmail / Twitter / LinkedIn / Notion
- 向量检索
- MCP server（消费者待确认）

## 技术栈

- Python + FastAPI 0.115 + Celery + Celery Beat
- LLM 栈：openai 1.109 / anthropic 0.75 / litellm / langgraph 1.0 / google-genai / Vertex
- 向量库：Zilliz / pymilvus
- 数据：MongoDB / MySQL / Elasticsearch

## 入口

- 启动模块：`mindspace.app.launch`
- 部署：`script/deploy_ml_backend.py`，蓝绿
- 容器双角色：`web`（HTTP）/ `background`（worker + beat）
- 流量：通过宿主机 Nginx `/ml/api/` 反代

## 与其他仓库的关系

- 被 [`mindspace_backend`](./mindspace_backend.md) 通过 HTTP / SSE 代理调用
- 被 [`mindspace_local_sql`](./mindspace_local_sql.md) 通过 vendor 软链复用 RSS / feed 发现逻辑
- 被 [`mindspace_user_simulator`](./mindspace_user_simulator.md) 通过 vendor 软链复用

## Open questions

- 是否直接对外服务（除被 `mindspace_backend` 代理外）
- MCP server 的实际消费者
- 当前 owner / 主要维护人
