# 美股日报数据、图表与 HTML

已完成首次手动验证：北京时间2026-10-23，对应美东2026-10-22常规收盘。此脚本只读公开行情并生成本地文件；不连接券商或交易。图表不能代替每次的联网新闻、官方日历、收益率和重要价格交叉核验。

现有隔离环境：`adhoc_jobs/us_market_daily/.venv`，Python 3.12，matplotlib、pandas；不需要每天重装。macOS字体使用系统Arial Unicode。

在仓库根目录执行（先核实asof确实是最近已完成交易日，不自动猜节假日）：

```bash
adhoc_jobs/us_market_daily/.venv/bin/python adhoc_jobs/us_market_daily/collect.py --asof 2026-10-22 --out contexts/survey_sessions/us_market_daily/2026-10-23
adhoc_jobs/us_market_daily/.venv/bin/python adhoc_jobs/us_market_daily/render.py --out contexts/survey_sessions/us_market_daily/2026-10-23 --report-date 2026-10-23
```

使用新日报目录保存每天快照。同目录重跑默认复用原始行情，以便复核；只有明确需要刷新原始数据时加`--refresh`。更换日期必须同步更换输出目录。Yahoo访问失败、缺完整历史或最近日期不符会报错，检查manifest后再决定能展示哪些标的，不用旧数据冒充新行情。

输出raw JSON、逐标的CSV、metrics JSON/CSV、来源及SHA256清单、60日归一化序列、两张PNG及SVG图。图表是60个连续交易日的60个收盘观测值，首末回报跨59个交易日间隔，不称“60日投资总回报”。每次保留数据口径说明并实际查看PNG；Markdown底稿通过绝对文件路径嵌入图片，再生成HTML交付。

## HTML 交付

2026-10-28用户要求将产物改为HTML。主产物为每日目录中的 `report.html`，同时保留 `report.md`、原图和来源数据，以便复核。HTML只转换已核验日报的展示，不重新请求行情、修改观察阈值或更新提醒状态。验收示例为 `contexts/survey_sessions/us_market_daily/2026-10-28/report.html`。

先完成当日的行情、Reddit核验和 `report.md`，再执行：

```bash
node adhoc_jobs/us_market_daily/render_html.mjs --out contexts/survey_sessions/us_market_daily/2026-10-28 --report-date 2026-10-28
```

每次同步替换目录和北京时间日报日期。脚本使用已有Node环境与 `marked`；优先解析本地依赖，缺失时使用Codex自带运行时中的版本，无须每天安装。样式和交互分别在 `report.css`、`report_interactions.js` 中维护。

- 单文件内嵌两张图、样式、交互及底稿链接的本地JSON/CSV；关联Markdown作为可展开的附录。离线可阅读，外部来源保留原链接。
- 支持目录跳转、图表放大、完整指标折叠、手机横向查看宽表和打印。页面不加载CDN、远程字体或行情接口。
- `report.md` 的一级标题为日报名称与日期；正文独立加粗行作为章节标题。今天对用户最重要的事、主观察表和入场研究默认展开；行业、Reddit、事件日历、完整数据与口径默认收起，目录跳转会自动展开。未知章节保留原文。
- 引用限于 `us_market_daily` 归档内，每个本地附件最多3MB；缺失附件、日期不符或不支持的引用会报错，不静默删除证据。若转换失败，仍发送文字摘要并说明HTML缺口。
- `html_manifest.json` 记录底稿与HTML哈希、图表及附录清单。每次核对日期、关键报价、两张图、来源入口；模板变更时检查桌面与手机排版及展开/放大功能，不必每日重复整套浏览器验证。

聊天中给出简短判断、重要提醒和可点击的HTML文件链接；不再重复粘贴完整长篇Markdown。休市继续使用简版，不把旧图作为新行情。HTML展示不代表草案获批或已交易。

2026-10-28用户进一步要求个性化选题，具体真源见 `contexts/survey_sessions/us_market_daily/research_policy.md`：Google优先、QQQ/QQQM首次建仓判断、低估机会池，不按市值限制；机器人供应链纳入研究。FiNews加入线索来源，重要信息回查原始披露。`collect.py` 独立增加 `RESEARCH = ["GOOGL"]`，按同口径保存价格与指标；原 `WATCH` 四标的提醒范围保持独立。Google的经营与估值证据仍须当次补充，不能用技术回撤替代。

Google专题估值使用 `value_google.py --out <专题目录>`，读取该目录 `google_model_inputs.json`，生成十年FCFF、资本桥、终值ROIC约束、反向DCF及敏感性。`plot_valuation.py --out <专题目录>` 从计算结果绘制明确标注为未来情景的图，不生成历史价格。模板可选 `--title 'Google估值与机器人机会'` 创建专题HTML；不传则保留美股观察标题。新财报必须先核验并更新输入，不能每天盲跑六月基线冒充最新估值。首次审阅记录、最终检查及研究观察价分别在专题目录和 `valuation_research_watch.json` 中；它们不扩展原四标的回撤提醒合同。

统一使用Yahoo拆股调整的OHLC收盘价，未计现金分红再投资；high_52w是当日向前364个日历日的盘中最高价（左开右闭）。50/200日均线使用同一价格序列。量比为当天成交量除以前20个交易日平均成交量，不包含当天。观察价先恢复高点至报价精度，再用十进制四舍五入到美分。

重要交叉核验发现：2026-10-06 QQQM盘中高点Yahoo为314.11，Stock Analysis为314.12；最新四标的收盘价一致，成交量小幅不同。本次不混源，Yahoo统一计算，QQQM15%观察价266.99（另一源267.00）；在日报标注微小差异，不把一美分差别当新信号。

## 盘前盘后与 SOFI（2026-10-29）

`RESEARCH`由下述分类名单派生（含GOOGL、SOFI等），仍独立于原`WATCH`四标的。先收集最新已完成常规交易日，再执行：

```bash
adhoc_jobs/us_market_daily/.venv/bin/python adhoc_jobs/us_market_daily/collect_extended.py --asof 2026-10-28 --out contexts/survey_sessions/us_market_daily/2026-10-29
```

每次替换正确的美国常规交易日和北京日报目录。输出`extended_quotes.json`和`extended_raw/<UTC采集时间>/`下的原始分钟数据/不可变快照；常规日线和提醒状态不改动。盘前以其日期之前最近一次常规收盘作分母，允许新一天盘前与上一天盘后同时存在；盘后以同日常规收盘作分母。缺时段数据或分母须明示，不能补0。未来再次运行会新取数，不能沿用今天的快照。

价格为Yahoo盘前盘后窗口内最新正值分钟收盘。零成交量可能是延续报价，不能称为最新实际成交或保证可成交价格；引用前检查时段和第二来源，并注明差异。原始快照可保留排查过程，日报只引用最后核验的有效记录。下一盘前尚未开始时写明，不把上一交易日盘前当今天。重大盘后事件应进入首页，原四标的收盘提醒合同仍不扩展。

HTML新增`盘前与盘后观察`、`SOFI研究观察`两个默认展开栏目及导航；完整历史盘前/跨源差异可放折叠附录。新增SOFI只表示研究关注，银行资产负债与工业企业DCF口径分开。

## 分类观察总表（2026-10-29最新）

`watchlist_groups.json`是展示分类与采集范围的共同真源，当前12项：指数ETF、机器人、AI/半导体、金融科技、价值、现金管理。`collect.py`从中派生研究名单，`collect_extended.py`覆盖全部分组标的，提醒合同继续只认原WATCH四项。

完成采集后，在日报目录维护`watchlist_research.json`（逐symbol的`status`和`next`，由本次研究核验后填写），运行：

```bash
adhoc_jobs/us_market_daily/.venv/bin/python adhoc_jobs/us_market_daily/render_watchlist.py --out contexts/survey_sessions/us_market_daily/2026-10-29 --report-date 2026-10-29 --next-session 2026-10-29 --premarket-status not_started
```

日期、下一交易日须先核交易所日历；盘前已开始则使用`--premarket-status read_quotes`。输出`watchlist_table.md/json`，将Markdown正文放在首页重点事项之后，不再分别放主表/盘后表/SOFI行情表。`extended_verification.json`若有同一session且常规分母匹配的明确跨源报价，展示可采用该核验值并保留来源时点；其余使用已采集、标注单源的有效分钟参考。不把孤立16:00边界柱当成最新盘后，不把尚未开始的盘前填成昨日报价。没有研究结论者默认估值待完成，不自动认定低估。

HTML支持“分类观察总表”，按分组首行加底色，宽表在自身容器横向滚动。Google/SOFI/机器人详情默认折叠，导航可展开；重大变化先提首页。旧的build_report.py是10/29早报基线生成器；交互更新的真源仍为report.md及当天更新脚本，不要不经合并重跑基线覆盖分类表。

## 关注清单卡片专题（2026-10-30）

分类真源现18项，新增SPMO/MAGS/SOXX/DRAM/VGT/MRNA；原四标的提醒不变。专题卡片替代单张大表，独立数据模型保留持仓/财务/报价各自日期及缺口。复算示例：

```bash
python3 adhoc_jobs/us_market_daily/render_catalog.py --data contexts/survey_sessions/us_market_daily/2026-10-30/watchlist_catalog/catalog.json --out contexts/survey_sessions/us_market_daily/2026-10-30/watchlist_catalog/report.html
```

此命令只渲染已核验数据，不联网。新日期须先制作新catalog.json，不能复制旧报价冒充最新。输入是结构化groups/assets；输出单文件HTML和catalog_manifest.json，支持本地搜索、分类筛选和来源折叠，全部事实在JSON中。DRAM显式标成立日期和allow_short_history，采集器仅对已登记新基金允许短历史，缺指标为null；52周不完整的高点/回撤分别保存为available_history_*，不写入52周信号。

## 实际持仓本地基线

2026-10-30开始，portfolio_private/latest.json保存经授权读取的持仓快照，目录已由本机.git/info/exclude排除。两种行情采集器额外读取实际持仓证券代码（例如GOOG），与研究名单取并集后去重；不发起券商登录，不向行情manifest写入股数、成本或账号。缺少该文件时仍可正常运行研究名单。持仓复核日与行情日分别注明，不以新行情日期暗示重新核验了股数。

## 统一ETF/个股布局与风险指标（2026-10-30更新）

清单卡片渲染会从分类名单聚合资产属性：10只ETF在一起，8只个股另列，题材仅留作卡片定位。样式直接读取report.css，附加catalog.css；不要复制出不同设计语言。先完成发行人资料与catalog.json，再按最近已完成美国交易日执行：

```bash
python3 adhoc_jobs/us_market_daily/catalog_metrics.py --catalog contexts/survey_sessions/us_market_daily/2026-10-30/watchlist_catalog/catalog.json --out contexts/survey_sessions/us_market_daily/2026-10-30/watchlist_catalog --asof 2026-10-29
python3 adhoc_jobs/us_market_daily/render_catalog.py --data contexts/survey_sessions/us_market_daily/2026-10-30/watchlist_catalog/catalog.json --out contexts/survey_sessions/us_market_daily/2026-10-30/watchlist_catalog/report.html
```

每次更换日期、目录与实际已完成session；不盲跑旧快照构造脚本覆盖最新研究/持仓标签。risk_metrics.json/CSV、metrics_*_daily.csv和raw/metrics_*带采集时刻保存。收益/波动/MDD用Adj Close，MA用Close；不足一年和不足200日明确标记，异常跳变通过quality_overrides记录价格复核状态并就近提示。共享CSS改动后应检查日报与清单；Browser明确阻止本地URL时不得改走其他浏览器或HTTP路由绕过，保留视觉未验收状态。

### 最新清单：17项与个股行业

2026-10-30用户移除QQQ，纳指100仅留QQQM；当前9ETF＋8个股。collect.WATCH缩为QQQM/VOO/BRK-B，QQQ有效提醒历史归档到retired_symbols，不改历史检查交易日。个股行业由watchlist_groups.json的industry_id/industry提供，目录分互联网与AI服务、半导体与算力、工业自动化与机器人、金融科技、医疗与生物科技、保险与综合经营。render_catalog.py使用相同字段，ETF全部集中，个股分行业。不要用旧快照构造脚本重新引入QQQ。

## 固定本地观察台

用户现要求紧凑概览、hover详情及无需每次重新生成HTML的刷新入口。启动：

```bash
adhoc_jobs/us_market_daily/.venv/bin/python adhoc_jobs/us_market_daily/catalog_server.py --background
```

固定入口：http://127.0.0.1:8789/ 。可双击start_catalog.command启动；不会登录券商或交易。进程detach后继续服务，但当前未启用登录自启动，重启机器后需重启服务；已有每天07:30任务可执行同一幂等命令。日志在~/Library/Logs/CodexMarketCatalog/，PID在contexts/survey_sessions/us_market_daily/live_catalog/server.pid。停止前须先核对PID确为本服务，不处理其他进程。

页面“刷新行情”真实POST/api/refresh，后台更新17份历史+17份时段参考；GET/api/status提供进度，GET/api/state提供单一原子快照。客户端GET/读取已渲染最新内容，DOMParser只替换catalog-assets/data-times/export，保留当前筛选与页面，不location.reload。HTML/CSS/JS本地内嵌，常规指标与最新时段参考分开。发行人/财报事实不会由自动行情刷新改写，保留各自日期。

只有固定路径被服务；不开放目录，private不可读。Host/Origin+X-Catalog-Refresh:1限制跨站；刷新单任务并发、60秒冷却、失败保留last-good。测试见test_catalog_server.py；用.venv/bin/python -m unittest discover -s adhoc_jobs/us_market_daily -p test_catalog_server.py执行定向测试，无浏览器旁路。
