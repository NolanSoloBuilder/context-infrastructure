import { chromium } from "/Users/xuhao/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs";
import { writeFile } from "node:fs/promises";

const browser = await chromium.launch({ headless: true });
const report = [];

for (const viewport of [
  { name: "desktop", width: 1440, height: 1000 },
  { name: "mobile", width: 390, height: 844 },
]) {
  const context = await browser.newContext({ viewport });
  const page = await context.newPage();
  const errors = [];
  page.on("console", (message) => message.type() === "error" && errors.push(message.text()));
  page.on("pageerror", (error) => errors.push(error.message));

  await page.goto(`http://127.0.0.1:4175/?smoke=${viewport.name}-hello#hello`, { waitUntil: "networkidle" });
  const social = await page.locator(".social-links .social-button").evaluateAll((items) => items.map((item) => ({
    label: item.getAttribute("aria-label"),
    href: item.getAttribute("href"),
    tag: item.tagName,
  })));
  await page.getByLabel("Notes", { exact: true }).click();
  const notesHash = await page.evaluate(() => location.hash);
  await page.goto(`http://127.0.0.1:4175/?smoke=${viewport.name}-about#hello`, { waitUntil: "networkidle" });
  await page.locator(".about-button").click();
  const portfolioHash = await page.evaluate(() => location.hash);

  const windows = [];
  for (const button of await page.locator(".dock button").all()) {
    await button.click();
    windows.push(await page.locator(".window-title").textContent());
  }

  await page.getByRole("button", { name: "Open Projects" }).click();
  await page.getByRole("option", { name: /Cited Alpha/ }).click();
  const citedLayout = await page.locator(".project-media.gallery-count-2").evaluate((element) => ({
    display: getComputedStyle(element).display,
    direction: getComputedStyle(element).flexDirection,
    images: element.querySelectorAll("img").length,
  }));

  await page.goto(`http://127.0.0.1:4175/?smoke=${viewport.name}-end#end`, { waitUntil: "networkidle" });
  await page.getByRole("button", { name: "Back to start" }).click();
  const restartHash = await page.evaluate(() => location.hash);
  const dimensions = await page.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth,
    clientWidth: document.documentElement.clientWidth,
  }));

  report.push({ viewport, errors, social, notesHash, portfolioHash, windows, citedLayout, restartHash, dimensions });
  await context.close();
}

await writeFile(new URL("./site-smoke-report.json", import.meta.url), JSON.stringify(report, null, 2));
await browser.close();
