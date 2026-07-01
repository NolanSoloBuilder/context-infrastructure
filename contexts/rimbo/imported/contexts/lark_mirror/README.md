# lark_mirror/

从 Lark 拉下来的 markdown 镜像。**只读**——任何人手改这里的内容会被下次同步覆盖。

## 用途

让 AI 能基于 Lark 的内容做 semantic search 与离线检索，覆盖团队 wiki 与文档。

## 何时是权威

不是。Lark 端才是权威。如果 AI 需要某份 Lark 文档的最新版本（比如刚刚有人在 Lark 改了），应该直接调 `tools/lark/lark_doc_pull.py --doc_id <xxx>` 实时拉一次，不依赖镜像新鲜度。镜像负责覆盖面，实时调用负责精度。

## 同步流程

任何人都能跑 `periodic_jobs/lark_sync/`，但跑前先看 `_meta.json` 的 `last_synced_at`，超过阈值（默认 6 小时）才真正调 API，否则直接退出。同步结果走 `feat/lark-sync-<yyyy-mm-dd-HH>` 分支 + 发布 skill 自动 PR。

详见 `rules/skills/lark_read.md`（Phase 2 新增）和 `rules/skills/workflow_publish.md`。

## 目录结构

```
lark_mirror/
├── README.md
├── _meta.json                  # 每个文件对应的 obj_token / 版本号 / 同步时间
└── <space>/<doc_path>.md       # 实际镜像内容
```

`_meta.json` 在 Phase 2 自动维护，Phase 1 阶段先空着。

## 写回 Lark 的约束

任何对 Lark 文档的写回（`lark_doc_push.py`）必须**先 commit 到仓库 + push + merge**，再触发推送。不允许 AI 跳过仓库直接写 Lark。理由是仓库才是版本权威，否则 git 和 Lark 会渐行渐远。
