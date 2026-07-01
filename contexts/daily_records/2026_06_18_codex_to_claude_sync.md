# 2026-06-18 Codex to Claude Sync

## Summary

Synced Codex local MCP and skills into Claude Code local configuration.

## Changes

- Backed up Claude global state to `/Users/xuhao/.claude.json.bak-codex-sync-20260618-174859`.
- Backed up Claude settings to `/Users/xuhao/.claude/settings.json.bak-codex-sync-20260618-174859`.
- Backed up existing Claude skills to `/Users/xuhao/.claude/backups/skills-codex-sync-20260618-174859/`.
- Copied Codex skills from `/Users/xuhao/.codex/skills/` into `/Users/xuhao/.claude/skills/` with `rsync -a`, preserving Claude-only skills.
- Merged enabled Codex MCP servers into top-level `mcpServers` in `/Users/xuhao/.claude.json`.

## MCP Servers Synced

- `context7`
- `fedith-mcp`
- `figma`
- `playwright`
- `proxyman`
- `tracking-kit`

Codex MCP servers with `enabled=false` were not enabled in Claude: `Sentry`, `ai-sdk-5-migration`, `api_docs`, `vercel-ai-docs`, `voltagent`.

Codex internal `node_repl` was skipped because it depends on the Codex app runtime.

## Verification

- `/Users/xuhao/.claude.json` and `/Users/xuhao/.claude/settings.json` both pass `python3 -m json.tool`.
- Claude skill directory now contains 39 skills: 35 Codex skills plus 4 Claude-only skills.
- No Codex skills are missing from Claude after sync.
- `claude mcp list` reached MCP health checking, but did not finish within a 20 second timeout.
