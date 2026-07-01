# research/

数据与调研产物。

```
research/
├── user_research/         # 用户研究报告
├── experiments/           # 线上 / 离线实验记录
└── feedback/              # 用户反馈(原始 + 整理)
```

## 命名

- `user_research/<yyyy-mm>_<topic>.md`
- `experiments/exp_<id>_<short_name>.md`
- `feedback/<source>_<yyyy-mm>.md` (source 如 `lark`、`survey`、`bug_report`)

## 与 contexts/survey_sessions/ 的区别

`survey_sessions/` 是 deep research 工作流（`workflow_deep_research_survey`）的标准产出位置——多 agent 并行调研后的成果，结构是固定的 phase 1/2/3。

`research/` 装的是更日常的调研产物，包括但不限于 user research、AB 实验、用户反馈整理。两者可以互相引用。
