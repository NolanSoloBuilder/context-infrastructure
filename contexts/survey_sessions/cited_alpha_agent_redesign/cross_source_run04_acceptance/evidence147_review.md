# Run04 checkpoint147：14条已登记证据独立审查

结论：14条全部来自同一SEC合并利润表 table23，7个指标各2024/2023两年。逐条按原始DOM table/row/cell定位重取文本，匹配原件的XBRL concept/context/period/dimensions/unit/scale/value，未发现错行、收入混成本或期间错位。它们尚不是完整报告，也未涵盖税项、GAAP净利、non-GAAP调整、现金流或风险解释；不能据此给报告通过结论。

## 方法与证据层级

仅访问指定checkpoint的progress.rawCatalog，未读messages/思考/签名；未轮询运行、调用模型/网络/数据库。SEC原件SHA重新算得2a5dc10024afd96cf71f154c949759123c1da05715fb574866eaba6e1ec3bb18，所有14条provenance sha/captureReceipt contentHash及retained状态一致。云端是否仍可读取沿用Root已完成的独立scope/hash检查，本次没有访问GCS。

PDF原件SHA重新匹配05dfde334f800ec5f0ee140c0dd78409f24ad775e11a0c68f8a6b534b04cafdc，读取物理页5。该页与已归档独立baseline支持汽车总收入、能源、服务、总收入、毛利两年对照；表中“页5出现同值”本身只是文本层辅助检查，不冒充PDF字段坐标核验。这14条没有任何PDF evidence locator，故没有声称其PDF bbox/字段身份通过。

## 逐条核对

所有期间均为本年01-01至12-31；unit=iso4217:USD、scale=6，因此展示值单位百万美元，typed value是原始美元。指标列来自原始行标题；坐标为零起始DOM索引（不是视觉列号）。

| evidence ID | 原始行 | 年 | quote（百万美元） | table/row/cell | concept | context | 维度 | PDF辅助 |
|---|---|---|---:|---|---|---|---|---|
| `ev-145f44aacb625decaea989c74ef2c7c701b85c1e0ce5df65e1a609f18cd28fa3` | Energy generation and storage | 2023 | 6,035 | 23/8/4 | RevenueFromContractWithCustomerExcludingAssessedTax | c-23 | tsla:EnergyGenerationAndStorageMember | 页5出现同值，见限制 |
| `ev-1559fa454d23f2d02483e6fed5a3eb89a9a108120d550b91dede0aba78240e7f` | Automotive regulatory credits | 2023 | 1,790 | 23/5/4 | RevenueFromContractWithCustomerExcludingAssessedTax | c-14 | tsla:AutomotiveRegulatoryCreditsMember | 未做PDF字段匹配 |
| `ev-209028db96b251222e2fa3aba75c7380358afba7746685222a96d5958a29578e` | Total revenues | 2023 | 96,773 | 23/10/4 | RevenueFromContractWithCustomerExcludingAssessedTax | c-28 | 无维度 | 页5出现同值，见限制 |
| `ev-520b81586a8a6530353f47cc79f9d145f7400c71b6c584334fed3803e1b6eef6` | Automotive regulatory credits | 2024 | 2,763 | 23/5/1 | RevenueFromContractWithCustomerExcludingAssessedTax | c-13 | tsla:AutomotiveRegulatoryCreditsMember | 未做PDF字段匹配 |
| `ev-52276fe094b640a2f10481da0f00ca62dd6d9540150786ff90c21c2d2cc8ccf6` | Services and other | 2023 | 8,319 | 23/9/4 | RevenueFromContractWithCustomerExcludingAssessedTax | c-26 | tsla:ServicesAndOtherMember | 页5出现同值，见限制 |
| `ev-5bb6713c3c93d5ba7bf343e726bf702b2b2161e892cede68e3b809e158460b69` | Automotive sales | 2023 | 78,509 | 23/4/6 | RevenueFromContractWithCustomerExcludingAssessedTax | c-11 | tsla:AutomotiveSalesMember | 未做PDF字段匹配 |
| `ev-6a0b028e5b5e7fc46049bfd06c30b9863864a1bb075a30e5d993b4a4271ba7c8` | Gross profit | 2023 | 17,660 | 23/18/4 | GrossProfit | c-28 | 无维度 | 页5出现同值，见限制 |
| `ev-7a597f53277c88cf47fbe7b433fd4152c8a628ef852100fb7366c50294e25b21` | Services and other | 2024 | 10,534 | 23/9/1 | RevenueFromContractWithCustomerExcludingAssessedTax | c-25 | tsla:ServicesAndOtherMember | 页5出现同值，见限制 |
| `ev-7c1c2b40896b6b07b9d17d869a26768c2181a073f39865ec9bd9aa7ecac00497` | Automotive sales | 2024 | 72,480 | 23/4/2 | RevenueFromContractWithCustomerExcludingAssessedTax | c-10 | tsla:AutomotiveSalesMember | 未做PDF字段匹配 |
| `ev-7cebd00c566709a71738a3575406b36f941a9c29215f3cc636dced2c6bfad079` | Total automotive revenues | 2024 | 77,070 | 23/7/1 | RevenueFromContractWithCustomerExcludingAssessedTax | c-19 | tsla:AutomotiveRevenuesMember | 页5出现同值，见限制 |
| `ev-819a81b6efaf1d60345e371d07d04a4bebc903b5188346d2c42fa3f3f4fa5b8b` | Gross profit | 2024 | 17,450 | 23/18/1 | GrossProfit | c-1 | 无维度 | 页5出现同值，见限制 |
| `ev-839807ffb06d94a5070c28bf6452d23ce4ad1e9345a4525ef634dcaa325bdadc` | Total automotive revenues | 2023 | 82,419 | 23/7/4 | RevenueFromContractWithCustomerExcludingAssessedTax | c-20 | tsla:AutomotiveRevenuesMember | 页5出现同值，见限制 |
| `ev-ccc4431aba314b48a328a01f3576d1a6a552b1f384027b447a4d833aacdea244` | Energy generation and storage | 2024 | 10,086 | 23/8/1 | RevenueFromContractWithCustomerExcludingAssessedTax | c-22 | tsla:EnergyGenerationAndStorageMember | 页5出现同值，见限制 |
| `ev-d4e106e57eeae9152f63adfb1bc7befb35352479ba40e2295bf6ae9e114d1769` | Total revenues | 2024 | 97,690 | 23/10/1 | RevenueFromContractWithCustomerExcludingAssessedTax | c-1 | 无维度 | 页5出现同值，见限制 |

## 口径限制

- Automotive sales（72,480/78,509）是不含监管积分及租赁的汽车销售收入；Total automotive revenues（77,070/82,419）包含上述项。后者不等于包含Services and other的2024年汽车分部收入87,604，不能互换标签。
- Energy generation and storage（10,086/6,035）为收入行row8；不是成本行row15的7,446/4,894，也不能仅称储能收入。核对使用实际DOM行而非全文搜数字。
- Gross profit（17,450/17,660）是合并毛利润，不是营业利润/净利润/自由现金流。此14条不包含任何GAAP/non-GAAP净利证据或税项，无法核验2023税项收益驱动净利变化的解释。
- 两年总收入、毛利等数值与独立baseline重叠项一致。全部14条都有SEC原件级重取证据，不仅是rawCatalog内部字段自洽；PDF仅辅助对照，不是两个独立机构的背书。
- 原件quote与XBRL事实正确不等于后续正文解释正确；派生同比/利润率仍需后续实际计算记录和引用绑定。本快照无计算不等于无法继续，也不预判运行结局。

离线复核脚本：/tmp/run04-evidence147-check.py；逐条机器结果：/tmp/run04-evidence147-source-checks.json。
