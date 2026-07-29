# App Store → Web niche 第一轮 live 扫描

日期：2026-07-17  
市场：美国 iPhone  
模式：Internal decision memo

## 当前结论

工作流已经跑通，第一轮抓到 2,983 条榜单记录和 2,454 个唯一 App。30 个请求覆盖总榜与九个目标分类的 free、paid、grossing，全部成功。Apple Lookup 又补齐价格、评分量、描述和更新时间；12 个候选进入评论证据队列。

这一轮改变了最初判断。Chrome 的能力确实足以实现大量工具，但最容易实现的方向已经出现密集的 browser-native 竞品。精确尺寸打印、PDF imposition、cross-stitch pattern、tattoo stencil、CNC/HVAC 计算器、pool chemistry 和 shutter count 都能在当前 SERP 找到直接 Web 产品。机会不再是“把一个 App 搬到网页”，而是找到现有网页没有完成的专业输出合同。

独立复核美国 Productivity 免费榜前 20 后，没有发现可直接立项的 niche。这个区间主要由通用 AI、邮箱、云盘、Office 和系统型工具占据；把 Link to Windows、HP 或 Authenticator 还原成原子任务后，也分别受后台同步/系统权限、打印机设备管理和安全信任边界限制。这进一步说明，研究资源应优先放在各分类 paid 榜和 30–100 位，而不是平均扫描榜首。

目前建议把验证资源集中到三组：

1. **Drum lug tuning / frequency training**：真实付费和社区需求最强，Web Audio 可以完成核心实验。
2. **Production timecode logging**：用户和导出格式非常具体，PWA 技术可行，但需要验证现场手机体验是否压倒 Web 分发优势。
3. **专业 fabrication / measurement micro-tools**：pipe lateral/support、countertop drawing 等任务有明确职业输出；需要继续寻找“网页搜索存在、现有 Web 工具仍缺失”的单点。

## 数据基线

Apple 公开 RSS 实际最多返回 100 条，所以本轮覆盖的是每个榜单前 100，而不是完整前 500。更深榜单需要 AppTweak/Appfigures adapter。当前工作流保存 immutable raw snapshot、normalized JSONL、Apple metadata、machine shortlist 和 review evidence，评分规则变化后可以重跑。

数据源复核还发现 legacy RSS 可能在分类参数错误时返回 HTTP 200 并静默退回总榜。工作流现已校验 `feed.title`、返回条数和原始响应 hash；grossing 分类的标题不包含分类名，因此标为 `legacy_unverified_category`，在 AppTweak/Appfigures 交叉确认前只用于发现候选，不作为精确分类排名证据。[AppTweak Top Charts](https://developers.apptweak.com/reference/top-charts-current)、[Appfigures Ranks](https://docs.appfigures.com/api/reference/v2/ranks)

机器初筛从 2,454 个 App 中标出 958 个待证据复核候选，但这个数量明显过宽。通用描述里的 `photo`、`AI`、`file` 等词会把大型平台和原生相机 App 推高。因此 `machine_screen_score` 只保留为路由分，最终 `evidence_score` 在评论、SERP、社区、竞品价格和原型完成前保持为空。

## 第一梯队：继续验证

### 1. Drum lug tuner / tuning trainer

[iDrumTune Pro](https://apps.apple.com/us/app/drum-tuner-idrumtune-pro/id1234266367) 在美国 Music 付费榜约第 15，售价 $12.99，当前约 2,298 个评分；同一分类还有 [Drumtune PRO](https://apps.apple.com/us/app/drumtune-pro-drum-tuner/id655607914) 位于约第 54。社区里反复出现“App 是否准确”“如何测 lug frequency”“Tune-Bot 是否值得买”的实际问题，用户还会购买约百美元的专用硬件。[近期讨论](https://www.reddit.com/r/drums/comments/1iw971a)、[频率读数问题](https://www.reddit.com/r/drums/comments/1rew4aa)

核心 Web 任务可以限制为：获得麦克风权限；连续捕获敲击；识别 fundamental 与每个 lug 的稳定峰值；记录目标频率；给出逐 lug 偏差。实现上使用 Web Audio + Worker，模型不是必需品。

风险在准确性而不是功能。iOS 麦克风处理、环境噪声、手机距离和击打方式都会改变读数。第一原型必须用同一只鼓对照 Tune-Bot 或现有 App，达到重复性后才讨论产品。

当前判断：**P1 prototype candidate**。

### 2. Production timecode logger

[Timecode+](https://apps.apple.com/us/app/timecode/id590534084) 位于 Photo & Video 付费榜约第 47，售价 $6.99，约 88 个评分。它解决的不是视频编辑，而是拍摄现场快速标记 timecode，并导出 FCPXML、EDL、Premiere XML、SRT、CSV 等下游格式。[产品说明](https://timecodeplus.com/)

这个任务的价值来自格式和现场流程，离线 PWA 可以完成 session、marker、quick label、语音备注、OPFS checkpoint 与文件导出。浏览器不需要完整视频处理。

风险是分发假设可能反转：现场用户本来就拿着手机，原生 App 的单手操作、常亮和系统音频体验可能更好。Web 的优势只有免安装、跨设备和团队模板共享。需要先访谈 5 名 camera operator、DIT 或 script supervisor，再决定是否做原型。

当前判断：**P1 interview candidate；prototype 暂缓**。

### 3. Pipe fabrication ordinate / template calculator

美国 Productivity 付费榜中，[Lateral Pipe Calculator](https://apps.apple.com/us/app/lateral-pipe-calculator/id521690013) 约第 69，[Pipe Support Calculator](https://apps.apple.com/us/app/pipe-support-calculator/id521694054) 约第 75；社区用户会直接推荐这些付费 App，并明确提到 offsets、fishmouths、laterals、saddles 和 ordinate 计算。[App 使用讨论](https://www.reddit.com/r/pipefitter/comments/1ch57ma)、[工作流需求](https://www.reddit.com/r/pipefitter/comments/1qu0kjf)

Web 可以实现分数输入、metric/imperial、8–128 ordinate、打印模板和离线缓存。当前搜索没有首先出现成熟的 exact-purpose Web 工具，竞争信号弱于 CNC/HVAC 泛计算器。

风险同样来自现场：用户戴手套、离线、需要大键盘，手机/PWA 比桌面网站更自然；公式错误会直接造成材料浪费。需要把公式来源、测试样例和专业免责声明作为产品合同，而不是只写一个计算器页面。

当前判断：**P1 evidence candidate**。

### 4. Lightweight countertop drawing + quote handoff

[Countertops Draw](https://apps.apple.com/us/app/countertops-draw/id1617910987) 位于 Business 付费榜约第 28，售价 $4.99，约 16 个评分。任务是把现场尺寸变成带 cutout、backsplash 和边型标记的 scale drawing。商业软件已有 countertop drawing/quoting 模块，例如 [ActionFlow](https://www.actionflow.net/solutions/quoting/countertop-drawing/) 和 [iCounterSoft](https://www.icountersoft.com/drawing-tools)，说明职业工作流存在，但轻量临时工具的空间仍未确认。

浏览器端 Canvas/SVG 足以完成绘图和 PDF 输出。更有价值的 wedge 可能是“客户自测草图 → fabricator 可报价 PDF”，而不是做完整 countertop SaaS。

当前判断：**P2 research candidate**。

## 第二梯队：需求存在，竞争已明显

### Cross-stitch / craft pattern

[StitchSketch](https://apps.apple.com/us/app/stitchsketch/id525117691) 位于 Graphics & Design 付费榜约第 36，售价 $7.99，约 403 个评分。抓到的 50 条近期书面评论中，20 条为一至三星；重复问题包括 250×250 上限、fabric count 设置、DMC/Perler 色表、fractional stitches、PDF 缺页、界面难用和文件丢失。

这些问题非常具体，证明任务真实。不过 [FlossCross](https://www.reddit.com/r/CrossStitch/comments/lpo0un)、[StitchXCross](https://stitchxcross.com/) 和 [Knyt Studio](https://www.knytstudio.com/) 已覆盖浏览器编辑、DMC palette、PDF/SVG、photo conversion 等功能。复制 pattern maker 不成立。

可继续观察的 wedge 是“扫描旧纸质 pattern → 识别 grid/symbol/color → 转成可勾选的交互 pattern”，因为近期社区仍有人描述现有 Pattern Keeper 无法处理扫描图。[纸质图纸数字化讨论](https://www.reddit.com/r/CrossStitch/comments/1ufrfxp/chat_digitizing_paper_patterns/)

当前判断：**P2，改写问题后再研究**。

### Electrical single-line diagram

[SLD | Electrical diagrams](https://apps.apple.com/us/app/sld-electrical-diagrams/id1534899128) 位于 Productivity 付费榜约第 74，售价 $1.99，约 131 个评分。桌面 Web 拖拽 IEC/ANSI symbol 并导出 PDF，在体验上明显优于手机。但 [EleCAD](https://elecas.com.au/elecad) 已提供 browser-based SLD builder；完整 CAD/EDA 市场也很成熟。

可行的 wedge 必须进一步限制行业和交付，例如美国住宅 solar permit one-line、特定设备 BOM 或特定检查表。标准和专业责任增加了维护成本。

当前判断：**P2，等待更窄行业切口**。

### Tattoo stencil / tiled stencil output

[Tattoo Stencil Lab](https://apps.apple.com/us/app/tattoo-stencil-lab/id6758417192) 位于 Graphics & Design 付费榜约第 24，售价 $8.99；[ToneStencil](https://apps.apple.com/us/app/tonestencil-stencil-maker/id6767592281) 约第 52。Canvas/WebGPU、本地处理和 tiled PDF 都容易实现，但当前已有 [StencilMind](https://www.stencilmind.com/)、[StencilX](https://stencilx.com/) 和多款免费在线 stencil maker。StencilMind 甚至给出面向 studio 的高价订阅，说明付费存在，也说明竞争已经进入专业工作流。

当前判断：**P2，只有 thermal printer calibration / exact-size transfer 等更窄输出才继续**。

## 当前淘汰或降级

| 方向 | 判断 | 原因 |
|---|---|---|
| Exact-size photo printing | 降级为 SEO/小工具 | App 需求很强，但 [GridPrint](https://gridprint.app/en/use/exact-size-print) 与 [PrintAtSize](https://www.printatsize.app/en) 已直接覆盖本地处理、真实尺寸和 PDF |
| 通用 local transcription | 淘汰 | [Aiko](https://apps.apple.com/us/app/aiko/id1672085276) 证明本地价值，但通用转录竞争密集；没有垂直输入/输出 wedge |
| PDF 2-up / booklet imposition | 淘汰 | [PDFInOne](https://pdfinone.com/en/pdf-booklet/) 和 [PDF Press](https://pdfpress.app/) 已提供 browser-local 实现 |
| CNC/HVAC 通用计算器 | 淘汰 | 当前已有 [MachiningCalc](https://machiningcalc.com/en)、[Online Ductulator](https://online-ductulator.com/) 等完整站点；公式责任高 |
| Craft/Etsy pricing | 淘汰 | Etsy 自带估算器，当前还有 [MakerMargins](https://makermarginsapp.com/) 与 [CraftWorth](https://craftworth.app/) 等直接竞品 |
| Shutter count | 淘汰通用版本 | [ShutterCount.org](https://shuttercount.org/) 已覆盖文件路径；Canon USB/Wi-Fi 又带来浏览器硬件边界 |
| Pinhole exposure | 作为内容入口 | 规则清楚、Web 易做，但 App 只有约 19 个评分，单独产品规模偏小 |

## Browser 技术门槛

统一实现顺序是 Browser API → WASM/Web Worker → WebGPU 可选加速 → 可续接云任务。Chrome built-in AI 只能作为降本增强，因为官方当前仍要求特定桌面系统、内存/GPU、磁盘空间和首次模型下载，Android/iOS 不能作为同等基线。[Chrome built-in AI 条件](https://developer.chrome.com/docs/ai/get-started)

以下任务直接淘汰纯 Web：持续后台执行、锁屏录音/GPS/BLE、HealthKit、VPN/Network Extension、CallKit、系统键盘、页面关闭后仍要完成本地计算，以及移动端核心依赖 Chrome Extension 或 built-in AI。WebGPU、WebCodecs、File System Access 和 WebUSB/Bluetooth 都必须 feature detect 并准备 fallback。[File System Access](https://developer.chrome.com/docs/capabilities/web-apis/file-system-access)、[WebGPU](https://developer.mozilla.org/en-US/docs/Web/API/WebGPU_API)

## 下一步

下一轮不再扩张候选数量，先完成三个验证：

1. 为 drum tuner 做一个浏览器麦克风频谱 spike，与现有 App/硬件对照 20 次敲击的重复性。
2. 对 pipefitter 社区做 5–10 次问题访谈，确认 ordinate/printable template 是否比手机 App 的大键盘和离线体验更重要。
3. 对 Timecode+ 的目标岗位做 5 次流程访谈，确认免安装/跨平台是否足以抵消原生现场体验。

只有其中一个通过，才进入正式上站。当前最优先的是 drum tuner 技术 spike；它同时具备明显付费证据、重复社区需求和可在浏览器前台完成的核心任务。
