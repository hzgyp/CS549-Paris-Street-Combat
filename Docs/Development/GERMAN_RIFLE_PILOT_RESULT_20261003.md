# German rifle pilot result — local candidate, production gate not passed

2026-10-03. [中文](GERMAN_RIFLE_PILOT_RESULT_20261003_ZH.md). Scope: German rifle only. No M1 reload, character, game map, NPC behavior, UE import, SFTP/Catalog or Git publication changes.

## Outcome

One Aholo base generation produced a recognizable Kar98k appearance. A 28,884-triangle two-part Blender candidate passes basic export checks and reproduces to identical GLB SHA. It **does not pass the complete model/visual contract**: reduction causes color/UV artifacts, handle cuts remain jagged, only the exterior handle is separated rather than the whole bolt, receiver/sights remain soft. Stop at the planned one generation / two bounded repair cap, preserve both useful base and failed adaptation evidence. Do not mark the German rifle asset gap closed or label this game-ready.

## References, billing and method

Four original photographs of the same 1943 museum specimen were inspected: opposing sides and receiver top/underside details. Photographs and caption identify CC0; credit Paris Musées / Musée de la Libération de Paris – musée du général Leclerc – musée Jean Moulin. [Museum collection2019.1.1](https://parismuseescollections.paris.fr/en/node/860143). Full three-quarter photograph was unavailable; complementary generated views check depth. Approximate overall length1.105m; missing hood/rod and replaced British Sten canvas sling are specimen-condition exceptions, not approved German loadout. No commercial intake bytes were uploaded.

Live API260 reconciled the300 gift minus two earlier20 jobs; quote20, task3919866, actual debit20, remaining240. No payment, top-up, subscription, new segmentation/articulation service or second base job. Gift expiry is not exposed by balance API. Original photos exceeded single-upload block; first client guard stopped before upload POST, then official block protocol with status-only completion queries succeeded. Keys/tokens/signed URLs/account context remain ignored private state, not this report or manifest.

Blender5.2.2 LTS. Relevant cases read: FP001 and the stopped Lux3D character pilot. The Blender modeling skill imposed actual reference/form/material/complementary-view and fresh-import review; these checks prevented confusing an attractive base image or fourteen true basic assertions with production acceptance. This trial concerns one rigid prop and does not reopen detailed-character creation.

## Recorded stages / evidence

- Reference/contract: complete with stated view/condition uncertainty; `Tools/AssetCreation/GermanRiflePilot/reference_notes.md`.
- Base incoming:17,173,888-byte GLB,299,479 triangles, one mesh/UV/material and two packed2048² images. ZIP13,923,303 bytes. Incoming SHA `a8ccfed78eed6da13de2070b86cec6bd32357218dd0c0cfb4efe6ae512387b60` unchanged.
- Incoming v1: diagonal provider pose misframed top/quarter views. Retain as diagnostic, not valid comparison. Incoming v2 aligns pose along principal axis without changing shape; reviewed sides/top/quarter show identifiable stock, slender barrel, open guard and downturned handle. This admitted bounded adaptation, not finish acceptance.
- Round1: preserve geometry/UV appearance while separating external handle, welding working-copy seam positions, decimating and setting compatible roughness0.58. Author28,897 versus exported28,884 triangles; export invalid-mesh warning was retained, not waved away.
- Round2: explicit validation before save/export removes13 duplicate body faces. Source/export now28,884 (body27,486 + handle1,398), no invalid-mesh export warning; construction validation logs its13 diagnosed duplicates, not an entirely error-free construction. GLB7,808,256 bytes, packed source .blend11,117,965 bytes. Fresh GLB14 basic checks pass: names/root, hierarchy, exact triangle parity, ≤30k, Blender mesh validity, finite coordinates/UV, scale, packed textures, materials, embedded URI closure, pivot, unchanged body, restored rest pose, unchanged input bytes. Extent approximately1.10494×0.14255×0.27155m, includes sling and display orientation; not internal engineering measurements.
- Independent clean-process reproduction of round2 produces identical GLB SHA `5ecc94326f18df9a217986dd6b1c1724e8c71e278bb3da7e541522562bab1d56`. Reproduction is not a third geometry repair.
- Final fresh views: six neutral and four PBR images opened. Matched unlit-color views show reduction artifacts even without glossy shading, supporting a color/UV-transfer fault introduced by the welded/decimated adaptation; welding versus decimation was not isolated further. Close rest/exploded views show jagged cuts and remaining handle stub; separation demonstration is **not a bolt-cycle/reload**. Welded diagnostics still flag body119 boundary/947 nonmanifold edges, handle35/38; these require actual topology review, not a closed-volume claim.
- Before/after protected43 native +7 action hashes match. All pilot Blender jobs exit0; no Unreal launched. No formal asset changed.

## Local files / review images

All binaries stay under `Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-v1/`. This is not a second usable SFTP copy. The inventory `Assets/Integration/GERMAN_RIFLE_PILOT_INVENTORY_20261003.json` lists non-secret source/artifact SHA/size, not restoration authority.

[Original GLB](../../Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-v1/incoming/kar98k-base-v1.glb) · [Base inspection .blend](../../Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-v1/evidence/incoming_v2/incoming_inspection.blend) · [Unaccepted adapted .blend](../../Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-v1/exports/reproduced_v2/Kar98k_WorldCandidate_v2.blend) · [Unaccepted adapted GLB](../../Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-v1/exports/reproduced_v2/Kar98k_WorldCandidate_v2.glb) · [Durable source](../../Tools/AssetCreation/GermanRiflePilot/adapt_rifle.py).

Base, not production-approved:

![Base three-quarter](../../Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-v1/evidence/incoming_v2/pbr_three_quarter.png)

Adaptation's visible color defects:

![Adapted right side](../../Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-v1/evidence/adapt_v2_fresh/pbr_right_side.png)

Jagged partial-handle cuts, exploded diagnostic not reload:

![Handle diagnostic](../../Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-v1/evidence/validate_v2/handle_exploded_not_reload.png)

See [GP001 analysis](../../Failures/GP001-20261003-kar98k-pilot/FAILURE_ANALYSIS.md). Before further authoring, review this case and choose a new bounded mechanism (UV-preserving adaptation/retopology or finished licensed asset), not another blind weld/decimate sweep. A high-detail static-base option changes the current reduced/moving-parts target and still needs explicit review and later UE/performance/history checks. Do not spend more gifted credits automatically.
