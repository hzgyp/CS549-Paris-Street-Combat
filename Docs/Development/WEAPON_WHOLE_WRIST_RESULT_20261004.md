# Intact-grip wrist approach: comparison retained, not selected

4 October2026. [Chinese review](WEAPON_WHOLE_WRIST_RESULT_20261004_ZH.md).
Plan: `WEAPON_WHOLE_WRIST_V11_20261004.md`. User explicitly resumed the
whole-hand proposal; no individualized digit refinement resumed.

## Actual change and checks

ONE fixed0s existing-D059 pose comparison, with approved V3 index local pose
and V2 gun calibration. Right wrist/whole grasp approaches0.75cm along gun-local
+X; gun stays fixed in the baseline frame. Existing two-bone right arm chain
uses original lengths/elbow side to maintain wrist connection and preserve
hand orientation. No finger curl, source motion, geometry, weight, rig or
camera change; no new action or native asset.

Maximum finger-local matrix delta2.84217e-14 (floating point only); hand
orientation delta0, wrist displacement error2.72938e-15cm, left support skin
delta1.27898e-13cm. Both arm length errors1.06581e-14cm. No new severe edges
under the plan's criterion; max extra edge length0.08959cm. Four checked
nonadjacent digit-pair intersections remain0. These preserve shape/continuity,
not proof of accepted contact or a full deformation pass.

| Actual surface-crossing triangles,0s | Before | Whole-wrist approach |
| --- | ---: | ---: |
| Thumb / wood |45|45|
| Middle / wood |48|61|
| Ring / wood |6|49|
| Little / wood |0|0|
| Index / blade |22|27|

Index/wood and index/guard remain0; the same actual pad triangle is0.05151cm
from the blade before and0.09245cm after. This does not clear the remaining
index blade crossings. Counts are not penetration depth/volume.

**Early contact gate fails.** Whole-hand translation is visibly closer in
top/oblique views, but middle/ring fingers enter the wood more, while underside
enclosure remains incomplete. Source shoulder sheets/spikes remain in whole-arm
views. This candidate is stopped/unselected; do not adopt it, add further
offsets automatically or return to the stopped per-digit solvers. This ONE
direction/pose result is not proof that all whole-wrist fitting is impossible.

## Evidence and technical stops

All evidence in the existing single private workspace's
`Evidence/WeaponWholeWristV11/`, source in `Tools/Integration/WeaponWholeWristV11/`.

- `landmarks_v1`: bone-location mean wrongly used as cavity center;4.76172cm
  target stops at1.5cm cap before pose edit, inputs unchanged.
- Initial corrected-palm launch fails sibling-module import before creating
  evidence; exit0 is not completion. Explicit script import-path correction
  yields `palm_landmarks_v2b`: broad palm-side full-closure target4.53482cm
  again stops before editing; not proof of required C-grasp displacement.
- Documented ONE partial0.75cm approach, `small_approach_v1`: completes exit0,
  errors[], unchanged input hashes.14 fixed-camera before/after images plus
  new static `WholeWristApproach_7p5mm.blend`. Entire paired contact sheet
  inspected; ten original images opened (top/bottom/oblique pairs and both
  whole-arm pairs). Right/opposite views additionally reviewed in the sheet.
- `image_review_v1/before_after.jpg` is a matched oblique/bottom comparison,
  not a new pose or retouched clearance image.
- `fresh_check_v1`: separate Blender5.2.2 opens frozen blend, exit0/unchanged,
  max saved/evaluated vertex error2.03388e-6cm.72 source rig bones, hand object
  retains6135 vertices/4308 selected faces, gun2131 vertices. Static evaluated
  comparison, NOT a playable rig/action export or UE acceptance. Blend SHA256
  `653c67e55490c6cf43603f6765bb79f0a5d4ea8e3d1405ccd89cdf927fc07b4c`.

Blender character workflow guided fixed multiview, sleeve continuity and fresh
read checks. It did not authorize creating fingers/actions or native adoption.
No continuous reload/movement/gameplay/lifecycle/near-wall tests ran.

## Protection / next boundary

23:18:31 EDT:528 current map_recovery size/SHA records match, canonical map
`2791b4a7f76b4b3d07f42286b6ad0156c3a185c2e3e795fa2446aaac0ad68519`
unchanged; known unselected V6 rate difference included in this current snapshot.
No engines remain, no UE slot claimed, B/NPC/controller/BT/BB unchanged.
No formal asset/map selection, Catalog/release/package/commit/push. Preserve
failed measurements, comparison and all earlier work; no source rollback.

User comparison is next. Further placement work must first identify a different
actual stock-neck seating direction/contact mechanism rather than repeat this
side-closure target or simply increase its displacement. Finger local pose stays
protected; no inference that fingers need rebuilding. Native/dynamic integration
requires a separately scoped plan and serialized editor coordination.
