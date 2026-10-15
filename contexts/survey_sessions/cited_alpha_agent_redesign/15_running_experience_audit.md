# 实际 running UI 状态审查

2026-09-11；只读源码，未请求模型、未更改运行中服务、未取消Run。业务目标workspace-1342c9bc-012e-48c5-9a3c-3cc5dd21a0f2。以下 B=/Users/xuhao/Documents/Other/mindspace_backend，W=/Users/xuhao/Documents/Other/mindspace_web_frontend。

## 1. “Working elapsed 从进页面计时”目前不能按源码确认为产品计时 bug

在当前 W/src 中全文检索 elapsed/startedAt/startTime/Date.now/setInterval，没有找到研究Run elapsed组件。已找到的实际渲染路径：

- W/src/app/pages/AppWorkspaceDetailPage.tsx:1616 选取recoverableRun；1631通过useWorkspaceRunObservation轮询真实Run，onSnapshot合并；终态1638刷新Workspace及聊天。
- 同文件3341将状态与summary传给WorkspaceRunRecoveryBanner；运行中默认文字来自conversationRunning，即Working...。
- W/src/app/components/workspace/WorkspaceRunRecoveryBanner.tsx:1：没有elapsed/start时间props或时钟。该组件能渲染数字的只有retryAfterSeconds。
- W/src/app/pages/AppWorkspaceDetailPage.tsx:1655-1671：唯一该页秒级timer是将server retryAfterSeconds拷贝到本地然后倒数，不是已用时。
- B/mindspace/service/workspace_payloads.py:480 输出createdAt，481输出finishedAt，没有在基础payload输出startedAt。

因此58秒若是“递增elapsed”而不是重试倒计时，当前证据不支持认定此源码实现错误。请root确认数字的DOM节点/所属浏览器页面；可能来自外层执行器UI、另一预览构建或其它计时层。不要直接改RecoveryBanner倒计时来修“elapsed”。

若产品需要新增真实耗时：明确指标是自admission排队至今，还是实际execution开始至今。前者用真实createdAt/finishedAt；后者需稳定startedAt后端字段（不能用每次lease acquired或当前页面mount）。用服务端时间锚点+客户端tick，刷新不归零，终态停止。此为能力缺失建议，尚不是已定位到58秒的bug。

## 2. 聊天为空：后台admission接入差异已确认，同时暴露恢复体验缺口

- /tmp/cited-alpha-business-run-canary/business_routes.py:32-38：harness走真实POST /workspaces，随后POST /workspaces/{id}/runs。没有走/conversation/stream，也没有调用聊天消息persist。
- B/mindspace/router/v1/workspace_router.py:900-929：POST/runs确保chat session绑定，然后create_run(background_research)，并不持久化user聊天消息。
- B/mindspace/domain/dao/workspace_research_admission_dao.py:45-52校验chat归属，103附近将chat_session_id写进Run；整个admit方法只创建Run/Event/Outbox/可能空artifact，没有ChatMessageModel写入。
- B/mindspace/service/workspace_run_message_finalizer.py:58-64只允许终态，72起构造assistant消息，97调用persist_message_once。因此running阶段没有终态assistant是正常的。
- W/src/app/pages/AppWorkspaceDetailPage.tsx:2160-2184加载真实chat history；仅historyMessages.length>0时填聊天。没有从后台Run.question生成任务卡片。

结论：空聊天不能说明模型没执行，也不是聊天GET一定失败；本次是合法后台入口没有会话user message。当前harness尚未验收“用户在Web输入→conversation持久化”的端到端入口。

最小建议：
- 当前running Run不要补写伪造历史，更不要重发问题触发第二模型任务。
- 这次可在恢复界面用真实Run中的问题/Workspace Goal呈现“后台任务”卡片，明确非聊天消息；属于产品恢复体验优化。
- 下一次检验会话输入路径时改用真实conversation入口或它已有的服务流程，不能harness手造assistant/Run状态。
- 后台运行是否也要求保存规范user消息，应作为API产品合同决定，由Backend正常service原子/幂等保存，而非Web本地缓存生成证据。当前API自身确实不做这件事。

## 3. No version：空V1被有意隐藏，文案不够准确；不是报告版本丢失

- B/mindspace/domain/dao/workspace_research_admission_dao.py:77-87初始化私有研究草稿，current_version=1、content=''，没有report_schema_version。它只是目标占位，不是生成报告。
- W/src/app/pages/AppWorkspaceDetailPage.tsx:305-317：primary artifact、version<=1且content为空，即认定placeholder。
- 同文件330-336：getVisibleWorkspaceArtifacts过滤掉placeholder，默认active artifact变成null。
- 同文件2187-2193：documentBaseVersion取可见artifact；没有可见artifact得到null。
- 同文件1814-1823 / 4163：null对应No version。

所以底层V1存在与页面No version是同一套有意占位隐藏规则，不因schema=null本身，而是primary+V1+empty内容组合。真正报告完成会写V2，过滤条件version>1立即放行；终态onSettled会刷新Workspace。

最小修复建议是产品空态：有queued/running researchRun且没有已交付报告时显示“报告生成中，尚未形成可查看版本”，并展示可回读任务状态；不要把空V1放出来假装报告，也不要改变版本号来绕过滤器。若V2已成功而仍No version，再检查真实Workspace latestVersion映射/终态刷新，才是交付显示bug。

## 本次优先级

1. root定位58秒真正DOM，不误改倒计时。
2. 保留正在执行Run，让真正终态验证V2和finalizer聊天出现。
3. 把“后台创建Run→刷新后空聊天+No version”的无信息恢复状态纳入产品优化；事实来源是Run/Goal/真实progress，不能引入模拟输出。
4. 本次paid后台链路与下一轮真正Web提交会话链路分别验收，不把其中一条当两条都通过。

## 追加：已用真实API定位43→58秒的机制

root补充真实DOM含两行Working...与Working...(43s)，随后58s。授权后使用18873同一真实userJWT读取Run（token未输出）：code0/status running/retryAfterSeconds=50/resultSummary=null/statusMessage=null。由此已闭环，前述“尚未定位数字归属”已解决：

1. B/mindspace/service/workspace_payloads.py:491-504：retryAfterSeconds = ceil(lease_expires_at - datetime.now(UTC))。这是**lease剩余秒数**。
2. B/mindspace/service/workspace_run_lease_heartbeat.py:27默认20秒，51-60循环续租Run与Step。
3. W/src/app/hooks/useWorkspaceRunObservation.ts:31-32 每5秒poll。
4. W/src/app/pages/AppWorkspaceDetailPage.tsx:1655-1671 每次Run.retryAfterSeconds变化就重置本地倒数。
5. W/src/app/components/workspace/WorkspaceRunRecoveryBanner.tsx:56-58 将retryAfterSeconds与busyLabel组合；调用方busyLabel=Working...。于是lease续租后“43秒→58秒”，看似elapsed实为锯齿重置的技术倒计时。

**已确认产品呈现缺陷：将运行中lease剩余秒数直接显示为Working...(Ns)，会误导为已耗时/剩余完成时间。不是页面mount初始化elapsed的错误。**

最小修复：active/running状态不要展示retryAfterSeconds数字；failed且确有重试冷却才显示“可在N秒后重试”等明确文案。等待用户输入也不应显示lease秒数。保留后端lease/CAS机制，不能为UI调整续租。

若确需耗时另加真实计时，先修时间合同。此次实际API还发现createdAt="2026-09-11T11:15:12"，deadlineAt="2026-09-11T03:45:12"，均无timezone。任务真实03:15UTC开始，对应createdAt看似数据库本地+08时间。未查询SQL timezone，不能直接确认全系统时区bug，但**不应拿这个未带时区createdAt直接当UTC新增elapsed**。需核对MySQL session/default timestamp与_serialize_datetime，再输出统一UTC带Z/offset；本次无修改。

## 最小修复已实施，待root浏览器复验

仅修改W/src/app/components/workspace/WorkspaceRunRecoveryBanner.tsx，新增同目录WorkspaceRunRecoveryBanner.test.tsx，README已有dirty部分保持原样，仅追加“Run租约与恢复倒计时”。active/waiting隐藏lease数字；failed且有Continue回调时显示Continue(Ns)。原disabled与回调语义不变，busyLabel prop仍兼容唯一页面消费者。不涉及API或elapsed。

focused测试5项通过；首轮测试因本仓测试环境未自动cleanup导致用例DOM互相残留，补显式afterEach(cleanup)后全部通过。git diff --check通过。未提交、未推送、未改其他dirty文件。root负责真实Chrome页面回读。后台入口聊天为空与空V1隐藏均未通过本次fix“填充”，保持上述证据边界。
