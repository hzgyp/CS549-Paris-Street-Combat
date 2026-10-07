# German rifle — Blender surface-guided refinement V4

2026-10-03. Yupu explicitly resumes refinement using the Blender modeling skill after GP003. Local rifle only; no Aholo call/spend, detailed character, M1, Unreal/game, SFTP/Catalog, commit/push. Existing source and every old draft remain immutable.

## Read failures / changed mechanism

Read failure index, GP001 (global reduction/UV and incomplete handle), GP002 (wood cut by volumes, unrelated contours bridged by hull/cover plates), GP003 (object splitting only rifle/sling), latest HANDOFF and all four Blender modeling references. Current input is the geometrically/UV-exact cloud original or its verified whole-rifle/sling partition, not failed GP002 refinements.

Different mechanism: use source UV/PBR/color observations to guide actual surface boundaries. First prove a small wood/metal interface without deleting faces, altering wood vertices, or generating caps. Preserve triangle positions/UV while assigning meaningful materials; geometry refinement then locks interface vertices and source wood, changing only identified metal interiors. No whole-plane convex hull, large cut boxes, covering plates, global weld/decimation or automatic bolt-action claim. Spatial regions may constrain observed metal features, but cannot determine wood-vs-metal alone.

## Contract

- Smooth exterior Kar98k world prop matching the inspected Paris museum specimen; provisional1.105m display length. Full side, top/bottom detail photos already CC0 and reviewed, reopened relevant views before feature changes. Camera names link observed references; absent full-quarter photo remains a gap.
- Preserve successful stock outline, open trigger guard, source UV/material atlas and sling (museum replacement, not German loadout approval). Improve readable wood/steel separation, receiver/bolt/sight/front exterior, preserving true contact instead of covering damaged stock.
- Editable Python source, packed `.blend`, GLB, fixed clay/PBR whole and detail evidence. Detail-master ceiling350k triangles; no new30k runtime or motion/LOD/history claim. Distinct exterior parts may be static attached surfaces; no complete working firearm/internal mechanism is designed.
- Source coordinates and UV outside explicitly reported metal edits must remain exact. No low-poly requested. Matte worn wood / dark blued steel, restraint on bright metal highlights. Cosmetic material improvement alone is not geometric completion.
- New source `Tools/AssetCreation/GermanRifleSurfaceV4/`; new physical root `Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-surface-v4/`. Retain all prior77+7/65+5/31+4 and43+7 native/action inventories. Outputs use new exclusive identities and absolute paths.

## Order / falsifiable early gate

1. Read-only source-material/UV and geometry probe, source SHA and native guards. Record face color/PBR statistics and uncertain classification instead of treating hue as perfect semantics.
2. Small interface proof: all source faces retained, wood positions and UV unchanged. Colored and PBR receiver side/top/quarter views must show useful metal boundary, no wood damage, fins, gap or false plate. If ambiguity is widespread, stop that classification approach; no repeated threshold sweep.
3. If useful, proceed to bounded source metal smoothing/profile adjustment with locked interface boundary, no wood deformation. Source/after clay views must actually sharpen shape and preserve contact, not hide failures with darker paint. At most two coherent geometry candidates, not unlimited parameter rounds. Visible uncertainty is recorded.
4. Materials, export, fresh import and independent clean reproduction. Verify names/hierarchy, triangles, UV/images, finite data, protected wood, local edit count/max movement, plausible joins and fixed multiview. Keep original cloud GLB unmodified and every failed intermediate.
5. Report what improved and what remains. No automatic game/SFTP selection. Stop if early interface cannot be proved, two local shape passes fail, a new wood artifact appears, or new approach requires broad stock reconstruction. Another mechanism requires a new documented scope rather than a fourth cover/cut attempt.

Rollback is non-selection, never restoring old files over current work. Skill self-review gates are not extra user-approval requests; continue in the approved local scope when evidence is good.

## Probe outcome / surface marking before authoring

Initial source probe shows color and generated metallic values overlap heavily between stock, bolt and exposed barrel; no hue/ORM threshold alone is justified. Use photograph-guided top ribbons and exposed protrusion surface marking (all triangles retained), with material/UV observations as a check, not automatic semantic truth. Source atlas stays unchanged; separate matte-wood/blued-steel shader settings and steel corner colors preserve detailed variation without overwriting texture bytes. The early proof is receiver side/top/quarter and whole reverse view. Markings must be inspected before geometry changes. This is a surface material assignment, not a complete operating bolt split. Local profile adjustment may only edit vertices wholly interior to inspected steel faces; all wood-incident coincident points lock. No cap or replacement plate.

## Early proof failure / distinct contour-label pass

`interface_v1b` fresh-import side/top/quarter inspection fails: rectangular ribbons label only the tops of receiver metal; lower shell and safety remain wood-colored. No geometry was changed. Freeze this source with that draft; stop this classifier, do not sweep its thresholds. The export failure in `interface_v1` is also retained.

Before further authoring, change to explicit manually traced surface labels: a varying-width receiver outline, a side contact-seam curve, a separate safety outline, and a bent-handle envelope. These labels are observations of the actual clay surface checked against the museum top/right photos, not an automatic material segmentation or precise mechanical drawing. Surface points are painted, never cut. Each uncertain label remains auditable in Python. This is one coherent replacement labeling proof (`contour_v1`), not another geometry candidate. Preserve UV and every triangle; no caps or added cover hardware. Receiver side/top/quarter must now show continuous steel shell and visible wood margins without a stripe bisecting metal. If this single contour proof still mislabels the interface, stop receiver classification/refinement and report failure; no third classifier/threshold sweep. Geometry remains conditional on this new early proof, at most two candidates as above.
