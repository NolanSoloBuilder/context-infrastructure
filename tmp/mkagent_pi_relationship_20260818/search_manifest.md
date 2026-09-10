# Search Manifest

日期：2026-08-18

## 产出文件索引

| 文件 | 路径 | 说明 |
|---|---|---|
| Scratchpad | `tmp/mkagent_pi_relationship_20260818/scratchpad.md` | Claim、消歧、关键事实与来源 |
| Search Manifest | `tmp/mkagent_pi_relationship_20260818/search_manifest.md` | 本文件 |
| 最终报告 | `contexts/survey_sessions/2026_08_18_mkagent_pi_agent_relationship.md` | 面向用户的结论与判断 |

## 覆盖范围

- MkAgent 官网、README、架构、连接、权限、浏览器、上游同步与 Craft 对比文档
- MkAgent GitHub API：仓库元数据、贡献者、提交、release 资产
- MkAgent 源码：Pi package import、`createAgentSession`、built-in tool、权限 hook
- Pi 官方仓库与 npm package metadata
- Craft Agents OSS 官方 README 与 MkAgent NOTICE
- 通用 Web 搜索：同名 PAgent 消歧、独立评论与迁移案例

## 证据缺口

- 没有发现独立第三方的 MkAgent 深度评测、生产使用报告或迁入/迁出记录。
- MkAgent 自带的 Craft 复用比例和 installer 对比数字来自项目自己的审计文档；本轮只验证了来源关系、依赖与主要代码边界，没有重新跑两个仓库的完整审计。
- 本轮没有安装并运行 MkAgent，所以“可下载”和“源码存在”不等于已完成本机真实 smoke。

## Subagent 原始产出

| Agent | 任务 | 状态 |
|---|---|---|
| `pi_relationship` | Pi 与 MkAgent 技术边界复核 | completed |
| `craft_lineage` | Craft Agents 来源关系复核 | completed |
| `market_signal` | 外部信号、成熟度与 PAgent 消歧 | completed |
