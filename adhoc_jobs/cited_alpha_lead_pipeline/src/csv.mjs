import { readFile, writeFile } from "node:fs/promises";
import { parse } from "csv-parse/sync";

export function parseCsv(text) {
  return parse(text, {
    bom: true,
    columns: (headers) => headers.map((header) => header.trim()),
    skip_empty_lines: true,
    relax_column_count_less: true,
    trim: true
  });
}

export async function readCsv(path) {
  return parseCsv(await readFile(path, "utf8"));
}

function escapeCell(value) {
  let text = value == null ? "" : String(value);
  if (/^[\u0000-\u0020]*[=+\-@]/.test(text)) text = `'${text}`;
  return /[",\n\r]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}

export function stringifyCsv(rows, headers) {
  const lines = [headers.map(escapeCell).join(",")];
  for (const row of rows) {
    lines.push(headers.map((header) => escapeCell(row[header])).join(","));
  }
  return `${lines.join("\n")}\n`;
}

export async function writeCsv(path, rows, headers) {
  await writeFile(path, stringifyCsv(rows, headers), "utf8");
}
