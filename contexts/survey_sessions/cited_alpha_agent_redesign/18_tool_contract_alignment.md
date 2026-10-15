# 工具参数契约与无效调用审查

2026-09-11。Run02仍在运行；以下修订用于后续运行，不能追溯宣称改变了本次已加载的工具。

# 研究工具参数与执行边界审查

只读，ML ae0f9e59e08d9c211541c73846710d7b760f8681，绑定原 financial-report-agent-plan-writer 分支。未修改代码/网络/模型或运行资源。

## 可直接修复的真实差异

| 优先级 | 公开schema | 执行约束 | 最小修复 |
|---|---|---|---|
| P0 read_filing.limit | integer minimum0，无maximum | sec_tools.py:240：1..20，默认12 | minimum1 maximum20 default12；显式描述返回预算。35和0目前schema均放行却运行拒绝 |
| P1 read_filing.query | 任意string | sec_tools.py:242：长度≤300 | maxLength300（空串合法不要加min1） |
| P1 find_filings.form | 任意string | sec_tools.py:210：仅10-K/10-Q/20-F/6-K/8-K/10-K/A/20-F/A | 同集合enum；默认10-K。10-Q/A等看似合理表单目前也不支持，应让模型提前知道 |
| P1 find_filings.report_year | integer minimum0 | sec_tools.py:208：1900..2200 | 明确minimum1900 maximum2200 |
| P1 find_filings.ticker/entity | 任意string；互斥仅描述 | 执行恰好一个且≤200字符，空值被拒绝 | 字符长度1..200+可被Pi支持的oneOf互斥；已有友好repair保留，不把format校验当公司存在保证 |
| P1 calculate.inputEvidenceIds | 全operation均2..100、无uniqueItems | Backend calculations.py:36/40：不可重复；difference/ratio/growth_rate恰好2，只有sum可多项 | uniqueItems=true；按operation分支表达长度，或至少描述三种二元运算恰好两个。当前传3个会通过工具schema后被Backend拒绝 |
| P2 SEC各offset/table/row/cell/paragraph index | minimum0无maximum | _int默认0..100000 | maximum100000，真实文件范围仍运行校验 |
| P2 cite_filing_fields.fields | 长度1..16但无uniqueItems | sec_tools.py:136拒绝重复坐标 | uniqueItems=true；坐标存在与已读状态继续运行判定 |
| P2 immutable read_document.offset | minimum0无maximum | immutable_document_tools.py:146：0..100000 | maximum100000 |
| P2 search_documents.query（实际immutable版） | maxLength1000允许空白/无词项 | execute:124-129要求strip后1..1000且存在词项 | minLength1并描述需词项；运行保留strip/词项检查。schema按原字符串1000而执行按trim长度，长首尾空白存在反向差异，建议一致按原长度 |

## submit_report 静态结构缺口（非独立语义审查问题）

ML report_tools.py:26-59 对很多字段只标string/array；Backend research_report/contract.py 则明确：

- title非空≤300；summary≤10000；section heading非空≤300；paragraph text非空≤30000。
- sections 1..30、每section blocks 1..100、顶层citations≤300。
- 所有ID匹配 `^[A-Za-z0-9][A-Za-z0-9_.:-]{0,159}$`；引用ID数组≤100且不可重复。
- schema允许空sections/空blocks/空title/ID空串或空格，但纯contract会拒绝；这些是可前移的静态结构检查，不需要模型review。
- 已有table columns2..12/rows1..100/cell2..12及caption/label/cell.text上限基本对应，无需重做。行宽必须等于实际columns数、全局ID唯一、保留summary锚点、非空摘要必有引用、citation至少证据或计算之一，是跨字段约束；建议清楚描述并保持Backend权威验证，不强塞复杂递归schema。

优先补常见empty/length/array bounds，可减少整份报告写完后才失败。不能把静态schema通过等同事实或编辑质量通过。

## 一个可能反复空转的文档修复提示

immutable_document_tools.py:99-105 的 `_entry` 在整页context超过200000时提示“select a smaller source span instead”。但context取同一page的全部lines/table_cells/source_refs；在**同一页**改选更小span仍生成相同整页context，不会解决预算。这是真实不可操作repair路径。最小近期修复是准确返回“该页上下文超预算，当前无法引用”与换页/来源的明确选择；若需继续该页，应实现有界邻域上下文且保留字段定位，不能只修改提示假称可用。

page_number最大值取冻结pageCount，document_id/field_id必须存在、SEC url必须发现且字段已读、金融可比性/原文保留、文件4MB/最多8filings以及运行catalog预算均属动态能力约束，不能静态枚举为固定schema保证。宜通过工具返回导航和有用错误公开，不把它们误报成schema bug。

## 当前不在这条运行主链的旧Document工具

execution_service实际注入ImmutableDocumentResearchTools；document_tools.py旧适配器也有query≤2000但schema未写，以及页/行动态边界，不应为此Run改错旧工具。read_research_method的method enum与方法字典一致；SEC registration.mode/max_items 1..16也一致，未发现需要改动的参数范围矛盾。

## 必要离线测试

1. 用实际Pi/TypeBox校验read limit 0/1/20/21/35；1/20到达执行，其他在调用前明确拒绝；省略保持12。
2. 每个静态范围的边界值/前后一个值，同时比较公开schema与执行器，无模型/网络；布尔不能冒充整数。
3. calculate分别测试二元运算2/3项、sum2/100/101项、重复ID，不更改真实Decimal/可比性校验。
4. report最小合法文档、空结构、各长度上限、非法ID、引用重复；验证错误在付费review前返回，并保留跨字段与语义验真。
5. 同一超大PDF页两个不同field调用都能复现同一context超限，确保新repair不再建议无效同页缩span。

高收益排序：read.limit已造成真实无效调用；其次calculate二元arity、find表单/年范围、report必填非空结构。这些均不会降低原文/字段/恢复要求。


## 当前实施状态

Root已修正SEC read的limit1–20、query300字符、offset100000上限说明；13项SEC及最终wire测试通过，尚未提交。报告schema约束对齐由子任务实施中。PDF同页超大context的repair问题尚待实现；不把提示改写当作已解决实际读取能力。
