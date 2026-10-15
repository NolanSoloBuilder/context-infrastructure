# Run04 PDF页级精读：独立只读设计

## 结论

应把“给模型读懂页面的视图”和“可审计的字段证据记录”分开。当前工具按20条OCR记录分页，不是按人能理解的页、段落、表格行分页；大量坐标与重复身份字段占据上下文，而表头和数字被拆开。简单调大limit可以减少调用，却仍保留这个结构问题。

最小方向：新增显式页概览阅读模式，以完整页面文本布局＋稳定字段ID呈现；有真实表结构时提供完整表头和行，有缺失表结构时提供如实标注的空间布局视图，不伪造语义表。随后沿用既有 cite_document_field 对原始字段精读并登记证据。概览不自动成为事实，不自动登记所有数字，不注入Tesla问题答案。

本审查不改应用、运行工具定义、提示词、模型数据、数据库或服务，不调用模型/DocAI。当前Run04继续使用原协议。

## 1. 已核实的瓶颈

源码：`/Users/xuhao/Documents/Other/mindspace_ml_backend/mindspace/service/research_agent/immutable_document_tools.py`。

- definitions中read_document仅document_id/page_number/offset；**没有limit参数**，不是“默认20、最大可调”。execute硬编码`rows[offset:offset + 20]`，next_offset也是20。
- `_rows`先所有lines，再table_cells，最后spans，并非页内统一阅读顺序；每条text截到1000字符但未返回截断标志。record还包含bbox、同一document/line/page身份、reading_order等。
- 搜索只做词面匹配；找中段落或金额不等于证明数字口径。
- `cite_document_field`仍可完整读取原字段（20,000字符上限），构造带完整同页上下文的证据；page context>200,000 bytes拒绝。这是现有引用合同，不能因概览体积优化暗中截短。
- `_load`检查授权文档集合、版本hash/user/workspace等，并通过load_verified验证原件/provider/manifest、重放normalizer，单个实例内复用。导航视图必须从这个已验证结果生成，不能另开mutable文档表或跳过source校验。

checkpoint `/tmp/cited-alpha-cross-source-business-04/independent-checkpoints/72.json`只读取toolCall/toolResult：p4 offset0/20/40/60/80，p5 offset0/20/40/60/80/100/120/140，合计13次；全部isError=false。p5 offset140仍next_offset160，开始越过line层进入span层。实际每20条工具正文约11.5–11.9KB；混入span的offset140约18.9KB。这是成功但低效的导航，不是错误重试。checkpoint中工具结果还带独立的约302字节附加文本块，体积计算没有将其误当页面字段。

## 2. 离线实测

脚本 `/tmp/run04-page-read-audit.py`，结果 `/tmp/run04-page-read-size-results.json`。从原有36页解析provider归档 `/tmp/cited-alpha-cross-source-business-02/recovered-provider-readonly/providerDocuments.json` 离线重放当前adapter；使用实际document ID保持ID长度一致，不生成新版本、授权或provider执行记录。

| 页 | lines | spans | tables / cells | 按现工具翻完所需调用 | 全fields JSON bytes | 仅完整line text+kind+稳定ID bytes |
|---|---:|---:|---|---:|---:|---:|
| 4 季度财务表 | 144 | 139 | 0 / 0 | 15 | 225,336 | 14,393 |
| 5 年度财务表 | 144 | 137 | 0 / 0 | 15 | 223,426 | 14,401 |
| 7 季度运营表 | 109 | 107 | 0 / 0 | 11 | 172,702 | 10,968 |
| 8 年度运营表 | 109 | 103 | 0 / 0 | 11 | 168,593 | 10,970 |

p4/p5完整line文字分别只有1,253/1,261字符。上述字节是Python标准json ensure_ascii=False序列化，不是token估算、不包含结果外壳，也不宣称实际模型延迟减少比例。短ID试算会低估体积，本表已改用实际ID长度。

重要：仅把所有line数组一次吐出仍不够。p5前20条中先出现多个指标标题、然后2020..2024/YoY、最后才27,236。p8甚至部分数值列序交错。provider阅读序本身未把二维表恢复为逐行语义。必须保留这种不确定性，不能在不存在table/cell时生成“权威row/column”。

## 3. 最小工具合同建议

在新工具合同版本中给现read_document增加显式`view: page_overview | raw_fields`（或独立read_document_page；二者只选一种，避免重叠工具）。旧合同维持现有定义和默认行为；新Run经host选择版本后可默认page_overview。不要对正在运行的checkpoint热换默认。

page_overview参数只需document_id/page_number，可选region_id与分页cursor；不要要求模型输入预期指标值、quote、身份或storage URI。返回：

- document_version_id、page_number、view_version、citable=false。
- regions：完整段落、真实表、或spatial_text区域。每个区域有本版本内稳定region_id；每片原文携带原始kind/id，不使用文字匹配重新找回字段。
- 有真实table_cells：按原row_index/column索引及span呈现，保留多层表头、合并格、单位与脚注引用；若单元格没有已证明header关联，仅展示物理表位置，不宣称typed metric/period。
- 没有真实table_cells（本次p4/p5）：display_kind=spatial_text，按同provider页坐标生成保留二维位置的行带/文本块视图。可把稳定fieldID、原文、简化bbox或列锚点一起返回；仅作为导航布局。额外的行带分组标记derived_navigation，不写回normalized，不产生新的证据字段或期间推断。
- 单页公共标题、单位、日期、脚注原文在每个续页窗口保留其原ID；跨页脚注/表延续若不能建立明确关系，返回未解析状态，不猜接。
- counts、coverage（哪些collection/region已显示）、truncated及omitted_field_ids或有界continuation。不能把“浏览代表层line”冒称整个normalized已全部显示；span仍按需可达。

推荐首版硬界：单响应UTF-8 32KiB、最多300个导航字段；按完整段落或表行拆分并重复表头/单位，而非第20词处截断。若一个字段本身超过预算，显式返回full_text_available=false及精读入口，不输出可误当完整的片段。每个边界先按序列化结果验证，不把token数猜测当硬保证。

本次144个line加字段ID约14.4KB，合理增添空间布局仍有希望一页一次读取；必须离线实测后才确认32KiB适配。不要为了达到一次读取而丢字段/脚注或把ID隐式换成全局不唯一短名。若用页内短alias，须有host固定映射＋版本/page作用域并测试恢复，不建议首版增加此复杂性。

概览之后：模型选具体field ID，既有cite_document_field已同时做完整精读与登记，不必新造语义相同的read_field工具。若后续实测仍有多次独立引用调用瓶颈，可另设计有界批量引用，原子提交/预算/逐项失败语义先明确，本轮不是前提。

## 4. 二维布局的严谨边界

不能直接把OCR bbox排序后声称表结构正确。最小可用显示应保持原始fragment+坐标，空间分组只改善排版，不改变字段语义。异常页旋转、重叠、列宽不一致、跨栏、多行标题、小数/负号拆分应保留原片段并标注ambiguous；不要按金额相同去合并。真实表格结构缺失时，可提供已验证retained_provider_page图片供支持图像的阅读通道查看，但应使用现有安全图像表面合同，不能临时改原PDF坐标或为文本工具秘密启用多模态。

长期若需要稳定逻辑表格，应把表格恢复作为显式版本化解析增强：输入保留provider/PDF，输出带来源fragment映射的结构及不确定状态。新解析产物生成新版本，原始provider和原件均保留。该增强是比首版导航视图更大的工作，不能悄悄改变当前manifest的字段ID、normalizer回放或旧证据hash。

## 5. 具体最小文件范围

- 新 `mindspace/service/research_agent/document_read_view.py`：纯函数，输入已验证normalized+版本+page，输出受预算限制的导航projection；无IO、无LLM、无答案模板。
- `immutable_document_tools.py`：新协议定义/路由选择、view输出；旧cite/_entry及旧raw_fields保持；允许精读原稳定ID。
- `research_session.py`/`execution_service.py`工具构造与checkpoint合同版本选择：新增版本时显式传递。当前research-tools/v2已存在报告内容协议，不能以“只改PDF”理由偷偷改变恢复语义。建议新版本或独立documentReadViewVersion持久化；选一种统一策略，由Root整体决定。
- 新专用离线view tests、真实归档fixture review与README；CI清单由Root审查登记。
- Backend正常无需改证据授权/验证合同；若持久化toolContractVersion新增枚举，Backend checkpoint validator/占位创建逻辑必须同步接受新版本，先部署双版本读取支持再启用。

## 6. 可逆与不可逆边界

可逆：仅新增纯导航projection、保持现有字段与证据合同；旧Run按原版本继续；新Run可在创建前切回旧版本。新模式出错返回明确受限结果，不能自动降级为省略验证。

不可直接回滚：已保存新工具调用/结果的checkpoint不能交给不理解其协议的旧runtime继续。要保留双版本支持；不能强改pendingEffects或已生成Evidence/ReportVersion。重新解析/改变normalized IDs/重算既有证据hash不属于导航优化，需新不可变版本与显式迁移，不原地覆盖。

原始PDF/provider JSON/manifest完整归档不变；模型看不到重复metadata不意味着存储与引用可以不保留它们。每请求Backend授权仍保留，ML版本与scope检查不省略。view选择不允许越权发现其他文档页面。

## 7. 零模型验收条件

1. p4/p5/p7/p8真实归档：全部line原文和ID可无损从概览取回；新view同ID调用旧cite所得entry逐字一致；不存在虚构table/cell。目录/脚注也完整可达。
2. 正文页p6不重复展示line和span全文；coverage如实说明代表层。line缺失而span存在的fixture不能变成空页。
3. 真结构表、多层/合并表头、行名换行、跨页续表、单位脚注，验证预算分页不拆散关键条件；不足则明确待确认。
4. 多个相同金额不同期间/位置必须保留不同ID，不按text去重；OCR错字、拆负号不能被“纠正”为新原文。
5. 旋转/重叠/多栏/无bbox页不能推断错误顺序或typed数值。spatial_text布局与retained image视觉抽检，绝不声称原PDF字段框。
6. 超32KiB/300字段、超长单字段、空页、非法cursor、跨版本cursor、越权doc/page全部有明确行为；预算拒绝无悬空证据ID。
7. 旧checkpoint工具schema和raw_fields行为完全相同；新checkpoint恢复得到相同view及ID映射；unknown版本在provider初始化前拒绝。
8. 性能指标先用离线真实页：读到全表的调用数、响应字节、原文覆盖率、准确定位率；不能只看工具成功率。后续真实模型对照运行才判断证据登记速度和最终报告质量，本轮不做付费实验。
