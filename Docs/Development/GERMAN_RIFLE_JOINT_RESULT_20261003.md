# Kar98k V6 joint repair — partial result

2026-10-03. User authorizes repair after the current Allied M1 study. Blender modeling skill and the document-first V6 plan used; GP001–004 and V5 reviewed. **An actual ball-profile repair exists; the whole rifle is not finished or production-selected.** No Unreal/M1/action/camera change, cloud call/credit debit, SFTP/Catalog publication, commit or push.

## What changed and what did not

Actual ray-picked mesh landmarks and surface shortest-edge paths establish a simple 44-edge loop. Flooding from the visible ball-front face isolates 1,918 faces, rather than classifying every substance with coordinate envelopes. Side/top/quarter/underside selection images were inspected: ball only, no wood selected. The first reverse angle was occluded; it is retained but is not backside proof.

A sphere is fitted to original interior surface samples, with the neck/interface pinned and a 5 mm geodesic transition. One coherent profile candidate moves 1,129 indexed vertices, maximum 1.14283 mm (mean 0.20635 mm), below the declared 1.5 mm limit. Rounded-profile normals are feathered into the original neck. Every original face and corner UV remains; all unselected wood/sling and boundary positions are exact. No weld, cuts, caps, hulls, replacement cover, global decimation or commercial texture remapping.

All 16 original-versus-fresh-export images were inspected: five clay and three PBR views for each. Clay side/top/underside show a smoother round outline and removal of patch-like faceting on the ball, with the original attachment preserved. Receiver/whole-rifle comparisons retain the surrounding geometry. PBR closeups also improve the ball's fragmented highlight, but original blurred/baked color patches remain. **The change is local and modest, not a claimed whole-rifle quality leap.**

The distinct handle-root interface proof failed: the path union was not a simple closed ring (675 degree-2 nodes, two degree-1 and two degree-3). Stop that joint, do not shift stations or sweep parameters. No geometry/material adaptation is applied there; original own diffuse/ORM remain on the complete rifle. See GP005. Root/cylinder/sight refinement and material semantic repair remain open; the small successful ball selection is not permission to reuse failed root/GP004 masks.

## Export / independent evidence

- Packed editable master: `Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-joint-v6/profile_v1/Kar98k_JointRepair_V6.blend`.
- Export: same directory `Kar98k_JointRepair_V6.glb`; two meshes, 261,789 rifle +37,690 sling =299,479 triangles. GLB SHA-256 `3a87eefa093ed96e11908ba1214b64689dba8830b5f27c10eeebfdd26d6913f6`.
- Fresh-import geometry/winding/corner UV match authored face-corner multiset exactly (maximum error0); finite coordinates and materials present. Both original packed atlas byte hashes match.
- Separate clean source run `profile_v1_rerun`: geometry/UV/material data match, GLB bytes also match. This is source/export reproduction, not an independent visual reviewer or PNG-byte reproducibility test.
- Independent read-only `independent_audit.json` passes. Before/after guards protect all228 prior private rifle files,29 prior sources, four M1 reference files and50 game/action native files. No runtime/gameplay validation is claimed from these hashes.
- 22 PNGs generated/inspected in this work package: one original probe, four first selection views, one supplemental underside, sixteen before/after views. Files remain ignored LocalWorking, not usable SFTP baseline/restore authority.

First script invocation failed `ModuleNotFoundError: probe` before creating output, resolved by explicit local source-directory import path. Root ring assertion fails despite Blender exit0; this is not a successful proof. Export warned multiple image nodes share one glTF texture sampler; original source maps are byte-exact and fresh images reviewed, but this is not full UE shader parity. Blender World node deprecation is retained, not an execution failure.

## Remaining gates / next bounded work

The preserved detail master is still299k triangles, not a validated game-budget asset. Full operating bolt/rig/reload, manufactured receiver/sight shape, coherent semantic PBR/normal detail, variant/loadout/sling historical approval, UE compatibility/performance and human whole-rifle acceptance remain open. Do not use a round ball or import checks to close the German weapon gap. Do not rerun the failed root rays, GP004 envelopes, GP002 cuts/hulls or cloud segmentation automatically. A next local package must separately prove actual receiver/sight boundaries or use mature compatible content. Current game and M1 reload remain untouched.

## Visual comparison (private local evidence)

Before:

![Before ball clay](../../Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-joint-v6/before_review/clay_ball_side.png)

After, freshly imported GLB:

![After ball clay](../../Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-joint-v6/fresh_review/clay_ball_side.png)

Durable sources: `Tools/AssetCreation/GermanRifleSurfaceJointV6/`; result inventory `Assets/Integration/GERMAN_RIFLE_JOINT_INVENTORY_20261003.json` is local partial-repair metadata, not Catalog or native restore authority.
