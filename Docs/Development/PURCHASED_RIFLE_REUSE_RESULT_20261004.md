# Purchased-rifle reuse result

2026-10-04. Follow the paired review plan. Read-only assessment completed using Blender 5.2.2 LTS; no adapted model created or selected.

## Finding

SP-R 208 is the best **technical donor candidate** among the five inspected collections: clear bolt/receiver/barrel shapes, useful object/material boundaries and connected source materials. It is not a ready Kar98k. Replacing the modern stock/short fore-end, removing scope/rail/cheek riser/external magazine, changing sights, stock/receiver interfaces and relevant external receiver/bolt details is **moderate adaptation**, not a texture swap. The historical geometry, final budget, assembly and gameplay compatibility remain unverified. Do not transplant the old soft Aholo receiver into this mature model or silently put a modern rifle on German NPCs.

| Inspected collection | Meshes / collection triangles | Observed mismatch / decision |
|---|---:|---|
| SP-R 208 | 15 / 32,708 | Clear bolt handle and receiver; modern furniture, scope, rail and detachable magazine. Best donor, not a cheap whole Kar98k conversion. |
| Lockwood MK2 | 15 / 32,281 | Real wood texture looks coherent, but lever loop, receiver and tube beneath barrel are not the target mechanism. Reject as whole-rifle conversion base. |
| SO-14 | 12 / 28,617 | Large external magazine, different receiver and barrel assembly; broadly traditional stock does not make it a Kar98k. Reject as small adaptation. |
| LA-B 330 | 15 / 35,542 | Modern furniture/attachments; scope parts visibly separated in delivered arrangement. Not a fully assembled acceptance capture. No advantage over SP-R. |
| EBR-14 | 13 / 34,521 | Tactical stock, pistol grip, rail/chassis and external magazine. Reject as small adaptation. |

Counts include every mesh/accessory in the collection, not an optimized export budget. No UV-missing mesh in these five collections. Source SP-R body rig `Armature.018` contains `j_bolt`, `j_trigger`, `j_safety`; separate accessory rigs target barrel/stock/magazine/scope. This supports inspecting/editing components but does not establish full operating bolt geometry or usable animation. Library contains **zero Actions**. Lockwood has `j_lever`/`j_hammer`/`j_loading_gate`, reinforcing why its mechanism is a poor donor. Existing German Soldier WWII pack's MP40 remains an inventory option only if the user chooses a different weapon role; it is an SMG, not the requested rifle. Allied M1 is protected and not a German substitute.

## Actual evidence and limits

`Tools/AssetValidation/blender_weapon_library_inspect.py`: exit 0, ten opposite-side Workbench images generated and individually inspected. Workbench selected some normal textures as display color; its purple appearance is not proof of missing albedo. `blender_purchased_rifle_pbr_review.py`: exit 0, four original-material Cycles images generated and individually inspected (SP-R/Lockwood, both sides). Source materials were not edited. They display textured stock/steel, with no visible missing-texture magenta in these four views. This is Blender-side visual evidence, not calibrated material correctness, clean topology, deformation, historical or UE acceptance. Inspection temporarily links delivered meshes; no automatic attachment fitting was performed.

Private evidence: `Assets/LocalWorking/Validation/2026-10-04-purchased-rifle-reuse/views_v1/weapon_library_inventory.json`, `pbr_v1/original_material_review.json` and 14 PNGs. Commercial pixels/binary content remain ignored LocalWorking, not Git.

Source `MW2_Guns_Asset_Library.blend`: 2,364,179,404 bytes; SHA256 `9e5e1a18b1608f2359e9087834cf553621759e22d67ca343ec5182159f4b3a11`. Measured after the first read-only inspection and again after PBR review, both matching the previous 3 October catalog. Original library was never saved or duplicated. No UE/M1/V1–V9 writer ran; their hashes were not re-audited this turn. No cloud job, spend, asset release, Catalog selection, commit/push. Both task Blender processes exited 0.

Decision: stop at assessment. Recommend a separately documented SP-R donor proof **only if moderate stock/exterior conversion is desired**: first inspect actual editable component ownership, remove accessories non-destructively in a new candidate, prove one new wooden fore-end/receiver interface and consistent whole-rifle finish before proceeding. Do not promise historical accuracy from the present review. MW2 provenance/project-use/derivative-sharing rights remain unresolved and block publication/use approval, not this local inspection. The German rifle gap remains open.
