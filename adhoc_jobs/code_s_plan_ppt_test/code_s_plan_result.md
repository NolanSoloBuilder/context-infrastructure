# ForgePane MCP Rollout — Plan-Style Execution Brief

> Source of truth: `forgepane_mcp_plan_input.pptx` (4 slides). The PPTX was parsed
> **directly** (zip → `ppt/slides/slideN.xml`); the `.inspect.ndjson` fallback was
> cross-checked and matches the slide text exactly.
> Deck attribution line on every slide: "ForgePane local MCP rollout notes, 2026-06-19".

## Summary

The deck defines a small ForgePane MCP rollout whose purpose is to verify that a
delegated agent can turn a PPT into a plan-style execution brief. The rollout is
organized around three progressively more privileged access boundaries:

1. A **public, no-auth smoke endpoint** that must stay minimal and non-sensitive.
2. A **read-only adapter** (DevSpace Read) limited to search and fetch, gated by
   OAuth owner approval.
3. A **shell-capable DevSpace** that must sit behind strong authentication and
   limited filesystem roots.

Risk controls forbid exposing write/edit/bash tools without an explicit private
access layer, prefer server logs and visible ChatGPT tool-call rows over app chip
status text for evidence, and require recording every public hostname, LaunchAgent,
and verification command in repo docs. Acceptance hinges on a verifiable smoke
response, a complete ordered plan, and an honest final answer that surfaces
assumptions and avoids claiming unverified work.

## Assumptions

These are inferences not stated verbatim in the deck; treated as assumptions, not facts.

- "DevSpace Read" and "shell-capable DevSpace" refer to two distinct MCP server
  modes/tools of the same ForgePane MCP deployment, differentiated by capability.
- The smoke endpoint is the same surface exposed publicly under `forgepane.com`
  (the acceptance domain), reachable without authentication.
- "Limited roots" means the shell-capable DevSpace is constrained to an allow-list
  of filesystem directories rather than full-host access.
- "Private access layer" means an authentication/authorization gate (e.g. OAuth +
  owner approval) placed in front of any non-read capability.
- The agent producing this brief has no authority to actually deploy, expose
  hostnames, or run the smoke tool; this document is a plan, not a deployment record.

## Phases

Derived directly from slide 2 ("Implementation Phases"), each aligned to one
security boundary.

- **Phase 1 — Public smoke endpoint (boundary: public no-auth).** Keep the public
  smoke endpoint minimal and non-sensitive.
- **Phase 2 — Read-only adapter (boundary: read-only).** Use DevSpace Read for
  search and fetch only, with OAuth owner approval.
- **Phase 3 — Shell-capable DevSpace (boundary: shell-capable).** Keep the
  shell-capable DevSpace behind strong authentication and limited roots.

## Tasks

Each task lists **Owner / Input / Action / Output / Verification**. Tasks are
grouped by the boundary they belong to.

### Boundary A — Public no-auth smoke endpoint (Phase 1)

**Task 1 — Stand up the minimal public smoke endpoint**
- Owner: Rollout engineer
- Input: ForgePane MCP smoke service spec; acceptance contract from slide 4
  (`ok=true`, `service=forgepane-mcp-smoke`, `domain=forgepane.com`)
- Action: Deploy a public, unauthenticated smoke tool that returns only the
  fixed, non-sensitive status payload — no data access, no secrets.
- Output: A reachable public smoke endpoint under `forgepane.com`.
- Verification: Calling the smoke tool returns exactly
  `ok=true, service=forgepane-mcp-smoke, domain=forgepane.com`.

**Task 2 — Confirm the smoke surface carries nothing sensitive**
- Owner: Security reviewer
- Input: Deployed smoke endpoint from Task 1
- Action: Audit the public response and route to confirm it is minimal and
  non-sensitive, and that no write/edit/bash capability is reachable from it.
- Output: Sign-off note that the public boundary exposes only the smoke payload.
- Verification: Inspection of server logs + visible ChatGPT tool-call rows shows
  only the smoke call; no privileged tool is callable without auth.

### Boundary B — Read-only adapter / DevSpace Read (Phase 2)

**Task 3 — Enable DevSpace Read limited to search and fetch**
- Owner: Rollout engineer
- Input: DevSpace Read adapter configuration; OAuth owner-approval flow
- Action: Expose only search and fetch operations through the read-only adapter;
  ensure no write/edit/bash tool is bundled into this surface.
- Output: A read-only adapter that performs search/fetch and nothing else.
- Verification: Attempts to mutate state through the adapter are rejected; only
  search/fetch succeed, confirmed via server logs.

**Task 4 — Gate the read-only adapter behind OAuth owner approval**
- Owner: Access/identity owner
- Input: OAuth provider configuration; owner-approval policy
- Action: Require explicit owner OAuth approval before the read-only adapter can
  be used; deny access without it.
- Output: OAuth-gated read-only adapter with an approval audit trail.
- Verification: Unapproved requests are denied; approved sessions appear in the
  OAuth approval/audit log and in visible tool-call rows.

### Boundary C — Shell-capable DevSpace (Phase 3)

**Task 5 — Place shell-capable DevSpace behind strong authentication**
- Owner: Access/identity owner
- Input: Strong-auth mechanism (the explicit private access layer required by
  slide 3); shell-capable DevSpace build
- Action: Require strong authentication before any shell/bash capability is
  reachable; never expose write, edit, or bash tools on a public surface.
- Output: Shell-capable DevSpace reachable only through the private access layer.
- Verification: Without strong auth, shell/write/edit tools are not listed and
  not invocable; with auth, access is logged.

**Task 6 — Constrain shell-capable DevSpace to limited roots**
- Owner: Rollout engineer
- Input: Allow-list of permitted filesystem roots
- Action: Configure the shell-capable DevSpace so operations are confined to the
  approved roots only.
- Output: Shell DevSpace whose effective filesystem scope is the allow-list.
- Verification: Commands targeting paths outside the allow-list fail; in-scope
  commands succeed, confirmed via server logs.

### Cross-cutting

**Task 7 — Record hostnames, LaunchAgents, and verification commands in repo docs**
- Owner: Documentation owner
- Input: Public hostnames, LaunchAgent definitions, and verification commands
  produced by Tasks 1–6
- Action: Capture every public hostname, LaunchAgent, and verification command in
  repo docs so the rollout is reproducible and auditable.
- Output: Repo documentation enumerating hostnames, LaunchAgents, and commands.
- Verification: Doc review confirms each deployed surface has a matching, runnable
  verification command recorded.

## Verification

Mapped to slide 4 ("Acceptance Criteria") plus slide 3 evidence preferences.

- Smoke tool returns `ok=true, service=forgepane-mcp-smoke, domain=forgepane.com`.
- The plan lists ordered steps, owners, verification checks, and rollback notes
  (see Tasks above; rollback notes captured under Risks/Open Questions).
- Prefer **server logs** and **visible ChatGPT tool-call rows** as evidence over
  app chip status text.
- The final answer must mention assumptions (see Assumptions) and must not claim
  unverified work — this brief is a plan only; no deployment or smoke call was run.

## Risks

From slide 3 ("Risk Controls") plus boundary-specific exposure risks.

- Exposing write, edit, or bash tools without an explicit private access layer
  (highest-severity control on slide 3).
- Relying on app chip status text instead of server logs / visible tool-call rows,
  which can misreport true state.
- Failing to record public hostnames, LaunchAgents, or verification commands in
  repo docs, breaking reproducibility and auditability.
- Boundary creep: bundling mutating operations into the read-only adapter, or
  letting the shell-capable DevSpace escape its limited roots.
- Smoke endpoint inadvertently returning sensitive data or extra capabilities.

## Open Questions

Not answered by the deck; flagged for the owner.

- What concrete strong-authentication mechanism backs the "explicit private access
  layer" for the shell-capable DevSpace?
- What is the exact allow-list of "limited roots" for the shell-capable DevSpace?
- What are the rollback procedures for each phase (acceptance asks for rollback
  notes, but the deck does not specify them)?
- Which OAuth provider / owner identity drives the read-only adapter approval?
- Where in the repo should the hostname/LaunchAgent/verification-command docs live?
- Is `forgepane.com` already provisioned, and which host serves the public smoke
  endpoint?
