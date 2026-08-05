# Prototype Instructions

Run the local server yourself and open the preview in the browser available to this environment. Do not give the user server-start instructions when you can run it.

Before making substantial visual changes, use the Product Design plugin's `get-context` skill when the visual source is unclear or no longer matches the current goal. When the user gives durable prototype-specific design feedback, preferences, or decisions, record them in `AGENTS.md`.

When implementing from a selected generated mock, treat that image as the source of truth for layout, component anatomy, density, spacing, color, typography, visible content, and hierarchy.

## Durable product decisions

- This prototype is an independent product called `打字游中国`, not a mode or data layer inside the metro typing product.
- The selected visual direction is the full-window scenic journey: licensed real photography supplies atmosphere while the typing dock remains the dominant interaction.
- A real road basemap and the scenic photo must remain visible together. The map is a compact navigator by default and expands in place without leaving the typing journey.
- The shipped primary experience must not present AI-generated scenery as a real location. Every displayed photo carries source, author, license, location, and review metadata.
- Typing progress drives route progress continuously. Completing a city triggers a short arrival state and advances without requiring a click.
- Route overlays must follow a stored driving-route geometry rather than drawing straight city-to-city chords over a real map.
- Image failure and reduced-distraction states must preserve the complete typing journey.

Build app UI in `src/`. Keep `.openai/hosting.json`, `worker/index.js`, `scripts/prepare-sites-build.mjs`, and `tests/sites-worker.test.mjs` intact so the same local prototype can be handed to Sites. Before a Sites handoff, run `npm run build` and `npm run test:sites`; the build must leave `dist/client/index.html`, `dist/server/index.js`, and `dist/.openai/hosting.json`.
