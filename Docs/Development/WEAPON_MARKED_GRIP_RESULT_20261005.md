# V16 — marked grip pivot brings index to trigger; clearance still open

2026-10-05 00:11 EDT. [Plan](WEAPON_MARKED_GRIP_PIVOT_V16_20261005.md).
One offline rigid-gun candidate from V14, not native/game selection.

## User-marked pivot and result

User arrow on the scaled V14 oblique image maps approximately to original pixel
(591,545). Exact saved diagnostic-camera projection raycasts actual stock face
1225 at baseline-frame(-7.069780,-6.143180,-1.509192)cm; gun-local
(-0.225999,-7.407037,2.679976)cm. The red marker original image was inspected:
it lies in the user-indicated stock/palm holding area. Approximate screenshot
mapping is guidance, not precise metrology; no point grid or alternative marker.

A transverse-only rotation would retain0.898192cm side mismatch. Before authoring
we documented minimal 3D rigid rotation about the SAME fixed point instead, with
no gun/pivot translation or finger change. Additional rotation16.163076degrees;
muzzle highest-forward vertex height increases24.393886cm in diagnostic frame.
Pivot error0, original right skin delta1.543e-13cm, digit local matrices4.264e-14.

Actual index pad/blade distance improves2.267353→0.081402cm (about0.8mm).
Index/wood58→0; index/guard0→23 and blade0→17. Blade landmark radial residual
0.116471cm is not forced away by translating pivot or reshaping a finger.
The index visibly enters the trigger region, improving this requested relation;
guard intersections remain, not a fully cleared trigger assembly.

Thumb/wood0→51 intersection faces, so V14's thumb clearance is NOT preserved.
Middle/ring/little wood64/70/62 are reported/non-gating under the user scope.
Intersection face counts do not establish penetration depth or exact affected
phalanx; do not infer a root-only cause without a separate surface-depth audit.
Actual full grasp/contact acceptance remains false; no individual digit correction.

Left support source-length IK has bone-length errors<=3.56e-15cm, no new severe
edges, max extra edge length1.416584cm. Skin-palm tracking0.041080cm vs V14
0.029614cm, exceeding the declared +0.01cm relative screen by0.001466cm. Preserve
this failure and the old V14 absolute0.02cm failure; no threshold relaxation.

## Visual, fresh and protection checks

14 original matched before/after images are preserved; all-view sheet and hero
inspected, plus final both sides/top/bottom/oblique/left support/full continuous
arms originals. Fixed colors identify thumb/index/support. Full arms retain old
shoulder sheets; close views isolate hand triangles for diagnosis, not a source
mesh cut, mask, camera move or defect removal. Final left-support crop partly
leaves the frame as gun rises; whole-arm view supplies continuity context, not
complete finger-contact or gameplay acceptance. No visual perfection claimed.

Independent fresh Blender read exit0/errors[]: source72bones, hands/arms max
vertex difference1.994e-6cm, gun3.392e-6cm; blend and inputs unchanged. Static
evaluated diagnostic geometry is not a playable rig/new motion/UE export.
Blend SHA a315ac196dc5b315b2fab9ed38074edc47582f90ffbe013a29d1cca253aa488f.

Final verification timestamp is04:11:21 UTC /00:11 EDT.
528 current recovery size/SHA records match; old10/20/14/15 inputs/code/blend
proofs preserved, known unselected V6 saved-rate difference remains in snapshot.
Formal map2707948bytes/SHA2791b4a7f76b4b3d07f42286b6ad0156c3a185c2e3e795fa2446aaac0ad68519.
5 new scripts AST pass; no task error/native author. Candidate retained unselected,
no engine process, UE slot/B/NPC/BT/BB/formal map/Catalog/release/package/cloud/
commit/push changes. All evidence only single SFTP workspace WeaponMarkedGripV16.

## Interrupted V15 state (not a rollback)

V15 initial source stopped before rotation: face-center near patch not found.
One documented vertex-edge measurement entry v1b actually completed during the
user tool interruption: result/errors[]/blend14renders exist, engines absent;
OS exit code was not delivered by that interrupted call, do not assert exit0.
Its inferred section pivot(-6.293373,-5.129329,-5.115264)cm and17.479745degrees
produce thumb51wood/index74guard/gap0.884671cm; left tracking0.043453cm. Retain
failed result/source, not inspected as a human-approved candidate and not resumed.
V16 starts from V14 and the user's NEW indicated pivot, not from V15 geometry.

Next is user comparison. This single marked-pivot mechanism stops at actual
thumb/guard/continuity gate; no automatic angle/twist/translation/digit/weight
compensation or game/aim integration. A different measured follow-up needs its
own bounded scope; this is not evidence that all gun-only fitting is impossible.
