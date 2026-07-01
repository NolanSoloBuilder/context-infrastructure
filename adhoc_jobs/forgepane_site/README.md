# ForgePane Site

Minimal Cloudflare Worker site for `forgepane.com`.

## Hostnames

- `forgepane.com`: ForgePane brand entry.
- `www.forgepane.com`: redirects to `forgepane.com`.
- `xuhao.forgepane.com`: Xuhao personal homepage.

`devspace.forgepane.com` is intentionally not handled here. It should be routed through Cloudflare Tunnel and protected by Cloudflare Access before use.

## Commands

```bash
npm install
npm run check
npm run deploy
```

The production deployment in this workspace was performed through the Cloudflare API because local `wrangler` was not authenticated. The `wrangler.jsonc` file remains the source of truth for future CLI deployments.
