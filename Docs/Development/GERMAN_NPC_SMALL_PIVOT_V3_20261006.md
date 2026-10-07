# German NPC small trigger-pivot correction V3

6 October 2026. User rejects V2: the37.6deg angle is visibly excessive.
Treat this as a correction to the ongoing gun-fitting task, not permission for
new hand/finger/arm edits or formal adoption. Reconstruct V1 (translation only),
then ONE -5deg rotation in the same top-plane direction around its trigger point.
5deg is a deliberately small comparison chosen for this feedback, not a solved
full grasp and not37.6deg minus5deg.

## Cases read and different acceptance mechanism

Read Failures/README.md, GP010, AN002, AN008, German V1/V2 records and the
weapon-hand calibration guide; character workflow supplies actual multiview
and source/bone preservation checks. V2's apparent arrow-to-palm improvement
ignored the whole rifle's large yaw change. Stop that full-arrow target method.
Do not rerun its image registration/angle solve or adopt its candidate.

Use a small angular/displacement budget instead: same measured trigger pivot,
same direction, exactly5deg from V1 and at most8cm displacement of ANY original
gun vertex. Check actual full-gun/hand silhouette, not only one stock point's
screen gap. No angle grid or automatic next increment. Source gun scale and all
character bones stay fixed; no independent translation/support IK/digit changes.

## Inputs, ownership and early check

All618 current approved guards remain authoritative. Verify retained V1/V2
proofs/model/renderer bytes before use. Keep V2 failure/evidence unchanged.
Reuse only the reviewed native capture/staging arithmetic, with an explicitly
hashed V3 wrapper/proof in the one existing private SFTP workspace:
Evidence/GermanNPCSmallPivotV3. No model copies or new native packages.

One hidden owned native entry only after process/slot checks. Recreate V1 gun
relative to actual current right hand, pause world, inspect fresh BEFORE top/right
images. Require V1 relative residual<0.01cm/0.01deg/source index locals<0.05deg.
Then apply the one5deg rotation. Gun pivot<0.01cm, scale exact, all character
bones exact, capture drift<0.01cm and current618 guards exact before/after.

## Review, stop and closure

Open fresh after front/right/top/reverse, trigger and full-arm context. The two
old wrist-centered palm detail cameras failed coverage; don't count them as
grasp proof. Use the readable main top/right images and an explicitly labeled
original-pixel crop if a closer presentation helps, not an altered model/mask.

Stop on ownership/source/guard/BEFORE parity mismatch, unreadable main view,
over-budget gun displacement, wrong collision or240-second native deadline.
Complete contact remains unaccepted; neither a fixed pivot nor a small angle
proves skin clearance. No automatic second angle, new translation or finger/left
support compensation. Close only owned editor normally and release Lane A.
No formal map/package save, Allied/FP/B/AI edit, Catalog/release, source deletion,
Git commit/push or motion/gameplay/performance acceptance.

## Completed comparison

The one5deg comparison completed without source/guard mismatch. See
`GERMAN_NPC_SMALL_PIVOT_V3_RESULT_20261006.md` for actual measurements,
visual limitations and normal native closure. No further fit is authorized by
this completed plan; await user review.
