# 第二层：Codex Skills 迁移决策与 Prompt

状态：草案。本文只处理 Codex Skills，不处理插件、MCP、memory、automation、Codex 登录态或其他配置。

## 当前盘点

机器可读的完整迁移名单见 `manifests/codex-skills-migrate.txt`。

| 来源 | 当前数量 | 迁移决策 | 说明 |
|---|---:|---|---|
| `~/.codex/skills/.system` | 5 | 不迁移 | `imagegen`、`openai-docs`、`plugin-creator`、`skill-creator`、`skill-installer` 由 Codex 自带 |
| `~/.codex/skills/<name>/SKILL.md` | 49 | 迁移 37 个 | 内容级迁移自定义 Skill；排除系统、官方插件重复项、运行时目录和手动排除项 |
| `~/.agents/skills/<name>/SKILL.md` | 39 | 迁移 9 个 | 排除全部 Lark Skill 和官方插件重复项 |
| `~/.codex/skills` 软链接 | 2 | 重建 1 个 | 只重建 `find-skills`；`remotion-best-practices` 由官方 Remotion 插件提供 |
| `~/.agents/skills/superpowers` | 1 个软链接 | 条件重建 | 目标由 Superpowers 提供；本层不复制目标内容 |
| Codex 插件缓存中的 Skills | 动态 | 不迁移 | 由插件重新生成，不能复制 `~/.codex/plugins/cache` |
| `codex-primary-runtime`、`.DS_Store` | 2 类 | 不迁移 | 空目录或系统垃圾文件 |

建议排除的顶层重名或官方插件重复 Skill：

- `openai-docs`：Codex `.system` 已提供。
- `gh-fix-ci`：GitHub 插件已提供。
- `pdf`：PDF 插件/Primary Runtime 已提供。
- `sentry`：Sentry 插件已提供。
- `agents-sdk`：OpenAI Developers / Cloudflare 插件已提供。
- `cloudflare`、`cloudflare-deploy`、`durable-objects`、`sandbox-sdk`、`web-perf`、`workers-best-practices`、`wrangler`：Cloudflare 插件已提供同类能力。
- `figma`、`figma-code-connect-components`、`figma-create-design-system-rules`、`figma-implement-design`：Figma 插件已提供同类能力。
- `remotion-best-practices`：Remotion 插件已提供。

Lark 相关 Skill 全部不迁移。新机如果后续还需要飞书能力，应单独走 Lark 插件或重新安装策略，而不是从旧机复制。

手动排除 3 个 handoff / plugin installer Skill：`codewiz-handoff`、`codewiz-handoff-plugin-installer`、`claude-code-handoff-plugin-installer`。

迁移后应使用新 Codex 自带或插件提供的版本，避免旧的顶层副本遮蔽更新版本。

## 核心判断

当前绝大多数 Skill 目录不是独立 Git checkout，没有可用 remote。`skill-installer` 可以从已知 curated 名称或明确 GitHub repo/path 安装，但不能仅凭本机目录名还原这些 Skill。因此本次采用：

1. 系统 Skill：不打包，新 Codex 自带。
2. 插件 Skill：不打包，由插件层恢复。
3. 自定义 Codex Skill：迁移实际内容。
4. 共享 Agent Skill：迁移实际内容。
5. 软链接：不依赖旧用户名，恢复时用相对路径重建。

## Prompt A：在旧电脑导出 Skill 专用迁移包

```text
请在这台旧 Mac 上只导出 Codex Skills，生成一个独立迁移包。直接执行、验证并输出报告，不要迁移 Codex 的其他数据。

严格边界：
1. 只读取 ~/.codex/skills 和 ~/.agents/skills。
2. 不读取或打包 Codex auth、config.toml、memory、sessions、history、automation、MCP、plugins/cache、App 数据、SSH、npmrc 或任何 secret。
3. 不修改现有 Skill，不执行安装或更新，不删除任何文件。
4. 不跟随软链接复制目标；软链接关系单独写入 manifest。

导出规则：
- 从 ~/.codex/skills 导出所有顶层、包含 SKILL.md 的真实目录，但排除：
  .system
  codex-primary-runtime
  claude-code-handoff-plugin-installer
  cloudflare-deploy
  codewiz-handoff
  codewiz-handoff-plugin-installer
  figma
  figma-code-connect-components
  figma-create-design-system-rules
  figma-implement-design
  openai-docs
  gh-fix-ci
  pdf
  sentry
  .DS_Store
- 从 ~/.agents/skills 导出所有顶层、包含 SKILL.md 的真实目录，但排除：
  agents-sdk
  cloudflare
  durable-objects
  lark-*
  remotion-best-practices
  sandbox-sdk
  web-perf
  workers-best-practices
  wrangler
- 不导出 ~/.agents/skills/superpowers 软链接。
- 不导出 ~/.codex/skills/find-skills 软链接本身，改为写入 symlinks.tsv。
- 不导出 ~/.codex/skills/remotion-best-practices 软链接；该能力由官方 Remotion 插件提供。

预期软链接 manifest：
.codex/skills/find-skills<TAB>../../.agents/skills/find-skills
.agents/skills/superpowers<TAB>../../.codex/superpowers/skills<TAB>optional

执行要求：
1. 创建临时 staging，不在源目录内生成文件。
2. 每个待导出目录必须存在顶层 SKILL.md，否则跳过并记为 invalid。
3. 保留目录权限、脚本和 assets，但排除 .DS_Store、__pycache__、node_modules、.git、日志和临时文件。
4. 做高置信 secret 风险扫描，只报告文件路径和规则名，不输出匹配内容。若发现私钥、真实 token、.env 或凭据文件，停止打包并报告。
5. 生成 skills-manifest.tsv，至少包含 source_root、skill_name、file_count、byte_size 和内容 SHA-256。
6. 生成 symlinks.tsv 和 README.md，写明恢复边界。
7. 将 payload 打包到：
   ~/Documents/CodexMigration/codex-skills-<timestamp>.tar.gz
8. 同目录生成整个归档的 SHA-256 文件，归档及校验文件权限设为 600。
9. 校验归档路径安全，确认没有上述排除目录和 Codex 非 Skill 数据。
10. 将执行报告写到：
    ~/Documents/CodexMigration/codex-skills-export-report.md

最终回复必须给出：
- 导出的 Codex Skill 数、Agent Skill 数和软链接数。按当前决策应为 Codex 37、Agent 9、软链接 1。
- 排除、invalid 和 secret-risk 项。
- 归档、SHA-256 和报告的绝对路径。
- 明确确认没有迁移系统 Skill、插件缓存或 Codex 非 Skill 数据。
```

## Prompt B：在新电脑恢复 Skill 专用迁移包

```text
请在这台新 Mac 上只恢复 Codex Skills。直接执行、验证并输出报告，不要恢复 Codex 的其他配置。

输入归档：
~/Documents/CodexMigration/codex-skills-<timestamp>.tar.gz

严格边界：
1. 只允许写入 ~/.codex/skills 和 ~/.agents/skills。
2. 不修改 ~/.codex/skills/.system，不修改 config.toml、auth、memory、sessions、automation、MCP 或插件缓存。
3. 不从网络安装系统或插件 Skill；本步骤只恢复迁移包中的自定义/共享 Skill。
4. 不删除归档中没有出现的新机器 Skill。

恢复要求：
1. 先验证旁边的 SHA-256 文件。
2. 列出 tar 路径并拒绝绝对路径、.. 路径穿越和逃逸软链接；先解压到临时目录。
3. 校验 README、skills-manifest.tsv、symlinks.tsv 和每个 Skill 的顶层 SKILL.md。
4. 确认归档不包含 .system、plugins/cache、auth、config、memory、sessions 或其他越界内容；发现即停止。
5. 将新机器已有的同名目标先备份到：
   ~/Documents/CodexMigration/pre-codex-skills-restore-<timestamp>/
6. 内容哈希相同的 Skill 跳过；哈希不同的同名 Skill 在完成备份后，用归档版本替换。不得影响其他 Skill。
7. 恢复真实目录后，用相对路径重建：
   ~/.codex/skills/find-skills -> ../../.agents/skills/find-skills
8. 不创建 ~/.codex/skills/remotion-best-practices；该能力由官方 Remotion 插件提供。
9. 只有当 ~/.codex/superpowers/skills 已存在时，才创建：
   ~/.agents/skills/superpowers -> ../../.codex/superpowers/skills
   如果目标不存在，只记为 optional pending，不安装 Superpowers。
10. 不创建 openai-docs、gh-fix-ci、pdf、sentry、agents-sdk、cloudflare、cloudflare-deploy、durable-objects、figma*、remotion-best-practices、sandbox-sdk、web-perf、workers-best-practices、wrangler、codewiz-handoff、codewiz-handoff-plugin-installer、claude-code-handoff-plugin-installer 或 lark-* 的顶层迁移副本；验证它们没有被归档恢复。
11. 对恢复后的每个 Skill 重新计算哈希并与 manifest 比较，检查所有脚本仍保留可执行权限。
12. 运行只读发现检查，确认 Codex Skill 根目录和 Agent Skill 根目录可访问。说明新安装的 Skill 从下一次 Codex turn 开始可用。
13. 将报告写到：
    ~/Documents/CodexMigration/codex-skills-restore-report.md

最终回复必须给出：
- restored、identical skipped、replaced、invalid、optional pending 的数量和名称。
- 备份目录和报告绝对路径。
- 软链接验证结果。
- 明确确认没有覆盖系统 Skill，没有复制插件缓存，没有修改 Codex 非 Skill 配置。
```

## 待确认

当前策略已确认：不迁移 Lark Skill；不迁移系统 Skill、运行时目录、插件缓存、已有官方插件替代的本地副本，以及 3 个 handoff / plugin installer Skill。后续如需恢复某个被排除的本地 Skill，应单独从排除名单中挑回，而不是整体镜像旧机器。
