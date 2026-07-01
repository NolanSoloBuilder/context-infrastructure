# products/

每个产品/项目一个子目录，装这个产品的产物：

```
products/<product>/
├── prd/             # 产品需求文档(每版一文件)
├── rfc/             # 设计提案(架构 / 模块 / 接口)
├── decisions/       # ADR 风格决策记录(一条一文件)
└── README.md        # 产品现状摘要(由 owner 维护,1 屏内)
```

## frontmatter 约定

每份 PRD / RFC / decision 顶部:

```yaml
---
title: <标题>
owner: <handle>          # 这份产物的负责人,默认修改人
status: draft | review | approved | superseded
version: v0.1
created: 2026-MM-DD
updated: 2026-MM-DD
related:                 # 相关产物(可选)
  - contexts/products/<x>/prd/v2.md
  - contexts/capabilities/<y>/CAPABILITY.md
---
```

## 写入规则

- owner 是 `<handle>` 本人 → 走发布 skill,自动 merge
- owner 不是本人 → 走发布 skill,标 `Reviewer: @<owner>`,人审

详见 `rules/skills/workflow_publish.md`。
