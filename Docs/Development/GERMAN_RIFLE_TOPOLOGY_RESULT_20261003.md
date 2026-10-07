# Kar98k topology/standalone-mechanical result

2026-10-03. **Partial outcome, not a finished or integrated rifle.** User approved local receiver/sight/muzzle topology rebuilding. Blender modeling skill governed source-first gray review, one bounded structural correction, standard-material export, clean reproduction and fresh import. Read GP001–007. Original V7 rifle, wood, sling, ball, M1 and game remain unchanged.

## Original-surface gates stopped

V8: actual original-edge loop156 bounds1,884 connected conservative upper steel faces. Five cyan views inspected; no selected wood/ball/sling. Each boundary edge separates one selected and one retained face, but top projection has three crossings (51/54,94/96,94/97). No planar cap was authored. The projection Python assertion failed even though Blender shell exit was0.

V8B: same region, no new anchors. Diagnostic1,020 physical vertices/2,903 edges/Euler1 and exactly156 boundary edges, but one physical edge has four incident source faces. Exact coordinate duplicates prove this is not grouping tolerance. The required manifold-disk assertion failed (shell exit1), before harmonic solve or remesh. Read [GP007](../../Failures/GP007-20261003-kar98k-planar-patch/FAILURE_ANALYSIS.md). Both source-dependent mechanisms stopped; do not tune silhouettes/tolerances or remove intersecting faces blindly.

## Independent mechanical candidate

V8C creates **parts alone**, never cuts or overlays the source rifle: receiver front/rear rings/open lower rails, bolt body/cap/extractor/static safety; rear-sight base/inclined leaf/slider/two-shoulder notch/hinge/scale rails; hollow muzzle/front band/blade/base.24 separately named meshes, intentional local pivots,10,104 triangles, one UV per object, two own constant glTF steel materials. No commercial M1 atlas or procedural-material export dependency. Source-scale/sloped-axis placement is provisional, not calibrated manufacturing dimensions.

First eight clay images showed crossed wedge quads/black underside; positive volume and paired edges alone missed it. Preserve first source snapshot/images. The **one** structural correction fixes six wedge face loops and adds convex-corner orientation checks. Eight corrected clay images inspected: cylindrical curves/opening/bore readable and no original stray fins reproduced. Eight PBR and eight fresh-import views inspected. This is cleaner manufacturing **form**, still a coarse/subassembly candidate: sight marking numerals/cam detail, correct safety/bolt proportions, handle/ball mating, wood seats and full assembly are not accepted. The separated/front band has no wood seat in this standalone scene; it is not a complete supported gun.

![Fresh standalone receiver](D:/0.Rutgers/CS549/Project-New/Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-topology-v8/parts_audit_v1/fresh_receiver.png)

![Fresh hollow muzzle](D:/0.Rutgers/CS549/Project-New/Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-topology-v8/parts_audit_v1/fresh_muzzle.png)

## Technical evidence / deliverables

Blender5.2.2LTS/d13f752e3b9c. Corrected source solids pass paired-edge/positive-volume/convex-face/UV checks; independent imported triangle winding/topology/corner audit passes. Position/pivot max error0m, UV2.98023224e-8, normal0.03459591degrees (declared0.5degree gate). Clean source rerun exports byte-identical GLB SHA `6e49674ce0b0871df97951b1bd197c4cec540b7719276e174bc60b6f8a3376f4`,330,408 bytes. Self-contained blend232,161 bytes, no external textures. This is not UE/runtime/collision/reload/performance verification.

[Source](D:/0.Rutgers/CS549/Project-New/Tools/AssetCreation/GermanRifleTopologyV8/parts.py) · [Blend](D:/0.Rutgers/CS549/Project-New/Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-topology-v8/parts_finish_v1/Kar98k_StandaloneMechanical_V8C.blend) · [GLB](D:/0.Rutgers/CS549/Project-New/Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-topology-v8/parts_finish_v1/Kar98k_StandaloneMechanical_V8C.glb) · [Metrics](D:/0.Rutgers/CS549/Project-New/Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-topology-v8/parts_finish_v1/metrics.json) · [Fresh audit](D:/0.Rutgers/CS549/Project-New/Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-topology-v8/parts_audit_v1/audit.json)

Run clean `blender --background --factory-startup --python-exit-code 3 --python Tools/AssetCreation/GermanRifleTopologyV8/parts.py -- --output <NEW_PRIVATE_PATH> --pbr`; add `--skip-renders` for geometry/export reproduction only. Existing occupied identities cannot be reused. `verify_parts.py --input <first> --repeat <second> --output <new audit>` independently checks/import-renders. `manifest.py --verify` checks the private evidence/source inventory.

37 new PNGs all actually inspected (5 proof+8 initial clay+8 corrected+8 PBR+8 fresh). Seven old inventories355 private files/49 sources,50 native/action and four M1 reference hashes all match. Material.use_nodes deprecation warning retained; no export/runtime promise about future Blender APIs. All automated task Blender processes ended; no interactive preview opened. No cloud/spend, source rifle/game/UE/SFTP/Catalog or commit/push changes. The new hash inventory records unfinished work only.

## Next boundary

Do not declare German rifle asset gap closed. The approved original-stock-preserving automatic patch is blocked by the source surface, and this candidate must remain unselected. Next requires a separately documented manually controlled receiver/wood interface topology solution (or mature compatible licensed rifle), not another automatic source fill/cover/sweep. Prove one real assembled contact before detailing/whole-gun integration or making it an asset baseline. Current deliverable is standalone mechanical form plus failure evidence, not completion of the user's whole-rifle refinement goal.
