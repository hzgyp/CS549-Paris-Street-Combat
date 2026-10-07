# V13 — localized wood and coherent exposed-steel wear result

2026-10-04. User authorized revision2 of the paired V13 implementation plan.
Blender modeling skill stages5–7; read Failures/README, GP004 and GP009 first.
This is a private, user-review-ready ordinary-prop appearance candidate, not a
production asset, exact historical weapon, runtime pass or sharing approval.
Stages1–4 preserve the accepted V12 shape, no renewed reconstruction/cloud.

## Actual changes

Separate stock and upper-handguard2048² side texture sets retain existing M1
grain. Actual vertex/face-owned metric masks add sparse asymmetric scratches,
interrupted butt/lower/ridge wear and darker handling polish at the grip neck.
Overlapping wood caps keep original material assignments; isolation changes
the side bindings, not UVs. No new mesh/UV/sculpt/geometry-normal data.

Barrel/muzzle, exposed receiver/bolt, band outer shell, external butt-plate cap
and guard sides get separate localized D/ORM derivatives at their existing
1024² or2048×1024 resolution. Dark local oil/grime, finer bluing abrasion/scuffs
and related roughness variation, not global metallic reduction, white tube,
orange rust, bore alteration, soot or heat colour. Existing steel structural
normal images are reused exactly. Only wood normal maps gain a weak scratch
perturbation; no baked lighting or exported Pointiness dependence.

The source remains the small V12 scene, not the2.2GiB bought library or26GiB
city.24 raw geometry/topology/UV/corner-normal/modifier/hierarchy/world-transform
fingerprints match before/after. Two V12 source file hashes unchanged.

## Executed sequence and retained failures

Private root: `Assets/LocalWorking/Experiments/GermanRiflePilot/20261004-wood-wear-v13/`.

1. `preflight_v1`: actual wood side UV conflicts0 at512; caps overlap sides and
   each other. Stock cap IDs6400/6401, handguard1100/1101 retained.80 actual
   convex butt-cap adjacency edges recorded, selected lower-edge anchors used.
2. `ownership_v1`:1024 pixel test of isolated guard sides, band outer-shell
   faces58–115 and external butt-plate cap each has0 conflicts. This does not
   bless the original shared full-material UV layout.
3. `proof_v1`: small lower-butt/barrel/muzzle material proof, exit0; all8 actual
   PBR/unlit/alternate-light views inspected. `proof_mask_v2` three actual
   surface-mask views inspected; no wood/steel contamination/grid/white ring.
4. **Invalid diagnostic retained:** `proof_mask_v1` had absent unused Blender
   mask datablocks, producing black geometry; relative renderer paths resolved
   on C: while its JSON writer stayed in project. Three PNGs moved into intended
   private folder (no asset deletion); JSON already there. Absolute paths,
   explicit PNG loading and a minimum-mask assertion fixed the test. Do not
   claim v1 passed just because it exited0. Its metadata/images stay intact.
5. `finish_v1` source multiview showed insufficient new-wear contrast: selected
   bare-wood colour almost matched intact grain. Its scene/GLB/masks and frozen
   source remain. `early_export_v1` numerical pass is not appearance approval.
6. One allowed coordinated local contrast correction only: add warm raw-wood
   contrast within the same masks; strengthen existing steel dirt darkening/
   roughness. No new locations/count/lighting/shape. `finish_v2` exit0, all16
   source whole/close/unlit/alternate views actually opened.
7. `audit_v1` six actual imported GLB views and `fresh_details_v1` four imported
   stock/handguard/barrel/muzzle close views opened; both checks exit0/pass.
8. `repeat_v1` clean no-render rebuild and `repeat_audit_v1` exit0/pass. Exact36
   embedded PNG payloads match; **whole GLB differs**, cause unproved. No claim
   of byte-exact GLB reproduction or speculative exporter explanation.

## Delivered candidate and measured checks

- Scene `finish_v2/GermanRifle_CoordinatedWear_V13.blend`,77,183,277bytes,
  SHA256 `bb730a98cfe70241fb1a6af069d2366bdce69536db813aa9bbcd5634afb0f46e`.
- Export `finish_v2/GermanRifle_CoordinatedWear_V13.glb`,67,500,732bytes,
  SHA256 `76c557b3334c8b9a7ee178b33783376642b5c8a176a37e662ab7203714c00a81`.
-24 mesh names/24,466 evaluated+imported triangles,1.107303977×0.079198018×
  0.183007009m, no actions,36 embedded images/no external URI. Applied modifiers.
- Authored→imported position max0m, UV5.96046448e-8, normal0.03721044deg within
  declared tolerances (5e-7m/2e-5/0.5deg); not bit-exact exported normals.
- V12→V13 exported geometry normal max0.03539638deg. Clean cross-export max
  normal0.03346810deg; other position/UV tests pass. Source raw fingerprint exact.
-11 derivative bindings; GLB14 used materials/30 primitives (V12 had6/24).
  Fresh material names/triangle counts/per-material areas match authored data.
- All6 original normal PNG payloads still embedded byte-exact. Original
  new-blued-steel and trigger D/N/ORM outside derivative scope remain exact.
- New wood2K adds authored mark density, **not new detail in the original
  723×434 M1 grain patch**. Steel stays existing resolutions. Export grows from
  34,722,348 to67,500,732bytes; not a texture-memory/draw-call optimization pass.
- Blender5.2.2 LTS hash d13f752e3b9c. Existing exporter sampler warnings and
  future6.0 use_nodes deprecation remain, no task exception; not exact UE parity.

## Appearance assessment and stop

Agent inspection: local wear survives unlit/alternate lighting, wood grain/form
remain dominant, reverse/underside retain coherent quality and no new broad UV
white seam/substance leakage was observed. Added wear is **light**, less worn
than the Allied M1 reference. Bright studio metal reflections and stretched/
mirrored reused grain remain; don't claim full M1-level weathering or photorealism.
Ambiguous sight UV regions stay V12, not falsely certified localized aging.
User review governs whether the intensity is sufficient. No third material
correction, more microdetails or shape edits in this work package.

`comparison_v1` read-only six-view render exits0; all five M1/V13 input hashes
unchanged. `presentation_v1/m1_v12_v13.png` actually inspected, with original
stock/receiver close images checked. Labels/uniform resizing only, no retouch;
identical cameras/scale/lights/exposure, not native UE shaders. Whole-view V12→
V13 improvement is small and receiver/barrel remain visually clean under the
studio. Do not declare the intended M1-like weathering/coherent age fully met
from mask/attribute passes. Keep V13 unselected and V12 intact for user review.
Reduced contact-sheet views reviewed; actual UE runtime mip behaviour untested.
No original M1 save, game/map/rig/action/grip/AI writer, Aholo/cloud/spend,
SFTP/Catalog/allowlist/release/commit/push. Rights to MW2 project use/derivative
sharing, historical modern receiver differences, full operating rig/actions,
contacts and UE import/performance remain separate gates. Diagnostic inventory
is not Catalog selection or teammate restore authority. Retain V12 unchanged.

All task Blender processes ended; no interactive Blender launch. No auto further
iteration after the single correction. Diagnostic manifest:
`Assets/Integration/GERMAN_RIFLE_WOOD_WEAR_V13_INVENTORY_20261004.json`.

Sources/reproduction: `Tools/AssetCreation/GermanRifleWoodWear_v13/README.md`,
`main.py`, `preflight.py`, `ownership_checks.py`, `mask_review.py`,
`fresh_details.py`, `presentation.py`, `inventory.py`. See work_state for final
job/inspection status. No automated appearance iteration after this delivery.
