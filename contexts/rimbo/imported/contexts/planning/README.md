# planning/

团队管理向产物。和 `products/` 的区别：products 装"做什么"，planning 装"怎么排"。

```
planning/
├── okr/<quarter>/         # 例: okr/2026q2/
├── weekly/<yyyy-ww>/      # 例: weekly/2026-w20/(周报、周会纪要)
└── decisions/             # 管理类决策(人事、资源、方向),与 products/<x>/decisions 区分
```

## 写入规则

OKR / 周报通常多人贡献片段，建议单文件单作者：

- `okr/2026q2/<handle>.md` — 个人 OKR 段
- `okr/2026q2/team.md` — 团队级，必须 PR
- `weekly/2026-w20/<handle>.md` — 个人周报段
- `weekly/2026-w20/digest.md` — 周会纪要，由当周记录人写

`decisions/` 全部走发布 skill，PR + review。
