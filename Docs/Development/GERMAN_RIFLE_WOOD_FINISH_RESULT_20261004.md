# V14 — dark wood / coated response result

2026-10-04. User correction authorizes colour/finish, not more scratches.
Followed the paired V14 plan and Blender modeling skill stages5–7. Read failure
index, GP004/009, V12 gloss failure and V13 result before authoring.

## Actual change and appearance

Opened protected V13 finish_v2, not the original large library. Three existing
wood materials (stock sides, handguard sides, common end faces) become independent
V14 variants. Existing grain, wear masks, UV ownership and normal images retained.
No new scratches, wear locations, geometry, metallic response or steel edits.

Verified Blender sRGB image pixels equal the stored encoded PNG bytes at the
sampled location. Decode to linear RGB, tint by [.40,.36,.28], encode back to
sRGB, save/reload/pack PNGs before rendering/export. Intact finish becomes warm
deep brown; existing masks expose lighter wood at the same locations. Stock
mean encoded RGB .207/.134/.086→.125/.069/.031. These are atlas means, not a
perceptual acceptance score or calibrated physical pigment measurement.

Early preview_v1's five actual PBR/unlit images inspected: dark colour works
unlit but lower roughness/default specular creates excessive white wash across
receiver/handguard. Preserve preview scene/GLB/textures and frozen source. One
causal finish correction only, same colour/masks/lights: wood specular IOR level
.5→.18, roughness mean ~.423→.511 (bounds .48–.65). No added clearcoat or new
normal map. Actual GLB KHR_materials_specular factor .36 and freshly imported
node .18 verified. This is an artistic portable PBR adaptation, not a physical
coating recipe or exact native UE material parity.

Final eleven source images / eight fresh pictures / matched comparison sheet
actually opened, including individual M1/V14 stock and V14 receiver. Stock and
whole weapon visibly darker/warmer than V13, retained grain and lighter worn
patches. Remaining limitations: broad pale grazing reflections at handguard,
underside and receiver-side wood, stretched/mirrored grain, weaker fine wear
than M1. It is NOT full M1-like finish approval. Stop after the sole correction;
user appearance review governs selection, no automatic third adjustment.

## Candidate and actual tests

Private root `Assets/LocalWorking/Experiments/GermanRiflePilot/20261004-wood-finish-v14/`.

- `finish_v1/GermanRifle_DarkWood_V14.blend`:93,200,590bytes,
  SHA256 `5372fa3f4d85a7ee6c15bd476daa6b6fe42efdc22bf0a5d22743e312d2a53917`.
- `finish_v1/GermanRifle_DarkWood_V14.glb`:65,642,620bytes,
  SHA256 `9ca471321bd2b684d324cd094eb50d2e3ae0b0adaf174f3ea19dd8b30b0d3c80`.
-24meshes,24,466evaluated/exported triangles;1.107303977×.079198018×
  .183007009m;14 used materials/30 primitives,36 embedded PNGs, no actions.
- All24 raw geometry/topology/UV/corner-normal/modifier/transform/parent
  fingerprints exact. Face material slot indices unchanged; only wood slot
  materials replaced. V13 scene/GLB source hashes unchanged.
- `audit_v1`:fresh load/closed new solids/attribute comparison pass, exit0;
  position0m, UV5.96046448e-8, normal0.03721044deg under5e-7m/2e-5/.5deg gates.
  V13→V14 export geometry normal max.03346810deg; no geometry edit.
- `material_audit_v1`:fresh material triangle counts/areas match;30 protected
  embedded PNG payloads exact, including all original/V13 normal maps and all
  steel images. Complete11 nonwood exported material definitions match after
  texture-index/name normalization. Six wood D/ORM images replace six old ones.
  Response extension / fresh Principled specular checked, exit0.
- `repeat_v1` clean no-render generator and `repeat_audit_v1` pass, exit0:
  attribute comparison and all36embedded PNGs equal; **whole GLB differs**,
  cause unproved. Cross-export normal max.03346810deg. Not byte-exact export.
- `comparison_v1`:read-only M1/V14 three fixed views each, exit0; all five input
  scene/GLB/atlas hashes unchanged. M1/V13/V14 sheet `presentation_v1/m1_v13_v14.png`
  uses labels/uniform resizing only, no crop/colour retouch, equal camera/light/
  scale/exposure. Source/fresh diagnostics also keep studio settings unchanged.

Blender5.2.2 LTS hash d13f752e3b9c. Existing sampler and future6.0 use_nodes
deprecation warnings retained; no build/audit exception. All task processes
ended, no interactive Blender or Unreal launched. No full old-library/native
group hash sweep claimed. Larger packed blend still includes previous retained
images; no texture-memory/draw-call optimization or redundancy deletion.

## Handoff and boundaries

Metadata diagnostic: initial inventory ignore-coverage assertion failed because
Windows text-mode stdin encoded LF as CRLF, and Git quoted trailing CR in paths.
Direct check confirmed the private-root ignore rule. Frozen inventory source
retained in diagnostic_v1; binary NUL-delimited input/output corrects the check.
This is not an asset change or a visual/export pass inferred from exit0.

Source `Tools/AssetCreation/GermanRifleWoodFinish_v14/` (main, diagnostic, material
audit, presentation, references/work_state/final_report), plus reviewed V10/V11/
V12/V13 helpers. Hash-only diagnostic inventory
`Assets/Integration/GERMAN_RIFLE_WOOD_FINISH_V14_INVENTORY_20261004.json`.
Candidate/evidence remain ignored LocalWorking, V13 untouched and V14 unselected.
No game/UE/M1 original/SFTP/Catalog/allowlist/cloud/spend/commit/push changes.
MW2 use/derivative-sharing rights, historical donor differences, complete rig/
weapon-specific actions/contact, UE import/mips/performance remain open; this
turn does not close the German weapon production gap. Manifest is not a release
or teammate restore authority.
