import { readFile } from "node:fs/promises";
import { createHash, randomBytes } from "node:crypto";
import { Client } from "/opt/homebrew/lib/node_modules/@waishnav/devspace/node_modules/@modelcontextprotocol/sdk/dist/esm/client/index.js";
import { StreamableHTTPClientTransport } from "/opt/homebrew/lib/node_modules/@waishnav/devspace/node_modules/@modelcontextprotocol/sdk/dist/esm/client/streamableHttp.js";

const baseUrl = "https://devspace.forgepane.com";
const mcpUrl = `${baseUrl}/mcp`;
const redirectUri = "http://127.0.0.1/callback";
const workspacePath = "/Users/xuhao/Documents/Other/context-infrastructure";
const markerPath = "adhoc_jobs/devspace_live_gpt_link_test/task_input.md";

function form(data) {
  return new URLSearchParams(
    Object.entries(data).filter(([, value]) => value !== undefined),
  );
}

function base64url(buffer) {
  return Buffer.from(buffer).toString("base64url");
}

async function fetchJson(url, options) {
  const response = await fetch(url, options);
  const text = await response.text();
  if (!response.ok) {
    throw new Error(`${options?.method ?? "GET"} ${url} failed ${response.status}: ${text.slice(0, 500)}`);
  }
  return text ? JSON.parse(text) : {};
}

async function getAccessToken() {
  const auth = JSON.parse(await readFile(`${process.env.HOME}/.devspace/auth.json`, "utf8"));
  const ownerToken = auth.ownerToken;
  if (!ownerToken) {
    throw new Error("Missing ownerToken in ~/.devspace/auth.json");
  }

  const metadata = await fetchJson(`${baseUrl}/.well-known/oauth-authorization-server`);
  const registered = await fetchJson(metadata.registration_endpoint, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({
      client_name: "codex-direct-devspace-mcp-test",
      redirect_uris: [redirectUri],
      token_endpoint_auth_method: "none",
      grant_types: ["authorization_code", "refresh_token"],
      response_types: ["code"],
      scope: "devspace",
    }),
  });

  const codeVerifier = base64url(randomBytes(32));
  const codeChallenge = base64url(createHash("sha256").update(codeVerifier).digest());
  const state = base64url(randomBytes(12));

  const authorizeResponse = await fetch(metadata.authorization_endpoint, {
    method: "POST",
    headers: { "content-type": "application/x-www-form-urlencoded" },
    redirect: "manual",
    body: form({
      response_type: "code",
      client_id: registered.client_id,
      redirect_uri: redirectUri,
      code_challenge: codeChallenge,
      code_challenge_method: "S256",
      scope: "devspace",
      state,
      resource: mcpUrl,
      owner_token: ownerToken,
    }),
  });

  if (authorizeResponse.status !== 302) {
    const text = await authorizeResponse.text();
    throw new Error(`authorize failed ${authorizeResponse.status}: ${text.slice(0, 500)}`);
  }

  const location = authorizeResponse.headers.get("location");
  const callbackUrl = new URL(location);
  if (callbackUrl.searchParams.get("state") !== state) {
    throw new Error("OAuth state mismatch");
  }
  const code = callbackUrl.searchParams.get("code");
  if (!code) {
    throw new Error("Missing authorization code");
  }

  return fetchJson(metadata.token_endpoint, {
    method: "POST",
    headers: { "content-type": "application/x-www-form-urlencoded" },
    body: form({
      grant_type: "authorization_code",
      client_id: registered.client_id,
      code,
      redirect_uri: redirectUri,
      code_verifier: codeVerifier,
      resource: mcpUrl,
    }),
  });
}

const tokens = await getAccessToken();
const authProvider = {
  async tokens() {
    return tokens;
  },
};

const transport = new StreamableHTTPClientTransport(new URL(mcpUrl), { authProvider });
const client = new Client({ name: "codex-direct-devspace-mcp-test", version: "1.0.0" }, { capabilities: {} });

await client.connect(transport);
const tools = await client.listTools();
const openResult = await client.callTool({
  name: "open_workspace",
  arguments: { path: workspacePath, mode: "checkout" },
});
const workspaceId = openResult.structuredContent?.workspaceId;
if (!workspaceId) {
  throw new Error(`open_workspace did not return workspaceId: ${JSON.stringify(openResult).slice(0, 1000)}`);
}

const readResult = await client.callTool({
  name: "read",
  arguments: { workspaceId, path: markerPath },
});

await transport.close();

const readText = readResult.structuredContent?.result ?? readResult.content?.map((item) => item.text).join("\n") ?? "";
const markerMatch = String(readText).match(/DEVSPACE_LIVE_GPT_LINK_2026_06_19_1703/);

console.log(JSON.stringify({
  ok: Boolean(markerMatch),
  endpoint: mcpUrl,
  toolNames: tools.tools.map((tool) => tool.name),
  workspaceId,
  readPath: markerPath,
  markerSeen: markerMatch?.[0] ?? null,
}, null, 2));
