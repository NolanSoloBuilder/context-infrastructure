# Rimbo Context Archive

更新日期：2026-06-17

这个目录接管原 `/Users/xuhao/Documents/Other/rimbo-work-context` 中与 Rimbo 相关的长期上下文。原仓可以视为 deprecated source；后续在当前 `context-infrastructure` 里回答 Rimbo 产品、代码仓库、Lark 文档、团队协作规则相关问题时，优先从这里开始。

## 入口顺序

1. 先读本文。
2. 读 `MIGRATION_MANIFEST.md`，确认迁移范围和哪些内容是历史快照。
3. 读 `SOURCE_CODE_PATHS.md`，定位当前本机源码入口。
4. 读 `imported/contexts/products/rimbo/README.md`，获取产品入口。
5. 读 `imported/rules/TEAM.md`，获取团队和产品语义。
6. 具体问题再进入 `imported/contexts/lark_mirror/`、`imported/contexts/repos/` 或 `imported/rules/skills/`。

## 目录说明

- `imported/contexts/`：原仓的上下文产物，包括产品入口、Lark 镜像、repo cards、规划、调研、capabilities、memory。
- `imported/rules/`：原仓核心规则、团队画像、成员 profile、skills。
- `imported/docs/`：原仓协作协议、外部仓协议、Rimbo work context 改造方案等元文档。
- `imported/tools/lark_cli/`：原仓 Lark CLI 包装器和说明，保留用于理解历史 Lark 读写路径。
- `imported/AGENTS.md`、`imported/README.md`、`imported/setup_guide.md`：原仓入口文档快照。

## 当前权威口径

Rimbo.ai 是 Mindspace-ai 旗下 rimbo 团队的 AI 个人信息助手。核心模型是：

`Channel` 定义关注问题或任务，系统跨平台 follow `Source`，捕捉 `Change`，解释 `Importance`，保留 `Evidence`，最后沉淀为 `Memory`。

当前产品阶段是 MVP / Track：验证 AI + 订阅 > 订阅，让用户不再错过关键变化。后续 Archive / Network 阶段只作为上下文，不应混入 MVP 范围判断。

## 重要约束

- `imported/contexts/lark_mirror/` 是从 Lark 拉下来的历史镜像。它适合检索和理解背景，不代表 Lark 远端一定仍是最新状态。
- 原仓的 `contexts/repos/` 仓库卡片多数 `last_reviewed` 是 2026-05-18。涉及真实代码实现时，必须重新看对应代码仓的当前状态。
- 当前本机源码入口以 `SOURCE_CODE_PATHS.md` 为准；repo card 只保留仓库角色和历史扫描结论。
- 原仓的 `contexts/capabilities/` 仍是空骨架。不要把候选 capability 当成已交付能力。
- 原仓的成员 profile 多份是 AI 代写骨架。涉及个人偏好、owner、职责边界时，要当成待确认信息。
- 后续新增 Rimbo 上下文应写到当前目录下，不再写回原 `rimbo-work-context`。

## 常用路径

- 产品入口：`imported/contexts/products/rimbo/README.md`
- 产品规划：`imported/contexts/lark_mirror/产品调研/产品规划.md`
- 信源库：`imported/contexts/lark_mirror/产品调研/信源库建设PRD.md`
- 本机源码路径：`SOURCE_CODE_PATHS.md`
- 研发文档：`imported/contexts/lark_mirror/研发部门/`
- 仓库索引：`imported/contexts/repos/INDEX.md`
- 协作设计：`imported/docs/RIMBO_REDESIGN.md`
- Lark CLI：`imported/tools/lark_cli/README.md`
