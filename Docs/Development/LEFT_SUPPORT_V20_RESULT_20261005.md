# V20 — existing left-thumb grasp reuse / local native result

5 October 2026. Status: test variant, local approach improved; human review and
complete grip acceptance remain pending. NOT formal adoption or asset release.
Read the V20 plan, AN006/AN007, weapon-hand calibration guide and V19 human
feedback. The character-workflow skill informed source skin/multiview/fresh
and native checks; no character, animation or skin weights were created.

## What changed

The user explicitly permits only the three LEFT thumb local rotations reused
from an existing grasp. New private JSON changes exactly thumb_01/02/03_l.q.
Left wrist, other digit locals, right hand, gun, local translations/scales,
camera, original reload, rest mesh/rig/weights/materials and gameplay stay
unchanged. Source is the retained native D059 AimReload derivative at2.2s,
traced to the mature existing animation, not an untouched vendor clip. Using
three sampled rotations does NOT adopt its old stopped retarget/action owner.
Independent quaternion provenance maximum difference0.000029674degree.

No new .blend, motion, AnimBP or native package. Existing unchanged/default-off
V19 C++ runtime consumes the new JSON; Python prepares once and observes/stimulates
test inputs, never drives the hand pose per frame.

## Retained failed attempt and diagnostic correction

The one intact-left-grasp palm-pivot rotation13.194907degrees/wrist1.246675cm
improves thumb distance but increases left gun-crossing faces44→69/36new.
Stopped before native integration; three failed-pose images inspected. No scan,
larger offset, relaxed contact gate or individual-digit solver followed it.

Recorded source comparisonv1 wrongly classified vertices with0–10% thumb
influence as unaffected. Keep its original no-pass receipt. Source-weight
classification corrected to ANY positive influence; true-unaffected/right
skin remain exactly0. One other-digit-shared vertex moves0.036680cm from its
thumb weight; other-digit bone locals remain fixed. Do not claim neighboring
skin is wholly unchanged.

## Actual verification

- Static source-pose selection: mean sampled pad/wood gap2.511496→1.037860cm;
  this is not complete surface contact. Core thumb crossing faces2→2/self0;
  no new severe edges. All10 before/after side/reverse/under/top/full-arm views
  opened. Thumb turns toward the wooden side; fine clearance remains.
- Fresh Blender no-render boundary audit includes375 positive-influence
  vertices and688 touching faces, including low-influence boundaries. Crossing
  faces8→8/same identities/no new ones, component-matrix difference0, true
  unaffected/right skin0, no severe edges. Existing crossings are NOT repaired
  or accepted by this relative regression.
- Fresh JSON audit: ONLY three q arrays differ, t/s and old config unchanged.
- New serialized hidden native review, PID40300/identity native_review_v1,
  exits0/no timeout. Two unchanged V19 actors bind original and candidate in
  the same callback/source frame. Baseline/candidate Ready views inspected
  before continuing. Five actual city screenshots opened: paired Ready,
  left walk, original reload mid-frame and post-reload Ready.
- Native paired gun/left-wrist position delta0cm, gun angle0degree; unchanged
  digit local error0degree. Ready candidate digit max error0.000002415degree.
  Source-length IK/support match, original camera25/0/60/FOV90 and hand_r
  attachment/authoritative weapon remain intact. Lateral walk300cm/s.
- ONE original reload conserves2/16→8/10 with one commit; corrected thumb
  returns at Ready. During reload the grip override naturally releases to the
  original source, so deviation from the holding q arrays is expected. This
  is NOT a full-fade continuity or all-action/lifecycle test.
-533 current A+B guards, accepted V18 blend, original private config/runtime
  source/binaries and canonical map2791b4a7…ad68519 match after all tests.
  All engine/Blender processes absent; A releases the serialized native slot.

## Remaining limitations / stopping

Actual native Ready/left-walk/post views improve the thumb's outward splay,
but do not establish a completely closed grasp or all-angle contact. Keep
the residual gap and existing crossing evidence for human comparison. No
automatic further thumb-angle fitting or wrist/gun compensation.

Mid-reload large sleeve sheets and a post-reload lower-left fragment remain
visible; explicitly deferred by the user, NOT modified or a passed gate.
Original Reload_2 unchanged. Full return/fade, firing/recoil, life-cycle,
near-wall presentation, FPS/package acceptance remain unrun in this scope.

No formal map selection, superseded-copy deletion, NPC fit/numeric copy,
Catalog/release, commit or push. Do not overwrite original config or source.
Human viewing later needs a separate explicit manual entry and fresh serialized
slot/process check; the stopped AN007 full proof launcher remains locked.

## Evidence location

Private, ignored single SFTP workspace:
`Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/LeftSupportV20/`.
Current candidate: `reuse_pose_v2/binding.json`, SHA256
`04f4588cc6922a907f3aaa2bc60d41dec985240e96d3c6c31f1d32dfde3bc7a7`.
Fresh receipts: config_verification_v1, rotation_provenance_v1,
skin_boundary_verification_v1, verification_v1. Actual game views: native_review_v1.
These are test evidence/config, not Catalog/restore/release authority. Models,
poses and media stay out of Git; only generic code/docs/hash records belong there.
