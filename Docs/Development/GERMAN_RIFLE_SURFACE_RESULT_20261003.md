# German rifle surface refinement V4 — early gate failed

2026-10-03. Local Blender-only continuation explicitly requested by Yupu; Blender modeling skill used. Read GP001/GP002/GP003 before the V4 implementation. No cloud call, credit use, M1/reload, Unreal, SFTP/Catalog, commit or push.

## Actual outcome

**No improved rifle was selected.** Stopped at the surface/material-boundary gate, before any metal geometry polish. Original direction approval still applies to the original base, not these candidates. German production asset gap remains open.

- Original PBR color/metallic samples overlap between wood and metal, so texture thresholds cannot establish a semantic boundary.
- `interface_v1`: Blender saved the packed master but GLB export failed because Blender5.2 does not accept `export_colors`. Failed script and partial output retained. Blender exit0 did not establish success.
- `interface_v1b`: corrected supported vertex-color export; all299,479 triangles preserved. Fresh-import receiver side/top/quarter and whole reverse views show only upper strips of steel painted, while the lower shell/safety stay wood-colored. Failed early gate.
- Documented a distinct varying-width/seam-label pass before authoring `contour_v1`. Receiver coverage improves but actual side/top/quarter show a black patch on the adjacent wooden wrist, a wood-colored stripe on the handle and missed safety/sight surfaces. Failed early gate. **Do not run `--geometry` on these labels or sweep their parameters.** No third classifier was authored.

18 unedited clay/PBR images generated from fresh GLB imports; actually inspected11: interface_v1b receiver clay top/quarter, all6 PBR views; contour_v1 all3 PBR receiver views. The contour trial was deliberately not extended to whole-rifle polish after its local failure. Both GLBs have2 meshes, a UV layer and packed source diffuse image; this is export evidence, not visual acceptance.

Independent `independent_audit_v2.json` checks both authored masters against a freshly imported source using the same Blender transform application: every normalized vertex position, triangle index and corner UV is exact; source packed diffuse/ORM images are byte-identical. No geometry refinement occurred. The first audit used a different float32 matrix multiplication path, residual1.1920928955078125e-7m exceeded its1e-7 check; preserve that failed audit/script. V2 fixes the computation path rather than increasing tolerance and obtains exact equality. Original50 native/action checks passed before/after. Previous rifle artifacts/source protection is recorded by the new inventory.

Final inventory records39 private files and7 current source/state/report files. Earlier77+65+31 private files and7+5+4 scripts all hash-match. All task Blender processes ended normally; no Unreal was launched and no preview is open. The geometry option is now explicitly blocked because the labels failed their visual prerequisite.

## Boundaries / next route

These are failed LocalWorking diagnostics, not usable assets or automatic restoration authority. Do not replace the base or publish this material paint. Do not treat bright steel, zero wood movement, object count, source preservation or fresh import as geometric completion.

Before another rifle implementation, review GP004 and choose a genuinely different way to obtain semantic boundaries: explicit face-loop selection on the actual surface in Blender, or finished compatible exterior parts with a verified fit. That work must first prove one small wood/receiver junction from side/top/reverse. No further coordinate-envelope tuning, covering plates, cuts/hulls, automatic cloud split or from-scratch character work follows from this result. This finding is about this fused generated mesh, not a universal claim that mechanical modeling is harder than character modeling.

## Locations

- Plan: `Docs/Development/GERMAN_RIFLE_SURFACE_REFINEMENT_V4.md`.
- Durable source/state/report: `Tools/AssetCreation/GermanRifleSurfaceV4/`.
- Private packed masters/GLBs/evidence/frozen failures: `Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-surface-v4/`.
- Metadata: `Assets/Integration/GERMAN_RIFLE_SURFACE_INVENTORY_20261003.json` (non-release).
- Failure: `Failures/GP004-20261003-kar98k-surface-labels/FAILURE_ANALYSIS.md`.
