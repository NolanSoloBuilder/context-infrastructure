# Run04 独立产品验收基线

本文件只用于运行结束后的独立审查；未发送给模型、研究运行器或提示词。所有数字来自本地保留原件，并在本轮重新读取核对；不代表 Run04 已经取得这些证据、完成宿主计算或通过产品验收。

## 1. 原件与证据范围

- 原件：`/Users/xuhao/Documents/Other/context-infrastructure/contexts/source_materials/cited_alpha_cross_source_tesla_2024/2a5dc10024afd96cf71f154c949759123c1da05715fb574866eaba6e1ec3bb18.html`；SHA-256 `2a5dc10024afd96cf71f154c949759123c1da05715fb574866eaba6e1ec3bb18`；2596459 bytes。
- 原件：`/Users/xuhao/Documents/Other/context-infrastructure/contexts/source_materials/cited_alpha_cross_source_tesla_2024/05dfde334f800ec5f0ee140c0dd78409f24ad775e11a0c68f8a6b534b04cafdc.pdf`；SHA-256 `05dfde334f800ec5f0ee140c0dd78409f24ad775e11a0c68f8a6b534b04cafdc`；11267189 bytes。
- SEC：Tesla FY2024 Form 10-K，原URL https://www.sec.gov/Archives/edgar/data/1318605/000162828025003063/tsla-20241231.htm 。
- PDF：TSLA Q4 2024 Update，36页，原URL https://digitalassets.tesla.com/tesla-contents/image/upload/IR/TSLA-Q4-2024-Update.pdf 。PDF页码以下均为1-based物理页；第5页年度财务摘要、第8页年度经营摘要明确标注 Unaudited。
- 两份文件均来自 Tesla，能交叉核对披露一致性，不能称为两个独立机构的交叉背书。
- SEC下列无维度期间 c-1=2024-01-01 至 2024-12-31；c-28=2023-01-01 至 2023-12-31。本轮已读取原始 context 核对。美元财务量默认 million USD，不是美元/亿美元；EPS为美元每股。
- 复用并逐项重验 `/tmp/cited-alpha-business-run-02/independent-fact-baseline.json` 的12项核心事实；阅读 `20_run02_report_failure_review.md` 与 `06_report_experience_acceptance.md`。未访问模型/DocAI/云端，不操作数据库或运行服务。

## 2. 必审核心事实：年度口径

| 项目 | FY2024 | FY2023 | 精确原文定位 |
|---|---:|---:|---|
| 总收入 | 97,690 | 96,773 | SEC ix:nonfraction name末段 `RevenueFromContractWithCustomerExcludingAssessedTax`，contextref分别c-1/c-28，unitref=usd，scale=6；合并利润表/现金流量表 |
| 营业利润 | 7,076 | 8,891 | SEC ix:nonfraction name末段 `OperatingIncomeLoss`，contextref分别c-1/c-28，unitref=usd，scale=6；合并利润表/现金流量表 |
| 合并净利润 | 7,153 | 14,974 | SEC ix:nonfraction name末段 `ProfitLoss`，contextref分别c-1/c-28，unitref=usd，scale=6；合并利润表/现金流量表 |
| 归属普通股股东净利润 | 7,091 | 14,997 | SEC ix:nonfraction name末段 `NetIncomeLoss`，contextref分别c-1/c-28，unitref=usd，scale=6；合并利润表/现金流量表 |
| 经营现金流 | 14,923 | 13,256 | SEC ix:nonfraction name末段 `NetCashProvidedByUsedInOperatingActivities`，contextref分别c-1/c-28，unitref=usd，scale=6；合并利润表/现金流量表 |
| 购置物业厂房设备现金支出 | 11,339 | 8,898 | SEC ix:nonfraction name末段 `PaymentsToAcquirePropertyPlantAndEquipment`，contextref分别c-1/c-28，unitref=usd，scale=6；合并利润表/现金流量表 |
| 毛利润 | 17,450 | 17,660 | SEC ix:nonfraction name末段 `GrossProfit`，contextref分别c-1/c-28，unitref=usd，scale=6；合并利润表/现金流量表 |
| 研发费用 | 4,540 | 3,969 | SEC ix:nonfraction name末段 `ResearchAndDevelopmentExpense`，contextref分别c-1/c-28，unitref=usd，scale=6；合并利润表/现金流量表 |
| 汽车总收入 | 77,070 | 82,419 | PDF p5 Total automotive revenues，2024/2023列；SEC合并利润表同名行 |
| 能源发电及储能收入 | 10,086 | 6,035 | PDF p5 Energy generation and storage revenue，2024/2023列；SEC合并利润表同名行 |
| 服务及其他收入 | 10,534 | 8,319 | PDF p5 Services and other revenue，2024/2023列；SEC合并利润表同名行 |
| 汽车销售收入（不含积分与租赁） | 72,480 | 78,509 | SEC合并利润表 Automotive sales，2024/2023列 |
| 汽车监管积分收入 | 2,763 | 1,790 | SEC合并利润表 Automotive regulatory credits，2024/2023列 |
| 能源业务成本 | 7,446 | 4,894 | SEC合并利润表 Cost of revenues → Energy generation and storage，2024/2023列 |
| 总营业费用 | 10,374 | 8,769 | PDF p5 Operating expenses；SEC合并利润表 Total operating expenses |
| 税前利润 | 8,990 | 9,973 | SEC合并利润表 Income before income taxes |
| 所得税费用／（收益） | 1,837 | (5,001) | SEC IncomeTaxExpenseBenefit c-1/c-28 scale6；2023 sign="-" |
| 稀释每股收益 GAAP | 2.04 | 4.30 | PDF p5 EPS attributable to common stockholders, diluted (GAAP)；SEC EarningsPerShareDiluted c-1/c-28，usdPerShare |
| 公司披露自由现金流 | 3,584 | 4,358 | PDF p5 Free cash flow；与当期OCF减PP&E支出核对 |
| 汽车交付量（辆） | 1,789,226 | 1,808,581 | PDF p8 Total deliveries，2024/2023列 |
| 汽车产量（辆） | 1,773,443 | 1,845,985 | PDF p8 Total production，2024/2023列 |
| 储能部署量（GWh） | 31.4 | 14.7 | PDF p8 Storage deployed (GWh)，2024/2023列 |

上述业务行已对照PDF页面原文与SEC文本中的合并利润表；运营量来自PDF，不能臆造SEC XBRL ID。SEC汽车分部收入还包含 Services and other，不能把77,070等同于完整汽车分部收入87,604。能源收入包含发电与储能，不能全称“储能收入”。

## 3. 派生项：报告采用时必须存在实际宿主计算

以下为独立Decimal复算预期，不是Run04 calculationId；报告必须绑定它自己的实际输入 evidenceId、期间、单位、公式、精度及结果。原文已披露的取整同比可按直接披露引用；新精度和新推导应登记计算。

| 派生项 | 公式（million USD口径） | 预期 |
|---|---|---|
| 总收入同比 | (97690/96773-1)×100 | 0.95% |
| 营业利润同比 | (7076/8891-1)×100 | -20.41% |
| 合并净利润同比 | (7153/14974-1)×100 | -52.23% |
| 归属普通股股东净利润同比 | (7091/14997-1)×100 | -52.72% |
| 经营现金流同比 | (14923/13256-1)×100 | 12.58% |
| 购置物业厂房设备现金支出同比 | (11339/8898-1)×100 | 27.43% |
| 汽车收入同比 | (77070/82419-1)×100 | -6.49% |
| 能源收入同比 | (10086/6035-1)×100 | 67.13% |
| 服务及其他收入同比 | (10534/8319-1)×100 | 26.63% |
| 汽车交付同比 | (1789226/1808581-1)×100 | -1.07% |
| 自由现金流同比 | (3584/4358-1)×100 | -17.76% |
| 自由现金流 | 2024:14923−11339；2023:13256−8898 | 3,584；4,358 |
| 营业利润率 | 营业利润÷总收入 | 2024 7.24%；2023 9.19% |
| 营业利润率变化 | 两年未四舍五入利润率差×10000 | -194.42 bp |
| 能源毛利 | 收入−成本 | 2024 2,640；2023 1,141 |
| 能源毛利率 | (收入−成本)÷收入 | 2024 26.17%；2023 18.91% |
| 收入变化桥 | 汽车−5349＋能源4051＋服务2215 | 总收入＋917；只是算术分解，不是因果证明 |

储能同比按展示值31.4/14.7计算为113.61%，原文取整114%；GWh展示精度不能支持更多有效位数。资本支出原PDF以负号展示，SEC PaymentsToAcquirePropertyPlantAndEquipment 是正的支出量，不能做14923−(−11339)。单位换算million USD→亿美元需÷100。

## 4. 可支持的解释与最容易越界的归因

| 判断主题 | 原文位置与可支持范围 | 不应跨越的边界 |
|---|---|---|
| 汽车收入与利润率 | SEC Item7 Results of Operations，段落起句 Automotive sales revenue decreased：降价、融资优惠、产品组合使ASP降低；Gross margin for total automotive decreased：ASP与Cybertruck爬坡，部分被单位成本下降、积分/FSD收入抵消 | 汽车销售≠汽车总收入；cash deliveries≠全部交付；不能仅凭收入下降断言需求崩塌或精确量化单项贡献 |
| 能源增长与利润率 | SEC Item7起句 Energy generation and storage revenue increased：Megapack/Powerwall部署增加；Gross margin for energy generation and storage increased：成本降低、IRA制造积分和储能业务占比提升 | 部署量是实物量，不能直接换算已确认收入；发电储能业务不全是储能；不得把IRA贡献说成全部增长 |
| 净利润下降与税项 | SEC Item7概述与Note14 Income Taxes：2023 Q4释放美国联邦及州递延税资产估值备抵 **$6.54 billion**；2023税费行是收益5,001million，2024费用1,837million | 6.54B估值备抵释放≠5.001B总所得税收益≠税率调节表5.962B的change in valuation allowance；不要未经定义写“剔除59亿美元后净利”。税项解释不能掩盖营业利润下滑 |
| OCF改善 | SEC Item7 Liquidity and Capital Resources → Operating Activities，起句 Net cash provided by operating activities increased：净经营资产负债有利变动2.29B，部分被扣除非现金项目后的净收益减少623M抵消 | OCF/净利润比高不足以证明经营质量极好；净经营资产负债变化不全等于可持续效率改善 |
| 积分 | SEC Item7 Automotive regulatory credits revenue increased及Note2监管积分收入政策：北美需求；原文明确negligible incremental costs | 必须实际引用该政策段落才能说增量成本低，不能以收入值推导；收入不等于当期全部收到现金；低增量成本不等于无成本或完全利润 |
| 服务及其他 | SEC Item7起句 Services and other revenue increased：二手车、非保修维修及碰撞、付费超充、保险、零件 | 不以能源段落支持服务原因，不编造业务贡献额 |
| 季度/全年 | PDF p6 Financial Summary讨论的是Q4；p11 11.0GWh也是Q4，p8 31.4GWh才全年 | Q4交付增长/ASP/AI费用解释不能直接当FY2024全部原因；Q4年末存量与季度流量分别标记 |
| 流动性与前景 | SEC Item7概述一般能自筹资金(generally fund itself)，同时持续投入资本密集项目与研发 | 不升级为“完全自给、无融资风险”；FSD(Supervised)不等于完全自动驾驶；工厂未来爬坡/Robotaxi规划非已实现财务结果 |

## 5. Run04结束后的产品核验门槛

1. 先验证是否真正生成并持久化通过正式合同检查的ReportVersion，再审内容；failed/deadline或草稿不能冒充成品。
2. 报告需回答收入、盈利、现金流、汽车、能源五个问题，结论与条件可读；不要求机械堆满本表。若引用额外数值须另查原件，本表未覆盖值保持待核验。
3. 每个数值对应正确期间/单位/行；每个归因对应其实际原文段落。派生值有宿主计算记录；独立基线算对不代表Run已有该记录。
4. 两种来源的引用确实可打开本Run绑定原件；PDF retained_provider_page 可在保留解析图片同坐标字段高亮，原PDF只页级时如实标注，不能谎称原PDF字段定位。重复金额必须靠fieldId/行列/期间，不靠文字第一次匹配。
5. 引用registry无orphan，引用事实审查、权限、source版本、字段级位置都成立；本任务不进行UI点击或实际Run状态验收。

## 6. 可复核定位附录

SEC核心事实检索：HTML中 `ix:nonfraction[name$=":OperatingIncomeLoss"][contextref="c-1"]` 一类选择器；所有同concept/context的重复出现应一致。本轮直接原件核对了上表XBRL项，并核对c-1/c-28起止日期。PDF年度列顺序2020、2021、2022、2023、2024、YoY，避免把最后同比列当2024。

原文件保留，不另写造出的证据ID或解析定位。原文完整页面可通过上述sha文件复读；这是产品审查参考文件，不属于Run可引用证据目录。
