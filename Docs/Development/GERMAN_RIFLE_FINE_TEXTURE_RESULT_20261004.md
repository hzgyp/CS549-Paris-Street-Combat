# V15 — final fine-grain texture result

2026-10-04. User positively reviews V14, then requests one last texture-detail
pass. Followed paired V15 implementation document and Blender modeling skill
stages5–7; read failure index, GP004/009 and V12–V14 source/results first.
V14 colour praise is appearance feedback, not complete production approval.

## Change and actual appearance

Diagnosis: native723×434 M1 wood crop was stretched over global1.105m UV length;
subsequent1024→2048 resampling added pixels, not native grain. Stock side had
about631 source columns and322mm handguard about210. Linear filtering was not
the primary cause. Do not equate a4K label with an actual detail improvement.

Keep V14 dark macro colour, broad grain/wear positions, shape, UV, scalars and
all steel/caps. Replace only two side materials' D/N/ORM with independently baked
4096×2048 stock and4096×1024 handguard maps. Native fine detail is sampled at
fixed4×longitudinal/2×circumferential scale (~2614sourcepx/m longitudinal).
Transfer zero-mean log-linear luminance detail, registered DX→GL high-frequency
normal and modest roughness detail; mirrored normal directions and seam fades
are explicit. No new random noise, wear locations, hardware or positional AO.
Save/reload/pack real PNGs before rendering/export. Post-PNG mean linear colour
relative drift ≤.01572%; roughness mean remains~.511, specular IOR level.18 and
normal node strength.45. Colour statistics are guards, not visual quality scores.

All four early source and two fresh close pictures inspected: genuinely finer
grain, dark colour preserved. No corrective appearance round needed/used.
Final eleven source views and eight fresh GLB views actually opened, including
both stock sides/underside and affected close views. An independent read-only
review compared eight V14/V15 original-resolution views and corroborated the
improvement. Stock grain/flecks, especially reverse worn area, are more legible;
the handguard gain is smaller. No obvious new hard joins, checker noise or normal
faceting in these static pictures. Old broad stretched/mirrored motifs and pale
grazing highlights remain. This is not full M1-quality scratch/edge artwork.

Matched M1/V14/V15 sheet and identical1:1 stock crop inspected, plus original
M1/V15 stock and V15 receiver images. Fixed camera/light/scale and AgX Medium
High Contrast, exposure0/gamma1; labels/uniform resizing and explicit crop only,
no evidence sharpening/colour retouch. Uncropped originals remain available.

## Candidate / measured checks

Private root `Assets/LocalWorking/Experiments/GermanRiflePilot/20261004-fine-texture-v15/`.

- `finish_v1/GermanRifle_FineWood_V15.blend`:110,979,481bytes, SHA256
  `b6c9afcd4de1675d533158bef5698e8b05e47e6226880964b241d606292f26b8`.
- `finish_v1/GermanRifle_FineWood_V15.glb`:81,346,308bytes, SHA256
  `77f7fd8cdde8c6b0b030b7b0ed4646f6bce8b03ad47f4ecb1826b51e502b378f`.
-24meshes/24,466triangles;1.107303977×.079198018×.183007009m;
 14used materials/30primitives/36embedded PNGs, no actions.
- Raw topology/positions/UV/corner normals/modifiers/transforms/hierarchy exact;
 face material slot indices unchanged. V14 blend/GLB and original M1 D/N/ORM
 input hashes unchanged in generator, final audit and relevant comparison checks.
- `audit_v1` fresh geometry/closed new solids/baseline checks pass, exit0:
 position0m, UV5.96046448e-8, normal.03721044deg; tolerances5e-7m/2e-5/.5deg.
 V14→V15 export geometry normal max.03346810deg; no authored geometry change.
- `material_audit_v1` passes, exit0: actual material triangle counts/areas match,
 exactly six wood D/N/ORM payloads replaced,30other embedded PNGs byte-exact,
 12outside-scope material definitions exact (11nonwood + end faces). Actual
 GLB specular extension.36/fresh node.18 and normal.45 verified; no clearcoat.
 V14 side normals have V13 names; allowlist derived from actual ownership.
- `repeat_v1` clean separate no-render generator and `repeat_audit_v1` pass,
 exit0; all36PNG payloads and semantic attributes match. Cross-export normal
 max.03346810deg. **Whole GLB bytes differ**, cause unproved; not byte-exact.
- `comparison_v1` exit0, six fixed views/two inspection scenes, five input hashes
 unchanged. `presentation_v1/m1_v14_v15.png` and `v14_v15_stock_native.png` use
 actual renders; native crop rectangle[130,160,910,690] is identically applied.

Blender5.2.2 LTS d13f752e3b9c. Existing sampler/future6.0 use_nodes warnings
retained; no generator/export/audit exception. Two read-only source/report path
lookups were corrected after locating actual files, not reruns or asset fixes.
No full old-library/native asset hash sweep claimed. Larger blend retains earlier
packed images;4K detail increases storage/memory, not a runtime optimization.
All task Blender processes ended; no interactive Blender/Unreal launched.

## Stop / handoff

Final authorized texture round is complete and stopped. No automatic extra
polish, even though M1 remains sharper. Candidate remains unselected/private,
V14 intact. Source `Tools/AssetCreation/GermanRifleFineTexture_v15/`; hash-only
`Assets/Integration/GERMAN_RIFLE_FINE_TEXTURE_V15_INVENTORY_20261004.json` is
diagnostic metadata, not Catalog/release/teammate restore authority.

No game/UE/M1-original/SFTP/Catalog/allowlist/cloud/spend/purchase/commit/push
changes. MW2 use/derivative-sharing rights, historical donor differences,
complete mechanism/rig/actions/contact and UE import/mips/shimmer/FPS remain
open. Static fine-grain improvement does not close the German production gap.
