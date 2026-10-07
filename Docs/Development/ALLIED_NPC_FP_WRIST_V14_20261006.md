# Allied NPC right arm — approved FP directional reference V14

6 October 2026. Requested local static comparison, NOT formal adoption.

## References, scope and failure cases read

Read current HANDOFF/Git/611-row checkpoint, V13 plan/result, approved FP V21
result/config, V19 existing-hold selection/native socket probe and native C++
holding implementation, weapon-hand guide, failure index, FP001, AN002,
AN006 and AN007, and Blender character/execution/form-fit guidance.

FP001: do not distort the accepted gun/hand/camera to hide an arm issue.
AN002: use immutable full source skin cache, never live native skinned-vertex
queries. AN006/007: raw full-body offsets/quaternions or a static image are not
proof of usable motion. Do not rerun stopped FP/action authoring/proofs.
V13 kept contact but its original elbow-plane solution produces a conspicuous
right forearm-to-hand bend. Preserve this result as the comparison baseline.

## Mechanism and contract

Reference the APPROVED FP Ready holding source: existing licensed D059
`W2_Stand_Aim_Idle_IP`, deterministic fraction0 in retained native probe.
Verify its file inventory and the actual approved V20 configuration/native
holding code. The native display keeps this source's right-arm locals; the
camera assembly transform is rigid. Measure the unit elbow-to-wrist direction
IN hand_r coordinates, not FP world offsets, gun attachment or raw local q.
This is a source-derived directional analogue, not a new FP runtime test.

V13 axis diagnostic: forearm vs hand_r local -X approximately82.19degrees;
FP source approximately13.70degrees. These are reproducible rig-axis angles,
not clinically measured anatomical flexion or complete contact acceptance.

ONE original-length right-arm solution, actual native V13 baseline:
keep right shoulder origin AND hand_r world transform fixed. Preserve the
rifle, both wrists, all digits and entire left chain exactly. Choose the elbow
on its two-bone reach circle minimizing directional discrepancy to the FP
analogue, subject to elbow Z <= original right shoulder Z. The unconstrained
solution would place the elbow above the head; it is rejected analytically
BEFORE skin authoring, not rendered/adopted. Constrained circle-plane projection
has at most two boundary points: select the closer reference direction, not
an iterative angle sweep. Only upperarm_r/lowerarm_r and their existing twist
descendants may change; hand_r and its descendants are explicit fixed targets.

This cannot reproduce FP's exact wrist angle with the current frozen grip
and shoulder geometry. Expected comparison angle approximately57.88degrees,
elbow at shoulder height rather than above head. Inspect the silhouette; do
not label numerical improvement as natural posture acceptance.

Original full model/rig/weights/topology/UV/materials/actions, accepted FP,
B/German/AI/gameplay/formal map/Catalog/source inventories protected. No new
animation, finger changes, standalone wrist translation or source pose save.
Private diagnostic JSON/NPZ only; not a replacement playable rig.

## Early checks and stopping condition

Before UE: original arm lengths within0.01cm, fixed gun/wrists/protected bones
within0.001cm, all digit-local/skin contacts unchanged, unaffected skin exact;
new severe edges0 using existing >3x AND >2cm-extra test. Elbow must not exceed
shoulder height. Record mixed forearm/hand cuff skin changes explicitly.
Fresh clean-process reconstruction and all retained-input/611 guards required.
Stop if any fail; preserve evidence, do not change weights/fingers/gun to pass.

Then claim serialized lane A only after no actual engines/current guards.
One unsaved paused full-source native viewer: first reproduce V13 in side and
wrist detail; compare real baseline images before applying candidate. Capture
matched sides/front/reverse/top, close wrist/elbow/shoulder and complete-body
views. Review sleeve continuity, elbow/torso/head intersections and grip.
Stop on new severe deformation/unnatural high elbow/capture mismatch or guard
failure. No automatic second pole/arm/assembly offset scan. Native transform
checks do not establish skin correctness or motion acceptance by themselves.

Normal owned engine exit, fresh guards and explicit slot release. No source
package/map save, adoption/deletion/publication/commit/push. German waits for
Allied review; motion and human acceptance remain separate/unrun.
