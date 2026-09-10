# 汇丰香港向嘉信账户转入 HKD

## 结论

当嘉信页面给出的 HKD 收款行是香港本地银行，并同时提供香港 `Bank Code`、`Branch Code` 和收款账号时，`Pay & Transfer` → `Other local payees / FPS` → 通过银行账户号码付款，是 HSBC HK App 提供的候选本地路径。香港银行同业结算有限公司在 2026-08-12 的 FPS 参与机构名单中，将银行代码 `006` 的花旗银行香港分行列为港币实时“支付及收款”参与机构，因此 FPS 在银行间轨道上可用于把港币发送至该花旗账户。尚未确认的是嘉信这个汇集账户是否支持用 FPS 附言自动完成个人证券账户分配；不能把“汇丰显示转账成功”当作“嘉信个人账户已经入账”。

嘉信采用汇集账户收款。银行层面的收款人为 `Charles Schwab & Co., Inc.`；付款附言还必须写入最终入账人的嘉信证券账户号和账户英文姓名。这里的证券账户号来自用户自己的嘉信账户页面，不是收款银行的汇集账户号。

## 填写合同

- 付款账户：与嘉信账户完全同名的汇丰香港本人账户。联名账户需要核对所有账户持有人姓名是否一致。
- 收款银行：按嘉信当前 HKD wire instructions 选择香港花旗及其银行代码。
- 收款账号：如果汇丰只给一个账号输入框，使用 `Branch Code + Schwab Account Number`；如果分行号和账号分成两个输入框，则分别填写，避免重复拼接。
- 收款人名称：按嘉信当前指示原样填写 `Charles Schwab & Co., Inc.`。
- 币种：HKD。
- Message to payee / Reference：`FFC <个人嘉信8或9位证券账户号> <嘉信账户英文姓名>`。
- 地址：只有页面要求时才填。收款人地址与收款银行地址要分别使用嘉信指示中的对应字段。

若 HSBC HK App 没有可供填写并回看 `Message to payee` / `Reference` 的字段，不提交转账，改用 HSBC Online Banking 或先联系汇丰/嘉信确认附言是否会完整传递。没有最终入账信息时，款项即使到达嘉信的汇集账户，也可能需要人工认领。

## 转账前检查

1. 在嘉信登录态中重新打开目标证券账户的 HKD wire instructions，确认银行、分行、汇集账户与当前截图一致。
2. 确认 `FFC` 后写的是个人嘉信账户号和嘉信登记英文姓名。
3. 确认汇丰付款账户与嘉信账户同名。嘉信明确不接受第三方付款。
4. 首次先转小额，并保存 HSBC confirmation page、交易参考号、金额和日期；到账后再转大额。

## 已转出但嘉信未入账

若 HSBC 记录显示成功而嘉信仍未入账，先停止追加付款。FPS 成功只能证明付款指示进入本地支付链路；嘉信使用汇集账户，个人证券账户还依赖付款人信息、个人嘉信账户号和登记姓名完成内部匹配。

处理顺序：

1. 从 HSBC 交易详情保存完整回单，确认状态、支付方式、日期、金额、收款账号末位、交易参考编号，以及 `Message to payee` 是否完整保留。
2. 联系嘉信现有客户支持，请其按付款银行、日期、金额、付款人姓名、交易参考编号和附言人工查找未分配入款；通过登录后的 Secure Message 发送回单，避免在普通邮件里暴露账户资料。
3. 同时联系 HSBC，要求确认款项是否已经由 Citibank 最终接收，并说明真实支付轨道是 FPS、电子结算、RTGS 还是 TT。FPS 一般只有本地交易参考号；TT/跨行追踪才可能有 UETR，不应把普通 FPS reference 当成 UETR。
4. 如果 HSBC 显示失败、退回或待处理，先由 HSBC 处理；如果 HSBC 确认花旗已收款，由嘉信做人工认领或退回判断。

嘉信香港现有客户电话：`+852 2101 0500`；汇丰 Premier 电话：`+852 2233 3322`，其他个人客户电话：`+852 2233 3000`。电话和服务时间仍应以官网实时页面为准。

## 官方依据与证据边界

- [Schwab: How to wire money into your Schwab account](https://www.schwab.com.hk/content/how-to-wire-money-into-your-schwab-account)：说明款项先进入嘉信持有的第三方账户，再依据账户姓名和嘉信账户号内部入账；`For further credit to` 可缩写为 `FFC`。
- [Schwab: Fund Your Account](https://www.schwab.com.hk/fund-your-account)：明确不接受第三方付款，付款账户持有人必须与嘉信账户登记姓名一致。
- [HSBC HK: Transfers and Payments FAQ](https://www.hsbc.com.hk/help/faq/transfers-and-payments/)：HKD 转香港其他银行可在 App 使用 `Other local payees / FPS`，通过银行账户号码、银行名称/代码和收款人姓名付款。
- [HSBC HK: FPS guidelines](https://www.hsbc.com.hk/campaigns/fps/guidelines/)：官方流程允许在付款明细中加入给收款人的 message；提交后应保存确认页。
- [HKICL: List of FPS Participants](https://www.fpsconsole.hkicl.com.hk/pub/p1/FPSD2005.pdf)：截至 2026-08-12，银行代码 `006` 的花旗银行香港分行支持港币 FPS 实时支付及收款；这证明银行间轨道可达，不等于嘉信已完成个人证券账户入账。

具体香港花旗账号属于用户提供的嘉信截图，本轮没有从公开嘉信页面独立复核。每次付款应以登录后的实时 wire instructions 为准。
