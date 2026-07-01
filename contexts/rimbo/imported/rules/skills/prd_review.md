# Skill: prd_review

PRD 评审流程：**本地写完 → 推 Lark → IM 通知评审群**。让 review 在 Lark 里发生（评论、@人），仓库保留可追溯的版本快照。

## When to Use

- 一份 PRD 在仓库内 `status: draft` 完成，准备发起评审
- 评审反馈在 Lark 上集中，仓库不直接收 PR comment 作为评审意见

## Prerequisites

- PRD 在仓库内已 merge 到 main（`status: draft`）
- Lark 端有对应的 docx，且 obj_token 已记在 PRD 文件首行 `<!-- lark-mirror obj_token=... -->`
- 评审群 chat_id 可解析（按下面优先级查找）

## 通知群解析顺序

按这个顺序找 chat_id，命中即用：

1. `contexts/products/<product>/_meta.yml` 的 `review_chat_id`（产品自定义评审群）
2. `contexts/team_config.yml` 的 `lark.default_notify_chat_id`（团队默认通知群）

如果两者都没有，停下来问 caller，不要瞎猜。

## 步骤

### 0. （可选）配产品级评审群

只有当某个产品**需要单独的评审群**（不想发到团队默认群）时才建：

`contexts/products/<product>/_meta.yml`：

```yaml
review_chat_id: oc_xxxxxxxxxxxxxxxx   # 覆盖团队默认
docs:
  v0.1:
    obj_token: <obj_token>
    docx_url: https://example.feishu.cn/docx/<obj_token>
```

走 `workflow_publish` 提交（共享区域，owner 是自己时 auto-merge）。

如果用团队默认群，跳过本步骤，从 1 开始。

### 1. 切状态到 review

改 PRD frontmatter：

```yaml
status: review
updated: 2026-MM-DD
```

走 `workflow_publish`：

```
分支：feat/prd-<product>-review-<handle>-<timestamp>
commit："docs(products/<product>): mark v<n> PRD ready for review"
```

merge 到 main。

### 2. 推回 Lark

```bash
git checkout main && git pull --rebase origin main
./tools/lark_cli/push.sh <obj_token> contexts/products/<product>/prd/v<n>.md
```

### 3. IM 通知评审群

格式（精炼为主，让收到通知的人 30 秒内能判断是否要点开）：

```
[PRD review] <product> v<n>
  目标: <一句话产品目标>
  关键变化: <相对上一版的 1-3 个最重要变化>
  期望反馈周期: <X 天>
  文档: <docx_url>
  仓库快照: <commit URL>
```

> `im_send.sh` 会自动在最前面加 `[AI]` 前缀、末尾追加 `— <handle> / via lark-cli`，所以收到的实际是 `[AI] [PRD review] ... — xu / via lark-cli`。模板里**不要**再手动写这两行。

发送：

```bash
# 解析 chat_id（产品级 → 团队默认）
CHAT_ID=$(yq '.review_chat_id // ""' contexts/products/<product>/_meta.yml 2>/dev/null)
[ -z "$CHAT_ID" ] && CHAT_ID=$(yq '.lark.default_notify_chat_id' contexts/team_config.yml)

TEXT="[PRD review] <product> v<n>
  目标: ...
  关键变化: ...
  期望反馈周期: 3 天
  文档: https://example.feishu.cn/docx/<obj_token>
  仓库快照: https://github.com/Mindspace-ai/rimbo-work-context/commit/<sha>"

./tools/lark_cli/im_send.sh "$CHAT_ID" "$TEXT"
```

> 没装 `yq` → `brew install yq`，或用 `python3 -c "import yaml,sys;print(yaml.safe_load(open(sys.argv[1]))[...])"` 提取。

### 4. 收集反馈

评审在 **Lark 端进行**（评论、@、聊天讨论）。一条意见对应一次"是否纳入下一版"的判断：

- 纳入 → 在仓库内改 `prd/v<n>.md`（小改）或新建 `prd/v<n+1>.md`（大改），走新 PR
- 不纳入 → 在 PRD 末尾的 `## 未采纳的反馈` 段落简短记录"为什么不采"
- 仓库内不需要逐条同步 Lark 端评论，让 Lark 端的对话作为审议记录

### 5. 关闭评审

评审周期结束后切到下一个状态（[`prd_status_change.md`](./prd_status_change.md)）：approved / 退回 draft / superseded。

## 不要做的事

- **不要**让评审反馈在 GitHub PR 里碎片化：评审的核心阵地是 Lark，PR 只对应仓库内的版本快照
- **不要**漏掉 IM 通知：没人知道 PRD 进入 review，等于没 review
- **不要**在 review 状态下边收意见边偷偷改 PRD：每轮意见处理后明确切到 `v<n+1>` 或重启 review 周期

## 关联

- [`rules/skills/prd_draft_from_lark.md`](./prd_draft_from_lark.md)
- [`rules/skills/prd_status_change.md`](./prd_status_change.md)
- [`rules/skills/lark_write.md`](./lark_write.md)
- [`rules/skills/workflow_publish.md`](./workflow_publish.md)
