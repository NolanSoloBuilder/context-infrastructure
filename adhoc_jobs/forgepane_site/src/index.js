const BRAND_HOSTS = new Set(["forgepane.com", "www.forgepane.com"]);
const PERSONAL_HOST = "nalon.forgepane.com";
const BRAND_ASSET_PATHS = new Set([
  "/assets/arrow-right.svg",
  "/assets/forgepane-favicon.svg",
  "/assets/nunito-bold.woff2",
  "/assets/projects/china-metro-typing-route.webp",
  "/assets/projects/cited-alpha-landing.webp"
]);

const SECURITY_HEADERS = {
  "content-security-policy":
    "default-src 'none'; img-src 'self' data:; font-src 'self'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'",
  "referrer-policy": "strict-origin-when-cross-origin",
  "x-content-type-options": "nosniff",
  "x-frame-options": "DENY"
};

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.hostname === "www.forgepane.com") {
      url.hostname = "forgepane.com";
      return Response.redirect(url.toString(), 301);
    }

    if (url.hostname === PERSONAL_HOST) {
      return env.ASSETS.fetch(request);
    }

    if (BRAND_HOSTS.has(url.hostname)) {
      if (BRAND_ASSET_PATHS.has(url.pathname)) {
        return env.ASSETS.fetch(request);
      }
      if (url.pathname !== "/") {
        return html(notFoundPage(), 404);
      }
      return html(brandPage(), 200);
    }

    return html(notFoundPage(), 404);
  }
};

function html(body, status) {
  return new Response(body, {
    status,
    headers: {
      "content-type": "text/html; charset=utf-8",
      "cache-control": "public, max-age=300",
      ...SECURITY_HEADERS
    }
  });
}

function shell({ title, description, bodyClass, content }) {
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${escapeHtml(title)}</title>
  <meta name="description" content="${escapeHtml(description)}">
  <link rel="icon" type="image/svg+xml" href="/assets/forgepane-favicon.svg">
  <style>
    :root {
      color-scheme: light;
      --ink: #171717;
      --muted: #5f6368;
      --line: #d7d3cb;
      --paper: #f8f7f3;
      --panel: #ffffff;
      --accent: #2f6f73;
      --accent-strong: #174f53;
      --soft: #e8f1ef;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      min-height: 100vh;
      background: var(--paper);
      color: var(--ink);
      letter-spacing: 0;
    }

    a {
      color: inherit;
      text-decoration: none;
    }

    .site {
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }

    header {
      width: min(1080px, calc(100% - 40px));
      margin: 0 auto;
      padding: 28px 0 18px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid var(--line);
    }

    .mark {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      font-weight: 650;
      font-size: 15px;
    }

    .mark::before {
      content: "";
      width: 14px;
      height: 14px;
      border: 2px solid var(--accent-strong);
      border-radius: 3px;
      box-shadow: 5px 5px 0 var(--soft);
    }

    nav {
      display: flex;
      align-items: center;
      gap: 18px;
      color: var(--muted);
      font-size: 14px;
    }

    nav a {
      padding: 6px 0;
      border-bottom: 1px solid transparent;
    }

    nav a:hover {
      color: var(--ink);
      border-bottom-color: var(--accent);
    }

    main {
      width: min(1080px, calc(100% - 40px));
      margin: 0 auto;
      flex: 1;
      padding: 80px 0 64px;
    }

    .intro {
      max-width: 780px;
    }

    .eyebrow {
      margin: 0 0 18px;
      color: var(--accent-strong);
      font-size: 13px;
      font-weight: 700;
      text-transform: uppercase;
    }

    h1 {
      margin: 0;
      max-width: 880px;
      font-size: clamp(44px, 8vw, 92px);
      line-height: 0.96;
      letter-spacing: 0;
    }

    .lead {
      margin: 28px 0 0;
      max-width: 680px;
      color: var(--muted);
      font-size: clamp(18px, 2vw, 22px);
      line-height: 1.55;
    }

    .actions {
      margin-top: 36px;
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
    }

    .button {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 42px;
      padding: 0 16px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--panel);
      color: var(--ink);
      font-size: 14px;
      font-weight: 600;
    }

    .button.primary {
      border-color: var(--accent-strong);
      background: var(--accent-strong);
      color: #fff;
    }

    .grid {
      margin-top: 72px;
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 18px;
    }

    .item {
      min-height: 178px;
      padding: 24px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(255, 255, 255, 0.72);
    }

    .item h2 {
      margin: 0 0 12px;
      font-size: 18px;
      letter-spacing: 0;
    }

    .item p {
      margin: 0;
      color: var(--muted);
      line-height: 1.55;
      font-size: 15px;
    }

    .profile {
      display: grid;
      grid-template-columns: minmax(0, 1.1fr) minmax(280px, 0.9fr);
      gap: 48px;
      align-items: start;
    }

    .facts {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      padding: 24px;
    }

    .facts h2 {
      margin: 0 0 18px;
      font-size: 16px;
    }

    .fact {
      display: grid;
      grid-template-columns: 92px 1fr;
      gap: 16px;
      padding: 14px 0;
      border-top: 1px solid var(--line);
      font-size: 14px;
    }

    .fact:first-of-type {
      border-top: 0;
      padding-top: 0;
    }

    .fact span:first-child {
      color: var(--muted);
    }

    footer {
      width: min(1080px, calc(100% - 40px));
      margin: 0 auto;
      padding: 24px 0 32px;
      color: var(--muted);
      font-size: 13px;
      border-top: 1px solid var(--line);
    }

    @font-face {
      font-family: "Nunito ForgePane";
      src: url("/assets/nunito-bold.woff2") format("woff2");
      font-weight: 700;
      font-style: normal;
      font-display: swap;
    }

    .brand {
      --directory-width: 706px;
      --directory-line: #e5e5e5;
      background: #fff;
      color: #171717;
    }

    .brand .site {
      display: block;
    }

    .brand .brand-nav {
      width: min(var(--directory-width), calc(100% - 48px));
      justify-content: center;
      gap: 52px;
      padding: 34px 0 0;
      border: 0;
      color: #171717;
      font-size: 14px;
      font-weight: 600;
    }

    .brand .brand-nav a {
      padding: 5px 0;
    }

    .brand .brand-nav a:hover,
    .brand .brand-nav a:focus-visible {
      border-bottom-color: #171717;
    }

    .brand .directory-main {
      width: min(var(--directory-width), calc(100% - 48px));
      padding: 45px 0 34px;
    }

    .directory-hero {
      text-align: center;
    }

    .directory-hero h1,
    .product-entry h2 {
      font-family: "Nunito ForgePane", Inter, ui-sans-serif, system-ui, sans-serif;
      letter-spacing: -0.025em;
    }

    .directory-hero h1 {
      font-size: clamp(42px, 6vw, 55px);
      line-height: 1;
    }

    .directory-hero p {
      margin: 16px 0 0;
      color: #707070;
      font-size: 15px;
      line-height: 1.55;
    }

    .directory-links {
      margin-top: 30px;
      border-top: 1px solid var(--directory-line);
      border-bottom: 1px solid var(--directory-line);
    }

    .directory-row {
      min-height: 50px;
      display: grid;
      grid-template-columns: 95px minmax(0, 1fr) 246px 18px;
      align-items: center;
      gap: 16px;
      border-top: 1px solid var(--directory-line);
      font-size: 13px;
    }

    .directory-row:first-child {
      border-top: 0;
    }

    .directory-row strong {
      font-size: 13px;
    }

    .row-summary,
    .row-domain {
      color: #767676;
    }

    .row-domain {
      text-align: right;
    }

    .link-icon {
      width: 16px;
      height: 16px;
      display: block;
      transition: transform 160ms ease;
    }

    .directory-row:hover .link-icon,
    .directory-row:focus-visible .link-icon,
    .product-link:hover .link-icon,
    .product-link:focus-visible .link-icon {
      transform: translateX(3px);
    }

    .product-entry {
      margin-top: 55px;
    }

    .product-domain {
      margin: 0 0 10px;
      color: #737373;
      font-size: 14px;
    }

    .product-entry h2 {
      margin: 0;
      font-size: clamp(31px, 4.5vw, 39px);
      line-height: 1.05;
    }

    .product-description {
      margin: 12px 0 0;
      color: #656565;
      font-size: 15px;
      line-height: 1.55;
    }

    .product-link {
      width: fit-content;
      margin-top: 14px;
      display: inline-flex;
      align-items: center;
      gap: 9px;
      padding-bottom: 2px;
      border-bottom: 1px solid #171717;
      font-size: 14px;
      font-weight: 600;
    }

    .product-shot {
      width: 100%;
      height: auto;
      display: block;
      margin-top: 24px;
      border-radius: 2px;
    }

    .brand .directory-footer {
      width: min(var(--directory-width), calc(100% - 48px));
      margin: 0 auto;
      padding: 24px 0 34px;
      border-top-color: var(--directory-line);
      text-align: center;
    }

    .social-footer {
      display: flex;
      align-items: center;
      justify-content: center;
      flex-wrap: wrap;
      gap: 32px;
      color: #171717;
      font-size: 13px;
    }

    .directory-footer p {
      margin: 22px 0 0;
      color: #777;
    }

    @media (max-width: 760px) {
      header {
        align-items: flex-start;
        gap: 18px;
        flex-direction: column;
      }

      nav {
        width: 100%;
        justify-content: flex-start;
        overflow-x: auto;
        padding-bottom: 2px;
      }

      main {
        padding-top: 56px;
      }

      .grid,
      .profile {
        grid-template-columns: 1fr;
      }

      .grid {
        margin-top: 52px;
      }

      .fact {
        grid-template-columns: 1fr;
        gap: 4px;
      }

      .brand .brand-nav {
        width: min(var(--directory-width), calc(100% - 40px));
        flex-direction: row;
        align-items: center;
        gap: 28px;
        padding-top: 25px;
        overflow: visible;
      }

      .brand .directory-main,
      .brand .directory-footer {
        width: min(var(--directory-width), calc(100% - 40px));
      }

      .brand .directory-main {
        padding-top: 42px;
      }

      .directory-hero {
        text-align: left;
      }

      .directory-hero h1 {
        font-size: 44px;
      }

      .directory-row {
        grid-template-columns: minmax(0, 1fr) 18px;
        gap: 5px 12px;
        padding: 14px 0;
      }

      .directory-row strong {
        font-size: 15px;
      }

      .row-summary,
      .row-domain {
        grid-column: 1 / -1;
        text-align: left;
      }

      .directory-row .link-icon {
        grid-column: 2;
        grid-row: 1;
      }

      .product-entry {
        margin-top: 46px;
      }

      .product-entry h2 {
        font-size: 32px;
      }

      .product-shot {
        margin-top: 20px;
      }

      .social-footer {
        justify-content: flex-start;
        gap: 20px 26px;
      }

      .brand .directory-footer {
        text-align: left;
      }
    }
  </style>
</head>
<body class="${escapeHtml(bodyClass)}">
  <div class="site">
    ${content}
  </div>
</body>
</html>`;
}

function brandPage() {
  return shell({
    title: "ForgePane",
    description: "The map of Nalon's public work across the web.",
    bodyClass: "brand",
    content: `<nav class="brand-nav" aria-label="Primary">
  <a href="https://forgepane.com">Directory</a>
  <a href="#personal">Personal</a>
  <a href="#products">Products</a>
</nav>
<main class="directory-main">
  <section class="directory-hero">
    <h1>ForgePane</h1>
    <p>The map of Nalon's public work across the web.</p>
  </section>

  <section class="directory-links" id="personal" aria-label="Personal destinations">
    <a class="directory-row" href="https://nalon.forgepane.com">
      <strong>Nalon</strong>
      <span class="row-summary">Personal site</span>
      <span class="row-domain">nalon.forgepane.com</span>
      <img class="link-icon" src="/assets/arrow-right.svg" alt="">
    </a>
    <a class="directory-row" href="https://nalon.forgepane.com/#notes">
      <strong>Notes</strong>
      <span class="row-summary">Personal blog. Coming soon</span>
      <span class="row-domain">nalon.forgepane.com/#notes</span>
      <img class="link-icon" src="/assets/arrow-right.svg" alt="">
    </a>
    <a class="directory-row" href="https://nalon.forgepane.com/#portfolio">
      <strong>Portfolio</strong>
      <span class="row-summary">Selected work</span>
      <span class="row-domain">nalon.forgepane.com/#portfolio</span>
      <img class="link-icon" src="/assets/arrow-right.svg" alt="">
    </a>
  </section>

  <section id="products" aria-label="Products">
    <article class="product-entry">
      <p class="product-domain">metro.forgepane.com</p>
      <h2>CHINA METRO TYPING</h2>
      <p class="product-description">A typing game across real metro lines in 41 Chinese cities.</p>
      <a class="product-link" href="https://metro.forgepane.com/">
        <span>Open CHINA METRO TYPING</span>
        <img class="link-icon" src="/assets/arrow-right.svg" alt="">
      </a>
      <a href="https://metro.forgepane.com/" aria-label="Open CHINA METRO TYPING">
        <img class="product-shot" src="/assets/projects/china-metro-typing-route.webp" alt="CHINA METRO TYPING route view" width="2048" height="1024">
      </a>
    </article>

    <article class="product-entry">
      <p class="product-domain">cited-alpha.forgepane.com</p>
      <h2>Cited Alpha</h2>
      <p class="product-description">A source-backed AI workspace for financial research.</p>
      <a class="product-link" href="https://cited-alpha.forgepane.com/">
        <span>Open Cited Alpha</span>
        <img class="link-icon" src="/assets/arrow-right.svg" alt="">
      </a>
      <a href="https://cited-alpha.forgepane.com/" aria-label="Open Cited Alpha">
        <img class="product-shot" src="/assets/projects/cited-alpha-landing.webp" alt="Cited Alpha financial research landing page" width="2048" height="986" loading="lazy">
      </a>
    </article>
  </section>
</main>
<footer class="directory-footer">
  <nav class="social-footer" aria-label="Social links">
    <a href="https://github.com/NolanSoloBuilder">GitHub</a>
    <a href="https://x.com/NolanBuilder01">X</a>
    <a href="https://www.linkedin.com/in/web-xuhao/">LinkedIn</a>
    <a href="https://www.xiaohongshu.com/user/profile/676aae57000000001801c80d">Xiaohongshu</a>
  </nav>
  <p>© 2026 Nalon. All rights reserved. · forgepane.com</p>
</footer>`
  });
}

function notFoundPage() {
  return shell({
    title: "Not found",
    description: "This ForgePane hostname is not configured.",
    bodyClass: "not-found",
    content: `<header>
  <a class="mark" href="https://forgepane.com">ForgePane</a>
</header>
<main>
  <section class="intro">
    <p class="eyebrow">404</p>
    <h1>Not found</h1>
    <p class="lead">This ForgePane hostname is not configured.</p>
    <div class="actions">
      <a class="button primary" href="https://forgepane.com">Go to ForgePane</a>
    </div>
  </section>
</main>
<footer>ForgePane</footer>`
  });
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}
