#!/usr/bin/env node
import { resolve } from "node:path";
import { validateInput, runPipeline } from "./core/pipeline.mjs";
import { loadEnvFile, parseArgs, positiveInteger } from "./utils.mjs";

function usage() {
  return `Cited Alpha contact acquisition pipeline

Usage:
  node src/cli.mjs validate --input <targets.csv>
  node src/cli.mjs run --input <targets.csv> --output <directory> [--dry-run]

The pipeline only crawls official public websites and optional approved APIs.
It never scrapes LinkedIn/X and never sends messages automatically.`;
}

function configFrom(flags) {
  const contact = process.env.BOT_CONTACT || "https://example.com/contact";
  return {
    userAgent: `CitedAlphaContactResearchBot/0.1 (+${contact})`,
    maxTargets: positiveInteger(flags["max-targets"] || process.env.MAX_TARGETS, 100, "maxTargets"),
    maxPagesPerDomain: positiveInteger(flags["max-pages"] || process.env.MAX_PAGES_PER_DOMAIN, 12, "maxPagesPerDomain"),
    maxRuntimeSeconds: positiveInteger(flags["max-runtime-seconds"] || process.env.MAX_RUNTIME_SECONDS, 900, "maxRuntimeSeconds"),
    maxApiCalls: positiveInteger(flags["max-api-calls"] || process.env.MAX_API_CALLS, 100, "maxApiCalls"),
    requestDelayMs: positiveInteger(flags["request-delay-ms"] || process.env.REQUEST_DELAY_MS, 2000, "requestDelayMs"),
    refreshAfterDays: positiveInteger(flags["refresh-after-days"] || process.env.REFRESH_AFTER_DAYS, 30, "refreshAfterDays"),
    providerCacheDays: positiveInteger(flags["provider-cache-days"] || process.env.PROVIDER_CACHE_DAYS, 30, "providerCacheDays"),
    verificationCacheDays: positiveInteger(flags["verification-cache-days"] || process.env.VERIFICATION_CACHE_DAYS, 7, "verificationCacheDays"),
    maxPageBytes: 1_500_000,
    requestTimeoutMs: 15_000,
    maxProviderContactsPerTarget: 10,
    allowPrivateNetwork: false,
    suppressionPath: flags.suppression ? resolve(String(flags.suppression)) : "",
    suppressionRequired: Boolean(flags.suppression)
  };
}

async function main() {
  await loadEnvFile();
  const { command, flags } = parseArgs(process.argv.slice(2));
  if (["help", "--help", "-h"].includes(command)) {
    console.log(usage());
    return;
  }
  if (!flags.input) throw new Error("--input is required");
  const inputPath = resolve(String(flags.input));

  if (command === "validate") {
    const targets = await validateInput(inputPath);
    console.log(JSON.stringify({ valid: true, targets: targets.length }, null, 2));
    return;
  }
  if (command !== "run") throw new Error(`Unknown command: ${command}`);
  if (!flags.output) throw new Error("--output is required");
  const result = await runPipeline({
    inputPath,
    outputDir: resolve(String(flags.output)),
    config: configFrom(flags),
    dryRun: Boolean(flags["dry-run"])
  });
  console.log(JSON.stringify(result, null, 2));
  if (result.errors.length > 0) process.exitCode = 3;
}

main().catch((error) => {
  console.error(error.message);
  process.exitCode = 2;
});
