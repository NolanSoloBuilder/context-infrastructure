# 中国地铁打字：分享、统计、排行榜与大陆用户登录架构

日期：2026-07-22

关联项目：`adhoc_jobs/tw_metro_typing_china`

状态：架构校准，尚未创建或发布线上资源

## 结论

登录不是游戏入口，而是“保留身份”的升级动作。

默认给每位玩家签发游客身份，允许直接完成每日挑战、保存本机成绩并进入匿名日榜。只有在玩家需要跨设备同步、固定昵称、找回历史或认领榜单成绩时，才邀请登录。大陆用户第一登录方式推荐微信，手机号只作为后续恢复方式，不作为首屏门槛。

## 登录选择

### 推荐：游客身份 + 微信双入口

- 普通浏览器桌面端：微信开放平台网站应用扫码登录。
- 微信内置浏览器：认证公众号网页授权。
- 两个微信应用在同一开放平台主体下时，优先使用 UnionID 合并身份；无法取得统一标识时，用一次性绑定码由用户主动合并。
- 不主动读取微信昵称和头像。排行榜昵称由玩家自行设置，头像使用系统生成图形，降低个人信息处理范围。

该方案的前提是具备可用的微信开放平台主体、网站应用或认证公众号，以及审核通过的回调域名。没有这些资质时，先发布游客榜，登录入口保持 feature flag 关闭。

### 暂不首选手机号验证码

手机号虽然覆盖广，但会立即引入短信服务商、签名与模板审核、验证码滥用、费用、手机号这一直接身份标识、注销与换号恢复等问题。一个免费地铁打字游戏没有必要用手机号换取首次可玩性。

如果后续数据证明用户确有跨设备找回需求，可把手机号验证码作为账号恢复与绑定方式，而不是唯一登录方式。

### 暂不把 Passkey 作为大陆唯一入口

Passkey 可以作为已登录用户的快捷回访方式，但不同系统、浏览器和微信内置浏览器的可用性与迁移体验需要实机验证，不适合成为首版唯一身份入口。

## 身份模型

```text
Player
├── guest session（首次访问自动创建）
├── auth identities[]
│   ├── wechat_open
│   ├── wechat_official_account
│   └── phone_recovery（后续可选）
├── public profile（玩家自定昵称、系统头像）
└── progress / scores / streaks
```

关键约束：

- `player_id` 是内部随机 ID，不使用手机号、OpenID 或 UnionID 作为主键。
- OAuth 标识加密或 HMAC 后存储，只用于匹配身份。
- 登录后在服务端事务中把游客成绩合并到正式 Player；同一挑战只保留更好成绩。
- Session 使用 `Secure + HttpOnly + SameSite=Lax` Cookie；OAuth 使用短时 state、PKCE（提供方支持时）和一次性回调记录。
- 提供退出登录、导出/查看数据、删除账号和撤回授权入口。

## Cloudflare 数据职责

### Worker API

统一承载：

- `/api/session/guest`
- `/api/auth/wechat/start`
- `/api/auth/wechat/callback`
- `/api/challenges/:date/run-ticket`
- `/api/runs/submit`
- `/api/leaderboards/daily/:date`
- `/api/profile`
- `/api/account/delete`
- `/api/events`

静态资源仍由当前 Workers Static Assets 提供。API 和静态站同域，减少跨域、Cookie 和 OAuth 回调复杂度。

### D1：业务真源

首版表：

- `players`
- `auth_identities`
- `sessions`
- `daily_challenges`
- `run_tickets`
- `score_submissions`
- `daily_best_scores`
- `player_streaks`
- `account_deletion_jobs`

D1 只保存需要事务、一致性与查询的业务数据，不承担原始埋点日志。

### Analytics Engine：聚合产品事件

浏览器把白名单事件发给同域 `/api/events`，Worker 删除未知字段后写入 Analytics Engine。事件不包含输入内容、微信标识、手机号、昵称、完整 IP 或精确设备指纹。分析维度只保留挑战、城市、线路、输入语言、设备类别和来源类别。

### 分享图片

第一版在浏览器用 Canvas 生成 `1080 × 1440` PNG，用户主动保存或通过 Web Share 分享，图片不上传服务器。

链接预览使用按挑战生成的公共 OG 图，只展示日期、城市、线路，不展示玩家成绩。只有验证“公开成绩页”确有需求后，才增加短期 R2 对象和可撤销分享 token。

## 排行榜可信度

完全由浏览器上报分数不可信。首版使用轻量服务端校验：

1. 开局前申请一次性 `run_ticket`，绑定挑战版本、语言、开始时间和随机 nonce。
2. 完成后提交成绩、结束时间和顺序输入摘要。
3. 服务端检查 ticket 未使用、时间窗口、站点顺序、字符数、速度上限和挑战版本。
4. 同一 Player、日期、语言只展示最佳合法成绩。
5. 异常提交进入拒绝或待审状态，不污染公开榜。
6. 对开局和提交接口限速；只有触发异常策略时再要求 Turnstile，正常玩家不先过验证码。

榜单排序固定为：完成站数降序、正确字符数降序、正确率降序、提交时间升序。公开页只展示排名、玩家自定昵称、系统头像和成绩，不展示登录方式。

## 隐私与大陆访问边界

- 游戏基础功能不因用户拒绝登录或非必要分析而不可用。
- 登录前清楚说明处理目的、信息类型、保存期限、删除方式和第三方身份提供方。
- 不默认勾选同意，不采集与榜单/同步无关的数据。
- 微信 OpenID、UnionID、用户 ID、浏览记录等仍属于可关联到个人的网络身份或使用记录，不能因为使用随机 ID 就称为匿名数据。
- 当前 Cloudflare 全球网络不等于中国大陆境内部署。若目标变为稳定服务大陆用户，需要单独评估 ICP、境内部署/加速、跨境数据和微信回调可达性；不要把 Cloudflare China Network 当成免费开关。

## 实施顺序

1. 建立 Worker API、D1 migrations、游客 session 和本地 Miniflare 测试。
2. 接入 run ticket、成绩提交、每日榜和游客成绩合并。
3. 把现有 sessionStorage 事件改为同域事件 API，并保留拒绝未知字段的测试。
4. 实现 Canvas 动态成绩图与分享预览。
5. 增加 provider-neutral auth adapter 和关闭状态的微信 feature flag。
6. 取得微信资质、AppID/Secret 和回调域确认后，再启用微信登录并做真机验证。
7. 继续保持本地预览；用户明确批准前不创建生产 D1/R2/Analytics Engine 资源，不部署。

## 开工前唯一需要确认的外部条件

是否已有可用的微信开放平台主体，以及以下至少一项：

- 审核通过的网站应用；
- 认证公众号及可配置的网页授权域名。

如果都没有，工程实现仍从游客榜和 provider-neutral 身份层开始，微信登录保持关闭，不阻塞其余三项。

## 2026-07-22 本地实现记录

已按“没有微信开放平台主体”的约束完成本地第一阶段，未发布、未创建线上资源：

- Worker 同域 API 与本地 D1 migration 已落地，覆盖游客 session、昵称、一次性 run ticket、成绩提交和每日榜。
- 服务端重新计算速度与正确率，校验挑战版本、票据唯一性和实际运行时长；每日同题榜按固定规则只保留玩家最佳成绩。
- 产品事件经 `/api/events` 白名单清洗后写入 Analytics Engine binding；本地仍保留 sessionStorage 兜底。
- 每日结果页生成 `1080 × 1440` Canvas PNG。桌面端使用原生下载链接，移动端在浏览器支持时使用 Web Share，图片不上传服务器。
- 分享图增加真实地图区：后台用 MapLibre 渲染与游戏一致的 OpenFreeMap/OSM 道路、水系和地名底图，再叠加当天线路与站点；二维码指向对应日期的公开每日挑战路径，并明确“同一天、同一线路、同一方向”。本地预览不编码本机地址，导出图保留地图数据署名。
- `/api/auth/providers` 明确返回微信 `disabled / not_configured`；UI 不展示伪登录入口，只说明尚未配置。
- 本地 D1 E2E 已走通“创建游客 → 发 run ticket → 等待合法时长 → 提交成绩 → 查询榜单 → 修改昵称”，页面实测已确认排行榜与昵称更新。
- 自动化测试 60 项通过，生产构建通过。唯一构建提示是地图引擎异步 chunk 仍超过 Vite 默认提示阈值，不阻塞本阶段。

## 2026-07-22 生产发布记录

用户明确批准发布后，第一阶段已部署至 <https://metro.forgepane.com>：

- 创建生产 D1 `china-metro-typing-prod`，数据库 ID 为 `0f810cf3-2bc8-4148-8b11-3b687c53cb7a`，数据位置为 APAC；远程 migration `0001_growth_backend.sql` 已成功执行。
- 启用 Analytics Engine，数据集绑定为 `china_metro_typing_events`；线上 `/api/events` 实测返回 `sink: analytics_engine`。
- Worker Static Assets、Worker API、D1 和 Analytics Engine 已作为同一个版本发布，版本 ID 为 `31484df8-3bde-46de-8cb2-fff9bb602528`。
- 线上实测通过游客 session、每日榜查询、事件写入和 `/daily` 页面加载；首次 smoke session 只创建匿名玩家与 session，没有写入榜单成绩或 run ticket。
- 微信 provider 继续返回 `disabled / not_configured`，不展示不可用的登录入口；取得合法主体和审核通过的应用能力前不启用。

本次上线未包含：接口限流、删除账号闭环、正式隐私文本和中国大陆多网络/多运营商实测。这些属于下一阶段上线门槛，而不是当前游客挑战、分享与每日榜链路的隐藏完成项。
