# Allied NPC — preserve fitted hands/gun, lower the firing assembly V13

6 October 2026. Owner: lane A / Yupu. Current V12 is a static comparison,
not an accepted full grip. User now explicitly requests keeping both hand–gun
relationships while repositioning BOTH complete arms to a normal firing pose.

## Reviewed evidence and changed hypothesis

Read HANDOFF/current dirty Git, asset sync manual, Failures/README, AN002,
FP001, V12 plan/result, the weapon-hand calibration guide and Blender character
workflow/execution/form-fit references. Earlier gun-only rotations changed
contacts; isolated wrist movement could separate the arm. This attempt instead
applies ONE common rigid transform to the actual native V12 gun and both wrist
hierarchies, then solves both original-length shoulder–elbow–wrist chains.
No stopped finger, gun-seating, FP, action or native skin-query route is rerun.

## Bounded contract

- Source: actual `tip_curl_native_v12/result.json` after pose, immutable original
  full skin/weights cache and actual M1 geometry. Keep V12 finger locals exactly.
- One inferred ordinary forward-firing target: near-horizontal barrel (0 degrees
  world elevation, same horizontal heading), with the actual rear butt surface
  placed at the right shoulder's existing outer clothing surface. No ADS/head
  or torso correction; this is a static ordinary firing comparison, not a claim
  of exact historical posture, eye/sight alignment or gameplay aim acceptance.
- Preserve gun size/shape, both inverse(wrist)*gun transforms and digit locals.
  Change only two upper-arm subtrees; clavicles/torso/head/legs stay fixed.
  Two-bone IK retains original segment lengths and each source elbow bend plane;
  no bone/hand scaling, detached mesh shift, source weight or action editing.
- Original textures/materials/UVs, approved first person, German, B/AI,
  formal map/Catalog/gameplay transactions and all611 current guards protected.
  Outputs are new private ignored evidence only, no formal native asset save,
  selection, deletion, publication or Git commit/push.

## Early falsifiable check and stopping condition

Before UE: reconstruct full source skin; target must be reachable on BOTH arms;
segment length error <0.01cm, non-arm transforms/digit locals <0.00001 matrix
error, wrist-relative gun error <0.001cm/0.01degree, actual digit/grip-skin rigid
tracking <0.05cm, unaffected skin <0.001cm and new severe edges zero (edge >3x
baseline AND >2cm extra). Report all mixed wrist-skin residuals separately;
never call all hand-influenced skin fixed from only a pure-bone mask.
Measure trigger stock/guard/blade intersections BEFORE/AFTER and preserve the
existing failed-contact status: changing the assembly cannot cure relative
penetration. Stop on new digit contact, stretch, unreachable targets, changed
guard/source hashes or a failed native baseline/pose-parity/capture gate.
Do not scan angles/offsets, stretch arms, change fingers or relax thresholds.

If the offline gate passes: freshly check611/no engines, claim serialized A
slot, use ONE new full-source frozen native viewer. Inspect original V12 baseline
before applying candidate; capture matched front/side/top/reverse/full body and
hand/shoulder details. Open actual images, fresh verify all inputs and native
hand/gun relations, close only owned process normally, release slot. Stop after
this complete comparison. Static pose checks do not validate movement, reload,
firing, lifecycle, FPS, packaging or human acceptance.

## Offline checkpoint before native viewing

ONE computed33.106degree downward assembly rotation gives approximately0degree
elevation/muzzle37.129cm lower. Both arm lengths unchanged; right/left wrists
move16.840/4.761cm. Digit skin follows the exact rigid assembly (max4.1e-12cm),
actual index pad2.8e-12cm and both hand-relative gun matrices<1e-12. All ten
digit stock/guard/blade crossing counts identical; existing contact failure
NOT repaired. Non-arm/digit locals/unaffected skin remain exact, new severe
edges0/max extra1.457cm. ALL positive hand-weight skin includes mixed forearm/
cuff influence and has14.212/14.716cm residual versus rigid assembly; this is
NOT proof of hand detachment or of sleeve acceptance. Do not hide that mixed
boundary or label all hand-influenced skin rigid. Actual full-arm/cuff/shoulder
views decide the static visual gate. Fresh reconstructed encoded transforms,
full skin/gun/triangles/retained inputs and611 guards must pass before UE.

Fresh numeric audit: hand-influence>0.5 wrist/cuff skin maximum residual
0.928/0.614cm versus a rigid assembly; >0.99 residual0.039/0.025cm. Exact
digit/contact skin is distinct from these mixed cuff boundaries. Fresh encoded
geometry error0.000266cm/hand-relative gun0.000113 matrix/digit-local0.000416
matrix reflects serialization, below fresh0.003/0.001 gates, not authored scale
or a second fit. Final actual shoulder surface (after the arm rotates) is0.360cm
from rear-butt center; initial0.15cm target does not prove zero penetration or
complete stock seating. A read-only optional trimesh audit lacked the library;
retained that diagnostic failure, no install: numpy triangle-plane/edge closest
point calculation supplies the actual final measurement without changing pose.
Native baseline original two images opened: raised V12 silhouette and current
tip curve reproduce correctly; texture detail variation retained/no retouch.
Early parity gate accepted, not human contact or firing acceptance.
