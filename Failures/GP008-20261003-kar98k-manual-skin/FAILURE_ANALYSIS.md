# GP008 — manual receiver boundary succeeds, replacement skin construction stops

2026-10-03. Related work: `Docs/Development/GERMAN_RIFLE_MANUAL_V9.md` / `_ZH.md`. User authorizes manual game-prop quality, not micro mechanics. Read GP001–007 before work. This case is the **receiver work package**, not a rejection of the successful joined-front repair or all manual modeling.

## Actual sequence

- Fixed barrel X=.480 prerequisite initially assumed one ring and exited1 before edits. Read-only diagnosis found74outer+42inner degree2 loops; a documented nested-annulus proof and paired loft pass. Real assembled gun/front gray images inspected. No root hull/cap or seam sweep. Separate gun-front deliverable retained.
- Receiver uses the same previously inspected1,884-source-face region/156-edge boundary. Explicit local XY unfolding of ten rows removes the three projection crossings; Z retained, displacement bounded3mm and coincident copies aligned. `receiver_boundary_proof.json` records the actually measured displacement/copy count. No original patch deletion occurred in any failed execution.
- `assembly_gray_v1` exits1 on Blender5.2 tessellator returning integer indices, not Vectors. API adapter implemented, source snapshot retained privately. Not a visual pass.
- `assembly_gray_v2` exits1 at new-skin edge-incidence assertion. Read-only construction diagnostic records9,790two-face edges,156boundary edges, **one four-face edge and six tiny faces**. This new exceptional edge is at approximatelyX=-.15797..-.15738, distinct from GP007's originalX≈-.1155 defect. Do not call it the original source edge.
- One documented geometry-construction correction replaces float32 builtin polygon tessellation with double-precision explicit ears and reinserts the ten purposely collinear boundary vertices. Initial triangulation incidence/area checks pass; after internal-edge subdivision the same exceptional edge/tiny-face count returns. `assembly_gray_v3` exits1 before original deletion. This implicates the subdivision construction stage, but exact Blender implementation cause is **not proved**. Old source remains untouched; no receiver blend/GLB selected.

## Decision / lesson

Stop this receiver polygon-plus-internal-edge-subdivision mechanism; do not add another contour, tolerance, cap control or subdivision sweep, overlay parts, or publish the failed skin. Successful physical boundary/unfolding is not a clean replacement surface; checking area/topology only before subdivision is insufficient. The next receiver approach must explicitly differ (e.g. manually constructed conforming surface connectivity without this subdivider, or compatible mature content), with a fresh plan and its own small joined visual gate. No approval request for micro details is warranted: the issue is essential surface construction.

The successful front uses V7 behind the fixed root, exact source vertex positions/retained UV, retained corner normals, untouched sling and independently constructed inner/outer front. It does **not** repair the receiver/rear sight or establish game-ready optimization, historical variant, first-person mechanics, runtime or production baseline. Partial gun may be delivered honestly.

## Evidence / storage

Private ignored root: `Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-manual-v9/`.

- `seam_diagnosis.json`, `seam_v1/` (empty failed proof directory).
- `assembly_gray_v1/receiver_boundary_proof.json` and `source_snapshot/receiver.py`.
- `assembly_gray_v2/receiver_boundary_proof.json`.
- `skin_diagnosis_v1/skin_construction_diagnosis.json` and source snapshot.
- `assembly_gray_v3/receiver_boundary_proof.json`, `skin_construction_diagnosis.json`.
- Source: `Tools/AssetCreation/GermanRifleManualV9/receiver.py`, `assemble.py` (stopped, do not execute as accepted asset authoring).

Exact bytes/hash records belong to `Assets/Integration/GERMAN_RIFLE_MANUAL_INVENTORY_20261003.json`. Private PNG/binary files remain in LocalWorking, not Git. No UE/game/M1 edits, cloud charges, SFTP/Catalog, commit/push. Original inventories must be reverified at handoff; preserved existence is not a substitute for that verification.
