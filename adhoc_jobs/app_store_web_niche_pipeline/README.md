# App Store → Web Niche Pipeline

把 iOS App Store 榜单转成可复核的 Web 产品候选。榜单负责发现任务，机器规则负责缩小范围，评论、搜索、社区、竞品和原型证据负责最终决策。

## 数据流

```text
Apple charts snapshot
  → immutable raw JSON
  → normalized JSONL
  → Apple metadata enrichment
  → machine screen
  → evidence review
  → prototype / reject
```

`machine_screen_score` 不是市场机会分。它只根据榜单位置、产品描述、付费信号和 Browser 可替代性进行路由。`evidence_score` 在完成评论、SERP、社区和竞品复核前保持 `null`。

技术复核使用 `capability_matrix.json`。统一 fallback 顺序是 Browser API → WASM/Web Worker → WebGPU 可选加速 → 可续接云任务。Chrome built-in AI 只作为可选加速和降本能力，不能成为产品成立的前提。

## 运行

要求 Node.js 18+，无第三方依赖。

```bash
cd /Users/xuhao/Documents/Other/context-infrastructure/adhoc_jobs/app_store_web_niche_pipeline
npm test
npm run run -- --date 2026-07-17 --country us
```

缩小采集范围：

```bash
npm run collect -- --date 2026-07-17 --charts free,paid --categories productivity,utilities,photo_video
npm run enrich -- --date 2026-07-17
npm run analyze -- --date 2026-07-17
npm run report -- --date 2026-07-17 --limit 30
npm run reviews -- --date 2026-07-17 --pages 5
```

主要产物：

- `data/raw/<date>/<country>/`：原始榜单响应的归一化副本和请求元数据。
- `data/normalized/<date>/`：可跨榜单去重的 snapshot JSONL。
- `data/enriched/<date>/`：Apple Lookup 元数据。
- `data/analysis/<date>/`：候选、机器初筛 Markdown/CSV 和汇总。

## 证据复核合同

机器 shortlist 的前 20 项必须逐项补齐：

1. App Store 最近一至三星评论中的重复任务或失败点；
2. Google SERP 中的精确任务查询和现有 Web 竞品；
3. Reddit、YouTube 或专业社区中的主动求助；
4. 竞品收费、IAP 和价格锚点；
5. Browser API 原型的性能、兼容性和 fallback。

完成上述证据后才能填写 `evidence_score`，并将 disposition 改为 `prototype` 或 `reject`。

## 当前边界

Apple legacy RSS 当前实际最多返回 100 条。更深榜单由 AppTweak/Appfigures adapter 补充；数据模型已经保留 `source`、rank、chart、category 和 date，不需要改变后续分析层。

Legacy 分类请求可能在 HTTP 200 时静默退回总榜。采集器会检查 `feed.title`、返回条数与响应 hash；grossing 分类因为标题不自证分类生效，统一标记 `legacy_unverified_category`，在商业数据源交叉确认前只作候选发现，不作精确排名证据。
