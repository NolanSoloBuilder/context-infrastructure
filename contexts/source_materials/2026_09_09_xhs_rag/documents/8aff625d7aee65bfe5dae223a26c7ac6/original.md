# RedAgenticRAG 系统架构文档

## 目录

1. [系统概述](#系统概述)

2. [核心数据模型](#核心数据模型)

3. [文档输入（Ingestion）](#文档输入ingestion)

4. [文档解析（Parsing）](#文档解析parsing)

5. [文档分块与知识图谱构建（Chunking & KG Building）](#文档分块与知识图谱构建chunking--kg-building)

6. [查询逻辑（Query）](#查询逻辑query)

7. [检索方案演进建议](#检索方案演进建议)

8. [完整流程图](#完整流程图)

9. [文件索引](#文件索引)

---

## 系统概述

RedAgenticRAG 是一个面向小红书 REDoc 文档平台的 Agentic 知识图谱 RAG 系统。当前核心理念是将文档组织为**文档级关系树 + 单文档 TOC Tree + chunk 摘要/原文检索索引**三层结构，服务于文档导航、目录穿透和混合检索；当前已经落地 BM25 + Dense + RRF 的检索链路，但还没有内置最终答案生成 API。

**技术栈**：FastAPI + SQLite + Redis + NetworkX + Qwen LLM (qs_base_url)

**核心文件清单**：

| 层 | 文件 | 职责 |
| --- | --- | --- |
| 入口 | backend/app/main.py | FastAPI 应用启动 |
| 配置 | backend/app/config.py | 全局配置（数据库、LLM、Redis） |
| 数据模型 | backend/app/models/models.py | KnowledgeBase / Document / KGGraph / KGTocTree / KGChunk |
| 数据模型 | backend/app/schemas/kg.py | GraphNode / GraphEdge / TocNode / 枚举类型 |
| 请求模型 | backend/app/schemas/requests.py | API 请求体 Pydantic 模型 |
| API 路由 | backend/app/api/knowledge_base.py | 知识库 CRUD、同步、构建、查询 |
| API 路由 | backend/app/api/auth.py | SSO 认证 |
| SSO 认证 | backend/app/services/sso_auth.py | hi CLI SSO 登录流程 |
| 文档采集 | backend/app/services/redoc_collector.py | REDoc 文档同步与变更消费 |
| 文档解析 | backend/app/services/doc_parser.py | 多格式文件解析为纯文本/Markdown |
| 图谱构建 | backend/app/services/kg_builder.py | LLM 分析 + 图谱构建 + TOC 树构建 |
| 图谱存储 | backend/app/services/kg_store.py | 图谱的序列化/反序列化/持久化 |
| 图谱导航 | backend/app/services/kg_navigator.py | 图谱查询、搜索、TOC 导航 |
| LLM 服务 | backend/app/services/llm.py | QSChat（对话） / QSEmbed（嵌入） |
| 构建状态 | backend/app/services/build_status.py | Redis 分布式锁 + 构建状态进度跟踪 |
| 提示词 | backend/app/prompts/doc_analysis.py | LLM 文档分析提示词 + 关键词过滤 |
| 采集脚本 | backend/scripts/collect_all.py | REDoc 文档全量采集脚本 |

---

## 核心数据模型

### 关系型数据（SQLite）

```python
# KnowledgeBase: 知识库
class KnowledgeBase:
    id, name, description, language, llm_model, embed_model, parser_config
# KnowledgeBaseSource: 知识库来源与同步策略
class KnowledgeBaseSource:
    id, kb_id, external_key, source_type, source_url, folder_path,
    title, auto_update_interval_days, deep_collection_enabled,
    last_sync_status, last_sync_at, last_error
# Document: 文档（一个文档 = 一个 REDoc 页面或一个附件）
class Document:
    id, kb_id, name, location, source_type, source_url, size,
    status, progress, parser_config, content_hash,
    parsed_text, parse_status, chunk_status, chunk_num, token_num
# KGGraph: 完整知识图谱（JSON 序列化存储）
class KGGraph:
    id, kb_id, graph_json, node_count, edge_count
# KGTocTree: 单文档的目录树（JSON 序列化存储）
class KGTocTree:
    id, kb_id, doc_id, toc_json
# KGChunk: TOC leaf chunk 检索索引
class KGChunk:
    id, kb_id, doc_id, node_id, title, summary,
    full_text, source_url, breadcrumb, metadata, embedding_json
```

### 图数据模型（NetworkX DiGraph）

```python
# 节点类型
class DocNodeType(Enum):
    DOCUMENT = "document"   # 文档节点
    KEYWORD = "keyword"     # 关键词节点
    DIRECTORY = "directory" # 目录节点
# 文档类型
class DocType(Enum):
    STRUCTURED = "structured"
    UNSTRUCTURED = "unstructured"
    RELATION = "relation"
# 边类型
class EdgeType(Enum):
    REFERENCES = "references"           # 文档间引用
    RELATES_TO = "relates_to"           # 语义关联
    CONTAINS_KEYWORD = "contains_keyword"  # 文档→关键词
    IS_KEYWORD_OF = "is_keyword_of"        # 关键词→文档（反向边）
    PART_OF = "part_of"                     # 父子/目录关系
# 图节点
class GraphNode:
    node_id, node_type, title, source_url, summary,
    doc_type, compression_ratio, has_toc, toc_root_id,
    metadata, keyword, alias, description, related_docs
# 图边
class GraphEdge:
    edge_id, source_id, target_id, relation_type,
    confidence, evidence, created_by
    # created_by: "llm_extract" / "deterministic" / "directory_structure"
# 目录树节点
class TocNode:
    node_id, parent_id, doc_id, level, title, source_url,
    summary, compression_ratio, is_leaf, full_text,
    text_length, children_ids, children
```

### 存储架构

```plaintext
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   SQLite     │     │    Redis     │     │   文件系统    │
│              │     │              │     │              │
│ KnowledgeBase│     │ 构建状态      │     │ /data/uploads│
│ Document     │     │ 构建进度      │     │   redoc/     │
│ KGGraph      │     │ 进度文档      │     │   attachments│
│ KGTocTree    │     │ 取消标记      │     │ /data/redoc_ │
│ KGChunk      │     │ 分布式锁      │     │ sync/{kb_id} │
└──────────────┘     └──────────────┘     └──────────────┘
```

---

## 文档输入（Ingestion）

### 完整流程

```plaintext
┌──────────────────────────────────────────────────────────────────┐
│                      文档输入完整流程                              │
│                                                                  │
│  POST /api/v1/kb/{kb_id}/sync-redoc                              │
│         │                                                        │
│         ▼                                                        │
│  ┌─────────────┐                                                 │
│  │ 1. URL 解析  │  extract_shortcut_id(url) → shortcut_id        │
│  └──────┬──────┘                                                 │
│         ▼                                                        │
│  ┌─────────────┐                                                 │
│  │ 2. SSO 认证  │  ensure_sso_token() → run-sso.sh → token      │
│  └──────┬──────┘                                                 │
│         ▼                                                        │
│  ┌─────────────────┐                                             │
│  │ 3. 文档采集      │  run_collect_all(shortcut_id, output_dir)  │
│  │   collect_all.py │  → 子进程执行 collect_all.py                │
│  │                  │  → 输出到 /data/sync/{kb_id}                │
│  │                  │  → 持久化 registry.json + changes/*.jsonl   │
│  └──────┬──────────┘                                             │
│         ▼                                                        │
│  ┌─────────────────┐                                             │
│  │ 4. 变更消费      │  consume_redoc_changes()                    │
│  │                  │  → 读取 changes/added.jsonl                 │
│  │                  │  → 读取 changes/modified.jsonl              │
│  │                  │  → 读取 changes/deleted.jsonl               │
│  └──────┬──────────┘                                             │
│         ▼                                                        │
│  ┌─────────────────┐                                             │
│  │ 5. 文件入库存    │  复制文件到 /data/uploads/{redoc,attachments}│
│  │                  │  → 按 location/source_url upsert Document   │
│  │                  │  → content_hash 幂等去重                    │
│  │                  │  → parser_config 包含 shortcut_id,          │
│  │                  │    parent_shortcut_id, dir_path 等          │
│  └──────┬──────────┘                                             │
│         ▼                                                        │
│  ┌─────────────────┐                                             │
│  │ 6. 文档图构建    │  build_document_graph(kb_id)                │
│  │                  │  → 先生成文档级树形关系图                   │
│  │                  │  → TOC/chunk 分块可随后异步执行             │
│  └─────────────────┘                                             │
└──────────────────────────────────────────────────────────────────┘
```

### 关键函数调用链

1. **POST /api/v1/kb/&#123;kb_id&#125;/sync-redoc** (backend/app/api/knowledge_base.py)

- 接收 SyncRedocRequest（redoc_url, recursive, skip_external, skip_sheets, deep_collection_enabled）

- 获取分布式锁（Redis SETNX）

- 调用 ensure_sso_token() 验证 SSO 登录态

- 使用持久同步目录 /data/sync/&#123;kb_id&#125;，启动异步任务 _run()

- 同步期间可通过 POST /kg/cancel 设置取消标记终止采集/构建

1. **run_collect_all()** (backend/app/services/redoc_collector.py:32)

- 调用 backend/scripts/collect_all.py 子进程

- 子进程输出格式：[NEW] [MD] &#123;shortcut_id&#125; &#123;title&#125; 或 [UPDATE] / [SKIP]

- 通过 progress_callback 实时返回进度，逐行写入 Redis 构建进度与 progress_docs

- 输出并维护 registry/变更信息，用于判断新增、更新、删除和不变

- collect_all.py 会读取同目录下持久化的 registry.json，因此可以区分新增、更新、删除和不变

1. **consume_redoc_changes()** (backend/app/services/redoc_collector.py)

- 轮询处理 deleted → modified → added 变更

- deleted 删除 Document、对应 TOC 树和上传文件

- modified / added 都走 upsert，保留已有文档的稳定 doc_id

- 使用 content_hash 判断内容是否变化；未变化则跳过，变化则重置 parse_status/chunk_status

- 最后按 source_url/location 清理历史重复文档，并触发文档级 graph 重建

1. **_ingest_redoc_doc()** (backend/app/services/redoc_collector.py)

- 定位文件路径（internal/&#123;shortcut_id&#125;.md 或 &#123;shortcut_id&#125;.xlsx）

- 复制到 /data/uploads/redoc/&#123;shortcut_id&#125;&#123;suffix&#125;

- 构建 parser_config（shortcut_id, redoc_url, dir_path, parent_shortcut_id）

- 写入 content_hash，并 upsert Document 记录，状态为 "ready"

1. **_ingest_external_resource()** (backend/app/services/redoc_collector.py)

- 处理非 REDoc 类型的外部资源（图片、PDF 等附件）

- 基于 source_url/localPath 的 hash 生成稳定附件路径，避免重复导入

- 构建 parser_config（original_filename, source_type, local_path, parent_shortcut_id）

1. **父文档查找** (_find_parent_shortcut_id, _find_parent_by_source_file)

- 通过目录路径或文件名匹配已存在的 REDoc 文档

- 用于建立文档间的 PART_OF 边

### 深度收集模式

- KnowledgeBaseSource.deep_collection_enabled 控制 REDoc 来源的深度收集，默认开启。

- 开启时使用当前完整收集链路：MCP/DCC/hi fallback，并收集 REDoc 内嵌附件、外部链接和 Sheet 引用。

- 关闭时使用 hi CLI 的 docs:get 获取 REDoc 正文，不走 MCP/DCC 抽取附件与链接，并强制 skip_external=true、skip_sheets=true。

- 关闭深度收集不会关闭 REDoc 子文档递归；是否递归仍由 recursive 控制。

- 前端创建知识库和知识库设置弹窗都提供“深度收集模式”开关。

### SSO 认证流程

```plaintext
┌───────────────┐     ┌───────────────┐     ┌──────────────────┐
│  POST /auth/   │     │  sso_auth.py  │     │  run-sso.sh      │
│  sso/initiate  │────▶│  sso_initiate │────▶│  (bash 子进程)   │
│                │     │               │     │                  │
│                │     │               │◀────│  stdout: token   │
│                │     │               │     │  stderr: NEED_   │
│                │     │               │     │  LOGIN:url       │
│                │◀────│               │     │                  │
│  GET /auth/    │     │               │     │                  │
│  sso/status    │────▶│  sso_complete │────▶│  run-sso.sh      │
│                │     │               │     │  (再次执行)       │
│                │◀────│               │     │                  │
│                │     │               │     │                  │
│ Token 存储:     │     │ _save_auth_token → data/auth_token.json │
│ 有效期 20 分钟   │     │                                          │
│ 自动续期:       │     │ ensure_token_valid → run-sso.sh (重刷)   │
└───────────────┘     └───────────────┘     └──────────────────┘
```

- ensure_token_valid(): 检查 token 是否在有效期内，过期自动重刷

- Token 缓存：data/auth_token.json，按环境（prod/sit/beta）存储

- 应用 ID 分发：通过 BUILTIN_APP_IDS 映射环境到对应 app_id

---

## 文档解析（Parsing）

### 完整流程

```plaintext
┌─────────────────────────────────────────────────────────────────┐
│                      文档解析流程                                │
│                                                                 │
│  parse_file(file_path)  [doc_parser.py:9]                       │
│         │                                                        │
│         ▼                                                        │
│  ┌─────────────────┐                                             │
│  │ 按后缀名分发      │  parsers = {                               │
│  │                  │    ".md/.markdown": _parse_markdown,       │
│  │                  │    ".txt/.text":   _parse_text,            │
│  │                  │    ".html/.htm":   _parse_html,            │
│  │                  │    ".json/.jsonl": _parse_json,            │
│  │                  │    ".pdf":         _parse_pdf,             │
│  │                  │    ".xlsx/.xls":   _parse_xlsx,            │
│  │                  │    ".csv":         _parse_csv,             │
│  │                  │    ".docx":        _parse_docx,            │
│  │                  │    ".pptx":        _parse_pptx,            │
│  │                  │    ".epub":        _parse_epub,            │
│  │                  │  }                                        │
│  └──────┬──────────┘                                             │
│         ▼                                                        │
│  ┌─────────────────┐                                             │
│  │ 输出纯文本/       │  → 所有解析器统一输出 str                   │
│  │ Markdown 格式    │  → HTML/PDF 提取标题层级                    │
│  │                  │  → 表格转为 Markdown table 格式             │
│  └─────────────────┘                                             │
└─────────────────────────────────────────────────────────────────┘
```

### 各格式解析器详情

| 格式 | 解析器 | 依赖库 | 输出 |
| --- | --- | --- | --- |
| .md / .markdown | _parse_markdown | 无 (直接读取) | 原始 Markdown 文本 |
| .txt / .text | _parse_text | 无 (直接读取) | 原始文本 |
| .html / .htm | _parse_html | beautifulsoup4 | 提取 body 文本，标题保留 # 层级，表格转 Markdown |
| .json / .jsonl | _parse_json | 无 (json.loads) | 格式化 JSON 字符串 |
| .pdf | _parse_pdf / fallback | pdfplumber (优先) / pypdf (回退) | 提取文本 + 表格 |
| .xlsx / .xls | _parse_xlsx / fallback | openpyxl (优先) / pandas (回退) | 每个 Sheet 一个 Markdown 表格 |
| .csv | _parse_csv | pandas (优先) / 直接读取 (回退) | Markdown 表格 |
| .docx | _parse_docx | python-docx | 段落文本 + 标题层级 + 表格 |
| .pptx | _parse_pptx | python-pptx | 每页幻灯片文本 + 表格 |
| .epub | _parse_epub | zipfile + bs4 | 提取 HTML 内容文本 |

### 辅助函数

- **extract_sections(text)** (doc_parser.py:297): 按 # 标题分割文本为 [&#123;title, content&#125;] 列表

### 状态回写

- 手动解析接口 POST /api/v1/kb/&#123;kb_id&#125;/parse 会将解析结果写入 Document.parsed_text，并设置 parse_status = "parsed" 或 "failed"。

- 文件分块 / REDoc 同步触发的 run_kg_build() 也会在读取文档文本后回写 parsed_text、parse_status 和 token_num。

- 每个文档完成分块后会立即写入对应 KGTocTree、KGChunk 并标记 chunk_status = "chunked"；取消或失败时未完成的 chunking 文档会回到待分块状态，已完成的文档保留。

---

## 文档分块与知识图谱构建（Chunking & KG Building）

### 完整流程（核心）

```plaintext
┌──────────────────────────────────────────────────────────────────────────────┐
│                    KG 构建完整流程 (run_kg_build)                              │
│                                                                              │
│  POST /api/v1/kb/{kb_id}/kg/build                                            │
│         │                                                                     │
│         ▼                                                                     │
│  ┌──────────────────────────────────────────────────────────────────────┐    │
│  │ Phase 1: 文档加载                                                      │    │
│  │                                                                        │    │
│  │ _get_kb_documents(kb_id) → 从 SQLite 获取所有 Document 记录            │    │
│  │ _read_document_text(doc, upload_dir) → 优先使用 parsed_text，否则解析文件│    │
│  │ _mark_document_parsed(doc_id, text) → 回写 parsed_text/parse_status    │    │
│  └────────────────────────────────┬─────────────────────────────────────┘    │
│                                   ▼                                          │
│  ┌──────────────────────────────────────────────────────────────────────┐    │
│  │ Phase 2: LLM 并发分析 (asyncio.as_completed, 信号量控制并发)            │    │
│  │                                                                        │    │
│  │ _analyze_document(title, text, semaphore) → LLM 分析每个文档            │    │
│  │                                                                        │    │
│  │ Prompt: DOC_ANALYSIS_PROMPT (doc_analysis.py:8)                        │    │
│  │   输入: 文档标题 + 全文 (截断到 200000 字符)                             │    │
│  │   输出: JSON { summary, toc, keywords }                                │    │
│  │                                                                        │    │
│  │ 重试: 最多 2 次                                                         │    │
│  │ 关键词回退: 如果 LLM 未返回 keywords，单独调用 KEYWORD_ONLY_PROMPT       │    │
│  │ 关键词过滤: filter_keywords() 过滤无效/过宽/LLM 虚构词                   │    │
│  └────────────────────────────────┬─────────────────────────────────────┘    │
│                                   ▼                                          │
│  ┌──────────────────────────────────────────────────────────────────────┐    │
│  │ Phase 3: 构建节点与边                                                   │    │
│  │                                                                        │    │
│  │ 3a. 文档节点 (DOCUMENT)                                                │    │
│  │     - 每个 Document 生成一个 GraphNode                                 │    │
│  │     - 包含: title, summary, source_url, has_toc                        │    │
│  │                                                                        │    │
│  │ 3b. TOC 目录树 (TocNode)                                               │    │
│  │     _build_toc_from_llm_output(toc_data, doc_id, url)                  │    │
│  │     → 递归解析 LLM 输出的 toc JSON 树                                  │    │
│  │     → 每个节点: node_id, title, summary, level, is_leaf                │    │
│  │     → 叶子节点: start_text (前 10-30 字符) 用于锚定                     │    │
│  │                                                                        │    │
│  │     _fill_leaf_full_text(toc_nodes, full_text)                         │    │
│  │     → 将叶子节点的 start_text 锚定到原始文档文本                        │    │
│  │     → 填充 full_text (从标题开始到下一个标题/叶子结束)                   │    │
│  │     → 计算 text_length                                                  │    │
│  │                                                                        │    │
│  │ 3c. 关键词节点 (KEYWORD)                                               │    │
│  │     - 每个 keyword 生成一个 KEYWORD 节点                               │    │
│  │     - 边: CONTAINS_KEYWORD (doc→kw) + IS_KEYWORD_OF (kw→doc)          │    │
│  │     - created_by: "llm_extract"                                        │    │
│  │                                                                        │    │
│  │ 3d. 目录结构边 (PART_OF)                                               │    │
│  │     _build_parent_child_edges(documents)                               │    │
│  │     → 通过 parser_config.parent_shortcut_id 建立父子关系                │    │
│  │     → 通过 parser_config.dir_path 建立目录层级和文档归属                │    │
│  │     → 目录节点: DIRECTORY 类型，created_by: "directory_structure"       │    │
│  │                                                                        │    │
│  │ 3e. 引用边 (REFERENCES)                                                │    │
│  │     _build_reference_edges(doc_nodes, kb_id)                           │    │
│  │     → 通过 source_url 中的 shortcut_id 匹配文档间引用                  │    │
│  │     → created_by: "deterministic"                                      │    │
│  └────────────────────────────────┬─────────────────────────────────────┘    │
│                                   ▼                                          │
│  ┌──────────────────────────────────────────────────────────────────────┐    │
│  │ Phase 4: 持久化                                                         │    │
│  │                                                                        │    │
│  │ build_document_graph(kb_id) → 基于 Document/parser_config 生成文档树    │    │
│  │ kg_store.save_graph(kb_id, graph) → 序列化为 JSON 存入 SQLite          │    │
│  │ kg_store.save_toc_tree(kb_id, doc_id, root) → 单文档完成即保存 TOC 树   │    │
│  │ kg_store.save_chunks(kb_id, doc_ids, chunks) → 单文档完成即保存索引     │    │
│  │   - full_text 用于 BM25                                                │    │
│  │   - summary/title embedding 存入 embedding_json                        │    │
│  └──────────────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 图谱结构示意

```plaintext
                    ┌──────────────┐
                    │  DIRECTORY   │  (目录节点)
                    │  dir:xxx     │
                    └──────┬───────┘
                           │ PART_OF
                    ┌──────▼───────┐
                    │   DOCUMENT   │ ←─── has_toc → ┌──────────────┐
                    │   doc_id_A   │                 │   TocNode    │
                    │   summary    │                 │   (root)     │
                    └──┬───┬───┬──┘                 │   title      │
                       │   │   │                    │   summary    │
              ┌────────┘   │   └────────┐           └──┬───┬───┬──┘
              │PART_OF     │CONTAINS    │REFERENCES    │   │   │
              ▼            │_KEYWORD    │              ▼   ▼   ▼
       ┌──────────┐  ┌─────▼─────┐ ┌──▼───────┐  ┌──────────────┐
       │ DOCUMENT │  │  KEYWORD  │ │ DOCUMENT │  │  TocNode     │
       │  doc_B   │  │  kw:xxx   │ │  doc_C   │  │  (section)   │
       └──────────┘  │  alias    │ └──────────┘  │  is_leaf     │
                     │  desc     │               │  full_text   │
                     └───────────┘               └──────────────┘
```

### 关键设计点

1. **LLM 并发控制**：通过 asyncio.Semaphore(llm_concurrency) 限制并发 LLM 调用数（默认 5）

2. **文本截断**：LLM 分析时截断到 200000 字符，关键词回退截断到 15000 字符

3. **叶子节点锚定**：LLM 输出 start_text（前 10-30 字符），用于在原文中定位完整段落

4. **目录结构推断**：通过 parser_config.dir_path 和 parent_shortcut_id 两种方式建立层级关系

5. **关键词过滤**：过滤单字符、纯数字、过于宽泛的词（如 "方法"、"模型"）、LLM 虚构词（如 "truncated"、"placeholder"）

6. **检索索引**：关键词节点仍生成和展示，但默认检索使用 KGChunk 的 TOC leaf chunk，不再依赖关键词列表召回。

7. **文档图与分块解耦**：文档级 graph 可在采集完成后立即生成；TOC Tree、summary embedding 和 chunk 索引由后续分块逐文档补齐。

---

## 查询逻辑（Query）

### 查询流程总览

```plaintext
┌──────────────────────────────────────────────────────────────────────────────┐
│                           查询流程                                            │
│                                                                              │
│  API 入口                                                                     │
│  ├── POST /api/v1/kb/{kb_id}/kg/search        (节点搜索)                      │
│  ├── POST /api/v1/kb/{kb_id}/kg/search-unified (统一搜索)                     │
│  ├── GET  /api/v1/kb/{kb_id}/kg/explore/{id}  (TOC 导航)                     │
│  ├── GET  /api/v1/kb/{kb_id}/kg/read/{id}     (TOC 内容读取)                  │
│  ├── GET  /api/v1/kb/{kb_id}/kg/stats         (图谱统计)                      │
│  ├── GET  /api/v1/kb/{kb_id}/kg/subgraph      (子图查询)                      │
│  ├── GET  /api/v1/kb/{kb_id}/kg/node/{id}     (节点详情)                      │
│  └── GET  /api/v1/kb/{kb_id}/kg/toc/{doc_id}  (文档目录树)                    │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 1. Chunk 混合检索 (search_nodes / search_chunks)

```plaintext
┌──────────────────────────────────────────────────────────────────────┐
│  search_nodes(kb_id, query, top_k=10, node_type=None)                 │
│                                                                      │
│  默认路径: node_type 为空时，转到 search_chunks()                       │
│                                                                      │
│  Phase 1: BM25 召回                                                   │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ load_chunks(kb_id) → 读取 KGChunk                             │   │
│  │ _tokenize(query/full_text)                                     │   │
│  │ _bm25_rank(query, chunks) → 对 chunk 原文 full_text 排序        │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  Phase 2: Dense 召回                                                  │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ 构建期已对 chunk summary/title 生成 embedding_json             │   │
│  │ 查询时 qs_embed.encode([query]) → query_vec                   │   │
│  │ cosine_similarity(query_vec, chunk_vectors) → dense 排序       │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  Phase 3: RRF 融合                                                    │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ _rrf_fuse([bm25_ranked, dense_ranked], k=60)                  │   │
│  │ final_score = Σ 1 / (60 + rank_in_each_layer)                 │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  返回: Top-K chunk，默认包含 snippet/has_more/breadcrumb/source_url    │
│        full_text 需通过 /kg/read/{node_id} 按需读取                    │
└──────────────────────────────────────────────────────────────────────┘
```

如果显式传入 node_type，仍保留旧的图节点搜索能力用于调试或后台用途，但默认搜索不再使用 keyword 节点。

### 2. 统一搜索 (search_unified)

```plaintext
┌──────────────────────────────────────────────────────────────────────┐
│  search_unified(kb_id, query, top_k=5, filters?, penetrate=True)      │
│                                                                      │
│  Phase 1: Chunk 混合检索                                               │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ search_chunks(query, top_k, filters) → BM25 + Dense + RRF     │   │
│  │ 返回 chunk_results                                            │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  Phase 2: 文档聚合与 TOC 结果                                         │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ 从 chunk_results 聚合 document_results                         │   │
│  │ toc_results 直接映射命中的 TOC leaf chunk                      │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  返回:                                                                │
│  {                                                                   │
│    "query": "...",                                                    │
│    "document_results": [...],   # 文档级结果                          │
│    "toc_results": [...],        # 命中的 TOC leaf                    │
│    "chunk_results": [...],      # snippet 优先，全文按需读取           │
│    "doc_coverage": 3,           # 命中的不同文档数                    │
│    "confidence": "high"        # high / medium / low                 │
│  }                                                                   │
└──────────────────────────────────────────────────────────────────────┘
```

### 3. TOC 导航 (explore_doc / read_toc_content)

```plaintext
┌──────────────────────────────────────────────────────────────────────┐
│  explore_doc(kb_id, doc_id, parent_node_id, filter_query)            │
│                                                                      │
│  → 加载文档 TOC 树                                                   │
│  → 定位到指定 parent_node_id（或 root）                               │
│  → 返回当前节点的子节点列表                                           │
│  → 如果指定 filter_query，按标题/摘要匹配过滤子节点                    │
│  → 限制 max_children = 10                                            │
│                                                                      │
│  read_toc_content(kb_id, node_id, include_path, include_siblings)    │
│                                                                      │
│  → 在所有 TOC 树中查找 node_id                                        │
│  → 如果是叶子节点，返回 full_text                                     │
│  → include_path: 返回面包屑路径 (breadcrumb)                          │
│  → include_siblings: 返回同级兄弟节点                                 │
└──────────────────────────────────────────────────────────────────────┘
```

### 4. 其他查询接口

| 接口 | 方法 | 功能 |
| --- | --- | --- |
| /kb/&#123;kb_id&#125;/docs | GET | 获取文档列表，返回 parse_status/chunk_status 等状态 |
| /kb/&#123;kb_id&#125;/docs | DELETE | 按 doc_ids 删除文档和上传文件 |
| /kb/&#123;kb_id&#125;/docs/reset | POST | 清空选中文档的解析文本、TOC 和 chunk 索引，但保留文档记录及文档级 graph 关系 |
| /kb/&#123;kb_id&#125;/docs/refetch | POST | 重新下载选中文档源文件，适用于 REDoc/外部来源变更后刷新本地文件 |
| /kb/&#123;kb_id&#125;/parse | POST | 按 doc_ids 或全量解析文档，写入 parsed_text/parse_status |
| /kb/&#123;kb_id&#125;/kg/stats | GET | 返回图谱统计（节点数、边数、文档数、关键词数） |
| /kb/&#123;kb_id&#125;/kg/subgraph | GET | 获取子图（可按 node_type 过滤，限制 max_nodes=500） |
| /kb/&#123;kb_id&#125;/kg/node/&#123;node_id&#125; | GET | 获取节点详情（含入边/出边） |
| /kb/&#123;kb_id&#125;/kg/toc/&#123;doc_id&#125; | GET | 获取文档的完整 TOC 目录树 |
| /kb/&#123;kb_id&#125;/kg/search-in-doc | POST | 在单个文档内做 BM25 + Dense + RRF 二次检索 |
| /kb/&#123;kb_id&#125;/kg/build | POST | 触发 KG 构建（run_kg_build），支持 doc_ids 文件级分块 |
| /kb/&#123;kb_id&#125;/kg/build-status | GET | 查询构建状态和进度 |
| /kb/&#123;kb_id&#125;/kg/cancel | POST | 设置取消标记，终止收集/构建任务 |

### 当前查询机制特点

- **无 LLM 参与查询**：当前查询只做检索和排序，不涉及 LLM 生成最终答案

- **仍未形成完整回答链路**：已经有可作为上下文的 chunk 召回，但还没有 retrieve → context pack → LLM answer API

- **默认检索对象是 TOC leaf chunk**：KGChunk.full_text 用于 BM25，KGChunk.summary/title 的 embedding 用于 Dense 召回

- **混合检索已落地**：默认 search_nodes() 调用 search_chunks()，执行 BM25 + Dense + RRF

- **默认返回 snippet**：搜索结果默认不返回 full_text，通过 has_more 和 /kg/read/&#123;node_id&#125; 支持按需深读

- **有置信度和覆盖面**：返回 0-1 归一化 score、confidence、doc_coverage、total_candidates

- **支持结构化过滤**：filters 可按 chunk metadata（如 source_type/biz_line/doc_path/path_parts）缩小候选集；核心系统不内置业务语义标签

- **支持二次检索**：/kg/search-in-doc 在指定 doc_id 内执行同样的混合检索

- **关键词不参与默认检索**：keyword 节点仍生成、保存和展示，但不再作为默认搜索召回依据

- **向量存储是 SQLite JSON**：当前不依赖外部向量库，查询时从 SQLite 加载 embedding 并在内存中计算余弦相似度

---

## 检索方案落地

用户提出的精简检索流程可以概括为：chunk 原文建 BM25，chunk summary 建 Dense 向量，文档 summary 向量做可选路由，BM25 与 Dense 用 RRF 融合，最终返回原文 chunk 给 LLM。

### 与原始实现的核心区别

| 维度 | 原始实现 | 当前落地 | 说明 |
| --- | --- | --- | --- |
| 基本单元 | 文档节点 + TOC 节点 | KGChunk，来源于 TOC leaf | 保留目录结构，同时拥有可检索 chunk |
| 稀疏检索 | 手写 substring/word 加分 | 内置 BM25 on chunk full_text | 使用 IDF 和长度归一化 |
| 稠密检索 | 查询时临时 embedding 候选 title/keyword | 构建时 embedding chunk summary/title，存入 embedding_json | 查询时只 embedding query |
| 文档级路由 | document 节点搜索后 TOC 穿透 | 从 chunk 结果聚合 document_results | 文档结果来自真实命中的 chunk |
| 融合方式 | 0.4 _ lexical + 0.6 _ semantic | RRF，1 / (60 + rank) | 不依赖 BM25 与 cosine 的分数尺度 |
| 返回内容 | 节点/文档/TOC 匹配结果 | Top-K chunk 原文片段 + breadcrumb | 可直接作为后续 LLM 上下文 |
| 存储 | SQLite graph_json + toc_json | SQLite graph_json + toc_json + kg_chunk | 暂不引入外部向量库 |

### 实现取舍

1. **保留 TOC leaf 作为 chunk**：不引入固定长度 chunk，避免丢失目录层级和面包屑。

2. **检索用 summary/title embedding，返回用 full_text**：summary/title 是 Dense 索引对象，full_text 是上下文对象。

3. **关键词保留但不检索**：keyword 节点继续用于图谱展示和统计，不进入默认 chunk 检索。

4. **不新增外部向量库**：embedding 以 JSON 存在 SQLite 中，降低本地 Docker 和 K8s 部署复杂度。

5. **中文 tokenization 使用 jieba**：当前使用 jieba 做中文分词，英文/数字按正则切分，并过滤常见中文停用词；核心检索层不硬编码业务语义标签。

### 当前落地方式

当前已经按“TOC leaf 作为 chunk”的方式落地混合检索：

1. 将每个 TocNode leaf 视为一个 chunk，full_text 是返回给 LLM 的原文上下文。

2. 对 leaf full_text 建 BM25 索引。

3. 对 leaf 的 title + summary 或 summary 生成 embedding，存入 KGChunk.embedding_json。

4. 文档级结果从 chunk 命中结果聚合，暂未单独建立 document summary 向量路由。

5. 查询时并行执行 BM25 和 Dense 召回，用 RRF 合并；API 默认返回 summary、snippet、breadcrumb、source_url，全文通过 /kg/read/&#123;node_id&#125; 按需读取。

6. 对没有 TOC 或所有 leaf full_text 为空的文档，fallback 为将整个文档文本赋给第一个 leaf 节点（不使用固定长度分块）。

### 能力状态

| 能力 | 当前状态 | 说明 |
| --- | --- | --- |
| chunk/leaf 索引表 | 已有 | KGChunk 保存 TOC leaf chunk、summary、full_text、breadcrumb、embedding_json |
| BM25 检索 | 已有 | 查询时基于 KGChunk.full_text 计算轻量 BM25 |
| Dense 检索 | 已有 | 构建期保存 summary/title embedding，查询时计算 query embedding 和 cosine similarity |
| RRF 融合 | 已有 | _rrf_fuse(..., k=60) 合并 BM25 与 Dense 排名 |
| 外部向量库 | 暂无 | 当前使用 SQLite JSON，后续可替换为 ChromaDB / FAISS / pgvector |
| LLM 答案生成链路 | 暂无 | 仍需新增 query → retrieve → context pack → chat completion API |

### 迁移风险

- **构建成本上升**：离线 embedding 会把成本从查询时转移到构建时，需要批处理和失败重试。

- **索引一致性**：Document upsert、删除、重新分块时，需要同步删除旧 BM25/向量索引。

- **内存计算规模**：当前查询时从 SQLite 加载 chunk embedding 并在内存中计算相似度，适合中小规模知识库。

- **TOC 锚定失败**：部分 leaf 可能没有 full_text，需要 fallback 到 title + summary 或 deterministic chunk。

### 后续建议

短期继续保留当前 KG/TOC 架构。下一步可以新增答案生成 API，把 chunk_results.full_text 组装为上下文送入 LLM；当单个知识库 chunk 数明显增长时，再将 KGChunk.embedding_json 迁移到 ChromaDB / FAISS / pgvector。

---

## 完整流程图

```plaintext
                            ┌─────────────────────────┐
                            │    用户发送 REDoc URL    │
                            │  或直接上传文档文件       │
                            └───────────┬─────────────┘
                                        │
                    ┌───────────────────▼───────────────────┐
                    │          Phase 1: 文档输入             │
                    │                                       │
                    │  POST /sync-redoc                     │
                    │  ├── SSO 认证 (ensure_sso_token)       │
                    │  ├── 采集文档 (collect_all.py)          │
                    │  ├── registry 增量检测                  │
                    │  ├── 变更消费 (consume_redoc_changes)   │
                    │  ├── 文件复制 (→ /data/uploads/)       │
                    │  └── upsert Document 记录 (SQLite)     │
                    └───────────────────┬───────────────────┘
                                        │
                    ┌───────────────────▼───────────────────┐
                    │          Phase 2: 文档解析             │
                    │                                       │
                    │  parse_file(file_path)                │
                    │  ├── MD → 直接读取                     │
                    │  ├── HTML → BeautifulSoup              │
                    │  ├── PDF → pdfplumber / pypdf          │
                    │  ├── XLSX → openpyxl / pandas          │
                    │  ├── DOCX → python-docx                │
                    │  ├── PPTX → python-pptx                │
                    │  └── EPUB → zipfile + bs4              │
                    │                                       │
                    │  输出: 纯文本 / Markdown 格式文本       │
                    │  回写: parsed_text / parse_status       │
                    └───────────────────┬───────────────────┘
                                        │
                    ┌───────────────────▼───────────────────┐
                    │       Phase 3: KG 构建 (分块)          │
                    │                                       │
                    │  run_kg_build(kb_id, upload_dir)      │
                    │  ├── LLM 并发分析 (每个文档)            │
                    │  │   ├── Summary (2-5 句)              │
                    │  │   ├── TOC (层级目录树)              │
                    │  │   └── Keywords (5-15 个 + alias)    │
                    │  │                                    │
                    │  ├── 构建 TOC 目录树 (TocNode)         │
                    │  │   ├── 递归构建层级                  │
                    │  │   ├── 叶子节点锚定原文 (start_text)  │
                    │  │   └── 填充 full_text               │
                    │  │                                    │
                    │  ├── 构建图节点                         │
                    │  │   ├── DOCUMENT 节点 (含 summary)    │
                    │  │   ├── KEYWORD 节点 (含 alias)       │
                    │  │   └── DIRECTORY 节点 (目录层级)     │
                    │  │                                    │
                    │  ├── 构建边                            │
                    │  │   ├── CONTAINS_KEYWORD / IS_KEYWORD_OF │
                    │  │   ├── PART_OF (父子/目录)           │
                    │  │   └── REFERENCES (文档引用)         │
                    │  │                                    │
                    │  └── 持久化                            │
                    │      ├── kg_store.save_graph (SQLite)  │
                    │      ├── kg_store.save_toc_tree (SQLite) │
                    │      └── chunk_status = chunked         │
                    └───────────────────┬───────────────────┘
                                        │
                    ┌───────────────────▼───────────────────┐
                    │          Phase 4: 查询                 │
                    │                                       │
                    │  KGNavigator                          │
                    │  ├── search_nodes (词汇+语义)          │
                    │  ├── search_unified (文档+TOC穿透)     │
                    │  ├── explore_doc (TOC导航)             │
                    │  ├── read_toc_content (内容读取)       │
                    │  ├── get_doc_toc_tree (目录树)         │
                    │  ├── get_node_info (节点详情)          │
                    │  └── get_subgraph (子图)               │
                    │                                       │
                    │  输出: 匹配的节点/文档/目录节点信息     │
                    └───────────────────────────────────────┘
```

---

## 文件索引

| 文件 | 绝对路径 | 核心职责 |
| --- | --- | --- |
| main.py | backend/app/main.py | FastAPI 应用启动、CORS 中间件、路由注册 |
| config.py | backend/app/config.py | Settings 配置（数据库、LLM、Redis、路径） |
| models.py | backend/app/models/models.py | SQLAlchemy 数据模型（KnowledgeBase, Document, KGGraph, KGTocTree） |
| base.py | backend/app/models/base.py | 数据库引擎、会话工厂、init_db |
| kg.py | backend/app/schemas/kg.py | 图数据模型（GraphNode, GraphEdge, TocNode, 枚举） |
| requests.py | backend/app/schemas/requests.py | API 请求体模型（KBCreate, SyncRedocRequest, BuildRequest） |
| knowledge_base.py | backend/app/api/knowledge_base.py | 知识库 CRUD、REDoc 同步、KG 构建、查询 |
| auth.py | backend/app/api/auth.py | SSO 认证接口 |
| router.py | backend/app/api/router.py | 路由聚合 |
| sso_auth.py | backend/app/services/sso_auth.py | SSO 登录、Token 管理、缓存 |
| redoc_collector.py | backend/app/services/redoc_collector.py | REDoc 文档采集、变更消费、文件入库 |
| doc_parser.py | backend/app/services/doc_parser.py | 多格式文件解析（Markdown、PDF、Office、HTML 等） |
| kg_builder.py | backend/app/services/kg_builder.py | LLM 分析 + 图谱构建 + TOC 树构建 |
| kg_store.py | backend/app/services/kg_store.py | 图谱/目录树的序列化存储与加载 |
| kg_navigator.py | backend/app/services/kg_navigator.py | 图谱查询、搜索、TOC 导航 |
| llm.py | backend/app/services/llm.py | QSChat（对话）/ QSEmbed（嵌入向量） |
| build_status.py | backend/app/services/build_status.py | Redis 分布式锁 + 构建状态/进度管理 |
| doc_analysis.py | backend/app/prompts/doc_analysis.py | LLM 文档分析提示词 + 关键词过滤 |
| collect_all.py | backend/scripts/collect_all.py | REDoc 文档全量采集脚本 |
| collect_redoc.py | backend/scripts/collect_redoc.py | 递归采集 REDoc 文档树，输出 .meta.jsonl |
| extract_links.py | backend/scripts/extract_links.py | 从 REDoc meta 中提取附件、外链、Sheet 队列 |
| collect_external.py | backend/scripts/collect_external.py | 下载附件、PDF、网页和 Sheet，输出 .ext-meta.jsonl |
| detect_changes.py | backend/scripts/detect_changes.py | 基于 registry.json 与本次 meta 检测新增、更新、删除 |
| update_registry.py | backend/scripts/update_registry.py | 根据本次采集结果重建持久 registry |
| mcp_redoc.py | backend/scripts/mcp_redoc.py | REDoc MCP 查询客户端 |
| dcc_redoc.py | backend/scripts/dcc_redoc.py | DCC API 附件提取 fallback |
| read_sheet.sh | backend/scripts/read_sheet.sh | REDoc Sheet 导出辅助脚本 |
| run-sso.sh | backend/scripts/run-sso.sh | hi CLI SSO 登录辅助脚本 |
| frontend | frontend/ | React + Vite 前端页面，包含数据集、同步弹窗、图谱/TOC 视图 |
| docker | docker/ | Docker Compose、nginx、supervisord 本地部署配置 |