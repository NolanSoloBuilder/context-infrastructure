# AI 长视频转短视频竞品分析

调研日期：2026-06-08

## 结论先行

不建议做一个泛化版 `ShortsGenerator.ai`。这个方向已经进入功能同质化阶段：AI clipping、caption、auto reframe、export、scheduler、brand template、team workspace 都已经被头部竞品覆盖。你如果只是做“上传长视频，AI 自动生成 Shorts”，会直接撞上 OpusClip、Vizard、Klap、Quso / vidyo.ai、2short.ai，获客和留存都会被挤压。

但这个方向仍然有可做空间，入口不是更便宜的 clipping tool，而是更窄的垂直工作流。最值得做的形态是：针对某一种内容类型，把“选片段是否准”做到明显更好，再把发布前后的业务结果接住。比如 podcast / interview、course / webinar、real estate listing、B2B webinar-to-lead-gen、中文播客切小红书 / 视频号。

用户差评给出的核心机会是：大家都能生成 clip，但用户不信任 AI 的片段判断、字幕和账单。产品真正要赢的是“这个片段为什么值得发、发到哪里、怎么改成我的账号风格、有没有带来结果”。

## 竞品总览

| 产品 | 定价 | 核心功能 | 评价信号 | 对新进入者的压力 |
|---|---:|---|---|---|
| OpusClip | Free；Starter `$15/mo`；Pro `$29/mo` 或年付 `$14.5/mo`；Business custom | AI clipping、Virality Score、animated captions、AI reframe、AI B-roll、scheduler、brand template、XML export、team workspace | Trustpilot `4.0/5`，`414` reviews；`1-star 21%` | 品牌、功能、企业销售都强；泛工具正面撞它不划算 |
| Vizard.ai | Free；Creator / Business 按 credits，官网当前抓取价格显示异常为 `$0`，但 plan limit 清楚 | AI clipping、dynamic captions、speaker detection、auto-reframe、emoji / B-roll、social captions、video editor、API | Trustpilot `4.8/5`，`2,527` reviews；官网还标 G2 `4.7`、Capterra `4.9` | 口碑很强，覆盖创作者和团队，差评空间小 |
| Klap | 年付 `$14/mo`、Pro `$39/mo`、Pro+ `$94/mo` | long video to shorts、HD / 4K export、AI dubbing 29 languages、API | Trustpilot `2.9/5`，`26` reviews；`1-star 42%`，样本小且偏噪音 | 功能窄，但有 dubbing 差异；口碑弱说明服务和信任可作为突破点 |
| 2short.ai | Free；Lite `$9.90/mo`；Pro `$19.90/mo`；Premium `$49.90/mo` | 专注 YouTube creator，按 AI analyzing hours 计费，URL import、server-side export | G2 `4.5/5`，但只有 `5` reviews；Capterra `0` reviews | 价格低、定位窄；适合说明“窄定位可以活”，但 review moat 很弱 |
| Quso.ai / vidyo.ai | Free；Lite `$29/mo` 或年付约 `$15/mo`；Essential `$39/mo`；Growth `$49/mo` | AI clips、captions、resizing、social scheduling、analytics、content planner、brand kit | Trustpilot 上 vidyo.ai 只有 `1` review；官网重定向到 Quso，产品已转成 social media growth suite | 它已经从 clipping 扩展到社媒运营套件，新进入者不宜跟它比功能广度 |

## 竞品功能拆分

### OpusClip

来源：[OpusClip Pricing](https://www.opus.pro/pricing)、[OpusClip Trustpilot](https://www.trustpilot.com/review/opus.pro)

OpusClip 是这个赛道的标杆。官网价格页列出：Free `60 credits/mo`，Starter `$15/mo` 给 `150 credits`，Pro `$29/mo` 或年付 `$14.5/mo`，Business custom。功能覆盖 AI clipping、Virality Score、animated captions、auto post、editor、brand template、filler / silence removal。Pro 往上还有 AI B-roll、10+ input sources、Premiere / DaVinci XML export、multiple aspect ratios、social scheduler、team workspace。

评价上，Trustpilot 显示 `414` reviews、`4.0/5`。正面集中在省时间、易用、能生成多个 clip、caption 和竖屏优化。负面集中在 slow processing、failed projects、glitches、support delay、subtitle accuracy、video alignment。星级分布里 `1-star` 有 `21%`，这说明即便头部产品也有明显差评。

对你来说，OpusClip 证明了两个事实：市场存在，而且泛工具头部已经有完整功能栈。新产品如果从“我也能自动切视频”出发，差异会很弱。

### Vizard.ai

来源：[Vizard Pricing](https://vizard.ai/pricing)、[Vizard Trustpilot](https://www.trustpilot.com/review/vizard.ai)

Vizard 更像“视频再利用 + 轻编辑 + social content”平台。官网列出 Free `60 credits/month`，Creator 从 `600` monthly credits 起，Business 也从 `600` monthly credits 起；1 credit = 1 minute uploaded video。功能包括 AI-generated clips、720p / 4K export、video editor、watermark removal、social scheduling、longer storage、API rate limit、auto subtitling。Trustpilot 公司简介还列出 AI Dynamic Captioning、speaker detection、auto-reframe、emoji / B-roll、social captions。

评价上，Trustpilot 显示 `2,527` reviews、`4.8/5`。这是本组里最强的公开口碑。用户正面反馈集中在跨语言处理、功能齐全、节省时间。能看到的小抱怨包括免费额度希望更多、希望批量下载 clips。

Vizard 对新进入者的压力在于，它不只功能多，口碑也好。你如果做横向 clipping，很难靠“体验更好”说服用户迁移。

### Klap

来源：[Klap Pricing](https://klap.app/pricing)、[Klap Trustpilot](https://www.trustpilot.com/review/klap.app)

Klap 的价格页非常简洁：年付 `$14/mo` 上传 `10` 个视频、生成 `100` clips；Pro `$39/mo` 上传 `30` 个视频、生成 `300` clips、4K download、AI dubbing 29 languages；Pro+ `$94/mo` 上传 `100` 个视频、生成 `1000` clips。Klap 页面还显示 `8.5M clips made by 3.5M creators`。

评价上，Trustpilot 只有 `26` 条，评分 `2.9/5`，`1-star 42%`。负面样本里有 free trial 预期落差、沟通问题、支持响应慢。Trustpilot 也提醒该公司没有邀请客户评价，因此样本可能不代表整体用户。

Klap 的启发是：小团队可以靠窄功能和价格活下来，但口碑和支持会成为明显弱点。它的 AI dubbing 是一个差异方向，说明这个赛道还能用“某个工作流能力”做局部差异。

### 2short.ai

来源：[2short.ai Pricing](https://2short.ai/pricing)、[2short.ai G2](https://www.g2.com/sellers/2short-ai)、[2short.ai Capterra](https://www.capterra.com/p/10015861/2short-ai/)

2short.ai 是更窄的 YouTube Shorts generator。它的官网写得很清楚：所有 plan 都给 full access，主要差异是 AI video analysis hours。Free 给 `30 minutes/month`，Lite `$9.90/mo` 给 `5 hours/month`，Pro `$19.90/mo` 给 `15 hours/month` 和 unlimited fast server-side exports，Premium `$49.90/mo` 给 `50 hours/month` 和 priority support。

评价上，G2 显示 `4.5/5`，但只有 `5` 条 reviews；Capterra 目前 `0.0`，没有 review 数据。这个产品说明低价、窄定位、按分析时长卖是可行方向，但它还没有建立强 review moat。

如果要做小而快的 MVP，2short.ai 比 OpusClip 更接近可复制对象：它没有试图做社媒运营全套，而是服务 YouTube creator 的一个动作。

### Quso.ai / vidyo.ai

来源：[Quso / vidyo.ai Pricing](https://quso.ai/pricing)、[vidyo.ai Trustpilot](https://www.trustpilot.com/review/vidyo.ai)

vidyo.ai 已重定向到 Quso.ai，定位从 AI clipping 扩展到 social media growth suite。价格页显示 Free、Lite `$29/mo` 或年付折后 `$15/mo`、Essential `$39/mo`、Growth `$49/mo`。功能包括 AI Clips & Captions、AI Video Generator、AI resizing、unlimited 1080p exports、social scheduling、analytics、custom templates、brand kit、priority support。

Trustpilot 上 vidyo.ai 只有 `1` 条 review，不能作为强口碑判断。官网描述里，它面向 video creators、editors、podcasters、marketers、small business owners，提供多比例视频、直接发布 / 排期、captions、templates、AI content assistant、Virality Predictor、filler word removal。

它的方向更像“从 clipping 往 social publishing / analytics 扩张”。这条路更重，对小团队意味着 scope 容易失控。

## 差评模式

这些竞品的差评集中在四类。

第一类是 AI 选片段不够准。用户真正要的是“像人类剪辑师一样判断哪里值得发”。只要输出的 clip 缺上下文、hook 弱、节奏不对，用户就会手工返工。这个抱怨是产品核心，不是边缘体验。

第二类是字幕、对齐、reframe 和导出质量。视频工具的输出很直观，字幕错、脸没居中、导出失败、进度卡住都会立刻破坏信任。

第三类是 credits / billing / cancellation。OpusClip 的差评里能看到 credits 退款、重复扣费、套餐权益变化、取消订阅等问题。ShortsGenerator 和 Klap 也有类似信任风险。AI 视频处理天然要用 credits / minutes 控成本，但 credits 体系越复杂，差评越容易出现。

第四类是 support 响应。用户通常是在赶发布或赶客户交付时用这类工具，一旦处理失败，慢支持会把产品问题放大成信任问题。

## 面向“要不要做”的判断

我的判断：可以做，但只能做窄场景，不该做泛工具。

不适合做的版本：

- “OpusClip 但更便宜”
- “ShortsGenerator 但 UI 更好”
- “支持所有视频类型的一键生成 viral shorts”
- “先做 clipping，再慢慢加 scheduler、analytics、team、brand kit”

这些版本的问题在于，功能会被头部产品追平，获客要靠 SEO / affiliate / paid ads，留存又会被高 churn 拖住。ShortsGenerator 的 Flippa 数据已经说明了这点：`70k users` 只有 `$1,130 MRR`，`24% churn`。这不是一个很轻松的 SaaS 模型。

可以做的版本：

1. **Podcast / interview clips for serious creators**  
   只做对话类内容，核心是 transcript 语义切片、speaker-aware reframe、上下文保留、hook rewrite、episode highlights。卖点是“比通用工具更懂对话内容”。

2. **Course / webinar to short lessons**  
   把课程、直播、webinar 切成短知识点，附 title、summary、quiz、CTA。这个比“viral shorts”更适合 B2B / creator education，也更容易卖给有预算的人。

3. **B2B webinar-to-lead-gen content pack**  
   输入一场 webinar，输出 clips、LinkedIn posts、newsletter snippet、landing page highlights、sales follow-up snippets。这里客户买的是 pipeline 支持，不是剪视频分钟数。

4. **中文内容转小红书 / 视频号 / 抖音发布包**  
   英文竞品对中文语境、字幕风格、平台标题、封面文案、口播节奏不一定好。这里的机会在本地平台语感和发布模板，而不是底层视频处理。

如果你要做，我建议 MVP 选第 2 或第 3 个。Podcast clips 用户多，但竞争也最直接；course / webinar 更接近付费能力强的用户，且对“viral”要求没那么玄学，评价标准更明确：能不能把长内容拆成可发布、可转化、可复用的内容包。

## 推荐 MVP

方向：`Webinar / course video → short content pack`

目标用户：在线课程创作者、B2B SaaS marketing team、小型 agency。

最小功能：

- 上传 YouTube / Loom / Zoom recording 或本地视频。
- 自动转写，按 topic 切段。
- 输出 5-10 个候选 short clips，每个带 hook、summary、CTA。
- 允许用户在 transcript 上微调起止点。
- 自动 caption、speaker reframe、9:16 / 1:1 / 16:9 导出。
- 同时生成 LinkedIn post、newsletter snippet、X thread、小红书标题 / 封面文案。
- 结果按 content pack 展示，而不是一堆孤立 clips。
- 透明按分钟计费，不做复杂 credits；失败任务返还分钟数。

定价建议：

- Free：30 分钟/月，带 watermark，适合验证。
- Solo：`$29/mo`，300 分钟/月，基础 content pack。
- Pro：`$79/mo`，1000 分钟/月，brand voice、批量导出、无水印。
- Team / Agency：`$199/mo` 起，多 workspace、客户项目、白标导出。
- 一次性 setup：`$299-999`，帮客户配置 brand voice、CTA 模板、输出格式和内容策略。

关键差异：

不要把产品说成“AI 自动剪 viral shorts”。应该说成“把一场长内容变成可发布的增长素材包”。这样你避开了最难证明的 viral 承诺，也避开了跟 OpusClip 直接抢 creator tool 心智。

## Go / No-Go

Go，但条件很严格：

- 只做一个明确内容类型，先不要支持所有视频。
- 先证明 clip selection 比通用工具更准。
- 把 pricing 做成 minutes + content pack，不做复杂 credits。
- 支持失败返还分钟数，主动规避差评里最常见的 billing 信任问题。
- 从一开始收集 review，尤其是具体 use case 的 review；这个赛道的购买决策高度依赖第三方评价。

No-Go 的信号：

- 如果 MVP 输出的 clip 仍然需要用户大量手工返工。
- 如果只能靠低价和免费额度获客。
- 如果目标用户只是泛 creator，没有更具体的付费场景。
- 如果你没有渠道拿到足够多真实长视频样本做评估。

最终判断：这个方向能做成小生意，但不适合做成“再一个 AI clipping SaaS”。你要卖的是某类长内容的再分发 workflow，而不是视频剪辑按钮。
