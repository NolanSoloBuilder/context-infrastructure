# 三个 App Store → Web niche 可行性复核 Scratchpad

日期：2026-07-22  
模式：Internal decision memo  
目标：不再回答“浏览器能不能实现”，而是回答“能否作为一个人快速上线并获利的 Web-first 产品”。

## Claim Extraction

| Claim | 原来源 | 独立验证通道 | 当前状态 |
|---|---|---|---|
| Drum lug tuner 的核心频率分析可由 Web Audio 完成 | 技术推断 | 浏览器音频能力、硬件规格、社区对比 | 功能可做；可靠识别与校准尚未验证 |
| Timecode logger 适合离线 PWA | 技术推断 | 现场工作流、外部同步、后台与导入兼容 | 前台记录可做；Web-first 优势不成立 |
| Pipe fabrication calculator 的 Web 竞争较弱 | 2026-07-17 SERP 扫描 | 当前竞品、社区新产品、价格 | 已被反驳；2026 年新增多款离线/低价竞品 |
| App Store 付费榜与评分证明值得做 Web 产品 | Apple 榜单、评分 | 搜索获客、Web 使用优势、付费转化 | 被反驳；只证明原生渠道内有需求 |

## 共同判断框架

候选必须同时通过四道门槛：

1. **Web 原生优势**：用户无需安装、从搜索直接进入、文件输入输出、桌面大屏或分享至少有一项是任务核心。
2. **可信交付**：结果错误不会直接造成现场损失，或有可执行的基准测试和专家验证机制。
3. **获客路径**：存在独立于 App Store 的搜索词、社区入口或可复用免费工具入口。
4. **单人经济性**：不是靠高支持成本换取低价一次性收入；可扩成内容/工具组合或高价值工作流。

## 初步事实

### Drum lug tuner

- [Tune-Bot 官方规格](https://tune-bot.com/tune-bot/)给出 30–400 Hz、±0.5 Hz 分辨率、750 ms 响应，并专门提供 Filter Mode 处理 false reading。这说明难点不是 FFT，而是鼓声的多泛音、误读过滤和稳定反馈。
- [Tune-Bot 使用说明](https://tune-bot.com/instructions/)要求麦克风位于鼓皮上方、按特定位置敲击，获取正确读数后再设置 ±18% filter；姿势和交互本身属于测量协议。
- [MDN MediaStreamTrack capabilities](https://developer.mozilla.org/en-US/docs/Web/API/MediaStreamTrack/getCapabilities)明确说明 `autoGainControl`、`echoCancellation`、`noiseSuppression` 等能力取决于浏览器和硬件；[constraints 文档](https://developer.mozilla.org/en-US/docs/Web/API/MediaTrackConstraints/echoCancellation)说明非 exact 约束只是尽力满足。
- [iDrumTune](https://www.idrumtune.com/)不是简单频谱仪，而是 pitch/lug/resonant modes、presets、课程和 212 页教材的组合。复制频率显示不等于复制产品价值。

### Production timecode logger

- [Timecode+](https://timecodeplus.com/)的当前价值包含单击 marker、time-of-day/manual/external MTC、离线转录、全屏 slate，以及 FCPXML/EDL/Premiere XML/ALE/SRT 等多种导出。
- [MovieSlate](https://www.movie-slate.com/)把现场竞争门槛推到硬件/协议集成：LTC、Wi-Fi timecode hub、script department、报告与 camera workflow；其官方宣称 incoming LTC drift 不超过每小时一帧。
- [Apple FCP XML frame-rate 文档](https://developer.apple.com/library/archive/documentation/AppleApplications/Reference/FinalCutPro_XML/FrameRate/FrameRate.html)区分 23.976、24、25、29.97、30、50、59.94、60，并用 `timebase + ntsc` 表达准确分数；[Adobe 文档](https://helpx.adobe.com/premiere/desktop/organize-media/import-files/migrate-from-final-cut-pro-x.html)明确指出 Premiere 不能直接导入 FCPXML，需转换且复杂元素不一定正确迁移。
- 当前已有多款免费 [Web timecode calculator](https://framemath.com/tools/timecode-calculator/)；简单换算或 DF/NDF 不是付费 wedge。

### Pipe fabrication calculator

- [ASME B16.9](https://www.asme.org/codes-standards/find-codes-standards/b16-9-factory-made-wrought-buttwelding-fittings)覆盖 NPS 1/2–48 的尺寸、公差、评级、测试和标识，当前 PDF/纸本价格约 $116–165。可信数据并非随手抄公式。
- [Pipe Trades Pro](https://www.calculated.com/mobile/prd267/Pipe-Trades-Pro-4095-Advanced-Pipe-Trades-Calculator.html)硬件 MSRP $89.95；但新竞争者 [PipeFit Pro](https://pipefitproapp.com/)已经提供 10 个计算器、7 组参考表、100% offline、一次性 $5.99。
- 2026 年社区现场反馈直接抓出了 [1/2 英寸和 2 英寸 take-out 错误](https://www.reddit.com/r/pipefitter/comments/1rri7jg/update_i_fixed_the_asme_b169_math_errors_you_guys/)，开发者随后从通用公式改成 ASME B16.9 表。这证明错误成本和专家验证门槛真实存在。
- 新近社区讨论已经出现“[这是一个已经解决的问题，你的产品比 Pipe Trades Pro 多什么](https://www.reddit.com/r/pipefitter/comments/1v0u4op/fitterswhat_do_you_use_for_on_the_job_calculations/)”的直接质疑。此前“Web 竞争弱”的判断已经过时。

## 暂定结论

- 三者都不符合“快速上站”原假设：Drum 是信号处理与校准项目；Timecode 是现场原生工作流；Pipe 是专业数据与责任项目。
- 如果必须保留：Drum 只保留为两天技术证伪 spike；Timecode 只保留重构后的桌面文件 converter/validator；Pipe 只保留有 pipefitter 专家共同验证的工具组合，不保留单页计算器幻想。
