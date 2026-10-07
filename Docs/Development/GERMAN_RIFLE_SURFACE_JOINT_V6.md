# Kar98k actual-surface joint repair V6

2026-10-03. User authorizes a local repair after the Allied M1 reference study. This is a bounded Blender repair, not UE selection or asset publication.

## Contract and prior cases

Read GP001 (global weld/decimation and UV damage), GP002 (box cuts and convex-hull closures), GP003 (cloud part splitting only separated the sling), GP004 (coordinate envelopes mislabeled wood), and the V5 Allied reference result. Learn manufactured outlines and coherent PBR response, not M1 dimensions, mechanism, copyrighted atlas or grip transforms. Use the verified original rifle/sling GLB; preserve original wood, sling, topology and corner UVs. The provisional 1.105 m length is unchanged. Keep the detailed mesh below 350,000 triangles; no whole-model low-poly reduction.

## Different mechanism

Begin at the exposed bolt-handle ball and neck. Ray-pick actual visible mesh faces; trace a closed mesh-edge boundary around the neck from multiple surface landmarks, then flood connected faces on the ball side. UV-seam coincident vertices may share diagnostic adjacency, but do not weld the mesh. This is not a coordinate-box material classifier, cut, cap, convex hull or replacement cover. Explicit face/edge IDs and seed points are durable selection evidence. A planar cross-section may locate ray-pick landmarks, but does not classify all wood/metal by location.

Early acceptance: inspect highlighted selection and boundary from side, top and reverse quarter. It must include the ball/neck exterior without crossing into wood or the receiver. Check a closed separating boundary and source topology/UV preservation. If this cannot be demonstrated, stop this joint rather than expand envelopes. Do not repair geometry on an unproved selection.

After the proof, fit the ball's manufactured rounded profile to its actual selected vertices, pin the neck/interface and move only selected interiors. Limit displacement to 1.5 mm, retain every source face/UV and lock coincident interface points. Inspect fixed before/after clay views for improved curvature without collar ridges, pinching or detached joints. At most two explicitly documented coherent geometry candidates, not parameter sweeps. Preserve unsuccessful evidence. If the proof supports only a small joint, report that partial scope honestly; receiver, sight and full operating bolt remain open.

Use this rifle's own PBR maps elsewhere. A clearly proved metal joint can have a standard glTF-compatible blued-steel material; no procedural shader portability claims, new cloud calls or commercial texture copying. No whole-rifle texture/normal rebake without a separate documented proof.

## Storage, order and evidence

1. New deterministic sources: `Tools/AssetCreation/GermanRifleSurfaceJointV6/`. New private artifacts: `Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-joint-v6/`. Never overwrite earlier outputs or hashed sources.
2. Verify the five earlier rifle manifests and the native/action guards. Build read-only surface probe and proof views.
3. Inspect actual boundary; record accept/reject before authoring. Then generate the single bounded profile/material repair from the same original input.
4. Save packed editable `.blend`, export `.glb`, fresh import and inspect side/top/reverse/whole-rifle views. Verify finite geometry, exact topology/UV and unchanged unselected vertices. Independently rerun source and compare semantic geometry/material data; byte determinism is a separate test.
5. Record results and metadata with exact limitations. No UE, M1 edits, source actions/camera, Catalog/SFTP move, asset release, cloud spending, purchase, commit or push.

Rollback is non-selection: source input and game remain unchanged; retain all local candidates and evidence. Stop if seam proof fails, wood moves, export differs materially, or the bounded candidates fail actual visual improvement.

### Proof checkpoint before geometry

`boundary_v1b` separates 1,918 ball faces with a simple 44-edge closed path. Inspected side/top/quarter show no wood crossing; reverse quarter occludes the handle and is not proof of its backside. Supplement underside view. The first invocation failed local Python module resolution before loading/creating output; retain this diagnostic, add the explicit source-directory import path.

To avoid an artificial material change midway along one steel handle, trace a second **distinct joint** at handle-to-receiver root using the same actual edge-path method and inspect its underside/side/top. It is a semantic interface proof, not a new ball-threshold sample. If it passes, use one coherent steel material for the entire exposed handle, but retain the ball-only selection for geometry. If it fails, leave original handle material and repair only the proved ball geometry; do not expand a failed material envelope. No receiver/stock edits are added.
