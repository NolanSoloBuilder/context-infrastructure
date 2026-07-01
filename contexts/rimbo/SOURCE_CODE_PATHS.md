# Rimbo Source Code Paths

更新日期：2026-06-17

这个文件补齐 Rimbo 上下文里的“真实代码入口”。原 `imported/contexts/repos/` 主要是 2026-05-18 的仓库卡片和角色判断；后续分析 RSS、信源管理、Channel、Evidence、Memory 等实现时，应该从这里定位本机源码，再读当前代码。

## 当前结论

上下文仓已经标明了相关仓库和 GitHub 角色，但之前没有把本机源码路径作为一等入口写清楚。现在以本文为准：

- 先读 `contexts/rimbo/README.md` 理解产品上下文。
- 再读本文定位真实代码。
- 最后进入实际源码仓按路径分析，不要只依据旧 repo card 或 Lark mirror 快照。

## 本机源码位置

| 仓库 | 本机路径 | 当前用途 | 备注 |
|---|---|---|---|
| `mindspace_web_frontend` | `/Users/xuhao/Documents/Other/mindspace_web_frontend` | Web app、Sources 页面、Channel 页面、RSS dashboard 前端服务 | 当前工作区有未提交改动，分析时只读，不要无关改动 |
| `mindspace_backend` | `/Users/xuhao/Documents/Other/mindspace_backend` | 主业务后端、移动/Web API 代理、集成授权、ML backend 代理 | 当前工作区有未提交改动，分析时只读，不要无关改动 |
| `mindspace_ml_backend` | `/Users/xuhao/Documents/Other/mindspace_ml_backend` | RSS/Source/Channel 核心后端、抓取调度、source repository、agent tools | 当前工作区有未提交改动，分析时只读，不要无关改动 |
| `mindspace_app` | `/Users/xuhao/Documents/Other/mindspace_app` | React Native App、移动端信源管理、X/Twitter 授权、onboarding source 选择 | 当前工作区有未提交改动，分析时只读，不要无关改动 |
| `rimbo-work-context` | `/Users/xuhao/Documents/Other/rimbo-work-context` | 已废弃的旧上下文仓 | 只作为历史来源；新上下文写入当前 `contexts/rimbo/` |

未在 `/Users/xuhao/Documents/Other` 下找到的源码目录：

- `mindspace_local_sql`
- `mindspace_user_simulator`
- `mindspace_info_source`

这些仓在旧 repo card 中出现过，但本机当前没有对应目录。需要分析它们时，应先确认是否要重新 clone 或从远端读取。

## RSS / 信源管理优先读码顺序

1. `mindspace_ml_backend`：事实上的 Source/RSS 领域实现层。
2. `mindspace_backend`：对 Web/App 暴露的 API 代理、用户集成授权、任务触发。
3. `mindspace_web_frontend`：Web 端 sources、channel sources、RSS dashboard 交互。
4. `mindspace_app`：移动端 sources、X/Twitter 授权、onboarding source selection。
5. `contexts/rimbo/imported/contexts/lark_mirror/产品调研/信源库建设PRD.md`：产品语义和字段设计参考，不代表当前代码已完整实现。

## `mindspace_ml_backend` 关键入口

源码根目录：`/Users/xuhao/Documents/Other/mindspace_ml_backend`

| 关注点 | 关键文件 |
|---|---|
| App router 挂载 | `mindspace/app/launch.py` |
| Source ORM | `mindspace/domain/models/source.py` |
| 用户 source 订阅模型 | `mindspace/domain/models/user_source_subscription.py` |
| Source repository | `mindspace/repository/source_repository.py` |
| Source feed repository | `mindspace/repository/source_feed_repository.py` |
| Channel-source repository | `mindspace/repository/channel_source_repository.py` |
| RSS API | `mindspace/router/v1/rss_router.py` |
| RSS dashboard API | `mindspace/router/v1/rss_dashboard_router.py` |
| Source discovery API | `mindspace/router/v1/source_discovery_router.py` |
| Source discovery 子路由 | `mindspace/router/v1/source_discovery/source_routes.py` |
| Admin RSS API / 页面 | `mindspace/router/v1/admin_rss_router.py`, `mindspace/router/v1/admin_rss_page.py` |
| RSS admin service | `mindspace/service/admin/rss_admin_service.py` |
| Source feed 调度 | `mindspace/task/source_feed_scheduler.py` |
| Source feed retention | `mindspace/task/source_feed_retention_scheduler.py` |
| Channel agent source tools | `mindspace/service/agent/channel_langgraph_tools.py` |
| Tool package registry | `mindspace/service/agent/channel_agent_tool_package_registry.py` |
| 投资/信号 source anchor | `mindspace/service/agent/signal_anchor_catalog.py` |
| Gmail / Twitter 接入 | `mindspace/router/v1/gmail_router.py`, `mindspace/router/v1/twitter_router.py`, `mindspace/router/v1/twitter_io_router.py` |

## `mindspace_backend` 关键入口

源码根目录：`/Users/xuhao/Documents/Other/mindspace_backend`

| 关注点 | 关键文件 |
|---|---|
| App router 挂载 | `mindspace/app/launch.py` |
| Channel source API | `mindspace/router/v1/channel_source_router.py` |
| RSS dashboard API 代理 | `mindspace/router/v1/rss_dashboard_router.py` |
| Channel discovery API | `mindspace/router/v1/channel_discovery_router.py` |
| Integration API | `mindspace/router/v1/integration_router.py` |
| ML channel source service | `mindspace/service/ml_service/ml_channel_source_service.py` |
| ML channel discovery service | `mindspace/service/ml_service/ml_channel_discovery_service.py` |
| ML integration service | `mindspace/service/ml_service/ml_integration_service.py` |
| Gmail/Twitter OAuth | `mindspace/service/integrations/gmail_oauth_service.py`, `mindspace/service/integrations/twitter_oauth_service.py`, `mindspace/service/integrations/twitter_io_followings_service.py` |
| Integration sync tasks | `mindspace/worker/tasks/integration_sync_tasks.py`, `mindspace/worker/tasks/gmail_sync_task.py` |
| Mobile source display builder | `mindspace/service/mobile/builders/source_info_builder.py` |

## `mindspace_web_frontend` 关键入口

源码根目录：`/Users/xuhao/Documents/Other/mindspace_web_frontend`

| 关注点 | 关键文件 |
|---|---|
| `/app` route allowlist | `src/utils/router-adapter.tsx` |
| Sources 页面 | `src/app/pages/AppSourcesPage.tsx` |
| Channel sources 页面 | `src/app/pages/AppChannelSourcesPage.tsx` |
| Channel 页面 | `src/app/pages/AppChannelPage.tsx` |
| Twitter sources 页面 | `src/app/pages/AppTwitterSourcesPage.tsx` |
| Channel discovery 页面 | `src/app/pages/AppChannelDiscoveryPage.tsx`, `src/app/pages/AppChannelDiscoveryDetailPage.tsx` |
| RSS dashboard client | `src/app/services/rssDashboard.ts` |
| Source discovery client | `src/app/services/sourceDiscovery.ts` |
| Channel client | `src/app/services/channel.ts` |
| Channel sources modal | `src/app/components/channel/ChannelSourcesModal.tsx` |
| Signal sources modal | `src/app/components/channel/SignalSourcesModal.tsx` |
| Twitter sources dialog | `src/app/components/TwitterSourcesDialog.tsx` |
| Source 分类前端常量 | `src/app/lib/source-categories.ts` |
| RSS media helper | `src/app/lib/rss-dashboard-media.ts` |

## `mindspace_app` 关键入口

源码根目录：`/Users/xuhao/Documents/Other/mindspace_app`

| 关注点 | 关键文件 |
|---|---|
| 移动端 sources 页面 | `app/sources/index.tsx` |
| Channel detail | `app/channel/[id].tsx` |
| Channel sources | `app/channel/[id]/sources.tsx` |
| Channel discovery | `app/channel-discovery/index.tsx`, `app/channel-discovery/[id]/index.tsx` |
| X/Twitter 授权入口 | `app/source-auth/x.tsx`, `app/source-auth/x/sources.tsx` |
| Onboarding source selection | `app/guide/onboarding.tsx` |
| Article/source 展示 | `app/article/[id].tsx` |
| RSS dashboard API client | `service/api/rssDashboard/index.ts` |
| Source discovery API client | `service/api/sourceDiscovery/index.ts` |
| Channel API client | `service/api/channel/index.ts` |
| Source auth state | `store/useSourceAuthStore.ts` |
| Source list UI | `components/ui/context/SourceList.tsx`, `components/ui/context/SourceTag.tsx` |
| Onboarding source UI | `components/ui/onboarding/AddSourceOptions.tsx`, `components/ui/onboarding/SourceCard.tsx` |
| Agent 推荐 source 卡片 | `components/ui/agent/RecommendSourcesToolCallCard.tsx` |
| Channel source/evidence UI | `components/ui/channel/BriefSourceListSheet.tsx`, `components/ui/channel/InsightCitationPill.tsx` |

## 分析准则

- 旧 Lark mirror 和 repo card 只能作为背景；涉及“当前有没有实现”“该如何借鉴 Papr”时，以实际代码为准。
- 本地四个主源码仓当前都有未提交改动。除非用户明确要求实现，否则分析时只读，不做跨仓修改。
- 如果需要确认远端最新状态，优先 `git fetch` + 只读比较；不要 `pull`、`checkout` 或覆盖本地改动。
- Papr 可参考的重点应对照 `mindspace_ml_backend` 的 Source/RSS 实现，而不是直接套到 Web/App UI。
- Rimbo 的产品语义仍应保持 `Channel -> Source -> Change -> Importance -> Evidence -> Memory`，Papr 的 `feed/article/tag/rule` 只能作为底层采集和管理机制参考。
