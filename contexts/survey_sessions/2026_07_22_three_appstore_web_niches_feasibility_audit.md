# Drum / Timecode / Pipe 三方向 Web-first 可行性复核

日期：2026-07-22  
模式：Internal decision memo

## 结论

**三个方向按当前定义都不应该直接立项。** 7 月 17 日的初筛证明了“App Store 内有需求”和“浏览器理论上能实现”，但没有证明“Web 是更好的产品形态”或“一个人能快速做成可信生意”。这次复核后：

| 方向 | 当前判断 | 保留动作 |
|---|---|---|
| Drum lug tuner | **No-Go 立项；允许 2–3 天技术证伪** | 只做跨设备精度 spike；过不了即停止 |
| Production timecode logger | **No-Go** | 只有访谈发现一条现有工具反复失败的具体制作管线，才研究窄 converter |
| Pipe fabrication calculator | **通用版 No-Go；窄版 Conditional Go** | 仅考虑专家共建的 dummy-leg/trunnion verified layout pack |

如果目标是“利用 Chrome 能力快速上站”，这三个其实都不是理想样本：Drum 的核心是信号识别与校准，Timecode 的核心是现场可靠性和硬件同步，Pipe 的核心是专业数据与错误责任。它们的门槛恰好都不在前端实现速度上。

## 判断标准的修正

今后的候选不能只问“能否在网页实现”，必须同时满足：

1. **Web 原生优势**：搜索即用、文件输入输出、桌面大屏、链接分享或免安装必须显著改变任务，而不是只少一次安装。
2. **可信交付**：一个人能建立可执行的基准测试、golden corpus 或专家验证；错误成本不能失控。
3. **独立获客**：有 App Store 之外的搜索词、社区入口、模板或免费工具入口。
4. **经济性**：支持和兼容成本不能高于低价一次性收入；最好能形成多个页面共享内核的工具组合。

App 排名和评分只能证明原生渠道内存在需求，不能证明 Web 获客，也不能证明 Web 使用形态成立。

## 1. Drum lug tuner

### 为什么不能直接做

频率图很容易，稳定选对鼓头振动模式很难。一次敲击同时包含 transient、多个非整数泛音、整鼓 fundamental 和局部 lug mode。现有硬件 [Tune-Bot](https://tune-bot.com/tune-bot/)给出的规格是 30–400 Hz、±0.5 Hz resolution、750 ms response，并专门提供 Filter Mode；其[操作说明](https://tune-bot.com/instructions/)要求麦克风位于鼓皮上方、按指定位置敲击，获取正确读数后再锁定 ±18% 频率区间。产品门槛是测量协议和错误读数过滤，不是 FFT。

竞争也已经覆盖三层：$12.99 的 [iDrumTune Pro](https://apps.apple.com/us/app/drum-tuner-idrumtune-pro/id1234266367)已有 lug/resonant tuning、presets、课程和完整教学；约 $100 的专用硬件提供固定安装位置和过滤；[DrumTuner.io](https://drumtuner.io/)及 2026 年出现的新免费 Web tuner 已经占据“打开网页测频率”的位置。因此免安装不是差异化。

Web 还有额外输入不确定性。网页可以请求关闭 `autoGainControl`、`noiseSuppression`、`echoCancellation`，但 [MDN](https://developer.mozilla.org/en-US/docs/Web/API/MediaStreamTrack/getCapabilities)明确说明能力取决于浏览器与硬件，非 exact constraint 只是尽力满足；原生 iOS 则可使用 [`AVAudioSession.Mode.measurement`](https://developer.apple.com/documentation/avfaudio/avaudiosession/mode-swift.struct/measurement)降低系统信号处理。

### 允许继续的唯一方式：2–3 天证伪

不是做 UI，而是保存原始 PCM，完成 onset detection、候选峰、target filter 和重复敲击聚类。至少用 tom、snare、kick 各一只，一台 iPhone、一台 Android，每个 lug 十次敲击，并同时记录 Tune-Bot、iDrumTune 和 Web 结果。

全部通过才继续：

- 1.5 秒内有效读数率 ≥ 90%；
- 相对稳定参考的中位误差 ≤ 1 Hz，P95 ≤ 3 Hz；
- 同一 lug 重复标准差 ≤ 1 Hz；
- 两台手机差异 ≤ 2 Hz；
- overtone / 倍频 / 半频误抓率 < 3%；
- kick、tom、snare 都通过，不能只挑最好测的鼓。

技术通过后再找 20 名鼓手无指导使用；至少 15 人独立完成整鼓 lug equalization、12 人认为不弱于现有 App、5 人愿意立即支付 $10–15。否则最多做免费 SEO/内容工具，不作为独立产品。

## 2. Production timecode logger

### 为什么是明确 No-Go

现场 logger 的原生优势是能力边界，不只是体验更顺。[Timecode+](https://timecodeplus.com/)已经覆盖离线、Quick Labels、time-of-day/manual/external MTC、端侧转录和多格式导出；[Tentacle Live Timecode Notes](https://tentaclesync.com/news/live-timecode-note)可通过蓝牙连接 SYNC E、TRACK E、TIMEBAR；[MovieSlate](https://www.movie-slate.com/)继续向 LTC、Wi-Fi timecode hub、script department 和多机位流程扩展。

Web 在最重要的环节不可靠：Web Bluetooth 在 iOS Safari 不可作为基线，[Web MIDI](https://developer.mozilla.org/en-US/docs/Web/API/Web_MIDI_API)不是 Baseline，[Screen Wake Lock](https://developer.mozilla.org/en-US/docs/Web/API/Screen_Wake_Lock_API)在页面隐藏、锁屏或系统条件变化时会释放。专业用户会预先安装和测试工具，不会为了免安装接受丢日志或偏帧风险。

格式输出也不是一次性开发。[Apple frame-rate 文档](https://developer.apple.com/library/archive/documentation/AppleApplications/Reference/FinalCutPro_XML/FrameRate/FrameRate.html)区分 23.976、24、25、29.97、30、50、59.94、60，并用 `timebase + ntsc` 表达准确比率；还要处理 DF/NDF、rollover、跨午夜、offset、reel、不同 EDL/ALE 方言。[Adobe](https://helpx.adobe.com/premiere/desktop/organize-media/import-files/migrate-from-final-cut-pro-x.html)明确说明 Premiere 不能直接导入现代 FCPXML，转换后也可能映射不完整。真实维护对象是“格式 × 帧率 × NLE × 版本”兼容矩阵。

“改成通用 converter”也不是现成空位。[EditingTools.io Timecode Notes](https://en.editingtools.io/timecodenotes/)已经提供多人协作、快捷按钮、offset 和多 NLE 导出，其产品套件还覆盖 EDL、ALE、marker、FCPXML converter 和离线 converter。免费 Web timecode calculator 也已经很多。

### 重新进入候选池的门槛

只能从具体失败管线出发，例如“某录机 CSV → Premiere grouped clips markers”或“批量修复 DF/NDF、午夜跨日和 reel 名”。不能先做万能转换器。

重新研究前必须满足：

- 访谈 12 人：4 名 logger/script supervisor、4 名 DIT/assistant editor、4 名后期编辑；
- 至少 5 人描述同一个、反复发生、现有工具未解决的问题；
- 收到至少 30 份匿名化真实文件；
- 在目标 NLE 实机达到 0 rejected file、marker 误差 0 帧、round-trip 可验证；
- 至少 5 个团队预付 $15–30/月或 $20–50/项目，或 2 家制作公司付费 pilot。

在这些证据出现前，从当前候选中淘汰。

## 3. Pipe fabrication calculator

### 为什么通用版本也应淘汰

原判断“Web 竞争弱”已经过时。免费 Web 工具已覆盖 fishmouth、offset、1:1 PDF/SVG、DXF、3D 和离线使用，例如 [Pipe Calculators](https://pipecalculators.com/)、[Trade-Schools fishmouth generator](https://www.trade-schools.net/tools/pipe-miter-template) 和 [FabCalc](https://fabcalc.app/)。原生侧还有 [Pipe Trades Pro](https://www.calculated.com/mobile/prd267/Pipe-Trades-Pro-4095-Advanced-Pipe-Trades-Calculator.html)及低价终身制 [PipeFit Pro](https://pipefitproapp.com/)；后者用 $5.99 已提供十个计算器和七组参考表。

这条线的真正门槛是信任工程。[ASME B16.9](https://www.asme.org/codes-standards/find-codes-standards/b16-9-factory-made-wrought-buttwelding-fittings)覆盖尺寸、公差、评级、测试与标识，当前标准本身需要购买；管 OD/壁厚还涉及 B36.10/B36.19，压力与工艺又涉及 B31 等。NPS/OD、pipe/tube、schedule、LR/SR、实际 elbow radius、ovality、kerf、bevel、root gap、weld shrinkage 和打印缩放都会改变结果。

社区已经抓出新产品的 [1/2 英寸与 2 英寸 take-out 错误](https://www.reddit.com/r/pipefitter/comments/1rri7jg/)，开发者随后放弃通用公式，改为 ASME 表。一个公式错误会直接造成坏切料，免责声明无法替代验证。

### 唯一可保留的窄方向

不是“全能 pipe calculator”，而是当前仍有现场长尾证据的 **dummy-leg / trunnion on elbow ordinate + 可校准打印放样**。只承诺 fabrication layout aid，不承诺结构承载、压力规范或安装合规。

最低可信范围：

- measured OD、自定义 elbow radius、LR/SR、concentric/eccentric、8–128 ordinate；
- fraction/metric；ordinate table + 1:1 PDF/SVG；
- 明示 assumptions、excluded allowances、标准版本和数据 provenance；
- 100–200 个合法来源 golden cases，加性质测试和单位往返测试；
- 5 名真实 pipefitter/fabricator 参与，至少 20 次模板试切；
- 数值对 reference 误差 ≤ 1/64 in，打印校准误差 ≤ 0.5%；实际 fit-up 阈值由领域专家定义。

商业 Go gate：10 次访谈中至少 5 人过去三个月做过目标任务、3 人愿意支付 $15–30 one-time，且收集到至少 10 个现有工具无法处理的案例。没有持续参与的领域专家，直接 No-Go。

这个方向即使通过，也更像多个专业 SEO 页面共享几何/单位/管表/导出内核的“小而稳工具包”，不是 SaaS。

## 决策与后续

当前优先级不是三选一正式开发，而是：

1. **只批准 Drum 的 2–3 天 spike**，因为它可以用低成本实验迅速证伪；这不等于批准产品。
2. **停止 Timecode 原型**，除非先获得具体失败管线和付费 pilot。
3. **停止通用 Pipe calculator**；只有找到领域专家且 dummy-leg/trunnion 访谈过 gate，才进入原型。

更重要的流程调整：下一轮 App Store 扫描要新增 `web_advantage_score`、`trust_burden`、`distribution_evidence` 和 `support_surface` 四个硬字段。凡是“Web 只是能做，但原生更符合现场动作”、或“结果错误需要领域专家背书”的候选，不再进入快速上站队列。
