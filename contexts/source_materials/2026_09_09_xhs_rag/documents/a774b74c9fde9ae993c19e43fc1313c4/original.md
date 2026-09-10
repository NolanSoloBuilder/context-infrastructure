# 欧盟与美国隐私合规法律中麦克风/摄像头前端功能设计要求

> 本报告基于 agentic-rag 内部知识库、EDPB/FTC/EU AI Act 官方文件及监管处罚案例综合分析，整理了欧盟和美国主要隐私法规对涉及麦克风、摄像头的前端功能设计的规定，归纳通用功能设计与地区强制差异功能设计。

---

## 一、法律框架总览

### 1. 欧盟

| 法规 | 核心条款 | 对麦克风/摄像头的要求 |
| --- | --- | --- |
| **GDPR** | Art 6（合法依据）、Art 9（特殊类目数据）、Art 25（隐私设计） | 生物识别数据属特殊类目，需明示同意；隐私设计原则要求默认不采集 |
| **ePrivacy Directive** | Art 5(3) | 访问/存储用户设备信息前需获得同意（opt-in），涵盖摄像头/麦克风设备访问 |
| **EU AI Act** | Art 5（禁止性实践） | 禁止实时远程生物识别（公共场所）、情绪推断（职场/教育）、面部图像无目标抓取 |
| **EDPB Guidelines 3/2019** | 视频设备指南 | 视频监控需合法依据、告知、数据最小化、保留期限 |

### 2. 美国

| 法规/判例 | 管辖范围 | 对麦克风/摄像头的要求 |
| --- | --- | --- |
| **CCPA/CPRA** | 加州 | 生物识别信息属"敏感个人信息"，用户有权限制使用和出售；需在收集时告知 |
| **Illinois BIPA** | 伊利诺伊州 | 收集生物标识前须获得**书面同意**，须制定保留/销毁时间表，须公开生物识别政策 |
| **COPPA** | 联邦（FTC 执行） | 面向 13 岁以下儿童的服务，收集语音录音需**可验证的父母同意**；2013 年修订将音视频文件纳入"个人信息" |
| **FTC Section 5** | 联邦 | 不公平/欺骗性商业行为管辖，多次对未充分告知的摄像头/麦克风采集进行执法 |

---

## 二、通用前端功能设计（EU + US 均需）

### 1. 场景化权限请求弹窗（使用前告知 + 同意）

所有地区均要求在调用麦克风/摄像头前进行场景化告知并获取同意，禁止一揽子授权。

- **GDPR** 要求同意必须"自由给出、具体、知情"（freely given, specific, informed），且可撤回。敏感数据处理需"单独同意"。

- **CCPA/CPRA** 要求在收集时或收集前告知消费者所收集的个人信息类别及用途。

- **BIPA** 要求在收集前以书面形式告知并获得同意。

> **内部文档**：《海外合规产品及技术原子能力建设》&gt; 一、背景 &gt; 用户告知同意及协议管理
> **原文**：海外隐私法要求，企业对用户数据的处理需要尽到充分告知和获取用户同意的义务，**其中对于敏感数据的处理，在每个场景需要获取用户的单独同意**。……企业需要建设整套的用户协议、系统弹窗和用户同意的管理的技术能力。
> **链接**：[https://docs.xiaohongshu.com/doc/f219243be2123e8108d3989b0ba48700](https://docs.xiaohongshu.com/doc/f219243be2123e8108d3989b0ba48700)

> **法条**：GDPR Art 4(11) & Art 7
> **原文**：Consent must be **freely given, specific, informed** and unambiguous. The data subject must be able to withdraw consent at any time.
> **链接**：[https://gdpr.eu/gdpr-consent-requirements/](https://gdpr.eu/gdpr-consent-requirements/)

> **法条**：Illinois BIPA 740 ILCS 14/15(b)
> **原文**：A private entity in possession of biometric identifiers must **develop a written policy** and **obtain written consent** before collecting biometric identifiers.
> **链接**：[https://www.aclu-il.org/campaigns-initiatives/biometric-information-privacy-act-bipa/](https://www.aclu-il.org/campaigns-initiatives/biometric-information-privacy-act-bipa/)

### 2. 使用中实时指示器（录制状态可视化）

通用最佳实践，部分法规间接要求。iOS/Android 系统级指示灯（绿点/橙点）由操作系统提供，但应用层面应在录制界面显示明显的录制状态图标和倒计时。GDPR Art 25 隐私设计原则要求"默认隐私"（data protection by design and by default），实时指示器属于技术措施之一。

### 3. 权限撤回与同意状态管理

GDPR 明确要求可撤回；CCPA 要求提供"选择退出"机制。

> **内部文档**：《海外合规产品及技术原子能力建设》&gt; 一、背景 &gt; 用户告知同意及协议管理
> **原文**：在用户同意或不同意后，**未提供便捷灵活的同意状态管理能力**。……
> **链接**：[https://docs.xiaohongshu.com/doc/f219243be2123e8108d3989b0ba48700](https://docs.xiaohongshu.com/doc/f219243be2123e8108d3989b0ba48700)

### 4. 数据最小化与及时删除

GDPR Art 5(1)(c) 数据最小化原则；CCPA 要求保留期限限制；FTC COPPA 指南要求语音转文字后立即删除。

> **内部文档**：《埋点禁止上报数据清单》&gt; 禁止上报数据列表 &gt; 系统数据
> **原文**：禁止采集**麦克风采集的音频原始数据**（mic_audio）、**摄像头采集的图像/视频原始数据**（camera_frame）……除非用于安全风控或特定崩溃诊断场景，否则禁止采集麦克风/摄像头权限状态。
> **链接**：[https://docs.xiaohongshu.com/doc/d82e4badeff5a0b4054901b7f015894a](https://docs.xiaohongshu.com/doc/d82e4badeff5a0b4054901b7f015894a)

> **法条**：FTC COPPA Guidance on Voice Recordings (2017)
> **原文**：The FTC announced a new enforcement policy where it will not enforce the parental consent requirement for the limited circumstances where audio of a child's voice is collected **solely for the purpose of replacing written words and is then immediately deleted** after transcription.
> **链接**：[https://www.fenwick.com/insights/publications/ftcs-new-coppa-guidance-on-recording-childrens-voices-five-tips-for-app-developers-and-toymakers-to-comply](https://www.fenwick.com/insights/publications/ftcs-new-coppa-guidance-on-recording-childrens-voices-five-tips-for-app-developers-and-toymakers-to-comply)

### 5. 隐私政策明示披露

所有地区均要求隐私政策中明确披露麦克风/摄像头数据收集类型、目的、保留期限和共享方。

### 6. 埋点/监控系统的隔离

内部治理要求——埋点系统禁止采集麦克风/摄像头原始数据，确保性能监控和行为统计系统不触碰敏感设备数据。

> **内部文档**：《埋点禁止上报数据清单》&gt; 禁止上报数据列表 &gt; 系统数据
> **原文**：禁止采集……麦克风采集的音频原始数据（mic_audio）、摄像头采集的图像/视频原始数据（camera_frame）……除非用于安全风控或特定崩溃诊断场景，否则禁止采集麦克风/摄像头权限状态。
> **链接**：[https://docs.xiaohongshu.com/doc/d82e4badeff5a0b4054901b7f015894a](https://docs.xiaohongshu.com/doc/d82e4badeff5a0b4054901b7f015894a)

---

## 三、地区强制差异功能设计

### 🇪🇺 欧盟特有要求

#### (1) ePrivacy Art 5(3)：设备访问的 opt-in 前置同意

欧盟独有——访问设备硬件（包括摄像头/麦克风数据存储）前须获得 opt-in 同意，不可默认开启。

> **法条**：ePrivacy Directive Art 5(3) &#124; EDPB Guidelines 2/2023
> **原文**：Article 5(3) requires that **user consent is obtained before storing or accessing information** on an end user's device, unless an exception applies.
> **链接**：[https://www.edpb.europa.eu/system/files/2024-10/edpb_guidelines_202302_technical_scope_art_53_eprivacydirective_v2_en_0.pdf](https://www.edpb.europa.eu/system/files/2024-10/edpb_guidelines_202302_technical_scope_art_53_eprivacydirective_v2_en_0.pdf)

#### (2) EU AI Act Art 5：摄像头 + AI 的禁止性实践

欧盟独有——以下摄像头 + AI 组合被**直接禁止**，前端不得提供此类功能：

| 禁止项 | 条款 | 涉及设备 |
| --- | --- | --- |
| 实时远程生物识别（公共场所、执法目的） | Art 5(1)(h) | 摄像头 + 人脸识别 |
| 面部图像无目标抓取建库 | Art 5(1)(e) | CCTV/网络摄像头图像爬取 |
| 情绪推断（职场和教育场景） | Art 5(1)(f) | 摄像头 + 表情分析 |
| 基于生物识别的种族/政治/宗教/性取向分类 | Art 5(1)(g) | 摄像头 + 生物特征分类 |

> **法条**：EU AI Act Art 5
> **原文**：(e) the placing on the market…of an AI system that creates or expands facial recognition databases through **the untargeted scraping of facial images from the internet or CCTV footage**; (f) …AI systems to **infer emotions of a natural person in the areas of workplace and education institutions**; (h) the use of '**real-time' remote biometric identification systems in publicly accessible spaces** for the purposes of law enforcement…
> **链接**：[https://artificialintelligenceact.eu/article/5/](https://artificialintelligenceact.eu/article/5/)

#### (3) GDPR Art 9：生物识别数据的特殊类目同意

摄像头采集人脸、虹膜等生物识别数据属于 GDPR Art 9 "特殊类目个人数据"，需要比普通同意更高的标准——**明示同意**（explicit consent），且需有 Art 9(2)(a) 的例外依据。EDPB 视频设备指南进一步要求设置告知标识（如监控区域张贴告知标志）。

> **法条**：EDPB Guidelines 3/2019 on processing of personal data through video devices
> **原文**：These guidelines examine **how the GDPR applies in relation to the processing of personal data by video devices** and how consistent application of the GDPR can be ensured.
> **链接**：[https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-32019-processing-personal-data-through-video_en](https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-32019-processing-personal-data-through-video_en)

---

### 🇺🇸 美国特有要求

#### (1) Illinois BIPA：书面同意 + 保留销毁时间表（州级强制）

美国独有（Illinois 州）——收集生物标识（含面部识别、声纹）前须获得**书面同意**，并须制定**保留期限和销毁时间表**。违反可被私人诉权（private right of action），每 negligent 违规 $1,000，每 intentional 违规 $5,000。

> **法条**：Illinois BIPA 740 ILCS 14/15
> **原文**：Under the BIPA, employers must **receive the individual's informed, written consent** before capturing, collecting, or otherwise obtaining biometric identifiers.
> **链接**：[https://www.icemiller.com/thought-leadership/dont-forget-about-biometric-information-privacy-laws-when-implementing-ai-in-the-workplace](https://www.icemiller.com/thought-leadership/dont-forget-about-biometric-information-privacy-laws-when-implementing-ai-in-the-workplace)

> **法条**：Illinois BIPA Retention
> **原文**：Biometric information must now be **disposed of within three years** of the last interaction with the individual unless a longer period is required.
> **链接**：[https://mosey.com/blog/illinois-biometric-information-privacy-act/](https://mosey.com/blog/illinois-biometric-information-privacy-act/)

#### (2) COPPA：儿童语音录音的可验证父母同意（联邦强制）

美国独有（联邦）——面向 13 岁以下儿童的服务，收集语音录音需**可验证的父母同意**（VPC）。FTC 2017 年指南提供了有限豁免：仅用于语音转文字替代键盘输入且立即删除的，可豁免 VPC，但仍需在隐私政策中披露。

> **法条**：FTC COPPA Rule 16 CFR Part 312
> **原文**：COPPA imposes certain requirements on operators of websites or online services directed to children under 13 years of age.
> **链接**：[https://www.ftc.gov/legal-library/browse/rules/childrens-online-privacy-protection-rule-coppa](https://www.ftc.gov/legal-library/browse/rules/childrens-online-privacy-protection-rule-coppa)

> **法条**：FTC COPPA Voice Recordings Guidance (2017)
> **原文**：Generally, online services that are directed to children under 13 need **verifiable parental consent before collecting voice recordings**. Under the new guidance, a company may not have to get VPC before collecting audio files from children as long as the audio is being used to **replace text-based commands** and is not used for any other purpose…and **deleted immediately** after replacing written words.
> **链接**：[https://www.fenwick.com/insights/publications/ftcs-new-coppa-guidance-on-recording-childrens-voices-five-tips-for-app-developers-and-toymakers-to-comply](https://www.fenwick.com/insights/publications/ftcs-new-coppa-guidance-on-recording-childrens-voices-five-tips-for-app-developers-and-toymakers-to-comply)

#### (3) CCPA/CPRA：敏感个人信息的"限制使用"权利（加州强制）

美国独有（加州）——生物识别信息属 CCPA/CPRA "敏感个人信息"（SPI），消费者有权**限制企业使用和出售** SPI，企业须提供"限制使用"的 opt-out 链接。

---

## 四、监管处罚案例

| 案例 | 管辖区 | 罚款/和解金额 | 违规要点 | 对前端设计的启示 |
| --- | --- | --- | --- | --- |
| **TikTok BIPA 集体诉讼和解** (2022) | 美国 Illinois | $9,200 万 | 未经充分告知和同意收集面部生物数据 | 摄像头 + 人脸识别须前置 BIPA 书面同意 |
| **FTC v. Facebook** (2019) | 美国联邦 | $50 亿 | 面部识别功能未获明确同意 | 摄像头面部识别须提供 clear and conspicuous notice + affirmative consent |
| **小红书 Google Play 权限弹窗整改** (2025.12–2026.1) | 全球（Google Play 政策） | 应用下架风险 | 权限弹窗设计不符合 Google Play 要求 | 权限请求弹窗须符合应用商店合规规范 |
| **Meta GDPR 罚款** (2023) | 欧盟 | €12 亿 | 数据跨境不合规（间接涉及用户数据处理同意） | 同意机制和数据传输须合规 |

> **内部文档**：《海外合规产品及技术原子能力建设》&gt; 一、背景 &gt; 用户告知同意及协议管理
> **原文**：2022年，**TikTok在美国伊利诺伊州北区联邦地区法院达成一项9200万美元的和解协议**，原因是在处理面部生物数据时未能充分告知用户并获得同意。……2025年12月至今年1月，**小红书因权限弹窗设计不符合Google Play要求**，被Google Play要求限期整改否则将下架。
> **链接**：[https://docs.xiaohongshu.com/doc/f219243be2123e8108d3989b0ba48700](https://docs.xiaohongshu.com/doc/f219243be2123e8108d3989b0ba48700)

> **法条**：FTC v. Facebook (2019)
> **原文**：Facebook, Inc. will pay a record-breaking $5 billion penalty…As part of the penalty, **Facebook was required to provide clear and conspicuous notice of its facial recognition technology and obtain affirmative consent**.
> **链接**：[https://www.ftc.gov/news-events/news/press-releases/2019/07/ftc-imposes-5-billion-penalty-sweeping-new-privacy-restrictions-facebook](https://www.ftc.gov/news-events/news/press-releases/2019/07/ftc-imposes-5-billion-penalty-sweeping-new-privacy-restrictions-facebook)

---

## 五、功能设计清单汇总

### 通用功能（EU + US 均需）

| # | 功能 | 法规依据 |
| --- | --- | --- |
| 1 | 场景化权限请求弹窗（使用前告知 + 同意） | GDPR Art 6/7, CCPA, BIPA |
| 2 | 录制中实时指示器 | GDPR Art 25 隐私设计 |
| 3 | 权限撤回 / 同意状态管理 | GDPR Art 7(3), CCPA opt-out |
| 4 | 数据最小化（仅采集必要数据 + 及时删除） | GDPR Art 5(1)(c), COPPA FTC 指南 |
| 5 | 隐私政策明示披露 | 所有法规 |
| 6 | 埋点/监控隔离（禁止采集 mic/cam 原始数据） | 内部治理要求 |

### 欧盟强制功能

| # | 功能 | 法规依据 |
| --- | --- | --- |
| E1 | 设备访问 opt-in 前置同意（不可默认开启） | ePrivacy Art 5(3) |
| E2 | 生物识别数据明示同意（explicit consent） | GDPR Art 9 |
| E3 | 视频监控区域告知标志 | EDPB Guidelines 3/2019 |
| E4 | 禁止实时远程生物识别功能（公共场所） | AI Act Art 5(1)(h) |
| E5 | 禁止情绪推断功能（职场/教育） | AI Act Art 5(1)(f) |
| E6 | 禁止面部图像无目标抓取建库 | AI Act Art 5(1)(e) |

### 美国强制功能

| # | 功能 | 法规依据 |
| --- | --- | --- |
| U1 | 生物识别收集前书面同意（Illinois 州） | BIPA 740 ILCS 14/15(b) |
| U2 | 生物识别保留期限 + 销毁时间表（Illinois 州） | BIPA 740 ILCS 14/15(a) |
| U3 | 儿童语音录音可验证父母同意 VPC（联邦） | COPPA 16 CFR 312 |
| U4 | 敏感个人信息"限制使用"opt-out 链接（加州） | CCPA/CPRA |
| U5 | 面部识别功能 clear and conspicuous notice + affirmative consent（联邦 FTC） | FTC Section 5 |

---

## 六、来源清单

**agentic-rag 知识库**：

- 《海外合规产品及技术原子能力建设》&gt; 一、背景 &gt; 用户告知同意及协议管理 → [https://docs.xiaohongshu.com/doc/f219243be2123e8108d3989b0ba48700](https://docs.xiaohongshu.com/doc/f219243be2123e8108d3989b0ba48700)

- 《埋点禁止上报数据清单》&gt; 禁止上报数据列表 &gt; 系统数据 → [https://docs.xiaohongshu.com/doc/d82e4badeff5a0b4054901b7f015894a](https://docs.xiaohongshu.com/doc/d82e4badeff5a0b4054901b7f015894a)

**外部官方信息**：

- EDPB：Guidelines 3/2019 on video devices → [https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-32019-processing-personal-data-through-video_en](https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-32019-processing-personal-data-through-video_en)

- EDPB：Guidelines 2/2023 on Technical Scope of Art. 5(3) ePrivacy → [https://www.edpb.europa.eu/system/files/2024-10/edpb_guidelines_202302_technical_scope_art_53_eprivacydirective_v2_en_0.pdf](https://www.edpb.europa.eu/system/files/2024-10/edpb_guidelines_202302_technical_scope_art_53_eprivacydirective_v2_en_0.pdf)

- EU AI Act：Article 5 Prohibited AI Practices → [https://artificialintelligenceact.eu/article/5/](https://artificialintelligenceact.eu/article/5/)

- GDPR.eu：GDPR Consent Requirements → [https://gdpr.eu/gdpr-consent-requirements/](https://gdpr.eu/gdpr-consent-requirements/)

- FTC：COPPA Rule 16 CFR Part 312 → [https://www.ftc.gov/legal-library/browse/rules/childrens-online-privacy-protection-rule-coppa](https://www.ftc.gov/legal-library/browse/rules/childrens-online-privacy-protection-rule-coppa)

- FTC：FTC Imposes $5 Billion Penalty on Facebook (2019) → [https://www.ftc.gov/news-events/news/press-releases/2019/07/ftc-imposes-5-billion-penalty-sweeping-new-privacy-restrictions-facebook](https://www.ftc.gov/news-events/news/press-releases/2019/07/ftc-imposes-5-billion-penalty-sweeping-new-privacy-restrictions-facebook)

- Fenwick：FTC COPPA 语音指南解读 → [https://www.fenwick.com/insights/publications/ftcs-new-coppa-guidance-on-recording-childrens-voices-five-tips-for-app-developers-and-toymakers-to-comply](https://www.fenwick.com/insights/publications/ftcs-new-coppa-guidance-on-recording-childrens-voices-five-tips-for-app-developers-and-toymakers-to-comply)

- ACLU Illinois：BIPA → [https://www.aclu-il.org/campaigns-initiatives/biometric-information-privacy-act-bipa/](https://www.aclu-il.org/campaigns-initiatives/biometric-information-privacy-act-bipa/)

- Ice Miller：BIPA written consent → [https://www.icemiller.com/thought-leadership/dont-forget-about-biometric-information-privacy-laws-when-implementing-ai-in-the-workplace](https://www.icemiller.com/thought-leadership/dont-forget-about-biometric-information-privacy-laws-when-implementing-ai-in-the-workplace)

- Mosey：BIPA Retention Requirements → [https://mosey.com/blog/illinois-biometric-information-privacy-act/](https://mosey.com/blog/illinois-biometric-information-privacy-act/)

- California AG：CCPA → [https://oag.ca.gov/privacy/ccpa](https://oag.ca.gov/privacy/ccpa)