# 周期复盘维护卡

适用场景：`Codex Experience Review` automation、经验文档维护、session/summary/sqlite 统计与续跑策略。

## 数据来源

- `/Users/xuhao/.codex/sessions/`
- `/Users/xuhao/.codex/archived_sessions/`
- `/Users/xuhao/.codex/memories/MEMORY.md`
- `/Users/xuhao/.codex/memories/rollout_summaries/`
- `/Users/xuhao/.codex/logs_2.sqlite`
- `/Users/xuhao/.codex/sqlite/logs_2.sqlite`
- 当前 workspace 的 `AGENTS.md`、`rules/`、`contexts/`、`periodic_jobs/`

## 最近已验证范围

- 本次运行日期为 2026-09-15，盘点快照 `2026-09-15T01:03:16.042141+00:00`；从上次已完成运行保留的事件锚点 `2026-09-14T01:01:24.263Z` 检查增量，覆盖旧会话续聊。当前 automation 仍在写入，数字仅代表快照。
- `sessions/` 全部 117 份可读，共 76,076 条 JSONL，解析错误 0；创建时间 `2026-01-14T04:01:04.241Z` 至 `2026-09-15T01:02:04.777Z`，事件时间 `2026-01-14T04:01:04.267Z` 至 `2026-09-15T01:03:15.599Z`。
- `archived_sessions/` 全部 85 份可读，共 26,066 条 JSONL，解析错误 0；创建时间 `2026-02-13T03:06:43.738Z` 至 `2026-09-14T01:01:24.263Z`，事件时间 `2026-02-13T03:07:13.958Z` 至 `2026-09-14T01:06:39.370Z`。
- 全库用户/助手消息定向检索失败、修复、回滚、缓存、验证、偏好、UI、产品、文案、Chrome、数据库、部署、MCP、skill、mock、hard-cut，分别命中 active 1,376 条、archived 691 条。含注入规则与复制历史，不作为独立经验数。
- 增量涉及 active 24 份、archived 1 份；按首条身份元信息识别 16 个 subagent，再显式排除当前和上次复盘两个 automation，保留 7 个主会话，其中 2 个为旧会话续聊。147 条用户/最终回答候选中有 79 条用户消息，含目标续跑与结构化回复。阅读用户请求概览并按主题抽样最终回答；宽输出曾截断，晋升内容另行窄范围回读，未声称逐条精读全部候选。
- `rollout_summaries/` 全部 43 份读取正文并扫描日期、关键词，42 份命中；正文 `updated_at` 从 `2026-08-12T02:27:58+00:00` 至 `2026-09-11T10:58:27+00:00`，本次增量窗口内 0 份。`MEMORY.md` 共 1,822 行，定向读取复盘注册项及其技能；旧技能的创建时间筛选建议服从本卡事件时间规则。未修改全局 memory。
- 两份 SQLite 均只读核验 `logs` schema、`ts / ts_nanos` 范围与触发器：各 0 行、时间边界为空，均有 `codex_block_logs_insert`。所有指定来源可读取，SQLite 没有可精读执行条目。

## 本轮经验与证据

- 执行经验：工程 L1 合并原件、派生视图与当前网页版本的区别，并要求检查旧能力是否接入新入口。原始会话 `/Users/xuhao/.codex/sessions/2026/09/09/rollout-2026-09-09T17-58-27-01a0859a-c322-7712-a67a-be6d7272dda1.jsonl` 第 26954 行纠正转换内容冒充原件；第 28227、28250 行记录旧 iframe 能力与新入口未接通，第 28625、28995 行要求并汇报真实报告验证。交叉核对 `contexts/survey_sessions/cited_alpha_agent_redesign/36_production_full_function_20260914.md` 的原件验收纠正、当前网页版本及真实报告本地验收小节。具体右侧布局留在项目合同，不升为全局 UI 模板。
- 偏好与理念：产品 L1 增加从使用场景和验收标准进入技术方案的规则；L0 合并到既有架构偏好，仍保持 8 条热路径规则。`/Users/xuhao/.codex/sessions/2026/09/14/rollout-2026-09-14T17-05-09-01a09f29-c535-7af3-94eb-103d826b3d70.jsonl` 第 797、807、810 行区分产品方向和技术实现，第 881、884、961 行区分 README 参考、源码对比与真实运行，第 968 行要求保留先前需求。跨案例复证来自 `/Users/xuhao/.codex/sessions/2026/09/14/rollout-2026-09-14T19-10-22-01a09f9c-685f-74c3-9d1d-87795b82bd13.jsonl` 第 9、208、211 行：业务调研先于产品定案，儿童探索目标需要同步修正记忆/答题指标。具体儿童产品定位只保留为任务级证据。
- 阶段状态校正：9 月 14 日生产报告已有成功结果。回读 `artifacts/20260914-production-report/run-status.json` 的 `status=succeeded`、`executionStatus=succeeded`、`deliveryStatus=complete`，与上述第 36 号报告的最终生产验收及 session 第 26405 行一致。随后原件展示验收仍经历用户纠正；最终新增 RSS 原网页适配的真实报告验证仅本地生效。不能沿用上轮生产未启用结论，也不能把本地后续改动写成已部署。本轮未执行云端查询或浏览器复验。
- L2 保留登录复用边界、支付申请与可收款状态、绘本视觉反馈、地铁繁体/线路与排行榜、儿童资料准备；主要复证现有能力分层和用户验收规则，不新增通用供应商、布局或指标偏好。DeepSearch 新链路最终回答仍记录本地验收与内容质量缺口，全量测试失败未被聚焦测试掩盖，不记作上线或质量全面通过。
- 本次只更新指定经验文档与 automation memory；现有其他脏文件保留，未改业务代码、提交或推送。

## 当前写入策略

- `L0` 启动卡只保留默认加载必须知道的约束，不写运行级细节。
- `L1` 专题卡只保留可复用的主题规则，不做流水账。
- `L2` 冷数据承接 run-level 细节：
  - automation memory
  - `MEMORY.md` 索引
  - rollout summaries
  - 原始 sessions / archived sessions / sqlite

## 晋升规则

1. 新样本先写到 automation memory。
2. 满足“重复 2 次以上 / 高风险 / 稳定偏好”之一，才升级到 `L1`。
3. 满足“跨任务通用 + 高频命中 + 不读就容易反复犯错”三项，才升级到 `L0`。
4. 只服务单一项目、时效已过、或只是本轮证据摘要的内容，一律留在 `L2`。

## 删除规则

- 重复表达只保留信息密度更高的版本。
- 低频、过时、只描述一次现场的条目，优先降级或删除，不做历史尾巴。
- `Codex Experience Review` 不是周报；不要在任何层追加按日期堆积的变更日志。

## 维护要求

- 每次运行都要统计本次读取的 session、archived session、summary 和 sqlite 范围。
- 增量筛选扫描会话内事件时间，覆盖旧文件续聊；文件名和 `session_meta.timestamp` 只表示创建基线。summary 按正文 `updated_at` 判断补写，避免仅按文件名漏检，也不用 `mtime` 直接断定内容更新。以文件首条身份元信息识别 automation/subagent；后续复制历史中可能出现父会话的 `session_meta`，不能用最后一条覆盖文件身份。再结合主会话 id、事件标识与消息内容去重。
- 新鲜用户线程还没进入 rollout summary 时，直接回读 session 原文补证，不把“summary 暂缺”误判成“没有新样本”。
- 如果增量窗口只命中 automation/self-run，就按维护轮处理：刷新统计、维护卡和 automation memory，不为制造变更而扩写 `L0`。
- 如果窗口里只有 1 个新用户线程，且它只是复证已有 `L0/L1` 规则，就更新维护卡和 automation memory，不为“有增量”而硬造新条目。
- 完成后中文简报只需要报告三件事：这次更新了哪些层、动了哪些小节、哪些来源未能读取。
- 敏感信息只保留抽象经验、可执行规则和必要证据路径。
