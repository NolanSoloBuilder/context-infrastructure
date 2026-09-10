# AI 订阅额度共享池研究笔记

日期：2026-08-27

## 研究对象的三种资产

1. Consumer subscription quota：个人 ChatGPT / Claude / Cursor 套餐中的消息数、五小时窗口、周限额或动态 fair-use。通常不可转让，也不存在官方扣划 API。
2. Prepaid API credits：有金额或 token 计量，但余额通常仍归属于单一客户或组织；能否用于面向终端用户的应用、能否转售，要看商业条款与书面授权。
3. Platform-owned API capacity：平台以自己的商业 API 合同向终端用户提供应用服务。平台可以在自己的账本中做共享额度、成员限额和 overage，但这已是 API gateway / usage broker，不是个人订阅余量交易。

## Claim Extraction

| Claim | 来源层级 | 验证通道 | 当前状态 |
|---|---|---|---|
| 个人订阅中存在可划转的 token 余额 | 用户方案假设 | 官方使用限额、账户和 credit 条款 | 已反驳：典型个人套餐是账号绑定、窗口化使用权；OpenAI credits 明示不可转让 |
| 押金可以保证池子随时兑付 | 机制假设 | 会计恒等式、峰值压力测试 | 已反驳：押金只覆盖违约损失，不增加瞬时供给或 provider rate-limit |
| 用户开启入池即可恢复押金 | 机制假设 | 交割状态机 | 已反驳：只有其额度真实承接了其他用户请求并完成结算，才产生可用于偿债的供给 |
| 个人账号可以通过代理共享给其他用户 | 技术假设 | OpenAI / Anthropic / Cursor 官方条款 | 已反驳或高风险：账户凭证共享、转售、规避 usage limit 普遍受限 |
| API 模式允许平台服务终端用户 | 官方商业条款 | OpenAI Services Agreement、Anthropic Commercial Terms | 部分验证：允许 API 驱动 customer application；转售、密钥交易仍受限，需按 provider 和合同确认 |
| 用户押金可由平台直接沉淀和冻结 | 产品假设 | 中国电子商务、支付和预付资金规则 | 未确认：押金退还规则必须明示；如果形成代收待付、预收余额或清算功能，需要持牌支付/银行存管与律师出具具体业务定性 |

## 核心会计模型

设 `1 CU` 等于同一 provider、model、region、时间窗口下的 1 元上游标准 API 成本。跨模型不能直接按 token 个数等价。

- 借用 `x CU`：借方负债增加 `x`，锁定押金 `x × reference_price × collateral_ratio`。
- 供给 `y CU`：只有请求成功完成、官方 meter 可核验后，供方才获得 `y` 的正余额；仅声明在线不记账。
- 归还：借方后续实际交付的 CU 先冲减负债，再按比例解锁押金。
- 到期：未归还负债以押金按 replacement cost 清算，平台 reserve 吸收滑点、封号、供应中断和价格变化。
- 供应奖励：正余额可以换未来使用权或现金结算；若没有奖励，供给侧没有入池动力。

池子的基本约束：

`可承诺供给 <= 已验证可用额度 × 条款可用系数 × 到期折扣 × rate-limit headroom - 风险准备金`

## 初步判断

- 个人订阅余量 P2P 池：通过 consumer OAuth 凭证代理可以实现；没有上游书面授权时属于高封号、高供应波动的风险模式，不应再写成“技术不可行”。
- 平台统一采购 API，再做内部共享账本：Conditional go。
- 单一企业 / 团队 workspace 内的共享 credit 和成员限额：最适合作为第一版。
- 开源模型 GPU 算力池：资产可计量、可调度，但已变成算力市场，应作为另一条产品线评估。

## TokenShare 反例

- 贡献方式：ChatGPT Codex / Grok consumer account，通过设备码 OAuth 授权。
- 交割方式：其他用户的请求通过贡献者凭证发出，不是 provider ledger transfer。
- 买方：预付 USD，按 token 逐请求扣款。
- 供方：实际承接请求后按既定比例获得分成。
- 风险归属：TokenShare 条款明确说明可能违反上游账号共享规定，限流、封禁和永久封号损失由贡献者承担。
- 信息缺口：公开页面未见运营主体法定名称、厂商授权、OAuth token custody 细节、prompt retention 与贡献者数据隔离说明。

## 用户确认的产品定位

- 产品是 Subscription Capacity Time Bank，不是 token marketplace。
- 同一用户在空闲期贡献真实服务量，获得未来调用权；突发期从其他成员的当前闲置容量调用。
- `pool_balance > 0` 表示已贡献形成的未来权益；`pool_balance < 0` 表示先使用后贡献形成的临时负债。
- 押金只给负余额提供信用担保；后续真实 `settled_delivery` 冲减负余额并解冻押金。
- 必须区分账面权益与实时流动性。即使用户有正余额，成员集中使用时仍可能排队；即时保证需要平台自营 API reserve。
- 推荐分阶段：先做 earn-first 正余额池，再加入押金担保的 borrow-first。
