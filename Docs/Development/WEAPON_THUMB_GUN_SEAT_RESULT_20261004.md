# V14 — thumb above the stock; local success, not game selection

2026-10-04 23:56 EDT. [Plan](WEAPON_THUMB_GUN_SEAT_V14_20261004.md).
The user's latest thumb-only scope supersedes the earlier aggregate-digit gate
for this trial. Other three digits did not stop it; their positions were not fixed.

## One measured placement

Original D059 0s/V2 gun/V3 approved index locals, right arm/skin/digits unchanged.
Actual measured turn-toward-palm direction gives 25.981331 degrees about the prior
trigger pivot, then lateral approach -0.989757 cm and downward seating -3.794783
cm in baseline gun coordinates. Additional displacement is below the 4 cm bound.
This is one surface-height solution, not an angle grid, and not proof that this
angle is a globally correct grasp. Thumb vertices, face centers and edge midpoints
ray-projected onto actual stock triangles determine a 0.10 cm vertical allowance.

Actual triangle tests: thumb intersects neither wood nor any other gun part
(0 vs prior 77 wood faces); nearest sampled skin/wood distance 0.090462 cm.
Fourteen actual same-camera before/after views compose the review sheet; the
sheet, new top/oblique/both sides/bottom/left support/whole arms originals and
hero were inspected. Thumb visibly lies over the stock, near it. Close views
isolate hand regions for diagnosis; whole-arm image retains original uncut skin
and original shoulder sheets. No finger/weight/camera edits or defect repainting.

## Separate limitations, not a complete grip pass

The index's local pose remains exact, but world-space trigger contact does NOT:
pad/blade gap becomes 2.267353 cm (prior 0.0484495 cm), with 58 index/wood crossing
faces. This result must not replace the approved trigger-contact comparison or
be selected for gameplay. Keeping a finger pose is different from keeping its
contact. Additional gun translation moved the original trigger pivot as well.

Non-gating middle/ring/little wood crossing faces: 65/52/54. These are explicitly
recorded, not treated as trial-stopping or full-grip acceptance criteria. Counts
are not penetration depth. Overall enclosing grasp remains unresolved.

Right skin delta 1.543e-13 cm, right bone matrices 8.527e-14, digit local matrices
4.264e-14; left source-length IK bone-length error <=3.56e-15 cm, new severe edges
0, maximum extra edge length 0.46489 cm. Left skin-palm following error 0.029614
cm exceeds this plan's declared 0.02 cm check. Preserve this failure; do not relax
the threshold or silently label all contact/continuity checks passed. Thumb-only
surface/visual result passed; full planned gate remains false. No further fitting
or game/aim integration was performed in this trial.

## Fresh read and protection

Fresh independent Blender process passes: same saved geometry, hands/arms maximum
error 1.994e-6 cm, gun 3.185e-6 cm, source armature 72 bones; input/blend hashes
unchanged. This blend contains baked evaluated diagnostic geometry, not a new
playable rig, source action, animation export or native/movement/reload acceptance.
Blend SHA f3d46e71aeb428cc8c152849ce35164a2330d4935e19a558be05d29a505ee054.

The first combined AST command used Windows default GBK while reading the Chinese
composer and raised UnicodeDecodeError; it was a checker encoding issue, not a
Blender geometric/native failure. An explicit UTF-8 command and final verifier
pass all five scripts. Composer and fresh process independently completed; no
candidate rerun or source/geometry change resulted from that command correction.

Evidence only in the single private SFTP workspace Evidence/WeaponThumbGunSeatV14:
surface_probe_v1, thumb_seat_v1, image_review_v1, fresh_check_v1, verification_v1.
Final audit 03:56:23 UTC / 23:56 EDT: 528 current recovery size/SHA records match,
old 10/20 input/code/blend hash proofs remain exact; current snapshot includes
the known unselected V6 saved-rate difference. Formal map remains 2707948 bytes /
2791b4a7f76b4b3d07f42286b6ad0156c3a185c2e3e795fa2446aaac0ad68519.
No UE/Blender process remains, no UE slot claimed, no B/NPC/BT/BB/native/map/Catalog
selection/release/package/cloud/commit/push changes. Static local fit retained
unselected. Next review must distinguish successful thumb placement from the
displaced trigger and open complete-grip/motion/aim requirements.
