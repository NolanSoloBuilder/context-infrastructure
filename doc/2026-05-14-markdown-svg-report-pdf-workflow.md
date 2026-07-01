---
categories: ["Syncopation", "Workflow", "PDF", "Markdown", "SVG"]
date: 2026-05-14
draft: true
comments: true
links:
readtime: 12
slug: markdown-svg-report-pdf-workflow
authors:
  - <qihang>
---

# Markdown + SVG Report To PDF Workflow

This note captures a standalone workflow for producing a polished PDF report from a Markdown report with interleaved SVG illustrations. It is intentionally independent of the `extended-memory` repo harness. The same pattern should work in any local project as long as the required tools are installed.

The concrete use case that produced this workflow was a tutorial-style report: meeting notes were reorganized into a readable report, explanatory SVG diagrams were inserted between sections, and the final PDF was written directly to `~/Downloads` rather than committed to the repo.

## Goal

Turn this:

```text
report.md
assets/
  figure-1.svg
  figure-2.svg
  figure-3.svg
```

into this:

```text
~/Downloads/report.pdf
```

while keeping the source of truth as Markdown plus SVG assets.

## Non-goals

- Do not rely on a repo-specific agent harness.
- Do not commit generated PDF output unless explicitly desired.
- Do not require Pandoc, LaTeX, or InDesign.
- Do not make the SVG a separate artifact detached from the report. The SVGs should explain the report content where they appear.

## Recommended Artifact Model

Use this split:

```text
project/
  report.md                         # canonical text
  assets/
    report-work-split.svg            # explanatory illustration
    report-hot-path.svg              # explanatory illustration
    report-async-eval-loop.svg       # explanatory illustration

/tmp/
  report.html                        # generated intermediate, disposable
  report-html-check.png              # optional visual check, disposable

~/Downloads/
  report.pdf                         # final handoff artifact
```

The Markdown and SVG files are durable source artifacts. The HTML is a generated intermediate. The PDF is a user-facing export and can live only in Downloads.

## Dependencies

Required:

- Node.js
- `marked` Node package
- Google Chrome or Chromium with headless mode

Recommended for checks:

- `xmllint` for SVG validation
- `file` for basic PDF type check
- macOS `mdls` for page count
- Python `pypdf` for page count and text extraction
- macOS `qlmanage` for a quick PDF thumbnail

Install `marked` in any normal Node environment:

```bash
npm install marked
```

If running inside an environment where packages are preinstalled in a nonstandard location, set `NODE_PATH` before invoking Node:

```bash
export NODE_PATH=/path/to/node_modules
```

## Authoring Rules For The Report

Write the report as normal Markdown:

```markdown
# Report Title

Intro text.

## First Concept

Meeting note text.

![Source work split](assets/source-work-split.svg)

Explanation text.
```

Keep diagrams close to the section they explain. The diagram should not be an appendix-only architecture dump unless the report explicitly needs an overview.

Use this structure for tutorial reports:

```text
TLDR
Context
Concept 1
  meeting note
  figure
  tutorial explanation
Concept 2
  meeting note
  figure
  tutorial explanation
TODO
Open Questions
Design Principles
```

## SVG Authoring Rules

SVG text does not wrap automatically. Split long labels into multiple `<text>` lines manually:

```xml
<text x="84" y="542" class="small">If the source store is stale or sparse, retrieval and agent reasoning</text>
<text x="84" y="562" class="small">are bottlenecked before the model starts.</text>
```

Do not place text baselines too close to the bottom of a rectangle. Leave enough vertical padding because PDF scaling can clip descenders.

Prefer several explanatory diagrams over one huge diagram when the report is meant to teach. A large overview is useful, but small figures are better for section-by-section explanation.

Validate SVGs before rendering:

```bash
xmllint --noout assets/*.svg
```

## Reusable Render Script

This script:

- strips optional YAML front matter;
- converts Markdown to HTML with `marked`;
- supports Marked's newer image-token renderer API;
- resolves relative image links to absolute `file://` URLs;
- wraps images in `<figure>` with captions;
- applies print CSS;
- invokes Chrome headless with browser header/footer disabled;
- writes the PDF to `~/Downloads` or another explicit output path.

Save it as a temporary script, for example `/tmp/render-markdown-svg-report-to-pdf.js`, or paste it into `node <<'NODE'`.

```javascript
const fs = require("fs");
const os = require("os");
const path = require("path");
const { execFileSync } = require("child_process");
const { marked } = require("marked");

function requiredEnv(name) {
  const value = process.env[name];
  if (!value) throw new Error(`Missing required env var: ${name}`);
  return value;
}

const mdPath = path.resolve(requiredEnv("REPORT_MD"));
const baseDir = path.dirname(mdPath);
const outPdf = path.resolve(
  process.env.OUTPUT_PDF ||
    path.join(os.homedir(), "Downloads", `${path.basename(mdPath, ".md")}.pdf`)
);
const outHtml = path.resolve(
  process.env.OUTPUT_HTML ||
    path.join(os.tmpdir(), `${path.basename(mdPath, ".md")}.html`)
);
const chrome = process.env.CHROME_BIN || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";

let md = fs.readFileSync(mdPath, "utf8");
md = md.replace(/^---[\s\S]*?---\s*/, "");

const escapeHtml = (s) =>
  String(s || "")
    .replace(/&/g, "&amp;")
    .replace(/"/g, "&quot;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

const renderer = new marked.Renderer();

renderer.image = function imageRenderer(tokenOrHref, title, text) {
  let href;
  let imageTitle;
  let imageText;

  // Marked v17+ passes a token object. Older versions pass href/title/text.
  if (tokenOrHref && typeof tokenOrHref === "object") {
    href = tokenOrHref.href;
    imageTitle = tokenOrHref.title;
    imageText = tokenOrHref.text;
  } else {
    href = tokenOrHref;
    imageTitle = title;
    imageText = text;
  }

  if (href && !/^[a-z]+:/i.test(href)) {
    href = "file://" + path.resolve(baseDir, href);
  }

  const titleAttr = imageTitle ? ` title="${escapeHtml(imageTitle)}"` : "";
  return [
    "<figure>",
    `<img src="${escapeHtml(href)}" alt="${escapeHtml(imageText)}"${titleAttr}>`,
    `<figcaption>${escapeHtml(imageText)}</figcaption>`,
    "</figure>",
  ].join("");
};

marked.setOptions({ renderer, gfm: true, breaks: false });
const body = marked.parse(md);

const html = `<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>${escapeHtml(path.basename(mdPath, ".md"))}</title>
  <style>
    @page { size: A4; margin: 16mm 15mm 18mm; }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      color: #111827;
      font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI",
        "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
      font-size: 12.2px;
      line-height: 1.62;
      background: #ffffff;
    }
    h1, h2, h3 {
      color: #0f172a;
      line-height: 1.25;
      letter-spacing: 0;
    }
    h1 {
      font-size: 30px;
      margin: 0 0 12px;
      padding-bottom: 14px;
      border-bottom: 2px solid #e5e7eb;
    }
    h2 {
      font-size: 21px;
      margin: 28px 0 10px;
      padding-top: 4px;
    }
    h3 {
      font-size: 15.5px;
      margin: 18px 0 7px;
    }
    p { margin: 8px 0; }
    ul, ol { margin: 7px 0 12px 20px; padding: 0; }
    li { margin: 3px 0; }
    blockquote {
      margin: 14px 0;
      padding: 10px 14px;
      border-left: 4px solid #60a5fa;
      background: #eff6ff;
      color: #1e3a8a;
      border-radius: 8px;
    }
    code {
      font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
      font-size: 0.92em;
      background: #f3f4f6;
      border: 1px solid #e5e7eb;
      border-radius: 5px;
      padding: 1px 4px;
    }
    pre {
      margin: 12px 0;
      padding: 12px 14px;
      background: #0f172a;
      color: #e5e7eb;
      border-radius: 10px;
      overflow: hidden;
      white-space: pre-wrap;
      page-break-inside: avoid;
    }
    pre code {
      background: transparent;
      border: 0;
      color: inherit;
      padding: 0;
    }
    figure {
      margin: 16px 0 18px;
      padding: 10px;
      border: 1px solid #e5e7eb;
      border-radius: 12px;
      background: #ffffff;
      page-break-inside: avoid;
    }
    figure img {
      display: block;
      width: 100%;
      height: auto;
    }
    figcaption {
      margin-top: 7px;
      color: #667085;
      font-size: 11px;
      text-align: center;
    }
    a {
      color: #2563eb;
      text-decoration: none;
    }
  </style>
</head>
<body>${body}</body>
</html>`;

fs.writeFileSync(outHtml, html);

execFileSync(
  chrome,
  [
    "--headless=new",
    "--disable-gpu",
    "--no-pdf-header-footer",
    "--allow-file-access-from-files",
    `--print-to-pdf=${outPdf}`,
    "file://" + outHtml,
  ],
  { stdio: "inherit" }
);

console.log(outPdf);
```

## Render Command

Use absolute paths:

```bash
export REPORT_MD="/absolute/path/to/report.md"
export OUTPUT_PDF="$HOME/Downloads/report.pdf"
export CHROME_BIN="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

node /tmp/render-markdown-svg-report-to-pdf.js
```

If `marked` is installed in a nonstandard package directory:

```bash
export NODE_PATH="/absolute/path/to/node_modules"
```

Then rerun the same Node command.

## QA Commands

Basic file check:

```bash
file "$OUTPUT_PDF"
ls -lh "$OUTPUT_PDF"
```

macOS page count:

```bash
mdls -name kMDItemNumberOfPages "$OUTPUT_PDF"
```

Python page count and text extraction:

```bash
python3 - <<'PY'
from pypdf import PdfReader
import os

p = os.environ["OUTPUT_PDF"]
r = PdfReader(p)
print(len(r.pages))
print((r.pages[0].extract_text() or "")[:500])
PY
```

Quick PDF thumbnail on macOS:

```bash
rm -rf /tmp/report-pdfcheck
mkdir -p /tmp/report-pdfcheck
qlmanage -t -s 1600 -o /tmp/report-pdfcheck "$OUTPUT_PDF"
```

Continuous HTML screenshot for catching SVG clipping:

```bash
"$CHROME_BIN" \
  --headless=new \
  --disable-gpu \
  --allow-file-access-from-files \
  --hide-scrollbars \
  --window-size=1400,5200 \
  --screenshot=/tmp/report-html-check.png \
  "file:///tmp/report.html"
```

The HTML screenshot does not prove exact page breaks, but it is very good at catching image loading failures, SVG text clipping, and obvious layout problems.

## Common Problems And Fixes

### Problem: Chrome adds date, URL, and page numbers

Use:

```bash
--no-pdf-header-footer
```

Without this flag, Chrome's default printed PDF can include browser headers and footers.

### Problem: SVG images do not load in the PDF

Make sure the renderer converts relative Markdown image paths to absolute `file://` URLs.

Also include:

```bash
--allow-file-access-from-files
```

### Problem: Marked image renderer crashes

Newer `marked` versions can call `renderer.image` with a token object instead of `(href, title, text)`. Use a renderer that supports both signatures:

```javascript
if (tokenOrHref && typeof tokenOrHref === "object") {
  href = tokenOrHref.href;
  imageTitle = tokenOrHref.title;
  imageText = tokenOrHref.text;
} else {
  href = tokenOrHref;
  imageTitle = title;
  imageText = text;
}
```

### Problem: SVG text is clipped

SVG `<text>` does not wrap. Split long lines manually and leave vertical padding in containing rectangles.

Bad:

```xml
<text x="740" y="566">A long line near the bottom of a short rectangle...</text>
```

Better:

```xml
<text x="740" y="542">Keep the interface narrow:</text>
<text x="740" y="562">prompt -> candidate URLs -> append to SQL/source store.</text>
```

Also keep the final text baseline comfortably above the rectangle bottom.

### Problem: One huge diagram is too dense

Use smaller explanatory figures near the relevant sections. For example:

- a governance vs capability split diagram;
- a hot-path runtime diagram;
- an async maintenance and evaluation loop diagram;
- optionally one full architecture overview.

The report should teach the reader section by section. A giant architecture chart can be included, but it should not be the only visual explanation.

### Problem: Chinese text renders poorly

Use a CSS font stack that includes macOS and Windows Chinese fonts:

```css
font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI",
  "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
```

## Git Hygiene

For a report workflow where the PDF is only a handoff artifact:

- commit the Markdown report;
- commit durable SVG source assets;
- do not commit `/tmp` intermediates;
- do not commit the generated PDF if the user only wants it in Downloads;
- stage only files related to the current task.

Useful status check:

```bash
git status --short
```

Useful staged diff check:

```bash
git diff --cached --stat
git diff --cached --check
```

## Minimal Checklist

1. Write or update `report.md`.
2. Put SVG illustrations under `assets/`.
3. Validate SVGs with `xmllint --noout assets/*.svg`.
4. Render Markdown to `/tmp/report.html`.
5. Print HTML to `~/Downloads/report.pdf` with Chrome headless.
6. Check file type, page count, first-page text extraction, and at least one visual preview.
7. Fix SVG clipping or layout issues.
8. Commit only Markdown and SVG source files if durability is needed.

## Retrieval Keywords

Markdown to PDF workflow, SVG report workflow, Chrome headless PDF export, marked renderer image token, file URL image resolution, no-pdf-header-footer, qlmanage PDF thumbnail, pypdf page count, SVG text clipping, Downloads-only PDF artifact, tutorial report generation.
