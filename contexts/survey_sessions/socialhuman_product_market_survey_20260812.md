# SocialHuman 产品与市场调研

> 核验日期：2026-08-12

## 结论

SocialHuman 已经是一个真实上线、iOS 与 Android 均可下载、仍在快速迭代的产品。它目前还不是一个形成市场的社区，而是一个由 solo founder 主导的早期实验：截至 7 月 3 日，创始人自报 245 名注册用户、51 WAU、124 MAU、7 名付费用户和 27 美元 MRR；Google Play 当前只有 `100+` 下载，美国 App Store 没有评分。

产品方向有价值。SocialHuman 不依赖事后 AI detector 猜一张图真假，而是控制内容入口：只能用 App 内相机现场采集，再结合设备证明、传感器、媒体取证和输入行为生成凭证。这能有效拦住直接上传 AI 图片、复制粘贴 AI 文本和低成本批量机器人。

不过，官方的“every post is real”说得过满。它实际能较强证明的是：**正版 SocialHuman App 在一台真实设备上完成过一次受控采集**。它不能证明相机前的场景真实，也不能证明文字思想来自人类。拍摄高质量屏幕或打印品、真人照抄 AI 文本、真人代发、机器人操作真机，都在这套证明能力之外。

我的判断是：SocialHuman 看准了一个会持续扩大的问题，却同时承担了两个极难任务，一边建立可信采集协议，一边从零建立社交图谱。前者有长期市场价值，后者尚未通过采用数据验证。更有机会的形态是“高信任垂直社区 + 可携带的真实性凭证”，而不是直接再造一个通用 Instagram。

## 产品现在到了什么阶段

[Apple Lookup API](https://itunes.apple.com/lookup?id=6761835659&country=us) 显示，SocialHuman 于 2026 年 5 月 11 日上线，8 月 10 日已经更新到 `1.0.18`。三个月内至少发布 12 个版本，增加了 Stories、Circles、端到端加密私信、视频编辑、设备硬件证明、on-device captions 和类似 BeReal 的每日随机六秒拍摄 `Right Now`。它不是停留在 landing page 的概念产品，solo builder 的交付速度也很快。

公开采用数据仍接近零点：[Google Play](https://play.google.com/store/apps/details?id=com.socialhuman.app&hl=en) 显示 `100+` 下载；芬兰 App Store 有 4 个评分和 1 条文字评论，美国区为 0 个评分。没有找到 HN 条目、Product Hunt 产品页、主流媒体独立评测、用户迁移故事或长期使用复盘。

最完整的业务数据来自[创始人 7 月 3 日的 Reddit 自报](https://www.reddit.com/r/SideProject/comments/1umm2y1/my_social_app_with_no_upload_button_went_from_0/)：

| 指标 | 数值 | 含义 |
|---|---:|---|
| 注册用户 | 245 | 仍是封闭实验规模 |
| MAU / WAU | 124 / 51 | WAU/MAU 约 41%，但样本小且产品刚上线 |
| Posts / Stories | 739 / 81 | 已产生实际内容，并非空壳 |
| 付费用户 | 7 | 注册到付费约 2.9% |
| MRR | $27 | 尚不具备商业可持续性 |
| 从未发首帖 | 58% | camera-only 与验证流程带来明显供给摩擦 |

创始人同时写道：`No organic or viral loop yet`，增长来自其约一万名既有社媒关注者、X 广告和手工社区推广。当前数据只证明有人愿意试，尚未证明自然增长、长期留存或朋友迁移。

[芬兰 PRH/YTJ 官方企业 API](https://avoindata.prh.fi/opendata-ytj-api/v3/companies?businessId=3627558-3) 显示，运营主体 `SocialHuman Technologies Oy` 于 2026 年 5 月 25 日取得 Business ID，5 月 27 日完成公司登记，主营为 computer programming activities。公司成立在 App 上线约两周后。公开材料均指向 Olli Albert Airola 个人主导，尚未发现第二名公开团队成员或融资披露。

商业模式是 free core + Founding Member：美国区约 `$6.99/month` 或 `$39.99/year`，芬兰区约 `€7.99/month` 或 `€47.99/year`。Premium 主要卖更长视频与 caption、verification insights、Trust Score analytics、置顶和外观功能。这些增值项目前不足以证明能覆盖媒体存储、反作弊和人工审核成本。

## 验证机制成立到哪一步

[官方验证说明](https://socialhuman.dev/verification) 列出了以下信号：

- App 内相机是图片和视频的唯一入口；
- accelerometer 与 gyroscope 检查设备运动；
- EXIF、压缩和频域分析检查文件来源与重编码；
- moiré、视频与音频取证寻找屏幕翻拍等异常；
- caption 禁止粘贴，并分析 keystroke timing；
- device attestation 检查正版 App 和真实设备；
- 多信号共同判定，疑似内容进入人工复核。

这个架构比“上传文件后跑一个 AI detector”合理。[Apple App Attest](https://developer.apple.com/documentation/DeviceCheck/establishing-your-app-s-integrity) 能让服务端确认请求来自真实 Apple 设备上的合法 App instance；[Google Play Integrity](https://developer.android.com/google/play/integrity/overview) 能确认请求来自 Google Play 分发的正版 App 和可信设备。把媒体 hash、server challenge 与 assertion 正确绑定后，直接篡改客户端和重放请求会困难很多。

证明边界也必须写清楚：

| Badge 容易被理解为 | 公开机制实际能支持的判断 |
|---|---|
| 这件事真实发生了 | SocialHuman App 拍到了这个画面 |
| 这是人类原创内容 | 有真实设备与采集动作参与 |
| 账号就是这个真人 | 账号通过邮箱注册并积累了验证历史 |
| 文字由这个人思考 | 文字表现出真人逐键输入行为 |

[C2PA 自己的安全说明](https://spec.c2pa.org/specifications/specifications/2.0/security/_attachments/Harms_Modelling.pdf) 也明确强调，provenance 不对数字内容的真假做价值判断；有效凭证只能证明相关来源记录可验证、格式正确且没有被篡改。

独立研究给出了两个直接边界。USENIX Security 2025 的[物理重拍攻击研究](https://www.usenix.org/conference/usenixsecurity25/presentation/liu-yuxin) 指出，把合成内容显示在屏幕、投影、纸张或画布上再用可信相机拍摄，对 provenance 系统普遍有效。SocialHuman 的 moiré 与频域分析会增加难度，却没有公开 depth sensing、误判率或绕过基准。

文本方面，人可以看着另一台设备上的 ChatGPT 输出逐字输入。[2026 年关于 copy-type attack 的研究](https://arxiv.org/abs/2601.17280) 把边界概括得很准确：键入行为可以确认有人操作键盘，不能确认文字由这个人产生。禁 paste 对批量机器人有效，对人类转录无效。

因此，SocialHuman 更准确的产品定义是：**camera-gated、provenance-first 的实验性社区**。它能显著提高伪造和自动灌水成本，不能颁发 human-origin certificate。目前也没有找到它自身的独立安全审计、公开 false positive / false negative、第三方 red-team、C2PA 样本或密码学协议说明。

## 信任的隐私代价

[SocialHuman Privacy Policy](https://socialhuman.dev/privacy) 披露的数据比普通图片社区更敏感：EXIF、加速度计与陀螺仪、按键时序、包含光标位置的 text composition replay、短原始视频片段和 audio fingerprints。政策将键入、composition replay 和设备运动视为 `biometric-adjacent` 数据，并按 GDPR Art. 9 的显式同意处理。

原始传感器与视频片段在帖子终局判定后 7 天清除；原始按键事件与 composition replay 保留 30 天；聚合键入指标、每帖 analyzer scores、verdict、Trust Score inputs 和部分 sensor fingerprints 保留更久。平台还会使用 verified content 与 verification signals 训练自己的检测模型，承诺不出售或授权第三方训练。

这里有三个需要继续追问的问题：

1. 用户能否只拒绝“训练自有模型”，同时继续接受完成发帖所需的核心验证？
2. 删除账号后，已经进入模型参数的用户数据如何处理？
3. 是否完成过 DPIA，以及误判后的人工复核 SLA 是多少？

治理成熟度目前跟不上技术承诺。隐私政策 changelog 承认，官网此前已默认加载 X conversion pixel，却仍声称没有 tracking SDK/cookie，直到 8 月 2 日才改成 consent-only。后续版本才逐步公开 composition replay、永久聚合统计和训练自有模型等处理。它愿意留下修正记录是积极信号，也说明单人团队的 policy-as-operated 审核能力有限。

## 市场存在，但不等于新网络成立

真实性焦虑已经是大众问题。墨尔本大学与 KPMG 的[2025 全球研究](https://assets.kpmg.com/content/dam/kpmgsites/sa/pdf/2025/trust-attitudes-and-use-of-ai-global-report.pdf.coredownload.inline.pdf) 覆盖 47 国 48,340 人，70% 表示因为分不清真实内容与 AI 内容而难以信任线上信息，86% 希望社交与新闻平台提供识别机制。[Jumio 对四国 8,000 多名成年人的调查](https://www.jumio.com/about/press-releases/2025-survey-consumer-trust/) 中，69% 表示自己比一年前更怀疑在线内容，72% 担心被操纵过的社交媒体内容欺骗。

不过，担心不等于迁移，更不等于付费。现有市场证据可以分成三层：

| 市场层 | 已验证案例 | SocialHuman 面临的问题 |
|---|---|---|
| 即时、少修饰的真实分享 | [BeReal 官方称 40M+ MAU](https://bereal.com/ads/audience)，2024 年被 Voodoo 以 €500m 收购 | BeReal 的核心是共同仪式与朋友密度，技术验证很轻；真实性带来下载，朋友停止发帖后使用价值会快速下降 |
| 利益绑定的无 AI 垂直社区 | [Cara 超过 100 万用户、400 万帖子和 500 万图片](https://blog.cara.app/blog/finances-and-future-of-cara) | 艺术家的作品权利、职业展示和客户获取提供了迁移动机；通用用户缺少同等强的利益 |
| 新一代 human-only 产品 | Bliish、Sonnet、PRSN、Only Human Hub、Glas、Sapien | 大多仍是百级、千级或 waitlist，说明供给正在出现，尚无品类赢家 |

BeReal 证明“少修饰的朋友生活”可以成为大众产品；Cara 证明当 AI 问题直接伤害一个职业群体时，用户会迁移。二者都没有证明，人们会单纯为了“No AI”把整个朋友网络搬到新平台。

SocialHuman 的 `Right Now` 正在补 BeReal 式日常仪式，这是正确方向。但它比 BeReal 多了验证等待、禁相册、禁粘贴和 Trust Score，同时又没有 BeReal 已经形成的朋友密度。创始人自报的 58% 首帖流失，已经显示信任提升和内容供给之间的直接交换。

## 最有机会的市场路线

短期继续做“所有人的新社交网络”，现实上更可能停在 1,000–10,000 名忠实用户。进入一个关系密度高、现场真实性有明确价值的垂直群体，才有机会先做到 10,000–100,000 活跃用户。达到百万需要 Cara 式外部触发事件、职业利益或既有 creator graph；当前没有证据支持 BeReal 级规模。

适合的垂直切口包括：

- 现场活动、校园社团、跑步与户外挑战；
- 本地社区和公民见证；
- 约会安全、二手交易的现场状态证明；
- 保险查勘、field service、marketplace condition proof；
- 新闻目击与机构素材采集。

后四类尤其重要，因为真实性直接影响金钱、责任或证据价值，不需要先说服全世界的朋友一起迁移。Truepic、ProofMode 与 C2PA 的发展也说明，可信采集在 B2B 和新闻链路里比“纯理念社交”更容易找到付费理由。

我建议的产品路线是：

1. 保留 SocialHuman 社交端，作为验证系统的 dogfood 和 reference community；增长单位从单个用户改成完整 Circle、活动或组织，让新用户第一天就有 5–20 个认识的人。
2. 把 badge 改成精确事实，例如 `Captured in SocialHuman on an attested device at T`，不再用 `real` 概括来源、作者和事实三件不同的事。
3. 公开 threat model、设备覆盖、误报/漏报、人工复核 SLA，并邀请第三方 red-team。
4. 把验证层抽成 SDK/API，输出可携带 receipt，并与 C2PA 互操作。用户应能把凭证带到 Instagram、新闻 CMS、交易平台或组织工作流，而不是只能留在一个空 feed 中。
5. 变现优先卖组织席位、验证次数、存储导出、API volume 和 marketplace trust；个人 Premium 作为辅助收入。仅靠长 caption、颜色和 Trust Score analytics 难以覆盖长期审核成本。

## 最终评价

| 维度 | 评价 |
|---|---|
| 问题真实性 | 高。AI 内容与机器人正在侵蚀在线信任 |
| 产品执行 | 早期产品中较强，双端上线且迭代快 |
| 技术方向 | 对。provenance-first 优于单纯事后 detector |
| 技术证明强度 | 中等。能证明受控采集，不能证明事实与人类原创 |
| 社区采用 | 很低。百级安装、245 名自报用户、无自然增长环 |
| 商业验证 | 尚无。7 名付费、27 美元 MRR |
| 通用社交机会 | 低。朋友网络、内容密度与发布摩擦尚未解决 |
| 垂直社区机会 | 中等，需要找到真实性具有实际收益的 cohort |
| SDK / provenance infrastructure 机会 | 中高，但必须开放、可审计并建立互操作性 |

SocialHuman 最重要的资产不是一个拥有 245 名注册者的 feed，而是它正在积累的受控采集方法、攻击经验和用户可理解的信任界面。把这些能力锁在新社交网络里，价值受制于网络冷启动；把它们变成精确、可携带、能进入已有工作流的凭证，才可能形成更大的市场。
