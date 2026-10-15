# Cited Alpha Creem 正式支付接入

用户请求：审核通过后启用正式支付，完成 checkout、webhook 与权益流程。用户已明确确认创建正式 API 密钥并配置到 GCP Secret Manager。

## 实时核对

- Creem NolanBuilder 首页显示已上线并可接受付款，test mode 关闭。
- 正式商品 Plus `prod_145udTrucAXz6itiTAoXZb`：USD 15/月；Pro `prod_12gGE9AnEvdfdfd7rIVgTg`：USD 90/月，税费另计。两者 active、API mode=prod。
- 两个商品已通过 Dashboard 保存客服邮箱 `support@forgepane.com`、return URL `https://cited-alpha.forgepane.com/app/billing/success`；官方 API 回读一致。
- 正式 API key 权限限定为 checkout 读写、product read、customer 读写、subscription read、webhook 读写，未开启全访问。密钥只保存在仓库外私有文件与 Secret Manager。
- 正式 Webhook `wh_4TvsUDGSSUULHXgWgAKaUB` 指向 `https://api-cited-alpha.forgepane.com/api/v1/billing/creem/webhook`，监听 checkout.completed 及 paid/scheduled_cancel/canceled/expired/paused/past_due/unpaid/trialing。
- 生产原来无 creem 配置，Waffo 已启用。本次保留 Waffo。

## 实现及验证

- Backend [PR 42](https://github.com/NolanSoloBuilder/mindspace_backend/pull/42)：live 配置对应官方 prod 事件；owner scoped portal；数据库唯一 checkout reservation 避免多次/并发新单；Creem live 只在已付周期内授权益。113 项 billing 测试通过。
- 真实 MySQL 仅在 acceptance 库验收：10 并发 reservation 仅1赢家、6重复event仅1处理、owner冲突事务回滚、旧事件及到期边界通过。临时记录精确清理，未写生产数据。
- Web [PR 39](https://github.com/NolanSoloBuilder/mindspace_web_frontend/pull/39)：订阅管理、focus刷新、60秒服务端权益轮询。22 项 focused tests，生产构建、35个SEO路由验证通过。全仓TS仍有其他区域既有错误。
- 主仓有大量其他任务改动，全部保留；生产只发布独立billing变更。

## 发布结论

两仓正式发布完成，Secret Manager v12 的 live/enabled 配置已生效。正式扣款尚未发生，不能将商品创建、审核通过、测试或checkout创建等同于正式付款/权益链路验收。

## 运维边界

unknown checkout 创建结果不按TTL自动解锁，必须按 request_id 在Creem核对，避免重复周期扣费。订阅升级不通过另购一份实现；先管理已有订阅。不得用模拟 paid 事件为真实用户开权益。

### 已完成的发布证据

- Web merge `101160977a0eb452cd9a8c4f78a0b78eeb7c4b7f`，Actions [35297547648](https://github.com/NolanSoloBuilder/mindspace_web_frontend/actions/runs/35297547648) success，Pages `91e10181.cited-alpha-web.pages.dev`，正式域名 smoke 通过。
- Backend merge `7d553ff8f27036d1518f726705003c1838abea85`，Actions [35297829796](https://github.com/NolanSoloBuilder/mindspace_backend/actions/runs/35297829796) success；revision `cited-alpha-api-00053-cdd` 已100%流量，初次部署使用 Creem disabled 配置。
- 线上 webhook 非变更性 healthcheck：错误签名400，正确HMAC签名200 ignored，无订单/权益写入。此检查不是Creem真实付款投递证明。
- Secret Manager v12 已将 Creem 设为 live/enabled，保留 Waffo enabled；Actions [35298529956](https://github.com/NolanSoloBuilder/mindspace_backend/actions/runs/35298529956) 已成功完成正式配置发布。
- 当前用户账号已有手动 Pro（manual，非Creem订阅），未修改权益。用户尚未提供Free验收账号，未进行真实扣款。

### 正式配置已接管流量

- `cited-alpha-api-00054-hf4` 100% 流量，image `release-7d553ff8f27036d1518f726705003c1838abea85-35298529956`。启动晚于 Secret Manager v12 的写入；Creem ready=true、environment=live、Waffo ready=true。正式 health 返回 `Service echo success.`。
- Web feature `feat_codex/creem-live-web-20260918`，commit `608ff91`；Backend feature `feat_codex/creem-live-20260918`，最终 feature commit `25b5700`（实现 `7d71736`）。两仓PR均已合并。
- 会员购买必须从网站内套餐按钮发起，服务端绑定owner metadata；Creem后台静态商品付款链接没有账号绑定，不能作为自动开通会员入口。
- 需要关闭Creem时，以当前最新Secret为基础仅设 `mindspace.billing.creem.enabled=false`，保留其他字段，新增Secret版本并通过同一main workflow发布；不覆盖其他配置，不重用测试key。

### 最终发布状态

正式配置 Actions `35298529956` 已 success；Cloud Tasks queue 回读 `RUNNING`，Scheduler 回读 `ENABLED`，两仓上线流程全部完成。另一次使用数据库既存 mobile refresh token 的只读API验收尝试返回Token invalid，未取得访问token、未创建checkout、未改账号；不据此宣称authenticated API验收通过。

### 线上页面验收

生产域名登录页面打开套餐弹窗，Plus 显示 Monthly / $15；确认页 Creem 选中，Waffo Pancake 未选中且可用，按钮为 Continue to Creem。当前账号已有手动 Pro，未点击创建订单或付款。浏览器核对证明正式支付方式已展示，不证明实际付款或 Creem 真实支付回调成功。

## 后续：套餐直接跳转 Creem（已上线）

用户要求移除支付方式选择弹窗。Plus/Pro 按钮现在直接创建 Creem checkout，并在当前页跳转；保留订阅管理、防连点、失败重试、目录加载 gate 和测试模式提示。Creem 未启用时不允许购买，也不自动切换渠道。后端 Waffo 实现和配置未改。

- Web branch `feat_codex/creem-direct-checkout`，commit `b133eb2c001c4ee50083cab692cccc419a51357f`。
- [PR 40](https://github.com/NolanSoloBuilder/mindspace_web_frontend/pull/40) merged，merge SHA `e44064e45a57be59dc5615c6fb720a10d46ccf97`。
- [正式发布 Actions 35300106878](https://github.com/NolanSoloBuilder/mindspace_web_frontend/actions/runs/35300106878) success；Pages `8b223fe4.cited-alpha-web.pages.dev`，main，部署命令绑定上述 merge SHA。
- 16 项组件/回跳测试通过，完整构建、35 SEO 路由及 CI 正式域名 smoke 通过。额外回读 `/app` HTTP 200，private/no-store、noindex/nofollow。
- Chrome 控制出现 debugger unattached / timeout，本次线上浏览器点击回读未完成。没有真实扣款，不将 mock 跳转验证当作实付验收。
- 只涉及前端，无 migration；未动其他主仓未提交改动。回滚可通过 revert PR 40 后重新走 main 发布。

## 后续：当前档位及低档位按钮禁用（已上线）

服务端已计算 canUpgrade，前端补齐按钮及点击处理双重门禁。当前档位显示当前方案，低档位显示不可降级订阅并禁用；缺失 canUpgrade 时禁止操作。独立管理入口保留。

- branch `feat_codex/billing-tier-buttons`，commit `d5a47a59bc3dd3886a5af421c901895e19b35c8c`。
- PR https://github.com/NolanSoloBuilder/mindspace_web_frontend/pull/41 merged；merge SHA `07f14b1bcf3b9dd98d2e0ffe9a44c95136a647b4`。
- Actions https://github.com/NolanSoloBuilder/mindspace_web_frontend/actions/runs/35300713094 success；Pages `1117de85.cited-alpha-web.pages.dev`，main，source SHA 为上述 merge。
- 20 项测试通过，涵盖 Free/Plus/Creem Pro/manual Pro；完整生产构建与35 SEO路由检查通过；正式域名 smoke 通过。
- Chrome 线上加载完成后实际回读：当前徐昊账号 Free/Plus 均为 disabled Not available for downgrade，Pro 为 disabled Current plan。未点击付款、未改权益。
- 仅Web变更，无迁移，无付费调用，工作区干净，其他仓改动未纳入；回滚可 revert PR41 后走main发布。

## 手动权益恢复 Free（2026-09-18 11:00 CST）

用户明确要求将 webxuhao@163.com 之前手动改库的 Pro 恢复为 Free。生产 cited_alpha 库精确核对唯一用户，唯一有效权益为 billing_subscriptions.id=22，provider=manual，无真实支付订阅或 checkout 关联。事务锁定并备份原记录至仓库外权限600文件后，将该记录置 canceled、结束时间设当前UTC并追加撤销原因。只更新1行，不删除历史，不动 pending Waffo 记录或其他用户。提交后回读有效订阅数0，按当前 billing DAO/service 默认规则有效档位为 Free。无需代码发布。

## 左下角会员身份展示（已上线）

按用户确认方案：Free 展示 FREE + 升级到 Plus，Plus 展示 PLUS + 升级到 Pro，Pro 展示不可点击 PRO · 当前方案。独立 SidebarPlanIdentity 消费有效权益接口，focus 和套餐弹窗开关时刷新；加载占位、失败中性入口，按 token 隔离结果并忽略过期响应。设置新增方案与账单入口，继续使用现有 PricingDialog 管理路径。

- Web branch `feat_codex/sidebar-plan-identity`，commit `a69cb56`，PR https://github.com/NolanSoloBuilder/mindspace_web_frontend/pull/43 已合并，merge SHA `79bdca77b68e94dec60e08cdb120a3bbac3ce4af`。
- Actions https://github.com/NolanSoloBuilder/mindspace_web_frontend/actions/runs/35302101698 success；Pages `197d808e.cited-alpha-web.pages.dev` main，source SHA 同上述 merge，正式域名 smoke 通过。
- 37 项侧栏/身份/套餐组件测试通过，完整生产构建和35 SEO路由通过。Chrome 线上截图检查当前 Free 身份及升级按钮，设置 Plan and billing 点击成功打开套餐弹窗。Plus/Pro、收起、加载失败、账号切换、focus 刷新由组件测试覆盖，未通过修改真实账号来模拟。
- 仅前端变更，无迁移，无实付或权益修改，其他主仓改动未纳入。回滚可 revert PR43 后走main发布。
