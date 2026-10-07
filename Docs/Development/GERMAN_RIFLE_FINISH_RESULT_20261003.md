# Kar98k V7 result — partial improvement, not whole-rifle finish

2026-10-03. User requested continued refinement until broadly satisfactory. Plan `GERMAN_RIFLE_FINISH_V7.md` / `_ZH.md`, GP001–005 read first; GP006 now records the failed surface mechanism. Blender modeling skill influenced fixed evidence cameras, reproducible source, broad-surface first review and independent fresh import. No characters, M1/game/UE changes or additional cloud calls.

## What actually improved

Area-weighted angular-filtered seam-aware corner normals reduce fragmented highlights across wood/receiver. No weld, vertex movement, faces, UV, own packed images or materials change. V6 repaired ball shape and source sling remain. Gray before/after and matched own-atlas PBR show smoother broad surfaces. This is shading improvement only: receiver/sights/front hardware still visibly soft/melted up close, steel/wood source texture semantics ambiguous, whole bolt not articulated.

Candidate, not production-selected: `Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-finish-v7/normals_v1/Kar98k_Normals_V7.blend` and `.glb`.2 meshes,299479 triangles; provisional1.105m. Durablesource `Tools/AssetCreation/GermanRifleFinishV7/`, generation entry normals.py, fresh evidence review.py, independent audit audit.py, record record.py. Binary/evidence private, not SFTP/Catalog/automatic teammate restore.

## Stopped mechanism / technical evidence

surface_v1 manual visible-face polygons mistakenly select hidden wood (sling omitted from visibility tree), wood shoulders and insert surroundings. Only allowed correction surface_v2 includes sling and subtracts actual visible wood. Major mistakes shrink, but hardware coverage remains incomplete/jagged with uncertain fore-end area; all11 views inspected, gate fails. No actual metal PBR or profile edit. Stop this selection route, do not add contour/views or use it to darken flaws.

Clean normal rerun GLB bytes exactly reproduce SHA34368dbb3e40828fd58c07ae668585d0f63fcb081d480b927bb17b3c15185c2d. Independent audit_v3 verifies exact V6 vertex/face/cornerUV/images/materials and unchanged sling normals; raw GLB/fresh Blender triangle position/UV maxerror0. Export normal directional error≤0.00487912 degrees; fresh Blender custom-normal directional error≤0.16327650 degrees. Not bit-identical normals. Two initial stricter component-error audits failed (first Blender exit0 despite traceback, second exit1); retained in GP006. Cause of encoding difference not proven. Final stated directional tolerances0.01/0.3 degrees passed, not whole visual acceptance.

70 PNGs generated;56 unique primary images actually inspected (14 repetition images not separately reviewed). Six prior inventories269 private/39 sources,50 native/action and4 M1 references remain SHA-identical. No cloud/debit/Catalog/SFTP/UE/game/commit/push. All task automated Blender processes ended. Export multiple-image sampler warning retained; no claim that it resolves original material ambiguity.

## Decision boundary

This has not reached “broadly satisfactory whole-rifle.” Existing fused mesh cannot yet be selected safely at its wood/steel boundary. A further pass needs genuinely established local topology/material interfaces or compatible finished content, not another failed selection sweep. Proposed scope decision: permit a separately named local mechanical topology replacement (receiver/rear sight/front hardware) while leaving original input, stock/sling and game untouched, after a small connected-interface proof. No such replacement is authored/approved by this report.

See synchronized Chinese review for actual pictures and links; metadata `Assets/Integration/GERMAN_RIFLE_FINISH_INVENTORY_20261003.json` is partial/diagnostic, not a release.
