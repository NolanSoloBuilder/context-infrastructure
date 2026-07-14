import test from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { acquireLock } from "../src/runtime/event_store.mjs";

test("lock ownership prevents overlap and stale lock can be recovered", async () => {
  const root = await mkdtemp(join(tmpdir(), "cited-alpha-lock-"));
  const release = await acquireLock(root);
  await assert.rejects(() => acquireLock(root), /Another pipeline run/);
  await release();

  await writeFile(join(root, ".pipeline.lock"), JSON.stringify({ token: "stale", pid: 99999999, acquiredAt: "2000-01-01T00:00:00.000Z" }));
  const releaseRecovered = await acquireLock(root, 1);
  await releaseRecovered();
});
