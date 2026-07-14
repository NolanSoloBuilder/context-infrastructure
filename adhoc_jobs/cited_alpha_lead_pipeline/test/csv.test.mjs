import test from "node:test";
import assert from "node:assert/strict";
import { parseCsv, stringifyCsv } from "../src/csv.mjs";

test("CSV parser handles quotes, commas and newlines", () => {
  const rows = parseCsv('name,note\n"Doe, Jane","line 1\nline 2"\n');
  assert.deepEqual(rows, [{ name: "Doe, Jane", note: "line 1\nline 2" }]);
  assert.equal(stringifyCsv(rows, ["name", "note"]), 'name,note\n"Doe, Jane","line 1\nline 2"\n');
});

test("CSV export neutralizes spreadsheet formulas", () => {
  assert.equal(stringifyCsv([{ value: "=HYPERLINK(\"https://evil.example\")" }], ["value"]), 'value\n"\'=HYPERLINK(""https://evil.example"")"\n');
});
