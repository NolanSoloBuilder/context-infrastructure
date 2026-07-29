import test from "node:test";
import assert from "node:assert/strict";
import { groupSnapshots, machineScreen, normalizeFeed, parseArgs } from "../src/lib.mjs";
import { normalizeReviews } from "../src/reviews.mjs";

test("parseArgs accepts spaced and inline values", () => {
  assert.deepEqual(parseArgs(["--date", "2026-07-17", "--country=us", "--dry-run"]), {
    date: "2026-07-17",
    country: "us",
    "dry-run": true
  });
});

test("normalizeFeed preserves rank and app identity", () => {
  const data = {
    feed: {
      entry: [
        {
          "im:name": { label: "PDF Tool" },
          id: { attributes: { "im:id": "123", "im:bundleId": "com.example.pdf" } },
          "im:artist": { label: "Example" },
          summary: { label: "Compress PDF files" },
          "im:price": { label: "$1.99", attributes: { amount: "1.99", currency: "USD" } },
          category: { attributes: { label: "Productivity", "im:id": "6007" } },
          link: { attributes: { href: "https://apps.apple.com/app/id123" } }
        }
      ]
    }
  };
  const rows = normalizeFeed(data, {
    collectedAt: "now",
    snapshotDate: "2026-07-17",
    sourceUrl: "https://example.com",
    country: "us",
    chart: "paid",
    category: { id: "productivity", name: "Productivity" }
  });
  assert.equal(rows[0].rank, 1);
  assert.equal(rows[0].appId, "123");
  assert.equal(rows[0].priceAmount, 1.99);
});

test("machineScreen favors bounded file tasks over native integrations", () => {
  const base = {
    appId: "123",
    name: "Private PDF OCR Compressor",
    summary: "Scan, OCR, compress and resize document files locally",
    category: "Productivity",
    priceAmount: 2.99,
    priceLabel: "$2.99",
    appearances: [{ rank: 60, chart: "paid", category: "productivity" }]
  };
  const web = machineScreen(base, { userRatingCount: 2_000, inAppPurchases: ["Pro"] });
  const native = machineScreen({
    ...base,
    name: "Watch GPS VPN",
    summary: "Apple Watch GPS navigation and VPN proxy server"
  });
  assert.equal(web.screen.disposition, "shortlist_for_evidence_review");
  assert.equal(native.screen.disposition, "reject_likely_native_or_platform");
  assert.ok(web.screen.machineScreenScore > native.screen.machineScreenScore);
});

test("groupSnapshots deduplicates apps while preserving appearances", () => {
  const apps = groupSnapshots([
    { appId: "1", name: "A", requestedCategory: "overall", requestedCategoryName: "Overall", chart: "free", rank: 10 },
    { appId: "1", name: "A", requestedCategory: "utilities", requestedCategoryName: "Utilities", chart: "free", rank: 3 }
  ]);
  assert.equal(apps.length, 1);
  assert.equal(apps[0].appearances.length, 2);
});

test("normalizeReviews ignores non-review feed entries", () => {
  const reviews = normalizeReviews(
    {
      feed: {
        entry: [
          { id: { label: "app-metadata" }, title: { label: "metadata" } },
          {
            id: { label: "review-1" },
            author: { name: { label: "User" } },
            "im:rating": { label: "2" },
            "im:version": { label: "1.0" },
            title: { label: "Needs export" },
            content: { label: "Please add PDF export" }
          }
        ]
      }
    },
    "123",
    1,
    "https://example.com"
  );
  assert.equal(reviews.length, 1);
  assert.equal(reviews[0].rating, 2);
});
