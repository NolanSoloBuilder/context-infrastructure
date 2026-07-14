# Codex 本地缓存与历史文件占用分析

扫描时间：2026-07-13（Asia/Shanghai）

扫描方式：对 `~/.codex`、`~/Library/Application Support/Codex` 和 `~/Library/Caches/Codex` 执行只读 `du`、`find`、`stat` 与 JSONL 类型统计，并用 `df` 核对磁盘基线。通用全盘扫描脚本运行 10 分钟后达到执行时限，因此本文只对用户要求的 Codex 范围给出结论，不把未完成的整机扫描结果混入统计。

## 结论

本机 Codex 相关目录合计约 **6.3 GB**：`~/.codex` 约 3.4 GB，`~/Library/Application Support/Codex` 约 1.3 GB，`~/Library/Caches/Codex` 约 1.6 GB。

其中约 **3.0 GB** 属于浏览器缓存、代码缓存、临时插件同步目录和目录索引缓存。完全退出 Codex/ChatGPT 后清理这些路径，应用会在后续启动和使用过程中重建。当前磁盘还有约 96 GiB 可用空间，因此这次优化的主要价值是控制 Codex 的持续增长，并非应急释放空间。

剩余空间里，`~/.codex/sessions` 和 `~/.codex/archived_sessions` 合计约 **2.5 GB**。它们保存任务历史、工具调用和上下文，不属于普通缓存。一个 2026-06-08 开始的会话文件达到约 **740 MiB**，包含约 4.8 万条 JSONL 记录，是当前最明显的异常增长点。会话治理应采用“先摘要或归档，再按保留期处理”的方式。

## 占用构成

| 路径 | 占用 | 属性 | 判断 |
|---|---:|---|---|
| `~/.codex/sessions` | 约 2.4 GB | 会话历史 | 需人工判断，不能按缓存直接删除 |
| `~/Library/Caches/Codex` | 约 1.6 GB | Chromium 网络与代码缓存 | 可重建，退出应用后优先清理 |
| `~/Library/Application Support/Codex/Partitions/codex-browser-app/Cache` | 约 829 MiB | Browser partition cache | 可重建 |
| `~/Library/Application Support/Codex/Partitions/codex-browser-app/Code Cache` | 约 310 MiB | JavaScript code cache | 可重建 |
| `~/.codex/plugins` | 约 433 MiB | 插件运行时与下载缓存 | 当前运行时应保留，仅清临时安装残留 |
| `~/.codex/.tmp` | 约 265 MiB | marketplace/plugin 同步临时副本 | 可重建，退出应用后清理 |
| `~/.codex/archived_sessions` | 约 98 MiB | 已归档会话 | 仍是用户历史数据 |
| `~/.codex/mcp-servers` | 约 82 MiB | MCP 服务运行文件 | 保留 |
| `~/.codex/computer-use` | 约 60 MiB | Computer Use 运行时 | 保留 |
| `~/.codex/skills` | 约 42 MiB | 用户与全局 Skills | 保留 |
| `~/.codex/cache` | 约 15 MiB | App directory、插件目录等索引缓存 | 可重建 |

`~/Library/Application Support/Codex` 中约 1.14 GiB 集中在 `Partitions/codex-browser-app` 的 `Cache` 与 `Code Cache`。同一目录下的 `Local Storage`、`Session Storage`、`Cookies`、`Preferences` 和浏览器侧边栏状态体积很小，但承载登录态和交互状态，应与缓存目录分开保留。

## 可安全优化的范围

执行前需要完全退出 Codex/ChatGPT，确认 `Codex`、`codex app-server`、`codex-code-mode-host` 等进程已经结束。当前扫描时这些进程仍在运行，因此本次没有执行任何清理。

第一批可以处理以下纯缓存和临时目录，预计释放约 **3.0 GB**：

- `~/Library/Caches/Codex`
- `~/Library/Application Support/Codex/Partitions/codex-browser-app/Cache`
- `~/Library/Application Support/Codex/Partitions/codex-browser-app/Code Cache`
- `~/Library/Application Support/Codex/Cache`
- `~/Library/Application Support/Codex/Code Cache`
- `~/Library/Application Support/Codex/GPUCache`
- `~/Library/Application Support/Codex/GraphiteDawnCache`
- `~/.codex/.tmp`
- `~/.codex/cache`

插件目录里还存在约 **16 MiB** 的 `plugin-install-*` 和 `plugin-backup-*` 临时残留。它们可以单独处理，但收益较小。`~/.codex/plugins/.plugin-appserver` 约 293 MiB，是当前运行时；`~/.codex/plugins/cache` 中当前版本的 Skills 和 MCP 能力也被 Codex 直接引用，不适合整目录手动删除。

## 会话历史治理

当前共有 720 个 active session 文件和 152 个 archived session 文件。按文件修改时间统计：

| 时间范围 | 文件数 | 占用 |
|---|---:|---:|
| 超过 30 天 | 621 | 约 892 MiB |
| 超过 60 天 | 424 | 约 394 MiB |
| 超过 90 天 | 337 | 约 212 MiB |
| 超过 120 天 | 175 | 约 110 MiB |

这里最有效的策略不是批量删除所有旧会话，而是先处理极端大文件。`~/.codex/sessions/2026/06/08/rollout-2026-06-08T16-43-07-019ea666-5e41-7d13-8287-87e5421dea24.jsonl` 单文件约 740 MiB，约占全部会话数据的三成。它累计了 47,850 条记录，其中包括 31,226 条 `response_item` 和 15,921 条 `event_msg`，表现为长时间追加造成的历史膨胀。

建议采用以下保留策略：

1. 最近 30 天会话完整保留，保证仍在继续的任务可以恢复。
2. 30 至 90 天会话先确认是否已有 `memories/rollout_summaries` 或仓库文档承接结论，再归档或删除原始 JSONL。
3. 超过 90 天的会话以“已有摘要、无未完成任务”为清理条件，而不是只按日期判断。
4. 对超过 100 MiB 的单会话设置专项检查。完成长期任务后创建新任务继续，避免一个 rollout 持续追加数万条工具记录。
5. 不直接手删 `state_5.sqlite`、`session_index.jsonl` 或仍显示在 Codex 侧边栏中的会话文件。优先通过 Codex 的归档/删除入口处理，避免文件与索引状态不一致。

### 740 MiB 会话专项检查

最大文件对应 Codex 任务 `三仓都基于 preview 更新最新代码`，thread id 为 `019ea666-5e41-7d13-8287-87e5421dea24`。它从 2026-06-08 16:43 持续到 2026-06-19 22:32，当前仍是 active 状态，`history_mode=legacy`。任务后期在 `session_index.jsonl` 中曾显示为 `【workspace】功能开发验证`，说明同一个任务跨越了多个开发阶段，标题已经不能完整表达它的内容。

文件中的 740.1 MiB 主要由以下记录组成：

| 记录类型 | 数量 | 占用 | 比例 |
|---|---:|---:|---:|
| `compacted` | 100 | 约 613.5 MiB | 82.9% |
| `function_call_output` | 8,322 | 约 58.7 MiB | 7.9% |
| assistant/user message | 约 5,950 | 约 25 MiB | 约 3.4% |
| reasoning、MCP、tool call 等 | 其余 | 约 43 MiB | 约 5.8% |

`compacted` 记录保存 `message` 和 `replacement_history`。这个任务在 11 天内发生 100 次 context compaction，后期每条 compacted snapshot 达到约 10–11 MiB。6 月 19 日一天的 20 次 compaction 就新增约 205 MiB。这里的主要问题是每次压缩继续保存逐渐变大的替代历史，形成重复写入，并非图片或附件占满空间。

数据库记录的累计 token counter 为 1,149,595,595，其中 cached input token 为 1,080,396,672。这个数字包含同一长任务反复加载的缓存输入，不能直接当作账单 token；它能说明任务长期携带了大量历史上下文。Top 1 文件占全部 active session 数据的 29.8%，Top 10 占 48.8%，因此优先治理少量极端长任务比按日期批量删除更有效。

这条会话承载的内容远多于现有标题，至少包括：Workspace 产品方案和多轮需求确认、Web/Backend/ML 三仓实现、流式对话与 UI 调整、数据库迁移、信源和 artifact provenance、Workspace Harness tool runtime、research quality gate、final URL 原文闭环以及多轮浏览器 E2E。当前 `memories/rollout_summaries` 只为该 thread 生成了一份 document-reference provenance 总结，主要覆盖 6 月 19 日后段的引用预览修复，无法代表 11 天内的全部决策。

因此这条会话当前不适合直接删除。建议先从原始会话、三仓提交记录和现有 Workspace 设计文档生成一份完整的阶段总结，核对产品决策、架构约束、数据迁移和测试证据都已有文档承接，再通过 Codex 任务入口删除原任务。仅归档不会减少 JSONL 占用。将原文件做 `gzip -1` 只能从 740.1 MiB 降到约 506.5 MiB，节省约 31.6%，同时 Codex 无法直接恢复压缩文件，因此压缩归档的性价比较低。

## 必须保留的资产

以下目录体积不大，且承担配置、记忆或能力注册，清理收益低、恢复成本高：

- `~/.codex/config.toml`、`auth.json`、`AGENTS.md`、`rules/`
- `~/.codex/memories` 与 `memories_1.sqlite`
- `~/.codex/skills`、`~/.codex/superpowers`
- `~/.codex/automations`
- `~/.codex/state_5.sqlite`、`session_index.jsonl`
- `~/.codex/mcp-servers`、`~/.codex/computer-use`
- `~/Library/Application Support/Codex` 下的 `Local Storage`、`Session Storage`、`Cookies`、`Preferences`

## 长期优化建议

Codex 当前的增长来源主要是 Browser Cache 和长会话 JSONL。建议把清理机制分成两条：纯缓存按月清理；会话历史按季度审查，并以摘要是否已落入 `memories` 或仓库文档作为删除前提。两条机制分开后，空间优化不会牺牲任务可恢复性和长期记忆。

如果要进一步自动化，可以增加一个只读巡检脚本，每月报告以下指标：Codex 总占用、纯缓存占用、超过 100 MiB 的 session、30/60/90 天会话占用、插件临时安装目录。脚本默认只生成报告，不执行删除。

## 会话标签清理策略

2026-07-13 确认后续用标题前缀 `【长期】` 标记需要长期保留的 Codex 会话，没有该前缀的已结束会话进入删除候选。使用精确前缀比搜索“长期”二字更可靠：当前有一条异常旧标题嵌入了大段 JSON，正文偶然出现“长期合作伙伴”，按普通 substring 会被错误识别为长期会话。

当前 dry-run 结果为：873 条数据库 thread 中，2 条带 `【长期】` 前缀，合计约 6.5 MiB；其余 871 条合计约 2,572.7 MiB。最大 740 MiB Workspace 会话没有长期标签，按新规则属于删除候选。当前正在运行的任务和 automation run 需要在批量操作时临时排除，结束后再进入下一轮清理。

批量清理不能只删除 `sessions/` 和 `archived_sessions/` 下的 JSONL。Codex 还在 `state_5.sqlite`、`session_index.jsonl` 和相关动态工具表中维护 thread 状态。应优先使用 Codex 自带的任务删除能力；如果当前版本没有批量删除接口，需要先设计带备份、事务和一致性校验的迁移脚本，避免侧边栏残留失效任务或 SQLite 外键记录不一致。
