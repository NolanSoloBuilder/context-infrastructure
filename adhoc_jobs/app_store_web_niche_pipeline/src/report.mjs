import fs from "node:fs/promises";
import path from "node:path";
import { ROOT, csvCell, parseArgs, readJsonl } from "./lib.mjs";

const args = parseArgs();
const snapshotDate = args.date ?? new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Shanghai" }).format(new Date());
const country = args.country ?? "us";
const limit = Number(args.limit ?? 50);
const outputDir = path.join(ROOT, "data", "analysis", snapshotDate);
const candidates = await readJsonl(path.join(outputDir, `${country}-candidates.jsonl`));
const shortlist = candidates
  .filter((item) => item.screen.disposition === "shortlist_for_evidence_review")
  .slice(0, limit);

const lines = [
  `# App Store → Web niche 机器初筛（${snapshotDate}）`,
  "",
  `市场：${country.toUpperCase()}；候选 App：${candidates.length}；进入证据复核：${shortlist.length}。`,
  "",
  "> `machine_screen_score` 只负责排序，尚未验证搜索需求、评论痛点、竞品价格或付费转化。`evidence_score` 在人工研究完成前保持为空。",
  "",
  "| # | App | 榜单位置 | 类别 | 机器分 | Web 信号 | 价格信号 |",
  "|---:|---|---|---|---:|---|---|"
];

shortlist.forEach((item, index) => {
  const positions = item.appearances
    .sort((a, b) => a.rank - b.rank)
    .slice(0, 3)
    .map((entry) => `${entry.chart}/${entry.categoryName} #${entry.rank}`)
    .join("；");
  const signals = item.screen.webSignals.map((signal) => signal.group).join(", ");
  const price = item.priceLabel || (item.lookup.inAppPurchases.length ? "IAP" : "Free/unknown");
  lines.push(
    `| ${index + 1} | [${item.name}](${item.lookup.trackViewUrl ?? item.appStoreUrl}) | ${positions} | ${item.category ?? ""} | ${item.screen.machineScreenScore} | ${signals} | ${price} |`
  );
});

lines.push("", "## 下一步", "", "对前 20 名逐项补 App 评论、SERP、Reddit/论坛、竞品价格与 Browser API 原型证据，然后填写 `evidence_score` 和最终 disposition。", "");
await fs.mkdir(outputDir, { recursive: true });
await fs.writeFile(path.join(outputDir, `${country}-machine-shortlist.md`), lines.join("\n"));

const csvHeaders = ["app_id", "name", "category", "best_rank", "machine_screen_score", "disposition", "web_signals", "app_store_url"];
const csvRows = shortlist.map((item) => [
  item.appId,
  item.name,
  item.category,
  item.screen.bestRank,
  item.screen.machineScreenScore,
  item.screen.disposition,
  item.screen.webSignals.map((signal) => signal.group).join("|"),
  item.lookup.trackViewUrl ?? item.appStoreUrl
]);
await fs.writeFile(
  path.join(outputDir, `${country}-machine-shortlist.csv`),
  `${[csvHeaders, ...csvRows].map((row) => row.map(csvCell).join(",")).join("\n")}\n`
);

