# Codex 执行经验复盘

> 维护方式：由 `Codex Experience Review` 周期任务更新。本文档是后续 Codex 会话默认继承的经验档案，聚焦执行方式、用户偏好、产品与 UI 判断，以及可直接遵循的行为准则。

## 数据来源

周期任务必须读取并交叉验证以下本机资料：

- `/Users/xuhao/.codex/sessions/`
- `/Users/xuhao/.codex/archived_sessions/`
- `/Users/xuhao/.codex/memories/MEMORY.md`
- `/Users/xuhao/.codex/memories/rollout_summaries/`
- `/Users/xuhao/.codex/logs_2.sqlite`
- `/Users/xuhao/.codex/sqlite/logs_2.sqlite`
- 当前 workspace 的 `AGENTS.md`、`rules/`、`contexts/`、`periodic_jobs/`

任务可以读取真实日志和对话记录，但不得把 secrets、token、cookie、私密内容或可识别的第三方隐私写入本文档。必要时只写抽象经验和可复用规则。

## 最近复盘范围

- 本轮运行于 `2026-07-15`，已建立索引：`/Users/xuhao/.codex/sessions/` 335 个 rollout，时间范围 `2026-01-14 12:01:04` 到 `2026-07-15 09:01:58`；`/Users/xuhao/.codex/archived_sessions/` 92 个 rollout，时间范围 `2026-03-05 11:35:24` 到 `2026-07-14 11:15:26`。
- 已读取 `MEMORY.md` 与 17 份 `rollout_summaries`，其时间范围是 `2026-05-22 09:04:21` 到 `2026-07-14 06:19:20`。本轮额外定向回读了 5 个 raw session rollout、1 个 archived session rollout，以及 1 份新增 rollout summary；重点线索集中在 Workspace 默认 mounted skill、evidence/provenance 修复、本地 `Upgrade required`、context unit 原子计数和参考站个人站实现约束。
- 已核对 `/Users/xuhao/.codex/logs_2.sqlite` 和 `/Users/xuhao/.codex/sqlite/logs_2.sqlite`。两份库都可读，但 `logs` 表当前都是 0 行，所以这轮依旧没有额外 sqlite 事件证据可提炼。
- 已交叉对照当前 workspace 的 `AGENTS.md`、`rules/`、`contexts/`、`periodic_jobs/` 与现有复盘文档，把重复经验合并，只保留足够稳定或高风险的规则。

## 一、执行经验总结

### 1. 先读规则，再动手

问题做法：进入 workspace 后直接搜索或改文件，容易忽略目录路由、沟通规则、测试约束和已有 skill。

正确做法：每次先读取 `AGENTS.md` 要求的 `rules/SOUL.md`、`rules/USER.md`、`rules/WORKSPACE.md`、`rules/COMMUNICATION.md`、`rules/skills/INDEX.md`。找文件时先看 `rules/WORKSPACE.md`，再用 `rg` 定位。

教训：这个仓库的价值在于长期上下文。跳过规则会让 agent 退化成一次性脚本执行器。

### 2. 结论必须落到文件

问题做法：把产品判断、架构方案、调研结论只留在聊天里，后续 session 无法继承。

正确做法：凡是后续可能复用的结论，都按 `rules/WORKSPACE.md` 写入对应目录。调研报告进 `contexts/survey_sessions/`，复盘和方法论进 `contexts/thought_review/`，可复用流程进 `rules/skills/`，长期协作规则进 `AGENTS.md` 或 `rules/`。

教训：文件是这个系统的长期记忆接口。聊天里的判断只有被写成文档，才会变成可继承资产。

### 3. 不用印象替代真实链路

问题做法：看到现象后只按经验解释，或者只看 UI / README / 文件存在就下结论。

正确做法：沿真实链路核对代码、配置、数据库、缓存、运行时、部署和日志。涉及 OpenAI / 第三方 / 时间敏感信息时查官方文档或真实状态。涉及浏览器验证时使用 Codex 插件控制本地 Chrome。

教训：徐昊更看重可验证的闭环，而不是看起来合理的解释。

### 4. 保护本地工作区

问题做法：为了让当前任务变干净，直接 reset、checkout 或覆盖已有改动。

正确做法：先 `git status --short`。只改本次任务相关文件；遇到已有改动默认视为用户或其他任务的工作成果。需要跨分支、merge、stash 或清理时，先确认影响范围。

教训：本地脏工作区是常态。工程动作要以“不破坏已有工作”为底线。

### 5. Hard-cut 要做完整

问题做法：用户说产品没上线、不需要兼容、目前不透出时，只做视觉隐藏或入口隐藏。

正确做法：同时清理入口、路由、open-state、dialog、guide、scheduler、tests、docs 和共享依赖边界。删除前必须查 call sites，避免误删仍被其他功能复用的类型或存储。

教训：产品未上线时，长期合理性优先于表面兼容。完整下线比半隐藏更可维护。

### 6. 失败经验要写成规则

问题做法：修完一个环境、CLI、MCP、缓存、日志或部署问题后，只汇报“修好了”。

正确做法：补充“症状、原因、正确处理方式、下次默认动作”。如果是跨项目可复用经验，写到 `rules/skills/` 或本文件。

教训：同类问题一定会再次出现。可复用规则比一次性修复更有价值。

### 7. 先恢复系统基线，再做下游验收

问题做法：浏览器、页面、Chrome bridge 或 UI 展示异常时，立刻在壳层现象上打转。

正确做法：先恢复底层基线，再做下游验证。对 Mindspace 这类三服务链路，先确认 `8099/8079/9090` 都健康；对系统网络问题，先看默认路由、DNS、关键进程和过滤器状态。只有底层健康后，浏览器验收才有解释力。

教训：下游 symptom 噪声很大。底层没站稳时，Chrome、loading shell、UI 空白都不具备诊断价值。

### 8. 用户改了一个变量，就做一次新的单变量诊断

问题做法：用户已经关闭后台隧道、重启机器或换了一个运行状态后，仍沿用旧结论，或者继续叠加新的猜测性操作。

正确做法：把用户刚刚改动的那个变量当成新的起点，立即重采 baseline，再围绕这一个变量做 A/B。必要时明确写出“启用时怎样、停用时怎样、重启后怎样”。

教训：能归因的诊断，比“看起来修好了”的描述更有复用价值。

### 9. 历史方案与当前状态必须分开验证

问题做法：把“之前调研过”“之前做过”“之前安装过”直接当成当前事实。

正确做法：凡是涉及账号状态、平台条款、provider endpoint、浏览器扩展、native host、MCP 连接、自动化集成的事，都要把历史方案和当前实况拆开验证。历史记录只能提供搜索入口，不能替代 live check。

教训：这类系统最容易漂移。旧方案、旧路径、旧授权状态和现在往往不是同一回事。

### 10. 输出偏好与能力证据要分开存档

问题做法：自动化、brief、召回、插件或第三方集成任务里，只要输出结构看起来合理，就顺手把“能力已经打通”也当成事实写下来。

正确做法：区分两种资产。用户给出的版式、语言、筛选口径，属于稳定偏好；真实数据链路、授权成功、插件可用、浏览器可连，属于执行证据。没有 tool-run 或 live proof 时，只能记录前者。遇到交互授权，则尽快把精确的 `verification_url` 或下一步动作交还用户继续。

教训：偏好可以复用，能力必须验真。把两者混在一起，后续 session 很容易误判现场状态。

### 11. 完成态按用户目标定义，不制造提交噪音

问题做法：把“提交一个分支”“推上去”机械理解成“必须新建 commit”，即使 worktree 已经没有 tracked diff。

正确做法：先检查 `git status -sb` 和远端状态。用户要的是可见的远端结果时，完成态可以是“当前 HEAD 上的分支已创建并推送”，不需要为了形式去制造空提交。本地运行产物如 `.playwright-mcp/`、`.local-stack-logs/` 默认留在工作树外。

教训：面向结果的 git 操作更干净，也更符合长期仓库卫生。

### 12. 任务合同只能有一个真源

问题做法：产品已经有 `Profile` / schema / quality gate 这类正式任务合同后，还保留一个默认 mounted skill 作为兜底能力，导致 UI 标签、模型指令和真实任务边界相互打架。

正确做法：先判断系统里谁才是任务合同的真源。对 Workspace 这类执行系统，`Profile` 应独占来源、工具、产物结构和质量门禁；默认 mounted skill 要 hard-cut，只保留用户主动添加的正交增强能力。历史数据则在读取、更新和 run 执行入口统一过滤，而不是只改某一层展示。

教训：当两个合同同时存在时，产品会先出现错误暗示，执行层再被旧逻辑带偏。稳定修复不是“换一个更准的默认值”，而是删掉多余合同。

### 13. 计数和门禁必须绑定原子单元

问题做法：把文件数、命中的来源条数、`有正文` 的 source 数或宽泛的 `usableReferenceCount` 当成复杂度、覆盖率或成功门槛。

正确做法：先定义真正的原子单元，再让计数、复杂度和 gate 都绑定到这个单元。对 context/skill 同步，应以 `skill` / `rule` 单元为准，而不是文件数；对检索/证据链路，应以 `source family`、`evidence role`、relevance 和 `attempted / matched / skipped / failed` 这类显式状态为准，而不是“数量够了”。

教训：指标口径一旦错了，UI 展示、fallback 逻辑和质量门禁会同时被污染。问题表面看像文案或排序，根上其实是资产模型和状态模型定义错了。

### 14. 本地调试绕过要做成环境边界

问题做法：本地调试遇到套餐、额度或商业门禁时，只在某个子路径关开关、加账号白名单，或者只改前端文案；结果一旦本地和生产共享数据库、队列或 runner，生产门禁仍会在真实链路里抢先触发。

正确做法：把“本地调试绕过”做成清晰的环境边界。后端统一返回稳定的机器原因码，如 `upgrade_required` / `llm_usage_quota`；Web 负责按 `resolvedLanguage` 显示中英文；`ENV_MODE=local` 要同时控制 quota enforcement 和任务 transport/runner ownership，确保任务真的走本地执行链路。

教训：本地 debug path 如果没有独立边界，只是把线上商业约束随机地移来移去。真正的修复是让 local mode 拥有完整、可验证的执行闭环。

### 15. Provenance 的信任边界要卡在持久化凭据

问题做法：接受模型自报的 URL、quote、`sourceType`、成功态或 Artifact 内容；provider 抓到原文但 clue 不匹配时直接丢弃快照；HTML 原文未经清洗就进入最终报告。

正确做法：把信任边界卡在已持久化的 planner / retrieval checkpoint 和 canonical receipt。任何 provenance 敏感字段都必须绑定真实 preflight/provider grounding；不满足就标记 `model_unverified` 并 fail closed。provider 抓取成功但暂时不能提升时，先保留原文快照；只有经过 dimension × role × period 复核的结果才能提升为正式证据或写入 Artifact。所有引用和报告 block 在 Artifact 边界统一转纯文本。

教训：这类系统的长期稳定性，不来自更多 prompt，而来自更窄的 trust boundary。

### 16. ID 合同出错时先修生成器，不要先扩列

问题做法：数据库报 `Data too long` 之类错误时，先扩 `VARCHAR`、放宽 schema 或新增一次性兼容迁移，把上游 ID 合同问题藏起来。

正确做法：先核对列宽、ID namespace 和生成器的原始设计，再修上游生成逻辑。像 `goal_revision_id` 这类统一业务 ID，应维持稳定长度合同，用确定性派生或新的安全命名空间修复，而不是让不同入口各自生成不同长度的 ID。

教训：扩列能让当前写入通过，但会把不一致的 ID 语义扩散到更多表和更多服务里。

## 二、徐昊偏好与理念档案

### UI 设计偏好

- 偏好真实、密度合适、可重复使用的工作界面。SaaS、CRM、运营工具应安静、克制、可扫描，避免营销式 hero、装饰性卡片堆叠和单一色相氛围。
- 文案必须精确，尤其是状态、CTA、错误、disabled、expired、互斥关系和 backend display text。用户给出明确文案时应原样落实。
- 错误文案应由展示层按当前语言环境映射，不把某一种自然语言硬编码进后端稳定错误合同。
- 图标语义要准确。工具按钮优先使用熟悉符号和已有 icon library，不用文字胶囊替代常见图标。
- UI 状态不能只靠“看起来差不多”。需要验证移动端和桌面端的文本容器、布局重排、重叠、加载态、空态和错误态。
- 临时 mock 只用于验证，验证后立刻删除，不能留下会误提交的开关。
- 参考站复刻或个人资料页任务里，核心交互语言要尽量贴近参考站；未确认的个人信息、项目内容和外链应留空，不靠推断补满。

### 产品设计理念

- 产品壳层和真实能力要对齐。未上线或未准备好的能力宁可 hard-cut，也不要制造可点击但不可用的假入口。
- AI 产品设计要区分“感知层”和“真实执行层”。前台可以用用户理解的比例和状态，后台必须保留真实成本、token、模型、source、artifact、checkpoint 等可审计数据。
- Workspace / agent 类产品的价值在于上下文、来源、产物、记忆和可续接运行，而不只是一个聊天框。
- 一旦已有 `Profile`、schema 或 run contract 这种正式任务合同，它就应成为唯一真源；默认 mounted skill 只适合用户显式选择的正交增强，不适合做兜底任务定义。
- 首页推荐、任务入口和 briefing 需要具体到公司、行业、资产范围或明确目标，泛泛推荐没有决策价值。
- 当用户说“展示内容不对”时，尤其是 memory / goal / context 这类界面，默认问题在真实数据分层、revision/version 语义或 durable context pack，而不只是标签文案。
- 复杂度、资产数和 coverage 这类产品指标，应该展示原子单元，并把 `unit_count` 与底层 `file_entry_count` 之类实现细节分开。

### 交互原则

- 直接执行优先。用户说“改吧”“跑一下”“merge进去”“写到 AGENTS.md”时，默认推进到实现、验证、文档回填，不停在解释层。
- 该问时问，但先自己查。只有答案无法从本地上下文发现，并且错误假设会造成风险时再问。
- 回答要短、直接、有判断。不要客套，不要用“好问题”“乐意效劳”，不要用漂亮但空的判断词。
- 对用户的纠正要转成长期规则。尤其是文案、图标、状态、mock 回收、验证方式、兼容边界和测试要求。
- 用户说“我重启了，你重新验收吧”时，要把它理解为一次 fresh acceptance request，而不是让你复述上一轮结果。

### 工程验证偏好

- 浏览器、插件、Chrome extension、MCP 或页面壳层异常时，先把底层服务和系统基线拉到健康状态，再做 UI/交互验收。
- 用户主动改变一个环境变量后，偏好单变量复测。关掉后台隧道、停用一个过滤器、重启机器之后，都要重采 baseline。
- 不接受“组件都装着”“扩展看起来 enabled”“命令能跑 `--help`”这种弱证据。用户更看重真正连通、真正可用、真正通过测试的闭环。
- 自动化和集成类任务里，没有执行证据时只能沉淀输出格式和口径，不能顺手暗示能力已经接通。
- 本地调试类修复，偏好真实队列/数据库/浏览器闭环验证；配置值显示正确不等于执行路径真的已经切到 local。

## 三、Codex 可复用规则清单

1. 每个 workspace 先读 `AGENTS.md` 和它要求的规则文件，再执行任务。
2. 找文件先看目录路由，再用 `rg`；不要上来全盘搜索。
3. 遇到“怎么做 X”先查 `rules/skills/INDEX.md`，再查系统工具。
4. 所有长期可复用结论必须写入仓库文件，不能只留在对话。
5. 涉及当前状态、最新信息、价格、规则、第三方接口和高风险判断时，必须实时验证。
6. 涉及真实产品链路时，优先核对代码、配置、数据库、缓存、日志和部署，不凭印象回答。
7. 涉及 Web UI、截图和交互验证时，默认使用 Codex 插件控制本地 Chrome。
8. 改文件前先看 `git status --short`，保护已有未提交改动。
9. 不执行破坏性 git 或文件操作，除非用户明确要求。
10. 处理下线、隐藏、迁移和 hard-cut 时，要清理入口、状态、测试和文档，并查共享依赖。
11. 设计 UI 时保证所有状态完整：loading、empty、error、disabled、expired、success、retry。
12. 前端临时 mock 验证后必须删除。
13. 文案遵循用户给出的精确表达；不擅自改写产品状态含义。
14. 工程任务要跑相应测试或 smoke；无法运行时说明原因和剩余风险。
15. 环境和工具链修复必须补真实 smoke，不把 `--help` 或文件存在当成最终验证。
16. 复盘类任务要写“问题做法、正确做法、教训”，避免只写抽象原则。
17. 对外部或敏感数据只提炼行为规则，不写 secrets、token、cookie 或隐私明文。
18. 浏览器、Chrome extension、MCP 或页面壳层异常时，先恢复底层基线；本地服务、路由、DNS、进程和过滤器健康之后，再做下游验收。
19. 用户刚改了一个变量时，先采新的 baseline，再围绕这个变量做单变量 A/B，不叠加新的猜测性修复。
20. 历史调研、旧方案、旧账号认知和当前 live state 不是一回事；涉及条款、endpoint、授权、扩展、native host 或集成状态时，必须重查实况。
21. 输出偏好和执行证据分开记录。没有 tool-run、live data 或成功连通证据时，只能沉淀格式偏好，不能暗示能力已打通。
22. 遇到交互授权卡点时，尽快把精确的 `verification_url` 或下一步操作原样交给用户，不在同一轮里盲目重试。
23. “push 一个分支”之类请求的完成态是远端结果可见；没有 tracked diff 时不要制造空提交。
24. 本地运行产物如 `.playwright-mcp/`、`.local-stack-logs/` 默认不提交，除非用户明确要求。
25. 已有 `Profile` / schema / quality gate 合同时，不再叠加默认兜底 skill；`Profile` 负责来源、工具、产物和质量门禁，skill 只保留用户主动添加的正交增强。
26. 计数、复杂度、coverage 和成功门禁要绑定原子单元或显式 family/status，不用文件数、弱 source 数量或“有正文”当代理指标。
27. 本地调试绕过必须通过环境边界和 transport 边界实现；不要依赖账号白名单或散落开关。后端返回稳定机器错误码，前端按当前语言本地化展示。
28. provenance 敏感链路不能信模型自报的 URL、quote、`sourceType` 或完成态；必须绑定已持久化的 planner/retrieval checkpoint 与 canonical receipt，不满足就 fail closed。
29. provider 抓到原文但 clue 不匹配时，先保留快照；只有经过 dimension × role × period 复核的结果才能提升为正式证据或写入 Artifact。
30. 参考站重建或个人资料页任务中，优先保留真实交互语言；未知的个人信息、项目链接或资历留空，不用推断内容补满。

## 周期任务维护要求

每次 `Codex Experience Review` 运行时，应追加或更新以下小节：

- `最近复盘范围`：本次读取的 session/log 时间范围、文件数量、被跳过的敏感来源。
- `新增执行经验`：新增的失败模式、正确路径和证据位置。
- `偏好档案变更`：新增或修正的 UI / 产品 / 交互偏好。
- `规则清单变更`：新增、合并或废弃的可执行规则。

更新时应保持本文档可读，不要无限追加低价值流水账。重复经验要合并，只有被多次验证或足够高风险的经验才进入规则清单。

## 四、本轮变更记录（2026-07-14）

### 新增执行经验

- 已把“先恢复系统基线，再做下游验收”合并为第 7 条。证据主要来自 Workspace Harness 的三服务验收与 Chrome bridge 恢复，以及 macOS 网络问题里先做 route/DNS/filter 基线再做上层验证的做法。
- 已把“用户改了一个变量，就做一次新的单变量诊断”合并为第 8 条。它来自关闭 background tunnel、Defender Network Filter A/B、以及重启后重新验收这几类高复现诊断场景。
- 已把“历史方案与当前状态分开验证”“输出偏好与能力证据分开存档”“完成态按用户目标定义，不制造提交噪音”合并为第 9、10、11 条，分别对应 Cloudflare/StrongVPN、每日简报/Lark 授权、clean worktree branch push 这几组证据。

### 偏好档案变更

- 产品设计理念新增了对 workspace context 展示问题的默认判断：优先查真实数据分层、revision/version 和 durable context pack。
- 交互原则新增了“重启后重新验收=重新做 live pass”。
- 新增 `工程验证偏好` 小节，集中记录徐昊对基线恢复、单变量复测、强证据验收和自动化执行证明的要求。

### 规则清单变更

- 新增规则 18-24，覆盖基线优先、单变量 A/B、历史方案 live re-check、偏好与证据分离、授权分流、无空提交 branch push、运行产物不入库。

### 未能提供额外证据的来源

- `/Users/xuhao/.codex/logs_2.sqlite` 与 `/Users/xuhao/.codex/sqlite/logs_2.sqlite` 虽可读，但 `logs` 表均为空，所以本轮没有从 sqlite 补充到新的经验条目。

## 五、本轮变更记录（2026-07-15）

### 新增执行经验

- 新增了第 12-16 条，分别覆盖“任务合同唯一真源”“计数与门禁绑定原子单元”“本地调试绕过的环境边界”“provenance 绑定持久化凭据”“ID 合同错误先修生成器”。
- 证据主要来自 2026-07-14 的 Workspace mounted skill / investor brief 讨论与修复、`Upgrade required` 本地链路修复、context unit 原子计数修复，以及一个 `goal_revision_id` 超长写库失败的 archived rollout。

### 偏好档案变更

- `UI 设计偏好` 新增两点：错误文案按当前语言环境在展示层映射；参考站复刻和个人资料页里，未知事实保持留空。
- `产品设计理念` 新增两点：`Profile` 是正式任务合同的唯一真源；复杂度和资产数要展示原子单元，而不是底层文件数。
- `工程验证偏好` 新增了对 local mode 的要求：必须验证真实 transport/queue/DB 是否已切到本地闭环。

### 规则清单变更

- 新增规则 25-30，覆盖 Profile 与 skill 的边界、原子计数、local debug 环境边界、receipt/provenance fail-closed，以及参考站复刻时的事实留空策略。

### 未能提供额外证据的来源

- `/Users/xuhao/.codex/logs_2.sqlite` 与 `/Users/xuhao/.codex/sqlite/logs_2.sqlite` 这轮依旧没有事件数据。
