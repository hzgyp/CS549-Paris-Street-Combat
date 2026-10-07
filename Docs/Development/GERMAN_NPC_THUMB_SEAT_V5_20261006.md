# German NPC thumb seating V5

6 October 2026. New user instruction: keep left support/gun and the index-trigger
contact together; position the stock under the unchanged right thumb. This
supersedes V4's stop only for a new measured thumb-seating comparison. No formal
selection, source model deformation, new animation or individual-finger editing.

## Cases read / what changes

Read HANDOFF/current618 guards, Failures index, GP010, AN002, AN008, V4 plan and
result, weapon-hand calibration guide/right and left supplements and character
workflow. V2 excessive37.6deg and V4 failed fixed-hand pitch/final clearance are
retained; do not rerun their angle/offset mechanisms. The new target is actual
upper stock contact below the fixed thumb, not a palm cavity guessed from a
nearest point or further whole-left-arm retreat.

Starting revision is V4 offline_v6/ordered_native_v2 (not failed clearance_v7).
Interpret the preserved index/trigger relationship as a fixed actual trigger
contact point while the complete rigid rifle rotates around it. Right hand,
right arm and ALL finger bone locals/worlds remain fixed. The left whole arm
follows the gun, preserving its current grasp relative to it through original
segment-length IK. The stock is not bent/moved independently from the gun.
This preserves contact location, not every triangle's orientation or complete
right-index clearance; measure those changes instead of claiming them exact.

## Bounded sequence and early check

1. Read retained full-skin/weights/topology/gun cache, source hashes and actual
   bone hierarchy. Inspect thumb/index/stock in diagnostic projections, recording
   actual skin and upper wood surface landmarks and outward-normal parity.
   No live native skinned-vertex queries or source reimport/edit.
2. From actual geometry find one minimal rigid rotation around the fixed trigger
   anchor that places upper stock below the distal right-thumb pad with a small
   outward clearance (nominal0.05cm). Use surface constraints, not an angle grid,
   projected arrow endpoint, arbitrary wood bounding box or Allied coordinates.
   Maximum15degrees new rotation. Preserve source gun shape/scale, fixed firing
   arm/hand/digits, torso/legs and existing materials/actions/FP/Allied/B/map.
3. Whole source-length left-arm follows this rigid change, current digit locals
   unchanged. Record true positive-influence mixed skin tracking, actual thumb
   stock crossings, trigger displacement/clearance and left contact. Stop on
   unreachable arm/new severe sleeve edges, lost trigger anchor, enlarged thumb
   penetration, cap violation or a visibly incompatible grip. At most one
   minimal constraint solve; no failed-angle/offset/finger retry.
4. If offline contact improves, reproduce baseline/candidate unsaved in one new
   owned serialized native entry. Open original thumb top/reverse/side details
   and full-arm/front/right/top. Native point/pose parity limits0.01cm/0.01deg;
   actual staged gun NoCollision. Close own editor normally/verify618 guards and
   source hashes/release slot, then hand off human views without formal adoption.

## Stopping condition / deliverable

The thumb must sit visibly above the stock without new severe penetration; the
index contact anchor and current left grasp must not be silently exchanged for
thumb improvement. A valid numeric surface point is not full grasp/animation
acceptance. On failed constraints retain result and stop rather than deforming
stock/fingers or shifting detached mesh pieces. Preserve V4 small cuff artifacts
and other known contact diagnostics without reopening their repair scope.
No UE packages/map/source edits, native motion proof, SFTP immutable release/
Catalog selection, deletion, Git commit/push. Evidence/tools/result documentation
only. Human/static and playable-motion acceptance are separate.

## User pause / superseded scope

User paused this gun-transform route after seeing measure_v1's actual-vertex
plot, then identified the original RIGHT thumb pose as the defect. No fitting,
gun transform, bone adaptation or native entry was executed under V5; only
cached read-only measurements/PIL projection (initial matplotlib import failure
retained). The new instruction explicitly starts thumb-pose-only V6. Do not run
this V5 gun-seating plan on resume; gun/left/index/right wrist are now protected.
