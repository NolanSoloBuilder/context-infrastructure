# Rimbo Migration Manifest

迁移日期：2026-06-17

源仓：`/Users/xuhao/Documents/Other/rimbo-work-context`

目标：`/Users/xuhao/Documents/Other/context-infrastructure/contexts/rimbo`

## 迁移原因

用户决定废弃独立的 `rimbo-work-context`，将 Rimbo 相关长期上下文纳入当前 `context-infrastructure` 统一管理。

## 已迁移范围

机械复制到 `contexts/rimbo/imported/` 的内容：

- `contexts/`
- `docs/`
- `rules/SOUL.md`
- `rules/IDENTITY.md`
- `rules/TEAM.md`
- `rules/COMMUNICATION.md`
- `rules/WORKSPACE.md`
- `rules/members/`
- `rules/skills/`
- `tools/lark_cli/`
- `AGENTS.md`
- `README.md`
- `setup_guide.md`

迁移时排除了 `.DS_Store`。未复制 `.git/`、`.venv/`、`node_modules/`、`.remember/`、`.env`、`.me` 等运行时或本机身份文件。

## 快照统计

- 总文件数：203
- 目录大小：约 2.1MB
- Lark mirror 文档数：105
- 原仓 skill 文件数：23

## 未迁移范围

- 原仓 git history。
- 原仓 Python / Node 运行环境。
- 原仓 `tools/lark/` Python fallback 工具代码。
- 原仓 `periodic_jobs/` 自动任务代码。
- 原仓 `adhoc_jobs/` 个人临时任务。
- 本机 OAuth / token / `.env` / `.me`。

这些内容更像运行系统或个人环境，不属于当前“上下文管理”第一轮迁移。如果后续要把 Lark 同步能力也并入当前空间，再单独迁移工具和定时任务。

## 迁移后的使用规则

1. 回答 Rimbo 相关问题时，先读 `contexts/rimbo/README.md`。
2. 需要历史 PRD / Lark 文档时，读 `contexts/rimbo/imported/contexts/lark_mirror/`。
3. 需要代码仓库定位时，先读 `contexts/rimbo/SOURCE_CODE_PATHS.md`，再看实际代码仓当前状态。
4. 新增 Rimbo 相关长期上下文时，写入 `contexts/rimbo/`，不要再写回原仓。
5. 原仓内容与当前项目事实冲突时，以当前实际代码、当前 Lark 远端、当前用户指令为准。

## 后续建议

- 把高频使用的 Rimbo PRD 从 Lark mirror 快照中提炼为 repo-native 文档，放在 `contexts/rimbo/products/`。
- 把信源基础设施、Lark bridge、用户模拟器等真实可用能力沉淀为当前空间的 capability 文档。
- 重新扫描 `mindspace_*` 代码仓，刷新 `contexts/rimbo/imported/contexts/repos/` 中已过期的 repo cards。

## 迁移后新增索引

- `SOURCE_CODE_PATHS.md`：补充 Rimbo 相关本机源码路径、RSS/信源管理关键文件和后续分析准则。这个文件不是从旧仓机械复制，而是迁移后为当前上下文仓新增的代码入口索引。
