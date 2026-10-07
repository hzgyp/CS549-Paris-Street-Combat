# German NPC marked translation V1 — static comparison

6 October 2026. Completed the user's ONE whole-gun translation with both hands
fixed. This is a coarse trigger-position comparison, not complete grip or
gameplay acceptance. The formal German remains unarmed; no asset was replaced.

## Scope, cases and early check

Followed `GERMAN_NPC_TRANSLATION_V1_20261006.md`; read AN002, GP010, AN008,
the native baseline/Allied translation records and the complete weapon-hand
calibration guide. The character workflow supplied source-preservation and
multiview checks, not character generation or a new pose solver.

Used the actual accepted German V15 GLB/Trigger_Donor geometry and existing V2
attachment, not Allied/player offsets. Original import bounds reproduce within
0.00000336cm. Initial raw screenshot registration failed RMS0.07958 and stopped
before launch; its evidence is retained. One presentation-only multiscale
initialization passes the unchanged 0.035 raw RMS gate at 0.00391612. No fit
candidate or native movement was made by the failed preflight.

The fresh native BEFORE image was opened and inspected before the translation:
correct soldier/weapon, readable index/trigger, intact arms and original material
identities. Source right-index local rotation errors are all 0deg. Both approved
Allied adapters and the approved first-person actor were initialized unchanged.

## Actual single movement

- Native world delta: (+2.680083, -0.062444, +6.135888)cm; length 6.695959cm.
  This raises the trigger toward the fixed index and moves the gun rearward in
  this character's frame. It is NOT a camera-independent instruction for other
  characters. The small fresh-idle global difference is handled through the
  measured original hand frame.
- Gun rotation and scale are exactly unchanged. Every character bone's world
  translation/rotation/scale is exactly unchanged before/after and during all
  captures; no hand, arm, digit, model, weight, action or material edit.
- Selected trigger-surface point residual is 0cm; capture drift is 0cm. This is
  a correspondence measurement, NOT a skin-clearance/intersection test.
- The marked image supplies only camera-plane coordinates. Unseen depth was
  retained from the old trigger point, not inferred as a true index-pad contact.
  The chosen actual blade surface is about 10 native pixels from the arrow tip.

## Viewed evidence and remaining limitations

Private evidence: `Evidence/GermanNPCGripV1/native_views_v1/` in the existing
`Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1` workspace. Seven
original 1600x1000 native images and three labeled sheets were opened/inspected:
BEFORE right; AFTER right/front/top/reverse/full-arm-context/trigger closeup.
`presentation.json` records their hashes; the sheets resize/place original
pixels without retouching. Original material paths remain exact; visible detail
variation versus the old baseline is not a diagnosed texture change.

The index is now visibly inside the trigger-guard region rather than along the
stock. It remains straight; the closeup/reverse view do not establish a curled
firing grip or absence of blade/guard penetration. The unmoved left hand no
longer fully seats around the translated fore-end; that expected limitation is
shown, not compensated. The firing palm and remaining fingers are also not
accepted as a complete grip. Arms/cuffs appear continuous in static context;
cropped/occluded shoulder or weapon regions are not hidden-contact proof.

No additional translation, rotation, finger reuse, support-arm IK, action test,
aiming/muzzle change, formal binding or asset publication was attempted. Stop
here for the user's next marking; do not automatically repair another contact.

## Closure and protection

Owned hidden editor PID3848 / identity `native_views_v1` closed normally with
OS exit0. The 240-second stopping limit was not reached; result errors are empty.
All 618 current approved guards are exact before/after, including the authorized
Allied map/Catalog epoch, FP and B assets. No Unreal/Blender process remained at
closure; Lane A is RELEASED. Old map/Catalog hashes remain historical.

Staging was unsaved memory only. No map/package save, formal German selection,
source/dependency deletion, immutable SFTP release, AI/B edit, Git commit or push.
Evidence stays in the one existing private SFTP workspace; no extra model copy.
Motion/contact/reload/recoil/near-wall/FPS/package/second-machine gates remain
unrun. Retain the original source and registration failure evidence.
