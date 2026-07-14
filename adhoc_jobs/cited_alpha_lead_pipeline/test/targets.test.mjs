import test from "node:test";
import assert from "node:assert/strict";
import { normalizeTarget } from "../src/core/targets.mjs";

test("target validation rejects social subdomains and unknown acquisition sources", () => {
  assert.throws(() => normalizeTarget({ domain: "m.linkedin.com" }, 0), /social platforms/);
  assert.throws(() => normalizeTarget({ domain: "example.com", acquisition_source_type: "linkedin_scrape" }, 0), /unknown acquisition_source_type/);
});
