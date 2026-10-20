# Continuous NPC display installed

17 October 2026. Native Asset Workbench `/npc-simulation` now continuously draws the actual0.1s movement segments between the existing0.5s responses. The previous canvas updated approximately twice a second. Adjacent recorded physics poses and shortest-angle heading interpolation drive requestAnimationFrame; no extrapolation or direct shortcut across a half-second path corner. Static backing dimensions are reused. Motion buffering is bounded; pause, review, reset, placement and navigation cancel presentation. Hidden pages pause, and the finite final segment drains before playback stops.

Installed measurement on this workstation, owned headless Edge,1480x1100 viewport,1x playback: **167 paints /164 moving paints** in the2.6s scenario. Median actual canvas paint interval **16.7ms**, p95 **16.9ms**, max18ms. Drawing p95 **0.4ms**; local request p95 **10.8ms**. Same long-walk baseline:6 paints /5 moving paints, median509.7ms, p95581.1ms. Raw original baseline and long-walk measurement remain retained. This is a bounded local browser observation, not every-machine/frame-rate acceptance.

## Verification and evidence

- **47 backend checks** pass, including retained31 world/API/raster cases,7 local-access cases,4 shared/public cases and5 motion-sampling cases. Sample capture leaves final AI/world state identical and checks actual adjacent swept segments.
- **6 client playback checks** pass: corner fidelity, late-data clamping, buffer continuity, reset, angle wrap, bounded buffering and chosen speed.
- TypeScript and the staged Vite build pass. The existing ModelViewer chunk-size warning remains. No UE/Game build.
- **20 installed native-platform workflow checks /81 world frames** pass, covering following, support, search/return, six placements, invalid placement, headings, zoom/pan, save/restore, timeline, navigation pause, reload, languages and asset library.
- **8 additional installed control checks** pass:4x rate, picking the rendered member, pause, authoritative manual step, review, reset, final drain at120s and no uncaught errors.
- Installed continuous paint trace: **166 poses /1986 collision checks** pass for all six displayed actor positions and adjacent segments before explicit pause. Actual painting, rather than only the browser RAF clock, is measured. No uncaught errors.

Exact private receipts: `tmp/npc-ai-smooth-display-20261017/work_v1/backend-v1.xml`, `candidate-v1-performance.json`, `installed-v1-performance.json`, `installed-v1-render-validation.json`, `installed-v1-controls.json`, `installed-functional-v1/BROWSER_RESULT.json` and `BROWSER_TRACE.json`; baseline `baseline-performance.json` and `baseline-long-performance.json`. Candidate functional/control runs also pass and remain retained. An initial client test incorrectly demanded one particular binary floating-point representation of0.5; the retained fixture failure was corrected to1e-12 tolerance without an implementation change.

## Installation and preservation

Owned idle loopback service PID51768 was replaced by PID15720 using `run.ps1 -Port 8766 -BindAddress 127.0.0.1 -NoBrowser -KeepAccessLink`. The staged candidate web bundle was copied without deleting earlier bundle assets. The latest index snapshot `42b0ad7f707740fe80217649862e5b44`, database, Catalog, JSON index and private bootstrap identity match the immediate pre-install readback. Candidate QA used a separate metadata-only copy, without live refresh. Its owned helper is stopped after verification.

[Implementation and rollback](SMOOTH_DISPLAY_IMPLEMENTATION_20261017.md); exact source/bundle pins `SOURCE_HANDOFF.json` in the same evidence directory; preimages `PREIMAGES.json`, `preimages`, `dist-before`. Original map geometry, oracle/config,0.1/0.2/0.5s simulation rules, ownership/CSRF/revisions/idempotency and token-free local entry remain. No asset registration, native/save/UE work, survey resumption, external transfer or coursework delivery. Map/UE/human-design acceptance retains the [original result's limits](RESULT_20261017.md).
