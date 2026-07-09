# ForgePane Domain Plan

Date: 2026-06-19

## Current State

- `forgepane.com` is registered through Cloudflare Registrar.
- The Cloudflare zone for `forgepane.com` is active.
- Nameservers are `aisha.ns.cloudflare.com` and `lakas.ns.cloudflare.com`.
- Registrar settings verified after purchase: WHOIS redaction enabled, domain lock enabled, auto-renew disabled.
- A named Cloudflare Tunnel already exists: `devspace-context-infra`, tunnel id `6d0d1a3c-b44c-41f7-bffa-27f8fc940495`.
- The tunnel is currently inactive and not yet bound to a `forgepane.com` hostname.

## Plan

### Phase 1: Reserve Hostname Layout

Use `forgepane.com` as the neutral umbrella domain and express use cases through subdomains:

- `www.forgepane.com`: public personal/home page.
- `labs.forgepane.com`: experiments and demos.
- `devspace.forgepane.com`: DevSpace MCP endpoint, only if secured.
- `api.forgepane.com`: future API endpoints.
- `ai.forgepane.com`: future AI product landing or app.
- `mac.forgepane.com`: future Mac tools landing or distribution.

### Phase 2: Bring Up a Safe Public Surface First

Start with a simple public site instead of exposing DevSpace immediately:

- Create a minimal Cloudflare Pages or Worker site for `www.forgepane.com`.
- Add a short brand/home page and a placeholder for future tools.
- Verify DNS, HTTPS, and redirects from apex to `www`.

### Phase 3: Reconnect DevSpace Behind a Named Hostname

Use the existing named tunnel for local DevSpace only after adding security controls:

- Bind `devspace.forgepane.com` to tunnel `devspace-context-infra`.
- Route tunnel traffic to local DevSpace.
- Update DevSpace `publicBaseUrl` from temporary `trycloudflare.com` to `https://devspace.forgepane.com`.
- Smoke test `/healthz`, OAuth discovery, MCP initialize, and one safe read-only workspace tool.

### Phase 4: Add Access Control Before Real Use

Do not leave DevSpace publicly reachable with only its current OAuth prototype:

- Put `devspace.forgepane.com` behind Cloudflare Access.
- Restrict access to the owner's email.
- Keep DevSpace allowlisted to specific local roots only.
- Avoid exposing shell-enabled workflows until DevSpace has better persistence and sandboxing.

### Phase 5: Operational Baseline

After the site and secure tunnel work:

- Document DNS records and tunnel config.
- Add a local start/stop runbook for DevSpace + cloudflared.
- Confirm no long-running public tunnel is left active accidentally.
- Re-check WHOIS/RDAP redaction in Dashboard.

## Recommendation

Build the public homepage first, then add the private DevSpace hostname behind Cloudflare Access. This makes `forgepane.com` useful immediately while keeping the local-machine gateway from becoming an accidental public attack surface.

## 2026-06-19 Implementation Result

The first public phase was implemented as a Cloudflare Worker project at `adhoc_jobs/forgepane_site/`.

- Worker name: `forgepane-site`.
- Routes:
  - `forgepane.com/*`
  - `www.forgepane.com/*`
  - `xuhao.forgepane.com/*`
- DNS records:
  - `A forgepane.com -> 192.0.2.1`, proxied.
  - `A www.forgepane.com -> 192.0.2.1`, proxied.
  - `A xuhao.forgepane.com -> 192.0.2.1`, proxied.
- Behavior:
  - `forgepane.com` serves the ForgePane brand page.
  - `www.forgepane.com` redirects to `forgepane.com`.
  - `xuhao.forgepane.com` serves the personal homepage.
  - `devspace.forgepane.com` remains unconfigured; DevSpace is still reserved for a later Access-protected tunnel phase.
- Verification:
  - `wrangler deploy --dry-run` succeeded locally.
  - `https://forgepane.com` returned `200` with the ForgePane page.
  - `https://www.forgepane.com` returned `301` to `https://forgepane.com/` when resolved through Cloudflare.
  - `https://xuhao.forgepane.com` returned `200` with the Xuhao page when resolved through Cloudflare.
  - Registrar status was rechecked after deployment: active, WHOIS redaction enabled, domain lock enabled, auto-renew disabled.

## 2026-06-19 DevSpace Long-Term Hostname

`devspace.forgepane.com` was moved from the temporary `trycloudflare.com` quick tunnel to the named Cloudflare Tunnel and protected by Cloudflare Access.

- Access organization: `ForgePane`.
- Access login domain: `forgepane.cloudflareaccess.com`.
- Access application: `DevSpace`.
- Protected hostname: `devspace.forgepane.com`.
- Access policy: allow `Webxuhao00@gmail.com` only.
- DNS record: `CNAME devspace.forgepane.com -> 6d0d1a3c-b44c-41f7-bffa-27f8fc940495.cfargotunnel.com`, proxied.
- Tunnel: `devspace-context-infra`, id `6d0d1a3c-b44c-41f7-bffa-27f8fc940495`.
- Tunnel config source: Cloudflare remote config, with ingress to `http://127.0.0.1:7676` and Access JWT validation enabled.
- Local DevSpace config: `/Users/xuhao/.devspace/config.json`, `publicBaseUrl` set to `https://devspace.forgepane.com`.
- Local cloudflared config: `/Users/xuhao/.cloudflared/config.yml`.

Runtime is managed by user-level LaunchAgents:

- `/Users/xuhao/Library/LaunchAgents/com.forgepane.devspace.plist`
- `/Users/xuhao/Library/LaunchAgents/com.forgepane.devspace-tunnel.plist`

Useful commands:

```bash
launchctl print gui/501/com.forgepane.devspace
launchctl print gui/501/com.forgepane.devspace-tunnel
launchctl kickstart -k gui/501/com.forgepane.devspace
launchctl kickstart -k gui/501/com.forgepane.devspace-tunnel
curl http://127.0.0.1:7676/healthz
cloudflared tunnel info devspace-context-infra
```

Verification:

- `devspace doctor` reports `Public MCP URL: https://devspace.forgepane.com/mcp`.
- Local `http://127.0.0.1:7676/healthz` returns `{"ok":true,"name":"devspace"}`.
- Unauthenticated `https://devspace.forgepane.com/mcp` returns `302` to `forgepane.cloudflareaccess.com`, confirming the MCP endpoint is not publicly exposed.
- Tunnel has active Cloudflare connector connections.

## 2026-06-19 ChatGPT MCP App Result

Two ChatGPT / Apps SDK surfaces were configured on the long-term ForgePane hostnames.

### Full DevSpace

- ChatGPT custom app name: `DevSpace`.
- MCP URL: `https://devspace.forgepane.com/mcp`.
- Security stance: shell-capable and therefore must remain authenticated and protected.
- Tools discovered by ChatGPT settings and Codex Apps: `open_workspace`, `read`, `write`, `edit`, `bash`.
- Verification result: Codex Apps successfully called `open_workspace` for `/Users/xuhao/Documents/Other/context-infrastructure` and received workspace id `ws_0f043092-a40e-43f0-9781-258718c069e9`.

### Read-Only Adapter and Smoke Endpoint

- Adapter path: `adhoc_jobs/devspace_chatgpt_adapter/`.
- Local service: `http://127.0.0.1:7677/mcp`.
- Public read-only MCP: `https://devspace-read.forgepane.com/mcp`.
- Public no-auth smoke MCP: `https://devspace-read.forgepane.com/smoke-mcp`.
- LaunchAgent: `/Users/xuhao/Library/LaunchAgents/com.forgepane.devspace-read.plist`.
- Read-only tools: `search`, `fetch`.
- Smoke tool: `status`.
- Verification result: Codex Apps successfully called `ForgePane MCP Smoke.status` and received:

```json
{
  "ok": true,
  "service": "forgepane-mcp-smoke",
  "domain": "forgepane.com"
}
```

### ChatGPT Web UI Note

The ChatGPT web app settings page can create, connect, and inspect the custom apps, including tool metadata and auth scheme. Early attempts in the composer showed `点击以重试` and produced a model response saying the connector/API tool was unavailable. A later retry succeeded from ChatGPT Web:

- ChatGPT conversation title: `MCP Smoke Status`.
- Selected app: `ForgePane MCP Smoke`.
- Tool call UI: `Status checked`.
- Returned JSON:

```json
{"ok":true,"service":"forgepane-mcp-smoke","domain":"forgepane.com"}
```

Adapter logs confirmed the web composer reached the server:

```text
2026-06-19T08:48:10.514Z POST /smoke-mcp 57.151.131.239
2026-06-19T08:48:11.352Z POST /smoke-mcp 57.151.131.230
```

Current interpretation: the ForgePane MCP servers, Apps SDK metadata, Codex Apps tool layer, and ChatGPT Web composer can all invoke the public no-auth smoke endpoint. The app chip may still display `点击以重试` after invocation, so the authoritative signal is the visible tool call row plus server-side `/smoke-mcp` request logs.

## 2026-07-06 Cited Alpha Hostname

`cited-alpha.forgepane.com` is bound to Cloudflare Pages project `cited-alpha-web`.

- Project domains: `cited-alpha-web.pages.dev`, `cited-alpha.forgepane.com`.
- Deployment used existing local `dist/` from `/Users/xuhao/Documents/Other/mindspace_web_frontend`.
- Latest deployment URL: `https://48bc55dd.cited-alpha-web.pages.dev`.
- Public contact email changed to `CitedAlpha@163.com`.
- Verification:
  - `https://cited-alpha.forgepane.com/` returned `200`.
  - `https://cited-alpha-web.pages.dev/` returned `200`.
  - `https://cited-alpha.forgepane.com/.well-known/security.txt` returned `Contact: mailto:CitedAlpha@163.com`.
