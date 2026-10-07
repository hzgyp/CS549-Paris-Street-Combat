# Allied rifle reference study / German response proof

2026-10-03. User requests learning existing Allied gun parameters before further German refinement. V5 plan and GP001-004 read; Blender modeling skill used. No native/M1/camera/actions changed, no Unreal/Aholo, no credits, publication or commit/push. This is a completed bounded reference study, **not a completed German rifle repair**.

## Actual source / values

| Item | Read evidence | Transfer decision |
| --- | --- | --- |
| Current appearance | Native historical registry and attachment source name `Sm_M1_Garand`; related exported `SK_M1_Garand.blend` inspected | Appearance reference; not exact static topology/pivot or new runtime test |
| Size/axis | Static bounds7.4322×112.3624×20.8409cm; long+Y. Exchange same extents in meters but reversedY | Meter/cm and axis conventions; do not copy grip/pivot coordinates across exports |
| Exchange mesh | 3,586 indexed vertices /3,923 triangles, one `DiffuseUV` layer, one portable material | Clean outlines/edge structure more useful than high triangle count; not a new3,923-face Kar budget |
| Textures | Three2048² D/N/ORM source exports | PBR/normal workflow; no commercial atlas/UV transplantation or cloud upload |
| Material response | Native recorded `ColorPower=0.899999976...`, `RoughPower=1.0`; parent M_Equipment | Response controls, not semantic labels; full native master shader not re-audited |
| Wood/metal pattern | Whole ORM blue48.4%<0.1,34.7%>0.9 | Sharp low/high response useful; includes UV background, NOT mesh surface fractions |
| Rig / grip | Historical native M1 single-bone appearance, exchange currently no armature modifier; attachment source uses two grasp heading and right-anchor(-0.5,-8,0)cm | Not complete articulated bolt/clip, not a compatible Kar grasp profile. No runtime rebinding |

Kar reference remains provisional1.105m and299,479 triangles including37,690 sling faces. Triangle density itself does not repair its soft receiver/sight or mapped material ambiguity. M1 and Kar mechanisms/variant proportions remain separate.

## Controlled response test

`response_v1` renders M1 existing portable material, original Kar PBR, and Kar own atlas with per-linear-RGB color power0.9/roughness power1.0. Fixed side/top/quarter cameras and AgX/key/fill/rim settings, all9 unedited images actually inspected. Existing M1 portable normal mapping includes the DirectX-to-Blender green inversion from prior repair. This is approximate Blender appearance, not exact UE master/function parity; some steel highlights are strong in this studio preset and are not a claimed game lighting calibration.

The Kar response shifts tone slightly, with no newly painted wood patch because there is **no semantic coordinate classifier**. It does NOT resolve soft forms, material identity or mechanical joints. Mean full-image absolute RGB differences are about0.47–0.70/255 side and2.12–2.95/255 close views; these include background and are diagnostic, not perceptual quality scores. **Do not select response_v1 as a useful repair; stop the one scalar-response proof, no sweep.**

Reopened packed original/response scenes confirm exact local/world vertices, triangle indices, corner UV and both source atlas byte hashes. Source run used clean Blender5.2.2LTS and fresh input loads; no independent second source/render reproduction or GLB/native pass is claimed. Deliberately no GLB: custom power nodes require an explicit bake/export mapping and fresh-import check before a game asset can claim those colors. Native50 checks pass; final metadata verifies earlier source/asset records and M1 reference bytes.

## What changes in the modeling approach

The current M1 uses one material to represent wood and steel. Therefore splitting every substance into separate geometry is **not a necessary prerequisite for static appearance**; earlier treating it as such was too restrictive. Actual moving parts still need appropriate separable geometry/rigs when required.

Learn its method, not just two scalar values: preserve good stock silhouette; establish actual surface selection/UV boundaries; make receiver/bolt/sight manufactured edges readable; use coherent wood/steel roughness/metallic and normal detail on this rifle's own UVs. M1 semi-auto/en-bloc form cannot be transplanted into a Kar98k bolt-action model. Do not instantly reduce the cloud mesh to M1 density or reuse failed labels/cuts/hulls/cover plates. Concrete next geometry/texture adaptation remains to be planned and proved at one real joint before expansion; no whole-rifle rebuild, commercial content remap or production selection performed here.

## Durable evidence

- Source: `Tools/AssetCreation/GermanRifleAlliedReferenceV5/` (inspection, comparison, reopen audit, protection inventory, state/report).
- Private root: `Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-ally-reference-v5/`; `inspection/ally_parameters.json`, `response_v1/comparison.json`,9 PNGs,3 packed `.blend`, reopen/protection records. No GLB or accepted candidate.
- Metadata: `Assets/Integration/GERMAN_RIFLE_ALLIED_REFERENCE_INVENTORY_20261003.json`, reference-only, not Catalog/restore.
