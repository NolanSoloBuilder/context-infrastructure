# Prototype Instructions

Run the local server yourself and open the preview in the browser available to this environment. Do not give the user server-start instructions when you can run it.

Before making substantial visual changes, use the Product Design plugin's `get-context` skill when the visual source is unclear or no longer matches the current goal. When the user gives durable prototype-specific design feedback, preferences, or decisions, record them in `AGENTS.md`.

When implementing from a selected generated mock, treat that image as the source of truth for layout, component anatomy, density, spacing, color, typography, visible content, and hierarchy.

## Durable product decisions

- This prototype is an independent product called `打字游中国`, not a mode or data layer inside the metro typing product.
- The selected visual direction is `分岔奇遇`: a full-window real satellite/terrain map with route chapters, visible event points, a vehicle, city nodes, and a persistent typing dock.
- Licensed real photography is destination content opened from the journey header. It switches with the current city and keeps its provenance visible; it must not be confused with the live basemap.
- The shipped primary experience must not present AI-generated scenery as a real location. Every displayed photo carries source, author, license, location, and review metadata.
- Typing progress drives route progress continuously. Completing a city triggers a short arrival state and advances without requiring a click.
- Route overlays must follow a stored driving-route geometry rather than drawing straight city-to-city chords over a real map.
- Reuse the metro prototype only at the neutral rendering-pattern level: separate route, progress, node-state, vehicle, and camera layers. Product entities remain road routes, cities, and journeys; do not introduce metro stations or metro data contracts.
- The map defaults to a pitched 3D terrain view. Route geometry, stateful city nodes, and the vehicle marker must remain legible above terrain and buildings, with a usable pitched-map fallback if elevation tiles fail.
- Scenic photography is keyed to the current destination, preloads the next destination, crossfades on automatic arrival, and switches its visible provenance together with the image.
- Image failure and reduced-distraction states must preserve the complete typing journey.
- Route chapters are independent road journeys. Locked chapters expose their unlock requirement; typing replaces dice as the movement mechanic.
- Fork events are deterministic and auditable: their trigger condition is visible, each choice changes explicit resources, and hidden-route conditions are shown before they resolve.
- The primary map combines EOX Copernicus Sentinel imagery, OpenFreeMap/OpenStreetMap roads and labels, Mapterhorn elevation, and stored OSRM driving geometry. Every provider remains visibly attributed, and the non-satellite terrain basemap is the network fallback.

Build app UI in `src/`. Keep `.openai/hosting.json`, `worker/index.js`, `scripts/prepare-sites-build.mjs`, and `tests/sites-worker.test.mjs` intact so the same local prototype can be handed to Sites. Before a Sites handoff, run `npm run build` and `npm run test:sites`; the build must leave `dist/client/index.html`, `dist/server/index.js`, and `dist/.openai/hosting.json`.
