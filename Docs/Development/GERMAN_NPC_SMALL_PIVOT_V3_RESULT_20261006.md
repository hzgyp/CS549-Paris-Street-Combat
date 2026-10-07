# German NPC small trigger-pivot correction V3 result

6 October 2026. Bounded static comparison completed; awaiting human review.
The user rejected V2's37.6deg as excessive. V2 remains rejected and unselected;
its original evidence is retained. This result does not establish full grasp.

## Scope and cases

Follow `GERMAN_NPC_SMALL_PIVOT_V3_20261006.md`. Read Failures/README.md,
GP010, AN002, AN008, German V1/V2 records and the weapon-hand calibration
guide. Character workflow informed actual multiview and bone preservation.
The change is a small angle/whole-rifle displacement budget, not another
arrow-endpoint fit or a retry of V2's stopped angle solver.

Reconstructed V1 translation-only alignment, then ONE -5deg rotation in the
same direction around the same actual trigger point. It is not37.6deg minus5.
5deg was chosen as a modest feedback comparison, not a solved grasp angle.
Hands, arms, all character bones and gun scale remain fixed. No independent
translation, finger edit, support IK, material/mesh/weight/action edit occurred.

## Early check and actual measurements

Fresh original BEFORE top/right views were inspected before the move.
V1 relative gun position residual0cm, quaternion residual0.000003415deg and
source index locals0 passed the planned early check. Retained V1/V2/model and
reviewed renderer bytes were verified; V2's candidate transform was not used.

- Requested5deg; measured native rotation4.999997918deg.
- Native trigger-pivot residual0.0000005654cm; all character bones exact.
- Maximum displacement of16107 original GLB vertices:5.611639cm, below8cm.
- Marked stock/palm projected reference gap6.693808->5.937824cm; this screen
  measurement is not a skin-clearance or full-contact test.
- All ten captures have0cm gun drift; existing weapon NoCollision verified.
- All618 current approved guards exact before and after; approved Allied/FP
  initialization and B dependencies preserved. No historical map rollback.

## Visual review and limitations

Opened ten native originals and three labeled sheets. Main front/right/top,
reverse, trigger closeup and full-arm context are readable. The5deg comparison
avoids the previous large apparent yaw; right palm enclosure remains incomplete,
the index stays straight and fixed left support is still unseated. Do not claim
the gun is fully gripped or that every finger/guard overlap is resolved.

The two inherited wrist-centered detail cameras still crop the grasp or show
torso occlusion. They are retained as coverage failures, not hidden-contact
proof. Main top/right views are the basis of review; no camera/fitting retry.
Material-detail variation is native capture variation, not texture authoring.

`angle_comparison.png` labels the previous37.6deg view REJECTED/old capture;
its different capture phase is not presented as an identical native frame.
`three_views.png` and `trigger_context.png` show the fresh V3 candidate.

## Closure and next boundary

Private evidence: `Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/`
`Evidence/GermanNPCSmallPivotV3/small_rotation_v1/` (result, early acceptance,
presentation hashes and original PNGs). Owned PID47628 normal exit0 is recorded
in `tmp/german-npc-small-pivot-v3/small_rotation_v1.log.exit.json`; no UE/Blender
engines remain and Lane A is RELEASED after exact guard verification.

Formal Germans remain unarmed. This existing weapon was staged unsaved only.
No package/map save, formal selection, SFTP immutable release/Catalog change,
source deletion or Git commit/push occurred. Motion/reload/recoil/gameplay,
performance/Shipping/second-machine tests were not run or passed.

Stop here for user review of the smaller angle. No automatic second increment,
arrow solve, translation, finger/arm compensation or formal adoption. Preserve
V1/V2 inputs and both rejected-method/camera-coverage evidence.
