# AIsa Survey Search Manifest

Date: 2026-06-17

## Output Index

| File | Path | Purpose |
|---|---|---|
| Scratchpad | `tmp/2026_06_17_aisa_survey/scratchpad.md` | Claim extraction, source notes, intermediate judgment |
| Search Manifest | `tmp/2026_06_17_aisa_survey/search_manifest.md` | This file |
| Final report | `contexts/survey_sessions/aisa_survey_20260617.md` | Internal survey memo |

## Search Coverage

Searches and direct fetches covered:

- Official website and docs: `https://aisa.one/`, `/docs/guides`, `/api`, `/skills`, `/models`, `/api/tavily-search`, `/docs/guides/security`, `/docs/guides/pricing`, `/docs/llms.txt`, `/sitemap.xml`.
- GitHub: `AIsa-team` org, `aisa-one` user, repo metadata through GitHub REST API.
- Company/funding evidence: LinkedIn company profile, Draper portfolio page, Prospeo enrichment profile.
- Market context: OpenRouter official pages, Circle Nanopayments, x402, Coinbase x402 launch.
- Social launch context: AIsa X snippets and AIsa blog about Circle Arc hackathon.

## Evidence Limits

- No AIsa API key was used, so endpoint execution, billing logs, wallet behavior, and actual upstream API quality were not tested.
- X/Twitter pages were only available through search snippets, not authenticated timeline inspection.
- LinkedIn and enrichment pages are partially indexed. Treat employee/funding details as indicative unless confirmed by primary investor/company filings.
- The model catalog route rendered as a loading state with `0` visible models in the static scrape, while docs and homepage claim broad model coverage. This is recorded as an evidence conflict rather than a product failure.
- `/.well-known/agent.json` returned 404 during this run, so agent discovery claims remain weak.

## Main URLs

- https://aisa.one/
- https://aisa.one/docs/guides
- https://aisa.one/api
- https://aisa.one/skills
- https://aisa.one/models
- https://aisa.one/api/tavily-search
- https://aisa.one/docs/guides/security
- https://aisa.one/docs/guides/pricing
- https://aisa.one/sitemap.xml
- https://aisa.one/blog/aisa-data-layer-agentic-economy-arc
- https://github.com/AIsa-team
- https://github.com/aisa-one
- https://api.github.com/orgs/AIsa-team/repos?per_page=100
- https://api.github.com/users/aisa-one/repos?per_page=100
- https://www.linkedin.com/company/aisaonehq
- https://www.draper.vc/portfolio/alsa
- https://prospeo.io/c/aisa-ai-agent-payment-network
- https://openrouter.ai/about
- https://openrouter.ai/docs/quickstart
- https://www.circle.com/nanopayments
- https://www.x402.org/
- https://www.coinbase.com/developer-platform/discover/launches/x402

## Subagent Usage

No subagent was launched. The scope was a single product/company survey with a small enough source set for main-thread verification. I still used the deep research workflow shape: claim extraction, independent-source checking, evidence conflict recording, and final memo.
