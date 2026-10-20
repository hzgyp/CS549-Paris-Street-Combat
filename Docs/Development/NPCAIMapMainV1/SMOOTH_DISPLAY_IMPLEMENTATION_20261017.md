# Continuous presentation of verified NPC motion

17 October 2026. User reports visibly choppy display in the integrated native map scene. Scope: measure and improve the local web simulation's rendering/transport, preserving actual 0.1s movement, 0.2s sensing, 0.5s decisions, collision/pathfinding, private memory, finite episodes, token-free local entry and platform integration. No UE or gameplay/native build, asset registration, survey continuation or publication.

Inputs: current handoff and NPC/local-access selectors, map result, exact frontend/API/engine source. Read NI003 actual-arrival failure and MI006 stale-destination/bounded-recovery failure: displayed interpolation must follow recorded swept movements, never a direct shortcut between distant half-second endpoints or invented state/arrival. Existing UI pumps one0.5s step and redraws only on response (~2Hz); it also resets the canvas backing dimensions on every draw.

## Sequence and acceptance

1. Preserve source, frontend dist, selectors and routing preimages in `tmp/npc-ai-smooth-display-20261017/work_v1`. Measure the unchanged installed page with a fresh owned headless browser, recording actual canvas paints and request timings.
2. Add opt-in bounded motion samples to step responses: starting pose plus each of at most five actual0.1s ticks. Existing frame/state/revision/idempotency semantics remain authoritative. Avoid full-state copies per display sample.
3. Render those actual adjacent movement samples with requestAnimationFrame independently of React's half-second inspector/transport cadence. Interpolate headings by the shortest angle. Buffer only recorded samples, clamp when data is late, and never extrapolate. Resize the backing canvas only when actual dimensions change. Stop/review/placement/reset/navigation cancels presentation; commands remain serialized with CAS and CSRF.
4. Early checks: optional sample capture does not change final world state; every captured segment passes swept collision; a rendered corner follows both recorded segments; bounded playback handles late data, speed, pause/reset and heading wrap. Run retained world/API/raster/auth checks, TypeScript and a local Vite build. No UE build.
5. Inspect the exact owned idle loopback service and current jobs/index before installation. Preserve latest database/Catalog/index and access mode. Install only the web bundle/backend, restart only that owner if necessary, verify fresh plain entry, continuous paints, actual behavior, single step, pause/review/reset/navigation, input after pause, finite playback and existing library.
6. Pin actual source/evidence and update only the current NPC selector/routing and targeted README/result after passing gates. Report local paint cadence and measured request/draw timings, not an unmeasured guarantee for every machine.

## Storage, stopping and rollback

New source is confined to the NPC web/simulation lane; private traces/screenshots/preimages stay in the new tmp directory. Retain baseline and failed measurements. Stop on changed simulation results, interpolated wall crossing, uncontrolled backlog, stale command mutation, owner ambiguity or unintended protected-byte changes. Restore only exact patch/preimages after checking concurrent edits; do not roll back the live index/Catalog or other sessions. Human design acceptance and future UE integration remain separate.
