# 第三层：从当前 Repo 恢复 Codex 环境

把下面这段 prompt 发给新电脑上的 Codex。它假设新电脑已经 clone 了当前 repo，并且当前工作目录位于：

`/Users/xuhao/Documents/Other/context-infrastructure`

```text
请从当前 repo 中的迁移包恢复 Codex 环境。直接执行、验证并输出报告。

迁移包位置：
adhoc_jobs/mac_migration_kit/artifacts/codex-environment-20260710T151838.tar.gz

校验文件：
adhoc_jobs/mac_migration_kit/artifacts/codex-environment-20260710T151838.tar.gz.sha256

恢复脚本：
adhoc_jobs/mac_migration_kit/scripts/restore_codex_environment.sh

严格边界：
1. 这是 Codex 环境恢复，不恢复 OpenCode。
2. 先只做 dry-run，不要直接覆盖任何文件。
3. 不恢复登录态，不复制 auth、session、history、plugin cache、attachments、node_modules、Lark Skills、官方插件重复 Skills 或手动排除的 handoff/plugin-installer Skills。
4. 不修改 Git 仓库中的迁移包和 manifest。
5. 如果归档内出现 .config/opencode、auth.json、.cockpit_codex_auth.json、sessions、archived_sessions、plugins/cache、attachments、node_modules、lark-*、remotion-best-practices、figma*、cloudflare-deploy、gh-fix-ci、pdf、sentry、wrangler、workers-best-practices、web-perf、sandbox-sdk、durable-objects、agents-sdk、codewiz-handoff* 或 claude-code-handoff-plugin-installer，停止恢复并报告。

执行步骤：
1. 确认当前目录是 context-infrastructure repo。
2. 执行 SHA-256 校验：
   cd adhoc_jobs/mac_migration_kit/artifacts
   shasum -a 256 -c codex-environment-20260710T151838.tar.gz.sha256
3. 列出归档内容并检查路径安全：
   - 拒绝绝对路径。
   - 拒绝 `..` 路径穿越。
   - 拒绝越界软链接。
4. 检查归档必须包含：
   - BACKUP_METADATA.txt
   - README.txt
   - SKILL_COUNTS.txt
   - MANIFESTS/codex-skills-migrate.txt
   - home/.codex/config.toml
   - home/.codex/AGENTS.md
   - home/.codex/rules/
   - home/.codex/memories/
   - home/.codex/memories_1.sqlite
   - home/.codex/sqlite/memories_1.sqlite
   - home/.codex/automations/
   - home/.codex/skills/code-search/SKILL.md
   - home/.agents/skills/find-skills/SKILL.md
5. 读取 SKILL_COUNTS.txt，确认应为：
   - codex_skills=37
   - agent_skills=9
   - skill_symlinks=1
6. 先执行 dry-run：
   cd ..
   ./scripts/restore_codex_environment.sh artifacts/codex-environment-20260710T151838.tar.gz
7. dry-run 输出正常后，提醒我先完全退出 Codex App 和 Codex CLI。
8. 等我确认退出后，再执行实际恢复：
   DRY_RUN=0 ./scripts/restore_codex_environment.sh artifacts/codex-environment-20260710T151838.tar.gz
9. 恢复后重新校验：
   - ~/.codex/config.toml 存在。
   - ~/.codex/AGENTS.md 存在。
   - ~/.codex/rules 存在。
   - ~/.codex/memories 存在。
   - ~/.codex/automations 存在。
   - ~/.codex/skills 中有 37 个迁移 skill。
   - ~/.agents/skills 中有 9 个迁移 skill。
   - ~/.codex/skills/find-skills 是 symlink。
   - ~/.config/opencode 没有被本流程写入。
10. 最终报告必须包含：
   - 校验结果。
   - dry-run 摘要。
   - 实际恢复时的备份目录。
   - 恢复的 skill 数量。
   - 被明确排除的类别。
   - 下一步需要手动重新登录的账号和插件同步事项。
```

## 当前包说明

| 项目 | 值 |
|---|---:|
| Codex Skills | 37 |
| Agent Skills | 9 |
| Symlink | 1 |
| OpenCode | 不迁移 |
| Codex auth/session/history/plugin cache | 不迁移 |
| Lark Skills | 不迁移 |
| 官方插件重复 Skills | 不迁移 |
| 手动排除 handoff/plugin-installer Skills | 不迁移 |
