# Skill 作用域治理

## 适用范围

盘点、安装、迁移或更新本机 Skills 时使用。先依据实际 `SKILL.md`、脚本依赖和目标项目分类，再调整发现入口。

| 类型 | 生效范围 | 判断依据 |
| --- | --- | --- |
| 通用能力 | 用户级全局 | 可跨项目复用，不绑定内部平台或某个仓库 |
| 公司内部能力 | 对应公司 Git 仓库 | 依赖公司认证、内网、平台 API、业务协议或内部发布链路 |
| 特定业务项目能力 | 对应业务 Git 仓库 | 绑定固定仓库、运行脚本、发布合同或部署目标 |

公开平台的内容创作能力不因名称含“小红书”自动归为公司内部。Cloudflare、浏览器、设计、文档和媒体等通用能力可保留全局；Mindspace 发布能力属于该业务项目。

用户明确指定 `peskill` 仅在公司项目生效。定位其真实安装入口后按公司项目登记，禁止全局安装或向私人项目挂载；尚未找到入口时不得声称已完成迁移。

Codex 从当前目录到 Git 根目录读取 `.agents/skills`，支持技能目录软链接。公司仓库与私人仓库混放时，应在各 Git 根登记，避免安装到共享父目录。[官方加载规则](https://developers.openai.com/codex/skills/)

## 本机来源与项目入口

- 来源目录：`~/.local/share/agent-skill-scopes/skills/`。该目录不属于用户级 Skill 扫描入口。
- 本机清单：`~/.local/share/agent-skill-scopes/manifest.json`。包含 canonical 来源、实际 Skill 名称、旧全局路径、允许项目、操作记录、哈希和备份位置。
- Codex 项目入口：`<repo>/.agents/skills/<name>`。
- Claude Code 项目入口：`<repo>/.claude/skills/<name>`。本轮检查了链接与文件，未运行 Claude 模型会话。
- 本轮完整原始副本保存在清单的 `backupPath`；不同内容的旧副本也完整保留。

链接及公司 Skill 内容只在本机保存。每个目标仓库用本机 Git `info/exclude` 忽略新增链接，避免提交私人路径、公司能力或认证文件。已有项目实体 Skill 保留，不用中央版本覆盖。

Skill 发现、全局 Node CLI 安装和认证缓存分别管理。迁移发现入口不改动 CLI、SSO 缓存、凭据及现有插件。公司专用插件会建立用户级入口，仅在用户明确要求全局安装该插件时执行。

## 修改顺序

1. 从各全局入口盘点，依据正文与可执行文件确认内部依赖；同名副本逐文件比较，保留差异。
2. 核验真实目标 Git 根及其规则；保持前端、服务、IDL、客户端和私人业务项目的范围。
3. 完整备份并记录哈希，将 canonical 内容放入本机来源库。执行样例从当前 `SKILL.md` 所在目录定位；依赖 Skill 按可用列表解析，避免使用旧全局路径。
4. 建立项目链接并检查文件可读，随后将旧全局入口移入备份区，不删除原始内容。
5. 用原生 `skills/list` 强制重扫：目标项目应返回 `scope=repo` 且启用；其余项目不应加载该 Skill，用户级入口不得残留。

新增或更新公司 Skill 时沿用以上项目范围，不向用户级 `~/.codex/skills`、`~/.agents/skills`、`~/.claude/skills` 回装。本机中央库的安装来源和授权说明保持可追溯；若从上游新装到本仓，仍须遵守现有外部注册表流程。

## 复查

```bash
python3 /Users/xuhao/Documents/Other/context-infrastructure/tools/audit_skill_scopes.py \
  --manifest /Users/xuhao/.local/share/agent-skill-scopes/manifest.json \
  --output /Users/xuhao/.local/share/agent-skill-scopes/runtime-after.json
```

该命令只读调用 Codex app-server 的 `skills/list`，不启动模型或公司业务接口。退出码 `0` 为范围检查通过，`1` 为失败。它检查全局残留、用户级泄漏、允许项目缺失、其他项目错误加载、迁移相关加载错误，并记录已有无关加载错误。

新增公司仓库时，按清单中适用领域建立本机链接，补充 `targets` 后复查。Git worktree 也有独立项目入口；本轮未向自动生成的 worktree 批量铺设链接，使用时应单独登记。

## 恢复

恢复以 manifest 的 `operations` 为准：先确认当前链接仍指向记录的 canonical 目录、原全局目标没有新内容，再逐个移除本轮新增链接，将 `move` 记录的备份目录放回 `source`。有冲突时保留双方并人工核对。`excludeBackups` 记录了本轮修改前的忽略文件，恢复时保留后续新增规则。

不要删除中央库或备份来完成恢复，也不要覆盖已有项目 Skill。恢复后再次调用 `skills/list` 核验实际范围。
