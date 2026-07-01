# Skill: prd_status_change

PRD 状态切换：**改 frontmatter status → 推 Lark → 群通知**。每次状态切换是一次明确的团队信号。

## 状态机

```
draft  →  review  →  approved  →  shipped
   ↘         ↘            ↑
    superseded（被新版替代）
```

迁移规则：

| from → to | 触发 | 谁能做 |
|---|---|---|
| draft → review | 起草完成，发起评审 | PRD owner |
| review → draft | 评审退回，需重写 | owner 或评审拒绝者 |
| review → approved | 评审通过 | owner 或被指定的批准人 |
| approved → shipped | 功能上线 | 实施 owner（一般同 PRD owner） |
| 任意 → superseded | 被新版 PRD 替代 | 新版 PRD 的 owner |

## When to Use

- 评审结束，PRD 进入 approved
- 功能上线，PRD 进入 shipped
- 新版 PRD 取代旧版

## Prerequisites

- PRD 文件在仓库内已 merge 到 main
- 通知群 chat_id 可解析（与 [`prd_review.md`](./prd_review.md) 同样的优先级）：
  1. `contexts/products/<product>/_meta.yml` 的 `notify_chat_id` 或 `review_chat_id`
  2. `contexts/team_config.yml` 的 `lark.default_notify_chat_id`

## 步骤

### 1. 改 frontmatter

```yaml
status: approved          # 或 shipped / superseded
updated: 2026-MM-DD
approved_by: <handle>     # approved 状态额外加这个字段
approved_at: 2026-MM-DD
shipped_at: 2026-MM-DD    # shipped 状态加这个字段
superseded_by: contexts/products/<product>/prd/v<n+1>.md   # superseded 加这个字段
```

### 2. 走 workflow_publish

```
分支：feat/prd-<product>-status-<handle>-<timestamp>
commit："docs(products/<product>): mark v<n> PRD <new_status>"
```

owner 自动 merge。owner 不是自己（比如批准人代切）→ 标 Reviewer 让 owner 知会一下。

### 3. 推回 Lark

```bash
git checkout main && git pull --rebase origin main
./tools/lark_cli/push.sh <obj_token> contexts/products/<product>/prd/v<n>.md
```

Lark 文档头部的状态字段会被这次推送同步更新。

### 4. 群通知

```
[PRD <new_status>] <product> v<n>
  之前: <old_status>  现在: <new_status>
  <按 status 一句话补充>
  文档: <docx_url>
  快照: <commit URL>
```

> `im_send.sh` 会自动加 `[AI]` 前缀和 caller 署名行，模板里不要再手写。

针对各状态的"一句话补充"建议：

| status | 一句话补充 |
|---|---|
| review | 期望反馈周期 X 天 |
| approved | 批准人: @<handle>，下一步实施 owner: @<handle> |
| shipped | 上线时间 / 链接 |
| superseded | 新版: <v<n+1> docx_url> |

```bash
# 解析 chat_id
CHAT_ID=$(yq '.notify_chat_id // .review_chat_id // ""' contexts/products/<product>/_meta.yml 2>/dev/null)
[ -z "$CHAT_ID" ] && CHAT_ID=$(yq '.lark.default_notify_chat_id' contexts/team_config.yml)

./tools/lark_cli/im_send.sh "$CHAT_ID" "$TEXT"
```

## 不要做的事

- **不要**只改 Lark 不改仓库：仓库是版本权威。下次 lark_sync 镜像会把 Lark 的状态字段冲掉
- **不要**跳过 IM 通知：状态变更对干系人来说是关键信号
- **不要**把 approved 直接跳到 shipped 而不留时间戳：approved → shipped 之间有实施期，分开记录便于回溯
- **不要**同一份 PRD 反复 `review ↔ draft` 来回切：超过 2 次说明应该重起 v<n+1>，让历史清晰

## 关联

- [`rules/skills/prd_draft_from_lark.md`](./prd_draft_from_lark.md)
- [`rules/skills/prd_review.md`](./prd_review.md)
- [`rules/skills/prd_archive.md`](./prd_archive.md)
- [`rules/skills/lark_write.md`](./lark_write.md)
