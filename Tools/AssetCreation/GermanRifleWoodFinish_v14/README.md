# V14 wood finish

Read the paired V14 implementation document and work_state first. Use Blender
5.2.2 LTS at `C:/Program Files/Blender Foundation/Blender 5.2/blender.exe`.

`main.py --out NEW_ABSOLUTE_DIR --stage final [--no-render]` opens protected V13,
changes only three wood material D/ORM sets and wood specular response, then
saves a self-contained blend and GLB. Existing normals/steel/shape remain intact.
No outputs may overwrite an occupied directory. Randomness not used.

Run sibling V10 `audit.py --candidate DIR --out NEWDIR --name
GermanRifle_DarkWood_V14 --geometry-baseline V13_GLB --render --pbr-only`.
Then `material_audit.py --candidate DIR --out NEWDIR --render` verifies 30
protected PNG payloads, nonwood material definitions, bindings and exported
KHR_materials_specular / fresh wood node response. Two actual wood close views.

Clean rerun main with --no-render; V10 audit --compare-glb FINAL_GLB checks
semantic attributes/PNG equality, reports whole-file equality without assuming.
Matched M1/German render uses Tools/AssetValidation/blender_rifle_texture_compare.py
with --german FINAL_GLB --variant german_v14 --expected-sha ACTUAL --out NEWDIR.
Bundled Python `presentation.py --comparison DIR --out NEWDIR` labels/resizes
actual M1/V13/V14 renders only. It does not edit texture/appearance evidence.

Private outputs: ignored LocalWorking/Experiments/GermanRiflePilot/
20261004-wood-finish-v14. Not UE runtime, Catalog, sharing or restore authority.
