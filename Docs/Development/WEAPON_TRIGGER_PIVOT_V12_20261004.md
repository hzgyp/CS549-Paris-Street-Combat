# V12: fixed firing hand, trigger-pivot rifle, following support arm

4 October 2026. [Chinese review](WEAPON_TRIGGER_PIVOT_V12_20261004_ZH.md).
Status: ONE offline candidate completed and STOPPED at contact screening; no
selection. Later actual evidence: WEAPON_TRIGGER_PIVOT_RESULT_20261004.md.

## Authority, reviewed cases and changed mechanism

Yupu authorizes the order RIGHT hand -> rifle -> LEFT support arm -> eventual
assembly aiming. Rotation/raising are permitted, not translation only. His
approximately 10-degree turn toward the firing hand is a visual hypothesis,
not a measured final setting. Read HANDOFF/current Git, Failures/README and full
AN003/AN004/AN005/FP001 analyses, V2/V3 contact and V11 results; reuse the inspected
DVIDS/UNT M1 reference observations in WEAPON_CLOSED_GRIP_REFERENCE_V6_20261004.

V1 gun translation broke fixed left support; V2 constrained both hands and did
not clear the complete firing-hand grasp. V11 translated the whole right wrist
with source-length IK but increased wood/blade crossings. This attempt keeps the
RIGHT chain and approved index completely fixed, turns the rifle about its actual
trigger contact, then lets the LEFT chain follow the new rifle frame. It does not
repeat V11 offsets, V7-V10 digit solvers, AN004 transitions or AN005 weights.

## Scope, inputs and storage

- Baseline: D059 Aim Reload 0s, V2 calibrated M1 transform, V3 accepted index
  LOCAL rotations; other digits retain original D059, not failed thumb/grip fits.
- Blender character workflow: actual skin/surface contacts, fixed multiview
  comparisons and wrist/forearm continuity; no from-scratch character/action.
- New tools: Tools/Integration/WeaponTriggerPivotV12/. Private results/blend/
  renders: the single SFTP workspace Evidence/WeaponTriggerPivotV12/.
- Preserve source model/topology/UV/material/rig/weights/actions, camera, all
  right-chain component matrices and all finger LOCAL matrices. Rifle scale 1.
  No UE authoring/map selection, NPC copying, Catalog/release/commit/push.
- No engine reservation; offline Blender only. Later native work needs a new
  runtime plan and serialized editor-slot coordination.

## Execution and first falsifiable check

1. Read-only geometry probe: identify the existing actual index-pad/trigger
   contact, rear wood/stock-neck surface and inward firing-palm surface. Retain
   face IDs and positions; do not call finger-bone means an empty grip cavity.
2. ONE user-informed 10-degree pivot comparison. Determine the 3D turn axis/sign
   from the actual rear stock-neck -> firing-palm approach direction, not an
   arbitrary Euler axis or a rotation/offset grid. The pivot remains fixed in
   component space; translation of the gun origin follows the rotation about
   that pivot, not a detached free translation. This can raise/roll/yaw the gun.
   Record this as a bounded partial seating hypothesis, not exact full closure.
3. LEFT hand goal follows the same rigid rifle transformation (position AND
   orientation). Solve existing upper/lower left arm at original bone lengths,
   original elbow bend side, no stretch; fingers retain all local transforms.
   Rifle never derives its new target from that corrected left hand.
4. At fixed 0s, compare actual skin: per-digit wood/guard/blade crossings,
   actual index pad gap, left support relative skin, bone lengths, new severe
   wrist/forearm edges. Right evaluated skin must remain exact. First gate:
   pivot error <0.001cm; right skin <0.0001cm; finger local delta <1e-10;
   bone-length error <0.001cm; left contact-patch tracking <0.02cm; no new
   severe edges (>3x and >2cm extra); index stock/guard remain zero, blade
   crossing faces do not exceed baseline22, pad gap <=0.2cm; total non-index
   wood crossing faces do not increase and no previously clear digit becomes
   penetrating. Counts are screening evidence, not depth or visual acceptance.
5. Render matched right/opposite/top/bottom/oblique, whole rifle and continuous
   arms. Inspect actual images, including hidden-side grasp; stop on increased
   penetration, detached cuff, collapsed joint or still-incomplete enclosure.
   Preserve known source shoulder sheets; do not hide/cut/remodel them.
6. Retain a new static comparison blend and fresh-open it independently to verify
   saved geometry and hashes; verify all528 current recovery guards. A frozen
   comparison is not an exported playable rig, animation or gameplay pass.

## Stop and rollback

Stop after this one candidate if any contact/continuity/visual gate fails. No
rotation sweep, increasing the angle, additional translations, individual-digit
correction, changed weights or relaxed gate. Preserve failure and all old assets,
no source rollback/deletion. If static grasp passes, record human-review status
before expanding to continuous movement/reload and overall aim. This first static
experiment does not authorize rigid whole-body framing offsets/ADS or changing
gunplay spatial inputs without near-wall/lifecycle regression.
