import test from "node:test";
import assert from "node:assert/strict";
import http from "node:http";
import { crawlOfficialSite } from "../src/discovery/official_site.mjs";

test("robots failure defers crawl instead of claiming no public contact", async (context) => {
  const server = http.createServer((request, response) => {
    if (request.url === "/robots.txt") {
      response.writeHead(503, { "Content-Type": "text/plain" });
      response.end("unavailable");
      return;
    }
    response.writeHead(200, { "Content-Type": "text/html" });
    response.end("<p>should not be fetched</p>");
  });
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  context.after(() => server.close());
  const { port } = server.address();
  const result = await crawlOfficialSite({ domain: "127.0.0.1", websiteUrl: `http://127.0.0.1:${port}` }, {
    userAgent: "CitedAlphaContactResearchBot/0.1", maxPageBytes: 100_000, requestTimeoutMs: 2_000,
    allowPrivateNetwork: true, requestDelayMs: 1, maxPagesPerDomain: 2
  });
  assert.equal(result.crawlStatus, "DEFERRED");
  assert.match(result.deferredReason, /robots_http_503/);
});
