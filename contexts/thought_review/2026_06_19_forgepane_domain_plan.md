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

## 2026-07-15 Nalon Personal Site Upgrade

个人主页的公开品牌统一为 `Nalon`，长期地址改为 `nalon.forgepane.com`；旧的 `xuhao.forgepane.com` Worker 路由退出生产配置。新版内容来自 `adhoc_jobs/xuhao_personal_site/` 中的完整 Vite 作品集。

- 仍由现有 `forgepane-site` Worker 承载，不新增重复的 Pages 项目；`nalon.forgepane.com` 使用 Workers Custom Domain 自动建立域名与证书。
- Worker 使用静态资产 binding 读取 `../xuhao_personal_site/dist`，且通过 `run_worker_first` 先按 hostname 分流。
- `nalon.forgepane.com` 委托给新版静态站；`forgepane.com` 品牌页与 `www.forgepane.com` 重定向继续由原 Worker 逻辑处理。
- 旧的内联个人主页实现已删除，避免同一域名存在两份内容源。
- 站内姓名、Notes 标题、HTML 标题、meta description、头像缩写和版权署名统一为 `Nalon`。
- 发布前必须先构建个人站，再执行 `forgepane_site` 的 Wrangler dry-run 与部署；发布后同时验收个人域名、根域名和 `www` 重定向。

Production verification on 2026-07-15:

- Final Worker deployment `2068b81c-cfbb-4a3d-85ef-eb2581f44cc5` is active at 100%, version `e51d389f-7122-41c6-ad5e-ef066fbc7116`.
- Wrangler triggers contain `forgepane.com/*`, `www.forgepane.com/*`, and the `nalon.forgepane.com` custom domain; the former `xuhao.forgepane.com/*` Worker route is absent.
- Cloudflare public DNS resolvers return the Cloudflare edge addresses for `nalon.forgepane.com`.
- `https://nalon.forgepane.com/` returns `200`, page title `Nalon`, and its hashed JavaScript asset returns `200` as `text/javascript`.
- The deployment ignore manifest excludes the removed Instagram, travel, coffee, unused Xiaohongshu PNG, reference article image, and unused project captures. A direct request to the former coffee image path returns the SPA HTML shell rather than the image asset.
- `https://forgepane.com/` remains `200` with title `ForgePane`; `https://www.forgepane.com/` remains a `301` redirect to the apex domain.

## 2026-07-15 ForgePane Root Directory

`forgepane.com` 从抽象的个人实验室介绍页调整为公开子域名总导览；`nalon.forgepane.com` 的个人站视觉与交互保持不变。

- Personal 区域链接 Nalon 个人页、Notes 和 Portfolio。
- Products 区域只展示已确认公开的 CHINA METRO TYPING 与 Cited Alpha，并复用各自的真实产品截图。
- 根域不展示 DevSpace、API、验证 Worker 或其他私人/基础设施入口。
- 根域仅允许四个显式静态资产路径进入共享 `ASSETS` binding，其他未知路径返回 `404`；个人域继续完整委托给同一个静态资产 binding。
- 视觉目标来自用户选中的 ForgePane 纵向导览图；Codex 内置浏览器初始化报错 `Cannot redefine property: process`，因此浏览器截图对比需在运行时修复后补验，具体记录见 `adhoc_jobs/forgepane_site/design-qa.md`。
- Production deployment `238f8d1a-2354-4132-a2d4-ea3409cb3980` is active at version `adc6a7cf-94c8-43a9-88ca-6c2ca4dd9713`.
- Live HTTP verification: root `200` with title `ForgePane` and the new directory copy; personal domain `200` with title `Nalon`; arrow SVG, Nunito font, and both product screenshots return `200` with correct MIME types; removed Instagram and unknown paths return `404`; `www` remains a `301` redirect to the apex.
- Root favicon added as `/assets/forgepane-favicon.svg`, a three-pane ForgePane mark. Deployment `a56f87f4-2c8a-4597-b36a-ae1dd8477690`, version `d635ac6c-9bae-4a60-8735-8bf4e2b08092`; live HTML contains the SVG favicon link and the asset returns `200 image/svg+xml`.
