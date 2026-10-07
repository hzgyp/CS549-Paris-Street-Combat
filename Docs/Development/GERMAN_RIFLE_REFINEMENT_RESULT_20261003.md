# German rifle refinement V2 — partial result, not production accepted

2026-10-03. [中文](GERMAN_RIFLE_REFINEMENT_RESULT_20261003_ZH.md). Follow [implementation](GERMAN_RIFLE_REFINEMENT_V2.md); reviewed GP001/FP001 and the Blender modeling workflow. Yupu approved the original direction and local refinement, not this new result. No cloud call/debit, M1 edit, Unreal launch, SFTP/Catalog change, commit or push.

## Outcome

Named smooth exterior receiver, visible bolt/connected handle, tangent sight and front barrel/sight replace the original soft zones. Source stock appearance outside the bounded cuts is preserved without welding or decimation: 248,443 original faces retained, unchanged-corner UV error zero. However, the whole rifle **fails visual/finish acceptance**. Cut interfaces retain seams/gaps; the attempted planar closures form conspicuous fins beside the bolt and on the far-side stock. New metal has excessive white highlights and some block-like support forms. This is not a better accepted baseline than the immutable original. Stop the box-cut/convex-hull closure route; keep its results unselected as GP002 evidence.

Final export: **265,976 triangles / 46 meshes**, 15,899,872-byte GLB; editable source 15,686,768 bytes. Fresh-import bounds approximately **1.101 × 0.134 × 0.295 m** (actual validation JSON governs dimensions). The shape-length gate uses a declared4mm tolerance from1.105m; that is not historical precision. Original/replaced museum sling remains, not approved German issue. This detail master is far above the provisional30k runtime budget; no LOD or UE performance acceptance.

## Actual checks / limitations

- Blender5.2.2 LTS, factory-startup/autoexec-disabled processes. Final construction, clean export import and independent construction rerun complete. Exit0 alone was not used as acceptance: the very first setup TypeError returned0 without constructing a model and is recorded.
- Final fresh import passes13 basic gates: names, triangle parity, hierarchy, approximate length, master ceiling, finite geometry/UV, mesh data validity, UV/material/packed-image presence, source-corner UV retention, and new steel closed/outward topology on a welded **diagnostic copy**. Original retained source/cap surfaces are not certified globally watertight.
- All **19 final images** opened: ten fixed neutral views, eight PBR views and one displaced-bolt diagnostic. Early source four close views and first candidate ten views were inspected; intermediate V2 inspected five decisive views (others generated but not separately claimed reviewed). Stock gaps/fins are visible in top, side and receiver detail, so numerical passes do not approve the asset. Displacement demonstrates semantic exterior grouping only, not correct weapon operation or matched reload.
- Reproduction **does not have an identical GLB SHA**: first `6f4261db85d5f77255a18ccc3bf9c72b8a6225f68cf5511d08929249963249fd`; rerun `1fa3432f7319d6baf9550e9059a2c5fe0f4fd032cccd376eaf784d9e4d5cc348`. Read-only comparison finds identical JSON/authored metrics but18 different buffer views (new UV/index data). Their exact nondeterministic source is unverified; do not call byte reproducibility passed. Both are preserved.
- Original GLB SHA remains `a8ccfed78eed6da13de2070b86cec6bd32357218dd0c0cfb4efe6ae512387b60`; before/after checks match all43 native and7 action drafts. Final inventory verifies the old pilot's77 private files and7 source hashes. No live billing re-query this turn; last recorded240-credit balance is historical, while this turn made zero service calls.

## Files / evidence

All binaries remain physical LocalWorking; no team release/automatic restore authority.

- [Editable local draft](../../Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-refine-v2/blender/interface_finish_v3/Kar98k_RefinedMaster_V2.blend)
- [GLB draft](../../Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-refine-v2/blender/interface_finish_v3/Kar98k_RefinedMaster_V2.glb)
- [Fresh-import review scene](../../Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-refine-v2/evidence/final_v3/Kar98k_RefinedMaster_Review.blend)
- [Durable source](../../Tools/AssetCreation/GermanRifleRefinementV2/refine_rifle.py), [fresh review](../../Tools/AssetCreation/GermanRifleRefinementV2/review_export.py), [reproduction diagnostic](../../Tools/AssetCreation/GermanRifleRefinementV2/check_reproduction.py)
- [Hash inventory](../../Assets/Integration/GERMAN_RIFLE_REFINEMENT_INVENTORY_20261003.json), [GP002 analysis](../../Failures/GP002-20261003-kar98k-interfaces/FAILURE_ANALYSIS.md)

Whole-rifle view — unaccepted draft:

![Whole unaccepted rifle](../../Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-refine-v2/evidence/final_v3/pbr_three_quarter.png)

Top view exposes the faulty stock closing sheet:

![Faulty closure](../../Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-refine-v2/evidence/final_v3/clay_receiver_top.png)

## Stages and next bounded method

Contract/reference review complete; retained primary silhouette/proportions usable as a base, but structural interfaces and surface polish failed. UV-retention checks and export diagnostics are partial technical evidence; final completion gate failed. No further geometry or cloud iteration in this work package. A future implementation must identify connected cut contours / actual material-surface boundaries before modifying stock, and prove a single small interface in graybox and PBR first. Do not use one convex hull for unrelated stock/bolt/slings crossing a plane, add another covering plate, sweep cut boxes, adopt this draft, or retouch detailed characters. Original base remains the reference; German production-asset gap stays open.
