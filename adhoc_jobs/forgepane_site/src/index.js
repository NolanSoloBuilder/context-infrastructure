const BRAND_HOSTS = new Set(["forgepane.com", "www.forgepane.com"]);
const PERSONAL_HOST = "xuhao.forgepane.com";

const SECURITY_HEADERS = {
  "content-security-policy":
    "default-src 'none'; img-src 'self' data:; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'",
  "referrer-policy": "strict-origin-when-cross-origin",
  "x-content-type-options": "nosniff",
  "x-frame-options": "DENY"
};

export default {
  async fetch(request) {
    const url = new URL(request.url);

    if (url.hostname === "www.forgepane.com") {
      url.hostname = "forgepane.com";
      return Response.redirect(url.toString(), 301);
    }

    if (url.hostname === PERSONAL_HOST) {
      return html(personalPage(), 200);
    }

    if (BRAND_HOSTS.has(url.hostname)) {
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
    description: "A personal lab for Mac tools, AI workflows, and local-first experiments.",
    bodyClass: "brand",
    content: `<header>
  <a class="mark" href="https://forgepane.com">ForgePane</a>
  <nav aria-label="Primary">
    <a href="https://xuhao.forgepane.com">Xuhao</a>
    <a href="https://forgepane.com/#labs">Labs</a>
    <a href="https://forgepane.com/#devspace">DevSpace</a>
  </nav>
</header>
<main>
  <section class="intro">
    <p class="eyebrow">Personal lab</p>
    <h1>ForgePane</h1>
    <p class="lead">A personal lab for Mac tools, AI workflows, and local-first experiments.</p>
    <div class="actions">
      <a class="button primary" href="https://xuhao.forgepane.com">Xuhao</a>
      <a class="button" href="#labs">Labs</a>
      <a class="button" href="#devspace">DevSpace</a>
    </div>
  </section>
  <section class="grid" id="labs" aria-label="Focus areas">
    <article class="item">
      <h2>Mac tools</h2>
      <p>Small utilities, interface experiments, and local-first workflows for daily work.</p>
    </article>
    <article class="item">
      <h2>AI workflows</h2>
      <p>Agent patterns, context systems, and practical automation around real projects.</p>
    </article>
    <article class="item" id="devspace">
      <h2>DevSpace</h2>
      <p>A private MCP workspace endpoint reserved for secure local development experiments.</p>
    </article>
  </section>
</main>
<footer>ForgePane · built on Cloudflare Workers</footer>`
  });
}

function personalPage() {
  return shell({
    title: "Xuhao",
    description: "Personal homepage for Xuhao.",
    bodyClass: "personal",
    content: `<header>
  <a class="mark" href="https://xuhao.forgepane.com">Xuhao</a>
  <nav aria-label="Primary">
    <a href="https://forgepane.com">ForgePane</a>
    <a href="#work">Work</a>
    <a href="#contact">Contact</a>
  </nav>
</header>
<main>
  <section class="profile">
    <div class="intro">
      <p class="eyebrow">Builder / Engineer</p>
      <h1>Xuhao</h1>
      <p class="lead">I build tools and systems around AI, software workflows, and local-first productivity. This page is the personal entry point under ForgePane.</p>
      <div class="actions" id="contact">
        <a class="button primary" href="https://github.com/WebXuHao">GitHub</a>
        <a class="button" href="https://forgepane.com">ForgePane</a>
      </div>
    </div>
    <aside class="facts" id="work" aria-label="Profile details">
      <h2>Current focus</h2>
      <div class="fact">
        <span>AI</span>
        <span>LLM agents, context infrastructure, workflow automation.</span>
      </div>
      <div class="fact">
        <span>Mac</span>
        <span>Focused desktop utilities and local development tools.</span>
      </div>
      <div class="fact">
        <span>Labs</span>
        <span>Small experiments that can become durable products.</span>
      </div>
    </aside>
  </section>
</main>
<footer>xuhao.forgepane.com · personal homepage</footer>`
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
