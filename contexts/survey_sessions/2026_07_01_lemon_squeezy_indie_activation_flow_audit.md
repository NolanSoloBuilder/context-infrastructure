# Lemon Squeezy 独立开发者激活流程审计

日期：2026-07-01

## 结论

原流程的大方向成立：Lemon Squeezy 新店铺默认处于 Test Mode，可以先完成产品、Checkout、API 和 Webhook 接入；正式收款前需要激活店铺，激活包括业务问卷和身份验证。Lemon Squeezy 作为 Merchant of Record，会做 KYC/KYB 和产品合规审核。

需要修正的点：

1. 审核时间官方口径是通常 2-3 个工作日，不是 1-3 个工作日。
2. Test Mode 和 Live Mode 是隔离环境；live API key、live webhook、live 产品 ID 和 checkout URL 都需要单独配置。
3. 产品从 Test Mode 复制到 Live Mode 后会产生新的唯一 ID，手工粘贴过的 checkout URL 必须更新。
4. 非美国个人需要完成 W-8 税表；缺少税务信息时，payout 可能暂停或阻塞。
5. 非美国银行账户通过 Stripe payout 有 1% per payout 费用；PayPal 非美国账户是 3% capped at $30。
6. Bank payouts 总体以 USD payout 为基础；选择非 USD payout currency 时会按中间价转换。港卡可作为香港银行账户路径，但不要把“港币账户一定最优”写死，美元账户可能减少转换。
7. “设计咨询、代写、web development、consulting”等服务明确属于 prohibited products；SaaS/software、license keys、课程等通常可行。
8. 官方文档只写需要政府签发 ID，没有公开承诺“中国大陆护照通过率最高”或固定使用 Stripe Identity/Persona。实操上可以优先准备护照，但不能写成官方规则。

## 官方来源

- Activate Your Store: https://docs.lemonsqueezy.com/help/getting-started/activate-your-store
- Testing & Going Live: https://docs.lemonsqueezy.com/guides/developer-guide/testing-going-live
- Verify Your Identity: https://docs.lemonsqueezy.com/help/getting-started/verify-your-identity
- Supported Countries: https://docs.lemonsqueezy.com/help/getting-started/supported-countries
- Prohibited Products: https://docs.lemonsqueezy.com/help/getting-started/prohibited-products
- Getting Paid: https://docs.lemonsqueezy.com/help/getting-started/getting-paid
- Fees: https://docs.lemonsqueezy.com/help/getting-started/fees
- Tax Forms: https://docs.lemonsqueezy.com/help/tax-forms
- Currencies: https://docs.lemonsqueezy.com/help/payments/currencies
