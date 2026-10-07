# V14 — dark coated wood, bounded implementation

2026-10-04. Authorized by the user's correction: V13 still reads as freshly
planed wood; compare the Allied M1's dark brown coated wood, not more scratches.
This new work package supersedes V13's iteration stop only for wood colour and
finish. Private modeling candidate; no UE/game/SFTP/Catalog/cloud/commit/push.

## Contract and reviewed failures

Read Failures/README, GP004 (wrong substance selection), GP009 (missing export
modifiers), V12's excessive-gloss preview and V13's weak appearance delta / mask
reload diagnosis. Change the hypothesis from mark density to intact wood's
colour and finish response. Use the three existing verified wood materials,
including end caps, NOT coordinate classifiers or new wear locations. Keep
the approved 24-part, 24,466-triangle, 1.1073 m form, geometry normals, UVs,
transforms, all steel materials and all texture normal layers unchanged.

Blender modeling skill stages 5–7 only; stages 1–4 reuse the accepted shape.
Ordinary game-prop finish, not detailed reconstruction or a low-poly request.
Target warm deep walnut with readable grain and restrained satin coating;
existing bare wear should contrast against the finish without yellow outlines.
M1 is a local appearance reference, not a certified historical coating recipe
or exact native UE shader match. No new purchase, images, cloud use or spending.

## Order and early falsifiable check

1. Read-only V13 node/pixel diagnostic. Resolve colour-space handling before
   remapping; log the starting base colour, roughness, specular and normal inputs.
2. New source/output identities under GermanRifleWoodFinish_v14 and private
   `20261004-wood-finish-v14`. Open V13 finish_v2; remap wood D/ORM only, retaining
   existing grain/wear locations, cap ownership and normal images. Moderate
   satin roughness, no uncontrolled gloss/clearcoat extension or new scratches.
3. Early whole/stock/receiver/handguard PBR plus unlit wood, same camera/light/
   exposure. Inspect: darker warm brown on broad faces, grain still readable,
   no raw pale caps, no broad plastic-white wash or black crushed wood. At most
   one diagnosed colour/response correction in a new directory; do not sweep.
4. Final six views and wood close views, GLB with applied modifiers, fresh
   import geometry/binding/embedded-image checks, unchanged nonwood and all
   normal PNG payloads, clean rerun semantic/image comparison. Whole-file byte
   equality is reported, not assumed. Fixed matched M1/V13/V14 evidence.
5. Record actual results/limitations and diagnostic hashes, show user review.

## Stop / rollback

Early evidence amendment: preview_v1's five actual pictures were inspected.
Colour succeeds unlit, but default specular plus lower roughness gives excessive
white wash in receiver/handguard. Sole causal correction reduces specular IOR
level .5→.18 and raises roughness mean ~.43→.52, keeping base colour/masks/studio.
This may export KHR_materials_specular, which must be verified in fresh import;
no clearcoat is added. Retain preview and frozen source, no further correction.

Stop if geometry, nonwood data, normal images or input hashes change, or colour
handling is unproved. If the sole appearance correction still fails, retain
evidence and explain; do not add detail or change studio lights to disguise it.
V13 is never overwritten. Rollback means keep V14 unselected, not restore game
packages. After this pass stop for appearance review. Rights/history/mechanism/
rig/actions/contact/UE/mips/performance and production selection remain open.
