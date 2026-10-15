# Vercel AI Gateway 与 MiMo 官方按量价格对比

核对日期：2026-10-12。范围为相同 MiMo 模型的实时推理，不含 Token Plan、赠送额度、支付手续费或汇率成本。

每百万 tokens，顺序为未缓存输入 / 缓存命中输入 / 输出：

| 模型 | Vercel（美元） | 小米海外（美元） | 小米国内（人民币） |
| --- | --- | --- | --- |
| mimo-v2.6-flash | 0.14 / 0.0028 / 0.28 | 0.14 / 0.0028 / 0.28 | 1 / 0.02 / 2 |
| mimo-v2.6-pro | 0.435 / 0.0036 / 0.87 | 0.435 / 0.0036 / 0.87 | 3 / 0.025 / 6 |
| mimo-v2.6-pro-ultraspeed | 4.35 / 0.036 / 8.7 | 4.35 / 0.036 / 8.7 | 30 / 0.25 / 60 |

结论：Vercel 与小米海外官方相同模型的标价一致。Pro 网页可能显示 0.43 或 0.44，为显示精度差异；Vercel 公共模型 API 返回输入价格 0.000000435 美元/token，即 0.435 美元/百万 tokens。Vercel 目录提示部分模型价格随 provider 变化，缓存价需按实际 provider 检查。

小米官方批量推理 Flash 与 Pro 为实时价格的 50%；UltraSpeed 不支持。小米文档注明缓存写入限时免费，联网搜索单独收费。旧版 mimo-v2.5 和 mimo-v2.5-pro 将于北京时间 2026-10-21 10:00 下线。

每次 1 万未缓存输入 + 2 千输出 tokens，国内 Flash 约 0.014 元，Pro 约 0.042 元，UltraSpeed 约 0.42 元；Vercel 分别为 0.00196、0.00609、0.0609 美元。此为 token 费用计算，不代表真实请求总账单。

来源：
- https://mimo.mi.com/docs/zh-CN/price/pay-as-you-go
- https://vercel.com/ai-gateway/models/mimo-v2.6-flash
- https://vercel.com/ai-gateway/models/mimo-v2.6-pro
- https://vercel.com/ai-gateway/models/mimo-v2.6-pro-ultraspeed
- https://ai-gateway.vercel.sh/v1/models （本次无鉴权只读查询）
- https://vercel.com/docs/ai-gateway/pricing
