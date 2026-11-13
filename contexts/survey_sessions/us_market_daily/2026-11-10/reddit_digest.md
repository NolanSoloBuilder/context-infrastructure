# Reddit 信息观察｜北京时间 2026-11-10

本次为**部分覆盖**：六社区 New / Top 日窗均尝试读取，但 Top 全部为陈旧缓存；仅 r/investing 直接 RSS 成功取得绝对时间和完整正文，另外五社区单次 HTTP 429 后停止。不能把这一结果写成“六社区均无新增”。采集主窗口为 11/8 23:38–11/9 23:38 UTC，以下两帖均在 24 小时内；所核公司事件分别发生于 11/5 和 11/4，并非当天新财报。正文与实质评论已读，不采用未独立核验的股价、赞数或评论热度。

## 1. TEAM：FDE 已有可核的上市公司经营披露，估值仍要拆开迁移与现金成本

- **新增讨论 / 已核验历史披露，未完成估值。** [r/investing 原帖](https://www.reddit.com/r/investing/comments/1xrp3ik/atlassian_grew_revenue_24_last_quarter_guided/)，北京时间 **11/9 19:17:14**。公司 11/5 官方股东信明确本季度扩大 FDE 项目，连接更多系统、定制 Rovo agents / 自动化，推动跨团队流程落地；没有单列 FDE 收入或利润。[官方股东信](https://s206.q4cdn.com/270053503/files/content_files/index-4.html)
- **经营与现金流意义：** FY27Q1 收入 17.72150 亿美元、云收入增长 30.5%；FY27 云增长指引 26%，其中迁移贡献中到高个位数百分点。不能将全部云增量归功于 AI。季度 CFO 4.68530 亿美元减资本支出 0.05976 亿美元，FCF 为 4.62554 亿美元；SBC 为 3.56487 亿美元。简单 FCF 减 SBC 为 1.06067 亿美元，只是自定义保守敏感性代理，不能当完整正常化股东收益或直接年化。[SEC 财报](https://www.sec.gov/Archives/edgar/data/1650372/000165037226000049/ex991q1fy27.htm)
- **最强反证：** 迁移收入是真实收入，云需求和 GAAP 盈利改善也是真实结果；不能把收入确认时点效应等同需求坍塌。评论反方强调 SBC、净股数和现金工资替代。官方同时预计 FY27 更多现金工资替代股权使 non-GAAP 利润率受约 3 个百分点影响，历史表面 FCF 倍数因而不能直接外推。
- **对研究的判断：** 这补强了“上市公司在做 FDE / 应用落地”的证据，适合与 NOW、CRM 比较商业化和现金质量；不自动加入监测清单、不认定低估。下一步核 FDE / Rovo 付费增量、迁移外增长、净股数及正常化现金流，再结合独立核价建保守估值。部分 Data Center 产品计划 2029-03-28 终止支持，Bitbucket / Bamboo 例外，Jira Align 不在本次范围。[官方产品政策](https://www.atlassian.com/licensing/data-center-end-of-life)

## 2. Google：应用落地与基础设施投入可以同时增长

- **新增讨论 / 已核验历史投资计划，电力挤出效应待核。** [r/investing 原帖](https://www.reddit.com/r/investing/comments/1xrqkig/aluminium_supply_faces_growing_competition_for/)，北京时间 **11/9 20:36:26**。Google 11/4 公告计划在 **2027–2028 年**向马来西亚投资 **150 亿美元**，推动超过 1GW 新清洁发电容量，并承担自身用电和直接电网接入成本。这是未来计划，不能算已支出，也不能直接加到已有集团资本开支指引之外。[Google 官方公告](https://blog.google/intl/en-my/company-news/inside-google/google-investment-malaysia-digital-infrastructure-november-2026/)
- **为何重要：** AI 应用发展不等于基础设施现金压力结束；应核资本开支分年付款、合同收入回款和转固折旧。公告未给出这些项目的独立回报或 Cloud 订单，尚不足以改变 Google 的安全边际结论。
- **反证与下一核查：** 原帖承认半岛数据中心与砂拉越铝厂涉及不同电网，不能写成当下争抢同一电力资源；新增供电也可能缓解约束。帖中铝供需预测与具体交易未逐项核原始来源，不纳入已核判断。1GW 发电装机不等于全天候稳定供电或数据中心负荷。

## 访问、去重与未采纳

- NVDA 11/8 董事会声明此前已报道，本次不重复。新的隔夜 / 盘中收益分解帖未核绝对日期与计算，未采用；主观 AI 估值打分帖缺时间与客观分母，未采用。
- 五社区 RSS 429、Top 缓存陈旧是**访问 / 时效缺口**，不是“没有新帖子”。
- 今日 FiNews 实际 HTTP 页面为 11/9 版，但 web 工具缓存仍显示 11/6。FiNews 把 11/11 银行假日写成“市场休市”，NYSE 2026 日历并无该美股休市安排；不可沿用。[NYSE 日历](https://www.nyse.com/trade/hours-calendars)
- `reddit_state.json` 未修改。仅在主任务确实发布对应内容后，才将相应帖子 / 主张记为已报道；不能将本次标为完整六社区成功扫描。

记录：[reddit_sources.json](reddit_sources.json)；[FiNews 核验](finews_check.json)。复核截至 2026-11-09T23:45:10.415388+00:00。
