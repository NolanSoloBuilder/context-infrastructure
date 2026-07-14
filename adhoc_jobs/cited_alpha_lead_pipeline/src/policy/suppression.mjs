import { readFile } from "node:fs/promises";
import { parseCsv } from "../csv.mjs";
import { sha256 } from "../utils.mjs";

export async function loadSuppression(path, { required = false } = {}) {
  if (!path) return { targetIds: new Set(), contacts: new Set(), fingerprint: sha256("") };
  let text;
  try { text = await readFile(path, "utf8"); } catch (error) {
    if (error.code === "ENOENT" && !required) return { targetIds: new Set(), contacts: new Set(), fingerprint: sha256("") };
    throw error;
  }
  const rows = parseCsv(text);
  return {
    targetIds: new Set(rows.map((row) => row.target_id).filter(Boolean)),
    contacts: new Set(rows.map((row) => row.contact_value).filter(Boolean).map((value) => value.trim().toLowerCase())),
    fingerprint: sha256(text)
  };
}

export function contactSuppressed(suppression, value) {
  return Boolean(value) && suppression.contacts.has(String(value).trim().toLowerCase());
}
