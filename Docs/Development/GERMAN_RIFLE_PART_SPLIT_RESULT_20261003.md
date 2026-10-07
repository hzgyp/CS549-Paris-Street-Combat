# German rifle part split — bounded result

2026-10-03. **Task succeeded; requested useful wood/metal/bolt separation failed.** No finished German weapon, game import or SFTP publication. Read implementation `GERMAN_RIFLE_AHOLO_PART_SPLIT_V3.md` and GP003; GP001/GP002 were reviewed first.

## Actual result and cost

One Aholo task3920959 on the immutable original base, not on the failed locally clipped refinements. Actual gifted-credit debit30, live240→210, no purchase. The quote endpoint returned422 `PRICING_ITEM_NOT_QUOTABLE` twice before submit; official authenticated pricing page listed30 promotional/40 original. The documented pre-submit amendment reserved40 gifted credits. No second task, regenerated gun, articulation, retopology or texture generation.

Result GLB17,191,104 bytes, SHA `78d3398820afc92314ce553afc4f1aa2528267281b644432177338bc052f4bf4`. Two meshes: `Mesh_0`261,789 triangles is still the entire rifle including wood, metal, bolt and sights; `Mesh_1`37,690 triangles is the sling. Total299,479 triangles, unchanged from original. Original size/hash remain17,173,888 / `a8ccfed78eed6da13de2070b86cec6bd32357218dd0c0cfb4efe6ae512387b60`.

Independent fresh-process full face multiset check: **all triangle world positions, winding and corner UVs exactly preserved**, not just the10,000-point sample. Packed two2048² images also have identical SHA. Internal mesh-data diagnostics do not change either mesh. This is preservation evidence, not good segmentation, mechanical articulation, smoothing, material-node equivalence, watertightness, history or runtime acceptance. No softened geometry was repaired. PCA-scaled display remains1.105m, not a calibrated mechanical measurement.

15 images actually inspected: six clay fixed whole views, four PBR views, three assembled colored-part views, two isolated parts. The images prove only rifle-vs-sling separation; no wood/receiver/bolt split. Original museum replacement sling and soft front/receiver remain. The early useful-separation gate fails, so stop this one-task route rather than purchase/rerun.

## Evidence and artifacts (private LocalWorking)

Root: `Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-parts-v3/`.

- GLB: `incoming/kar98k-parts-v3-0-recovery.glb`.
- Self-contained Blender inspection: `evidence/fresh_import/incoming_inspection.blend`.
- Colored/isolated diagnostic: `evidence/part_audit/part_diagnostic.blend`.
- Structural inventory: `evidence/part_audit/audit.json`; complete preservation test: `evidence/full_partition_check.json`.
- Clean rerun: `evidence/part_audit_reproduced/`; audit JSON SHA identical. Five PNG file hashes differ but decoded RGB pixels are EXACT (maximum channel difference0); preserve both, do not claim PNG byte determinism. The initial inventory assertion incorrectly required identical PNG hashes and failed before writing a manifest; replaced with truthful byte/pixel distinction, no outputs overwritten. One reproduced quarter image additionally inspected. Cloud result is preserved directly, not a locally scripted regenerated GLB or byte-reproduction claim for Blender save metadata.
- Native43+7 before/after guards: `protected_before.json` / `protected_after.json`; non-secret inventory: `Assets/Integration/GERMAN_RIFLE_PART_SPLIT_INVENTORY_20261003.json`.

![Colored actual split](../../Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-parts-v3/evidence/part_audit/colored_quarter.png)

## Retained diagnostics and boundaries

Initial urllib artifact download stalled at resource host, wrote an empty file and was stopped by its verified task-owned PID; no resubmission. An anonymous curl recovery with total60s/connect15s completed the same task. Preserve the empty initial file and private status. A relative render path initially wrote five PNGs under this exact C-drive task leaf; all five were moved, not copied/overwritten, into project LocalWorking after path/inventory checks. The source now resolves output paths and clean rerun stayed inside project. Initial attempted scoped relocation command was rejected by execution policy before execution; explicit file moves succeeded. No material/model lost or shared asset deleted.

All old pilot77 private files/7 source scripts and prior refinement65 files/5 source scripts are checked against their manifests; protected43 native+7 actions remain unchanged. No M1, map, game config, UE, SFTP/Catalog, commit or push. All modeling/download processes ended; pricing tab remains open. Private API state is ignored and excluded from inventory.

## Next useful direction, not another cloud task

Keep the original base as the protected starting point. Further refinement needs an explicit small surface/material-boundary proof in Blender, preserving stock shape/UV and following connected boundaries, not more box cuts/whole-plane hulls or assuming cloud object splitting equals material separation. A mature compatible rifle or bounded manual surface reconstruction is an alternative. This run does not reopen detailed characters or erase previous failures. German production asset gap remains open.
