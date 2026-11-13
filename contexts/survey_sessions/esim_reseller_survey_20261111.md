# 个人经营旅行 eSIM 网站：供货、接入与利润

调研日期：2026-11-11。只读公开资料，未注册、充值、购买或联系供应商。价格为公开目录快照，不是签约报价；经营数据未经审计。

个人开发者可以完成这类产品，批发采购与白标交付已经产品化。长期经营的关键是客源、售后和收款条件。个人开发不等于任何地区的自然人均可直接签约经营，具体取决于上游审核、销售地区和收款主体。

## eSIMPal 的供货来源

[创始人 Reddit 自述](https://www.reddit.com/r/SideProject/comments/1w72lrt/my_esim_app_makes_2x_my_swe_salary_how_i_found/)明确承认转售，原话为 “The connectivity is wholesale”。但没有公开批发商名称。

[创始人 GitHub](https://github.com/deniurchak)写有 “a modular eSIM provider architecture”，说明设计支持供应商模块化，不能证明实际同时接入多家。[隐私政策](https://www.getesimpal.com/en-US/privacy)仅笼统提及 network partners。子任务检查首页公开加载的27个JS，也未找到可靠的上游接入标记。Docomo、SoftBank等是目的地接入网络，不是直接采购对象的证据。

创始人在同一 Reddit 帖自报六个月做到约5,600美元/月，未能确定净利润；已有Yadaphone用户及联盟渠道。自报首发约50万曝光带来45次付款、约800美元收入。这说明不能把现成客源带来的增长直接外推到零基础新站。

## 上游选择

| 供应商/产品 | 公开条件 | 适用判断 |
|---|---|---|
| eSIM Access / Redtea Mobile | 50美元起充，无最低订购量，API/后台 | 小规模验证首选候选 |
| eSIM Access Express | 19美元/月，首月免费，自备Stripe及供货账户 | 现成白标网页店铺 |
| eSIM Go 直连 | Standard前三月每月充值1万美元，合计3万美元 | 不适合小预算试水 |
| Keepgo | 旅行分销API及免费sandbox，完整商务价需核实 | 备选询价 |
| 1GLOBAL | 商务onboarding后发凭据，未核实公开最低承诺 | 后续规模化候选 |

来源：[eSIM Access官网](https://esimaccess.com/)、[Express](https://app.esimaccess.com/)、[eSIM Go定价](https://www.esimgo.com/pricing)、[Keepgo sandbox](https://partnerfaq.keepgo.com/kb/faqs-for-api-partners-a8b112da5c93573f/how-does-the-sandbox-work)、[1GLOBAL快速入门](https://docs.connect-api.1global.com/getting-started/quickstart/)。

eSIM Go旧开发文档仍写无最低用量，新商务页却有首次三个月充值承诺。预算采用新页，签约仍须确认；充值是可消费的供货余额，不是平台手续费。

[eSIM Access FAQ](https://esimaccess.com/faq/)称注册后可购买，大批量购买需要商业资料；不构成任何自然人都能经营的保证。[合作协议](https://esimaccess.com/docs/terms-of-service/)明确充值余额不可退，订单取消退回余额与提现退款不同。

## 真实批发价与售价参照

[官方价表](https://app.esimaccess.com/public/current-price)前端标注“Wholesale price in USD”。[公开数据接口](https://app.esimaccess.com/api/public/products)时间戳为2026-11-11T00:00:04.904+00:00；主线程与子任务分别只读核验。样本已保留到 `tmp/esim_reseller_20261111/price_samples.json`。

| 套餐 | eSIM Access批发USD | eSIMPal首页零售USD | 参照商品毛利率 |
|---|---:|---:|---:|
| 英国5GB/30天 | 2.38 | 5.90 | 59.7% |
| 泰国5GB/30天 | 2.70 | 8.90 | 69.7% |
| 美国5GB/30天 | 3.40 | 9.90 | 65.7% |
| 日本1GB/7天 | 0.70 | — | — |
| 日本3GB/15天 | 1.70 | — | — |
| 日本5GB/30天 | 2.70 | — | — |

零售来源：[eSIMPal首页](https://www.getesimpal.com/en-US)。毛利率=(售价-采购价)/售价。跨供应商比较只是测算，网络、出口IP、可充值范围和售后不一定相同；不是eSIMPal实际成本、毛利或产品等价证明。充值手续费、汇兑及税均未计入表格。

## 单笔利润模型

以美国套餐9.90美元售价、3.40美元公开采购价测算。以下其他费用均为自设预算假设，不是供应商报价或行业均值：

- 支付费按4%+0.30美元：0.696美元。
- 退款/故障损失准备按收入3%：0.297美元。
- 客服折算0.50美元/单。
- 固定软件成本50美元/月，100单时摊0.50美元/单。
- 获客前结余4.507美元/单；CAC=2美元时约2.51美元，CAC=5美元时约亏0.49美元。

以上还未扣税、额外换汇、余额充值费和开发投入，不能称最终净利润。低客单价下固定支付费和人工客服占比明显；在该假设下首次订单可承受CAC上限约4.51美元。若每单最终只留2美元，月赚2000美元需要约1000单，按9.9美元客单对应约9900美元营收。

## 接入路径与关键合同

技术路径：注册与审核→充值→服务端获取密钥→同步套餐与价格→客户付款→校验支付回调→幂等下单→查询/接收开卡结果→交付二维码/安装链接→用量、充值、退款与对账。

[eSIM Access API](https://docs.esimaccess.com/)有套餐、下单、查询、充值、取消及webhook接口，无独立sandbox，生产测试会消耗余额。上游超时不能直接再次扣款下单；需要保存本地订单、供应商订单与ICCID对应关系，先查状态再补偿。密钥只放服务端。

同卡跨国复用不是统一保证。API文档说国家套餐一般补同国家，区域套餐补同区域；应按ICCID查询可充套餐。零流量访问自己网站涉及网络侧能力，也不能仅靠前端实现。网页换logo与手机设置里显示自有运营商品牌不是同一服务。

[取消规则](https://esimaccess.com/making-an-api-cancel-request/)允许未安装且未使用profile取消退回余额；不能据此向用户承诺所有已使用订单无条件退款。

[Stripe支持地区](https://stripe.com/global)列出香港等地区，未列中国内地为Payments开通地区。Express依赖自己的Stripe账户，不能只凭19美元月费推断已解决收款。经营地、销售地、税务和资质需要在确定市场后专项核对，本次不提供特定法域可经营的结论。

## 建议验证顺序

先选择一个明确客群、少量目的地，比较同规格真实网络及报价；用50–200美元供货测试余额和现成网页店铺验证真实购买、安装及充值，预算为试验建议、不含主体和收款设立成本。先拿20–50笔真实订单观察获客成本、安装失败、客服耗时和退款损失。初期单供应商即可，但保留供应商与自身商品的映射；需要复购与家庭管理时再定制，不先开发原生App或承诺全球一卡永久通用。

结论边界：已确认个人开发可行、低门槛供货方案存在、公开套餐采购价格。eSIMPal具体上游、合同折扣、真实利润、上游实测网络质量仍未知。
