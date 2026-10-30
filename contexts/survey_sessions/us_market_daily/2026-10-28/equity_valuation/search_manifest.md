# Google与机器人研究索引｜2026-10-28

## 最终产物

- `report.html` / `report.md`：主线程整合的单一主报告，Google估值、分批研究价与九家公司筛选。
- `google_model_inputs.json` / `google_valuation_model.json` / `google_forecast.csv`：估值事实基线、假设、逐期输出、敏感性和反向DCF。
- `google_valuation_scenarios.png`：明确标为未来研究假设的曲线与敏感性图。
- `valuation_checks.json`：FCFF恒等式、终值增长与再投资、反向估值和折现率方向检查。
- `parent_normalization_review.json`：主线程恢复RRX股权薪酬成本的调整，与初筛较宽松口径区分。
- 上级 `valuation_research_watch.json`：研究价位与基本面有效条件，非订单或原四标的回撤提醒。

## 并行研究定位

| Agent规范名 | 工作范围 | 工件 | 状态 |
| --- | --- | --- | --- |
| /root/google_capital_audit | 资本结构、投资资产、租赁、优先股、TTM EBIT及模型审阅 | google_capital_audit.md / google_capital_sources.json | 已交叉审阅 |
| /root/robotics_quality_screen | CGNX、NOVT、ROK、ZBRA、TER；价格与收购边界 | robotics_quality_screen.md / robotics_quality_sources.json | 已完成 |
| /root/robotics_value_screen | RRX、ATS、AMBA、STM；正常化利润与现金流口径 | robotics_value_screen.md / robotics_value_sources.json | 已完成，主线程RRX口径更审慎 |

## 交叉核验与结论变化

Google资产桥经独立原始10-Q核验：股权投资不能全当现金，经营租赁不可在含租金现金流外再扣，优先股索偿法与转股法不叠加。主线程回读主要原披露。Google的初版第10年按终值增长配置再投资、但实际收入仍高速增长，审阅发现后改为第6–10年增长平滑衰减至终值，并按第10年实际增长配置再投资；最终207美元基准采用修正后模型，未沿用初版约232美元。

RRX初筛只剔退税得到EPS10.03；主线程回读指引对照表后另恢复SBC0.32，最终采用EPS9.71、17倍假设基准165.07及130–140美元研究区。旧初筛170.51保留为可追溯的较宽松参考，不能混称为最终结论。

## 覆盖与缺口

报价同为2026-10-27美国常规收盘。Google财务基线截至6月30日、普通股数截至7月15日；Q3尚未用于模型。主要公司事实来自原始IR/SEC，价格由Yahoo/StockAnalysis交叉；市场估值统计不是公司保证。ATS部分财年现金流来自可读索引，汇率为日线参考。机器人相关收入未完整单列，未臆造客户订单和人形机器人收入。没有全市场穷尽、历史回测、概率拟合或账户操作。

财报属于财务事实证据；产品和客户能力页只验证产品关系，不能据此验证未来收入与投资回报。全部未来增长、倍数、折现率及买入研究价为分析假设，重要来源与读取范围在三个sources JSON及主报告中就近保留。
