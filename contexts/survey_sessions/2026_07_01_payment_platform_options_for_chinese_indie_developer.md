# 中国个人独立开发者 MoR / 收款平台选择

日期：2026-07-01

## 背景

用户以中国个人身份做独立开发，希望申请可用于 SaaS、软件、AI 工具、数字产品的海外收款平台。此前 Lemon Squeezy `dashboard.lemonsqueezy.com/register` 页面出现 404。

## 当前判断

Lemon Squeezy 官方文档当前指向 `app.lemonsqueezy.com`，旧 `dashboard.lemonsqueezy.com/register` 不应继续依赖。Lemon Squeezy 2026 年更新中强调正在向 Stripe Managed Payments 迁移，Managed Payments 仍处于扩张/早期访问状态，不应作为唯一上线路径。

用户明确有香港银行卡，但身份和居住地是中国大陆。这个条件只能作为 payout instrument 使用，不能当作香港身份、香港居住地或香港商业主体。所有申请里应保持 KYC 真实一致：大陆居民、中国国籍、中国居住地址；只有在平台明确允许个人用香港个人银行账户收款，且收款人姓名与 KYC 姓名一致时，才使用港卡。

对中国个人独立开发者，优先级如下：

1. **Dodo Payments**：最适合作为第一申请对象。官方 FAQ 明确支持没有注册公司的个人 / unregistered business；中国在 merchant account/payout 支持列表中；产品定位覆盖 SaaS、AI、数字产品、订阅、usage-based billing。风险是平台较新，合规审核和资金冻结规则要严格遵守。
2. **Creem**：适合作为并行备用。支持 China 和 Hong Kong；中国个人 payout 官方写的是 Alipay，business recipient 是 local bank account。适合 SaaS、AI tools、软件和数字产品。风险是中国个人 payout 有额度限制，且 payout fee 为 7 USD/EUR 或 1%，取较高者。
3. **Paddle**：成熟 MoR，适合更完整的 SaaS/software。官方支持“software businesses anywhere”但排除制裁/高风险国家，中国不在 unsupported list。审核更偏成熟业务，建议产品网站、条款、隐私、退款和支持邮箱准备完整后申请。
4. **Polar**：开发者体验强、价格透明，但 payout supported countries 列表未包含中国大陆，只包含 Hong Kong/Macao/Taiwan 等。仅持有港卡而没有可匹配的香港身份/主体时，不应假设能通过。
5. **PayPro Global / FastSpring**：成熟 MoR，适合有一定收入或 B2B/SaaS 形态更稳定后申请。早期个人产品可能销售门槛和沟通成本较高。
6. **Gumroad**：适合电子书、模板、课程、一次性数字下载，不适合作为 SaaS/API 订阅的主支付基础设施。
7. **PayPal 直接收款**：可作为临时 fallback，但不是 MoR，不处理全球税务和合规，争议和风控不确定性较高。

## 申请前准备

- 产品官网公开可访问，写清产品用途、功能、价格。
- 准备英文 `Terms of Service`、`Privacy Policy`、`Refund Policy`、support email。
- 避免提交咨询、代写、金融建议、灰产工具、绕过平台规则等类别。
- 身份、地址、payout account 的姓名必须一致；不要用港卡包装成香港身份。
- 若平台支持中国个人 payout，优先按中国个人身份如实 KYC；只有平台明确允许大陆个人 KYC 搭配香港个人银行账户时，再使用港卡路径。
- 不要因为有港卡就在账户国家、居住地或商业所在地选择 Hong Kong。这样会制造 KYC mismatch，后续 payout 或账户审核更容易被卡。

## 主要来源

- Lemon Squeezy Getting Started: https://docs.lemonsqueezy.com/guides/getting-started
- Lemon Squeezy 2026 Update: https://www.lemonsqueezy.com/blog/2026-update
- Dodo FAQ: https://docs.dodopayments.com/miscellaneous/faq
- Dodo accepted countries: https://docs.dodopayments.com/miscellaneous/accepted-countries-and-territories
- Dodo pricing: https://dodopayments.com/pricing
- Creem introduction: https://docs.creem.io/getting-started/introduction
- Creem supported countries: https://docs.creem.io/merchant-of-record/supported-countries
- Creem payouts: https://docs.creem.io/merchant-of-record/finance/payouts
- Paddle supported countries: https://www.paddle.com/help/start/intro-to-paddle/which-countries-are-supported-by-paddle
- Polar supported countries: https://polar.sh/docs/merchant-of-record/supported-countries
- Polar pricing: https://polar.sh/resources/pricing
- PayPro Global: https://payproglobal.com/
