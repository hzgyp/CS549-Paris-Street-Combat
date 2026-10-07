# German rifle — learn from the existing Allied rifle V5

2026-10-03. Yupu requests learning current Allied rifle parameters before altering the German candidate. Blender modeling skill; HANDOFF, failure index, GP001/2/3/4 and all four skill references read; dirty Git changes preserved. English synchronization of the pre-authored Chinese plan is in `_ZH.md`. Local modeling/reference only, no M1/game/camera/action/native authoring, Aholo, SFTP/Catalog, commit/push.

## Changed mechanism / contract

Current static appearance is `/Game/USParatrooper/Meshes/Weapon/Sm_M1_Garand`; existing exported `SK_M1_Garand.blend` is the related appearance exchange, not proof of identical static triangle/pivot data. Inspect its geometry/UV/PBR/normal and existing native material/dimensions/attachment records read-only. `ColorPower≈0.9`, `RoughPower=1.0` are shader response controls, NOT semantic wood/steel labels. Full native master/function wiring is not independently rechecked; portable Blender and proposed response can only be approximations.

Learn units, intentional silhouettes/edge density, texture/normal response, semantic anchors and naming. Do not transplant M1 shape, semi-auto/en-bloc mechanism, texture bytes/UV or grip coordinates to Kar98k. New approach: continuous original-atlas PBR response in shared views, no coordinate labels, cuts/caps/hulls/cover pieces, old failed mask or geometry smoothing. Mechanical articulation remains unestablished.

## Order, early gate, stopping and rollback

1. Read-only M1 appearance, native metadata, atlas channel distributions and protected hashes. Do not upload commercial assets to cloud.
2. At most one `response_v1` comparison, geometry/UV/original own atlas unchanged. Borrow response method, not Allied atlas. Compare side/top/quarter at fixed lighting with original Kar98k PBR and existing M1 portable material. Save new packed `.blend`; no claim of native shader/export parity.
3. Early visual gate: no newly painted patches, lost UV/images; actual useful surface improvement, not merely lighter color. This cannot itself fix source soft receiver, prove semantic segmentation or complete bolt articulation. If little benefit/worse, stop this one response test; no scalar sweep or restarted classifier.
4. Record actual transferable/nontransferable numbers, evidence and protection. No full production/history/UE/FPS acceptance. Another geometry/texture repair requires a concrete plan and small actual surface proof, not automatic whole-rifle reconstruction. Rollback is non-selection, never overwriting old source/drafts.

New source `Tools/AssetCreation/GermanRifleAlliedReferenceV5/`; private exclusive root `Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-ally-reference-v5/`. Preserve GP001-004 and50 native/action manifests.

## Pre-comparison inspection amendment

M1 exported appearance3,923 triangles, one material/UV; static historical length112.36cm. Native long axis+Y versus exchanged appearance reversedY: grip coordinates cannot be mixed. Historical native one-bone appearance is not a complete operating weapon. Three2048² atlases; whole ORM blue about48.4%<0.1,34.7%>0.9, but UV background means these are NOT mesh material surface shares. Prior Kar98k region samples overlap strongly across wood/metal.

Only one **render-only** response proof is authorized by this plan: M1 portable versus original Kar PBR versus Kar per-RGB linear color power0.9/roughness power1.0. Preserve original atlases/geometry/UV, no old labels. Full native material shader remains approximate; power nodes do not automatically survive glTF, so no GLB is emitted without baking/export mapping and fresh-import verification. This is a reference-study scene, not a repaired game asset. If color alone changes while soft form/texture semantics remain, report insufficient benefit and stop; actual surface selection/retopology needs its own concrete next scope.
