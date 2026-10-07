# Right-thumb stock contact V4

4 October2026. [Chinese review](WEAPON_THUMB_CONTACT_V4_20261004_ZH.md).
User accepts the latest index contact visually and requests RIGHT thumb resting
above the stock in a closed grip. This is the new narrow thumb adaptation scope,
not renewed index repair or whole-hand repositioning. Source/native protection
and current528 guards remain; no UE slot needed for initial offline work.

Read HANDOFF/current Git, failure index, AN003/004/005, FP001, rejected coarse
left-finger result and latest trigger-contact result. Differences: freeze accepted
V2 rifle fit and V3 index rotations exactly; solve only thumb_01/02/03_r contact,
not coarse all-finger curl, source retarget, masks, weights or whole-pose offsets.

## Contract and order

1. First inspect existing D059 reload and RifleAnimsetPro idle thumb rotations
   already recorded on this owner. Measure thumb skin/joint positions relative to
   the frozen gun, upper stock contact surfaces, mixed skin influences and index
   regression. Reuse compatible existing thumb pose first if it fits.
2. If existing poses cannot reach the shifted stock, one bounded thumb-only local
   rotation contact adaptation of the existing grip may align the distal pad to
   the actual upper stock. No new animation/keyframes, action synthesis or source
   track edit: an offline contact display layer only. Preserve local translations/
   scales, thumb proportions/weights, all non-thumb joints, fixed index layer,
   palm/wrist/left hand/gun/camera. Do not move only the thumb mesh or detach joints.
3. Record actual upper-stock face and pad landmarks, final local rotations, source
   hashes and all eight reload phases. Inspect before/after from both sides/top/
   contact close-up and whole arms; fresh-open final saved diagnostic source.
   Native/game runtime remains separate, no stopped owner integration rerun.

Early acceptance: index local matrices AND its evaluated skin stay unchanged;
gun/palm/left contact unchanged; thumb pad materially closes its upper-stock gap
without stock/receiver penetration, inverted/excessively collapsed thumb skin or
breaking its base. Contact distance alone is not a clearance/visual pass. Stop if
index regression, unreachable contact under the three-joint chain, new visible
skin defect or remaining main thumb penetration occurs; preserve evidence, do not
broaden to hand/wrist/weights/gun or sweep contact parameters to claim success.
Existing blade22 surface crossings remain recorded; user approves current index
appearance, not measured solid clearance or native dynamics. No automatic NPC
copy/formal-map selection/Catalog/release/package/commit/push. Further native
selection must first coordinate the single UE slot and record actual runtime
transition/lifecycle/contact checks.

Storage: tools `Tools/Integration/WeaponThumbContactV4/`, private evidence in the
single existing workspace `Evidence/WeaponThumbContactV4/`. Preserve earlier input
and candidate identities. Geometry/rig/bone lengths/UV/materials/weights/source
motions protected; only thumb local rotations may differ in the copied evaluation.

Read-only probe completed: ten recorded poses (eight D059 reload, two Rifle_Idle).
D059 thumb is effectively invariant and has45 crossing triangles at the fixed
gun; Rifle_Idle improves distal-centre upper-stock distance3.32→1.41cm but still
has30 crossings. No index vertices have thumb influences under the existing mask.
Use Rifle_Idle0s thumb rotations as the mature starting grip. ONE root swing about
thumb_01_r, derived by actual pad/upper-stock offset-triangle sphere intersection,
keeps bone lengths and distal local grip angles. Limit40degrees from the reused
idle thumb root, unchanged gate; do not adjust gun/contact margins in a sweep.
Nominal pad margin0.05cm is not solid-clearance proof. Require no thumb/stock or
other-gun crossings in recorded poses and no new severe edge (>3× plus2cm stretch)
relative to pre-thumb baseline, inspect base/web/tip and report actual residuals.
