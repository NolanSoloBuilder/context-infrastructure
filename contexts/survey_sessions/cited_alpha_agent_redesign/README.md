# Cited Alpha 通用研究 Agent 方案

状态：设计与实施持续推进。2026-09-10 用户已授权逐层细化并实施至高标准 MVP；完整交付范围以 04 为准。总方案用于保持产品方向，已有代码与真实运行逐项验收，不将离线测试视为产品验收。

## 阅读顺序

1. [总方案 v0.1](00_master_plan.md)：产品目标、系统职责、核心数据、主要决策、首期范围、迁移与验收。
2. [分层设计与实施路线](01_design_and_delivery_map.md)：每个子方案解决什么问题、依赖什么、交付什么，以及进入实现的条件。

总方案、证据合同和产品体验子方案已形成。运行适配、报告合同、字段查看与恢复已进入实现和真实运行验证；完整研究交付与生产验收仍未完成。当前进展查看 05，产品总览查看 12。

## 设计基线

- 通用 Agent 承载研究；多信源 RAG、原文快照和字段级溯源是产品核心。
- 模板随用户要求选择和组合，不强制把短核验写成完整研报。
- 按总方案、专题方案、实现设计、实施验收的顺序推进；已有三仓未提交改动继续保留，线上运行器在验收前不切换。
- 设计决策以本目录为当前入口；历史调研保留原样，冲突时以更新后的明确决策为准。

## 已有证据

- [现有 RAG 代码评估](../2026_09_10_cited_alpha_rag_architecture_assessment.md)
- [恢复及真实产物失败记录](../2026_09_10_cited_alpha_restore_and_rag_validation.md)
- [报告产品标准](../2026_09_10_cited_alpha_report_product_standard.md)
- [通用 Agent 架构 Review](../2026_09_10_cited_alpha_general_agent_architecture_review.md)

历史代码观察、已发布功能、目标设计三者分开记录。此前“基础设施已恢复”不代表“报告质量已合格”。

## 当前子方案和实现

- [证据合同审查](02_evidence_contract_audit.md)
- [产品体验设计](03_product_experience_design.md)
- [MVP交付合同及验收矩阵](04_mvp_delivery_contract.md)

Pi核心循环、Node JSONL适配与Python宿主已实现。早期离线测试只使用模型替身；后续已经进行真实模型、原文存储、计算及分段MySQL验证，详见05的日期和证明范围。完整模型报告进入真实业务Run、跨来源续研和生产验收仍未完成，不能把这些分段结果合并称为已交付。

- [MVP实施进展及下一步](05_implementation_progress.md)
- [报告体验与产物验收](06_report_experience_acceptance.md)：三类报告样稿、六条用户旅程、原文/计算/续研/恢复的真实验收。
- [运行与队列接入设计](07_run_integration_design.md)：复用现有队列与租约，冻结执行轨道、checkpoint和交付边界。
- [运行器、工具与恢复设计](08_runtime_tools_design.md)：权威计算委托、工具恢复、生产依赖和累计预算。
- [报告生成、检查与交付实现设计](09_report_delivery_design.md)：当前合同差异、单次独立审查、修订反馈、候选冻结、表格与字段引用扩展。

- [产品与架构总览](12_product_and_architecture_blueprint.md)：从最终产物理解总体职责与分层交付。设计整理不暂停已授权的实施；每批仍按04完整验收范围推进。

- [真实业务Run集成验收设计](13_real_business_run_acceptance_design.md)：复用现有运行器接通真实MySQL、模型、GCS、检查和报告版本，明确本地认证与生产验证的边界。
- [真实运行上下文与存储成本](14_runtime_context_cost_audit.md)：分开衡量模型输入、重复存档和串行I/O，保留恢复与原文边界。
- [运行中页面体验审查](15_running_experience_audit.md)：真实JWT页面的租约倒计时、空聊天和空版本原因。
- [可恢复研究进度设计](16_recoverable_research_progress_design.md)：随checkpoint原子保存有限活动和登记计数，避免虚假百分比。
- [PDF跨来源业务接入](17_pdf_business_preflight_design.md)：正常上传和附件授权、隔离数据准备、一次真实解析与长期版本复用方向。

- [工具参数契约与无效调用审查](18_tool_contract_alignment.md)：真实limit35失败、报告结构规格和PDF修复提示的能力边界。

- [PDF解析产物复用设计](19_pdf_parse_artifact_reuse_design.md)：统一上传解析与研究绑定，保留原始分片和版本，控制并发与未知提交；尚未完整实现。

- [Run02真实草稿失败审查](20_run02_report_failure_review.md)：格式、未留痕计算、引用支持与财务推断问题；未验收草稿不作交付成绩。

- [报告内容编译与版本兼容](21_report_content_compiler_design.md)：模型提交内容，宿主生成格式和引用目录；新旧工具协议按Run冻结，正式报告继续复用既有合同。

- [跨来源业务运行与解析恢复](22_cross_source_run_and_provider_recovery.md)：真实Run失败、ADC配额项目原因、既有operation成功回读及原始分片归档；不重复付费解析。

- [留存解析页与原始 PDF 双视图](23_retained_page_rendition_design.md)：解析图上的字段高亮、原件查看及三仓授权合同，保留两个视图各自的精度边界。

- [跨来源上下文成本复验](24_cross_source_context_cost_review.md)：真实消息按工具统计及可逆投影收益，原文与 checkpoint 保留。

- [原文读取延迟与复用设计](25_source_read_latency_design.md)：真实单字段27秒冷读，逐次授权与不可变材料/索引复用的边界；尚未实现。

- [检查点 I/O 与截止失败审查](26_checkpoint_io_and_deadline_review.md)：区分模型生成耗时和调用间隔，消除纯进度回调重复整包读取，保留恢复边界。

- [生产接入与容量隔离](27_production_integration_design.md)：实际身份、并发槽、配置及生产验收差距；待实现，不以本地token组合替代。
- [运行中报告体验细化](28_running_report_experience_design.md)：真实活动概述、按需统计与报告空态；保留旧版与失败语义。

- [生产执行与控制容量决策](29_production_capacity_topology_adr.md)：最多新增一个ML控制部署，隔离长执行与review/原文读取；最小身份和连接配置，尚待实现与容量验收。

- [PDF页面阅读与字段引用分工](30_pdf_page_reading_design.md)：固定20字段导航的实际成本、页概览合同与离线原型；原型单份48KiB可容纳已测财务页；集成按完整工具envelope计量分页，保留字段与坐标。

- [检查点传输生命周期设计](31_checkpoint_transport_design.md)：有界独占客户端、真实线程取消与关闭边界。
- [Run04终态与后续改进](32_cross_source_run04_terminal_review.md)：42条证据与4项计算已保存，未交付报告；完整耗时和只读连接对照。
