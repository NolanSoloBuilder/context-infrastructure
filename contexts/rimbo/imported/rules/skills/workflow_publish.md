# Skill: workflow_publish

让 AI 在多人协作仓库里走和人开发一样的发布流程：分支 + PR + 自动 merge。这是 rimbo 仓库协作流的核心。

## When to Use

- AI 改了 `contexts/`、`rules/`、`tools/` 里的内容,需要发布到 main
- 跑完 `reflector.py` / `lark_sync` / `digest` 等定时任务,有产出要分发
- 写完 PRD / 决策记录 / 调研报告,要让团队看到

## 不需要走发布 skill 的写入

这些区域是单作者/不入 git，AI 直接 commit 即可：

- `contexts/memory/people/<我>/` — 单作者私域记忆
- `adhoc_jobs/<我>/` — 个人临时项目
- `.me` / `.env` — 不入 git

## 前置

- 本机装好 `gh` CLI 并已 `gh auth login`
- `git config user.name` / `user.email` 已配置（AI commit author 用这个）
- 当前分支是干净的，没有未提交的别的工作

## 步骤

### 1. 同步 main

```bash
git checkout main
git pull --rebase origin main
```

冲突就停下来问用户，不要自动 resolve（main 不该有本地未推改动）。

### 2. 起分支

分支命名约定：`feat/<purpose>-<handle>-<timestamp>`，purpose 用以下前缀：

| purpose 前缀 | 适用场景 |
|---|---|
| `prd-<name>` | 写/改 PRD |
| `rfc-<name>` | 写/改 RFC |
| `decision-<topic>` | 决策记录 |
| `research-<topic>` | 调研产物 |
| `capability-<name>` | capability 创建/升级 |
| `reflect` | reflector 周度蒸馏 |
| `lark-sync` | lark_sync 同步结果 |
| `digest` | digest 摘要 |
| `chore` | 维护性改动（修 typo、整理目录等） |

`<handle>` 取自 `.me`，`<timestamp>` 用 `YYYY-MM-DD-HHMM` 或 `YYYY-W<weeknum>`（reflector 用周编号）。

```bash
git checkout -b feat/prd-source_infra-xu-2026-05-16-1430
```

### 3. 完成改动并 commit

每个 commit 描述清楚意图，禁止 "update"、"fix"、"wip" 这种空消息。Conventional commits 风格：

```
docs(products/source_infra): add v0.1 PRD with scope and 3 milestones

- 定义 source_infra 的边界(只做拉取+去重,不做内容理解)
- 列出 3 个 milestone 与依赖
- 关联 capability source_infra 的 introduce 计划
```

### 4. dry-run merge 预测冲突

```bash
git fetch origin main
git merge-tree $(git merge-base HEAD origin/main) HEAD origin/main | head -50
```

输出空表示干净，能 fast-forward。否则按下面"冲突处理"段处理。

### 5. push

```bash
git push -u origin <branch-name>
```

### 6. 自审清单

在开 PR 前自查（写到 PR 描述里）：

- [ ] 没改 [敏感清单](#敏感清单) 里的文件，或改了但已设 reviewer
- [ ] 改 `rules/` 时考虑了团队层面影响，不是塞个人偏好
- [ ] frontmatter 里的 `owner` / `status` / `version` 正确
- [ ] PRD/RFC 类的 `updated:` 字段已更新到今天
- [ ] commit 消息描述清楚意图，不是 "update"
- [ ] 没有把 `.env` / `.me` / 凭据 / 大文件意外加进去

### 7. 开 PR

```bash
gh pr create \
  --title "<type>(<scope>): <summary>" \
  --body "$(cat <<'EOF'
## Why
<这次改动想解决什么>

## What
<改了哪些文件,语义是什么>

## Scope
<影响哪些下游(rules / contexts / 其他人的工作)>

## AI 自审
- [x] 没改敏感清单 / 已设 reviewer
- [x] frontmatter 字段正确
- [x] 没引入凭据或大文件
- [x] commit 消息描述清楚

## Reviewer
auto-merge | @<handle>
EOF
)"
```

### 8. auto-merge 决策

读 PR diff 自动判断：

- 命中敏感清单 → `Reviewer: @<handle>`，**不**开 auto-merge，等人 review
- 不命中 → 开 auto-merge

```bash
# auto-merge (squash)
gh pr merge --auto --squash --delete-branch
```

`--auto` 让 GitHub 在所有检查通过后自动 squash merge，并自动删远端分支。

### 9. 清理本地分支

```bash
git checkout main
git pull --rebase origin main
git branch -d <branch-name>
```

如果 `-d` 报 "not fully merged"（squash 后常见），用 `-D` 强删。

## 敏感清单

命中以下任一条 → **不** 开 auto-merge，必须人 review：

| 路径 / 改动 | 默认 reviewer |
|---|---|
| `rules/SOUL.md` / `TEAM.md` / `IDENTITY.md` / `COMMUNICATION.md` | 全团队任一成员 |
| `rules/axioms/team/` 任何新增或修改 | 全团队任一成员 |
| `rules/skills/` 新增或修改（不含 `_reference_grapeot/`） | 全团队任一成员 |
| `rules/members/<别人>.md` | 该 handle 本人 |
| `contexts/products/<x>/`（owner 不是自己） | `<x>` 的 owner |
| `contexts/capabilities/<x>/CAPABILITY.md` 新建 | 全团队任一成员 |
| `contexts/capabilities/<x>/CAPABILITY.md` frontmatter 中 `status`/`version` (major)/`owner`/`exposes`/`deps` 变更 | capability owner |
| `contexts/capabilities/<x>/interface.md` 契约变更 | capability owner，标 `breaking-change` label |
| `tools/lark/`、其他凭据/认证相关代码 | 全团队任一成员 |
| `periodic_jobs/` 任何脚本变更 | 全团队任一成员 |
| `.gitignore` / `.env.example` / `setup_guide.md` | 全团队任一成员 |

可 auto-merge 的非敏感改动包括：`contexts/products/<x>/`（owner 是自己）、`contexts/planning/<我的部分>/`、`contexts/research/`、`contexts/capabilities/<x>/changelog.md`、`contexts/capabilities/<x>/examples/`、`contexts/glossary/`、`contexts/lark_mirror/`（只有 lark_sync 写）、reflector 产出（不动 axioms 时）。

## 冲突处理

### `OBSERVATIONS.md` 的 append-only 冲突

总是 keep both，按 `caller + date` 排序。约定每条新观察前后留空行，单条不超过一段，行级冲突概率接近零。

### 文本冲突 AI 三方合并

```bash
git merge origin/main
# 如果有冲突,AI 读 <<<<<<< 段,判断:
# - 两边都是补充(列表追加、独立段) → 合并保留
# - 同一字段不同值(version: v1 vs v2) → 标 [conflict],PR 描述 @owner
# - 上游已超越本分支(本分支基于过期 main) → rebase
git add <resolved files>
git merge --continue
```

不能确定的冲突，在文件里保留显式标记：

```markdown
<!-- [conflict: 2026-05-16 by xu] 本分支说 v2,main 已经升到 v3 -->
[需要 owner 决定]
```

并在 PR 描述里 `@<owner>`。

### reflector PR 的"假冲突"

多人 reflector 几乎同时开 PR，第二个 PR base 在第一个 merge 前的 main 上，merge 时 rebase 出大量历史变化。预防：错峰 cron（见 `docs/COLLAB_PROTOCOL.md`）。出现时直接 `git rebase origin/main`，绝大多数情况是 OBSERVATIONS.md 的 append-only 自动合并。

## Lark 写回的特殊约束

调用 `tools/lark/lark_doc_push.py` 之前必须满足：

1. 本地无未提交改动
2. 当前 HEAD 已经 push 到 origin/main（即修改已经进了主线）

这样保证仓库 → Lark 是单向且可溯源。详见 `lark_write.md`。

## 错误恢复

| 错误 | 处理 |
|---|---|
| `git push` 被 reject（远端有新提交） | `git pull --rebase origin <branch>` 或重 rebase main |
| `gh pr create` 报 "GraphQL: Resource not accessible" | 检查 `gh auth status`，repo 权限要够 |
| auto-merge 卡住（CI 没通过 / 有 review 但还在等） | 别强 merge，给用户报状态 |
| 需要回滚 | 通过新 PR revert，不直接 force-push main |

## 关联

- `docs/COLLAB_PROTOCOL.md`：协作协议（cron 错峰、commit 规范、命名约定）
- `rules/IDENTITY.md`：身份识别决定 `<handle>`
- `rules/skills/capability_use.md`：capability 改动的特殊规则
- `rules/skills/lark_write.md`：Lark 写回的特殊约束
