# capabilities/

项目阶段交付出来的"能力"。每个 capability 是 rimbo 对内（其他项目 / 其他成员 / AI agent）声明的、有契约的、可调用的能力。

## 判定标准

三条同时成立才算 capability，否则不进这里：

1. **可被复用** — 不是某个一次性项目的内部实现，而是设计上就准备给至少一个下游使用
2. **有契约** — 输入、输出、SLA、错误模式都明确，下游可以按契约调用，不需要读实现
3. **有维护者** — 有个 owner（个人或小组）对它的稳定性和演进负责

例：信源基础设施、内容打分模型、用户画像服务、Lark 文档双向同步引擎、内部 embedding 服务。
反例：某 PRD 里临时跑的数据处理脚本（不打算复用就不算）；个人 adhoc_jobs（没契约也没维护承诺）。

## 目录结构

```
capabilities/
├── README.md                        # 本文件
├── INDEX.md                         # 总览(AI 找能力的第一站)
└── <capability>/
    ├── CAPABILITY.md                # 能力卡片(主文件,frontmatter + 描述)
    ├── interface.md                 # 调用契约(CLI / HTTP / SDK / skill 的具体形态)
    ├── changelog.md                 # 版本演进
    ├── decisions/                   # 这个能力相关的 ADR(为什么这么设计)
    └── examples/                    # 调用示例
```

## CAPABILITY.md 模板

```yaml
---
name: source_infra
display_name: 信源基础设施
status: stable                  # experimental | beta | stable | deprecated
version: v1.2
owner: <handle>
contributors: [<handle>, <handle>]
since: 2026-MM-DD
last_reviewed: 2026-MM-DD       # 超过 90 天 INDEX 上会标 ⏰
implementation:
  primary_repo: Mindspace-ai/source-infra
  paths:
    - tools/source_infra/         # 本仓库内的入口(可选)
deps:
  - lark_bridge                   # 依赖另一个 capability
  - external: redis               # 外部依赖
exposes:
  - cli: source-pull
  - skill: rules/skills/source_pull.md
  - http: https://internal.../sources    # 可选
replaced_by:                      # 仅 deprecated 时填
---

# 信源基础设施 (source_infra)

## 它是什么
一两段话讲清楚:这个能力解决什么问题,边界在哪,典型的下游是谁。

## 怎么用
列举主要调用形态(CLI / skill / HTTP),每种给一两个最小示例。详细契约在 interface.md。

## 当前能力清单
- ✅ 从 RSS 拉取去重
- ✅ 从 Lark wiki 拉取
- 🚧 语义聚类(beta)
- ❌ 视频源(未支持)

## 已知限制 / 不适用场景
明确写出"如果你想做 X,别用这个能力"。避免下游误用。

## 维护与升级
谁负责、bug 怎么报、版本怎么升、deprecate 怎么处理。
```

## 生命周期

1. **构想期** — 还在 PRD/RFC 阶段，只在 `contexts/products/<product>/` 里讨论，不进 capabilities
2. **首次落地** — 第一版实现完成、有了下游真实使用意图，才创建 `capabilities/<cap>/`，状态 `experimental`。owner 通过发布 skill 提交 PR，标题 `capability: introduce <name>`
3. **稳定期** — 实测后 owner 提议升 `stable`。状态变更必须 PR + review，不允许 auto-merge
4. **退役** — 状态改 `deprecated`，`replaced_by:` 指向继任者，保留至少 90 天再考虑删除

## 与其他目录的关系

- **vs `contexts/products/<x>/`**：products 装"我们要做什么产品"（PRD/RFC/decisions），capabilities 装"我们已经做出了什么能力"。一个产品的几个迭代可能产出多个 capabilities；一个 capability 可能服务多个产品。多对多
- **vs `tools/`**：tools 装实现代码，capabilities 装契约和说明。本仓库内的实现指 `implementation.paths`，外部仓库指 `primary_repo`
- **vs `rules/skills/`**：skill 是 AI 用某个能力的具体步骤指南。capability 暴露 skill 形态时，`exposes` 字段指向对应 skill 文件，**skill 文件本身仍在 `rules/skills/` 下，不要复制到 capabilities**
- **vs `contexts/products/<x>/decisions/`**：单个产品内部的实现决策放产品下；影响整个 capability 的设计决策放 `capabilities/<cap>/decisions/`

## 协作工作流

发布 skill 在自审时新增几条规则：

| 改动 | 规则 |
|---|---|
| 创建新 capability（新增 `<cap>/CAPABILITY.md`） | PR + review，不 auto-merge |
| 修改 frontmatter 中的 `status` / `version`（major） / `owner` / `exposes` / `deps` | PR + review |
| 修改 `interface.md` 的契约（输入/输出/错误模式） | PR + review，标 `breaking-change` label |
| 修改 `examples/` / `changelog.md` / 正文非 frontmatter | auto-merge OK |

详见 `rules/skills/capability_use.md`（AI 怎么用 capability）和 `rules/skills/workflow_publish.md`（怎么发布）。
