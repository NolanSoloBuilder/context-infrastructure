# OPC 社区调研 Scratchpad

日期：2026-07-23

## 对象消歧

本轮把用户所说的“OPC 社区”优先解释为具体站点 [OPC Community](https://www.opc.community/)，运营主体为 Leago AI Inc.。同时纳入中国语境下的 OPC Space、OPC圈、OpenAIOPC、地方政府/园区 OPC 社区，以及 Indie Hackers、MicroConf 等相邻社群，用来判断它的真实位置。

OPC 在本轮有三种不同含义，报告中需要始终分开：

1. One-Person Company / 一人公司，一种由个人主导、借助软件、AI、外包和分发杠杆经营的模式。
2. 公司法意义上只有一个股东的公司。
3. 2025–2026 年中国地方政府、园区和创业服务机构使用的“人工智能 OPC”产业标签，实际范围可能扩到 1–10 人。

## Claim Extraction

| Claim | 来源层级 | 验证通道 | 当前状态 |
|---|---|---|---|
| OPC Community 是面向真实 builder 的高信任同行社区 | 官方 About（Tier 1） | 独立成员反馈、公开互动、活动参与、准入和治理机制 | 部分成立。已找到一次线上活动约 30 人参与；持续活跃度和成员质量尚无独立数据 |
| 已形成全球城市网络 | 官方 City 页面（Tier 1） | 各城市 host、活动、成员、独立社交记录 | 未验证。页面同时写 47 cities 和 64 Cities；Boston 等页面明确仍需 founding host、尚无活动 |
| 首页展示的是“真实 founder”和“真实评价” | 官方首页（Tier 1） | 身份交叉检索、头像来源、产品链接 | 证据不足且存在明显占位信号：首页 Alex/Priya 等使用 DiceBear 生成头像，同一组名字同时出现在 member 卡与 testimonial |
| OPC Elite 将提供 peer groups、Demo Day、workshop | 官方 About/Terms（Tier 1） | 当前付费入口、活动记录、会员反馈 | 尚未上线。条款写明 standard $199/year，waitlist early bird $99/year |
| 内容与机会聚合能直接帮助 founder | 官方首页/条款（Tier 1） | 数据时效、错误率、用户使用记录 | 聚合功能存在；官方条款要求用户自行核对截止日期和金额。首页曾出现 Sequoia Arc `Invalid Date` |
| AI 时代一人公司已经成为广泛可复制的经营模式 | 官方内容与中国政策报道（Tier 1–2） | 可验证收入、团队规模、持续经营、失败样本 | 趋势和政策热度成立；普遍可复制性未证实。站内关于典型 MRR、AI 提升倍数等数字缺少来源 |
| 国内 OPC 社区能够提供政策、工位、算力、客户和投资 | 地方政府/园区与平台宣传（Tier 1） | 政策原文、兑现条件、入驻企业存活率、订单记录 | 政策和物理资源在部分城市成立；社区关系、补贴兑现率和经营结果缺少统一数据 |

## 第一轮事实

- [OPC Community 条款](https://www.opc.community/terms)说明现有功能包括账户、Daily Builder Pulse、活动聚合、融资/项目数据库、LaunchPad、weekly check-ins、saved events 和 Perk Wishlist。Elite 仍在开发。
- [OPC Community 城市页](https://www.opc.community/city)标题写 47 个城市，统计卡写 64 Cities。列表中的城市页面主要是城市介绍和候补入口。
- [Boston 城市页](https://www.opc.community/city/boston)明确写“This city needs a founding City Host”“No events scheduled yet”，说明目录页不等于已运营 chapter。
- OPC Community 的 LinkedIn 页面在 2026 年 6 月一次 Boston Tech Week 线上活动后披露：100+ 人表达兴趣、约 30 人实际参加；搜索快照显示页面当时有 91 followers。这是当前最具体的行为证据。
- 第三方 Partiful 页面显示该活动 `96 Went`、`13 Interested`、`4 Maybe`，可验证报名热度；实际进入线上会议约 30 人仍是主办方自报。
- 城市 host 招聘为每周 2–5 小时的 unpaid volunteer，目标是“help bring OPC Community to life locally”和“build from zero”。这支持它仍处早期搭建期。
- 广州主理人在个人网站公开身份，北京、上海、广州活动也出现在站外活动目录；中国城市网络已经有少量真实运营痕迹。
- 官网法律页披露运营主体为 Leago AI Inc.，适用 California 法律；数据经 Supabase/AWS 存储，网站在 Vercel，未来支付使用 Stripe。
- RDAP 记录域名注册于 2026-03-24；城市目录 64 页中有 52 页仍缺 host 或活动，只有 12 个中国城市页写“主理人已就位”。
- 免费注册没有 builder 审核。About 的“Every member is actively building”目前属于价值主张，而不是准入事实。
- About 宣传 `$99` 早鸟价 “locked in for life”，条款同时保留上线前调整 benefits/terms 的权利。
- 中国实体 OPC 社区已有入驻筛选、项目转向、算力成本下降和企业合作案例；同时存在补贴细则未落地、政策与真实支出错位、层层分包和投资/IP 风险。

## 初步判断

OPC Community 当前是“内容与机会聚合产品 + 尚在搭建的社区网络”。它已经做出可用网站、账户系统、聚合内容和至少一次线上活动，但没有证据支持把城市目录、通用 founder 卡片或愿景性文案等同于成熟社群。

对徐昊而言，免费加入可以作为低成本观察；不应为了 OPC Elite 早鸟价提前形成付费承诺。真正需要验证的是能否匹配到 5–10 个同阶段、已在持续 shipping、愿意讨论真实获客与收入问题的人。
