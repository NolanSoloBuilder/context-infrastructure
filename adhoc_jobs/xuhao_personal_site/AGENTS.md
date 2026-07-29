# Prototype Instructions

Run the local server yourself and open the preview in the browser available to this environment. Do not give the user server-start instructions when you can run it.

Before making substantial visual changes, use the Product Design plugin's `get-context` skill when the visual source is unclear or no longer matches the current goal. When the user gives durable prototype-specific design feedback, preferences, or decisions, record them in `AGENTS.md`.

When implementing from a selected generated mock, treat that image as the source of truth for layout, component anatomy, density, spacing, color, typography, visible content, and hierarchy.

For future URL fidelity work, download the reference page's HTML, CSS, JavaScript chunks, fonts, and visible assets before editing. Read the compiled component markup and exact responsive tokens instead of inferring details from screenshots alone. Keep the source snapshot under the workspace `tmp/` directory and cite it in `design-qa.md`.

Do not infer or author Xu Hao's personal portfolio entries. If he has not supplied a project, keep the project collection empty and render the existing section structure without placeholder copy; he will add approved content later.

Xu Hao has explicitly approved two public projects for the portfolio: `CHINA METRO TYPING` at `https://metro.forgepane.com/` and `Cited Alpha` at `https://cited-alpha.forgepane.com/`. Treat their live public metadata and product pages as the source of truth for portfolio copy and links.

The Portfolio screen is a single simulated desktop workspace. Dock applications must open, restore, or switch a window inside that desktop; they must not navigate the whole portfolio screen. Keep only the public Finder, Projects, GitHub, and Toolbox applications in the Dock. Do not add Instagram, travel, coffee, or other private-life applications unless Xu Hao explicitly reverses this decision.

Approved real projects should use image-rich presentation grounded in actual public product pages or repository-owned screenshots. Avoid reducing them to plain text cards when suitable real product imagery exists.

Xu Hao supplied the canonical portfolio screenshots on 2026-07-15. Use `china-metro-typing-route.webp` for CHINA METRO TYPING, and use `cited-alpha-landing.webp` plus `cited-alpha-cited-report.webp` for Cited Alpha. Do not substitute older captures unless he asks.

Display the two Cited Alpha screenshots vertically at full window width. Do not place them side by side; the narrower columns make the product UI unreadable.

Xu Hao has approved these public social links for the intro header: LinkedIn `https://www.linkedin.com/in/web-xuhao/` and X `https://x.com/NolanBuilder01`. Notes is an internal placeholder until he supplies a public blog URL.

Xu Hao has also approved the Xiaohongshu profile `https://www.xiaohongshu.com/user/profile/676aae57000000001801c80d` for the intro shortcuts. Use the locally stored Simple Icons Xiaohongshu mark rather than a text glyph or hotlinked asset.

Notes now uses an internal placeholder inspired by the public information structure of `https://blog.yencheng.dev/` and its article layout, without copying the reference author's content or identity. Keep the narrow white reading column, list-to-detail interaction, and explicit `Coming soon` placeholder until Xu Hao supplies real writing.

The public identity for this site is `Nalon`. Keep the intro name, profile greeting, Notes title, page metadata, avatar monogram, copyright, and production hostname aligned to that identity. The canonical production URL is `https://nalon.forgepane.com`; do not restore `xuhao.forgepane.com`, `徐昊`, `Xu Hao`, or `Nolan` as public-facing site branding unless explicitly requested.
