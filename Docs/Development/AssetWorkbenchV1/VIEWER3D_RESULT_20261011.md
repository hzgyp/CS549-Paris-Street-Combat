# 3D and animation result — 2026-10-11

Implemented locally across six asset entries: German soldier, Allied soldier, first-person arms, German rifle, rifle animation set and candidate pressure mine. Allied/first-person pages also offer the M1 source mesh. Six private GLBs serve these entries; the 229-entry inventory remains intact.

Controls include orbit, zoom, pan, current-pose framing, wireframe, clip selection, play/pause, seeking and 0.25–2× speed. Seven existing skeletal clips cover idle, walk, run, shot, reload, hit and death. Rifles/mine explicitly have no embedded animation. Language changes preserve the viewer; images/audio remain accessible.

These are source mesh/clip previews. **UE clothing camouflage/tint, native finger/grip overrides, weapon attachment and gameplay state transitions are not included.** Visual inspection found base-colored clothing, so the UI states this limitation and retains original UE screenshots. Original mesh, rig, weights and game files were not edited. Generated preview images are at most 1024 pixels. Existing FineWoodV15 and finish_v2 mine GLBs are served unchanged.

## Validation

- 30 backend tests passed, including authentication, path/snapshot contracts and new registered GLB, unknown ID, origin, changed hash, malformed format, external URI and resource-boundary rejection.
- Production build passed. All nine Chrome UI tests passed. Two 3D tests passed again after adding explicit right-pan and 1366-width checks. Verified rendered geometry, orbit/zoom/reset, wireframe, real animated image changes, pause, seeking, speed selection, bilingual/model switching and disposal on navigation. Existing inventory/source/version/audio tests remained passing.
- Fresh Blender 5.2.2 imports passed for all four generated models. Three rigs × seven clips × first/middle/last samples compared world-space hand/foot positions and evaluated mesh bounds. Maximum bone-position discrepancy: **0.00001008482 m**. Embedded image dimensions were also checked.
- Actual WebGL frames were inspected for soldier/arms reload and death, first-person detail layout, M1, FineWood and mine. Private evidence lives under `Assets/LocalWorking/AssetWorkbench/runs/viewer3d/` and `3d/export-v3/`. Source-input SHA-256 checks remained exact.
- No game/native assets, selectors, Catalog, saves, Git or SFTP publication were changed. This establishes browser-preview checks, not new UE acceptance.

Generated files: German 47,782,104 B (68 bones); Allied 62,558,128 B (72 bones); arms 4,477,268 B (72 bones); M1 5,032,448 B. Exact reused files: FineWood 81,346,308 B; mine 1,852,408 B.

## Retained failures and limits

MI030/MI033 and the existing character exchange workflow informed this attempt. Export-v1 read object matrices before dependency evaluation; its invalid reference positions were rejected. Export-v2 fixed matrix evaluation, then rejected Allied's approximately 23 mm existing bind-proportion difference under a 10 mm guard. Export-v3 uses explicit parent-relative bind transforms, a bounded 50 mm compatibility check and independent fresh-import position verification. Earlier reports/files remain private and unregistered.

The first verifier imported at Blender's default 24 FPS before sampling at 30 FPS, causing approximately 0.1 m timing discrepancies. Setting 30 FPS before import resolved this without relaxing deformation tolerances. Browser checks exposed and fixed residual OrbitControls damping on reset and first-person's initial static-M1 selection. Range seeking tests now use actual pointer/keyboard operations.

Warnings retained: the lazy-loaded Three.js chunk is approximately 616 kB, above Vite's default 500 kB warning; Starlette emits an httpx test-client deprecation warning. Precise UE material/grip reproduction remains future work and is explicitly excluded from current preview claims.

## Interface and storage

`private-records/models.json` records workspace-relative paths, SHA-256, versions, sources, clips and local audience. The dedicated authenticated endpoint resolves only registered IDs in a snapshot, then verifies safe Windows paths, current hashes, embedded-only GLB structure/buffer ranges and the 128 MiB cap. No generic filesystem endpoint or external URI is enabled. Three.js loads on demand and disposes GPU resources on navigation; hidden/offscreen views stop rendering/advancing animation.

Implementation: `frontend/src/ModelViewer.tsx`, `app/models.py` and the prepare/verify/register scripts under `Tools/AssetWorkbench`. Conversion refuses an existing output directory: use a fresh identity and validate before registration. Source-only clones can continue without private models. See the [Chinese result](VIEWER3D_RESULT_20261011_ZH.md) for details and [implementation](VIEWER3D_IMPLEMENTATION_20261011.md) for acceptance/stopping criteria.
