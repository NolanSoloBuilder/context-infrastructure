# <handle>

_把这份模板复制到 `<handle>.md` 后填写。AI 在和你对话时会被动加载这一份。_

## 基础

- **称呼**：你希望 AI 怎么叫你
- **角色**：engineer / pm / designer / researcher / lead（可组合，如 `engineer+pm`）
- **时区**：UTC+8 等
- **Lark open_id**（可选，未来 IM 集成时用）：

## 当前在做什么

写 1-3 件你最近的主要工作，让 AI 在和你对话时有上下文。这一段保持新鲜——每月 reflector 会提醒过期。

例：
- 主导 `source_infra` capability 的 v1 → v2 迁移，重点解决 dedup 性能
- 在做 contexts/products/<x>/prd 的 v3 修订
- side：探索 Lark 群机器人入口

## 技术 / 工作偏好

帮 AI 调整给你的产出形态。例：

- **代码风格**：偏好类型严格、显式错误处理；不喜欢黑魔法
- **文档形态**：先给结论再给推理；判断要附依据
- **沟通**：直接、不用客套话；写错了直说

## 我负责的产物

约束 AI 默认在哪些目录直接 commit、哪些目录必须 PR：

- 我是 owner：`contexts/products/<x>/`、`contexts/capabilities/<y>/`
- 我是 contributor：`contexts/products/<z>/`

## 避雷点

写出和你协作时容易踩的坑，AI 会避开：

- 不要给我做选择题——直接给推荐选项 + 1 句话依据
- 不要在分析里堆 bullet，能一段话说清就一段话
- 不要假设我有时间读完 5000 字调研，先 200 字结论
