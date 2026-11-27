# Personal Agent 四周学习计划

2026-11-25。按每周 5–6 小时安排，约三分之一读资料和源码，三分之二做实验。以 Meta Muse 为产品主线，用 Pi 和本地 MkAgent 理解运行时，用一个跨天委托贯穿四周。

## 阅读入口

1. **Meta Muse 架构分享**。先看官方短视频的 VM、Sentinel、审批和最小权限，再读 Tarek Sheasha 的技术原文，画出 Secure VM、运行容器、Hatch、浏览器代理、凭据服务和 Sentinel 的职责。重点追踪一次受控写操作。技术文为发布时的架构说明，调度和记忆内部实现以公开披露为限。 [官方短视频](https://www.youtube.com/watch?v=N6KTQyRFpr0) · [How We Built Safety Into Muse](https://muse.ai/blog/security-and-safety-for-ai-agents-our-approach-with-muse)
2. **产品交互与评测**。看用户如何交代长期目标、查看后台工作和接管动作。然后对比模型评测和带工具、权限与持久状态的产品评测。 [How We Designed Muse](https://muse.ai/blog/how-we-designed-muse) · [Muse Spark 1.3 Evaluation Report](https://research.meta.ai/static/muse-spark-1-3-evaluation-report)
3. **内部 Personal Agent 对照**。《从一次委派到跨天履约》看主子交互、记忆和异步三节，《点点私信 Personal Agent》看 Harness／Worker 的分工与多会话账本，《一期规划设计》看短期／长期 context，《全景调研》优先看第七至九节如何用模拟事件与最终状态评测跨天委托。 [跨天履约](https://docs.xiaohongshu.com/doc/a8fe3a1a352e9dc3c2124039ef02565b) · [点点私信技术方案](https://docs.xiaohongshu.com/doc/624a6a260627c41cbcbfbb6d5d491f08) · [Context 规划](https://docs.xiaohongshu.com/doc/2e701f85c7db9ca495258b268e89b989) · [11 月 23 日全景调研](https://docs.xiaohongshu.com/doc/68563656b646665987ecc79ff6cd3a35)
4. **小红书 Muse 对照**。Workshop 看真实工作场景和演示，一体化应用方案看会话、Workflow 与构建发布，Modux Server 文档看状态机与工具如何接入。九月手册第 4、9、18 章可复习 Hub 路由、恢复与源码定位。该手册基于当时提交，本机目前缺少文中三个仓库的 checkout。 [Builder Workshop 分享](https://docs.xiaohongshu.com/doc/ae1da6ecf32d8830ff025d027f2e240e) · [一体化应用架构方案](https://docs.xiaohongshu.com/doc/b819b6e2ce8cc4ca6599ca586f012558) · [Modux Server](https://docs.xiaohongshu.com/doc/274060c79ad7214a071658af4a4849db) · [本地 Muse 手册](../../survey_sessions/2026_09_09_muse_agent_fde_complete_handbook.md)

## 开源源码阅读顺序

| 项目 | 阅读任务 |
| --- | --- |
| **Pi + MkAgent** | 追一次 `prompt → model → tool → event → session`。从 Pi 的 loop 和 session manager 读起，再到 MkAgent 的 `packages/pi-agent-server` 看应用如何接运行时。Pi 旧仓库地址目前重定向到 `earendil-works/pi`。 [Loop](https://github.com/earendil-works/pi/blob/main/packages/agent/src/agent-loop.ts) · [Session Manager](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/src/core/session-manager.ts) · [MkAgent 本地源码入口](/Users/xuhao/Documents/Other/mkagent/packages/pi-agent-server/src/index.ts) |
| **OpenClaw** | 追一条消息怎样通过 Gateway 定位会话，再追定时任务怎样获得运行上下文、保存历史和交付结果。 [仓库](https://github.com/openclaw/openclaw) · [Gateway 架构](https://docs.openclaw.ai/concepts/architecture) · [Automations](https://docs.openclaw.ai/automation/cron-jobs) |
| **Hermes Agent** | 阅读会话启动时的记忆快照、历史按需召回、记忆写入与定时触发。用两轮新会话验证记忆增删。 [仓库](https://github.com/NousResearch/hermes-agent) · [Memory](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory) · [Cron](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron) |
| **Letta** | 用 MemFS 对照 Hermes，重点看记忆如何跨对话共享、如何检查和版本化。 [仓库](https://github.com/letta-ai/letta) · [MemFS 资料](https://github.com/letta-ai/letta-docs-md/blob/main/configuration/memory/index.md) |
| **nanoMuse** | 选读。研究跨设备委派时，追一条任务如何从设备 A 经 relay 交给设备 B，再返回审批或结果。 [仓库](https://github.com/nano-muse/nanoMuse) · [架构](https://github.com/nano-muse/nanoMuse/blob/main/docs/architecture.md) |

## 四周与验收

练习场景为「替我跟进三份模拟供应商报价，明天下午按已确认偏好给比较表」。使用本地测试工作区、模拟收件箱和模拟时钟。先用 TypeScript、SQLite 和 CLI 做可复现的闭环，已有 MkAgent 可作为观察入口。数据先分为委托、执行记录、事件、记忆四类，按需保存动作回执和交付物引用。

| 周 | 读与做 | 验收 |
| --- | --- | --- |
| 1 · Runtime | 读 Muse 安全架构和 Pi loop。画一次调用时序图，实作两种只读工具、超时和执行事件。 | 能从日志还原哪条委托触发了哪次工具调用，工具失败和预算耗尽有明确结果。 |
| 2 · Memory | 读 Hermes 与 Letta。做带来源、作用域和更新时间的偏好记录，区分长期偏好、项目约束和当次要求。 | 新会话能读到用户已确认的偏好。更正后用新值，删除后旧值无法通过该记忆检索入口召回。报价正文不会获得修改用户偏好的权限。 |
| 3 · Async | 读 OpenClaw Automations 和点点私信方案。让委托进入等待，由回复或截止时间唤醒，持久化进度和结果。 | 在等待中退出进程，重启后同一委托继续。重复回复不会重复出表，超时能提交已有结果，取消后的迟到回复不能重新开启委托。 |
| 4 · Approval & eval | 读 Meta 发出动作的边界与点点长时间异步评测。模拟一次对外回复，将批准与收件人、内容、委托和有效期绑定。做 12 个可回放场景。 | 4 个正常、4 个异步恢复、4 个权限／记忆场景。验收读最终状态和模拟发送回执。越权发送、重复发送、撤销后执行均为 0。含一次提交成功、回执尚未记录就退出的实验。 |

最后用一张时序图、一个跨天回放 Demo 和一份评测结果解释委托怎样持续、什么能记、哪些动作要确认、发生故障后如何判断已经做到了哪一步。

## 第一晚 90 分钟

1. 20 分钟读 Meta 技术文的 VM 和 Sentinel，画运行与审批的边界。
2. 25 分钟从 Pi loop 追踪一次工具调用，标注发起、结果、失败和停止事件。
3. 35 分钟用三条模拟报价事件写一段最小回放，把其中一条重复投递，检查结果里仍只有一条对应报价。
4. 10 分钟记下退出后最少需要保存的状态，以及哪一个写操作需要稳定的幂等键。

本计划已核对公开资料入口、内部方案章节和 MkAgent 本地入口，开源项目的安装及练习验收留在对应周执行。
