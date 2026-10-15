# H5 判断小红书 App 容器

在浏览器端使用 `@xhs/ozone-detector` 的 `commonChecks.isXHS`：

```ts
import { commonChecks } from '@xhs/ozone-detector'

const isInXhsApp = commonChecks.isXHS
```

依据：Aurora 的 `packages/growth/growthrights-moon/src/composables/use-navbar.ts` 已这样使用。Aurora 当前锁定的 `@xhs/ozone-detector@3.16.2-1` README 将 `isXHS` 定义为“小红书 App”。该版本实现综合检查 Android/iOS/Harmony Bridge、UA 的 `discover` 标记及 `clientsource=app` 查询参数，并排除 UA 标记为 `merchant` 的商家版 App。查询参数是开发/测试兼容路径，不适合作为身份或安全校验。

`commonChecks` 在模块加载时计算；若需在运行时重新读取，使用同包的 `getCommonChecks(...)` 并确认构建环境对 `process.env.BROWSER` 的配置。SSR 场景用 `getCommonChecksInNode({ userAgent, url })`。

不要仅匹配 UA 中的 `XHS`：该包的 changelog 记录 Android 5.42 起 UA 已移除 `XHS` 标记。
