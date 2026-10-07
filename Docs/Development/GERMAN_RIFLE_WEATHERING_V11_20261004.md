# German rifle V11 — restrained texture-only weathering

2026-10-04. User accepts V10's whole form and asks for small texture/aging refinement. This supersedes its pending whole-form review, not historical/runtime/sharing acceptance. Use the Blender modeling skill, revisiting stages 5–7 only.

## Contract and failure review

Read Failures/README, GP004 and GP009. Unlike GP004, use the already verified wood/steel material ownership and UV atlases, never a coordinate classifier to separate substances. Unlike GP009's failed export, explicitly apply existing modifiers on export and compare the actual fresh GLB. Preserve V10 finish_v3, its source and all older trials.

Keep all 24 objects, topology, UVs, normals, modifiers, transforms, centered root and 1.1073m extent. No new low-poly requirement, moving parts or rig. Add sparse longitudinal wood scuffs, uneven oil/patina and subdued steel scratches/roughness variation. No large chips, rust coating, markings, extra mechanical detail or shape changes. Preserve a coherent ordinary game-prop finish across both sides/top/underside.

## Implementation and acceptance

Open only the approved 13MB standalone V10 blend, not the 2.2GiB bought library. A new deterministic `GermanRifleSPR_v11/main.py` generates packed base-color/roughness/normal textures and separately named private `20261004-spr-weather-v11` outputs. No game, M1, UE, cloud/spend, SFTP/Catalog, commit/push.

Early check: fixed quarter and receiver before/after views must show restrained wear without changing palette/shape, introducing seams or making steel look rusty/plastic. Geometry fingerprints must remain exact. If noisy/overdone, allow one material-only causal correction; if still worse, stop and retain V10, not a parameter sweep.

Then export applied-modifier GLB, reopen/import in a clean process, compare names/24,466 triangles/dimensions/UV/normals and baseline geometry. Check embedded textures and inspect six source/fresh material views. Rerun the generator cleanly; semantic geometry/packed-image checks, not an invented byte-exact GLB claim. Record actual evidence, exact final hashes and limitations in paired result documents. Candidate remains private LocalWorking; rights, historical variants, operating rig and game tests remain separate.

Rollback is simply continued use of untouched V10; never replace/delete old outputs. Stop once the small requested wear is legible and technically preserved, without extending into other features.

Early actual preview_v1: four matched before/after images inspected, geometry fingerprint unchanged, Blender exit0. No noisy patches, but small scuffs are too weak to read. One texture-only causal correction increases their width/contrast and modest wood patina/roughness contrast; same form, seed, cameras and material ownership. Preserve this first preview/source. No geometry or edge-mask redesign.
