# Skill: capability_use

让 AI 在做任何"用某个能力"或"提议某个能力"的工作时,正确地从 `contexts/capabilities/` 出发,而不是按 PRD 里描绘的理想形态盲目调用、或者重复造已有能力。

## When to Use

- 用户问"我们有什么能力可以做 X"
- AI 在写 PRD/RFC 时要引用某个已有能力
- AI 准备调用 / 集成某个能力(CLI / skill / HTTP)
- AI 在某个产品工作中产出了具备 capability 特征的东西,要决定"是否应该提升为 capability"
- 需要更新某个 capability 的 status / version / 契约

## 找能力的标准动作

1. 先读 [`contexts/capabilities/INDEX.md`](../../contexts/capabilities/INDEX.md) 总览
2. 定位到具体 `<capability>/CAPABILITY.md`
3. 读这个文件的 frontmatter(状态、版本、owner、exposes)和"已知限制 / 不适用场景"段
4. 如需调用细节,再读 `<capability>/interface.md`
5. 如需历史背景,再读 `<capability>/decisions/` 和 `changelog.md`

不要跳过 1-3 直接看实现代码。capability 存在的价值就是让你不用读实现。

## 用之前必读"已知限制"

`CAPABILITY.md` 里有一段"已知限制 / 不适用场景"。**调用前必须读这段**——很多误用都来自"按 PRD 里描绘的理想形态调用,但实际能力还没到那一步"。

读完后:

- 当前需求 ⊆ 能力清单 → 直接用
- 部分匹配 / 在 🚧 beta 段 → 用,但 PR 里说明依赖了 beta 能力
- 在 ❌ 不适用 / 已知限制段 → 不要硬上,提议给 capability owner 提个增量需求,或换路径

## 状态语义

调用前看 `status`:

| status | 调用约束 |
|---|---|
| ✅ stable | 直接用,有兼容性承诺 |
| 🟡 beta | 可以用,PR 描述里写明依赖了 beta capability |
| 🧪 experimental | 不要在生产路径上用;实验性集成可以,要承担 breaking change |
| ⚠️ deprecated | 不要再新增依赖。如果已有依赖,按 `replaced_by:` 指引迁移 |
| ⏰ stale (last_reviewed > 90d) | owner 该 review 了。可以用,但在 PR 里 @owner 提醒 review |

## 提议新 capability(从 product 内部产物升级)

判断升级的三条门槛(全部满足才提议):

1. 至少有一个非本产品的下游真实想用
2. 已经能写出明确契约(输入/输出/SLA/错误模式)
3. 有人愿意当 owner,承担稳定性和演进责任

满足后:

1. 创建 `contexts/capabilities/<name>/` 目录
2. 写 `CAPABILITY.md`(参照 `contexts/capabilities/README.md` 模板),`status: experimental`
3. 写 `interface.md` 描述契约
4. 把 `decisions/` 里相关 ADR 从产品目录复制过来(原件留在产品下作历史)
5. 走发布 skill,PR 标题 `capability: introduce <name>`,**敏感清单**——必须 review

## 升级状态

experimental → beta → stable 的升级:

1. 先在 `changelog.md` 写清这一版改了什么、是否 break 契约
2. 修改 `CAPABILITY.md` frontmatter 的 `status` 和 `version`
3. major 版本(契约变化) → 必须 PR + review,标 `breaking-change` label
4. minor / patch + 不动 status → 也要 PR + review (frontmatter 改 `version` 命中敏感清单)

参见 `contexts/capabilities/README.md` 的"协作工作流"段。

## 退役 capability

1. 找到 / 创建继任者
2. 修改 frontmatter:`status: deprecated`,`replaced_by: <new_capability>`
3. INDEX 自动归到 deprecated 区
4. PR + review
5. 通知所有当前依赖方(grep `deps:` 字段)
6. 保留至少 90 天再考虑删除目录

## 修 capability 文档但不动契约

修 `examples/` / `changelog.md` / 正文非 frontmatter 内容 → auto-merge OK,不进敏感清单。

## 与发布 skill 的关系

所有 capability 写入都通过 `workflow_publish.md` 的发布流程。这份 skill 补充的是 **capability 特有的判断**——什么时候新建、状态怎么升、什么必须人 review。具体的分支/PR/merge 步骤都在 `workflow_publish.md` 里。

## 反例

- ❌ 在 PRD 里写"集成信源服务,自动去重并语义聚类"——不读 `source_infra/CAPABILITY.md` 的能力清单,语义聚类可能还在 🚧
- ❌ 看到 `tools/source_infra/` 有代码,直接 import 调用——绕过契约层,后续 capability 升级会断
- ❌ 在产品 PRD 阶段就建 `contexts/capabilities/<name>/`——构想期不进 capabilities,等首次落地有真实下游再升
- ❌ 一个项目内部的临时脚本占据 capability 位置——三条判定标准没过

## 关联

- `contexts/capabilities/README.md`:capability 概念定义和模板
- `contexts/capabilities/INDEX.md`:总览
- `rules/skills/workflow_publish.md`:发布流程
- `docs/COLLAB_PROTOCOL.md`:整体协作协议
