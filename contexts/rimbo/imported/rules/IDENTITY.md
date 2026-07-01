# IDENTITY.md - 当前 caller 是谁

每个团队成员在自己机器上 clone 仓库后，第一次使用前要：

```bash
cp .me.example .me
# 编辑 .me,填写自己的 handle
```

`.me` 文件不入 git（见 `.gitignore`），所以每个人的本地状态彼此独立。

## AI 加载流程

每次 session 启动，AI 按这个顺序解析身份：

1. **读 `.me`**：取出 `handle` 字段。如果文件不存在或没有 handle，按 `guest` 处理，跳过个人画像加载。
2. **加载 profile**：读 `rules/members/<handle>.md`。如果文件不存在，提示用户「检测到你是 `<handle>`，但 members 目录里没有你的 profile，要不要现在建一个？」，并给出模板。
3. **加载私域记忆**：按需检索 `contexts/memory/people/<handle>/` 下的最近观察。不全文加载，只在话题相关时检索。
4. **设置写入归属**：后续 AI 主动 commit 时，commit author 用 git 配置的身份；写入 `contexts/memory/people/` 时只能写 `<handle>` 自己的目录。

## guest 模式

匹配不到 handle 时（新人还没建 profile / `.me` 没填 / 临时 demo），按 guest 处理：

- 不加载 `members/<handle>.md`
- 不加载 `contexts/memory/people/<handle>/`
- 仍然加载 `SOUL.md` / `TEAM.md` / `WORKSPACE.md` / `COMMUNICATION.md` / `skills/INDEX.md`
- 写入操作受限：禁止写 `contexts/memory/people/`，可以写 `adhoc_jobs/_guest/` 或临时分支

## 写入归属约束

| 区域 | 谁能写 |
|---|---|
| `contexts/memory/people/<handle>/` | 仅 handle 本人的 AI |
| `rules/members/<handle>.md` | 仅 handle 本人的 AI |
| `adhoc_jobs/<handle>/` | 仅 handle 本人的 AI（临时项目） |
| `contexts/products/<x>/`（owner 是自己） | 直接 commit |
| `contexts/products/<x>/`（owner 不是自己） | 必须走发布 skill 开 PR，标 `Reviewer: @<owner>` |
| `rules/` 任何文件 | 必须走发布 skill 开 PR，且在敏感清单内不 auto-merge |
| `contexts/capabilities/` 创建或 frontmatter 变更 | 同上敏感清单 |

详见 `skills/workflow_publish.md` 和 `../docs/COLLAB_PROTOCOL.md`。

## 当前已注册的成员

见 [`members/INDEX.md`](./members/INDEX.md)。
