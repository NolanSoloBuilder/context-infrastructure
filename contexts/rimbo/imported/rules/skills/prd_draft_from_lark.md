# Skill: prd_draft_from_lark

PRD 起草流程：**Lark 拉草稿 → 本地迭代 → 推回 Lark**。这是从一份 Lark 上的非正式讨论 / 早期草稿走向仓库内有版本的 PRD 的标准动作。

## When to Use

- caller 说"PRD 在 Lark 上，把它拉下来本地继续写"
- 在 Lark 文档里和 PM / RD 讨论了一份产品需求，要把它变成仓库内可追溯的 PRD
- 起一个新的 `contexts/products/<x>/prd/v0.1.md`，需要复用 Lark 上已有内容作为起点

## Prerequisites

- lark-cli 授权完成（[`setup_guide.md`](../../setup_guide.md) Step 2.5）
- `<product>` 在 `contexts/products/` 下已存在（不存在的话先建目录 + README，参考 `contexts/products/README.md`）
- 拿到 Lark 草稿的 obj_token（URL 里抠）

## 步骤

### 1. 从 Lark 拉草稿

```bash
PRODUCT=<product>
DOC_ID=<obj_token>
mkdir -p contexts/products/$PRODUCT/prd
./tools/lark_cli/pull.sh $DOC_ID contexts/products/$PRODUCT/prd/v0.1.md
```

### 2. 加 frontmatter + 镜像头

文件首行加 lark-mirror 标记，让后续同步能识别源；下面接 frontmatter（按 `contexts/products/README.md` 约定）：

```markdown
<!-- lark-mirror obj_token=<DOC_ID> domain=feishu.cn -->
---
title: <PRD 标题>
owner: <你的 handle>
status: draft
version: v0.1
created: 2026-MM-DD
updated: 2026-MM-DD
related:
  - <相关 capability 或上一版 PRD>
---

# <PRD 正文>

...
```

> 把 lark-mirror 标记放在 frontmatter **之上**：导出回 Lark 时会被剥掉，但本地解析 frontmatter 不受影响。

### 3. 本地迭代

正常编辑 markdown，有需要时调 AI 协助。改动期间保持 `status: draft`。

### 4. 走 workflow_publish 提交到仓库

按 [`workflow_publish.md`](./workflow_publish.md)：

```
分支：feat/prd-<product>-<handle>-<timestamp>
commit："docs(products/<product>): add v0.1 PRD draft, sync target Lark docx <obj_token>"
```

owner 是自己 → 自动 merge；owner 是别人 → 标 Reviewer 等审。

### 5. merge 后推回 Lark

```bash
git checkout main
git pull --rebase origin main
./tools/lark_cli/push.sh <DOC_ID> contexts/products/$PRODUCT/prd/v0.1.md
```

`push.sh` 会自查工作树干净 + HEAD 与 origin/main 一致。

### 6. 验证

```bash
./tools/lark_cli/pull.sh <DOC_ID> /tmp/verify.md
diff /tmp/verify.md contexts/products/$PRODUCT/prd/v0.1.md
rm /tmp/verify.md
```

差异应当只在 lark-mirror 标记 / frontmatter（这些 push 时被剥掉）。

## 不要做的事

- **不要**在 Lark 端边改边推：本地是版本权威，Lark 端的临时改动会在下次 push 时被覆盖
- **不要**跳过 workflow_publish 直接 push Lark：`push.sh` 自查会拒绝
- **不要**把别人 owner 的 PRD 自己起草：起草前先和 owner 对齐归属

## 后续流程

- 起草到 ready for review 时 → [`prd_review.md`](./prd_review.md)
- PRD 状态切换 → [`prd_status_change.md`](./prd_status_change.md)
- 已定稿 PRD 入归档 → [`prd_archive.md`](./prd_archive.md)

## 关联

- [`rules/skills/lark_read.md`](./lark_read.md)
- [`rules/skills/lark_write.md`](./lark_write.md)
- [`rules/skills/workflow_publish.md`](./workflow_publish.md)
- [`contexts/products/README.md`](../../contexts/products/README.md)
