# 2026-10-09 全局 Skill 作用域整理

已将 46 个公司内部 Skill 限定到 9 个活跃公司 Git 根，将 2 个 Mindspace 发布 Skill 限定到该业务的 4 个 Git 根。共迁移 48 个 Skill 目录、移走 55 个全局入口；其中 DMS 含 4 个子 Skill，实际覆盖 52 个不同 Skill 名称。

原生 Codex app-server 的实际用户级启用项从 98 个降至 48 个。关闭状态的 `xhs-cover`、`hatch-pet` 保持原状态；插件及系统能力保持原安装。

## 迁移清单

| 类别 | Skill 目录 | 允许范围 |
| --- | --- | --- |
| 公司协作与研发通用 | `code-search`、`codewiz-handoff`、`codewiz-handoff-plugin-installer`、`cowork-publish`、`cowork-xhs-sso`、`hi-docs`、`hi-im`、`hi-meeting`、`redoc-writer`、`yunxiao-assistant`、`pingcode-assistant-pro`、`verify-extraction`、`verify-execution`、`verify-reporting`、`skillhub-upload`、`xhs-skill-publisher`、`usage` | aurora、armor、merchant-trade、mono-live、vibe-rn、vibe-marketing-rn、wakanda-rn-monorepo、fulishe-services/couponbizcenter、fulishe-idls/couponbizcenter |
| 公司数据与平台查询 | `apollo-skill`、`dms-assistant`、`eventmq-tools`、`ones-assistant`、`redschedule-skill`、`registry`、`rpcdebugger-skill`、`service-governance-skill`、`table-discovery`、`sql-development` | aurora、armor、merchant-trade、mono-live、vibe-rn、vibe-marketing-rn、wakanda-rn-monorepo、fulishe-services/couponbizcenter、fulishe-idls/couponbizcenter |
| 公司前端与埋点 | `fe-skill`、`edith-tools`、`fedith-skill`、`xhs-file-tools`、`xhs-image-upload`、`xhs-everything-upload`、`xhs-short-url`、`xhs-note-crawler`、`xhs-content-inspiration`、`uba-assistant`、`uba-create-requirement`、`event-point-discovery`、`event-behavior-analysis`、`user-behavior-trace`、`tracker-helper` | aurora、armor、merchant-trade、mono-live、vibe-rn、vibe-marketing-rn、wakanda-rn-monorepo |
| Java 服务接入 | `infra-midware-component-skill` | fulishe-services/couponbizcenter |
| IDL 与网关生成 | `midware-metarepo`、`idl2edith` | fulishe-services/couponbizcenter、fulishe-idls/couponbizcenter |
| 小红书 C 端 Android 操作 | `xhs-android-run` | armor、vibe-rn、vibe-marketing-rn、wakanda-rn-monorepo |
| Mindspace 多仓发布 | `mindspace-tri-repo-release` | mindspace_web_frontend、mindspace_backend、mindspace_ml_backend、mindspace_app |
| Mindspace App OTA | `expo-rnota-release` | mindspace_app |

`hi-docs` 实际名称为 `redoc`，`uba-create-requirement` 实际名称为 `meta-lightweight-requirement`。Hi canonical 使用 `.agents` 中的新 XML 流程；旧 `.codex` Markdown 版本完整保留。XHS File Tools canonical 使用较新的 Codex SSO 处理版本。

## 保留全局

全局保留跨项目开发、设计、文档、媒体、运维和公开内容创作。`yunxiao-smartcr` 当前实现为本地只读审查，未因其名称而迁移；`devspace-mcp-setup`、`huimin-xhs-content-creator`、AIsa 检索、Cloudflare 和 Remotion 等继续全局。

本轮 CLI 实际启用的用户级 Skill 名称：

`agents-sdk`, `claude-code-handoff-plugin-installer`, `cloudflare`, `cloudflare-email-service`, `cloudflare-one`, `cloudflare-one-migrations`, `devspace-mcp-setup`, `diagram-design:diagram-design`, `documents:documents`, `durable-objects`, `find-skills`, `huimin-xhs-content-creator`, `khazix-writer`, `llm-router`, `local-image-compressor`, `lottie2code`, `multi-source-search`, `neat-freak`, `onchainos-skills:okx-agent-payments-protocol`, `onchainos-skills:okx-agentic-wallet`, `onchainos-skills:okx-ai`, `onchainos-skills:okx-dapp-discovery`, `onchainos-skills:okx-defi`, `onchainos-skills:okx-dex-market`, `onchainos-skills:okx-growth-competition`, `onchainos-skills:okx-guide`, `pdf:pdf`, `playwright`, `presentations:Presentations`, `remotion-best-practices`, `sandbox-sdk`, `screenshot`, `sora`, `spreadsheets:Spreadsheets`, `spreadsheets:excel-live-control`, `storage-analyzer`, `strongvpn-node-optimizer`, `template-creator:template-creator`, `text-to-lottie`, `tinify-image-compressor`, `turnstile-spin`, `ui-ux-pro-max`, `visualize:visualize`, `web-perf`, `website-to-design-md`, `workers-best-practices`, `wrangler`, `yunxiao-smartcr`

这是当前 CLI 的 `skills/list` 读回；桌面远程插件与当前会话已注入的技能说明不以这个数字代替全部插件安装目录数量。

## 实现与验证

- 完整原目录移动到本机备份，canonical 来源保存于非扫描目录；项目用 `.agents/skills` 链接加载，并建立 Claude 项目链接。
- 新建 721 个本机链接；保留 3 个已有同名项目入口，未覆盖实体版本。链接逐条加入本机 Git `info/exclude`，迁移后 13 个目标仓库的原工作区状态保持一致。
- 48 个 canonical 原副本已逐文件校验 SHA-256。不同版本的全局副本也完整保留。CLI 安装和认证缓存未迁入项目。
- 修正 CodeWiz、Cowork、上传、爬虫、Skill 发布样例的路径；Verify 缺少 REDoc 时改为报告项目依赖，避免安装回全局。
- 原生 `skills/list` 强制重扫通过 16 个目录：9 个公司项目、4 个 Mindspace 项目，以及 context-infrastructure、BeamJoin、context-vault 三个私人负向目录。目标能力均返回 `scope=repo`、启用状态；用户级和非目标项目泄漏为 0。
- 增加允许范围之外的 repo 能力检查：REDAndroid 仅匹配 4 个 C 端 RN 仓，Java 代码接入仅匹配服务仓，App OTA 仅匹配 Mindspace App。
- `external_skills_registry verify`、`vendor_global_codex_skills verify`、脚本编译和相关文档 diff 检查通过。本轮未向当前项目安装新的上游或全局快照。

公司 Git 根位于 `/Users/xuhao/Documents/Basic/`，但该目录混有私人 `context-vault`，因此未创建父目录共享入口。`aurora-fansopen-preserved` 为保存副本，未添加链接。自动 worktree 尚需在使用时单独登记。

Claude 链接和文件已检查；未运行 Claude 模型会话，本轮运行时验收限于原生 Codex。

## 原有边界

- 用户追加指定 `peskill` 仅在公司项目生效，规则已记录。截至本次核验，常见全局 Skill 目录、公司项目技能目录、Codex 已安装插件及缓存、Claude/OpenCode/CodeWiz 安装入口均未找到 `peskill`、`pe-skill` 或 `pe_skill`。尚未迁移该项，需准确名称或来源定位后完成。

- `armor/.agents/skills/rn-dev/SKILL.md` 原有文件缺少 YAML frontmatter，Codex 报加载错误；本轮未改此文件，迁移能力均通过。
- 部分原有 Skill 引用 `note-query`、`midware-qa-skill`、`xhs-android-compile`，当前未找到这些依赖。本轮不将已有依赖缺失宣称为业务能力验证通过。

## 本机证据与复查

- [范围清单](/Users/xuhao/.local/share/agent-skill-scopes/manifest.json)
- [原生加载结果](/Users/xuhao/.local/share/agent-skill-scopes/runtime-after.json)
- [完整备份](/Users/xuhao/.local/share/agent-skill-scopes/backups/20261009T113346Z)
- [治理规则与恢复方法](/Users/xuhao/Documents/Other/context-infrastructure/rules/skills/skill_scope_management.md)
- [只读验证脚本](/Users/xuhao/Documents/Other/context-infrastructure/tools/audit_skill_scopes.py)

```bash
python3 /Users/xuhao/Documents/Other/context-infrastructure/tools/audit_skill_scopes.py \
  --manifest /Users/xuhao/.local/share/agent-skill-scopes/manifest.json \
  --output /Users/xuhao/.local/share/agent-skill-scopes/runtime-after.json
```

发现范围依据 [Codex 官方 Skill 加载规则](https://developers.openai.com/codex/skills/)，完成态以本机实际 `skills/list` 返回为准。
