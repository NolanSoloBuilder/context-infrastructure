# DevSpace ChatGPT Adapter

Read-only MCP adapter for ChatGPT Pro developer mode.

It exposes only:

- `search`: search text or list files under the configured workspace root.
- `fetch`: read a file snippet or list a directory by id.
- `/smoke-mcp`: a separate no-auth MCP endpoint exposing only `status`.

The adapter uses the same owner password from `~/.devspace/auth.json`, but grants only `devspace.read`.

Default runtime:

- Local MCP: `http://127.0.0.1:7677/mcp`
- Public MCP: `https://devspace-read.forgepane.com/mcp`
- Public smoke MCP: `https://devspace-read.forgepane.com/smoke-mcp`
- Root: `/Users/xuhao/Documents/Other/context-infrastructure`

The smoke endpoint is intentionally public and non-sensitive. It returns only:

```json
{
  "ok": true,
  "service": "forgepane-mcp-smoke",
  "domain": "forgepane.com"
}
```
