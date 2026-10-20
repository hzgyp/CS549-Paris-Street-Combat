# Paris raster as the native NPC simulation scene

17 October 2026. Authorized scope: use the existing black/white Paris survey as the main scene in Asset Workbench, freely place the player/two Allies/three Germans and inspect following, support and finite last-seen search. No UE, native content, gameplay build, save, survey continuation, publication or coursework delivery.

## Inputs and failure cases

Current entry: CURRENT_NPC_AI_INTERACTIVE.json / NPCAILiveV1 result. Original NPCAIV2 oracle and synthetic exercise remain retained. Exact raster authority: complete_v3/figures_v1/FIGURE_AUDIT.json, independently audited dimensions720x960, cell0.25m, UE bounds[-4,176,-236,4]. Bounded expanded L0 is the default. Surface ordinals are separate measurements, not floors.

Read NI003 (projection is not connectivity/actual arrival), ML020 (unknown and budget failure are not physical obstruction), MI005 (player travel does not prove squad travel), MI006 (stale goals and mismatched coordinates). Changes: explicit raster identity; separate conservative footprint mask and sight mask; bounded A* with complete/invalid/unreachable/budget outcomes; actual swept movement and per-unit arrivals; no omniscient enemy fallback. Black pixels, including unknown, are blocked **by this 2D design policy**, not asserted to be real UE walls. No raster modification or survey resumption.

## Implementation sequence and gates

1. Snapshot changed source/selector/handoff preimages in tmp/npc-ai-map-main-20261017/work_v1; preserve unrelated work. Pin original policy/config, survey and Catalog hashes.
2. Add a read-only, audited raster adapter. Coordinates are local metres: x=UE-x+4, y=4-UE-y. White pixels admit sight; a conservative0.5m erosion admits character centres. A*8-neighbour routing forbids corner cuts, has12000 expansions/query and a bounded cache. Disconnected components prove only abstract-grid unreachability.
3. Derive six valid preset positions on the real raster. Keep exercise World defaults for retained tests; native API defaults to raster scenes. Persist scope/layer and headings in layout. Validate placement and heading before mutation; do not silently move invalid positions.
4. Make the opaque map the main canvas, with full-map and squad-focus views, visible paths/FOV/last-seen points, usable screen-sized markers, free placement and heading controls. Scene selection creates a fresh episode, with independent layer geometry. Retain authentication, CSRF, revision/ownership/idempotency and finite120s episodes.
5. Early gates: identity/coordinate/footprint/route checks; actual two-Allied follow/support arrival; German detection, occlusion, frozen last-seen search and return; unchanged hidden-target counterfactuals. Then TypeScript/Vite and owned headless browser checks for native route/placement/zoom/scene identity/save/restore.
6. Inspect normal platform process ownership and active jobs. Install only if the known project platform is idle; preserve its access link and index snapshot. Verify the installed native route. Update only NPC current pointers and exact NPC handoff paragraph after passing checks.

## Storage, stopping condition and rollback

New source remains under Tools/AssetWorkbench; test/evidence outputs under the new tmp work_v1 directory; dated result under this document directory. No standalone page, new engine processes, binaries, asset registration or external transfer. Stop when the native platform offers the audited main map, valid free placement and verified behaviours, or report a concrete failing gate without claiming acceptance. Human design acceptance remains pending. Rollback is restoration of the exact changed-file preimages after checking concurrent edits, followed by restoring the retained NPC selector; never blanket checkout, delete or restore other lanes.
