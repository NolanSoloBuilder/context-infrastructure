# 外部 Skills 注册表

> 本文件由 `tools/external_skills_registry.mjs sync` 生成。GitHub 安装来源维护在 `external_skills_registry.json` 与 `skills-lock.json`；从用户全局目录精选到项目的快照维护在 `global_skill_snapshots.json`。

当前项目登记 **33 个上游安装 Skill、0 个精选全局快照，共 33 个项目级 Skill**。最近对账日期：`2026-09-23`。

## 上游来源

| 来源 | Skill 数 | 版本 | 许可证 | 记录 revision | 最近更新 | 安全记录 |
| --- | ---: | --- | --- | --- | --- | --- |
| [dontbesilent2025/dbskill](https://github.com/dontbesilent2025/dbskill) | 29 | 2.18.1 | CC BY-NC 4.0 | `bd6f4651d98c` | 2026-07-21 | Mixed：27 个 Low Risk，2 个 High Risk |
| [4682B4LEE/xiaohongshu-content-checker](https://github.com/4682B4LEE/xiaohongshu-content-checker) | 1 | 1.3.3 | MIT（仅 SKILL.md 声明） | `60dbf1a28910` | 2026-07-21 | 未提供自动扫描结果；安装内容仅含 Markdown |
| [helloianneo/ian-xiaohei-illustrations](https://github.com/helloianneo/ian-xiaohei-illustrations) | 1 | — | MIT | `91b560849e8f` | 2026-07-21 | Safe；0 alerts；Low Risk |
| [helloianneo/ian-xiaohei-scenes](https://github.com/helloianneo/ian-xiaohei-scenes) | 1 | — | MIT | `3555bcb9ecab` | 2026-07-21 | Safe；0 alerts；Low Risk |
| [typesafe-ai/skills](https://github.com/typesafe-ai/skills) | 1 | — | MIT | `65a39f393687` | 2026-09-23 | Safe；0 Socket alerts；Snyk Low Risk |

## 精选全局 Skill 快照

当前未复制全局 Skill 到项目；克隆本仓库后，按需在全局环境安装这些能力。


明确排除：

- 任何小红书公司或内部业务 Skill
- Mindspace、Expo/RN release、Fedith、Hi 等公司专用 Skill
- code-search、Remotion、Lottie、text-to-lottie 等纯代码或代码生成 Skill
- Cursor-only Skill
- Codex .system Skill 与插件缓存 Skill

## 已安装 Skill

### dontbesilent2025/dbskill

- 仓库：https://github.com/dontbesilent2025/dbskill
- 安装日期：`2026-07-21`；最近更新：`2026-07-21`
- 许可证证据：仓库 LICENSE；商业用途需要单独授权
- Skills（29）：`dbs`、`dbs-action`、`dbs-agent-migration`、`dbs-ai-check`、`dbs-benchmark`、`dbs-bridge`、`dbs-chatroom`、`dbs-chatroom-austrian`、`dbs-content`、`dbs-content-system`、`dbs-decision`、`dbs-deconstruct`、`dbs-diagnosis`、`dbs-goal`、`dbs-good-question`、`dbs-hook`、`dbs-knowledge`、`dbs-learning`、`dbs-report`、`dbs-resonate`、`dbs-restore`、`dbs-save`、`dbs-script-flow`、`dbs-skill-cleaner`、`dbs-slowisfast`、`dbs-spread`、`dbs-update`、`dbs-wechat-html`、`dbs-xhs-title`
- 备注：dbs-report 与 dbs-restore 在安装扫描中被标为 High Risk，使用前审查文件访问行为。
- 备注：dbs-update 在安装扫描中出现 1 个 Socket alert，综合结果仍为 Low Risk。

### 4682B4LEE/xiaohongshu-content-checker

- 仓库：https://github.com/4682B4LEE/xiaohongshu-content-checker
- 安装日期：`2026-07-21`；最近更新：`2026-07-21`
- 许可证证据：仓库根目录没有独立 LICENSE 文件
- Skills（1）：`xiaohongshu-content-checker`
- 备注：平台规则会变化，检测结论仅作发布前风险参考。

### helloianneo/ian-xiaohei-illustrations

- 仓库：https://github.com/helloianneo/ian-xiaohei-illustrations
- 安装日期：`2026-07-21`；最近更新：`2026-07-21`
- 许可证证据：仓库 LICENSE
- Skills（1）：`ian-xiaohei-illustrations`
- 备注：小黑 1.0，适合观点、流程和方法的 16:9 白底手绘解释图。

### helloianneo/ian-xiaohei-scenes

- 仓库：https://github.com/helloianneo/ian-xiaohei-scenes
- 安装日期：`2026-07-21`；最近更新：`2026-07-21`
- 许可证证据：仓库 LICENSE
- Skills（1）：`ian-xiaohei-scenes`
- 备注：小黑 2.0，适合真实物件场景、项目故事和超横版长卷图。

### typesafe-ai/skills

- 仓库：https://github.com/typesafe-ai/skills
- 安装日期：`2026-09-23`；最近更新：`2026-09-23`
- 许可证证据：Skill 目录 LICENSE；GitHub 仓库许可证元数据为 MIT
- Skills（1）：`typesafe-ai`
- 备注：TypeSafe 官方使用说明 Skill；编写接口调用前要求读取当前官方 API 或 SDK 文档。
- 备注：与 Jev in Codex 的批量分类工具项目分别维护。

## 对账与更新

只读检查本地注册表、安装目录、锁文件和生成索引是否一致：

```bash
node tools/external_skills_registry.mjs verify
```

只读比较 GitHub 当前 revision，发现哪些上游有更新：

```bash
node tools/external_skills_registry.mjs check-updates
```

确认需要升级后，显式更新当前项目：

```bash
npx -y skills update --project -y
```

更新完成后，审查文件变化与安全提示，再修改 `external_skills_registry.json` 中对应来源的 `recordedRevision`、`version`、`lastUpdatedAt` 和风险备注，最后执行：

```bash
node tools/external_skills_registry.mjs sync
node tools/external_skills_registry.mjs verify
```

> 当前 CLI 没有只读的 `skills check`。不要把 `npx skills check` 当作 dry-run；2026-07-21 的实测会直接刷新全部项目 Skill。

精选全局快照只在需要吸收本机新版时执行增量同步：

```bash
node tools/vendor_global_codex_skills.mjs sync
node tools/external_skills_registry.mjs sync
node tools/external_skills_registry.mjs verify
```

新电脑克隆仓库后，Skill 文件已经位于项目目录；如清单中存在 npm 依赖，再执行 `node tools/bootstrap_project_skills.mjs`。该命令不会安装全局 Skill。

## 新增外部 Skill 的登记要求

1. 使用项目级安装，不带 `-g`，并确认 `skills-lock.json` 写入来源、路径和哈希。
2. 在 `external_skills_registry.json` 登记上游仓库、默认分支、revision、版本、许可证证据、安装日期和安全备注。
3. 执行 `sync` 生成本索引，再执行 `verify`，确保每个外部 Skill 都能追溯到上游来源。
4. 许可证缺失、自动扫描高风险或包含可执行脚本时，必须在登记记录中明确写出，不能只保留安装成功状态。
