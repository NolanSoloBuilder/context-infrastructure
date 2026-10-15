# 报告生产故障修复（2026-09-11）

任务要求：修复流程并在产品中完成一个成功报告，按接口与持久化数据验收，不做视觉验证。

## 已复现原因

1. retry-10 修订稿旧 callback 使用标准化目录（含 rawEvidence），仅数据部分 9,449,369 字节，超过客户端 8 MiB。请求在发送前失败；此前按 rawCatalog 测量低估大小。
2. 新引用回调漏了 rawCatalog 到报告证据目录的标准化转换。已将纯转换映射放到 Backend，并使用真实 62 条证据与 ML 投影逐项深比较一致。保持原文完整性验证独立。
3. 完整修订报告包 9,069,438 字节，超过原 8 MiB 存储/审查边界；统一上限至 16 MiB。检查点连同候选约 15.01 MB，在现有 16 MiB 内。模型阅读视图约 280,131 字符，不把全部原始包送入模型。
4. retry-12 日志明确为 GCS checkpoint 写入 ConnectionError。相同 create-if-absent 对象可安全重试一次；若原写入已成功，必须通过 412 后精确字节回读确认。测试覆盖已写入但回执丢失。
5. 模型反复复制大型 JSON 会生成错误字段名。增加 retainedReportDraft 的程序化提交：原稿通过同一 durable submit_report、来源核验与独立审查，成功后直接允许 Backend 入库。未知结果仍阻止自动重放，不继承旧批准。
6. 部分重试稿含未知计算 ID。只恢复引用在对应目录中存在的候选，最多沿同范围/同问题/同截止时间/同附件版本的 8 层祖先查找。实际只读回放找回与 retry-10 有效修订稿完全相等的文档。
7. retry-14 审查 MAX_TOKENS：8192 预算中 reasoning 为 7739，结果 438。Gemini 3 审查改 LOW thinking + 16384 输出预算；审查标准不变，仍拒绝截断结果。

8. retry-15 第二次内容审查已通过，但 DAO 的 checkpoint pointer 校验仍硬编码 8 MiB，导致 14,942,132 字节候选已写 GCS 后，数据库指针拒绝更新。统一 DAO 与对象存储使用同一 16 MiB 常量，增加 9 MiB 进度数据经过实际 DAO、候选审查保存、恢复、最终交付的回归测试。

## 当前真实验收

retry-16 已成功：Run `workspace-run-f8754e6c9bf94678ab1c5550afd69058`，状态 `succeeded`。正式版本 2：`research-version-3eba590c-3f49-5be7-89a9-438bb433f502`。5 章、58 个引用节点、61 条引用证据、18 条计算记录。来源完整性、语义与编辑审查均 passed。独立进程通过真实 MySQL DAO 和 GCS 校验，确认持久化报告与获批候选完全相同；检查点 14,844,415 字节。最终重试只调用 1 次审查模型，0 次写作模型。

报告为《Tesla 2024财年财务与业务分析报告：基于Form 10-K与Q4 2024 Update的对比研究》。产品 Workspace 正文 API 已返回相同 documentJson 与版本。当前运行于本机产品环境和隔离 MySQL，采用真实模型、GCS 原文和标准 Run/交付代码；不是 Google Cloud 线上部署验收。

当前针对性回归：Backend 76 项通过，补充 DAO 大对象端到端测试后 checkpoint suite 19 项通过；ML execution/review/router 44 项通过。

## 最终接口验收

- 正文与版本列表均返回已入库版本 2；documentJson 与独立 DAO 回读完全一致。
- 58 个引用节点逐个通过认证 GET，绑定证据与计算记录完整。
- SEC HTML 表格单元格来源回读通过原文完整性校验，返回目标锚点 `research-evidence-target`。
- 上传 PDF 字段引用返回对应第 5 页；原始 PDF 11,267,189 字节，SHA-256 `05dfde334f800ec5f0ee140c0dd78409f24ad775e11a0c68f8a6b534b04cafdc` 匹配。该抽查记录显示精度 `page`，未宣称框选坐标已验证。
- 只用认证 API、真实 DAO 和 GCS 回读；未做截图或视觉验收。
- 本机入口 `http://127.0.0.1:18910/app/workspaces/workspace-67c131c6-2579-4b48-aa05-d85cdbb94637`；一次性本地登录链接交给用户。Web 18910、API 18885、只读原文服务 18884 保持运行；付费生产进程已退出。
- 修复保留于既定需求分支，未发布到 Google Cloud。

机器可读凭据：`32_success-verification.json`、`32_success-api-verification.json`。
