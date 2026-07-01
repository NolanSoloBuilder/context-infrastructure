# Skill: prd_archive

PRD 归档：**Lark 上已定稿的 PRD 镜像到 `contexts/lark_mirror/`**，让 AI 在做 deep research / semantic search 时能检索到历史 PRD 全文，但不参与编辑。

## 适用场景

两类需要归档：

1. **历史 PRD**：Lark 上写过、但仓库里没建过 `contexts/products/<x>/prd/` 的老 PRD。**只读镜像，不导入仓库正文**
2. **已 shipped 的 PRD 快照**：仓库里有 `prd/v<n>.md` 且状态已切到 shipped/superseded，归档一份冻结版本到镜像，避免后续 PRD 模板演化掩盖历史细节

## 路径选择

`periodic_jobs/lark_sync/` 是同步入口，背后走 `tools/lark/` fallback 路径（tenant_access_token，能跑 cron）。**这里不走 lark-cli**——因为：

1. 镜像同步是批量 / 长跑任务，应用身份比个人 OAuth 更合适
2. 个人 OAuth 镜像出来的内容是 caller 个人能看到的，会污染团队共享镜像
3. 主路径 lark-cli 不能跑 cron

## When to Use

- caller 说"把 Lark 上的某某 PRD 同步进来给 AI 检索"
- 一份 PRD 状态切到 shipped，要冻结一份不可变快照
- `contexts/lark_mirror/` 严重过期，主动触发一次同步

## Prerequisites

- `tools/lark/` 的 `LARK_APP_ID` / `LARK_APP_SECRET` 已配（`.env` 或 1Password）
- 应用在 Lark 后台拿到目标 wiki space 的访问权限
- 注意：`tools/lark/` **未在 rimbo 团队充分验证**，第一次跑前先 dry-run

## 步骤

### 1. 找到 wiki space_id

PRD 所在的 wiki 空间，space_id 在 Lark wiki 设置里。team 共享的 space_id 建议记到 `contexts/lark_mirror/<space>/_meta.json` 的 `space_id` 字段，下次复用。

### 2. 触发同步（手动 / cron）

```bash
# dry-run 先看会拉什么
python3 periodic_jobs/lark_sync/run.py --space-id <space_id> --dry-run

# 实跑
python3 periodic_jobs/lark_sync/run.py --space-id <space_id>
```

`lark_sync` 内部：

- 读 `contexts/lark_mirror/<space>/_meta.json` 的 `last_synced_at`，新于 stale 阈值（默认 6h）就退出，避免多人 cron 撞车
- 拉空间内所有 PRD 类文档（按 `_meta.json` 配置的过滤规则）写到 `contexts/lark_mirror/<space>/<title>.md`，每个文件首行加 `<!-- lark-mirror obj_token=... -->`
- 同步结果走 `workflow_publish`（分支 `feat/lark-sync-<yyyy-mm-dd-HH>`），自动 commit + PR

### 3. 验证镜像

```bash
ls contexts/lark_mirror/<space>/
cat contexts/lark_mirror/<space>/_meta.json
```

`last_synced_at` 应该是刚才的时间戳。

### 4. shipped PRD 的快照归档（可选）

仓库内的 PRD 切到 shipped/superseded 后，可以额外把当前 `prd/v<n>.md` **复制**一份到 `contexts/lark_mirror/<space>/snapshots/<product>-v<n>.md`，作为不可变历史：

```bash
mkdir -p contexts/lark_mirror/<space>/snapshots
cp contexts/products/<product>/prd/v<n>.md \
   contexts/lark_mirror/<space>/snapshots/<product>-v<n>.md
# 走 workflow_publish 提交
```

snapshots 子目录是只读约定，AI 不能再改它。

## 镜像的只读约束

- `contexts/lark_mirror/` 下所有文件 **只能由 lark_sync 写**，AI 不能在普通对话里改
- 如果发现镜像和源头不一致 → 只在 Lark 端改 + 等下次同步，**不要**手动改镜像（会被下次同步覆盖，且污染 git 归属）
- 引用镜像内容时遵循 [`lark_read.md`](./lark_read.md) 的隐私边界

## 不要做的事

- **不要**用 lark-cli 来批量同步：lark-cli 是个人身份，会按 caller 权限过滤内容，多人跑结果不一致
- **不要**把镜像目录加进 PRD 起草路径：`prd/` 是源头，`lark_mirror/` 是只读副本
- **不要**在 cron 里跑 lark-cli：OAuth token 7 天不用就过期且只能交互式重授权，无人值守撑不住

## 关联

- [`tools/lark/README.md`](../../tools/lark/README.md) — fallback Python 路径（同步走这里）
- [`rules/skills/lark_read.md`](./lark_read.md) — 镜像怎么读
- [`rules/skills/prd_status_change.md`](./prd_status_change.md) — shipped 后的归档时机
- [`contexts/lark_mirror/README.md`](../../contexts/lark_mirror/README.md)
- [`docs/COLLAB_PROTOCOL.md`](../../docs/COLLAB_PROTOCOL.md) — cron 错峰约定
