# SP-R donor adaptation V10 result

2026-10-04. Local modeling/export stages completed with Blender modeling skill; **candidate for human whole-rifle review, not selected production asset**. Follows paired V10 implementation plan; reviewed GP002/004/008 before work, new export failure GP009 retained.

## Changed whole rifle

Retained inspected mature lower receiver component, bolt/handle, trigger and barrel/muzzle from bought SP-R. Removed entire synthetic stock/shroud, scope, upper rail component, cheek riser, magazine/release; no clipping/classification of old Aholo geometry. Retained extracted UV error0; barrel taper/trigger placement are bounded candidate adaptations. New continuous shaped lower stock with receiver/barrel bedding channel, upper handguard, fitted bands, butt plate, open guard, floor plate and bevelled iron sights. Whole assembly is approximately1.1073m, centered root,24meshes24,466triangles. New packed brown oiled-wood atlas/normal/roughness and source-derived steel albedo/normal bring front/middle/rear to a consistent finish. No Allied geometry/texture copied.

Actual self-review: six initial whole gray views found oversize guard/simple sight blocks; guard reduced and bases changed to sloped bevelled forms. Initial material views showed too-light orange wood; one whole-atlas darker/lower-contrast/rougher correction retained. Final source and actual exported views have readable steel/wood boundaries, smooth continuous stock, supported gun components and no old melted sections or modern kit accessories. This is ordinary world-prop finish, not photoreal wear or a high-detail FP kit. Perceptual acceptance is user review, not these observations.

## Deliverables / verification

Private candidate `Assets/LocalWorking/Experiments/GermanRiflePilot/20261004-spr-v10/finish_v3/GermanRifle_SPR_V10.blend` (13,077,144bytes) and `.glb` (11,621,376bytes), GLB SHA256 `795967ab635064139c69a4e46ffacfce222b992e275a7ffec5043cb974642323`. Deterministic entry `Tools/AssetCreation/GermanRifleSPR_v10/main.py`, source diagnosis/audit and reference/work-state notes alongside it. Non-secret draft inventory `Assets/Integration/GERMAN_RIFLE_SPR_DRAFT_INVENTORY_20261004.json` is not SFTP/Catalog/teammate restore authority.

`finish_v3`/`audit_v2` exit0. New authored solids: no <1e-12m² triangles, no open/overfull position-welded edges; this is a diagnostic, not global Boolean/self-intersection proof. Donor geometry is separately reported, not asserted all watertight. Fresh import preserves24names and triangle count, position max0m, UV max5.96e-8, normal max0.0411594deg, bounds1.107304×.079198×.183007m. All12 embedded images have pixels; no external image URIs, no Action. Normal shape/color transitions and interfaces inspected in12 source +12 fresh imported gray/PBR views, all individually opened. Initial8 source-part views and6 initial gray views also inspected; early material views were partial reviews, not every old PNG.

First export `finish_v2`/`audit_v1` failed modifier triangle equality (floorplate188vs12), exit1; retained. Explicit `export_apply=True` fixes it; small library closure is reopened and saved as a normal `.blend` rather than distributing a library-only UI state. `repeat_v1` clean generator and `repeat_audit_v1` pass, including cross-export geometry/UV/normal and **identical embedded PNG bytes**. GLB whole bytes differ (repeatSHAa8cbdba7...ae5c36); ordering/encoding cause unproved. Do not claim byte-exact generation. Exact candidate identity above governs review.

Original source library hash rechecked before/after local authoring against `9e5e1a18b1608f2359e9087834cf553621759e22d67ca343ec5182159f4b3a11`, never saved/duplicated. No UE/M1/V1–V9 writer, cloud call/spend, SFTP/Catalog/release or commit/push; their old files were not re-hashed as a group this turn. All automated task Blender jobs ended. Commercial bytes/pixels remain private ignored LocalWorking.

## Remaining gates

User whole-rifle appearance review; modern donor receiver/safety/extractor differences and exact historical loadout/variant approval; MW2 project-use/derivative-sharing license confirmation; semantic complete operating bolt separation/rig/actions, weapon contact/reload, collision/LOD/runtime/UE acceptance. Bolt tube/handle are separate appearance objects, not a verified complete operating mechanism. No gameplay binding or missing-asset closure follows. Continue bounded shape/finish corrections only if review finds meaningful flaws; do not reopen Aholo failure mechanisms or spend on micro-detail.
