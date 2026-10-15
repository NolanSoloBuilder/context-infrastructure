# 跨来源 Run04 终态记录

本轮未交付正式报告，MVP 仍未验收。真实数据库终态为 `failed / research_failed`，错误为 `research execution did not acknowledge completion`。Backend transport 在 ML HTTP 非 200 时使用该错误，不能仅据此改称 `deadline_exceeded`。终态 `reportVersionId=null`，现有 version 1 是 admission 初始化空稿。

独立进程从真实 MySQL Step 指针读取 GCS，并验证 scope、规范字节和完整 SHA：最后有效 sequence 190，4,029,869 bytes，34 次模型调用、59 次工具调用，42 条登记证据、4 项计算，没有 checkedCandidate。证据登记数不等同于审查通过。59 个 pendingEffects 均已 completed。原始模型消息仅保留在私有临时目录，未复制到文档仓库。

最后有效保存开始于 UTC 06:10:40.214，约 12.396 秒完成；随后下一回调读取 sequence 190，上传了候选 sequence 191 对象，但回调报 ValueError，真实 DAO 指针保持 190。既定 deadline 为 06:10:55。观察与最后写入跨过截止时间一致，但目前没有具体异常正文，不能直接断言 ValueError 的唯一原因。不可把已上传但未被 DAO 接纳的对象当作恢复点。

完整 timing 日志共 579 条：195 次 load、191 次 save、189 次 checkpoint callback、4 次 calculation callback。checkpoint load/save 时间区间并集约 1,408.54 秒。callback 包含内部 load/save，不能重复累加。这些数据支持先减少读取轮次与传输开销；并不证明所有开销都来自 token 刷新。

同一终态检查点进行了五次顺序、只读真实对照：每次新建连接约 4.920、5.122 秒；复用连接第一次约 3.926 秒，后两次约 3.536、3.437 秒。每次均完整验证 scope/hash。样本只代表本地 ADC、当前网络和约 4 MB 对象，尚未验证生产并发收益。无新模型、解析或 GCS 写入。

后续实施：页面级阅读 v3 保留字段原文、ID 和未舍入坐标，以完整工具返回 envelope 48 KiB 限制分页；v1/v2 保持原调用语义。检查点仅复用有界独占 HTTP 传输资源，继续逐次校验 scope/hash/CAS。新真实运行沿用完整研究问题和验收标准，不扩大预算掩盖问题。

相关证据位于 `cross_source_run04_acceptance/final-terminal.json`、`final-independent-checkpoint-readback.json`、`final-performance-summary.json`、`final-checkpoint-read-transport-benchmark.json` 及 timing 原始记录。工作进程均已由 launcher 退出，无在途付费 Run04。
