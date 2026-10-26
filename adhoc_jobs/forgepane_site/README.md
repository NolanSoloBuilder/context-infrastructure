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

历史根域 favicon 使用 `../xuhao_personal_site/public/assets/forgepane-favicon.svg`；该品牌页及根域资产白名单保留为历史实现，根域现由 BeamJoin 交付。

2026-10-26 已回读 Cloudflare：只将既有 `forgepane.com/*` route 从 `forgepane-site` 移交 `beamjoin-web`，其它 zone routes 保持。`www` 继续301到根域并保留路径和参数，个人站继续由原 Worker 提供；BeamJoin 双域官网/工作台、真实登录与共享工程验收已通过，正式回执在 BeamJoin 仓库 `docs/reviews/2026-10-26-dual-domain.md`。
