# AI 订阅额度共享池：可行性评估与产品方案

日期：2026-08-27

## 结论

如果这里的额度指 ChatGPT Plus/Pro、Claude Pro/Max、Cursor 等个人订阅里的使用限额，需要把“能不能实现”和“能不能作为获得厂商许可的长期业务”分开判断。通过 OAuth 凭证代理、设备码授权或本机 worker，工程上可以让陌生用户的请求消耗贡献者的个人订阅容量；但这不是服务商账本里的 token 转账，通常也没有得到上游对账号共享和转售的许可。

OpenAI 明确规定个人账号不得提供给他人使用，Service Credits 不可转让、出售或交易；其商业协议也禁止买卖或转移 API key、规避 usage limits。Anthropic 的个人条款禁止共享账号凭证，商业条款允许 API 驱动客户自己的产品，但转售服务需要 Anthropic 明确批准。Cursor 当前条款禁止出租、出借或出售其服务。相关依据见 [OpenAI Account Sharing Policy](https://help.openai.com/en/articles/10471989-openai-account-sharing-policy)、[OpenAI Service Credit Terms](https://openai.com/policies/service-credit-terms/)、[OpenAI Services Agreement](https://openai.com/policies/services-agreement/)、[Anthropic Consumer Terms](https://www.anthropic.com/legal/consumer-terms)、[Anthropic Commercial Terms](https://www.anthropic.com/legal/commercial-terms) 和 [Cursor Terms of Service](https://cursor.com/terms-of-service)。

可以继续研究的版本，是把产品改为以下两类之一：

1. 单一组织内的 API / Enterprise shared pool：企业统一采购额度，平台提供成员限额、弹性 overage、成本归集和闲置预测。这条路径已有官方产品先例，例如 OpenAI Enterprise/Edu 的 [workspace shared credit pool](https://help.openai.com/en/articles/20001001-setting-usage-limits-in-chatgpt-enterprise-and-edu)。
2. 获得服务商书面授权的 API usage broker：平台作为 customer application 向终端用户提供服务，用自己的商业合同、API project 和账本清算。用户之间交易的是平台定义的服务额度，个人账号、个人订阅和个人 API key 不进入池子。

第二类仍然有商业合同、支付资金、数据跨境、内容安全和单位经济问题，属于 Conditional go。建议先从第一类做 B2B 成本优化产品，再决定是否扩展为跨组织市场。

## TokenShare 反例带来的修正

[TokenShare 的贡献页面](https://token-share.app/zh/join)证明了个人订阅池在工程上有可执行路径。页面允许贡献者通过设备码 OAuth，把 ChatGPT 订阅中的 Codex 容量或符合条件的 Grok 账号接入共享池；买方使用统一的 OpenAI-compatible API。[定价页](https://token-share.app/zh/pricing)显示买方预充 USD、按 token 扣费，贡献者按照账号实际承接的请求获得分成。

它没有在上游账号之间划转 token。实际链路是：

```text
贡献者完成 consumer OAuth
→ 平台保存或控制可持续调用的授权凭证
→ 买方请求进入统一网关
→ 平台选择一个贡献账号并以该账号身份调用上游
→ 按调用量扣买方预付余额并给贡献者分成
```

这条路径与原方案的“闲置容量流动起来”高度相似，因此“个人订阅池技术上不可行”的表述需要撤回。更准确的判断是：它是技术可行、条款风险公开存在、长期供应稳定性尚未得到厂商背书的 marketplace。

TokenShare 自己的[服务条款](https://token-share.app/zh/terms)也明确披露了这层风险：其他用户的请求会通过贡献者凭证发出，上游可能据此认定账号违反服务条款，并采取限流、封禁或永久封号；平台无法代为恢复账号，也不承担贡献者的订阅费、余额和自用受影响等损失。贡献页还在遇到 OpenAI `unsupported_country` 时提示使用全局 VPN。这些信息说明其产品选择是把上游封禁和地域风险转移给自愿贡献者，而不是已经消除了风险。

TokenShare 还修正了原方案中的两个产品设计点：

1. 它只在请求真实完成后给贡献者分成，没有把“打开共享”当成交付。这个守恒条件应当保留。
2. 它让买方预付现金，没有用“借 token、冻结押金、未来贡献后解冻”的信用模型。这样避免了负余额、追偿、margin call 和押金挤兑，但新增了预付余额、贡献者收入和平台结算合规。

截至本次检查，没有在其公开条款、隐私政策或联系页面看到运营公司法定名称、注册地、厂商授权或 reseller 身份。隐私政策也没有具体说明 OAuth refresh token 的保存方式、请求内容是否落库、贡献者能否接触请求、数据保留期限、跨境接收方和安全事件责任。因此，它可以作为产品和技术 benchmark，不能单独作为合规性、资金安全或长期供应可靠性的证明。

## 产品本质：订阅额度时间银行

本方案的用户不是固定的买方或卖方。同一个 Plus/Pro 用户在空闲时是容量贡献者，在工作高峰时是容量使用者。平台将不同成员不同时段的 subscription capacity 合并，使单个用户获得比个人账号时间窗口更平滑的可用性。

```text
空闲期：自己的账号为其他成员完成请求
→ 获得 Pool Credit

突发期：自己的账号达到限额
→ 消耗 Pool Credit，从当前空闲成员调用

尚未积累足够 Pool Credit 但急需使用
→ 余额暂时为负，按负余额冻结押金

后续自己的额度恢复并真实承接请求
→ 负余额下降，押金按比例解冻
```

这是一种 closed-loop mutual credit，而不是 token 销售。Pool Credit 不提现、不转账、不升值，只代表未来从共享池获得同类服务的请求权。平台收入可以来自固定会员费或明确的基础设施服务费；用户押金始终是可退负债，不能当作平台收入。

### 两类贡献必须分开

- `available_capacity`：用户打开共享、账号健康且愿意接单。这是可调度供给，不立即产生信用。
- `settled_delivery`：账号真实完成了其他成员的请求，并通过 meter 结算。这才增加用户的 Pool Credit 或冲减负余额。

如果仅凭“保持在线 5 小时”就发放等额信用，期间没有其他成员使用，平台会凭空发行未来兑付义务。可以给在线账号少量 availability score、排队优先级或会员权益，不能把它等同于实际贡献额度。

### 账户模型

每个成员同时拥有：

- `pool_balance`：正数代表未来调用权，负数代表需要用后续贡献或现金清偿的额度；
- `available_collateral`：可退押金；
- `locked_collateral`：为负余额冻结的押金；
- `contribution_policy`：个人保留比例、允许贡献时段、最大并发和模型范围；
- `account_health`：成功率、最近限流、重置时间、撤权和风控状态。

基础记账可以采用：

```text
pool_balance_i(t+1)
= settled_supply_CU
 - consumed_pool_CU × scarcity_multiplier
```

正常供需下 `scarcity_multiplier = 1`。池子接近耗尽时，它可以提高到 1.2–1.5，减少非紧急消耗；也可以完全不用动态倍率，改用排队和每人 burst cap。第一版建议 1:1 记账，规则更容易被用户理解。

允许透支时：

```text
borrow_limit = collateral / stressed_replacement_price
locked_collateral
= max(0, -pool_balance) × stressed_replacement_price × collateral_ratio
```

用户后续每完成 1 CU 的真实供给，`pool_balance` 增加 1 CU，负债和锁定押金随之减少。用户在约定周期内没有完成回补，平台才使用押金购买 fallback capacity，履行对正余额成员的请求权。

### 时间银行最大的风险是未来集中兑付

前期贡献已经被别人消耗，贡献者获得的是对未来成员供给的请求权。如果很多成员在同一时段集中使用，账面 credit 足够，实时 capacity 仍可能不足。因此需要同时展示两种状态：

- `我的权益余额`：用户总共可以调用多少；
- `当前池流动性`：现在能否立即兑现、需要排队多久。

平台不能承诺“有 credit 就必定即时可用”，除非另有自营 API reserve。可以设计两级服务：普通请求走 best-effort pool；紧急请求在池子不足时由平台 API reserve 补齐，再从押金、会员费或保险准备金结算。

### Plus 与 Pro 如何共池

套餐名称不直接决定兑换比例。Pro 只是通常能提供更多容量，贡献收益仍按实际完成的 CU 计算。第一版只做同一 provider、同一类模型的池子，并把 input、output、cache 和 tool usage 换算成统一 CU。跨 OpenAI、Claude、Grok 的 credit 需要分账，等积累足够数据后再提供汇率。

### B 用户如何在 Codex 中消费 A 用户的额度

这里的“Key 接入”和“调用平台 API”不是两个方案，而是一套接入的两个部分：B 用户持有平台签发的 API Key，用它调用平台提供的 OpenAI-compatible Responses API。B 永远不接触 A 的 OpenAI access token、refresh token 或登录态。

```text
A 通过官方 OAuth 授权
        ↓
平台 Credential Broker 保存加密凭证
        ↓
B 的 Codex ──平台 Key──> 平台 /v1/responses
                              ↓
                     鉴权、余额和押金校验
                              ↓
                     调度并租约锁定 A/C/D
                              ↓
                     以被选账号的短期凭证
                     向上游发起本次请求
                              ↓
                     SSE 回传 B，完成双边记账
```

B 的客户端只需在用户级 `~/.codex/config.toml` 配置一个自定义 provider：

```toml
model_provider = "elastic_pool"
model = "gpt-5-codex"

[model_providers.elastic_pool]
name = "Elastic Pool"
base_url = "https://api.example.com/v1"
env_key = "ELASTIC_POOL_API_KEY"
wire_api = "responses"
```

```bash
export ELASTIC_POOL_API_KEY="pool_b_xxx"
codex
```

Codex 随后把 `Authorization: Bearer pool_b_xxx` 和 Responses API 请求发送给平台。平台 Key 只标识 B、权限、额度和限速，不对应任何一个固定贡献账号。Gateway 为每个请求动态选择健康供给账号并建立短租约；Credential Broker 在服务端取得该账号的短期 access token；Provider Adapter 再调用上游。这样同一个 B 的连续请求可以在 A、C、D 之间切换，但同一条有状态会话应保持粘性，或由平台统一维护并转换 conversation state。

如果产品目标是“用户自己的 Pro 额度用完后无感借池”，Codex 必须从一开始就始终连接平台 Gateway，而不是先直连 OpenAI、触顶后再修改 provider。Gateway 把该用户自己的 OAuth 凭证设为 `priority=SELF`：正常时所有请求仍消耗自己的订阅；检测到明确限额错误、达到用户设置的保留阈值或本账号进入 cooldown 后，在同一个平台 Key 和同一个 SSE 连接模型下切换到 `priority=POOL`。恢复窗口到达后再自动切回 SELF。

```text
同一个 Codex 配置、同一个平台 Key、同一个 Gateway
                 ↓
          SELF 凭证仍有容量？
          ├─ 是：使用 B 自己的 Pro
          └─ 否：租用 A/C/D 的池子容量
```

Codex 自身支持通过 profile 或配置切换 provider，但不会替平台完成“ChatGPT Pro 登录态触顶后自动切第三方 provider”。如果先使用 Codex 内置的 ChatGPT 登录，触顶后才启动平台 profile，用户至少需要新开一次 Codex 运行，已有请求也无法透明迁移；它只能作为手动兜底模式，达不到产品定义的无感弹性。

这里的无感边界是“请求级切换”，不是生成到一半后的 token 级热切换。若 SELF 在返回第一个 SSE 内容事件前报告限额，Gateway 可以在内部把同一请求重试到 POOL；一旦已经向 Codex 输出了部分内容，再换账号重放可能产生重复或不一致，应该结束该请求并在下一次请求切池。上游 `previous_response_id` 也可能只在原账号下有效，因此 Gateway 需要签发自己的虚拟 response id、保存必要上下文，并在跨账号时重建输入，不能把上游会话 ID 原样暴露给客户端。

平台至少要兼容 Codex 当前所需的 `/v1/responses`、SSE 事件、错误码、工具调用和 usage 字段。只实现普通 Chat Completions 不足以让当前 Codex 正常接入。上游凭证不得出现在响应、浏览器、本地配置、日志或普通业务数据库明文中，否则 B 可以绕过账本直接消费 A 的账号，甚至形成账号接管风险。

这只是推荐架构，并不意味着 OpenAI 已授权把个人 ChatGPT/Codex OAuth 凭证用于第三方流量。技术上，平台可以像一个 OAuth credential proxy 一样转发；经营上仍要把凭证撤销、上游封禁和接口变化视为可能让供给瞬间归零的核心风险。

## 这套机制真正要解决什么

用户买到的是一段时间内的峰值使用能力，个人需求却不均匀：有人本周空闲，有人今天集中写代码。产品想把这部分时间错配变成可交换价值。一个池子能成立，至少需要同时满足六个条件：

| 条件 | 个人订阅额度 | 平台自有商业 API |
|---|---|---|
| 可精确计量 | 弱，受消息长度、模型、工具和上下文影响 | 强，可按官方 usage meter 对账 |
| 可分割且同质 | 弱，不同模型、时间窗和套餐不可直接互换 | 中到强，可按 provider/model/region 分池 |
| 可依法或依合同转让 | 通常不允许 | 可用于 customer application；转售仍需合同确认 |
| 平台能控制交割 | 弱，需要账号凭证或 consumer OAuth | 强，平台控制 gateway 和 project key |
| 供需错峰 | 未验证；高峰往往高度相关 | 可用真实流量回放验证 |
| 利差覆盖运营风险 | 未验证，封号和欺诈风险可能高于节省 | 可通过采购折扣、路由和 committed-use 优化形成 |

个人订阅模式可以通过代理凭证绕过“没有转账接口”这一问题：平台不转移额度，而是代替贡献者发起请求。它仍然缺少厂商许可和可原子锁定的余额，所以更适合 best-effort marketplace，难以承诺长期 SLA。押金能赔付违约损失，不能在所有用户同时达到限额时制造新的供给。

## 原方案中需要修改的五个机制

### 1. 把 token 改成有明确规格的 CU

不同模型的 input、output、cached input、reasoning、tool call 成本不同，个人套餐还可能按消息窗口而非 token 计量。因此不能用裸 token 作为统一币种。

建议定义 `CU`（Compute Unit）：`1 CU = 某个 provider + model + region + 时间窗下，人民币 1 元的官方 API replacement cost`。用户界面可以显示统一余额，底层账本仍按 provider、model、版本和窗口分别记账。报价时预估，任务完成后按官方 usage true-up。

### 2. 入池不等于交付

用户打开共享开关、展示剩余额度或承诺未来供给，只能生成 offer，不能恢复押金。只有某次请求满足以下条件后，才算有效供给：

- 服务商合同允许这次使用；
- 请求由平台可控制的合法凭证完成；
- 返回成功，usage meter 可核验；
- 没有进入退款、滥用或争议状态；
- 经过短暂 settlement window。

因此，押金解锁条件应当是 `settled_supply_value`，而不是 `sharing_enabled=true`。

### 3. 押金和使用费要分开

押金用于保证负余额，供应者还需要获得回报。否则轻度用户承担账号、隐私和封禁风险，却没有入池动力。

一次借用应同时产生三笔账：借方的 usage debt、供方的 usage credit、平台的 fee/reserve。押金只是 debt 的担保，不是平台收入。用户停止使用时，可用后续真实供给偿债；没有供给则按 replacement cost 清算。

### 4. 额度价值必须 haircut

平台可承诺的实时供给应按以下公式计算：

```text
eligible_capacity
= min(verified_remaining, rate_limit_headroom)
   × permission_factor
   × reliability_factor
   × expiry_factor
   - operational_reserve
```

用于计算长期可承诺供给和 SLA 时，没有服务商书面许可的账号应当令 `permission_factor = 0`；用于明确披露风险的 best-effort 池时，可以把它作为随时可能归零的机会供给单独计算。即将到期、历史交付失败、供应者集中度过高或 provider 状态异常时，其他系数继续下降。用户截图、前端显示的“剩余 80%”和共享开关都不能作为已经完成的资产证明。

### 5. 池子需要拒单和降级

正常状态不是永远有额度，而是报价前知道能否交付。路由应按以下优先级处理：已锁定的合格供给、平台 reserve API、低价替代模型、排队、拒单。产品需要明确显示 provider unavailable、额度不足、报价变化、执行超额、供应撤回、清算中和争议状态。

## 建议的账本与状态机

每个用户至少有四个余额：

- `available_collateral`：可提现押金；
- `locked_collateral`：为未偿 usage debt 冻结；
- `usage_credit`：真实供给后获得，可用于未来消费；
- `usage_debt`：已经消费但尚未用供给或现金结清的负债。

核心状态流如下：

```text
供应：offer_created → verified → reserved → executed → metered → settled
                                      ↘ failed / expired / revoked

借用：quoted → collateral_locked → delivered → outstanding
                                      → repaid_by_supply
                                      → paid_in_cash
                                      → liquidated / disputed

押金：pending → available → locked → withdrawal_pending → refunded
```

账本使用 append-only double entry，所有余额都由分录汇总，不能直接改数字。供应 offer、请求、官方 usage record、报价、分录和清算记录需要可追溯。consumer password、session cookie 和 consumer OAuth token 不应进入系统；商业 API key 使用 project/service account，并放入 KMS/HSM，按项目设置 spend limit 和 rate limit。

## 押金模型如何计算

建议公式：

```text
locked_collateral
= outstanding_replacement_cost
   × (1 + price_volatility_buffer + fraud_buffer + liquidation_buffer)
```

如果 replacement cost 为 `100 CU`，三个 buffer 合计 20%，就锁定 120 元。用户后来实际供应并结算 40 CU，只能按 40 CU 冲减 debt，并按相同比例解锁。只要任务尚未被别人真实消费，就没有新增价值可用于偿债。

这会暴露一个商业问题：当抵押率接近 120%，重度用户直接购买按量 API 往往更简单。共享池只有在以下条件同时成立时才有吸引力：

- 用户未来确实有闲置供给，可以用服务而不是现金偿债；
- 池内成交价比公开 API replacement cost 低至少 15%–25%；
- 平台能提供统一入口、模型路由、预算控制或账单管理等额外价值；
- 供给的合规、故障和隐私成本没有吃掉折扣。

因此，押金机制不是主要护城河。真正的价值来自合法采购折扣、跨模型路由、企业预算控制和可审计账本。

## 一个示例经济模型

下面只是验证模型的示例参数，不代表市场价格：

| 项目 | 每 1 CU |
|---|---:|
| 借方成交价 | 0.80 元 |
| 供方获得的 usage credit / 应付款 | 0.58 元 |
| 支付、计量、风控和客服 | 0.08 元 |
| 风险准备金 | 0.08 元 |
| 平台贡献毛利 | 0.06 元 |
| 公开 API replacement cost | 1.00 元 |
| 初始锁定押金 | 1.20 元 |

这组参数看似给借方节省 20%，但必须通过四个压力测试：

1. 供给只有预测值的 70%：平台需要 reserve API 补齐或拒绝 30% 请求。押金只能赔钱，不能补吞吐。
2. 最大供应者失效，占池子 20%：单一 supplier/provider 需要 concentration cap，reserve 至少覆盖清算延迟期的 P99 replacement cost。
3. 上游价格上涨 30%：120% 抵押率已经不足，需要 margin call、缩短债务期限或由 reserve 承担损失。
4. 用户需求在工作日 14:00–18:00 高度相关：日均仍有大量闲置，峰值 fill rate 也可能低于可用标准。MVP 必须按 5 分钟粒度回放，不看月均利用率。

此外还会出现 adverse selection：轻度用户发现长期闲置后会降级套餐，留下的多是高消耗借方；重度用户更容易在高峰一起耗尽额度。池子的供给质量会随产品成功而下降，定价和准入模型要持续重算。

一组更保守的合成压力数据能说明风险量级：100 名用户声称愿意共享 30,000 SU，按账号可用率 90%、到期折扣 85% 和高峰相关性 80% 计算，有效供给只有 18,360 SU；再把接单上限控制在 70%，最大 outstanding claims 是 12,852 SU。若借用费只有 3%，满负荷月收入约 386 元。重压情景下，当期供给降到 6,000 SU、fallback 单价上涨到 1.5 元，平台需要立即支付约 10,278 元。若叠加 10% 押金盗刷或 chargeback，未覆盖损失约 2,878 元，相当于约 7.5 个月的毛手续费。这里的参数只用于压力测试，但它说明低费率和高可退押金难以同时维持。

## 三个产品版本

| 版本 | 技术可行性 | 条款与合规 | 单位经济 | 建议 |
|---|---:|---:|---:|---|
| 个人订阅 OAuth 代理池 | 7/10 | 1/10 | 6/10 | 可做高风险 best-effort 实验，不适合作为有 SLA 的长期供给 |
| 单一企业内部 shared pool | 9/10 | 8/10 | 7/10 | 首选切入点 |
| 获书面授权的跨组织 API broker | 7/10 | 5/10 | 5/10 | 第二阶段，先签合同再开发 |
| 开源模型 GPU 算力池 | 7/10 | 7/10 | 6/10 | 机制更匹配，但属于另一种产品 |

### 推荐切入点：企业 AI Usage Treasury

平台连接企业自己的 OpenAI/Anthropic/云厂商商业账号，提供：

- 团队、项目和个人预算；
- shared pool 与 overage policy；
- provider/model 路由和 fallback；
- 成本预测、异常检测和 chargeback；
- committed credits 到期预警；
- 部门间内部结算。

这里不需要向个人收押金，也不托管个人订阅凭证。企业已经拥有统一采购合同，平台只做可观测性、分配和优化。产品先证明能把企业实际成本降低 15% 以上，再谈跨企业清算。

### 第二阶段：授权的 mutual-credit market

只有在至少一家 provider 或正式 reseller 给出书面许可后，再引入跨组织供给。平台定义的 usage credit 保持闭环、不可提现转让；供应方如需现金结算，走合同、发票、税务和持牌支付渠道。此时产品更接近 API marketplace，而不是订阅拼车。

## 中国境内经营需要先确认的边界

这部分需要中国律师和支付机构根据实际资金流出具意见，下面仅用于识别 blocker。

- 《电子商务法》要求收取押金时明示退还方式和程序，不得设置不合理条件，并要求平台核验经营者、保存交易记录、履行消费者和个人信息保护义务，见[市场监管总局转载的法律全文](https://www.samr.gov.cn/zfjcj/tzgg/art/2023/art_d337c3291e8b40459ca03dea54395856.html)。
- 如果平台代收待付、允许用户余额在多方之间支付，可能进入支付业务和备付金监管的判断范围。《非银行支付机构监督管理条例》要求支付业务许可，禁止挪用备付金，并要求备付金存放在人民银行或合规商业银行，见[中国政府网条例全文](https://app.www.gov.cn/govdata/gov/202312/17/510339/article.html)。具体是否适用取决于资金流，不能仅靠把余额命名为押金规避。
- 如果平台向境外模型服务商发送用户 prompt、代码、账号信息或日志，需要完成个人信息处理告知、最小化、DPA 和个人信息出境路径评估。相关要求见[个人信息保护法第三十八条](https://www.cac.gov.cn/2021-08/20/c_1631050028355286.htm)和[个人信息出境标准合同办法](https://www.cac.gov.cn/2023-02/24/c_1678884830036813.htm)。
- 如果目标用户位于中国大陆，OpenAI 明示从不支持地区访问或向该地区提供访问可能导致账号封禁；Anthropic 当前 supported countries 列表不含中国大陆，并明确说明不向中国提供 commercial access，见 [OpenAI unsupported countries policy](https://help.openai.com/en/articles/9131992-chatgpt-and-api-services-in-unsupported-countries-and-territories)、[Anthropic Supported Countries](https://www.anthropic.com/supported-countries) 和 [Anthropic 关于中国商业访问的说明](https://www.anthropic.com/news/detecting-and-preventing-distillation-attacks)。若第一市场是中国大陆，直接汇集 OpenAI/Claude 的方案应视为 No-go。
- 面向公众提供生成式 AI 服务、撮合第三方经营者并向其结算收入，还要分别确认生成式 AI 服务规则、ICP/EDI、平台涉税信息报送、贡献者收入和发票义务。它们取决于最终产品、合同和资金流，不能用一张通用许可清单替代属地预沟通。

资金设计上，第一版优先使用持牌支付机构的预授权、分账或银行监管账户。平台自己的运营账户不沉淀用户押金，也不把押金用于上游采购和风险准备金。风险准备金来自股东资本或平台收入，不能来自用户可退资金。

## MVP：先验证六件事，再写完整平台

### Phase 0：两周纸面门禁

1. 选定一个 provider、一个国家/地区、一个具体额度类型。
2. 取得 provider 对 customer application、终端用户、转售/结算模式的书面答复。
3. 让律师画出资金流、合同流、数据流，确认押金、预付余额、发票和个人信息角色。
4. 任何一步需要 consumer password/session、规避区域限制或绕过 usage limit，立即停止该版本。

### Phase 1：四周离线仿真

找 5–10 家愿意提供脱敏 usage export 的团队，按 5 分钟粒度回放 30 天。只做计算，不碰真实账号。输出：

- 可节省金额与节省比例；
- 峰值 fill rate；
- provider/model/时间窗错配率；
- P95/P99 reserve 需求；
- 最大供应者失效和价格上涨压力结果；
- 按团队、项目、用户的预算策略。

### Phase 2：封闭 B2B pilot

使用平台或试点企业拥有的商业 API project，20–50 名内部成员，资金只走企业合同。实现 gateway、meter、append-only ledger、限额、fallback 和审计；暂不做 P2P 供应、不收个人押金。

建议门槛：

- 相比未优化基线节省至少 15%；
- 请求 fill rate ≥ 99%；
- 账单差异 ≤ 0.5%；
- 单一 provider 故障时有明确降级，不能静默跨越数据边界；
- 风控和支付成本后贡献毛利 ≥ 10%；
- 无 consumer credential、无不支持地区流量、无未解释资金沉淀。

连续两个账期达到门槛，再进入授权 market 的谈判。任何 provider 拒绝该业务形态、节省低于 10%、峰值 fill rate 低于 95%，或合规成本使贡献毛利为负，都应作为 kill criterion。

## 最终建议

这个想法抓住了真实问题：大量订阅额度在时间窗口结束时失效，而用户需求存在峰谷差。TokenShare 说明个人订阅容量可以通过 OAuth 代理形成可调用的机会供给，但这种供给不是上游认可的可转让资产，并且可能随封号、撤权、限流或地区策略立即消失。

产品应明确定位为 Subscription Capacity Time Bank，而不是低价 token 市场。同一个用户可以跨时间在贡献者和使用者之间切换：真实贡献形成 Pool Credit，未来突发调用消耗 Pool Credit；押金只为负余额提供临时授信，后续真实贡献会冲减负余额并解冻押金。

底层可以复用 TokenShare 的 OAuth 代理、健康检查、路由和计量方式，上层不采用买卖报价和现金分成。第一版建议先做 earn-first：用户贡献后才能调用池子，不允许负余额，用最小复杂度验证供需错峰和实时 fill rate。第二版再加入有押金担保的 borrow-first。两版都必须把“权益余额”和“当前池流动性”分开显示，并把 consumer capacity 定义为可能限流或撤销的 best-effort 供给。
