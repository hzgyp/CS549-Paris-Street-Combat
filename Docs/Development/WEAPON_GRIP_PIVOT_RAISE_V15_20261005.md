# V15 — raise the muzzle around the seated stock grip

2026-10-05. Latest user explicitly resumes a new rigid-gun trial from V14:
keep the right palm, thumb and grasping digits fixed; use their stock-holding
region as pivot and raise the muzzle until the trigger meets the index. No digit
joint edits are authorized/inferred by this request. Not native game selection.

Read HANDOFF/current Git, Failures index, AN003/004/005/FP001 full analyses, V14
plan/result and the reviewed M1 grip references. Unlike V14's downward whole-gun
translation, use the seated stock-neck section as fixed pivot and solve one
minimal rigid rotation toward the unchanged index's actual blade contact target.
Unlike old broad-palm fits, identify the section using actual thumb/wood near
surface pairs; the section center is a gun pivot, NOT a hand cavity proxy.

## Implementation and early acceptance

New code WeaponGripPivotV15; private Evidence/WeaponGripPivotV15 in the single
SFTP workspace. Load original D059 0s/V2/V3 hand and V14 gun transform. Measure a
contiguous thumb-near-stock patch, identify its longitudinal stock section from
actual wood triangles, and use that section center as grip pivot. Thumb and the
three lower fingers are not moved. Preserve source skin/weights/rig/actions.
Compute ONE vector-alignment rotation about this pivot, bounded to 30 degrees
additional turn. Confirm muzzle height increases in the fixed diagnostic frame.
If radial reach differs, report the residual; do not secretly translate pivot,
scale the gun, sweep angle/offsets or bend the index to force equality.

Require fixed pivot <0.001 cm; unchanged right skin <0.0001 cm and all digit local
matrices <1e-10; actual thumb whole-gun intersections 0 and visible above/near
stock; index pad/blade gap <=0.2 cm and index/stock and index/guard faces 0.
Blade-touch faces are reported separately, not equivalent to penetration depth.
Other three digits remain reported/non-gating under the preceding user scope;
do not claim complete grasp from the user's visual observation or numeric proxy.

Left support follows gun by source-length IK; no source weights/pose changes.
Report actual palm tracking versus V14's known 0.029614 cm failed 0.02 cm gate;
do not rewrite that failure. No new severe edges (>3x and >2 cm extra), no arm
length change >0.001 cm, tracking must not worsen by >0.01 cm in this static trial.
This comparative continuity screen does not clear the old absolute native gate.

Render before/after from both sides/top/bottom/oblique, left support and full
continuous arms, inspect originals. Retain original shoulder artifacts. Fresh
open saved static diagnostic geometry in a separate process; not an action/rig
export or reload/movement/aim/runtime acceptance.

If this pivot rotation misses the actual contact/visibility/continuity gate,
retain the single comparison and stop this mechanism, explain residual mismatch.
No hidden translations, finger/weight adjustments, camera shifts, angle grid,
stopped AN004/005/FP001 reruns, or automatic native follow-up. Preserve V14 and
old10/20 hashes plus528 current recovery records (known unselected V6 rate delta).
No UE slot/B/NPC/BT/BB/formal map/Catalog/release/package/cloud/commit/push changes.

## Surface-sampling preflight correction

The first entry stopped before computing any rotation: fewer than three thumb
triangle CENTERS lie within0.35cm of wood. Preserve grip_raise_v1/source/result;
do not claim a broad seated patch. V14's nearest sampled edge/vertex is closer
than its face centers. One new preflight entry uses the actual nearest thumb
vertex/wood pair and its stock cross-section to define the pivot, explicitly
an edge-contact section, not verified whole-grip enclosure. It does not loosen
thumb intersections/trigger distance/rotation bounds or author another gun angle
after a failed candidate. Existing source V1 remains unchanged. All actual fit
and multiview checks above still apply; this is the first computed gun candidate.
