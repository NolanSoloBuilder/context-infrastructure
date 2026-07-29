import { chromium } from "/Users/xuhao/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs";
import { mkdir, writeFile } from "node:fs/promises";

const outputDir = new URL("./notes-local/", import.meta.url);
await mkdir(outputDir, { recursive: true });
const browser = await chromium.launch({ headless: true });
const report = [];

for (const viewport of [
  { name: "desktop", width: 1440, height: 1000 },
  { name: "mobile", width: 390, height: 844 },
]) {
  const context = await browser.newContext({ viewport });
  const page = await context.newPage();
  const errors = [];
  page.on("console", (message) => {
    if (message.type() === "error") errors.push(message.text());
  });
  page.on("pageerror", (error) => errors.push(error.message));

  await page.goto("http://127.0.0.1:4175/#notes", { waitUntil: "networkidle" });
  await page.screenshot({ path: new URL(`index-${viewport.name}.png`, outputDir).pathname, fullPage: true });

  const indexState = await page.evaluate(() => ({
    hash: location.hash,
    heading: document.querySelector(".notes-index h2")?.textContent,
    notes: document.querySelectorAll(".notes-list button").length,
    scrollWidth: document.documentElement.scrollWidth,
    clientWidth: document.documentElement.clientWidth,
  }));

  await page.locator(".notes-list button").first().click();
  await page.screenshot({ path: new URL(`article-${viewport.name}.png`, outputDir).pathname, fullPage: true });
  const articleState = await page.evaluate(() => ({
    heading: document.querySelector(".note-article h2")?.textContent,
    paragraphs: document.querySelectorAll(".note-article > p:not(.note-date)").length,
    backVisible: Boolean(document.querySelector(".notes-back")),
  }));

  await page.locator(".notes-back").click();
  const returnedToIndex = await page.locator(".notes-index").isVisible();
  await page.getByRole("button", { name: "Portfolio" }).click();
  const portfolioHash = await page.evaluate(() => location.hash);
  await page.goto("http://127.0.0.1:4175/#notes", { waitUntil: "networkidle" });
  await page.getByRole("button", { name: "Continue" }).click();
  const continueHash = await page.evaluate(() => location.hash);
  report.push({ viewport, errors, indexState, articleState, returnedToIndex, portfolioHash, continueHash });
  await context.close();
}

await writeFile(new URL("report.json", outputDir), JSON.stringify(report, null, 2));
await browser.close();
