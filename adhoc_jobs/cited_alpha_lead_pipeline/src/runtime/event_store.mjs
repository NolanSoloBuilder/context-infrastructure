import { open, readFile, unlink, writeFile, chmod, rename } from "node:fs/promises";
import { randomUUID } from "node:crypto";
import { ensureDir, nowIso } from "../utils.mjs";

function processAlive(pid) {
  if (!Number.isInteger(pid) || pid <= 0) return false;
  try { process.kill(pid, 0); return true; } catch (error) { return error.code === "EPERM"; }
}

export async function acquireLock(outputDir, staleAfterMs = 2 * 60 * 60 * 1000) {
  await ensureDir(outputDir);
  await chmod(outputDir, 0o700);
  const path = `${outputDir}/.pipeline.lock`;
  const token = randomUUID();
  let handle = null;
  for (let attempt = 0; attempt < 2 && !handle; attempt += 1) {
    try {
      handle = await open(path, "wx", 0o600);
    } catch (error) {
      if (error.code !== "EEXIST") throw error;
      let existing = {};
      try { existing = JSON.parse(await readFile(path, "utf8")); } catch {}
      const age = Date.now() - Date.parse(existing.acquiredAt || 0);
      if (processAlive(existing.pid) || !Number.isFinite(age) || age < staleAfterMs) {
        throw new Error(`Another pipeline run holds ${path}`);
      }
      try {
        await rename(path, `${path}.stale.${existing.token || "unknown"}.${Date.now()}`);
      } catch (renameError) {
        if (renameError.code !== "ENOENT") throw renameError;
      }
    }
  }
  if (!handle) throw new Error(`Unable to acquire ${path}`);
  await handle.writeFile(JSON.stringify({ token, pid: process.pid, acquiredAt: nowIso() }));
  await handle.sync();
  await handle.close();
  return async () => {
    try {
      const current = JSON.parse(await readFile(path, "utf8"));
      if (current.token === token) await unlink(path);
    } catch {}
  };
}

export async function appendEvent(path, event) {
  const handle = await open(path, "a", 0o600);
  try {
    await handle.write(`${JSON.stringify(event)}\n`);
    await handle.sync();
  } finally {
    await handle.close();
  }
}

export async function readEvents(path) {
  let text;
  try {
    text = await readFile(path, "utf8");
  } catch (error) {
    if (error.code === "ENOENT") return [];
    throw error;
  }
  const lines = text.split("\n");
  const events = [];
  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index].trim();
    if (!line) continue;
    try {
      events.push(JSON.parse(line));
    } catch (error) {
      if (index === lines.length - 1) break;
      throw new Error(`Corrupt event log at line ${index + 1}: ${error.message}`);
    }
  }
  return events;
}

export async function writePrivateJson(path, value) {
  await writeFile(path, `${JSON.stringify(value, null, 2)}\n`, { mode: 0o600 });
  await chmod(path, 0o600);
}

export async function writePrivateJsonAtomic(path, value) {
  const temporaryPath = `${path}.${process.pid}.${randomUUID()}.tmp`;
  await writePrivateJson(temporaryPath, value);
  await rename(temporaryPath, path);
  await chmod(path, 0o600);
}

export async function readJsonIfExists(path) {
  try { return JSON.parse(await readFile(path, "utf8")); } catch (error) {
    if (error.code === "ENOENT") return null;
    throw error;
  }
}

export async function acquireAttemptMarker(path, payload) {
  try {
    const handle = await open(path, "wx", 0o600);
    await handle.writeFile(JSON.stringify(payload));
    await handle.sync();
    await handle.close();
    return true;
  } catch (error) {
    if (error.code === "EEXIST") return false;
    throw error;
  }
}

export async function clearAttemptMarker(path) {
  await unlink(path).catch((error) => { if (error.code !== "ENOENT") throw error; });
}
