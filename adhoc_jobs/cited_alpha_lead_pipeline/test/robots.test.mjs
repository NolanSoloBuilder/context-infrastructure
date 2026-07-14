import test from "node:test";
import assert from "node:assert/strict";
import { parseRobots, robotsAllows } from "../src/net/robots.mjs";

test("robots uses the most specific matching rule and allow wins a tie", () => {
  const policy = parseRobots(`
User-agent: *
Disallow: /private
Allow: /private/contact
Crawl-delay: 2
`, "CitedAlphaContactResearchBot/0.1");
  assert.equal(robotsAllows(policy, new URL("https://example.com/private/report")), false);
  assert.equal(robotsAllows(policy, new URL("https://example.com/%70rivate/report")), false);
  assert.equal(robotsAllows(policy, new URL("https://example.com/private/contact")), true);
  assert.equal(robotsAllows(policy, new URL("https://example.com/about")), true);
  assert.equal(policy.crawlDelayMs, 2000);
});

test("specific user-agent group overrides wildcard group", () => {
  const policy = parseRobots(`
User-agent: *
Disallow: /

User-agent: CitedAlphaContactResearchBot
Allow: /
`, "CitedAlphaContactResearchBot/0.1");
  assert.equal(robotsAllows(policy, new URL("https://example.com/contact")), true);
});
