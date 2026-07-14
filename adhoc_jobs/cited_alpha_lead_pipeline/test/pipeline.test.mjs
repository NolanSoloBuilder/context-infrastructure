import test from "node:test";
import assert from "node:assert/strict";
import http from "node:http";
import { mkdtemp, readFile, writeFile, stat } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { runPipeline, verificationFresh } from "../src/core/pipeline.mjs";
import { parseCsv } from "../src/csv.mjs";

async function fixtureServer() {
  const server = http.createServer((request, response) => {
    if (request.url === "/robots.txt") {
      response.writeHead(200, { "Content-Type": "text/plain" });
      response.end("User-agent: *\nAllow: /\n");
      return;
    }
    if (request.url === "/") {
      response.writeHead(200, { "Content-Type": "text/html" });
      response.end('<a href="/contact">Contact</a><a href="https://x.com/example">X</a>');
      return;
    }
    if (request.url === "/contact") {
      response.writeHead(200, { "Content-Type": "text/html" });
      response.end('<form action="/contact"><input type="email"></form>');
      return;
    }
    response.writeHead(404, { "Content-Type": "text/plain" });
    response.end("not found");
  });
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  return server;
}

test("pipeline produces contact queues and resumes without provider calls", async (context) => {
  const server = await fixtureServer();
  context.after(() => server.close());
  const { port } = server.address();
  const root = await mkdtemp(join(tmpdir(), "cited-alpha-pipeline-"));
  const input = join(root, "targets.csv");
  const output = join(root, "output");
  await writeFile(input, `target_id,company,domain,website_url,country,subscriber_type,discovery_channel,proof_url,acquisition_source_type,can_spam_ready,privacy_notice_ready\nfixture,Fixture,127.0.0.1,http://127.0.0.1:${port},US,corporate,fixture,http://127.0.0.1:${port}/about,official_company_website,true,true\n`);
  const config = {
    userAgent: "CitedAlphaContactResearchBot/0.1 (+https://example.com/contact)",
    maxTargets: 10, maxPagesPerDomain: 2, maxRuntimeSeconds: 30, maxApiCalls: 1,
    requestDelayMs: 1, refreshAfterDays: 30, maxPageBytes: 100_000,
    requestTimeoutMs: 2_000, maxProviderContactsPerTarget: 2, allowPrivateNetwork: true
  };

  const first = await runPipeline({ inputPath: input, outputDir: output, config, dryRun: true });
  assert.equal(first.eligible, 2);
  const eligible = parseCsv(await readFile(join(first.runDir, "eligible_for_manual_review.csv"), "utf8"));
  assert.deepEqual(new Set(eligible.map((record) => record.contact_type)), new Set(["x_profile", "contact_form"]));
  assert.equal((await stat(first.runDir)).mode & 0o777, 0o700);
  assert.equal((await stat(join(first.runDir, "eligible_for_manual_review.csv"))).mode & 0o777, 0o600);

  const second = await runPipeline({ inputPath: input, outputDir: output, config, dryRun: true });
  assert.equal(second.eligible, 2);
  const events = await readFile(join(output, "events.jsonl"), "utf8");
  assert.match(events, /target_reused_cache/);

  await writeFile(join(output, "suppression.csv"), "target_id,contact_value,reason\nfixture,,opt_out\n");
  const third = await runPipeline({ inputPath: input, outputDir: output, config, dryRun: true });
  assert.equal(third.eligible, 0);
  assert.equal(third.rejected, 1);
});

test("provider verification evidence expires independently of discovery cache", () => {
  const now = Date.parse("2026-07-14T00:00:00.000Z");
  assert.equal(verificationFresh({ verificationStatus: "deliverable", verifiedAt: "2026-07-10T00:00:00.000Z" }, 7, now), true);
  assert.equal(verificationFresh({ verificationStatus: "deliverable", verifiedAt: "2026-06-14T00:00:00.000Z" }, 7, now), false);
  assert.equal(verificationFresh({ verificationStatus: "deliverable" }, 7, now), false);
});
