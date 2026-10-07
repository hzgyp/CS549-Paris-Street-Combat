# Allied NPC marked grip pivot raise V7 — review checkpoint

5 October 2026. User approves the annotated interpretation and execution:
right firing hand/marked grip fixed, raise gun muzzle and left support together,
stop when index/trigger relationship is correct. Plan:
`ALLIED_NPC_PIVOT_RAISE_V7_20261005.md`, including its display-only addendum.
Status: **one static candidate presented; complete contact NOT accepted**.
German fitting and formal selection remain deferred to human review.

## Evidence, mechanism and preservation

Read Failures/README, AN002, FP001, the English calibration guide and current
V6 result; Blender character workflow and its execution/form-fit references.
No stopped digit/FP/AN fitting author executed. Use actual Allied US full FBX,
native73-bone V6 pose, original M1 topology and native centimetres. No player
numeric copy, new motion, mesh cut, weight edit or detached hand shift.

Private immutable measurement:
`Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/AlliedNPCGripV2/pivot_raise_measure_v7/`.
Rest alignment max0.000147449cm, explicit reflected coordinate basis. User's
small native-image mark(726,456) hits actual stock triangle1291; projected
point(726.000013,455.999976). No nearest-surface fallback used. Selected pivot
world(-5654.302817,-2250.003571,229.668680)cm identifies the annotated region;
the screenshot alone does not uniquely determine the ideal 3D anatomical pivot.

ONE minimal3D swing toward fixed index from this pivot gives15.909280degrees,
muzzle raises19.805075cm. No extra gun translation, scale or angle candidate.
Left wrist follows the same rigid change; source-length shoulder/elbow solve,
fixed shoulder/clavicle and preserved digit locals. Wrist displacement6.120209cm;
upper arm30.339930cm / forearm26.975140cm retained, reach34.012690cm.

Offline preservation: right/unaffected skin max7.31e-12cm, all digit local
matrix error1.82e-12, segment length error1.56e-13cm, pure-palm rigid tracking
1.91e-12cm. No new severe edges; max extra edge length1.344720cm, which is
reported rather than inferred to prove deformation quality. Actual elbow/cuff/
shoulder images also inspected. Source model/rig/weights/actions unchanged.

## Contact result and stopping condition

Actual fixed pad to nearest blade surface:1.929319→0.281807cm. The old chosen
blade landmark distance2.606150→1.475148cm is different: pivot-to-landmark
radius7.059841cm versus pivot-to-pad8.534989cm leaves1.475148cm radial mismatch
for this exact landmark pair/pivot. This does not prove all rigid fits impossible.

Right-digit stock crossing face counts before→after:
index63→89, thumb70→59, middle16→21, ring0→30, little0→36. Index guard0→5,
blade0→18. Surface distance improvement is **not clearance or complete grasp**.
Keep this candidate unselected; no automatic additional rotation/translation,
finger compensation or threshold relaxation. Await the user's next marking.

## Native presentation and retained failure

First owned viewer `pivot_raise_native_v7`, PID34352: public bone reads reproduce
V6 but actual two images show reference-pose lowered arms. Early visual gate
kept closed; V7 candidate never applied. Owned300-second deadline produces
recorded assertion, followed by normal editor exit0. Inputs/611 guards exact.
Preserve both actual failed images and result; this is a presentation failure,
not evidence of the candidate arm solve failing.

Installed engine source establishes that SetBoneTransform updates local storage,
while component refresh sends matrices to rendering. NEW display-only V7b
entry enables only the diagnostic Poseable component's native paused tick /
AlwaysTickPoseAndRefreshBones, and waits one second after pose application
before capture. Both baseline images now show recorded raised arms, confirming
render parity. The individual contributions of paused tick and capture delay
were not separately isolated. No new fit or model/action edit occurred.

Owned `pivot_raise_native_v7b`, PID43740: existing uninitialized actor used only
as a full original US Poseable component container. Actor tick disabled, no
BindExistingPose/config/FP hand overrides/pinky change/camera assembly. Original
NPC animation driver untouched; world paused during frozen comparison. Actual
M1, original character/gun material paths, no source replacement or native save.

Eleven1600x1000 images inspected at original resolution: matched before side/
trigger, after front/right/top/trigger/support/front-and-right/reverse, full-arm
before/after. Three2400x660 labeled sheets also inspected; equally resized,
not retouched. Full source sleeves/arms remain continuous in these static views;
no visible detached cuff. Right index is closer to guard/blade but is not a
validated curled trigger grasp. Top/reverse and geometric crossing results
prevent whole-contact acceptance. Native texture detail varies and some gun
closeups show speckle artifacts; no UV/material edit or unproved sole cause.

Native73-bone max position error2.84e-14cm / rotation0.00005335degrees. Protected
before/after bones exactly0cm/0degrees; actual native fixed-pivot drift0.000136406cm.
Each capture's gun drift screened<0.01cm. Native normal exit0; fresh611 combined
guards and all measurement/trial/viewer input hashes verified; no UE/Blender
process remains. Lane A native slot explicitly RELEASED.

Private results/images/verification/sheets:
`Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/AlliedNPCGripV2/pivot_raise_native_v7b/`.
Geometry, source pose data, screenshots/logs remain Git-ignored; Git contains
generic tools and documentation only. Existing dirty work preserved.

## Remaining gates

Human static grip review, complete right/left contact, actual animated idle/
walk/run/reload/recoil/aim transitions, authoritative runtime adapter, gameplay/
near-wall/performance/package/lifecycle and asset dependency audit remain unrun.
Frozen diagnostics are NOT a playable rig/action or formal NPC integration.
First-person approved assets, German, B AI/BT/BB, current formal map, Catalog,
shared transactions remain protected. No adoption, deletion, asset publication,
Git commit or push. Next step is user review, not automatic German fitting.
