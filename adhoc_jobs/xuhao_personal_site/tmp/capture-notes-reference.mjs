import { chromium } from "/Users/xuhao/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs";
import { mkdir, writeFile } from "node:fs/promises";

const outputDir = new URL("./notes-reference/", import.meta.url);
await mkdir(outputDir, { recursive: true });

const targets = [
  { name: "home", url: "https://blog.yencheng.dev/" },
  { name: "article", url: "https://blog.yencheng.dev/blog/introducing-subflow" },
];

const browser = await chromium.launch({ headless: true });
const report = [];

for (const viewport of [
  { name: "desktop", width: 1440, height: 1000 },
  { name: "mobile", width: 390, height: 844 },
]) {
  const context = await browser.newContext({ viewport });
  const page = await context.newPage();

  for (const target of targets) {
    const response = await page.goto(target.url, { waitUntil: "networkidle", timeout: 60000 });
    await page.screenshot({
      path: new URL(`${target.name}-${viewport.name}.png`, outputDir).pathname,
      fullPage: true,
    });

    const evidence = await page.evaluate(() => {
      const styleOf = (element) => {
        const style = getComputedStyle(element);
        const box = element.getBoundingClientRect();
        return {
          tag: element.tagName.toLowerCase(),
          text: element.textContent?.trim().replace(/\s+/g, " ").slice(0, 240),
          href: element instanceof HTMLAnchorElement ? element.href : undefined,
          box: { x: box.x, y: box.y, width: box.width, height: box.height },
          color: style.color,
          background: style.backgroundColor,
          fontFamily: style.fontFamily,
          fontSize: style.fontSize,
          fontWeight: style.fontWeight,
          lineHeight: style.lineHeight,
          borderRadius: style.borderRadius,
        };
      };

      return {
        title: document.title,
        url: location.href,
        bodyText: document.body.innerText.slice(0, 12000),
        body: styleOf(document.body),
        landmarks: [...document.querySelectorAll("header, nav, main, article, footer")].map(styleOf),
        headings: [...document.querySelectorAll("h1, h2, h3")].map(styleOf),
        links: [...document.querySelectorAll("a")].map(styleOf),
        images: [...document.images].map((image) => ({
          src: image.currentSrc || image.src,
          alt: image.alt,
          width: image.getBoundingClientRect().width,
          height: image.getBoundingClientRect().height,
        })),
        scroll: { width: document.documentElement.scrollWidth, height: document.documentElement.scrollHeight },
      };
    });

    report.push({ viewport, target, status: response?.status(), ...evidence });
  }

  await context.close();
}

await writeFile(new URL("evidence.json", outputDir), JSON.stringify(report, null, 2));
await browser.close();
