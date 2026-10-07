# Closed-grip V7: contact-envelope constrained local adaptation

Latest status,4 October23:06 EDT: user-paused, unselected. No further digit fitting;
see the pause/whole-wrist assessment in `WEAPON_CLOSED_GRIP_RESULT_20261004.md`.
The authorization wording below is historical, not permission to resume.

4 October2026. User explicitly resumes micro-adjustment of the coherent grasp.
Chinese review: `WEAPON_CLOSED_GRIP_MICROADAPT_V7_20261004_ZH.md`.

Read HANDOFF/current Git, failure index, AN003/004/005, FP001, rejected coarse
left-finger layer and V6 closed-grip result/localization. Reuse the actual DVIDS
M1/UNT references already inspected; their hidden finger angles are unknown.
This is a bounded existing-asset display adaptation, not a new action or detailed
character-production restart. V6 remains failed/unselected; old bytes stay intact.

## Changed mechanism and contract

V6 fixed two patch centroids to independently projected surface locations. That
soft target solve leaves distal intersections and insufficient bottom enclosure.
V7 does NOT repeat those targets, scan angles/offsets or merely enlarge limits.
It constrains the evaluated digit envelope (vertices, triangle edges/centroids),
using actual nearest stock surface; contact patch distances may slide along that
surface rather than chase fixed centroid targets. Sequential local constraint
projection gives nonpenetration priority over contact tightening/pose deviation.
Final exact triangle intersection still decides acceptance, not a signed proxy.

Keep accepted V3 gun fit/index local rotations AND evaluated index skin exact.
Only middle_02/03 and ring/pinky_01/02/03 local rotations adapt. Middle_01 is frozen
because four index-root vertices share its weights. Copied V5 thumb is an upper
contact hypothesis, not accepted whole-grip content; its rotations remain fixed
this attempt. Preserve wrist/palm/left arm, bone lengths/translations/scales,
mesh/weights/UV/rig/source actions/camera/transactions. Bounds stay30degree versus
existing D059 for first/second joints,20degree distal, as V6; no relaxed thresholds.

## Order / storage / early gate

1. Read-only stock topology/envelope proof under new `surface_probe_v7` identity.
   Validate reflected outward normals and surface closure/uncertainty; do not
   infer a global solid from an open upper-stock patch.
2. One bounded constrained solve, new `envelope_fit_v7`; use V6 only as diagnostic
   initialization with immutable existing D059 rotations as the deviation basis.
   At most24 local iterations per digit, small trust steps; no pose-grid renders.
3. Early check: source/index invariance, bone bounds, no new severe skin edges,
   exact thumb/middle/ring/little gun crossings0 at eight recorded phases. Report
   retained approved index blade intersections separately, do not alter them.
4. Inspect side/top/BOTTOM/oblique and full weapon/arms in affected phases against
   real grasp relationships; a fingertip minimum gap alone cannot pass. Check
   neighboring finger volume/spacing and contact patch coverage explicitly.
5. Fresh Blender read of the final copied scene/pose and528 native guards.
   Deliver images and reproducible local rotation metadata, not native adoption.

Evidence ONLY in existing single private workspace `Evidence/WeaponClosedGripV6/`;
tools in `Tools/Integration/WeaponClosedGripV6/`. No new asset storage duplicate.
No UE writer/reservation, NPC/B6/BT/BB change, formal map save, Catalog/release,
gameplay integration, packaging, commit or push. No cloud/purchase/new source clip.

## Stop / rollback

Stop on source/index change, untrusted surface sign, repeated non-improvement,
bounded solver failure, remaining actual crossings or visible collapsed/torn skin.
Preserve failing outputs unselected, don't overwrite V6 or original assets. If
protection prevents fit, localize the limitation before requesting a scope change;
do not presume changing weights, gun or index is necessary. Passing offline poses
does not prove continuous UE reload/transition/lifecycle/contact acceptance.
