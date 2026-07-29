import path from "node:path";
import { ROOT, fetchJson, mapLimit, parseArgs, readJson, writeJson } from "./lib.mjs";

export function normalizeReviews(data, appId, page, sourceUrl) {
  const entries = data?.feed?.entry ?? [];
  return entries
    .filter((entry) => entry?.["im:rating"]?.label)
    .map((entry) => ({
      appId: String(appId),
      page,
      sourceUrl,
      reviewId: entry?.id?.label ?? null,
      author: entry?.author?.name?.label ?? null,
      rating: Number(entry?.["im:rating"]?.label ?? 0),
      version: entry?.["im:version"]?.label ?? null,
      title: entry?.title?.label ?? null,
      content: entry?.content?.label ?? null,
      updatedAt: entry?.updated?.label ?? null,
      voteCount: Number(entry?.["im:voteCount"]?.label ?? 0),
      voteSum: Number(entry?.["im:voteSum"]?.label ?? 0)
    }));
}

const isDirectRun = process.argv[1] && path.resolve(process.argv[1]) === new URL(import.meta.url).pathname;
if (isDirectRun) {
  const args = parseArgs();
  const snapshotDate = args.date ?? new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Shanghai" }).format(new Date());
  const country = args.country ?? "us";
  const pages = Number(args.pages ?? 5);
  const queue = await readJson(path.join(ROOT, args.queue ?? "research_queue.json"));
  const candidates = queue.candidates.filter((item) => !args.priority || item.priority <= Number(args.priority));

  const results = await mapLimit(candidates, Number(args.concurrency ?? 3), async (candidate) => {
    const reviews = [];
    const failures = [];
    for (let page = 1; page <= pages; page += 1) {
      const sourceUrl = `https://itunes.apple.com/${country}/rss/customerreviews/page=${page}/id=${candidate.appId}/sortby=mostrecent/json`;
      try {
        const data = await fetchJson(sourceUrl, { retries: 2 });
        reviews.push(...normalizeReviews(data, candidate.appId, page, sourceUrl));
      } catch (error) {
        failures.push({ page, sourceUrl, error: error.message });
      }
    }
    process.stdout.write(`reviews ${candidate.appId}: ${reviews.length}, failures ${failures.length}\n`);
    return { ...candidate, reviews, failures };
  });

  await writeJson(path.join(ROOT, "data", "evidence", snapshotDate, `${country}-review-evidence.json`), {
    collectedAt: new Date().toISOString(),
    snapshotDate,
    country,
    pagesRequested: pages,
    candidates: results
  });
}

