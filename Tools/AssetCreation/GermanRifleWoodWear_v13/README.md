# Private V13 material repair

Use the project's paired V13 plan and `work_state.md`; this is not release or
game-selection authority. Skill: blender-modeling-workflow stages5–7. No cloud.

Blender5.2.2 LTS executable:
`C:/Program Files/Blender Foundation/Blender 5.2/blender.exe`.

Run `--background --factory-startup --python <script> -- <arguments>` from the
project root. All output paths resolve before loading another scene; use new
identities, never overwrite previous artifacts. Source V12 is read-only.

- `preflight.py --out <new>`: UV occupancy/conflicts, actual wood rings/caps and
  butt convex adjacency.512 side test and256 whole occupancy are diagnostics,
  not final appearance acceptance.
- `ownership_checks.py --out <new>`:1024 isolated exposed furniture conflicts.
- `main.py --stage proof|final --out <new> [--no-render]`: retained M1 grain,
  face-owned metre-space masks, baked D/ORM, wood-only weak normal perturbation.
  Preserve all original normal layers; retain ambiguous sight response.
- `mask_review.py --candidate <stage> --out <new>`: actual proof masks on mesh,
  explicitly reload PNG masks absent from unused Blender image datablocks.
- Existing `GermanRifleSPR_v10/audit.py --candidate <stage> --name
  GermanRifle_CoordinatedWear_V13 --out <new> --render --pbr-only
  --geometry-baseline <V12 GLB>`:24 names/24,466 triangles, attributes and6 views.
- `fresh_details.py --candidate <stage> --out <new>`: material counts/areas,
  original embedded normal/outside-scope PNG hashes and4 fresh close views.
- Clean final `main.py --no-render` into a new repeat directory, then existing
  audit with `--compare-glb <selected V13>` (no render): actual cross-export
  attributes/image payload equality; do not infer whole GLB byte equality.
- Existing `blender_rifle_texture_compare.py --german <selected GLB> --variant
  german_v13 --expected-sha <actual> --out <new>`: matched M1/reference views.
- `presentation.py --comparison <comparison> --out <new>` via bundled Python:
  M1/V12/V13 labeled sheet. No retouch, camera or scale adjustment.

Keep source/code/English+Chinese documents/hash metadata in Git, generated
commercial-derived images/scenes/exports in ignored LocalWorking. No SFTP,
Catalog, UE/game, native source/model, history/action/contact approval inferred.
