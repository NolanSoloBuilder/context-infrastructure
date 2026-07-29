import path from "node:path";
import { ROOT, fetchJson, groupSnapshots, mapLimit, parseArgs, readJsonl, writeJsonl } from "./lib.mjs";

const args = parseArgs();
const snapshotDate = args.date ?? new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Shanghai" }).format(new Date());
const country = args.country ?? "us";
const input = path.join(ROOT, "data", "normalized", snapshotDate, `${country}-snapshots.jsonl`);
const apps = groupSnapshots(await readJsonl(input));
const batches = [];
for (let index = 0; index < apps.length; index += 50) batches.push(apps.slice(index, index + 50));

const responses = await mapLimit(batches, Number(args.concurrency ?? 3), async (batch, index) => {
  const ids = batch.map((app) => app.appId).join(",");
  const url = `https://itunes.apple.com/lookup?id=${ids}&country=${country}&entity=software`;
  const data = await fetchJson(url);
  process.stdout.write(`lookup batch ${index + 1}/${batches.length}: ${data.resultCount ?? 0}\n`);
  return data.results ?? [];
});

await writeJsonl(
  path.join(ROOT, "data", "enriched", snapshotDate, `${country}-lookup.jsonl`),
  responses.flat()
);

