import fs from "node:fs/promises";
import path from "node:path";

export const ROOT = path.resolve(import.meta.dirname, "..");

export function parseArgs(argv = process.argv.slice(2)) {
  const args = {};
  for (let index = 0; index < argv.length; index += 1) {
    const value = argv[index];
    if (!value.startsWith("--")) continue;
    const [rawKey, inlineValue] = value.slice(2).split("=", 2);
    const next = argv[index + 1];
    if (inlineValue !== undefined) args[rawKey] = inlineValue;
    else if (next && !next.startsWith("--")) {
      args[rawKey] = next;
      index += 1;
    } else args[rawKey] = true;
  }
  return args;
}

export async function readJson(file) {
  return JSON.parse(await fs.readFile(file, "utf8"));
}

export async function writeJson(file, value) {
  await fs.mkdir(path.dirname(file), { recursive: true });
  await fs.writeFile(file, `${JSON.stringify(value, null, 2)}\n`);
}

export async function readJsonl(file) {
  const content = await fs.readFile(file, "utf8");
  return content
    .split("\n")
    .filter(Boolean)
    .map((line) => JSON.parse(line));
}

export async function writeJsonl(file, rows) {
  await fs.mkdir(path.dirname(file), { recursive: true });
  await fs.writeFile(file, `${rows.map((row) => JSON.stringify(row)).join("\n")}\n`);
}

export async function fetchJson(url, { retries = 3, timeoutMs = 20_000 } = {}) {
  let lastError;
  for (let attempt = 1; attempt <= retries; attempt += 1) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), timeoutMs);
    try {
      const response = await fetch(url, {
        signal: controller.signal,
        headers: { "user-agent": "context-infrastructure-app-store-research/1.0" }
      });
      if (!response.ok) throw new Error(`HTTP ${response.status} ${response.statusText}`);
      return await response.json();
    } catch (error) {
      lastError = error;
      if (attempt < retries) await new Promise((resolve) => setTimeout(resolve, 500 * attempt));
    } finally {
      clearTimeout(timeout);
    }
  }
  throw new Error(`Fetch failed: ${url}: ${lastError?.message ?? "unknown error"}`);
}

export async function mapLimit(items, limit, mapper) {
  const results = new Array(items.length);
  let cursor = 0;
  async function worker() {
    while (cursor < items.length) {
      const index = cursor;
      cursor += 1;
      results[index] = await mapper(items[index], index);
    }
  }
  await Promise.all(Array.from({ length: Math.min(limit, items.length) }, () => worker()));
  return results;
}

function label(entry, key) {
  return entry?.[key]?.label ?? null;
}

export function normalizeFeed(data, context) {
  const entries = data?.feed?.entry ?? [];
  return entries.map((entry, index) => ({
    collectedAt: context.collectedAt,
    snapshotDate: context.snapshotDate,
    source: "apple_legacy_rss",
    sourceUrl: context.sourceUrl,
    country: context.country,
    device: "iphone",
    chart: context.chart,
    requestedCategory: context.category.id,
    requestedCategoryName: context.category.name,
    rank: index + 1,
    appId: entry?.id?.attributes?.["im:id"] ?? null,
    bundleId: entry?.id?.attributes?.["im:bundleId"] ?? null,
    name: label(entry, "im:name"),
    developer: label(entry, "im:artist"),
    summary: label(entry, "summary"),
    priceLabel: label(entry, "im:price"),
    priceAmount: Number(entry?.["im:price"]?.attributes?.amount ?? 0),
    currency: entry?.["im:price"]?.attributes?.currency ?? null,
    category: entry?.category?.attributes?.label ?? null,
    categoryId: entry?.category?.attributes?.["im:id"] ?? null,
    releaseDate: label(entry, "im:releaseDate"),
    appStoreUrl: entry?.link?.attributes?.href ?? null,
    iconUrl: entry?.["im:image"]?.at(-1)?.label ?? null
  }));
}

export function groupSnapshots(rows) {
  const apps = new Map();
  for (const row of rows) {
    if (!row.appId) continue;
    const current = apps.get(row.appId) ?? {
      appId: row.appId,
      name: row.name,
      developer: row.developer,
      summary: row.summary,
      category: row.category,
      appStoreUrl: row.appStoreUrl,
      iconUrl: row.iconUrl,
      priceAmount: row.priceAmount,
      priceLabel: row.priceLabel,
      appearances: []
    };
    current.appearances.push({
      date: row.snapshotDate,
      chart: row.chart,
      category: row.requestedCategory,
      categoryName: row.requestedCategoryName,
      rank: row.rank,
      country: row.country
    });
    apps.set(row.appId, current);
  }
  return [...apps.values()];
}

const SIGNALS = {
  file: ["pdf", "document", "file", "scan", "scanner", "ocr", "receipt", "invoice", "spreadsheet", "csv", "resume", "font"],
  image: ["photo", "image", "picture", "background remover", "collage", "resize", "compress", "watermark", "pixel", "color palette"],
  video: ["video", "subtitle", "caption", "teleprompter", "transcript", "transcribe", "crop video", "video editor"],
  audio: ["audio", "voice", "noise removal", "equalizer", "metronome", "bpm", "tuner", "sound meter"],
  generator: ["calculator", "converter", "generator", "maker", "designer", "planner", "checklist", "template", "formatter", "validator"],
  localAi: ["ai", "summarize", "extract", "classify", "translate", "rewrite", "proofread", "recognition"]
};

const HARD_NATIVE = {
  vpn: ["vpn", "proxy server", "ad blocker"],
  location: ["gps", "turn-by-turn", "navigation", "speedometer", "radar detector"],
  wearable: ["apple watch", "watch app", "step counter", "pedometer", "heart rate"],
  deviceIntegration: ["keyboard", "caller id", "call recorder", "bluetooth", "remote control", "carplay", "widget"],
  healthData: ["healthkit", "cycle tracking", "blood pressure", "glucose monitor"]
};

const PLATFORM = {
  marketplace: ["food delivery", "shop online", "buy and sell", "marketplace", "grocery delivery"],
  network: ["dating", "social network", "make friends", "community chat", "messenger"],
  content: ["streaming service", "watch movies", "live sports", "tv shows", "news app"],
  regulated: ["mobile banking", "bank account", "crypto exchange", "sports betting", "medical diagnosis"]
};

function matchSignals(text, dictionary) {
  const matches = [];
  for (const [group, terms] of Object.entries(dictionary)) {
    const found = terms.filter((term) => text.includes(term));
    if (found.length) matches.push({ group, terms: found });
  }
  return matches;
}

function rankDemand(bestRank) {
  if (bestRank <= 10) return 16;
  if (bestRank <= 25) return 14;
  if (bestRank <= 50) return 12;
  if (bestRank <= 100) return 9;
  if (bestRank <= 200) return 6;
  return 3;
}

export function machineScreen(app, lookup = {}) {
  const text = [app.name, app.summary, lookup.description, lookup.genres?.join(" ")]
    .filter(Boolean)
    .join(" ")
    .toLowerCase();
  const webSignals = matchSignals(text, SIGNALS);
  const nativeSignals = matchSignals(text, HARD_NATIVE);
  const platformSignals = matchSignals(text, PLATFORM);
  const bestRank = Math.min(...app.appearances.map((item) => item.rank));
  const chartCount = new Set(app.appearances.map((item) => item.chart)).size;
  const categoryCount = new Set(app.appearances.map((item) => item.category)).size;
  const paidEvidence = app.priceAmount > 0 || lookup.price > 0;
  const iapEvidence = Array.isArray(lookup.inAppPurchases) && lookup.inAppPurchases.length > 0;
  const ratingCount = Number(lookup.userRatingCount ?? 0);

  const webFeasibility = Math.max(
    0,
    Math.min(25, 5 + webSignals.length * 5 - nativeSignals.length * 12 - platformSignals.length * 8)
  );
  const taskClarity = Math.min(15, webSignals.reduce((total, item) => total + Math.min(5, item.terms.length * 2), 0));
  const demand = Math.min(20, rankDemand(bestRank) + Math.min(4, chartCount + categoryCount - 2));
  const monetization = Math.min(15, (paidEvidence ? 7 : 0) + (iapEvidence ? 5 : 0) + (ratingCount >= 1_000 ? 3 : 0));
  const soloBuild = nativeSignals.length || platformSignals.length ? 2 : Math.min(10, 4 + webSignals.length * 2);
  const risk = platformSignals.some((item) => item.group === "regulated") ? 0 : nativeSignals.length ? 3 : 10;
  const machineScreenScore = webFeasibility + taskClarity + demand + monetization + soloBuild + risk;

  let disposition = "needs_manual_review";
  if (nativeSignals.length || platformSignals.length) disposition = "reject_likely_native_or_platform";
  else if (webSignals.length >= 2 && machineScreenScore >= 55) disposition = "shortlist_for_evidence_review";

  return {
    ...app,
    lookup: {
      description: lookup.description ?? null,
      genres: lookup.genres ?? [],
      averageUserRating: lookup.averageUserRating ?? null,
      userRatingCount: ratingCount,
      price: lookup.price ?? app.priceAmount ?? 0,
      currency: lookup.currency ?? null,
      inAppPurchases: lookup.inAppPurchases ?? [],
      currentVersionReleaseDate: lookup.currentVersionReleaseDate ?? null,
      trackViewUrl: lookup.trackViewUrl ?? app.appStoreUrl
    },
    screen: {
      machineScreenScore,
      evidenceScore: null,
      disposition,
      bestRank,
      components: { webFeasibility, taskClarity, demand, monetization, soloBuild, risk },
      webSignals,
      nativeSignals,
      platformSignals,
      evidenceStatus: "not_researched"
    }
  };
}

export function csvCell(value) {
  const text = value == null ? "" : String(value);
  return /[",\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}
