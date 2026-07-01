# 2026-06-17 GitHub Public Repos Snapshot

账号：`WebXuHao`  
主页：https://github.com/WebXuHao  
公开仓库数：28  
数据来源：本机 `gh` 已登录账号，读取 GitHub 公开仓库元数据。

## 管理视图

### 当前应保留关注

| Repo | 状态 | 语言 | 最近 push | 备注 |
| --- | --- | --- | --- | --- |
| `skills` | 自有 | 未识别 | 2026-06-16 | 近期新建，适合作为公开技能集合入口。 |
| `context-infrastructure` | fork | Python | 2026-04-29 | 当前 workspace 相关，虽然是 fork，但描述已经指向个人 context/memory system。 |
| `claude-code-run` | fork | TypeScript | 2026-04-01 | 近期 fork，描述较长，可后续判断是否需要保留在 profile 可见区。 |
| `claude-code` | fork | TypeScript | 2026-03-31 | 近期 fork，和 AI agent/tooling 方向相关。 |
| `univer` | fork | TypeScript | 2026-02-13 | AI-native spreadsheet 方向，可保留或改为非重点。 |
| `documentation` | fork | TypeScript | 2026-02-11 | Univer 文档 fork，若只是临时贡献，可后续考虑归档或删除。 |
| `git-ai` | fork | Rust | 2026-02-03 | AI-generated code tracking，方向相关。 |

### 建议归档或从 profile 弱化

| Repo | 状态 | 最近 push | 原因 |
| --- | --- | --- | --- |
| `browser-tools-mcp` | fork | 2025-03-26 | MCP 工具方向相关，但一年多未更新，可保留为普通 fork。 |
| `robFood` | fork | 2022-04-02 | 疫情抢菜脚本，历史用途明确，当前不再代表方向。 |
| `dagre` | fork | 2021-08-07 | 上游描述已 deprecated。 |
| `dagre-d3` | fork | 2021-07-10 | 上游描述已 deprecated。 |
| `wxp-ui` | fork | 2020-06-15 | 早期微信小程序 UI fork，长期未更新。 |
| `vue` | fork | 2018-08-12 | 大项目 fork，长期未更新。 |
| `vue-hackernews-2.0` | fork | 2017-09-27 | 早期 Vue demo fork。 |
| `vueblog` | fork | 2017-09-24 | 早期 Vue/Node demo fork。 |
| `CMS-of-Blog` | fork | 2017-09-09 | 描述为 deprecated。 |
| `iCSS` | fork | 2017-07-28 | 早期 CSS 资料 fork。 |
| `netease_yanxuan` | fork | 2017-07-16 | 早期 Vue demo fork。 |
| `vue-nReader` | fork | 2017-07-02 | 早期 Vue demo fork。 |
| `awesome-github-vue` | fork | 2017-06-12 | 早期 Vue 资源列表 fork。 |
| `vue-zhihu-daily` | fork | 2016-05-30 | 早期 Vue demo fork。 |

### 自有老项目

| Repo | 最近 push | 星标 | 备注 |
| --- | --- | --- | --- |
| `node.js-demo` | 2019-04-28 | 1 | Vue + Node 中间层 demo。 |
| `blog` | 2018-10-10 | 0 | 旧 blog 仓库。 |
| `-` | 2017-10-10 | 0 | 仓库名不利于展示，描述是 2018 前端面试题整理。 |
| `OFO-Bicycle-sharing-wechat` | 2017-09-05 | 0 | 早期微信小程序练习。 |
| `-new-clearance-of-mines` | 2017-09-05 | 0 | 扫雷项目，仓库名不利于展示。 |
| `Vue-ZhiHuRiBao` | 2017-08-09 | 0 | 早期 Vue 项目。 |
| `Task-Manager-Vue` | 2017-06-27 | 0 | 早期 Vue 任务管理器。 |

## 初步整理建议

1. Profile 对外展示只保留 `skills`、`context-infrastructure`，再按需要从 `claude-code-run`、`git-ai`、`univer` 里选 1-2 个作为方向信号。
2. 大量 2016-2022 的 fork 建议 archive，保留历史但降低维护暗示。
3. `-` 和 `-new-clearance-of-mines` 这两个仓库名会影响可读性。若还想保留，可 rename；若只是历史练习，可 archive。
4. `skills` 建议补充 README、topics、license，并设置为 pinned repo。
5. 如果要清理公开形象，优先顺序是：archive deprecated/old forks -> rename 奇怪仓库名 -> pin 近期方向仓库 -> 统一 README/profile。

## 本次已执行

执行时间：2026-06-17  
原则：不删除仓库；只做可恢复的 archive 和公开元数据整理。

### 已 archive

共 22 个：

- `browser-tools-mcp`
- `robFood`
- `dagre`
- `dagre-d3`
- `wxp-ui`
- `vue`
- `vue-hackernews-2.0`
- `vueblog`
- `CMS-of-Blog`
- `iCSS`
- `netease_yanxuan`
- `vue-nReader`
- `awesome-github-vue`
- `vue-zhihu-daily`
- `node.js-demo`
- `blog`
- `-`
- `-new-clearance-of-mines`
- `OFO-Bicycle-sharing-wechat`
- `Vue-ZhiHuRiBao`
- `Task-Manager-Vue`
- `documentation`

### 保持活跃

- `skills`
- `context-infrastructure`
- `claude-code-run`
- `claude-code`
- `git-ai`
- `univer`

### 已补 GitHub topics

- `skills`: `agent-workflows`, `ai-agents`, `codex`, `loop-engineering`, `skills`, `goal-definition`
- `context-infrastructure`: `agent-workflows`, `ai-agents`, `context-engineering`, `memory-system`, `personal-infrastructure`
- `claude-code-run`: `ai-agents`, `claude-code`, `developer-tools`, `typescript`
- `claude-code`: `ai-agents`, `claude-code`, `developer-tools`
- `git-ai`: `ai-generated-code`, `developer-tools`, `git-extension`, `rust`
- `univer`: `ai-native`, `developer-tools`, `spreadsheet`, `typescript`

### 其他设置

- `skills` 已关闭 wiki。
- `skills` 已关闭 projects。
- `skills` 的 `README.md` 已存在，远端文件大小约 3.4KB，本轮未改内容。

### 未执行

- 未删除任何仓库。
- 未修改 profile pinned repositories。GitHub pinned repo 通常需要通过网页或 GraphQL mutation 操作，后续可单独处理。
- 未重命名 `-` 和 `-new-clearance-of-mines`，因为它们已 archive，rename 的收益降低。
