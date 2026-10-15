# 当前大语言模型榜单快照

查询日期：2026-10-12。各榜单分别比较，避免混合不同评分或推理配置。

## Artificial Analysis 综合 Intelligence Index

精选模型与分数（同模型可有多种推理配置，以下非连续名次）：

| 模型配置 | 分数 |
| --- | ---: |
| Claude Opus 5.5 max with fallback | 58 |
| Claude Sonnet 5.5 max with fallback | 56 |
| Claude Opus 5.5 xhigh with fallback | 56 |
| GPT-6 Astra max | 53 |
| Gemini 4 Argon high | 53 |
| GPT-6.1 Sol max | 52 |
| MiMo V2.6 Pro | 46 |
| Qwen3.8 Max 0902 | 45 |
| GLM-5.3 max | 45 |
| Kimi K3 max | 44 |
| MiMo V2.6 Flash | 38 |

max / high 等配置影响分数、延迟和成本。AA 任务成本是其评测口径，不能直接当产品单请求账单。

## Arena 编程偏好榜

页面数据日期 2026-10-08。精选名次：Gemini 4 Argon high 第 1（1562，Preliminary），Claude Fable 5 high 第 2（1551），Claude Opus 4.7 high 第 3（1550），Claude Opus 4.6 high 第 4（1550），Claude Opus 5.5 high 第 5（1550），GPT-6.1 Sol max 第 8（1545），GPT-6 Astra max 第 9（1542），Kimi K3 max 第 10（1540），MiMo V2.6 Pro 第 11（1539），MiMo V2.6 Flash 第 45（1514）。

MiMo Pro 为 1107 票，分数区间 ±18，排名区间 1-47；不能把名义第 11 理解成固定领先关系。Arena coding 衡量代码回答的人类偏好，不能直接证明仓库级 Agent 任务完成率。

Arena 总体榜默认页面：MiMo Pro 第 26（1480），Flash 第 76（1451）。默认口径与 raw/no-style-control 榜存在差异。

判断：MiMo Pro 在综合评测中属于较强模型，结合此前核验的低 token 价格，值得列入低成本 Agent 主力候选；这属于基于榜单与价格的选型判断，需要实际业务评测验证。Flash 更适合预算优先的任务候选。

来源：
- https://artificialanalysis.ai/leaderboards/models
- https://arena.ai/leaderboard/chat/text/coding
- https://arena.ai/leaderboard/chat/text
- https://vercel.com/ai-gateway/leaderboards/models （usage 榜，不等同能力榜）
