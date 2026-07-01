# AIsa Survey Scratchpad

Date: 2026-06-17
Target URL: https://aisa.one/?utm_source=twitter&utm_medium=text&utm_campaign=cellinlab

## Initial Read

AIsa positions itself as a capability and payment layer for the agent economy. The homepage says one API key can route LLMs, data APIs, skills, and machine-payment flows. The product surface has four layers:

- Model Gateway: LLM/media model routing.
- API catalog: search, Twitter/X, financial data, prediction markets, DataForSEO, Apollo, Agent Mail, etc.
- Skills: packaged workflows that combine these endpoints for agent tools such as Claude Code, OpenClaw, and Hermes.
- Machine-to-machine payments: Circle Nanopayments / MPP / x402-style payment flows, currently marked private beta.

## Claim Extraction

| Claim | Source tier | Verification channel | Current status |
|---|---:|---|---|
| AIsa is a unified API gateway for LLMs, data APIs, skills, and payments. | Tier 1, homepage/docs | API catalog pages, sitemap, GitHub repos, docs repo | Partly verified. API and skills catalog pages exist; model catalog frontend loaded with `0` visible models during scrape, while docs claim support. |
| One key gives access to 100+ data APIs. | Tier 1, homepage/docs | `/api` catalog and sitemap endpoint list | Partly verified. `/api` page lists endpoint families with endpoint counts, including DataForSEO 445 endpoints, Apollo 54, Agent Mail 46, Twitter 32, Financial 22, CoinGecko 21. Actual calls require API key and were not tested. |
| 41 skills are available. | Tier 1, `/skills` | Skills page and GitHub `agent-skills` repo | Partly verified. `/skills` page lists 41 skills; public repo `AIsa-team/agent-skills` exists with 12 stars, 3 forks as of this run. |
| AIsa is backed by Alibaba, Tribe Capital, Draper Associates, Saison. | Tier 1, homepage | LinkedIn, Draper portfolio, third-party funding databases | Mixed. LinkedIn says backed by Tribe, Draper, BoostVC and others; Draper portfolio confirms AIsa/AIPay. Alibaba/Saison logos appear on homepage but were not independently confirmed. |
| Every endpoint is nanopayment-enabled through Circle Nanopayments or MPP / x402 flows. | Tier 1, homepage/blog/docs | Circle Nanopayments docs, x402 docs, AIsa GitHub repos | Partly verified. Circle/x402 are real external rails; AIsa has `nanopayment-x402` and `tempo-mpp-skill` repos. Product is still shown as private beta and not externally validated in production. |
| AIsa has agent discovery / A2A-compatible manifests. | Tier 1, homepage/docs | `.well-known` routes and sitemap | Weak. `/.well-known/agent.json` returned 404 during this run. Homepage still links to A2A Compatible. |
| Foundry deploys production-ready cloud-hosted agents. | Tier 1, homepage/docs | Product page and repo evidence | Unverified. Homepage marks Foundry as Coming Soon. |

## Source Notes

### Official AIsa

- Homepage: https://aisa.one/
  - Claims: "The Transaction Network for AI Agent Economy", "One key, every capability your agent needs", "1000+ LLMs, APIs and Skills", private beta machine-to-machine payments, Foundry coming soon.
- Docs home: https://aisa.one/docs/guides
  - Claims: AIsa routes GPT, Claude, Gemini, Grok, DeepSeek, Qwen, Kimi, MiniMax, GLM, Seed, Seedream, Wan; gives 100+ APIs and a wallet.
- API catalog: https://aisa.one/api
  - Evidence: shows grouped endpoint families and endpoint counts.
- Skills catalog: https://aisa.one/skills
  - Evidence: shows "41 skills available" and many skills tagged for OpenClaw / Claude Code / Hermes.
- Tavily API page: https://aisa.one/api/tavily-search
  - Evidence: specific endpoint `POST https://api.aisa.one/apis/v1/tavily/search`.
- Models page: https://aisa.one/models
  - Evidence conflict: page says catalog last updated 2026-06-10, but scrape showed 0 available models while loading live catalog.
- Security page: https://aisa.one/docs/guides/security
  - Claims: no prompt/output storage; limited operational metadata; upstream provider policies still apply.
- Pricing page: https://aisa.one/docs/guides/pricing
  - Claims: token pricing for LLMs, per-call pricing for non-LLM APIs, usage logs and no fixed monthly platform fee.
- Sitemap: https://aisa.one/sitemap.xml
  - Evidence: route inventory lastmod 2026-06-17.
- AIsa Arc blog: https://aisa.one/blog/aisa-data-layer-agentic-economy-arc
  - Claim: Circle selected AIsa as technology partner for Agentic Economy on Arc hackathon.

### GitHub

- `AIsa-team` org API: https://api.github.com/orgs/AIsa-team/repos?per_page=100
  - Public repos include `docs`, `agent-skills`, `cli`, `nanopayment-x402`, `tempo-mpp-skill`, `API-use-case-demo`, `aisa-cookbook`.
  - `agent-skills`: 12 stars, 3 forks, pushed 2026-05-27.
  - `docs`: created 2025-11-25, pushed 2026-06-15.
  - `nanopayment-x402`: created 2026-04-09, pushed 2026-05-01.
- `aisa-one` profile API: https://api.github.com/users/aisa-one/repos?per_page=100
  - Looks like a separate user/profile with small repos and OpenClaw forks. The homepage JSON-LD points to `AIsa-team`, so `AIsa-team` is treated as the primary evidence source.

### External Validation

- LinkedIn company page: https://www.linkedin.com/company/aisaonehq
  - Claims: 100+ models, composable skills, deployable agents, backed by Tribe Capital, Draper Associates, BoostVC and others; company size 2-10, locations San Francisco and Singapore.
- Draper portfolio page: https://www.draper.vc/portfolio/alsa
  - Confirms AIsa / AIPay Inc. as current portfolio company, with AI payments infrastructure / blockchain payment systems / AI commerce platforms positioning.
- Prospeo profile: https://prospeo.io/c/aisa-ai-agent-payment-network
  - Claims founded 2025, 1-10 employees, Jordan Liu as founder and CEO. Treat as weak third-party enrichment source.
- OpenRouter official about: https://openrouter.ai/about
  - Benchmark: 400+ models through one API; mature LLM router competitor.
- Circle Nanopayments: https://www.circle.com/nanopayments
  - External rail: transfers from $0.000001 to $1M using Gateway balance.
- x402 official: https://www.x402.org/
  - External standard: open standard for internet-native payments.
- Coinbase x402 launch: https://www.coinbase.com/developer-platform/discover/launches/x402
  - x402 lets APIs, apps, and AI agents transact through HTTP.

## Working Judgment

AIsa is best read as an early-stage "agent capability marketplace + payment wrapper" rather than a pure OpenRouter clone. The visible, testable part is the API/skills catalog and public GitHub materials. The strategically interesting part is the attempt to package paid data APIs into agent-readable skills and attach nanopayment settlement, but that part still has private-beta and partner-narrative risk.

For Mindspace-like thinking, the useful reference is less "model gateway" and more "capability registry + skill packaging + spend control". If adopting this pattern, avoid bundling too many unrelated surfaces before one narrow workflow has usage. AIsa's site currently suffers from exactly that ambiguity: model gateway, data API marketplace, skills marketplace, payment network, hosted agent Foundry, and hackathon infrastructure all compete for the primary story.
