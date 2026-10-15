# 跨来源业务运行与已付费解析恢复

日期：2026-09-11。实际运行记录；完整MVP仍未验收。

## 当前结果

跨来源任务要求结合Tesla 2024 Form 10-K与已上传Q4 Update分析收入、盈利、现金流及汽车/储能业务，保留字段引用与派生计算。正常Workspace conversation SSE已接纳，真实Outbox consumer执行。使用本地隔离MySQL/PG与真实GCS/Document AI；内部认证是本地token，不能作为生产OIDC证据。

`/tmp/cited-alpha-cross-source-business-01`仅在Backend启动配置校验失败，数据库核对零Run，无provider调用。修复临时配置后，`business-02`接纳`workspace-run-2a9dc7fa0c0d4086a5b7b1da93f5a00f`。

该Run实际终态failed，原因`research_failed`，消息`document_capture_outcome_unknown: automatic provider retry forbidden`。独立MySQL/GCS回读checkpoint 1，工具协议v2，模型及工具调用均0，document capture为intent，无报告候选。旧任务保持原终态，不改写为成功。

## 云端解析并未失败

一次batchProcess已返回operation `6488767485854092832`。后续GET被403拒绝：本地Application Default Credentials缺少quota project。仅在读取进程设置`quota_project_id=cited-alpha-20260701`后，实际GET确认done=true、state=SUCCEEDED。

只读恢复精确定位该operation的`/6488767485854092832/0/`输出目录，按GCS generation读取4个原始分片，页号完整覆盖1–36。provider输入原件与正常上传原件逐字节一致，SHA为`05dfde334f800ec5f0ee140c0dd78409f24ad775e11a0c68f8a6b534b04cafdc`。未重复POST。

原始分片与输入/operation/generation/hash关系归档于`../../source_materials/cited_alpha_cross_source_tesla_2024/batch_operation_6488767485854092832/`。恢复脚本和临时接入位于`/tmp/cited-alpha-cross-run-7YGKhq/`。

下一步使用该真实解析结果，通过现有normalizer和DocumentVersionService封存，再由同owner新独立Run继续报告验证。恢复不预填研究答案，不跳过当前附件授权、原件哈希或报告检查。这是明确的临时恢复组合；19所述生产统一解析产物复用仍未实现。

## 页面原文接入

Backend新增可选`research_document_client`构造参数，由两个研究原文resolver使用，默认依赖不变。实际owner/citation/字段验真仍经过原服务；HTTP不接受客户端选择。提交`3f14ce4e8035adfa7d6df3dae134d83eb9d50c91`已推送，本地离线303 passed、1 deselected、14 warnings。

独立UI API18885和Web18910使用正常JWT、真实DAO及该客户端注入；Root Chrome已看到真实失败任务，无正式报告。PDF引用完整点击仍待新报告。频道发现侧栏明确不可用，不伪造空结果；内部本地连接不替代生产验证。

## 已核对的CI

ML `4b12278`的CI34562908293已success；Backend `6ebce93`的CI34562912154已success。后续DI提交的CI需单独核对。测试通过与实际报告失败分别记录，不能互相覆盖。

## 附件与文件身份修复及新任务

跨仓核对发现Backend使用真实`fileItemId`，ML却将其与原件`fileId`比较；旧fixture两者同值掩盖了问题。修复后授权对象分别携带两者，文件版本只绑定真实fileId。当前附件权限仍由Backend DAO核验，未删除校验或增加同值兜底。

ML提交`8200d056031f89cab7356d7e92e7bf33863011af`，本地296 passed、2 warnings；Backend提交`10b767cf0793d1bfb01c577f78a53f816d251286`，本地303 passed、1 deselected、14 warnings；另有一项实际跨仓构造兼容检查通过。两仓已推送，当前CI分别34563727564与34563736968。DI前一提交3f14ce4的CI34563442478已success。

新任务输出`/tmp/cited-alpha-cross-source-business-03`，通过正常SSE接纳`workspace-run-95b62390855242a98c43937d9e3a977c`，原截止时间UTC 2026-09-11 05:21:01。执行器PID75896、ML PID75907；launcher session59487。上述HEAD为实际加载代码基线，旧dirty改动仍保留。

本次显式选择`--reuse-recovered-provider`，使用真实原始shards和现有normalizer；没有新的batchProcess意图。封存前离线freeze/load_verified已验证，provider canonical JSON 33,636,011 bytes，manifest 12,042,923 bytes，均小于80MB上限。线上封存、模型报告和检查结果仍以该任务后续回读为准。观察中断时继续检查同一handle，不因未见最终报告重新启动。

## 当前模型阶段与实现检查（UTC 04:55）

当前HEAD对应的ML CI34563727564与Backend CI34563736968均已success，head分别为8200d05与10b767c。仅说明当前提交通过离线CI。

独立进程读取实际MySQL指针与GCS原始checkpoint并验证scope/hash：sequence23，research-tools/v2，PDF捕获completed，模型5次、工具5次，登记证据0、计算0，尚无检查通过的候选。报告任务仍running，consumerDone=false；不将资料捕获完成当作报告完成。

Chrome在既有工作区刷新后显示Working及真实研究进展，没有新建Run。旧失败记录仍保留，当前报告为No version。这次回读证明刷新能够恢复观察活动任务，尚未证明完成后的版本切换或原文点击。

终态后的只读ML服务已准备在临时harness的ml_readonly_app.py，未启动或占用当前18884；仅真实read-verified和鉴权health，6项离线路由检查通过。须待当前paid worker终止、端口空闲后启动，再验证PDF引用。

## business03 终态（2026-09-11 UTC05:21）

原deadline 05:21:01到期，launcher实际exit1，consumerDone=true，Run failed/deadline_exceeded，reportVersionId=null。独立MySQL指针与GCS回读checkpoint146：35模型、36工具、33证据（32 SEC cell与1 PDF field）、3计算，无checkedCandidate。PDF capture已completed；通用错误消息提及可能pending的capture不代表本次已完成材料重新变为unknown。两个付费worker退出，未重发。

此次没有正式报告，不能作为跨来源产物验收。原始状态、计数和SDK usage见[cross_source_run03_acceptance](cross_source_run03_acceptance/)。已保存证据与计算留待恢复设计和后续真实运行使用。新留存解析页代码与PDF模型投影均未加载到此次付费执行。
