import fs from "node:fs/promises";
import path from "node:path";
import { ROOT, groupSnapshots, machineScreen, parseArgs, readJsonl, writeJson, writeJsonl } from "./lib.mjs";

const args = parseArgs();
const snapshotDate = args.date ?? new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Shanghai" }).format(new Date());
const country = args.country ?? "us";
const snapshots = await readJsonl(path.join(ROOT, "data", "normalized", snapshotDate, `${country}-snapshots.jsonl`));
const lookupFile = path.join(ROOT, "data", "enriched", snapshotDate, `${country}-lookup.jsonl`);
let lookups = [];
try {
  lookups = await readJsonl(lookupFile);
} catch (error) {
  if (error.code !== "ENOENT") throw error;
}
const lookupById = new Map(lookups.map((item) => [String(item.trackId), item]));
const candidates = groupSnapshots(snapshots)
  .map((app) => machineScreen(app, lookupById.get(String(app.appId))))
  .sort((a, b) => b.screen.machineScreenScore - a.screen.machineScreenScore || a.screen.bestRank - b.screen.bestRank);

const outputDir = path.join(ROOT, "data", "analysis", snapshotDate);
await writeJsonl(path.join(outputDir, `${country}-candidates.jsonl`), candidates);
await writeJson(path.join(outputDir, `${country}-summary.json`), {
  generatedAt: new Date().toISOString(),
  snapshotDate,
  country,
  candidateCount: candidates.length,
  dispositionCounts: Object.fromEntries(
    [...new Set(candidates.map((item) => item.screen.disposition))].map((key) => [
      key,
      candidates.filter((item) => item.screen.disposition === key).length
    ])
  ),
  note: "machineScreenScore is a routing signal. evidenceScore remains null until reviews, SERP, community demand and competitor pricing are verified."
});

await fs.mkdir(outputDir, { recursive: true });

