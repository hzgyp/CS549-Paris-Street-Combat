# Retained gunplay workstream

These files preserve selected gunplay work from CS549-Normandy-Sim at commit `7cadd764e565c2da160c935acddd8f333ef289b5`. They are reference candidates for Paris Street Combat, not a new approved Normandy development branch.

## Contents

- `UnrealContent/`: selected player/weapon Blueprint components, combat feedback/HUD samples, input assets and prototype rifle meshes/materials, preserving their original Content-relative paths.
- `SourceAssets/`: prototype/hero rifle sources and reports. These are historical studies, not accepted final weapon models.
- `Scripts/`: selected gunplay generation/probe scripts, plus relevant helper modules. They are retained as readable implementation examples; they may depend on additional archived scripts/assets.
- `BrowserPrototype/`: the earlier complete local Three.js mockup, with its original README and library license. It depicts the old beach scene and is not a Paris demo or evidence of Unreal correctness.
- `FILE_MANIFEST.json`: every copied file's old path, new path, byte size and SHA-256.

## Reuse boundary

Potentially useful mechanisms are ammo/state guards, input handling, camera/muzzle traces, health/damage dispatch, impact feedback, HUD update patterns and restart logic. Inspect them before adapting to `/Game/ParisCombat` during later Gate 2.

The snapshot deliberately excludes the fine-character iteration tree, landing craft, water/shoreline implementation, crowd/air-traffic orchestration and old mission-map requirements. It is not guaranteed to be a self-contained Unreal migration set. Referenced old characters, materials or helpers may be absent; choose replacement dependencies rather than importing the entire old project.

No retained script was executed and no Blueprint was imported, compiled, retargeted or runtime-tested during the planning reset. Original script documentation describes its old environment and cannot override the new root AGENTS.md.
