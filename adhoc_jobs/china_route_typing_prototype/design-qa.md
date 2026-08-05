# Design QA

## Comparison target

- Source visual truth: `/Users/xuhao/.codex/generated_images/019fc666-9083-7cc0-9e1b-62e8d5daf8d3/exec-c0fd28b7-7fbe-4d7c-83b2-39e5bea6bd92.png`
- User revision to the source: keep the selected full-window journey but require a real map and real photography to be visible together.
- Browser-rendered implementation: `/Users/xuhao/Documents/Other/context-infrastructure/adhoc_jobs/china_route_typing_prototype/implementation-real-map-desktop.png`
- Mobile implementation evidence: `/Users/xuhao/Documents/Other/context-infrastructure/adhoc_jobs/china_route_typing_prototype/implementation-real-map-mobile.png`
- Full-view comparison: `/Users/xuhao/Documents/Other/context-infrastructure/adhoc_jobs/china_route_typing_prototype/design-comparison-final.png`
- Focused typing-dock comparison: `/Users/xuhao/Documents/Other/context-infrastructure/adhoc_jobs/china_route_typing_prototype/design-comparison-focus-dock.png`
- State: active `川南城市线` journey, destination `雅安`, sound enabled, real map collapsed, normal imagery mode.
- Browser: Codex in-app browser.

## Viewport and normalization

- Requested desktop CSS viewport: `1440 × 1024`, device scale factor `1`.
- Browser screenshot pixels: `1404 × 1024`; the in-app browser reserved 36 horizontal pixels outside the captured page content.
- Source image pixels: `1487 × 1058`.
- Full comparison normalized both images with center crop to `720 × 512`, then placed them side by side in a `1440 × 512` image.
- The focused comparison crops each bottom typing region independently and normalizes both to `720 × 220` before placing them side by side.
- Mobile responsive evidence uses `390 × 844` CSS and screenshot pixels.

## Findings

No actionable P0, P1, or P2 mismatch remains after the real-map revision.

- [P3] The real map adds a compact information surface that was absent from the original generated mock.
  - Location: upper-left scenic stage.
  - Evidence: it remains subordinate to the scenic image and typing dock at rest, but is always visible and can expand in place.
  - Reason: this is the user's explicit revision to the selected visual direction.

- [P3] Scenic image and route trace are separate generated assets rather than crops of the source mock.
  - Location: main scenic stage and route progress.
  - Evidence: both preserve the selected composition and art direction, while their mountain contour and route bends differ from the source pixels.
  - Reason: the implementation requires independently reusable assets and dynamic progress.
  - Follow-up: retain the asset contract; visual variation between route segments is a product feature rather than a fidelity defect.

## Required fidelity surfaces

- Fonts and typography: passed. The implementation uses local `Noto Sans SC` weights 400–700 and `DM Mono` weights 300–500. Chinese destination hierarchy, route metadata, pinyin tracking, active underline, weights, wrapping, and antialiasing match the source direction.
- Spacing and layout rhythm: passed. The 86 px top bar, full-bleed scenic stage, bottom overlay margins, three-column typing dock, route-to-dock gap, 16 px dock radius, and restrained elevation align with the source after iteration.
- Colors and visual tokens: passed. Warm paper, deep ink, muted gray, off-white route trace, and green progress use stable CSS tokens with sufficient foreground contrast.
- Image quality and asset fidelity: passed. The scenic asset is a `1440 × 1080` licensed photograph of the road to Bifengxia, Ya'an, with a verified checksum and CC BY-SA 3.0 attribution. The road map is live MapLibre rendering over an OpenFreeMap/OpenStreetMap basemap; its route overlay uses a stored 3,284-point driving geometry rather than a straight visual chord.
- Copy and content: passed. `川南城市线 · 成都 → 宜宾`, `1 / 4 城`, `正在前往`, `雅安`, `ya an`, and `下一城 乐山` are consistent with the displayed four-city route.

## Interaction and browser verification

- Typed `ya`; both the scenic route trace and the position dot on the real map advanced continuously.
- Typed `yaan`; the journey entered its arrival state, incremented route count from `1` to `2`, and automatically advanced from `雅安` to `乐山` without a click.
- Expanded the real map in place and confirmed the typing journey remained visible and active.
- Toggled sound from enabled to disabled and back.
- Opened the real-world image panel, enabled reduced-distraction mode, and verified `aria-pressed="true"`.
- Reset the journey with `返回` and confirmed it returned to `雅安`, `1 / 4 城`.
- Verified desktop and `390 × 844` responsive layouts in the Codex in-app browser; the mobile default keeps the map compact and the typing dock unobstructed.
- Checked browser console after the primary interaction flow: no warnings or errors.

## Comparison history

### Pass 1

- Findings: typing dock was too short, the road focal point was hidden behind the dock, and top-bar route/count placement drifted right.
- Fixes: increased dock height and column widths, regenerated the scenic asset with the road higher in frame, and repositioned route metadata to the source proportions.
- Post-fix evidence: `implementation-desktop-pass-2.png` and `design-comparison-pass-2.png`.

### Pass 2

- Finding: a straight native progress line lost the travel-map character of the source's curved route trace.
- Fix: generated a dedicated route-line raster, removed its solid background, produced light and green progress states, and bound clipping to live typing progress.
- Post-fix evidence: `implementation-desktop-pass-3.png`.

### Pass 3

- Finding: the first raster route trace rendered too thick and competed with the scenery.
- Fix: reduced its rendered height from 80 px to 40 px while preserving the route bends and vehicle marker.
- Post-fix evidence: `implementation-desktop-pass-4.png` and `design-comparison-pass-4.png`.

### Final pass

- Evidence: `implementation-desktop-final.png`, `design-comparison-final.png`, and `design-comparison-focus-dock.png`.
- Result: the final pass has no actionable P0, P1, or P2 differences.

### Real map + real photography revision

- Evidence: `implementation-real-map-desktop.png` and `implementation-real-map-mobile.png`.
- Result: real photography, real basemap, road-following route geometry, live typing position, provenance, expand/collapse, and mobile layout all passed browser verification.

## Implementation checklist

- [x] Reproduce the selected scenic-window composition.
- [x] Keep typing as the dominant interaction.
- [x] Bind character progress to the route trace and vehicle.
- [x] Advance automatically after city completion.
- [x] Add sound, imagery provenance, and reduced-distraction controls.
- [x] Preserve the journey if imagery fails.
- [x] Verify responsive mobile layout and accessible names.
- [x] Replace the primary AI concept scene with a licensed real photograph and visible provenance.
- [x] Keep a real road map visible beside the scenic view and bind its position to typing progress.
- [x] Use a stored driving-route geometry instead of straight city chords.
- [x] Pass production build and Sites packaging tests.

## Follow-up polish

- Connect the remaining route segments to a licensed image manifest.
- Add segment-specific image preloading and crossfade after at least two more approved route assets exist.

final result: passed
