import { createHash } from "node:crypto";
import { mkdir, readFile } from "node:fs/promises";

export const nowIso = () => new Date().toISOString();
export const sleep = (milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds));
export const sha256 = (value) => createHash("sha256").update(String(value)).digest("hex");

export async function ensureDir(path) {
  await mkdir(path, { recursive: true });
}

export function parseBoolean(value, fallback = false) {
  if (value == null || value === "") return fallback;
  if (typeof value === "boolean") return value;
  return ["1", "true", "yes", "y", "on"].includes(String(value).trim().toLowerCase());
}

export function positiveInteger(value, fallback, name) {
  const parsed = Number.parseInt(value ?? fallback, 10);
  if (!Number.isFinite(parsed) || parsed <= 0) throw new Error(`${name} must be a positive integer`);
  return parsed;
}

export function normalizeDomain(value) {
  if (!value) return "";
  const candidate = /^https?:\/\//i.test(value) ? value : `https://${value}`;
  try {
    return new URL(candidate).hostname.toLowerCase().replace(/^www\./, "");
  } catch {
    throw new Error(`Invalid domain: ${value}`);
  }
}

export function splitPersonName(personName) {
  const parts = String(personName ?? "").trim().split(/\s+/).filter(Boolean);
  if (parts.length < 2) return { firstName: parts[0] ?? "", lastName: "" };
  return { firstName: parts.slice(0, -1).join(" "), lastName: parts.at(-1) };
}

export function parseArgs(argv) {
  const [command = "help", ...rest] = argv;
  const flags = {};
  for (let index = 0; index < rest.length; index += 1) {
    const item = rest[index];
    if (!item.startsWith("--")) throw new Error(`Unexpected argument: ${item}`);
    const key = item.slice(2);
    const next = rest[index + 1];
    if (next && !next.startsWith("--")) {
      flags[key] = next;
      index += 1;
    } else {
      flags[key] = true;
    }
  }
  return { command, flags };
}

export async function loadEnvFile(path = ".env") {
  let text;
  try {
    text = await readFile(path, "utf8");
  } catch (error) {
    if (error.code === "ENOENT") return;
    throw error;
  }
  for (const rawLine of text.split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line || line.startsWith("#")) continue;
    const separator = line.indexOf("=");
    if (separator <= 0) continue;
    const key = line.slice(0, separator).trim();
    const value = line.slice(separator + 1).trim().replace(/^(["'])(.*)\1$/, "$2");
    if (process.env[key] == null) process.env[key] = value;
  }
}
