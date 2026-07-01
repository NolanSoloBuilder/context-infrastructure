#!/usr/bin/env node

const crypto = require("node:crypto");
const fs = require("node:fs");
const http = require("node:http");
const path = require("node:path");
const { execFile } = require("node:child_process");
const { URL, URLSearchParams } = require("node:url");

const HOST = process.env.DEVSPACE_READ_HOST || "127.0.0.1";
const PORT = Number(process.env.DEVSPACE_READ_PORT || "7677");
const ROOT = path.resolve(process.env.DEVSPACE_READ_ROOT || process.cwd());
const PUBLIC_BASE_URL = (process.env.DEVSPACE_READ_PUBLIC_BASE_URL || "https://devspace-read.forgepane.com").replace(/\/+$/, "");
const MCP_URL = `${PUBLIC_BASE_URL}/mcp`;
const WIDGET_URI = "ui://devspace-read/results.html";
const OWNER_TOKEN = JSON.parse(fs.readFileSync(path.join(process.env.HOME, ".devspace/auth.json"), "utf8")).ownerToken;

const clients = new Map();
const codes = new Map();
const tokens = new Map();
const sessions = new Set();

function logRequest(req) {
  const forwarded = req.headers["cf-connecting-ip"] || req.headers["x-forwarded-for"] || "";
  console.log(`${new Date().toISOString()} ${req.method} ${req.url} ${forwarded}`);
}

function json(res, status, body, headers = {}) {
  const payload = JSON.stringify(body);
  res.writeHead(status, {
    "content-type": "application/json; charset=utf-8",
    "content-length": Buffer.byteLength(payload),
    "access-control-allow-origin": "*",
    ...headers,
  });
  res.end(payload);
}

function text(res, status, body, headers = {}) {
  res.writeHead(status, {
    "content-type": "text/html; charset=utf-8",
    "content-length": Buffer.byteLength(body),
    ...headers,
  });
  res.end(body);
}

function token() {
  return crypto.randomBytes(32).toString("base64url");
}

function nowSeconds() {
  return Math.floor(Date.now() / 1000);
}

function safeEqual(a, b) {
  const left = Buffer.from(String(a));
  const right = Buffer.from(String(b));
  return left.length === right.length && crypto.timingSafeEqual(left, right);
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    req.on("data", (chunk) => chunks.push(chunk));
    req.on("end", () => resolve(Buffer.concat(chunks).toString("utf8")));
    req.on("error", reject);
  });
}

async function parseBody(req) {
  const raw = await readBody(req);
  const type = req.headers["content-type"] || "";
  if (type.includes("application/json")) return raw ? JSON.parse(raw) : {};
  if (type.includes("application/x-www-form-urlencoded")) return Object.fromEntries(new URLSearchParams(raw));
  return raw ? JSON.parse(raw) : {};
}

function oauthMetadata() {
  return {
    issuer: PUBLIC_BASE_URL,
    authorization_endpoint: `${PUBLIC_BASE_URL}/authorize`,
    token_endpoint: `${PUBLIC_BASE_URL}/token`,
    registration_endpoint: `${PUBLIC_BASE_URL}/register`,
    response_types_supported: ["code"],
    grant_types_supported: ["authorization_code", "refresh_token"],
    code_challenge_methods_supported: ["S256"],
    token_endpoint_auth_methods_supported: ["none"],
    scopes_supported: ["devspace.read"],
  };
}

function protectedResourceMetadata() {
  return {
    resource: MCP_URL,
    authorization_servers: [`${PUBLIC_BASE_URL}/`],
    scopes_supported: ["devspace.read"],
    resource_name: "DevSpace Read",
  };
}

function widgetResource() {
  return {
    uri: WIDGET_URI,
    mimeType: "text/html+skybridge",
    text: `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    body { margin: 0; font: 13px ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #18181b; background: #fff; }
    main { padding: 12px; }
    h2 { margin: 0 0 8px; font-size: 14px; }
    pre { margin: 0; white-space: pre-wrap; word-break: break-word; color: #3f3f46; }
  </style>
</head>
<body>
  <main>
    <h2>DevSpace Read</h2>
    <pre id="out">Read-only workspace result.</pre>
  </main>
  <script>
    function render() {
      const output = window.openai?.toolOutput || {};
      const text = output.text || (output.results || []).map((item) => item.id + " " + item.text).join("\\n") || "No result.";
      document.getElementById("out").textContent = text;
    }
    window.addEventListener("openai:set_globals", render);
    render();
  </script>
</body>
</html>`,
    _meta: {
      "openai/widgetDescription": "Shows read-only search and file snippets from the DevSpace workspace.",
      "openai/widgetPrefersBorder": true,
      "openai/widgetCSP": {
        connect_domains: [],
        resource_domains: [],
      },
      ui: {
        prefersBorder: true,
        csp: {
          connectDomains: [],
          resourceDomains: [],
        },
      },
    },
  };
}

function toolMeta(invoking, invoked, securitySchemes = [{ type: "oauth2", scopes: ["devspace.read"] }]) {
  return {
    securitySchemes,
    ui: { resourceUri: WIDGET_URI },
    "openai/outputTemplate": WIDGET_URI,
    "openai/widgetAccessible": false,
    "openai/visibility": "public",
    "openai/toolInvocation/invoking": invoking,
    "openai/toolInvocation/invoked": invoked,
  };
}

function authorizePage(params, error) {
  const hidden = Object.entries(params)
    .map(([key, value]) => `<input type="hidden" name="${escapeHtml(key)}" value="${escapeHtml(value)}" />`)
    .join("\n");
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Connect DevSpace Read</title>
  <style>
    body { margin: 0; font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #111; color: #f4f4f5; }
    main { max-width: 440px; margin: 12vh auto; padding: 28px; border: 1px solid #3f3f46; border-radius: 10px; background: #18181b; }
    label, input, button { display: block; width: 100%; box-sizing: border-box; }
    input { margin-top: 8px; padding: 12px; border-radius: 6px; border: 1px solid #52525b; background: #09090b; color: #fff; }
    button { margin-top: 16px; padding: 12px; border: 0; border-radius: 6px; background: #67e8f9; color: #111; font-weight: 700; }
    .error { padding: 10px; background: #7f1d1d; color: #fecaca; border-radius: 6px; }
    dl { padding: 14px; background: #09090b; border-radius: 6px; }
    dt { color: #a1a1aa; font-size: 12px; text-transform: uppercase; }
    dd { margin: 4px 0 10px; word-break: break-word; }
  </style>
</head>
<body>
  <main>
    <h1>Connect DevSpace Read</h1>
    <p>This grants ChatGPT read-only search and fetch access to the configured workspace root.</p>
    ${error ? `<p class="error">${escapeHtml(error)}</p>` : ""}
    <dl>
      <dt>Client</dt><dd>${escapeHtml(params.client_id || "ChatGPT")}</dd>
      <dt>Scope</dt><dd>${escapeHtml(params.scope || "devspace.read")}</dd>
      <dt>Resource</dt><dd>${escapeHtml(params.resource || MCP_URL)}</dd>
    </dl>
    <form method="post">
      ${hidden}
      <label for="owner_token">Owner password</label>
      <input id="owner_token" name="owner_token" type="password" autocomplete="current-password" autofocus required />
      <button type="submit">Authorize DevSpace Read</button>
    </form>
  </main>
</body>
</html>`;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function verifyBearer(req) {
  const auth = req.headers.authorization || "";
  const match = auth.match(/^Bearer (.+)$/i);
  if (!match) return false;
  const record = tokens.get(hash(match[1]));
  return Boolean(record && record.expiresAt > nowSeconds());
}

function hash(value) {
  return crypto.createHash("sha256").update(value).digest("base64url");
}

function resolveSafe(inputPath = ".") {
  const clean = String(inputPath || ".").replace(/^\/+/, "");
  const resolved = path.resolve(ROOT, clean);
  if (resolved !== ROOT && !resolved.startsWith(`${ROOT}${path.sep}`)) {
    throw new Error("Path is outside the configured workspace root.");
  }
  return resolved;
}

function relativeSafe(absPath) {
  return path.relative(ROOT, absPath) || ".";
}

function runRg(args, cwd = ROOT) {
  return new Promise((resolve) => {
    execFile("rg", args, { cwd, timeout: 8000, maxBuffer: 1024 * 256 }, (error, stdout, stderr) => {
      if (error && error.code !== 1) {
        resolve((stderr || error.message).trim());
        return;
      }
      resolve(stdout.trim());
    });
  });
}

async function searchWorkspace({ query, path: scope = ".", limit = 20 }) {
  const scopedRoot = resolveSafe(scope);
  const max = Math.min(Math.max(Number(limit) || 20, 1), 50);
  const trimmed = String(query || "").trim();
  let lines;
  if (trimmed) {
    const output = await runRg(["-n", "--hidden", "--glob", "!{.git,node_modules,.devspace,dist,build}/**", "--", trimmed, scopedRoot]);
    lines = output ? output.split("\n").slice(0, max) : [];
  } else {
    const output = await runRg(["--files", "--hidden", "--glob", "!{.git,node_modules,.devspace,dist,build}/**", scopedRoot]);
    lines = output ? output.split("\n").slice(0, max) : [];
  }
  const results = lines.map((line) => {
    const match = line.match(/^(.+?):(\d+):(.*)$/);
    if (match) {
      const rel = relativeSafe(path.resolve(match[1]));
      return { id: `${rel}:${match[2]}`, title: `${rel}:${match[2]}`, text: match[3].slice(0, 240) };
    }
    const rel = relativeSafe(path.resolve(line));
    return { id: rel, title: rel, text: "File in workspace" };
  });
  return {
    content: [{ type: "text", text: results.length ? results.map((item) => `${item.id} ${item.text}`).join("\n") : "No matches." }],
    structuredContent: { results },
  };
}

function parseFetchId(id) {
  const raw = String(id || ".").trim();
  const match = raw.match(/^(.*?):(\d+)$/);
  if (match) return { relPath: match[1], line: Number(match[2]) };
  return { relPath: raw, line: undefined };
}

function fetchWorkspace({ id, limit = 160 }) {
  const { relPath, line } = parseFetchId(id);
  const absPath = resolveSafe(relPath);
  const stat = fs.statSync(absPath);
  if (stat.isDirectory()) {
    const entries = fs.readdirSync(absPath, { withFileTypes: true })
      .filter((entry) => ![".git", "node_modules", ".devspace"].includes(entry.name))
      .slice(0, Math.min(Number(limit) || 80, 120))
      .map((entry) => `${entry.isDirectory() ? "dir " : "file"} ${path.posix.join(relativeSafe(absPath), entry.name)}`);
    return {
      content: [{ type: "text", text: entries.join("\n") || "Empty directory." }],
      structuredContent: { id: relativeSafe(absPath), text: entries.join("\n") },
    };
  }

  const maxLines = Math.min(Math.max(Number(limit) || 160, 1), 240);
  const allLines = fs.readFileSync(absPath, "utf8").split(/\r?\n/);
  const start = line ? Math.max(line - 40, 1) : 1;
  const selected = allLines.slice(start - 1, start - 1 + maxLines);
  const numbered = selected.map((content, index) => `${start + index}: ${content}`).join("\n");
  return {
    content: [{ type: "text", text: numbered }],
    structuredContent: { id: relativeSafe(absPath), startLine: start, text: numbered },
  };
}

function toolList() {
  return {
    tools: [
      {
        name: "search",
        title: "Search workspace",
        description: "Search filenames or text inside the configured context-infrastructure workspace. Read-only.",
        inputSchema: {
          type: "object",
          properties: {
            query: { type: "string", description: "Text to search for. Leave empty to list files." },
            path: { type: "string", description: "Optional relative directory scope." },
            limit: { type: "number", description: "Maximum results, up to 50." },
          },
          required: ["query"],
          additionalProperties: false,
        },
        securitySchemes: [{ type: "oauth2", scopes: ["devspace.read"] }],
        outputSchema: {
          type: "object",
          properties: {
            results: {
              type: "array",
              items: {
                type: "object",
                properties: {
                  id: { type: "string" },
                  title: { type: "string" },
                  text: { type: "string" },
                },
                required: ["id", "title", "text"],
                additionalProperties: false,
              },
            },
          },
          required: ["results"],
          additionalProperties: false,
        },
        annotations: { readOnlyHint: true, destructiveHint: false, openWorldHint: false },
        _meta: toolMeta("Searching workspace", "Search complete"),
      },
      {
        name: "fetch",
        title: "Fetch workspace file",
        description: "Fetch a file snippet or directory listing by id returned from search. Read-only.",
        inputSchema: {
          type: "object",
          properties: {
            id: { type: "string", description: "Relative file path, directory path, or path:line id returned by search." },
            limit: { type: "number", description: "Maximum lines or entries, up to 240." },
          },
          required: ["id"],
          additionalProperties: false,
        },
        securitySchemes: [{ type: "oauth2", scopes: ["devspace.read"] }],
        outputSchema: {
          type: "object",
          properties: {
            id: { type: "string" },
            startLine: { type: "number" },
            text: { type: "string" },
          },
          required: ["id", "text"],
          additionalProperties: false,
        },
        annotations: { readOnlyHint: true, destructiveHint: false, openWorldHint: false },
        _meta: toolMeta("Fetching file", "File fetched"),
      },
    ],
  };
}

function smokeToolList() {
  return {
    tools: [
      {
        name: "status",
        title: "Get ForgePane MCP status",
        description: "Return a public, non-sensitive health summary for this ForgePane MCP smoke server.",
        inputSchema: {
          type: "object",
          properties: {},
          additionalProperties: false,
        },
        outputSchema: {
          type: "object",
          properties: {
            ok: { type: "boolean" },
            service: { type: "string" },
            domain: { type: "string" },
          },
          required: ["ok", "service", "domain"],
          additionalProperties: false,
        },
        annotations: { readOnlyHint: true, destructiveHint: false, openWorldHint: false },
        _meta: toolMeta("Checking status", "Status checked", [{ type: "noauth" }]),
      },
    ],
  };
}

async function handleSmokeMcp(req, res) {
  const body = await parseBody(req);
  if (body.method === "initialize") {
    const sessionId = crypto.randomUUID();
    return json(res, 200, {
      jsonrpc: "2.0",
      id: body.id,
      result: {
        protocolVersion: body.params?.protocolVersion || "2025-06-18",
        capabilities: { tools: { listChanged: false }, resources: { listChanged: false } },
        serverInfo: { name: "forgepane-mcp-smoke", title: "ForgePane MCP Smoke", version: "0.1.0" },
        instructions: "Use the status tool for a public non-sensitive smoke test.",
      },
    }, { "mcp-session-id": sessionId });
  }
  if (body.method === "notifications/initialized") {
    res.writeHead(202).end();
    return;
  }
  if (body.method === "tools/list") {
    return json(res, 200, { jsonrpc: "2.0", id: body.id, result: smokeToolList() });
  }
  if (body.method === "resources/read") {
    return json(res, 200, { jsonrpc: "2.0", id: body.id, result: { contents: [widgetResource()] } });
  }
  if (body.method === "tools/call" && body.params?.name === "status") {
    return json(res, 200, {
      jsonrpc: "2.0",
      id: body.id,
      result: {
        content: [{ type: "text", text: "ForgePane MCP smoke is reachable from ChatGPT." }],
        structuredContent: { ok: true, service: "forgepane-mcp-smoke", domain: "forgepane.com" },
      },
    });
  }
  return json(res, 400, { jsonrpc: "2.0", id: body.id, error: { code: -32601, message: "Method not found" } });
}

async function handleMcp(req, res) {
  if (!verifyBearer(req)) {
    return json(res, 401, { error: "invalid_token", error_description: "Missing or invalid Authorization header" }, {
      "www-authenticate": `Bearer error="invalid_token", scope="devspace.read", resource_metadata="${PUBLIC_BASE_URL}/.well-known/oauth-protected-resource/mcp"`,
    });
  }
  const body = await parseBody(req);
  if (body.method === "initialize") {
    const sessionId = crypto.randomUUID();
    sessions.add(sessionId);
    return json(res, 200, {
      jsonrpc: "2.0",
      id: body.id,
      result: {
        protocolVersion: body.params?.protocolVersion || "2025-06-18",
        capabilities: { tools: { listChanged: false }, resources: { listChanged: false } },
        serverInfo: { name: "devspace-read", title: "DevSpace Read", version: "0.1.0" },
        instructions: "Use search first, then fetch by id. This server is read-only.",
      },
    }, { "mcp-session-id": sessionId });
  }
  if (body.method === "notifications/initialized") {
    res.writeHead(202).end();
    return;
  }
  if (body.method === "tools/list") {
    return json(res, 200, { jsonrpc: "2.0", id: body.id, result: toolList() });
  }
  if (body.method === "resources/list") {
    return json(res, 200, { jsonrpc: "2.0", id: body.id, result: { resources: [widgetResource()] } });
  }
  if (body.method === "resources/read") {
    if (body.params?.uri !== WIDGET_URI) {
      return json(res, 400, { jsonrpc: "2.0", id: body.id, error: { code: -32602, message: "Unknown resource uri" } });
    }
    return json(res, 200, { jsonrpc: "2.0", id: body.id, result: { contents: [widgetResource()] } });
  }
  if (body.method === "tools/call") {
    try {
      const name = body.params?.name;
      const args = body.params?.arguments || {};
      const result = name === "search"
        ? await searchWorkspace(args)
        : name === "fetch"
          ? fetchWorkspace(args)
          : { isError: true, content: [{ type: "text", text: `Unknown tool: ${name}` }] };
      return json(res, 200, { jsonrpc: "2.0", id: body.id, result });
    } catch (error) {
      return json(res, 200, {
        jsonrpc: "2.0",
        id: body.id,
        result: { isError: true, content: [{ type: "text", text: error instanceof Error ? error.message : String(error) }] },
      });
    }
  }
  return json(res, 400, { jsonrpc: "2.0", id: body.id, error: { code: -32601, message: "Method not found" } });
}

const server = http.createServer(async (req, res) => {
  try {
    logRequest(req);
    const url = new URL(req.url, PUBLIC_BASE_URL);
    if (req.method === "OPTIONS") {
      res.writeHead(204, {
        "access-control-allow-origin": "*",
        "access-control-allow-methods": "GET,POST,OPTIONS",
        "access-control-allow-headers": "authorization,content-type,mcp-session-id",
      }).end();
      return;
    }
    if (req.method === "GET" && url.pathname === "/healthz") return json(res, 200, { ok: true, name: "devspace-read" });
    if (req.method === "GET" && (url.pathname === "/.well-known/oauth-authorization-server" || url.pathname === "/.well-known/openid-configuration")) {
      return json(res, 200, oauthMetadata());
    }
    if (req.method === "GET" && url.pathname === "/.well-known/oauth-protected-resource/mcp") {
      return json(res, 200, protectedResourceMetadata());
    }
    if (req.method === "POST" && url.pathname === "/register") {
      const body = await parseBody(req);
      const clientId = `devspace-read-${crypto.randomUUID()}`;
      clients.set(clientId, body);
      return json(res, 201, {
        ...body,
        client_id: clientId,
        client_id_issued_at: nowSeconds(),
        token_endpoint_auth_method: "none",
      });
    }
    if (url.pathname === "/authorize") {
      const params = req.method === "GET"
        ? Object.fromEntries(url.searchParams)
        : await parseBody(req);
      if (req.method === "GET") return text(res, 200, authorizePage(params));
      if (!safeEqual(params.owner_token, OWNER_TOKEN)) return text(res, 401, authorizePage(params, "Owner password was not accepted."));
      const code = `code-${crypto.randomUUID()}`;
      codes.set(code, { clientId: params.client_id, redirectUri: params.redirect_uri, scope: params.scope || "devspace.read", expiresAt: Date.now() + 300000 });
      const redirect = new URL(params.redirect_uri);
      redirect.searchParams.set("code", code);
      if (params.state) redirect.searchParams.set("state", params.state);
      res.writeHead(302, { location: redirect.href }).end();
      return;
    }
    if (req.method === "POST" && url.pathname === "/token") {
      const body = await parseBody(req);
      const codeRecord = codes.get(body.code);
      if (!codeRecord || codeRecord.expiresAt < Date.now() || codeRecord.clientId !== body.client_id) {
        return json(res, 400, { error: "invalid_grant" });
      }
      codes.delete(body.code);
      const accessToken = token();
      tokens.set(hash(accessToken), { clientId: body.client_id, scope: codeRecord.scope, expiresAt: nowSeconds() + 3600 });
      return json(res, 200, {
        access_token: accessToken,
        token_type: "bearer",
        expires_in: 3600,
        scope: codeRecord.scope,
      });
    }
    if (req.method === "POST" && url.pathname === "/mcp") return handleMcp(req, res);
    if (req.method === "POST" && url.pathname === "/smoke-mcp") return handleSmokeMcp(req, res);
    return json(res, 404, { error: "not_found" });
  } catch (error) {
    return json(res, 500, { error: "server_error", message: error instanceof Error ? error.message : String(error) });
  }
});

server.listen(PORT, HOST, () => {
  console.log(`devspace-read listening on http://${HOST}:${PORT}/mcp`);
  console.log(`public base url: ${PUBLIC_BASE_URL}`);
  console.log(`read root: ${ROOT}`);
});
