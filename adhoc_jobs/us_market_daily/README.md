# 美股日报数据与图表

已完成首次手动验证：北京时间2026-10-23，对应美东2026-10-22常规收盘。此脚本只读公开行情并生成本地文件；不连接券商或交易。图表不能代替每次的联网新闻、官方日历、收益率和重要价格交叉核验。

现有隔离环境：`adhoc_jobs/us_market_daily/.venv`，Python 3.12，matplotlib、pandas；不需要每天重装。macOS字体使用系统Arial Unicode。

在仓库根目录执行（先核实asof确实是最近已完成交易日，不自动猜节假日）：

```bash
adhoc_jobs/us_market_daily/.venv/bin/python adhoc_jobs/us_market_daily/collect.py --asof 2026-10-22 --out contexts/survey_sessions/us_market_daily/2026-10-23
adhoc_jobs/us_market_daily/.venv/bin/python adhoc_jobs/us_market_daily/render.py --out contexts/survey_sessions/us_market_daily/2026-10-23 --report-date 2026-10-23
```

使用新日报目录保存每天快照。同目录重跑默认复用原始行情，以便复核；只有明确需要刷新原始数据时加`--refresh`。更换日期必须同步更换输出目录。Yahoo访问失败、缺完整历史或最近日期不符会报错，检查manifest后再决定能展示哪些标的，不用旧数据冒充新行情。

输出raw JSON、逐标的CSV、metrics JSON/CSV、来源及SHA256清单、60日归一化序列、两张PNG及SVG图。图表是60个连续交易日的60个收盘观测值，首末回报跨59个交易日间隔，不称“60日投资总回报”。每次保留数据口径说明并实际查看PNG；在正文中通过绝对文件路径嵌入图片。

统一使用Yahoo拆股调整的OHLC收盘价，未计现金分红再投资；high_52w是当日向前364个日历日的盘中最高价（左开右闭）。50/200日均线使用同一价格序列。量比为当天成交量除以前20个交易日平均成交量，不包含当天。观察价先恢复高点至报价精度，再用十进制四舍五入到美分。

重要交叉核验发现：2026-10-06 QQQM盘中高点Yahoo为314.11，Stock Analysis为314.12；最新四标的收盘价一致，成交量小幅不同。本次不混源，Yahoo统一计算，QQQM15%观察价266.99（另一源267.00）；在日报标注微小差异，不把一美分差别当新信号。
