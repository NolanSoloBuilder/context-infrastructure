# Skill: lark_write

让 AI 安全地把仓库里的内容**单向**写回 Lark 文档。这是 rimbo 仓库 ↔ Lark 集成的关键约束。

## 核心约束

**仓库是版本权威，Lark 是发布面**。任何对 Lark 文档的写回必须先经过 git：

1. 改动先 commit 到本地分支
2. 走 `workflow_publish` 发 PR + merge 到 origin/main
3. **再**调 `tools/lark_cli/push.sh` 推送

不允许 AI 跳过仓库直接改 Lark——一旦那样做，git history 和 Lark 会渐行渐远，下次 lark_sync 会把仓库的版本"覆盖"回去（或反之），双方都不可信。

## 路径选择

- **主路径**：`tools/lark_cli/push.sh`（OAuth 个人身份）。日常人工写回都走这条
- **fallback**：`tools/lark/lark_doc_push.py`（tenant_access_token）。仅在 lark-cli 不可用 / 写回操作需要在 cron 里跑 / 应用身份比个人身份更合适时用。**未充分验证**，慎用

## When to Use

- 在仓库里改了一份镜像过的 Lark 文档，要把改动同步回 Lark
- 起草了一份新的对外文档（产品发布说明、对外信源说明），先 review 通过仓库内版本，再发布到 Lark
- PRD 状态变更（draft → review → approved → shipped）时，文档头部状态字段同步到 Lark
- IM 推送某份产物（用 `tools/lark_cli/im_send.sh`，不在本 skill 范围）

## 前置检查

`tools/lark_cli/push.sh` 自己会跑这些检查（fallback `lark_doc_push.py` 同理），AI 不需要重复跑，但要理解为什么会失败：

| 检查 | 失败表现 | 如何修复 |
|---|---|---|
| 工作树干净 | `abort: 工作树有未提交改动` | 先 commit + push + merge |
| HEAD 已推到 origin/main | `abort: HEAD 比 origin/main 多 N 个 commit` | push 当前分支 + 走 `workflow_publish` 把它 merge 到 origin/main |
| lark-cli 已登录 | `auth: not logged in` 或 `tokenStatus: invalid` | `npx lark-cli auth login --domain docs,wiki,drive,im,contact` |
| Python fallback 凭据 | `runtime error: ... 未配置` | 配 `.env` 或 1Password vault |

不存在 `--skip-repo-check` 这种逃生口——主路径包装器和 fallback 都强制检查。

## 步骤

### 1. 在仓库里先把改动落地

按目标文档的语义，改对应的镜像文件 / 产出文件：

- 如果是镜像里的文档（`contexts/lark_mirror/<space>/<title>.md`），不能直接改！镜像是只读的。改动应该落到对应的源头：
  - 如果文档语义是 PRD → 改 `contexts/products/<x>/prds/v<n>.md`，再单独同步到 Lark 对应位置
  - 如果文档语义是会议纪要 → 仓库里没对应源头，那这次写回是「补充原会议纪要」，落到一份临时草稿文件再走发布

明确写回目标 obj_token：从 Lark URL 抠或 grep 镜像首行。

### 2. 走 workflow_publish

```
按 rules/skills/workflow_publish.md:
- 起分支 feat/lark-sync-<topic>-<handle>-<timestamp>
- commit 描述要包含「将同步到 Lark docx <obj_token>」
- 自审清单 + PR + merge
```

### 3. 调 push 包装器

merge 到 origin/main 之后：

```bash
git checkout main
git pull --rebase origin main

# 主路径
./tools/lark_cli/push.sh <obj_token> path/to/source.md
```

包装器会再次校验工作树干净 + HEAD vs origin/main，校验通过后才打 API。

fallback 路径（仅在 lark-cli 不可用时）：

```bash
python -m tools.lark.lark_doc_push \
  --doc-id <obj_token> \
  --file path/to/source.md \
  --repo-root .
```

### 4. 验证

```bash
# 拉回来对比
./tools/lark_cli/pull.sh <obj_token> /tmp/verify.md
diff /tmp/verify.md path/to/source.md  # 期望差异最小
rm /tmp/verify.md
```

不一致就回到第 1 步，不要在 Lark 端手改。

## 不要做的事

- **不要**绕过 git 顺序：commit → push → merge → 再 push Lark。绝不反过来
- **不要**改完 Lark 再回头补仓库的 commit
- **不要**把多个无关改动塞到一次 push 里（一次写回对应一份语义改动，便于回滚）
- **不要**对涉密文档用 push（财务、人事、客户名单等——和 caller 确认目标文档是否对外可见）
- **不要**用 push 替别人写其名义的产物（commit author 是仓库里的本人，但 Lark 上文档作者随 caller 的 OAuth 身份变化；如果接收方期待是「某成员的发布」，让该成员本人执行 push）

## 失败回滚

push 失败或推上去后发现错版本：

```bash
# 1. 在 Lark 端用「文档历史」恢复到上一版（运维口子，不在 AI 自动化范围内）
# 2. 仓库内同步回滚：用新 commit revert 错的那个 commit，而不是 force-push main
# 3. revert 的 PR 走正常 workflow_publish
```

## 关联

- [`rules/skills/lark_read.md`](./lark_read.md) — 读取（和写回的反方向）
- [`rules/skills/workflow_publish.md`](./workflow_publish.md) — 仓库内发布流程
- [`tools/lark_cli/README.md`](../../tools/lark_cli/README.md) — 主路径包装器
- [`tools/lark/README.md`](../../tools/lark/README.md) — fallback Python 路径
- [`docs/COLLAB_PROTOCOL.md`](../../docs/COLLAB_PROTOCOL.md) — Lark 写回顺序与协议
