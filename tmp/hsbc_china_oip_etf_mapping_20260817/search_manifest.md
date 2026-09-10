# Search Manifest

## 产出文件索引

| 文件 | 路径 | 说明 |
| --- | --- | --- |
| Scratchpad | `tmp/hsbc_china_oip_etf_mapping_20260817/scratchpad.md` | 主线程研究笔记与 claim 状态 |
| Search Manifest | `tmp/hsbc_china_oip_etf_mapping_20260817/search_manifest.md` | 本文件 |
| 最终报告 | `contexts/survey_sessions/2026_08_14_hsbc_easy_invest_sp500_nasdaq_etf_selection.md` | 既有报告增补内地汇丰 OIP 范围 |

## 主要来源

- 汇丰股票型海外基金清单：https://www.hsbc.com.cn/investments/products/qdii/equity/
- 汇丰 OIP 通用申购书：https://www.hsbc.com.cn/investment-platform/internet/aoc-pdf/investments/SRBP/GPSP_CN.pdf
- 汇丰 QDII 说明：https://www.hsbc.com.cn/investments/articles/qdii/
- 汇丰产品对照表：https://www.hsbc.com.cn/investments/products/migration-list/

## Subagent 原始产出

| Agent | 定位 | 状态 |
| --- | --- | --- |
| oip_status | 当前申购状态与代码 | completed |
| oip_holdings | 最新持仓与 ETF 相似度 | completed |
| oip_costs | 起购、费用与额度边界 | completed |
