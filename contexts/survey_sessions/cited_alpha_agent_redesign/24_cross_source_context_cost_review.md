# Business03 上下文占比与最小优化

结论：当前大头是逐轮保留的PDF字段和SEC表格读取结果，不是研究方法。应首先合入已做离线可逆验证的PDF模型副本投影；它保持全部原文字段/坐标/页上下文，不需要摘要、截断、重新检索或改变Agent执行流程。仅靠该优化还不能解决全部20万token规模，SEC表格事实载荷是下一项需独立测量的结构优化。

## 快照与统计边界

本次读取时最新独立checkpoint已由130变为137。以下固定checkpoint137：33 modelCalls、34 toolCalls、67 messages；SDK审计有33个已响应请求，最近一次prompt211,569 tokens，累计prompt3,349,371 tokens。SDK审计与checkpoint不是原子快照，不把序号强行一一配对。只统计SDK usage、message角色/工具名/序列化大小与toolResult结构；没有输出或分析thought/signature内容。

SDK前几次prompt2134→3447→3859→5733；第5–18次约每轮新增7千余tokens，第30–33次201011→205925→209649→211569。保存的PDF结果每次20条line，280条共14批，支持重复字段元数据逐轮累积这一原因；没有实际model wire逐token归因，因此不能断言全部增量仅由PDF造成。完整transcript重新作为上下文发送会让早期每条结果被重复计入后续prompt，不只是本轮新增成本。

## checkpoint137 canonical消息字节

|角色/工具|次数|bytes|全部消息占比约|
|---|---:|---:|---:|
|read_filing|9|191775|35.5%|
|read_document|14|189404|35.0%|
|cite_filing_fields|3|93419|17.3%|
|assistant，仅统计整消息尺寸|33|50517|9.3%|
|search_documents|2|6725|1.2%|
|cite_filing_field|2|4392|0.8%|
|cite_document_field|1|1644|0.3%|
|read_research_method|1|1175|0.2%|
|find_filings|1|949|0.2%|
|user|1|481|0.1%|

消息数组总540549 bytes。数字为JSON bytes，不能当tokens；toolResult文本内JSON又被消息JSON转义，统计层次不同会有开销差异。

当前已启用的SEC cite_filing_fields model_context_projection把3批工具消息93423→48057 bytes；checkpoint中的原始93423仍正确保留，不应误认为当前请求尚未优化。不能通过改checkpoint压小来修这一问题。

## PDF纯请求副本实测

复用 `/tmp/cited-alpha-pdf-model-view/prototype.py`，对14个实际PDF结果全部命中严格line已知形状。保留每条完整id/text/bbox/block_id/confidence/line_number/reading_order；本页共享document_id/page_id/page_number/kind、line_id=完整id规则。字段坐标、负号、小数、单位和脚注文本不删，预算块不改，没有新增ctx引用跳转。

- PDF消息189419→113881 bytes，减少75538（39.9%）。
- 全部toolResult经当前SEC投影后444164 bytes，再加PDF投影为368626 bytes，减少17.0%。
- 固定assistant/user内容不变时，整个消息请求副本由约495183→419645 bytes，减少约15.3%；不是对整个Vertex请求或token的实测比例。
- 280个line的text值合计5454 bytes，record值合计121715 bytes。这个差异说明主要是定位结构开销，但不能因此删record：它承载精确引用与版面语义。

前一轮3批样本已完成6次对象/列数组round-trip和10类负例。此次扩大到14批仅做体积与形状命中测量；若合入必须将全14批纳入round-trip和实际final-wire测试，另加unknown/error/扩展metadata原样及checkpoint不变断言。对象方案比列数组更自描述；不能把OCR line列表重排成猜测的财务表格。新函数放在既有model request deepcopy入口，不动模型工具定义和原数据存储。

## 下一项：SEC read_filing，先区分真实事实与重复结构

9个结果中8个为JSON结构、1个非JSON保持原样。已知结果共有79个表格block、10个段落block、303个cells。blocks值132008 bytes，其中cells107565；cells的xbrl_facts值65050 bytes、text3988、column_headers1884。source_contexts另20269 bytes。现有read_filing已提取source_contexts，不能重复造第二套source跳转。

下一步只考虑严格已知cell/fact的可逆字段列布局或在当前已有source_context内合并完全相同的事实元数据。期间、单位、维度、decimals、namespace、脚注及所有冲突候选必须保留；xbrl_facts占比大不是可删除的理由。先统计完全相同项的重复率，若主要是独有事实就不要为了字节目标另建引用图。此项本轮未实现、未宣称收益。

## 长期边界

1. 单一canonical checkpoint保存全部消息、原文、field IDs、pending effects与预算。model projection是确定性的请求副本，恢复后从同一canonical重新生成。
2. 保留完整可见上下文，不做隐式摘要/窗口裁剪，不删除已读的条件、脚注、冲突或“已用过”的证据，不把未来可检索替代本轮已经看到的事实。
3. 不修改signed assistant内容，不把字段精简注入持久evidence。只改已知成功toolResult；未知、错误、扩展结构原样。
4. 请求级结构优化无法保证减少研究轮数。是否增加显式“读取并登记”应由既有工具合同与质量对照决定，不能把压缩问题升级成固定金融workflow。
5. 生产服务应以已验证不丢信息的projection为基础，再单独评估供应商cache等成本能力；cache不等于降低上下文窗口、延迟或提升报告质量，本轮未研究/启用。

统计脚本 `/tmp/cited-alpha-cross03-context-stats.py`，数字结果 `/tmp/cited-alpha-cross03-context-stats.json`。无仓库/worker/Run修改，无模型/provider调用。当前Run继续使用启动时加载实现，不将这里的原型计作其实际token改进。
