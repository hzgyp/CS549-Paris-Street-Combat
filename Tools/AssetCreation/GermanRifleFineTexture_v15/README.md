# V15 final native-grain pass

Read the paired V15 implementation/result documents and work_state before use.
Blender 5.2.2 LTS: `C:/Program Files/Blender Foundation/Blender 5.2/blender.exe`.
Retain the accepted V14 dark macro appearance; this is the last authorized polish
round, not permission for another sweep, game integration or publication.

`main.py --out NEW_ABSOLUTE_DIR --stage preview|final [--no-render]` opens the
hash-pinned V14 blend and reads original private M1 D/N/ORM. It replaces only
stock-side and handguard-side maps at 4096×2048 and4096×1024. Registered native
high-frequency colour/normal/roughness at fixed4×/2× sampling adds actual detail;
the macro base, geometry/UV/steel/caps and scalar responses remain protected.
Save/reload/pack baked PNGs before export. No randomness or cloud service used.
Never overwrite an occupied output directory, even for an equivalent repeat.

Fresh geometry audit: sibling `GermanRifleSPR_v10/audit.py --candidate DIR --out
NEWDIR --name GermanRifle_FineWood_V15 --geometry-baseline V14_GLB --render
--pbr-only`. `material_audit.py --candidate DIR --out NEWDIR --render` verifies
actual ownership of six replaced PNGs,30 unchanged payloads,12 unchanged material
definitions, face material triangle counts/areas and fresh specular/normal scale.
V14 side normal images have V13 names: do not infer ownership from name prefixes.

Clean separate main process with --no-render, then V10 audit using --compare-glb
FINAL_GLB checks semantic attributes/all36 PNGs. Whole-file byte identity is
reported separately, never inferred from semantic equality.

Fixed M1 comparison: `Tools/AssetValidation/blender_rifle_texture_compare.py
--german FINAL_GLB --variant german_v15 --expected-sha ACTUAL --out NEWDIR`.
Bundled Python `presentation.py --comparison DIR --out NEWDIR` labels/uniformly
resizes the actual matched views and supplements them with an explicitly labeled
identical1:1 stock crop; no sharpness/colour retouch of evidence.

Private binaries/evidence remain ignored under
`Assets/LocalWorking/Experiments/GermanRiflePilot/20261004-fine-texture-v15/`.
`inventory.py` writes hash-only diagnostic metadata, not release/restore authority.
Do not run occupied authoring identities or write any original reference asset.
