# Domain Brand Candidates

Date: 2026-06-18

Purpose: record the naming logic and short list for buying a generic first-level domain on Cloudflare Registrar. The intended use is a personal umbrella domain for future Mac tools, AI apps, DevSpace experiments, and personal web pages.

## Naming Logic

The strongest pattern is a neutral maker/dev word plus a UI/workspace noun:

- `forge` / `craft` / `build` / `make`: signals creation, tooling, and product building.
- `pane` / `panel`: signals Mac windows, sidebars, command palettes, and focused utility surfaces.
- The root domain should avoid a personal name, while subdomains can carry identity or product scope, for example `xuhao.example.com`, `mac.example.com`, `ai.example.com`, `devspace.example.com`.

This makes the domain usable both as a brand and as infrastructure. It avoids locking the whole identity to one product category.

## Checked Available Candidates

Cloudflare Registrar `domain-check` showed these as standard `.com` registrations at `10.46 USD/year` at the time of checking. They were not purchased.

- `forgepane.com`: strongest overall. Maker/dev meaning plus UI-pane meaning. Broad enough for Mac tools, AI apps, personal lab, and Cloudflare tunnel hostnames.
- `craftpane.com`: softer and more creator-friendly than `forgepane`; good for apps that feel polished or handmade. Search showed weak social hashtag noise, not an obvious strong software brand.
- `buildpane.com`: direct for developer tooling, build monitors, automation, and command surfaces. More utilitarian and less elegant.
- `makepane.com`: simple and action-oriented, but slightly awkward in English and has technical/code occurrences around `MakePane`.
- `formpane.com`: polished for form/data/app-builder tools. Narrower if the future products are not form-related.
- `shapepane.com`: good for visual/design/spatial tools. Less suitable as a broad umbrella brand.
- `commandpane.com`: strong for Mac command palette, launcher, automation, or AI control surface. More descriptive and longer; web search shows generic UI/code uses of "command pane".
- `ideapane.com`: good for thinking, notes, writing, and AI ideation. Search showed existing "Idea Pane" bakery/social traces, so less clean as a brand.
- `brainpane.com`: fits AI/memory/knowledge products but sounds more gimmicky and less premium.
- `pilotpane.com`: good for assistant/control/agent products, but "pilot" is heavily used in AI naming.

## Lower Priority

- `copilotpane.com`: avoid because of Microsoft Copilot association.
- `toolbario.com`, `workbario.com`, `flowbario.com`, `commandbario.com`: available, but `bario` reads less naturally than `pane`.

## Current Recommendation

If buying one broad, non-personal domain now, prefer:

1. `forgepane.com`
2. `craftpane.com`
3. `commandpane.com`
4. `buildpane.com`

`forgepane.com` remains the best balance between memorability, breadth, and product fit.

## `.ai` Consideration

`.ai` is much more expensive than `.com` and is usually better reserved for a product that is explicitly AI-first. Cloudflare publicly supports `.ai`, but the Registrar API currently returned `extension_not_supported_via_api` for `.ai` availability checks in this account workflow, so final availability and checkout should be verified in the Cloudflare Dashboard.

As a pricing heuristic on 2026-06-19, public trackers and Cloudflare positioning indicate `.ai` is roughly around `80 USD/year`, and the Registrar API schema notes `.ai` commonly requires a minimum 2-year registration. That means first checkout is likely around `160 USD` before any taxes, versus `10.46 USD/year` for a standard `.com` checked through Cloudflare Registrar.

Recommendation: buy a broad `.com` as the root identity first, then use subdomains such as `ai.forgepane.com` or `agent.forgepane.com`. Buy a `.ai` only when a specific AI product name is clear enough to justify the higher renewal burden.

Additional checked `.com` candidates outside the `pane` pattern:

- `forgemote.com`: available, `10.46 USD/year`; tool/remote-control feeling, less elegant than `forgepane.com`.
- `craftmote.com`: available, `10.46 USD/year`; softer than `forgemote.com`, but `mote` is less self-explanatory.
- `forgeboxy.com`: available, `10.46 USD/year`; playful, weaker as a premium umbrella brand.
- `forgepadx.com`: available, `10.46 USD/year`; feels more like a workaround than a natural name.
- `moteforge.com`: available in a first check; awkward word order.

## Registration Result

`forgepane.com` was registered through Cloudflare Registrar on 2026-06-19. API verification after purchase showed the registration as active, expiring on 2027-06-19, with WHOIS redaction enabled, domain lock enabled, and auto-renew disabled.
