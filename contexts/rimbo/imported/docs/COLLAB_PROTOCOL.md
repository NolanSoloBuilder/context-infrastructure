# 协作协议

rimbo 是 **共享 workspace + 各自 AI 客户端** 的协作模式：仓库本身是事实源，每个人 clone 后用自己的 AI 客户端打开，git 是同步协议，PR 是协作机制。这份文档把所有跨人的约定集中在一处。

## 写入区域分类

| 区域 | 流程 |
|---|---|
| `contexts/memory/people/<我>/`、`adhoc_jobs/<我>/`、`.me`、`.env` | 直接 commit / 不入 git |
| `contexts/products/<x>/`（owner 是自己）、`contexts/planning/<我的部分>/`、`contexts/research/`、`contexts/glossary/`、`contexts/capabilities/<x>/changelog.md`/`examples/`、`contexts/lark_mirror/`（仅 lark_sync） | 走发布 skill auto-merge |
| `rules/`、`contexts/products/<x>/`（owner 不是自己）、`contexts/capabilities/<x>/CAPABILITY.md` 创建 / frontmatter 变更 / `interface.md` 契约变更、`tools/lark/` 等凭据相关、`periodic_jobs/`、`.gitignore`、`.env.example`、`setup_guide.md` | 走发布 skill，敏感清单，必须 review |

完整规则与判定逻辑在 [`../rules/skills/workflow_publish.md`](../rules/skills/workflow_publish.md) 的"敏感清单"段。

## 分支命名

`feat/<purpose>-<handle>-<timestamp>`

| purpose | 适用 |
|---|---|
| `prd-<name>` | 写/改 PRD |
| `rfc-<name>` | 写/改 RFC |
| `decision-<topic>` | 决策记录 |
| `research-<topic>` | 调研产物 |
| `capability-<name>` | capability 创建/升级 |
| `reflect` | reflector 周度蒸馏 |
| `lark-sync` | lark_sync 同步结果 |
| `digest` | digest 摘要 |
| `chore` | 维护性改动 |

`<handle>` 来自 `.me`。`<timestamp>` 用 `YYYY-MM-DD-HHMM`，reflector 用 `YYYY-W<weeknum>`，lark-sync 用 `YYYY-MM-DD-HH`。

## commit 消息

Conventional commits 风格，禁止空消息：

```
<type>(<scope>): <summary 50 字内>

<body 说清楚为什么改、影响什么>
```

type：`docs` / `feat` / `fix` / `chore` / `refactor` / `data`（数据/记忆类）

例：

```
docs(products/source_infra): add v0.1 PRD with 3 milestones

- 定义 source_infra 的边界(只做拉取+去重,不做内容理解)
- 列出 3 个 milestone 与依赖
- 关联 capability source_infra 的 introduce 计划
```

## PR 描述模板

```markdown
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
```

## cron 错峰

reflector / observer / lark_sync / digest 这类自动产出 PR 的任务，多人同跑容易撞 PR。约定错峰：

| 任务 | 频率 | 时间窗口建议 |
|---|---|---|
| `observer.py`（个人记忆，写自己 people/ 不开 PR） | 每日 | 任意，建议 23:00-23:55 |
| `reflector.py`（开 PR） | 每周 | **错峰**：A 周一 8:00、B 周三 8:00、C 周五 8:00 |
| `lark_sync/`（开 PR） | 每 6 小时 | 任意（自带 stale 检查会自动跳过） |
| `digest/`（开 PR） | 周度 / 日度 | 任意，建议早 9:00 |

新成员入职时由团队协调把他放进 reflector 错峰表。

## 冲突处理

### `OBSERVATIONS.md` 的 append-only

每条新观察前后留空行，单条不超过一段。冲突总是 keep both，按 `caller + date` 排序。

### 三方合并

AI 优先尝试自动合并；不能确定的冲突，在文件里保留显式标记并在 PR 里 @owner：

```markdown
<!-- [conflict: 2026-05-16 by xu] 本分支说 v2,main 已经升到 v3 -->
[需要 owner 决定]
```

### reflector "假冲突"

按错峰表跑可避免大部分。出现时直接 `git rebase origin/main`。

## Lark 写回顺序

**先 commit + push + merge → 再调 lark_doc_push**。仓库是版本权威，Lark 是发布面，不允许 AI 跳过仓库直接写 Lark。具体见 `rules/skills/lark_write.md`（Phase 2 落地）。

## 分支清理

- `gh pr merge --auto --delete-branch` 自动删远端分支
- 本地分支：每次跑发布 skill 步骤 9 自检并清理

如果残留分支堆积（`git branch | wc -l > 20`），手动一次性清：

```bash
git fetch -p
git branch -vv | awk '/: gone]/{print $1}' | xargs -r git branch -D
```

## review 责任

敏感清单的 PR 默认 reviewer 由发布 skill 自动填：

- 改别人 owner 的产物 → 该 owner
- 改 capability 契约 → capability owner
- 改 `rules/` / `tools/lark/` / `periodic_jobs/` / 其他全团队级 → 团队任一成员

被 @ 的 reviewer 收到通知后建议 24 小时内响应；超过 48 小时无响应，PR 作者可以 @ 第二人。

## 不变量（禁止打破）

- main 分支不允许 force push
- `.env` / `.me` / 凭据 / `.cache/` / 大文件不入 git
- `rules/` 任何修改必须 PR
- `contexts/capabilities/` 创建和契约变更必须 review
- `contexts/memory/OBSERVATIONS.md` append-only，不允许编辑历史条目
- Lark 写回必须经过 git
- AI commit 时使用 `git config user.email` 配置的本人身份，不假冒别人

## 版本

本协议 v0.1（Phase 1）。后续修改本协议属于敏感清单（影响所有人），必须 PR + review。
