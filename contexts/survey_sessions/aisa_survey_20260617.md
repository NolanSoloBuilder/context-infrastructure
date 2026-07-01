# AIsa 调研备忘录

日期：2026-06-17  
对象：https://aisa.one/?utm_source=twitter&utm_medium=text&utm_campaign=cellinlab  
中间材料：`tmp/2026_06_17_aisa_survey/`

## 结论

AIsa 当前更像一个早期的 agent capability marketplace，而不是单纯的 OpenRouter 替代品。它把四件事放在同一个叙事里：模型网关、第三方数据/API 聚合、可安装的 agent skills、以及基于 Circle Nanopayments / x402 / MPP 的机器到机器支付。官网把它称为 agent economy 的 capability/payment layer，这个定位比模型聚合更宽。

可验证的部分主要是 API catalog、skills catalog、公开 GitHub 资产和部分投资/合作背书。真正有战略差异的部分是 paid APIs + agent-readable skills + nanopayment settlement，但这部分仍带有明显 private beta 和发布叙事成分。换句话说，AIsa 已经有一批可展示的接口、技能和文档资产；是否已经形成稳定、可依赖的生产级 agent payment network，目前证据不足。

如果从 Mindspace / Codex App / agent runtime 角度看，AIsa 最值得借鉴的不是模型路由，而是它把 capability 做成可发现、可计费、可安装、可被 agent 直接调用的层。这个方向对长期有价值。不过 AIsa 自己也暴露了一个风险：产品线压得太满，用户第一眼很难判断它到底先解决哪一个高频痛点。

## 产品拆分

AIsa 的官网和 docs 把产品拆成几层。

第一层是 Model Gateway。它声称通过一个 API key 路由 GPT、Claude、Gemini、Grok、DeepSeek、Qwen、Kimi、MiniMax、GLM、Seed、Seedream、Wan 等模型。官方 docs 写明多数模型走 OpenAI-compatible chat completions，部分模型暴露 Anthropic Messages、OpenAI Responses、Gemini GenerateContent 或 image generation routes。这里的定位接近 OpenRouter，但 AIsa 把模型网关放在更大的 agent capability 叙事里。

第二层是 API catalog。`https://aisa.one/api` 页面列出了多个 API 家族：Chat 5 个 endpoint、Twitter 32 个、Tavily Search 4 个、Financial 22 个、YouTube 1 个、Scholar 4 个、Kalshi 4 个、Perplexity 4 个、Polymarket 10 个、CoinGecko 21 个、DataForSEO 445 个、Apollo 54 个、Agent Mail 46 个。`https://aisa.one/api/tavily-search` 还展示了具体 endpoint：`POST https://api.aisa.one/apis/v1/tavily/search`。

第三层是 Skills。`https://aisa.one/skills` 显示 41 个 skills，覆盖 SEO keyword research、trend forecast、Twitter autopilot、MarketPulse、crypto market data、prediction market arbitrage、multi-source search、media generation、AIsa LLM router 等。页面明确标注这些 skills 可用于 OpenClaw、Claude Code、Hermes。公开 GitHub 也能看到 `AIsa-team/agent-skills` 仓库，说明它至少在以可安装技能资产的方式组织这层能力。

第四层是机器支付。官网说每个 endpoint 都支持 nanopayment-enabled，支付流包括 Circle Nanopayments 或 MPP / x402-style flow；同时导航里把 Circle Nanopayments 和 Machine Payment Protocol 标成 Private Beta。AIsa 还有 `AIsa-team/nanopayment-x402` 和 `AIsa-team/tempo-mpp-skill` 这类仓库，说明团队确实在围绕支付协议做 demo / skill。但这一层还不能按成熟产品理解。

第五层是 Foundry。官网写的是 pre-configured OpenClaw instances、cloud-hosted agents、内置 monitoring / guardrails / billing，但页面同时标注 Coming Soon。这个部分现在更像路线图。

## 证据强弱

官网和 docs 是最完整的信息源，但它们只能证明 AIsa 想被市场如何理解。它们的强 claim 包括 one key、1000+ LLMs/APIs/Skills、100+ data APIs、stablecoin payments、5,000+ agents already running。这里面有些能被旁证，有些仍缺独立验证。

API/skills 目录是相对强的证据。`/api` 和 `/skills` 页面列出了具体 endpoint families、数量和功能描述，sitemap 也列出大量 API 路由，`lastmod` 是 2026-06-17。GitHub 侧，`AIsa-team` 组织下有 `docs`、`agent-skills`、`cli`、`API-use-case-demo`、`aisa-cookbook`、`nanopayment-x402` 等公开仓库。其中 `agent-skills` 有 12 stars、3 forks，`docs` 最近 pushed 到 2026-06-15。这说明项目不是纯 landing page。

不过也有冲突信号。`https://aisa.one/models` 静态抓取时显示 catalog last updated 2026-06-10，但页面里的 visible model count 是 `0`，处于 loading live catalog 状态；这可能是客户端渲染/接口加载问题，也可能是 catalog API 对未登录访问不可见。它不能直接推翻模型网关存在，但提醒我们不要把 homepage 的模型数量当作已验证事实。

另一个冲突是身份入口。官网 footer 搜索结果和某些页面链接出现 `github.com/aisa-one`，但首页 JSON-LD 的 `sameAs` 指向 `https://github.com/AIsa-team` 和 `https://www.linkedin.com/company/aipayhq`；搜索结果里的 LinkedIn 主页面是 `aisaonehq`。`AIsa-team` 的公开仓库更完整，所以本报告把它视为主 GitHub 证据源，同时记录这种命名漂移。这是早期 startup 常见状态，但对开发者信任感有影响。

支付层的外部环境是真实的。Circle 官方 Nanopayments 页面说 Gateway balance 可做低至 `$0.000001` 的转账；x402 官方站把它定义为 internet-native payments standard；Coinbase 也在 2025 年发布过 x402，定位为让 APIs、apps、AI agents 通过 HTTP 直接稳定币支付。这些只能证明底层生态存在，不能证明 AIsa 已经把它稳定产品化。

投资/背书方面，LinkedIn 页面说 AIsa 有 2-10 人，位于 San Francisco / Singapore，backed by Tribe Capital、Draper Associates、BoostVC and others。Draper portfolio 页面把 AIsa / AIPay Inc. 列为 current portfolio company，并定位在 AI payments infrastructure、blockchain payment systems、AI commerce platforms。官网上还出现 Alibaba、Saison 等 logo，但这两个我没有找到足够独立的确认来源。

## 竞品位置

如果和 OpenRouter 比，AIsa 的差异不是模型数量或路由体验。OpenRouter 官方说自己提供 400+ AI models through a single API，并且已经有更强的开发者认知。AIsa 直接在模型网关上硬碰 OpenRouter，短期并不占优势。

AIsa 的可辩护位置在 OpenRouter 之外：把付费数据源、SaaS API、agent skills、email/social/finance/search 能力打包成 agent 可调用的 marketplace，再把账单和支付统一掉。这个方向更接近 capability registry + billing layer。模型只是其中一种资源。

真正的竞争对手会分散在几类：

- OpenRouter / LiteLLM：模型网关和 routing abstraction。
- Composio / Pipedream / Zapier MCP 类产品：tool/API connector 和 action layer。
- RapidAPI / data marketplace：付费 API 发现和计费。
- Circle / Coinbase x402 / Cloudflare Agents SDK 相关生态：agent-native payment rails。
- OpenClaw / Claude Code / Cursor / Hermes：技能安装和 agent runtime 分发入口。

AIsa 的野心是把这些层合在一起，但早期产品最难的是「合」之后的第一高频场景。如果没有一个明确的 killer workflow，用户会把它看成又一个 API 超市。

## 可借鉴点

对我们有用的点有三个。

第一，capability 需要有 registry 形态。AIsa 不是只说「我们支持很多 API」，而是把 API endpoint、skill、适用 agent runtime、计费方式放在同一个目录结构里。这个形态适合 agent 自动发现，也适合开发者快速判断是否值得接入。

第二，skills 是比裸 API 更接近 agent 用户心智的包装。比如 SEO keyword research、trend forecast、market pulse、prediction market arbitrage 这些名称不是 API 名，而是工作流名。agent 平台如果只暴露工具列表，会把组合成本留给用户；skills 把组合后的意图封成一个安装单位。

第三，预算和支付控制需要前置到 agent runtime。AIsa docs 强调 API key、usage logs、wallet、budgets、per-call pricing。即使不做 crypto payment，agent 自主调用外部资源时也必须有 spend control、usage audit 和 per-call attribution。这里对 Mindspace 的 workspace/source/memory/artifact/run 体系有启发：外部能力调用不应该只是工具调用日志，还应该成为可审计的资源消费事件。

## 风险判断

AIsa 当前最大风险是叙事过宽。官网第一屏说 transaction network，下面又说 SEO keywords；导航里有 Model Gateway、API、Skills、Machine-to-Machine、Foundry；文档里又讲 OpenClaw、Hermes、wallet、dashboard、pricing。每一层都合理，但叠在一起会稀释「我今天为什么接入它」。

第二个风险是证据层级不均衡。API 和 skills catalog 有可见资产；支付网络、5,000+ agents、Foundry、A2A discovery 这些 claim 的独立证据偏弱。尤其是 `/.well-known/agent.json` 在本次抓取中返回 404，这让 agent discovery 的成熟度需要保留疑问。

第三个风险是信任门槛。AIsa 代理的是 LLM、Twitter、financial、email、Apollo 等高敏 API。安全页说 prompts 和 outputs 不存储，只保留有限 operational metadata，并提醒 upstream providers 的 policy 仍适用。这个表述合理，但企业用户会继续追问 SOC2、DPA、subprocessor list、data residency、provider passthrough policy、API key 权限边界。公开页面暂时没有足够信息回答这些问题。

第四个风险是 marketplace 冷启动。要成为 capability marketplace，需要两边都有密度：agent 开发者愿意来找能力，API/provider 愿意把服务挂进去。AIsa 现在更像团队自己先集成一批能力，再借 OpenClaw / Claude Code / Hermes 这类入口分发。这个策略合理，但需要一个明确场景带动，不然 marketplace 会变成目录页。

## 判断

AIsa 值得持续观察，尤其是它对 agent capability 和 payment 的组合方式。它短期不是一个可以直接学习产品完整形态的成熟样本，而是一个方向信号：未来 agent 平台的外部能力层，可能会从「工具连接」演化成「能力发现、技能安装、调用计费、预算控制、支付结算」的一体化层。

如果我们要吸收这个方向，建议先学 registry + skill packaging + spend audit，不急着学 nanopayment。对金融/知识工作类 agent 来说，最先产生真实价值的不是 agent 自己用 USDC 付费，而是用户能清楚看到：这个 run 调用了哪些外部能力、花了多少钱、拿回哪些证据、这些调用是否可复现。

AIsa 对我们最有用的问题不是「要不要做一个 AIsa」，而是：Mindspace 的 source、memory、artifact、run 之外，是否需要一个 first-class `capability` / `provider` / `spend_event` 层。我的倾向是需要，但要从一个强工作流切入。例如金融 agent 里的 market data、filing retrieval、analyst estimates、news search、brokerage action 这些能力，比泛 API marketplace 更容易形成闭环。

## 参考来源

- AIsa homepage: https://aisa.one/
- AIsa docs home: https://aisa.one/docs/guides
- AIsa API catalog: https://aisa.one/api
- AIsa skills catalog: https://aisa.one/skills
- AIsa model catalog: https://aisa.one/models
- AIsa Tavily endpoint: https://aisa.one/api/tavily-search
- AIsa security docs: https://aisa.one/docs/guides/security
- AIsa pricing docs: https://aisa.one/docs/guides/pricing
- AIsa sitemap: https://aisa.one/sitemap.xml
- AIsa Arc hackathon blog: https://aisa.one/blog/aisa-data-layer-agentic-economy-arc
- AIsa-team GitHub: https://github.com/AIsa-team
- aisa-one GitHub: https://github.com/aisa-one
- AIsa LinkedIn: https://www.linkedin.com/company/aisaonehq
- Draper portfolio: https://www.draper.vc/portfolio/alsa
- Prospeo enrichment profile: https://prospeo.io/c/aisa-ai-agent-payment-network
- OpenRouter about: https://openrouter.ai/about
- OpenRouter quickstart: https://openrouter.ai/docs/quickstart
- Circle Nanopayments: https://www.circle.com/nanopayments
- x402 official: https://www.x402.org/
- Coinbase x402 launch: https://www.coinbase.com/developer-platform/discover/launches/x402
