# German NPC trigger-pivot V2 — static comparison

6 October 2026. Completed ONE gun rotation toward the user-marked right palm,
using the same actual trigger-surface point as V1. Both hands/arms/digits remain
fixed. Candidate only: not a complete closed grasp or formal German adoption.
Plan: `GERMAN_NPC_TRIGGER_PIVOT_V2_20261006.md`.

## Later human rejection — 6 October

User explicitly rejects the37.6deg angle as excessive. This supersedes the
pending-review status below: V2 is visually REJECTED, not an acceptable stock
seat. Numeric pivot preservation did not prevent a visibly over-rotated rifle.
Do not reuse the full-arrow endpoint fit as a grasp solution. Original raw
evidence remains unchanged. The separate V3 plan reconstructs V1 and makes one
small5deg/displacement-budget comparison, not a clean rerun of this target fit.

## Cases and early acceptance

Read Failures/README.md, GP010, AN002, AN008, German V1 plan/result and the full
weapon-hand calibration guide. Character workflow used for source protection
and actual multiview checks, not mesh/rig/weight authoring or new motion.

First offline projection assumed mesh/root yaw90 for the top camera and failed
the 45deg gate at -88.345deg BEFORE candidate/native launch. Retain
`axis_preflight_failure_v1.json`. Native capture actually uses actor yaw180:
the retained front eye/target establish forward(-1,0,0). Correcting only that
projection frame yields the one marked fit below, without relaxing the gate,
trying another angle/offset or moving a hand. A patch-context verification error
also occurred before the successful source correction; no partial edits/native
mutation resulted from that error.

User screenshot registration RMS0.017266 passes0.035. Actual native GLB bounds
match within0.00000336cm. The marked stock point is resolved on the actual
Wood_ContinuousStock surface,5.084 native pixels from the arrow's stock end.
Target is the marked palm direction in the TOP plane, not inferred skin depth.

Fresh native BEFORE top/right images were opened BEFORE rotation. V1 gun-to-hand
position/rotation reproduce at0cm/0deg; source index local errors0/0/0deg.
Actual top camera pitch/yaw/roll(-90,180,0) corroborates the corrected frame.
Original character/weapon/material/collision identities verified; both approved
Allied adapters and first-person adapter initialized unchanged.

## Actual rigid rotation and protected inputs

- ONE signed -37.596278deg rotation around world +Z (clockwise in this TOP view),
  derived from the user's marked stock/palm directions. It is not an NPC recipe.
- Pivot: retained actual Trigger_Donor point in gun frame
  (-0.089019909,14.714152551,-7.517012940)cm, same as V1.
- Native actual rotation37.596278132deg; pivot residual0.0000000669cm.
  Position/rotation goal errors0cm/0deg; no independent translation. Gun-origin
  movement is only the compensation necessary to rotate around the fixed pivot.
- Every character bone world t/q/s exact before/after and through all captures;
  gun scale unchanged and capture drift0cm. Source/model/rig/weights/actions,
  hands/arms/digits and original materials are not altered.
- Marked stock camera-plane gap6.693808->2.295610cm offline. A2.295610cm radial
  mismatch remains: fixed-pivot rotation cannot place this same stock point at
  that exact arrow head without a different constraint. No scale/translation
  compensation applied. Native point invariance is not a skin-clearance proof.

## Opened visual evidence and limitations

Private evidence remains only in the existing SFTP workspace:
`Evidence/GermanNPCTriggerPivotV2/native_rotation_v1/`. Ten native originals
were opened/inspected: before top/right; after top/right/front/reverse/context,
trigger and two attempted palm details. Three sheets and their hashes are in
`presentation.json`; original pixels are only resized/laid out, not retouched.

Stock visibly turns toward the fixed palm in the top comparison. It still does
not establish complete palm/other-digit enclosure or zero penetration. Index
stays straight and its fixed point remains, but the blade/guard ORIENTATION
changes with the gun; the side closeup retains possible guard/trigger overlap.
Do not describe point invariance as unchanged whole-surface contact.

Left support remains fixed and visibly separated from the turned fore-end; no
IK/finger compensation attempted. Static full-arm context remains continuous.
Front view crops/occludes weapon regions and the two palm detail cameras were
centered on the wrist, not the palm: top detail crops the grasp, reverse detail
is blocked by the torso. Those captures are retained as coverage failures, not
proof of hidden contact. Main native TOP view shows the right grip clearly;
no further native fit or capture rerun was made. Material-detail variation is
not texture authoring or a diagnosed texture defect.

## Closure and next boundary

Owned hidden editor PID22372/identity `native_rotation_v1` closed normally,
OS exit0/result errors empty. All618 current approved guards exact before/after;
retained V1 proof/images/pose/gun bytes exact. No UE/Blender engines remain;
Lane A RELEASED. Formal German remains unarmed; unsaved staging only.

No package/map save, formal selection, Allied/FP/B/AI change, source deletion,
Catalog/immutable SFTP publication, Git commit or push. No motion/reload/recoil,
aiming/muzzle/gameplay/near-wall/FPS/package/second-machine acceptance. Stop for
the next user marking; do not add another angle or finger/support compensation.
