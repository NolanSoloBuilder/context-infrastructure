# Search Manifest

## 产出文件索引

| 文件 | 路径 | 说明 |
|---|---|---|
| Scratchpad | `tmp/socialhuman_market_survey_20260812/scratchpad.md` | 主线程 claim 与判断记录 |
| Search Manifest | `tmp/socialhuman_market_survey_20260812/search_manifest.md` | 调研来源和 agent 索引 |
| 最终报告 | `contexts/survey_sessions/socialhuman_product_market_survey_20260812.md` | 最终中文调研报告 |

## 初始来源

- https://socialhuman.dev/
- https://socialhuman.dev/privacy
- https://socialhuman.dev/terms
- https://apps.apple.com/us/app/socialhuman/id6761835659
- https://play.google.com/store/apps/details?id=com.socialhuman.app
- https://www.reddit.com/r/SideProject/comments/1sqhs5o/i_spent_six_months_building_a_social_network_that/

## Subagent 原始产出

| Agent | Task | URLs | 状态 |
|---|---|---:|---|
| `/root/socialhuman_tech` | 产品机制与安全边界 | 20+ | completed |
| `/root/socialhuman_adoption` | 用户采用、公司与市场信号 | 15+ | completed |
| `/root/socialhuman_market` | 竞品、需求与商业空间 | 30+ | completed |

## 覆盖评估

- 官方产品与政策：完整覆盖官网、验证说明、Privacy、Terms、双端商店。
- 公司：通过芬兰 PRH/YTJ 官方 API 验证。
- 采用：商店公开数据 + 创始人自报；缺少独立 analytics、长期留存和后台截图。
- 技术：覆盖 Apple/Google attestation、C2PA 官方边界与独立 recapture / keystroke 攻击研究；缺少 SocialHuman 自身审计。
- 市场：覆盖真实性态度调查、BeReal/Cara 行为证据及多款 2026 早期竞品。
