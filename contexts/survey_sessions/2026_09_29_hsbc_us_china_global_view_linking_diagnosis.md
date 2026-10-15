# HSBC 美国与中国账户 Global View 关联故障诊断

日期：2026-09-29  
范围：只读检查用户提供的截图、当前已登录页面状态与汇丰公开说明；未提交新的关联请求，未读取或记录账户号、密码、验证码等敏感信息。

## 结论

当前证据更支持美国端 Global View 服务或美国客户档案配置异常。美国个人网银已经可以正常登录，但 `Add or remove a country/territory` 页面在发起中国关联之前，读取“已关联国家/地区”时就返回 `We're sorry, this service is temporarily unavailable`。随后跳转到美国站 `gvtermsandconditions` 的关联流程也返回 `your request to link has not been completed`。

这组现象不能仅凭域名断言根因一定属于美国账户，因为中国端发起关联时也会跳转到美国站完成美国端认证。不过，美国端 Global View 自身无法读取关联列表，是目前最有区分度的证据，排查应优先从美国侧开始。

## 已核验事实

- 汇丰美国官网仍把 mainland China 列为 Global Transfer/Global View 支持地区，中国与美国之间的产品能力仍然存在。
- 中国内地账户需要通过网页网银关联；美国 App 当前列出的直接关联地区只有 UK、Hong Kong、Singapore、Expat 和 UAE。
- 美国官网要求：两地均已注册网上银行、具备另一地区的登录凭据，并使用 HSBC Security Device 生成的 log on security code。部分关联最多需要 48 小时完成。
- 当前美国网银页面显示已登录，国家选择器已选中 China；“链接国家/地区”按钮和错误页上的重试按钮在页面状态中均为启用。
- 当前 Global View 页面仍携带旧式 `__EntryPageParams` 和 `/bin/dsp/postback.html` 回跳参数。旧会话或失效回跳可能放大故障，但不能单独解释美国端关联列表加载失败。

## 建议顺序

1. 若美国账户、美国 Digital Banking 或中国账户刚开通/刚注册不足 48 小时，先满 48 小时再试。
2. 完全退出两地网银，关闭所有汇丰标签页。从 `https://www.us.hsbc.com/` 首页新开会话，登录时使用 Security Device / Digital Secure Key 生成的安全码，再进入 `My HSBC > Add or remove a country/territory`。不要复用含 `__EntryPageParams` 或 `/bin/dsp/postback.html` 的旧标签页。
3. 若“已关联国家/地区”区域仍先报 `service temporarily unavailable`，停止重复尝试，直接联系 HSBC US。请客服检查：
   - 美国账户是否已启用 Global View / Global Transfers；
   - 美国客户档案是否存在 pending、failed 或 duplicate Global View link；
   - 美国账户是否被正确标记为 Premier/eligible；
   - 是否需要后台清除失败的 link request 或重新 provision Global View profile；
   - 中国与美国两端的姓名、出生日期及客户身份资料能否匹配。
4. 推荐优先使用美国 App 或网银内的 secure chat，保留两条英文错误文案和发生时间。若致电，HSBC US Premier 官方号码为美国/加拿大 `888-662-4722`，境外 `716-841-6866`，官网列示 24/7。

## 给客服的英文描述

> I can log on to HSBC U.S. Online Banking successfully, but the Global View “Add or remove a country/territory” page already shows “This service is temporarily unavailable” when loading my linked countries. When I try to link my HSBC China account, the U.S. Global View Terms & Conditions page says the linking request has not been completed. Please check whether Global View is provisioned on my U.S. customer profile and whether there is a pending, failed, or duplicate link request that needs to be cleared. Please also confirm that my U.S. account is eligible and that my customer details can be matched with HSBC China.

## 官方来源

- HSBC US Global View and Global Transfers: https://www.us.hsbc.com/international-banking/global-view-and-global-transfers/
- HSBC US Move Money FAQ: https://www.us.hsbc.com/help/move-money/faqs/
- HSBC US Contact Us: https://www.us.hsbc.com/customer-service/contact-us/
- HSBC China Transfer Payments FAQ: https://www.hsbc.com.cn/en-cn/transfer-payments/faq/
