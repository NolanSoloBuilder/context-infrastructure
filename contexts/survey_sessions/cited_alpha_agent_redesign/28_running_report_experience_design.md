# 运行中研究体验最小修订（只读方案）

依据03“左研究/主区域报告、审计元信息按需”、06“运行状态与交付状态分开”、12“通用Agent按需行动、业务状态唯一权威”。不新增阶段状态机，不把登记量解释成完成度。

## 现状与最小修订

1. `ResearchProgressSummary.tsx` 当前默认渲染 Latest activity + 两项登记数 + review免责声明，导致运行卡被实现细节占据。保留真实activity为一行“最近活动：阅读来源材料”，计数和说明放原生details/summary“研究详情”，默认收起。0仍可在展开后如实看到，null不显示；无合法progress时不制造活动。不要把活动标签换成进度条或第N步：活动可能反复切换。
2. `WorkspaceRunRecoveryBanner.tsx` 当前active用整块sky背景+AlertCircle，而isBusy只代表取消/续研请求，不是Agent运行。active改中性细边框紧凑状态行，保留取消；不要把isBusy转成虚构运行状态。失败/等待保留现有告警语义与恢复动作。运行概要“研究进行中”加最近活动即可；若summary含真实业务信息，不因样式优化删除。失败时activity只作为“上次活动”，不能让“正在检查报告”覆盖失败。时间用现有事实，不展示假剩余秒/百分比。
3. `AppWorkspaceDetailPage.tsx:1824` 当前标题只按HTML/非HTML分支，故research-report也可能叫Markdown preview。新增报告读取分支：真实research schema报告标题“研究报告”；严格空内容、非来源预览、非版本加载失败、非草稿/旧版时显示“研究报告”，子标题“尚未生成报告”。保留legacy HTML/Markdown实际预览标题，不全局替换markdownEditor key。
4. 页尾现有空内容fallback`versionNoSummary`需要真实运行状态解释：queued“研究已排队。报告生成后会显示在这里。”；running“研究正在进行，报告尚未交付。你可以在左侧补充要求或取消本次研究。”（若流中实际禁止补充，则删补充要求，仅保留查看进展）；waiting“研究需要处理后才能继续，请查看左侧提示。”；failed/canceled“本次研究未交付报告，请查看左侧原因。”；无run“提出研究问题后，报告将在这里呈现。”。succeeded却无报告不能显示成功文案，应“报告暂不可用，请重新加载”并复用已有读取重试；不自行重新运行。
5. 已有旧版本则一直展示真实版本，并轻量标“当前查看版本N；本次研究尚未交付新版本”，不能用空态遮挡旧文档、不可冒充实时草稿。初始化版1如有真实placeholder正文，不得用关键词猜它不是报告；本轮只对明确空正文/无结构产物分支修改，placeholder识别需独立显式合同。

## 精确范围

- components/workspace/ResearchProgressSummary.tsx：activity文案+可展开计数，不动readResearchProgress解析。
- components/workspace/WorkspaceRunRecoveryBanner.tsx：active视觉与失败活动语态，原按钮处理/disabled/cooldown不变。
- pages/AppWorkspaceDetailPage.tsx：documentPanelPreviewLabel/subtitle和最末空内容fallback；复用现有recoverableRun状态，不动观察hook、stream、selectArtifact、保存、发布、权限。
- i18n/messages/zh.ts、en.ts：新增report/empty/activity-details文案，collecting_evidence改“整理引用依据”/“Organizing source evidence”，不宣称已核实。registrationNote放详情内；原markdownEditor保持legacy使用。
- 对应Banner/page tests及新增ResearchProgressSummary测试；组件README追加映射边界。

## 验收

RTL覆盖details默认关闭/展开查看真实计数、null/非法progress、activity变化、失败不显示进行中、取消仍原API、旧版本保留、research报告标题、HTML/source preview保持、queued/running/waiting/failed/canceled空态。页面标题不能靠一律替换翻译蒙混。

Chrome需在独立预览使用已取得只读Run快照或fixture验收窄宽屏：默认视线为任务自然状态和报告区，登记统计收起、取消可见、左侧没有醒目蓝色技术说明。真实Run04不重启、不热改其Backend/ML，不触发新模型任务。截图仅证明显示，不宣称报告已生成。
