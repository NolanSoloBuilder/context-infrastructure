import path from "node:path";
import { createHash } from "node:crypto";
import {
  ROOT,
  fetchJson,
  mapLimit,
  normalizeFeed,
  parseArgs,
  readJson,
  writeJson,
  writeJsonl
} from "./lib.mjs";

const args = parseArgs();
const config = await readJson(path.join(ROOT, "config.json"));
const snapshotDate = args.date ?? new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Shanghai" }).format(new Date());
const country = args.country ?? config.country;
const limit = Number(args.limit ?? config.limit);
const selectedCharts = args.charts ? new Set(String(args.charts).split(",")) : null;
const selectedCategories = args.categories ? new Set(String(args.categories).split(",")) : null;
const charts = config.charts.filter((item) => !selectedCharts || selectedCharts.has(item.id));
const categories = config.categories.filter((item) => !selectedCategories || selectedCategories.has(item.id));
const requests = charts.flatMap((chart) => categories.map((category) => ({ chart, category })));
const collectedAt = new Date().toISOString();
const outputDir = path.join(ROOT, "data", "raw", snapshotDate, country);

function assessIntegrity(data, category, chart, returnedCount) {
  const feedTitle = data?.feed?.title?.label ?? "";
  const sourceUpdatedAt = data?.feed?.updated?.label ?? null;
  const issues = [];
  let status = "verified";

  if (!feedTitle) issues.push("missing_feed_title");
  if (returnedCount < Math.min(50, limit)) issues.push("unexpectedly_low_count");
  if (category.genreId && chart.id !== "grossing" && !feedTitle.toLowerCase().includes(category.name.toLowerCase())) {
    issues.push("category_title_mismatch");
  }
  if (category.genreId && chart.id === "grossing") {
    status = "legacy_unverified_category";
    issues.push("grossing_title_does_not_self_verify_category");
  }
  if (issues.some((issue) => issue !== "grossing_title_does_not_self_verify_category")) status = "degraded";
  return { status, issues, feedTitle, sourceUpdatedAt };
}

const results = await mapLimit(requests, Number(args.concurrency ?? config.concurrency), async ({ chart, category }) => {
  const genreSegment = category.genreId ? `/genre=${category.genreId}` : "";
  const sourceUrl = `https://itunes.apple.com/${country}/rss/${chart.feed}/limit=${limit}${genreSegment}/json`;
  try {
    const data = await fetchJson(sourceUrl);
    const rows = normalizeFeed(data, { collectedAt, snapshotDate, sourceUrl, country, chart: chart.id, category });
    const integrity = assessIntegrity(data, category, chart, rows.length);
    const rawResponseHash = createHash("sha256").update(JSON.stringify(data)).digest("hex");
    await writeJson(path.join(outputDir, `${chart.id}-${category.id}.json`), {
      metadata: {
        provider: "apple_legacy_rss",
        collectedAt,
        snapshotDate,
        sourceUrl,
        sourceUpdatedAt: integrity.sourceUpdatedAt,
        rawResponseHash,
        country,
        device: "iphone",
        chart: chart.id,
        category,
        requestedLimit: limit,
        returnedCount: rows.length,
        integrityStatus: integrity.status,
        integrityIssues: integrity.issues,
        feedTitle: integrity.feedTitle
      },
      payload: data
    });
    process.stdout.write(`ok ${chart.id}/${category.id}: ${rows.length} (${integrity.status})\n`);
    return { ok: true, chart: chart.id, category: category.id, sourceUrl, integrity, rawResponseHash, rows };
  } catch (error) {
    process.stderr.write(`failed ${chart.id}/${category.id}: ${error.message}\n`);
    return { ok: false, chart: chart.id, category: category.id, sourceUrl, error: error.message, rows: [] };
  }
});

const rows = results.flatMap((result) => result.rows);
await writeJsonl(path.join(ROOT, "data", "normalized", snapshotDate, `${country}-snapshots.jsonl`), rows);
await writeJson(path.join(ROOT, "data", "normalized", snapshotDate, `${country}-manifest.json`), {
  collectedAt,
  snapshotDate,
  country,
  requestedLimit: limit,
  requestCount: results.length,
  successCount: results.filter((item) => item.ok).length,
  failureCount: results.filter((item) => !item.ok).length,
  rowCount: rows.length,
  results: results.map(({ rows: resultRows, ...result }) => ({ ...result, count: resultRows.length }))
});

if (!rows.length) process.exitCode = 1;
