# V12 fixed-right trigger pivot: comparison retained, contact gate failed

4 October 2026. [Chinese review](WEAPON_TRIGGER_PIVOT_RESULT_20261004_ZH.md).
Plan: WEAPON_TRIGGER_PIVOT_V12_20261004.md. User authorizes gun rotation/raising
around the trigger while the firing hand remains fixed, then left-arm correction.
ONE offline static0s candidate completed; no formal/native adoption or motion pass.

## Actual mechanism and evidence

Baseline is existing D0590s with V2 gun and V3 approved index local rotations;
other fingers retain original D059. Reviewed AN003/004/005/FP001, failure index,
V2/V3 and V11; no stopped digit/weight/transition solver resumed.

The read-only landmarks_v1 identifies actual blade triangle3173 near actual index
pad triangle10154. Pivot in baseline gun cm=(-0.143974,5.801779,-1.877380).
Rear-neck surface1333 and inward hand-dominant palm surface3554 determine direction.
Three actual marker views inspected. This nearest palm/neck pair is only a turn
direction, not an empty grip center or exact C-grasp seat. Its vector-direction
alignment angle25.9813degrees is NOT a required/full-fit angle or authorization
to increase the trial angle; radii/whole hand were not solved by that number.

One10degree rotation axis=(0.0602703,-0.0321559,-0.9976640) in baseline gun frame,
about the actual trigger point, turns rear wood toward the firing palm. The gun
origin translation follows this pivot. No free-translation or Euler-angle sweep.
Rear marker moves(-1.69174,0.40952,-0.11540)cm; landmark gap5.29284->3.61543cm.
That partial approach does not establish complete enclosed holding.

Left hand target receives the same rigid gun change in native component space;
source-length upper/lower-arm IK with original elbow side follows its position
and orientation. Gun does not chase the corrected left hand. Right arm and skin
stay unchanged, all finger local poses unchanged. No model/rig/weights/source
motion/camera/transaction modifications.

## Measured checks and stopped contact

| Actual surface-crossing hand faces at0s | Before | After |
| --- | ---: | ---: |
| Thumb/wood |45|33|
| Middle/wood |48|34|
| Ring/wood |6|58|
| Little/wood |0|0|
| Index/blade |22|14|
| Index/wood or guard |0|0|

Counts are not penetration depth/volume. Non-index wood total99->125 fails the
planned no-increase screening gate; ring interference remains visible in lower
contact views, bottom enclosure still incomplete. Some contacts improve, but this
candidate is stopped/unselected. Do not label this right-grip acceptance, and do
not infer all pivot solutions impossible or that10degrees is a correct final angle.

Actual index pad gap0.0515054->0.0507353cm. Pivot error0; right bone matrix delta
8.53e-14/right skin1.54e-13cm; all finger-local matrix delta4.27e-14. Left palm
tracking0.009054cm, left finger tracking1.63e-13cm; bone length errors<=7.11e-15cm.
No new severe edges under >3x AND >2cm criterion; max extra edge length0.38334cm.
These bounded continuity checks pass, not complete sleeve/deformation acceptance.

## Actual visual/fresh review and protected state

Private Evidence/WeaponTriggerPivotV12 has landmarks_v1, pivot_10deg_v1,
fresh_check_v1 and image_review_v1. Eighteen before/after fixed-camera views were
inspected in the complete sheet, with bottom/top/opposite/left-support/full-arm
originals opened plus labeled before_after.jpg. Right hand stays stationary;
left support follows without visible new cuff separation in inspected views.
Source shoulder sheets remain; no new masks/cuts or flattering-only acceptance.

Separate Blender5.2.2 fresh-open exits0, reads frozen static comparison without
changing bytes: hand/arm vertex max error1.9934e-6cm, gun3.0095e-6cm, original
armature72bones. Blend SHA22809d80e9c616a8ea74ed7eabd836cca12734fef14c7317bf84aaaaf9fc00d5.
This is baked static evaluation geometry, NOT a new playable rig/action export.
Probe/trial/fresh tasks exit0/errors[], source inputs unchanged; final audit checks
all six new scripts' AST. Fresh read does not clear the failed contact gate.

Trial before/after audits match all528 current recovery size/SHA records including
the known unselected V6 rate difference; formal map remains2791b4a7...ad68519.
No task UE slot or native writer, NPC/B/BT/BB changes, map selection, Catalog,
release, package, commit or push. UE/Blender processes absent at23:39 EDT check.
Final verification_v1 is the later guard audit, not an asset-selection authority.

## Next boundary

Stop this exact candidate after retaining comparison, as planned. No larger angle,
angle/offset sweep, individual-finger or weight compensation. Await user comparison.
Any later attempt first needs a different measured stock-neck contact/orientation
constraint in a new bounded plan. Do not proceed to continuous reload, gun-to-aim
alignment or native selection with this failed grasp; static improvement alone
does not clear those separate gates.
