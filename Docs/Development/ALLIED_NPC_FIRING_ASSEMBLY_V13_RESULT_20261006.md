# Allied NPC — whole fitted firing assembly V13 result

6 October 2026. Local static comparison complete, not formal adoption or motion
acceptance. Plan: `ALLIED_NPC_FIRING_ASSEMBLY_V13_20261006.md`.

## Requested change and measured preservation

Read current HANDOFF/Git/asset-sync, failure index, AN002/FP001, V12 plan/result,
weapon-hand guide and Blender character/execution/form-fit instructions. User
explicitly requested BOTH arms repositioned while preserving existing hand–gun
relationships; this is not more gun-to-hand fitting or finger correction.

ONE rigid transform from actual native V12:33.106degree downward rotation,
same horizontal heading, rear butt center placed at measured original right
shoulder clothing surface plus0.15cm outward clearance. Barrel elevation
33.106 -> approximately0degree; actual muzzle37.129cm lower. Both original-length
upper-arm/forearm chains follow their original elbow bend planes. Right/left
wrists move16.840/4.761cm. Clavicles/torso/head/legs/IK auxiliary bones remain
unchanged. All existing digit local poses, gun scale/shape, models/weights/UV/
materials/source actions/camera/gameplay and accepted FP/B/German protected.

| Check | Result |
| --- | --- |
| Both hand-relative gun matrices, offline | <1e-12 delta |
| Actual digit skin rigid tracking, right/left | <4.1e-12cm |
| Actual index pad rigid tracking | <2.9e-12cm |
| All ten digit stock/guard/blade counts | Identical BEFORE/AFTER |
| Right index stock/guard/blade | 0/0/10 retained; contact FAILED |
| Original arm segment length error | <4e-13cm |
| Non-arm/digit locals/unaffected skin | <4e-12 delta |
| New severe skin edges / maximum extra edge | 0 /1.457cm |
| Fresh encoded full-skin / gun error | 0.000266 /0.000129cm |
| Actual native right/left gun-to-hand position error | 0.000120 /0.000081cm |
| Actual native right/left gun-to-hand rotation error | 0.000003 /0.000009degree |
| Actual native maximum digit-local rotation error | 0.0000154degree |
| Actual native protected bone position | 0cm |
| Current combined guards / retained inputs | All611 exact / exact |

Mixed hand/forearm/cuff weighting means not every positive hand-influence vertex
moves rigidly with the assembly. ALL positive-weight maximum residual is
14.212/14.716cm; hand influence>0.5 max0.928/0.614cm, >0.99 max0.039/0.025cm.
These are retained wrist/clothing deformation readings, not detached hand meshes
or a claim that all hand skin is unchanged. Actual digit/contact skin is exact;
arm/cuff continuity is reviewed visually below. Source weights were not changed.

Because rotating arms deforms shoulder clothing too, the final actual shoulder
surface is0.360cm from the rear-butt center, rather than the initial0.15cm target.
Nearest distance does not prove full butt-surface seating or closed-solid
clearance. No additional fit/offset is applied. Existing right blade and other
digit/stock overlaps remain: rigidly lowering the assembly cannot repair them.

## Native visual evidence and limits

One Blender process normal exit0. Fresh full cache reconstruction/source triangle
and transform checks passed. One serialized unsaved frozen native entry
`firing_assembly_native_v13`, owned PID24840 normal exit0. Original V12 two-view
baseline opened before candidate/early gate accepted; no live native skin query,
FP binding or source NPC driver edit. Native readback reproduces the saved poses
and approximately0degree barrel elevation. All15 original1600x1000 images and
four labeled sheets opened/inspected. Full original mesh/materials retained.

Side/reverse/overview show a horizontal rifle near the right shoulder, complete
arms/cuffs and a lower supporting elbow; no obvious detached wrist, torn sleeve
or new giant sheet observed in these STATIC views. Right sleeve passes close to
the cheek; this is not an independently accepted ADS/eye/sight line. Shoulder
close-up is partly obscured by the right forearm, so it is not complete butt
clearance proof. Top crop trims the muzzle; the complete rifle is visible in
side/reverse/overview instead. Broad body views include legs/boots but trim the
helmet top slightly; upper-body context separately covers the full helmet.
Retain these framing limitations, not full-object proof from a single view.
Existing trigger/pad contact remains visible in reverse detail. Native wood/skin
texture detail varies over captures, not an authored material/texture change.

Private output: `Evidence/AlliedNPCGripV2/firing_assembly_v13` offline JSON/full
geometry/fresh read, and `firing_assembly_native_v13` actual native images/pose/
verification/presentation. Diagnostic NPZ is NOT a replacement playable rig.
Optional read-only trimesh inspection failed because the library is unavailable;
no install or pose correction. A numpy exact triangle-plane/edge closest-point
calculation verified the final shoulder distance. Earlier failures retained.

## Handoff

All611 guards/input hashes exact, no UE/Blender processes, lane A RELEASED.
No formal map/package save, asset selection, deletion, release/Catalog change,
Git commit/push. German remains deferred until Allied review. No automatic
further arm/pivot/digit/offset fit or stopped FP/action/skin-query rerun.
Human whole-pose acceptance and movement/fire/recoil/reload/lifecycle/FPS/build
checks remain unrun; this finishes the requested static pose comparison only.
