# Muse 源码证据核验（只读，2026-09-09）

范围：moduxserver 与 modux 当前本地源码。读过两业务仓 AGENTS；modux 未发现 AGENTS。未启动应用、未跑测试、未访问线上配置。以下证明实现存在，不证明生产生效、质量收益或用户个人贡献。尤其不能把框架能力直接说成 Muse 当前每个路径均启用。

## 1. 长任务上下文压缩，保留近期轨迹与文件操作索引

- 难点：代码 Agent 持续读取设计、文件与工具结果，历史超长会拖慢请求并稀释关键信息。
- 证据：`/Users/xuhao/Documents/Basic/modux/packages/agent/src/compaction/compactLogic.ts:48` 估计 token、选择 cutpoint；`:72` 读取前一摘要，`:77` 收集文件操作，`:81` 生成摘要，`:93` 组合摘要和保留消息。
- 触发机制：`/Users/xuhao/Documents/Basic/modux/packages/agent/src/actors/workflow/hook.ts:250` 无 compaction 配置则跳过；`:258` 估计阈值；`:273` 更新消息；`:285` 失败仅日志，继续原上下文。
- Muse RN 配置：`/Users/xuhao/Documents/Basic/moduxserver/src/app/agentInstance/workflows/rn-product-v2.workflow.ts:673` 配置 keepRecentTokens=200000，triggerThreshold=450000。数字仅当前源码，不建议面试背数字，也不代表所有模型安全窗口。
- 取舍：有损摘要与继续执行的成本之间平衡；关键业务约束/产物真源应放结构化状态及文件，而非只靠摘要。
- 不能声称：摘要无损、绝不会超窗、已证明节省多少成本；框架 hook 与线上实际包版本仍需核验。

## 2. Skill 元数据先展示，详情按需获取

- 难点：把所有企业能力说明塞进 prompt 会浪费上下文，也会增加工具选择歧义。
- 证据：`/Users/xuhao/Documents/Basic/modux/packages/agent/src/actors/workflow/utils.ts:374` 提取技能 name/description/mode/runners；`:418` 构造 available_skills 列表；`:440` 指引 get_skill_details 获取详情，再 execute_code 执行。
- Muse 工作流使用：`/Users/xuhao/Documents/Basic/moduxserver/src/app/agentInstance/workflows/rn-product-v2.workflow.ts:3691` 动态 resolveAppRuntimeSkills；同文件 `:3937` 另一节点使用。
- 取舍：progressive disclosure 降低常驻上下文，增加按需查询往返；技能描述质量会影响能否发现能力。
- 不能声称：Skill 等于 RAG；Skill 文档等于执行授权；所有节点都开放同一技能集。

## 3. 多 Agent 按产物责任拆分，overlay + 显式合并

- 难点：多页面并行生成存在文件覆盖、路由组装冲突和上下文串扰，单纯 Promise.all 不够。
- 证据：`/Users/xuhao/Documents/Basic/moduxserver/src/app/agentInstance/multi-frame/web-team-runtime.ts:164` 构建 assignments 并预检；`:186` 分配不合法则回落；`:212` worker 启动指定 initPrompt，`:213` fsMode=overlay，`:214` fsScope；`:514` 显式 mergeWorkersAndSpawnIntegrator；`:545` 调用 mergeChanges 并处理冲突。
- 同源契约：`/Users/xuhao/Documents/Basic/moduxserver/src/app/agentInstance/multi-frame/web-team.ts:498` Integrator 输入是已合并 Worker 产物，`:512` 负责跨页导航，`:513` 明确保留 Worker 页内控件，避免反复重写。
- 取舍：用可划分文件所有权的任务换并行收益；增加分配、合并、修复开销。不能拆清楚的任务保留单 Agent 回落。
- 不能声称：每个 Worker 拥有 OS 沙箱；overlay 文件隔离不是容器安全隔离；尚无墙钟延迟或成本收益实测。

## 4. Verifier 是确定性产物检查，且区分质量问题与交付阻断

- 难点：模型声称完成与可用产物之间有落差；要求所有质量项完美又可能吞掉本来可用的页面。
- 证据：`/Users/xuhao/Documents/Basic/moduxserver/src/app/agentInstance/multi-frame/web-codegen-verifier.ts:1` 使用 TypeScript；`:123` Worker 校验入口；`:138` 最终产物校验；`:146` 语法校验；`:161` router 缺失检查。
- 阻断集：同文件 `:70` Worker 仅缺产物/语法错误阻断；`:75` 最终加入 router、入口、组件 runtime 版本等；`:90` 按 severity 和白名单提取阻断问题。
- 运行策略：`/Users/xuhao/Documents/Basic/moduxserver/src/app/agentInstance/multi-frame/web-team-runtime.ts:1087` 请求集成修复；`:1092` 获取阻断项；`:1111` verified/degraded 两种交付模式。
- 取舍：有界修复后可降级交付非阻断问题；负责人应解释质量等级如何对用户可见。
- 不能声称：Verifier 是另一个 LLM Agent；检查通过=视觉一致/交互完整/真实业务成功；也不能说所有检查失败都阻断。

## 5. 执行隔离有不同等级，命名不是安全保证

- 框架证据：`/Users/xuhao/Documents/Basic/modux/packages/agent/src/tools/skill/execute_code.ts:479` 明确 NodeSDK 使用 in-process vm，`:487` 创建 SecureSandbox。
- 具体实现：`/Users/xuhao/Documents/Basic/modux/packages/agent/src/tools/skill/sandbox.ts:3` Node vm；`:17` timeout 与 allow/deny list；`:31` 禁用 process/require 等；`:107` Proxy 拦截访问。
- 另一能力：`/Users/xuhao/Documents/Basic/modux/packages/agent/src/tools/skill/providers/DockerProvider.ts:49` 提供 Docker 配置，`:84` memoryLimit 和 `:87` cpuLimit 为可选；`:121` 构造默认值；`:126` 默认复用容器。
- 取舍：进程内执行低开销；容器有依赖一致性与进程边界，但网络、挂载、凭证、租户复用都需单独设计。
- 不能声称：已确认 Muse 生产用 Docker/微虚机；Node vm 或 SecureSandbox 类名能保证执行不可信代码安全；Docker 选项存在不代表资源限制已配置。
- 面试建议：诚实区分“当前已确认实现”与“企业部署应补的安全边界”，不要为了讲完整而虚构生产沙箱。

## 6. 模型提供者与业务节点解耦，并统一错误诊断维度

- 难点：企业接入模型时供应商、鉴权、模型参数与流式错误存在差异，散落在业务节点会难以维护。
- 证据：`/Users/xuhao/Documents/Basic/moduxserver/src/app/aiRouter/providers/modux-ai.provider.ts:48` ModuxAIProvider 实现 AIModelProvider；`:58` createModel 接受 provider/model/runtime key/creator；`:89` buildModelTraceInput 汇总 preset、provider、model、tool 数量等；`:136` 单独处理 stream 消费期错误。
- 取舍：统一入口降低调用侧耦合，仍要保留 provider 特性差异和测试；统一接口不意味着模型行为可等价替换。
- 不能声称：已有自动智能选模、故障无缝 failover、供应商切换零成本、质量等价。当前读到的是 provider 适配与诊断收口。

## 7. MCP 与直接工具共同适配，协议标准化不替代业务控制

- 难点：既有内部工具与外部协议工具需要进入同一模型调用面，同时保留来源辨识。
- 证据：`/Users/xuhao/Documents/Basic/moduxserver/src/app/aiRouter/providers/modux-ai.provider.ts:143` 将 direct tools 转 AI SDK tool；`:173` 获取多 MCP 连接；`:184` 用 connection ID + tool name 命名；`:187` 转成模型工具定义。
- 取舍：协议统一工具发现/调用接口，可复用连接基础设施；仍需处理 schema 表达能力、错误映射、鉴权与敏感数据边界。
- 不能声称：MCP 自带 RAG、规划、权限审批或防注入；该入口支持 MCP 也不证明所有 Demo 可见工具均经 MCP 执行。

## 最强的负责人叙事

复杂性不是堆多 Agent：明确上下文何时加载与压缩、产物由谁负责、错误由谁判定、哪些失败应阻断、运行状态和实际产物如何保持一致。业界联系宜用模式对照，不应宣称复刻 v0 或等价某闭源实现。单次成功 Demo 只证明一次路径可行，系统质量必须通过代表性任务集、重复运行、失败归因、延迟/成本与人工修改量验证。
