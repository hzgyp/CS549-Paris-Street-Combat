# V12 — existing M1 texture transfer result

2026-10-04. Authorized private material adaptation under `GERMAN_RIFLE_M1_TEXTURE_TRANSFER_V12_20261004.md`; used blender-modeling-workflow stages5–7. Read GP004/009 and the preceding M1/V11 comparison. Stages1–4 retain the user-approved V10 form (V11 has identical geometry). No renewed shape, character, cloud or game implementation.

## Outcome and evidence

Actual M1 D/N/ORM patches now supply wood grain, colour, scuffs and fine surface detail to a separately named V12. The whole atlas was NOT assigned to incompatible UVs. Wood/steel use the existing named materials; existing mesh UVs remain. M1-specific screws/labels/UV padding are excluded. Source AO is not carried to another shape; DirectX normal green is inverted,11px coarse XY removed, donor steel structure retained with a small fine-detail perturbation. Roughness variation is source-derived but remapped for this rifle, not exact native UE material equivalence.

Preflight_v1 seam/border crops are rejected and retained with frozen source; corrected preflight_v2 six crops inspected. Preview_v1 whole/receiver/stock inspected: genuine grain improved, excessive broad glossy wood highlight failed. One scalar roughness correction only; all six final source and six fresh GLB pictures inspected. Grain/scuffs are visibly more natural than V11; wood highlight is reduced, material separation stays correct, no obvious large UV seam or fake transferred hardware observed. This is agent assessment, **not user visual acceptance**. Some grain stretching and mirrored patch reuse remain, steel is still bright under studio lights; no claim of photorealism, exact Kar98k or native UE appearance.

Private root: `Assets/LocalWorking/Experiments/GermanRiflePilot/20261004-m1-texture-v12/`.

- Editable scene: `finish_v1/GermanRifle_M1Texture_V12.blend`,36,270,382bytes; SHA256 `a7115130c30c5d53c1631f5aac6c90d020612a934bdc0fb9e65855453f13ff66`.
- Export: `finish_v1/GermanRifle_M1Texture_V12.glb`,34,722,348bytes; SHA256 `862baf5ab6afa6f977e373d4710fce1e3bf6964e51e7e6483424f15bc9424193`.
- Final source6: `finish_v1/pbr_{right,left,quarter,top,underside,receiver}.png`.
- Actual fresh-import6: `audit_v1/fresh_pbr_{right,left,quarter,top,underside,receiver}.png` and `audit.json`.
- Matched V11/V12 contact sheet: `presentation_v1/v11_vs_v12.png`, actually inspected; uniform downscale/labels only, no crop/retouch. Both underlying sets use same fixed camera, studio lights and AgX. Not M1 native-game parity evidence.
- Source: `Tools/AssetCreation/GermanRifleM1Transfer_v12/main.py`, with V10 image/material/camera helper and V11 raw geometry fingerprint. `patches.py` preflight, `report.py` presentation/private diagnostic manifest.

## Actual tests

Blender5.2.2 LTS hash d13f752e3b9c. Preview, final, fresh audit, clean no-render rerun and repeat audit all exit0. Export includes evaluated modifiers (`export_apply=True`). Fresh checks pass:24named meshes,24,466triangles,1.107303977×0.079198018×0.183007009m,18embedded images/no external URI, no actions, clean new closed solids. Authored24 raw topology/UV/corner-normal/modifier/world-transform/parent fingerprints exact before/after; original M1 three texture PNGs and V10/V11 four assets hashes rechecked unchanged.

Authored→GLB max position0m, UV5.96046448e-8, normal0.04115932degrees. V10GLB→V12 geometry max normal0.03346810degrees (no geometry edit). Clean rerun attributes and exact18embedded PNG bytes match; **whole GLB bytes differ**, cause unproved. Do not call byte-identical or invent exporter-order explanation. Retained build/audit JSON and immutable rerun evidence provide actual values.

Exporter repeated sampler warnings remain (all new nodes use default matching samplers), World.use_nodes deprecation in existing audit helper; no task exception. Fresh visual review does not show texture loss. All task Blender jobs ended; no interactive preview started. Seven small protected inputs rechecked, not a new hash sweep of the2.2GiB library or native game group.

## Storage, stop and remaining gates

V12 commercial-derived PNG/blend/GLB remain ignored LocalWorking; no original overwrite/delete, SFTP/Catalog/allowlist/UE/game/map/reload/AI/commit/push change or cloud call/spend. `Assets/Integration/GERMAN_RIFLE_M1_TEXTURE_V12_INVENTORY_20261004.json` records98private files/6source files; diagnostic only, not production selection or teammate restore authority.

Stop this bounded material iteration and show the result. User appearance review remains; MW2 use/derivative-sharing rights still need confirmation before sharing. Historical modern receiver differences, complete operating rig/reload/weapon-specific contacts, native UE import/materials/performance and game selection are separate outstanding gates. Current texture reuse does not close the full German weapon gap or imply an authorization to publish.
