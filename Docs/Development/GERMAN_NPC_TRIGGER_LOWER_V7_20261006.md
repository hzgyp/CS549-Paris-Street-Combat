# German NPC V7 — retained raised thumb, trigger-pivot stock lowering

6 October 2026. User marks V6's pure-elevation thumb image, explicitly retains
the raised thumb and requests downward gun rotation about the trigger with the
LEFT support hand following. This supersedes V6's no-consumption/no-gun-move stop
only for this new comparison; it does not accept V6's penetrations or authorize
formal selection, another thumb solve or publication.

## Read cases / changed mechanism

Read current HANDOFF/618 epoch, Failures index, V6 result, V4 result, GP010,
AN002, AN008, weapon-hand guide and character workflow. Preserve their failures.
V6 raises a thumb through a fixed stock; V7 instead keeps that exact thumb
pose fixed and lowers the stock about the actual retained trigger landmark.
Do not rerun V6 root fits, V4 clearance or the rejected large yaw.

The user's arrow is on the rear stock, below the raised thumb. Interpret it as
lowering this stock end, not lowering the opposite muzzle. Use the measured
gun forward / world-up pitch plane; verify actual stock Z decreases and actual
trigger point stays fixed before accepting the direction. ONE 8-degree modest
comparison (not a claimed final fit angle), no translation/yaw/scale or angle
sweep. This bounded default avoids repeating the rejected 37.6-degree solve.

## Protected inputs and contract

Starting state: V4 `offline_v6/result.json` and full skin `geometry.npz`, plus
exact retained V6 `vertical_lift_v2` three right-thumb quaternion arrays.
Only V7 gun rotation and original-length LEFT arm chain may change relative to
that reconstructed raised-thumb state. Right arm/wrist, all right digit locals,
thumb length, source rest mesh/weights/UV/materials/actions and other bone worlds
are protected. Left grasp locals stay fixed; move the complete wrist/grasp using
upperarm -> forearm -> wrist IK with the original elbow-side bend plane. No hand
mesh displacement, arm scaling, finger compensation or rig/source-action edits.
Unit: native centimeters; column-vector matrices. Evidence remains private in
the existing SFTP workspace; source code/docs only belong in Git.

## Early check / evidence / stop

Fresh reconstruction must reproduce the retained V6 pose before changing gun.
Require fixed trigger <0.0001cm, actual rear-stock downward motion, exact right
world matrices, left arm-length errors <0.0001cm and unchanged digit locals.
Check actual all-positive-influence thumb/index/other-digit and left contacts,
mixed skin tracking, wrist/shoulder continuity and new severe edges (>3x AND
>2cm extra). A fixed trigger point does not protect the entire rotated blade:
measure index/guard contact rather than claiming it unchanged.

Stop on failed protection, unreachable arm or new severe skin edges. Retain
contact failures, never loosen their thresholds or call partial geometry a
completed grip. Matched gray BEFORE/AFTER reverse/right/top and whole-arm views
are allowed for this explicit directional comparison even if contact remains
incomplete; label these limits clearly. Fresh-process reproduction verifies
exact configuration/skin/gun before rendering. No Unreal entry is needed for
this requested local comparison. Native motion/binding remains untested.

No third thumb-root solve, follow-up angle/offset/digit adjustment, asset save,
map/Catalog selection, source deletion, Allied/FP/B/AI edit, publication, Git
commit or push. Report actual results and stop for the user's marking.

## Post-comparison boundary diagnostic (no refit)

V1 stopped before pose evaluation because the user's Temp screenshot cannot be
recorded by a project-relative-only path helper. Distinct V2 fixes only external
reference bookkeeping; the ONE actual comparison remains 8 degrees. It verifies
trigger8.53e-14cm/protected bones2.73e-12/left original lengths/no new severe edges,
but the blanket ANY-right-weight skin assertion reports1.974cm and stops.
Read-only source-weight inspection finds SIX vertices influenced by both hands:
three actually on the left support, three on the right palm/thumb boundary.
The blanket right mask includes the left vertices; do not call their normal
left-arm motion a right-bone edit or classify shared skin as unchanged.

A distinct read-only fresh reconstruction of the retained V2 transforms may
audit every zero-LEFT-influence vertex and report all six shared displacements
and actual distal index separately. This does not repeat fitting, change an
angle, relax the old assertion or promote V2's failed receipt. Render only the
retained comparison as diagnostic evidence with explicit contact/shared-skin
limitations; no usable asset/native adoption. Full contact remains unaccepted.
