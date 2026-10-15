# Run04 seq190 最终证据与计算核验

结论：42条已登记证据（30 SEC、12 PDF）均完成本地原件定位核查，4项增长率独立Decimal复算一致。没有checkedCandidate，本结果不是报告交付或语义审查通过证明。

重新canonical序列化指定seq190所得4,029,869 bytes、SHA becad9b6cf758e2ad9fb507bacb2ebd697bfcafd8e9b628056fc674f977f1df5，与Root读回值相同。仅读rawCatalog/calculations；未访问思考/签名，未轮询Run，无模型/云端请求。

## 验证层次

- SEC原件SHA重新验证；按table/row/cell（零起始DOM序号）重取quote。22条有XBRL，进一步核对concept、context、年度起止、维度、scale、unit及value；8条table13毛利/毛利率为原文披露，非typed XBRL。table13原始表头为年度2024/2023/2022，注明Dollars in millions；百分比行另按毛利率解读。不把8条转换成无来源的typed计算输入。
- PDF原件SHA重新验证；12条冻结providerReceipt SHA与本地真实providerDocuments canonical字节一致。按原始provider page的精确polygon+text anchor文本匹配唯一line，再核对fieldId/record/documentVersionId。同一数值不跨行匹配。另从原PDF原生文字层核对对应行，详细原PDF行保存在JSON。此为坐标身份及文字核查，不替代浏览器实际显示/原PDF坐标转换验收。
- PDF p4是季度财务摘要，本次6条都是Q4 2024，绝不能写成年份累计；p5自由现金流两条为2023/2024年度；p8交付与储能部署两组为年度、单位分别辆/GWh。这些PDF汇总注明unaudited；SEC和PDF同为Tesla披露，不能称两个独立机构背书。

## 特别口径

1. 汽车总收入77,070/82,419不等于含服务及其他的汽车分部；汽车毛利14,197/16,030亦不等于完整汽车与服务分部毛利。能源发电及储能收入10,086/6,035不可简称纯储能收入。
2. 归属普通股净利7,091/14,997是GAAP，PDF季度2,317同样明确GAAP；本次未登记non-GAAP净利，不能支持调整净利对比。税项解释仍无明确所得税费用/收益证据，14,997本身不能证明一次性税收成因。
3. 现金流表PP&E原文quote带括号(11,339)/(8,898)，表示现金流出；XBRL Payments概念采用正支付金额。不得把展示负号二次施加到正支付输入而得到错误FCF。
4. 原文毛利率18.4/19.4%、26.2/18.9%为披露取整数；若报告产生更高精度，需新计算证据。FCF3,584/4,358此处有直接PDF披露，可直接引用，但若声称“系统复算”须存在相应计算记录（本次4项不含FCF）。

## 42条摘要

SEC typed单位iso4217:USD的quote按scale6显示为百万美元；JSON保留typed unit和scale。PDF列出的million USD为对应原文财务表单位。

| ID | 来源 | 指标 | 期间 | quote | 单位 | 定位 |
|---|---|---|---|---|---|---|
| `ev-0be700949501386ee50193bce1e24b677737c24b1288d82f98d16b93f643d587` | sec | Net cash provided by operating activities | 2023 | 13,256 | iso4217:USD | 26/20/4 |
| `ev-145f44aacb625decaea989c74ef2c7c701b85c1e0ce5df65e1a609f18cd28fa3` | sec | Energy generation and storage | 2023 | 6,035 | iso4217:USD | 23/8/4 |
| `ev-149b131b1f701f221863e4121e4a0673602cb5b93bda9b03162592f6bc6067d0` | pdf | Total gross profit | Q4 2024 | 4,179 | million USD | ['line', '4', '49'] |
| `ev-1559fa454d23f2d02483e6fed5a3eb89a9a108120d550b91dede0aba78240e7f` | sec | Automotive regulatory credits | 2023 | 1,790 | iso4217:USD | 23/5/4 |
| `ev-1fcd9dcdcb3edaedd43e9eb3df9d8cb53d1c693cb02bad05e1a3805ad1410771` | pdf | Free cash flow | 2023 | 4,358 | million USD | ['line', '5', '134'] |
| `ev-209028db96b251222e2fa3aba75c7380358afba7746685222a96d5958a29578e` | sec | Total revenues | 2023 | 96,773 | iso4217:USD | 23/10/4 |
| `ev-253a2f3034964d099d764cd684343e0bfee9acc058472501bf080a3901258eb2` | pdf | Income from operations | Q4 2024 | 1,583 | million USD | ['line', '4', '67'] |
| `ev-3e1811a581194a1ac17c7371c77d82ddcdec8a6dc1f607bd26a2df43ce447029` | pdf | Net income attributable to common stockholders (GAAP) | Q4 2024 | 2,317 | million USD | ['line', '4', '93'] |
| `ev-48e83670d44a3e770d540dc81fb82f4afe5f4d986928a9a87b699b147ecbbd67` | sec | Income from operations | 2023 | 8,891 | iso4217:USD | 23/24/4 |
| `ev-49febd6677ce963549be792038dc402b3231436ea16fb4d8bf5b93919cfe67c4` | pdf | Total automotive revenues | Q4 2024 | 19,798 | million USD | ['line', '4', '25'] |
| `ev-520b81586a8a6530353f47cc79f9d145f7400c71b6c584334fed3803e1b6eef6` | sec | Automotive regulatory credits | 2024 | 2,763 | iso4217:USD | 23/5/1 |
| `ev-52276fe094b640a2f10481da0f00ca62dd6d9540150786ff90c21c2d2cc8ccf6` | sec | Services and other | 2023 | 8,319 | iso4217:USD | 23/9/4 |
| `ev-5bb6713c3c93d5ba7bf343e726bf702b2b2161e892cede68e3b809e158460b69` | sec | Automotive sales | 2023 | 78,509 | iso4217:USD | 23/4/6 |
| `ev-66c7005d07d9d44998864c8d57e00e3661dcfacf714c82b5e51edbc4aeec2534` | sec | Gross profit total automotive | ['2024'] | 14,197 | million USD | 13/12/3 |
| `ev-6a0b028e5b5e7fc46049bfd06c30b9863864a1bb075a30e5d993b4a4271ba7c8` | sec | Gross profit | 2023 | 17,660 | iso4217:USD | 23/18/4 |
| `ev-7493961acf5440852717cc5b1c95c0be28aa614743edb31389734b7e9363452c` | sec | Income from operations | 2024 | 7,076 | iso4217:USD | 23/24/1 |
| `ev-753a39e4bba22b96d8b3439a3ac0117c0986c7c4c43fefd9b7956ca897260403` | pdf | Free cash flow | 2024 | 3,584 | million USD | ['line', '5', '135'] |
| `ev-7a597f53277c88cf47fbe7b433fd4152c8a628ef852100fb7366c50294e25b21` | sec | Services and other | 2024 | 10,534 | iso4217:USD | 23/9/1 |
| `ev-7c1c2b40896b6b07b9d17d869a26768c2181a073f39865ec9bd9aa7ecac00497` | sec | Automotive sales | 2024 | 72,480 | iso4217:USD | 23/4/2 |
| `ev-7cebd00c566709a71738a3575406b36f941a9c29215f3cc636dced2c6bfad079` | sec | Total automotive revenues | 2024 | 77,070 | iso4217:USD | 23/7/1 |
| `ev-7d25e8c90073db2b635554751606de322bacc5663009c03a8bd0de7979663c0a` | sec | Gross margin energy generation and storage segment | ['2023'] | 18.9 | percent | 13/19/5 |
| `ev-819a81b6efaf1d60345e371d07d04a4bebc903b5188346d2c42fa3f3f4fa5b8b` | sec | Gross profit | 2024 | 17,450 | iso4217:USD | 23/18/1 |
| `ev-839807ffb06d94a5070c28bf6452d23ce4ad1e9345a4525ef634dcaa325bdadc` | sec | Total automotive revenues | 2023 | 82,419 | iso4217:USD | 23/7/4 |
| `ev-8bade8408d0c7c45f75a2b86ce457bdafd95c29452d0e6cb8df60c06c172f316` | pdf | Storage deployed (GWh) | 2023 | 14.7 | GWh | ['line', '8', '76'] |
| `ev-958cc8e7076414226a1a8b507a6903915c2ec1c823b56306ef730cfd06c2f7c4` | sec | Gross margin total automotive | ['2023'] | 19.4 | percent | 13/13/5 |
| `ev-9697bbbc2440d850056a86c498acd43d44764df903eec62b798aa788c6c00816` | sec | Gross margin total automotive | ['2024'] | 18.4 | percent | 13/13/2 |
| `ev-99727f80cd85bff1ae696a21c3db9cfa752308a0959641a70f11be43f231ee9e` | sec | Purchases of property and equipment excluding finance leases, net of sales | 2023 | ( 8,898 ) | iso4217:USD | 26/22/4 |
| `ev-af12431ed9bb9223ba2dc002ae7f1b1481a1103f8b084f962ddcbc937c5fc72c` | sec | Net cash provided by operating activities | 2024 | 14,923 | iso4217:USD | 26/20/1 |
| `ev-b470d96c661680b04b398dc430d6032327f6214dd051db2cfbb9656949791452` | pdf | Total deliveries | 2024 | 1,789,226 | vehicles | ['line', '8', '50'] |
| `ev-b7659d3cb5b5cff5a79e5cd5752181723a056c234a8389eb07384218834bc5cf` | sec | Gross profit energy generation and storage segment | ['2024'] | 2,640 | million USD | 13/18/3 |
| `ev-ba64a74d561dc58659d2c4aafd21012dd304f600aede5023e37f76595c2a0fff` | pdf | Energy generation and storage revenue | Q4 2024 | 3,061 | million USD | ['line', '4', '31'] |
| `ev-be7e13460dc7aab0915e0ada25da8bb37fea676fb3f7f1aa33ed2c33f31cfe29` | sec | Gross profit total automotive | ['2023'] | 16,030 | million USD | 13/12/7 |
| `ev-c46d23ccac8363a1b2eac4db97c21bae283205398ee28a089679e54aeedb3129` | sec | Net income attributable to common stockholders | 2023 | 14,997 | iso4217:USD | 23/32/6 |
| `ev-c57aec1d9b9d09e34f68d8f4b07c4d54fb1cf8c4238b50b8649bb3aa04d3bf8d` | pdf | Total deliveries | 2023 | 1,808,581 | vehicles | ['line', '8', '49'] |
| `ev-cb1207a63ebd4e02d5a0385d201de26c2ae380b0d17cad264f9fe192f3f9d7c0` | sec | Gross margin energy generation and storage segment | ['2024'] | 26.2 | percent | 13/19/2 |
| `ev-ccc4431aba314b48a328a01f3576d1a6a552b1f384027b447a4d833aacdea244` | sec | Energy generation and storage | 2024 | 10,086 | iso4217:USD | 23/8/1 |
| `ev-d309bcde15c78fa8cdd0c266ca9337c2c839b9b02a7cdfde145e6e5a8a876c3b` | sec | Net income attributable to common stockholders | 2024 | 7,091 | iso4217:USD | 23/32/2 |
| `ev-d4e106e57eeae9152f63adfb1bc7befb35352479ba40e2295bf6ae9e114d1769` | sec | Total revenues | 2024 | 97,690 | iso4217:USD | 23/10/1 |
| `ev-d84e79b6d94d182e45ea0432dd8a29150ee6cb56207324410ee63429497ad559` | sec | Purchases of property and equipment excluding finance leases, net of sales | 2024 | ( 11,339 ) | iso4217:USD | 26/22/1 |
| `ev-d95600f13fdac2ec2a8e36aadb8b6a7ee89ea93450f2a0bcf2ef8b6133420aa0` | sec | Gross profit energy generation and storage segment | ['2023'] | 1,141 | million USD | 13/18/7 |
| `ev-ded970e298334a3a773ad5804bbf12a193cd87decc229fe669517392f996c122` | pdf | Total revenues | Q4 2024 | 25,707 | million USD | ['line', '4', '43'] |
| `ev-ec76077822abaa04b6d8d8f0d486b86c42395779ba50cb84d59926014bef1618` | pdf | Storage deployed (GWh) | 2024 | 31.4 | GWh | ['line', '8', '77'] |

## 4项计算

逐项检查inputEvidenceIds存在、inputs数值/单位与原始XBRL一致、两年metric/dimensions一致，2024/2023完整年度；独立用(current/prior−1)×100按2位Decimal四舍五入。没有使用模型结论作为验证依据。

| 指标 | 独立结果 | calculation ID |
|---|---|---|
| Income from operations | -20.41% | `calc-13c59dbc29ec1a2fbe0e5e0d9306f43dc7ace929eb33e8214fc0274a06db5172` |
| Total automotive revenues | -6.49% | `calc-157845aef15155449418afbb6580a46c30e0174631712c67f4ce108300cec1b2` |
| Total revenues | 0.95% | `calc-259320b2ef5de191040241a3257ecccf8d2bb5fa2bd8f142955b0bdce54f3b12` |
| Energy generation and storage | 67.13% | `calc-bbcf924c60d65bb68613dec79e1e0d767c39049424e5124cb32139482426a8b3` |

未核验任何尚未提供的报告正文、引用绑定、问题覆盖或可读性。证据正确不保证报告解释正确。结构化结果：/tmp/cited-alpha-run04-final-evidence-review.json；脚本：/tmp/run04-final-evidence-check.py。
