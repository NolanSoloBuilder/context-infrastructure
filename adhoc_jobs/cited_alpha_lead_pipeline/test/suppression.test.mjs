import test from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { contactSuppressed, loadSuppression } from "../src/policy/suppression.mjs";

test("suppression matches target IDs and normalized contact values", async () => {
  const root = await mkdtemp(join(tmpdir(), "cited-alpha-suppression-"));
  const path = join(root, "suppression.csv");
  await writeFile(path, "target_id,contact_value,reason\nblocked,,opt_out\n,Stop@Example.com,hard_bounce\n");
  const suppression = await loadSuppression(path);
  assert.equal(suppression.targetIds.has("blocked"), true);
  assert.equal(contactSuppressed(suppression, "stop@example.com"), true);
  assert.equal(contactSuppressed(suppression, "other@example.com"), false);
});

test("an explicitly required suppression file fails closed when missing", async () => {
  const root = await mkdtemp(join(tmpdir(), "cited-alpha-suppression-missing-"));
  await assert.rejects(loadSuppression(join(root, "missing.csv"), { required: true }), /ENOENT/);
  const optional = await loadSuppression(join(root, "missing.csv"));
  assert.equal(optional.targetIds.size, 0);
});
