# ForgePane Site

Cloudflare Worker for the personal site and `www` redirect.

## Hostnames

- `forgepane.com`：2026-10-26 移交 BeamJoin，根域路由归 `agent-native-aluminum-platform/apps/web/wrangler.jsonc` 管理，本 Worker 不再声明该路由。
- `www.forgepane.com`: redirects to `forgepane.com`.
- `nalon.forgepane.com`: Nalon 的 Vite 个人作品集，由相邻目录 `../xuhao_personal_site/dist` 提供静态资产。

`devspace.forgepane.com` is intentionally not handled here. It should be routed through Cloudflare Tunnel and protected by Cloudflare Access before use.

## Commands

```bash
npm --prefix ../xuhao_personal_site run build
npm install
npm run check
npm run deploy
```

`wrangler.jsonc` 是生产路由的唯一配置源。`run_worker_first` 保证本站绑定域名先经过 Worker：个人域名委托给 `ASSETS` binding，`www` 保留转根域的重定向逻辑。原根域品牌页代码仅留作历史实现，生产根域由 BeamJoin 接管。个人站启用 SPA fallback，使 `/#portfolio` 等前端状态和未来的前端路由可以直接访问。

根域 favicon 使用 `../xuhao_personal_site/public/assets/forgepane-favicon.svg`，并通过 Worker 的显式根域资产白名单提供，避免开放整个个人站资产目录。
