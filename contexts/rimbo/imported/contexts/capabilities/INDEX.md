# Capabilities Index

rimbo 团队当前对内（其他项目、其他成员、AI agent）声明的、有契约的、可调用的能力。

> **概念定义见 [`./README.md`](./README.md)。**

## AI 加载策略

session 启动时不主动加载。当用户问"我们有什么能力可以做 X"、"信源相关有现成的吗"、"团队有没有 embedding 服务"等问题，AI 第一步读这个 INDEX，定位到对应 `<capability>/CAPABILITY.md`。

## 状态图例

- ✅ stable — 契约稳定，下游可以放心依赖
- 🟡 beta — 契约基本稳定，可能小调
- 🧪 experimental — 实验中，下游用要承担 breaking change
- ⚠️ deprecated — 在被替代，参考 `replaced_by:` 字段
- ⏰ stale — `last_reviewed` 超过 90 天未更新，owner 该 review 了

## 当前 capabilities

> _Phase 1 阶段先留空。第一个 capability（候选：`source_infra`、`lark_bridge`）由 owner 通过发布 skill 提交 PR 时落到这里。_

### 数据与信源

_<空，待第一个 capability 落地>_

### 内容处理

_<空>_

### 基础设施

_<空>_

### Deprecated

_<空>_

## 依赖图

> _capability 之间的依赖关系（CAPABILITY.md 的 `deps` 字段汇总）。Phase 1 不维护，等 capability 数 ≥ 3 后再生成。_
