# Allied NPC — corrected upward rotation V9 result

5 October 2026. Completed one requested static comparison; complete contact
is NOT accepted. German remains deferred. Plan:
`ALLIED_NPC_PIVOT_ROTATE_V9_20261005.md`.

## Authority, reviewed failures and changed method

User corrects “raise” to upward ROTATION. Reviewed current HANDOFF/Git/611
guards, Failures/README, AN002, FP001, V7 native display-parity failure and its
V7b correction, V8 correction addendum, English weapon-contact guide and
Blender character workflow. One extra2degrees starts from ACTUAL native V7b
final, around the marked stock-grip pivot and original measured upward axis.
V8 translation/left-arm pose is NOT consumed. No independent translation,
angle sweep, digit adjustment, new action or first-person binding.

V8 remains superseded/unselected: its PID48820 was absent after interruption,
session unavailable and no native result directory existed. OS exit UNKNOWN;
no successful V8 native comparison, automatic rollback or editor termination
is claimed. Retain its offline trial and partial launch log.

## Early acceptance and stop

The plan's fixed-pivot, right/unaffected skin, digit-local, original-length
left-arm tracking and severe-edge checks passed before native viewing. One
native baseline-image gate accepted actual V7 pose, not a reference-pose render.
Full contact still fails; stop further fitting and retain this one honest
comparison. No automatic second angle/translation/finger compensation or
threshold relaxation.

## Actual offline and native checks

Offline full-source LBS:44,852vertices, original triangles/rest/weights/UVs and
materials. Three reviewed pure V7 helper functions were extracted without
executing its old top-level author. Full original-length left shoulder–elbow–
wrist follows rigid gun rotation; shoulder/clavicle, right arm and all digit
locals stay fixed.

| Check | Actual result |
| --- | --- |
| Additional rotation / muzzle rise | 2degrees / 2.345155cm |
| Offline fixed-pivot drift | 1.02e-12cm |
| Right and unaffected skin delta | 4.91e-12cm |
| Digit local matrix error | 1.82e-12 |
| Left palm tracking / segment-length error | 2.73e-12cm / 1.88e-13cm |
| New severe edges | 0; maximum extra edge0.161901cm |
| Native additional rotation | 2.000001degrees |
| Native protected bone position/rotation delta | 0cm / 0degrees |
| Actual native marked-pivot drift | 0.000110cm |

Contact BEFORE→AFTER uses actual geometry, not an anchor-only claim:

| Contact | V7b | V9 |
| --- | ---: | ---: |
| Index pad–trigger blade distance, cm | 0.281719 | 0.491565 |
| Index stock/guard/blade crossing faces | 89/5/18 | 94/6/20 |
| Thumb stock crossing faces | 59 | 58 |
| Middle/ring/little stock crossing faces | 21/30/36 | 23/40/51 |

Thus this extra upward rotation does NOT improve the measured pad–blade
distance or close complete contact. These counters do not establish that every
possible rigid fit is impossible. Do not relabel a successful transform as a
successful grasp.

## Actual presentation and self-review

New identity `pivot_rotate_native_v9`; owned PID35004 closed normally, launcher
exit0. Uninitialized frozen native container uses full original US mesh and UE
materials, paused Poseable refresh and pre-capture delay; no BindExistingPose,
source NPC driver edit, first-person hand/config mechanism or map save.
Nine original1600x1000 views and all three2400x660 labeled sheets were opened.
Baseline/right/trigger precede candidate front/right/top/trigger/reverse/full-
arm, followed by matched baseline full-arm context. Public bone parity maximum
position1.42e-14cm, angle0.000052degrees, scale0.

Visual self-review: muzzle visibly pitches slightly farther upward and left
support follows with continuous wrist/cuff/elbow/shoulder in these static
views. Right index remains extended along the stock/upper guard; correct
fingertip–blade contact is NOT established. Other grip/intersection limits
remain. Texture detail differs between captures with unchanged material paths;
no retouch or authored texture improvement/cause diagnosis is claimed. Static
continuity is not motion, AI integration or gameplay acceptance.

Private evidence root (ignored; not public commercial-asset publication):
`Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/AlliedNPCGripV2/`.
`pivot_rotate_trial_v9/` retains full diagnostic geometry/result;
`pivot_rotate_native_v9/` retains original PNGs, early acceptance, result,
verification and comparison/three_views/arm_context sheets. The native result's
inherited scope text mentions V6/V7; its actual identity, inputs and transforms
are V7b→V9, as verified here. No replacement rig or native package was authored.

Fresh verifier: all611 current A+B recovery guards and retained input hashes
exact;9distinct actual images and native transforms verified. No UE/Blender
processes remain; lane A native slot RELEASED. Original model/rig/weights/
actions, approved FP, German/B/BT/BB, formal map/Catalog and gameplay transactions
unchanged. No selection, deletion, publication, Git commit or push. Await human
marking; no further adjustment is authorized by this completed comparison.
