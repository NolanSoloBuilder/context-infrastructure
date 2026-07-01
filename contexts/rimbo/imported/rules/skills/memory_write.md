# Skill: memory_write

让 AI 把当下学到的、值得跨 session 保留的事写到 rimbo 的记忆系统。配合 observer / reflector,但也用于交互过程中即时落地。

## When to Use

- 用户明确说「记一下」「这个以后别再问我」「这件事记到 OBSERVATIONS」
- AI 在帮 caller 解一个非平凡问题时,发现一条 caller 偏好/负责领域/避雷点的事实
- 完成一段调研/决策后,有跨人价值的判断值得沉淀

## 三层记忆的写入规则

| 层 | 路径 | 写入规则 | 走发布 skill? |
|---|---|---|---|
| L3 全局约束 | `rules/SOUL.md` / `TEAM.md` / `IDENTITY.md` / `COMMUNICATION.md` | **AI 不直接改** —— 只能起 PR 让团队 review | 是,敏感清单 |
| L1/L2 团队全局观察 | `contexts/memory/OBSERVATIONS.md` | append-only,只追加 `## Week:` 或 `## Date:` 区块 | 是,auto-merge |
| L1/L2 个人私域 | `contexts/memory/people/<我>/observations.md` | 追加 `## Date:` 区块 | 否,直接 commit |
| L1/L2 个人私域 - 偏好 | `contexts/memory/people/<我>/preferences.md` | 一段一段 append,可编辑 | 否,直接 commit |
| L1/L2 个人私域 - 项目笔记 | `contexts/memory/people/<我>/notes/<topic>.md` | 自由格式 | 否,直接 commit |

## 决策树

caller 让你记一件事时,先问自己三个问题:

1. **属于哪一层?**
   - 影响所有人 / 是判断框架 → 提议 L3(走 PR,慢沉淀)
   - 跨人有用 / 团队级别的事实 → L2 OBSERVATIONS.md
   - 只对当前 caller 有用 → 个人 people/<handle>/

2. **是观察还是偏好?**
   - 一次性事实(「今天定了 Foo 用 RSS 优先」)→ observations.md(带日期)
   - 长期偏好(「我不喜欢被反问」)→ preferences.md(带日期但作为偏好维护)
   - 跨次的项目背景知识 → notes/<topic>.md

3. **够不够"非显然"?**
   - 显然的事(「caller 是工程师」、「文件在 contexts/products/」)→ 不写,在 profile / WORKSPACE 里能查到
   - 非显然的事(「caller 上周改主意把 X 替换成 Y,原因是 Z」)→ 写

## 步骤

### 个人 observations.md（直接 commit）

```bash
# 1. 找到 handle
HANDLE=$(grep '^handle:' .me | awk '{print $2}')
TODAY=$(date +%Y-%m-%d)

# 2. 检查是否已有今日条目(observer 可能跑过)
DEST="contexts/memory/people/${HANDLE}/observations.md"
mkdir -p "$(dirname $DEST)"
if grep -q "^## Date: ${TODAY}$" "$DEST" 2>/dev/null; then
  # 在已有区块下追加(用 sed 或手工编辑)
  echo "[追加到现有 ${TODAY} 区块]"
else
  # 新增区块
  printf '\n\n## Date: %s\n\n- <你要记的事,带相对路径>\n' "$TODAY" >> "$DEST"
fi

# 3. commit (单作者目录,不走 PR)
git add "$DEST"
git commit -m "observe(${HANDLE}): note about <topic>"
```

### 团队 OBSERVATIONS.md（走 workflow_publish）

```bash
# 直接调 reflector 是周度蒸馏的语义。如果是即时记录某条跨人观察,
# 起一个 chore 分支,append 一行,走 publish auto-merge:

git checkout -b feat/chore-add-obs-${HANDLE}-$(date +%Y-%m-%d-%H%M)
printf '\n## Date: %s, by %s\n\n- <跨人观察>\n' "$(date +%Y-%m-%d)" "$HANDLE" \
  >> contexts/memory/OBSERVATIONS.md
git add contexts/memory/OBSERVATIONS.md
git commit -m "chore(memory): add cross-person observation about <topic>"
# 然后走 workflow_publish 步骤 5 起,自审 + PR + auto-merge
```

注意 OBSERVATIONS.md 的 append-only 约束:**绝对不要**修改历史区块,即使发现写错了。整理由 reflector 周度蒸馏处理。

### 提议改 L3（必须走 PR + review）

```
按 workflow_publish.md,起分支 feat/chore-update-rules-<handle>-<ts>。
在 PR 里写明:
- 改的是哪条规则,为什么改
- 这条规则之前的形态(quote 原句)
- 改后的形态(quote 新句)
- 这次改动的触发场景(具体一次对话或事件)

PR 描述里 Reviewer 字段填团队某成员或 @team。
绝对不开 auto-merge。
```

## 不要做的事

- **不要**把 caller 的敏感信息(住址、身份证、健康状况、未公开人事变动)写到任何记忆层
- **不要**未经 caller 同意写跨人事实("yan 不喜欢晨会"——这是 yan 自己 profile 里的事)
- **不要**用记忆替代代码注释——能在代码 / WORKSPACE.md 里说清楚的事不进记忆
- **不要**把同一件事重复写到三层(选最贴的一层)
- **不要**修改已有 `## Date:` / `## Week:` 区块(append-only 红线)

## 关联

- `periodic_jobs/ai_heartbeat/observer.py` — 自动化版本(每日跑)
- `periodic_jobs/ai_heartbeat/reflector.py` — 蒸馏与晋升
- `rules/skills/workflow_publish.md` — 共享区域写入流程
- `rules/IDENTITY.md` — `<handle>` 怎么解析
- `contexts/memory/people/README.md` — people 目录约定
