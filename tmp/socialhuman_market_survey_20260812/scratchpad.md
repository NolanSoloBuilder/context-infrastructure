# SocialHuman 市场调研 Scratchpad

## Scope

- Reader mode: internal decision memo
- 截止日期：2026-08-12
- 核心问题：SocialHuman 是否真实可用、其真实性验证是否可信、市场需求与采用情况如何、是否有成为独立社区或基础设施能力的可能。

## Phase 1 初步扫描

已确认：

- iOS 与 Android 均已发布；Google Play 当前只显示 `100+` 下载，Android 端尚处极早期。
- App Store 当前版本 `1.0.15`，Google Play 于 2026-07-19 更新；产品仍在连续迭代。
- 运营主体为 2026 年新注册的芬兰公司 `SocialHuman Technologies Oy`，business ID `3627558-3`；产品由 Olli Albert Airola 个人主导。
- 收费为可选 Founding Member：美国区约 `$39.99/year`，芬兰区 `€7.99/month` 或 `€47.99/year`；无广告模式。
- 官方声称使用 EXIF、运动传感器、键入节奏、屏幕翻拍与摩尔纹、视频/音频取证、设备证明等信号；iOS 更新说明称已加入硬件签名的 capture proof。
- 隐私政策承认键入节奏、composition replay 与设备运动属于 biometric-adjacent 数据；原始传感器与视频片段最长保存 7 天，原始键入事件和文本输入回放保存 30 天，聚合指标与部分设备指纹保留更久。
- 产品会使用已验证内容与验证信号训练自己的 verification / AI-detection models；不出售或授权第三方训练。这意味着它是“feed 中拒绝 AI 内容”，不是“整个系统不使用 AI”。
- 创始人公开承认大量代码由 AI 辅助完成；其个人职业形象本身偏 AI advocate，并非反 AI 活动者。

## Claim Extraction

| Claim | 来源层级 | 独立验证通道 | 当前状态 |
|---|---|---|---|
| 所有帖子均由真人在真实设备上现场拍摄 | Tier 1 官网/商店 | 安装实测、独立用户绕过测试、安全分析 | 仅官方主张；尚无独立技术审计 |
| 自动化输入与 AI 文本无法进入平台 | Tier 1 官网/商店 | 输入法、辅助功能、外接键盘、人工转录与脚本绕过测试 | 仅官方主张；“无法粘贴”不能证明文本思想来源 |
| 硬件签名能证明内容来自真实 SocialHuman app 与设备 | Tier 1 App Store 更新说明 | Apple App Attest / Android Play Integrity 机制边界、安全研究 | 能证明 app/device provenance 的部分链条，不等于能证明场景本身真实 |
| 无广告、无跟踪、数据留在 EU | Tier 1 官网/隐私政策 | SDK/流量审计、处理方清单、政策变更记录 | 核心数据库/媒体/验证在 EU；仍使用 US processors；官网曾漏披露 X pixel，后修正为 consent-only |
| 市场存在足够强的 anti-AI / authentic-social 需求 | Tier 1 产品叙事 | 行业调查、竞品增长、迁移行为、留存与付费证据 | 大盘需求存在；是否愿意迁移和持续发帖待验证 |
| 订阅模式可以支撑无广告社交网络 | Tier 1 商业模式 | 下载量、付费量、同类订阅产品、基础设施成本 | 尚无采用或收入证据 |
| Trust Score 能建立可用的社区信任 | Tier 1 官网/政策 | 用户反馈、误判申诉、安全与治理研究 | 未独立验证；可能带来误判、冷启动与社会排序问题 |

## 待深入维度

1. 产品与真实性技术：provenance 链条能证明什么、不能证明什么，攻击面与隐私代价。
2. 市场采用与用户反馈：下载、评分、社区活跃、独立评论、创始团队与运营能力。
3. 市场与竞品：BeReal、Cara、Bliish、Sonnet、Divine、Spread 等产品验证了什么，哪些已经失败或停滞。
4. 商业与合规：订阅模型、网络效应、moderation 成本、GDPR / biometric-adjacent 处理、平台风险。

## Analytical Lens Selection

- 主线：L5 叙事与现实偏差。叙事是“AI-free feed”，真正要判断的是 provenance 约束能否形成足够有价值的社交关系和内容供给。
- 辅助：L2 瓶颈迁移。限制生成内容之后，瓶颈转移到冷启动、内容密度、误判申诉和真人 moderation。
- 辅助：L4 技术族谱。从实名认证、BeReal 的即时拍摄，到 C2PA / device attestation，再到 SocialHuman 的端到端来源验证。
- 不作为主线：L3 共识天花板、L6 执行摩擦价值转移。

## Cross-validation

- 三路调研一致认为：SocialHuman 可验证的是受控 App/设备采集链路，不是画面语义真实性或人类原创性。
- 三路调研均未找到独立安全审计、公开误判率、第三方 red-team 或长期使用案例。
- 采用数据由两路独立找到同一创始人自报：245 注册、51 WAU、124 MAU、7 付费、MRR 27 美元、58% 从未发首帖。
- 市场调研与采用调研一致认为：真实性需求已由 BeReal、Cara 等验证；SocialHuman 自身尚未证明冷启动、留存和付费。
- 芬兰公司登记已由主线程通过 PRH/YTJ 官方 API 直接验证。

## Genealogy

1. 规则与身份层：实名、人工审核、社区禁止 AI；能约束行为，难以验证每条内容来源。
2. 真实性 UX：BeReal 用即时相机与共同仪式降低修饰；验证用户体验需求，但不做技术 provenance。
3. 开放 provenance：ProofMode、Truepic、C2PA 记录采集与编辑链；更适合跨组织携带，但 provenance 本身不证明事实为真。
4. SocialHuman：把受控采集、设备证明、行为取证和社交网络绑在一起；获得更强的门口控制，也承担空社交图谱和高发布摩擦。

## Narrative Reframe

主流叙事：SocialHuman 是一个能保证所有内容由真人创造的无 AI 社交网络。

实际判断：它把“事后猜测是否 AI”改成“证明媒体经过受控采集”，方向合理，也能有效过滤低成本上传、粘贴和机器人灌水；但这张凭证的精确语义只是 genuine-app capture receipt。真正的商业问题不是 detector 精度，而是用户是否愿意为了这张凭证放弃相册、编辑和低摩擦发帖，并把朋友一起迁入一个空网络。

## Thesis & Skeleton

SocialHuman 看准了一个会持续扩大的问题，但当前产品同时承担了两个极难任务：建立可信采集协议，以及从零建立社交图谱。前者有技术与 B2B 市场依据，后者尚无采用证据。更合理的方向是把社交端作为 dogfood，用高信任垂直场景验证价值，再把窄语义、可审计、可携带的采集凭证做成 SDK/API。

论证顺序：

1. 产品已真实上线，但采用仍为百级实验。
2. 验证架构比纯 AI detector 合理，但 badge 的承诺过宽。
3. 隐私与审核成本随着验证强度一起上升。
4. 市场验证了真实性痛点，没有验证新的通用社交网络。
5. 垂直场景与 provenance 基础设施比通用 Instagram 替代品更可行。
