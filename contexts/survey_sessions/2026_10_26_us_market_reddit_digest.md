# 美股日报新增 Reddit 信息观察

用户于北京时间2026-10-26要求：在每天美股报告中汇总Reddit信息，重点关注投资与信息差。已更新现有heartbeat `automation-3`，没有新建重复任务；保留名称“每日美股观察与入场策略”、ACTIVE、每天北京时间07:30及当前聊天。已回读本机automation.toml，核对完整prompt、调度、状态和目标聊天一致。

同时将任务快照中的投资期限修正为用户已明确的3–5年、希望控制回撤；预算、最大可承受亏损仍未知。按时间分批入场方案仍为未确认提案；没有新增交易授权。

## 新栏目

交易日报在行情与行业观察之后、最终策略建议之前加入“Reddit投资与信息差观察”。休市日照常检索，有新线索则并入休市简报；没有值得新增的内容就简短说明，访问失败单独标明，不凑数。每天仍合并发送一次。

优先社区为r/investing、r/stocks、r/SecurityAnalysis、r/ValueInvesting、r/Bogleheads和r/ETFs，按议题补充行业社区。r/wallstreetbets只作为情绪和拥挤交易线索。重点包括宏观与利率、财报和估值、现金流、AI/半导体、电力能源、供需变化、伯克希尔、ETF与美债现金管理，并覆盖有证据支持的其他行业新线索。

每天优先筛选过去24小时，必要时扩展至72小时并标注，精选3–5条且宁缺毋滥。每条包含：

- 核心线索，原帖链接、社区及北京时间发布时间；区分原帖时间和事件发生时间。
- 已核验事实、待核验观点或仅情绪观察的标签。
- 为什么值得关注、与QQQ/QQQM、VOO、BRK.B、SGOV及3–5年控回撤目标的关系。
- 有实质内容的反方论据、不确定性，以及下一项可检查的条件。

关键事实回查公司IR/SEC、政府或交易所等原始来源。阅读原帖正文和有内容的评论，不用搜索摘要代替原文；读不到评论就明示。热度只反映讨论，不能当作真实性、资金流或入场触发证据。信息差是值得核验的公开线索和分歧，不能凭印象声称市场未定价或保证套利。

## 实施与证据边界

当日新增材料写入`contexts/survey_sessions/us_market_daily/YYYY-MM-DD/reddit_digest.md`及`reddit_sources.json`，完整`report.md`含摘要和链接。来源记录保存规范帖子URL/ID、社区、原帖/事件/采集时间、实际读取范围、关键主张、反方论据、核验来源和结论。

后续实际运行时使用`us_market_daily/reddit_state.json`记录成功检查与已报道主张，跨日只报新线索或实质更新，同日重跑去重。读取失败保留上次有效状态，不将失败写成没有新信息。现有`alert_state.json`继续只管理已核验的新交易日价格信号。

本次验证了Reddit首页及部分投资社区可公开读取，但检索页面存在1天至2周的缓存，热门页也包含旧帖。因此自动任务必须按原帖时间和实际可读取内容核验新旧。遵守访问限制，不绕过登录、权限或反爬；公开RSS/搜索仅用于合规定位来源，缺正文或日期时明确降低核验状态。

本次完成配置更新与回读，尚未生成或发送首份新的Reddit每日精选；没有把本次功能配置记为已完成每日内容核验，也未初始化空的去重状态冒充一次成功扫描。原行情图文格式、15%/25%观察阈值、仓位未确认状态和不自动交易约束保持有效。

来源入口：[Reddit](https://www.reddit.com/)、[r/investing](https://www.reddit.com/r/investing/)、[r/stocks](https://www.reddit.com/r/stocks/)、[r/SecurityAnalysis](https://www.reddit.com/r/SecurityAnalysis/)。

## 2026-10-26首次手动试跑

用户随后要求“先跑一个”。已于北京时间16:52–17:04实际检索、阅读原帖与相关评论并核对公司IR及Vanguard资料，生成[首份Reddit观察](/Users/xuhao/Documents/Other/context-infrastructure/contexts/survey_sessions/us_market_daily/2026-10-26/reddit_digest.md)及[来源记录](/Users/xuhao/Documents/Other/context-infrastructure/contexts/survey_sessions/us_market_daily/2026-10-26/reddit_sources.json)，并追加到当日report.md。保留三条：BKD经营改善与资产出售收益、RDDT财报事件与美国用户指标、分批投入的能力边界。

公开JSON接口403，没有绕过或重试；可公开读取的网页足以核验保留项正文，但无法获得全部精确发布时间。RDDT帖子不计为已核实的24小时新帖；其当前财报事件有公司公告。跨日去重仅登记实际报道主张，并保留这些核验缺口，不将本次视为全站完整扫描。行情alert_state.json未修改。
