# V18 UE binding result

5 October 2026. User-authorized continuation; **working native binding proof,
not formal adoption**. See the implementation plan and AN006. The accepted V18
hand remains accepted; do not change its shape/finger parameters to repair a
whole-view action problem.

## Implemented and actually tested

The new disabled-by-default runtime plugin `ParisGripBindingV18` compiles on
UE5.8 Win64 editor Development (BuildPlugin exit0, no compile correction).
A native actor copies existing source bone poses into the original continuous
arms mesh, applies the exact accepted holding data/distal proportion and engine
original-length support IK. The M1 is an actual hand_r child. One initial
camera-local assembly frame stays constant; C++ controls all subsequent poses
and attachments. Python performs setup, read-only observation and movement/reload
test inputs, not frame-by-frame pose/gun control.

`Evidence/GripBindingV18/cpp_motion_v1` in the single private SFTP workspace
records969 observer samples/650 last native updates,8 rendered requests and
normal editor exit0. Tested idle,20degree look up/down, forward/left walk, stop,
one stationary existing-baseline reload and natural Ready return. Both walking
phases reach300cm/s. The four motion/transaction assertions pass:

- Accepted30 holding-local rotations externally reproduce within0.00000242degree;
  gun attachment/support and source limb lengths are within declared gates.
- Camera remains25/0/60cm/FOV90 within1e-6cm; native original materials intact.
- Ammo2/16→8/10, exactly one reload commit and total18 conserved.
- Natural Reloading→Ready gun0.108116cm/wrist0.118699cm step over60.6176ms,
  below the unchanged3cm AN004 gate. This is sampled continuity for this source,
  not proof that the approved D059 game integration or all RLD defects are fixed.

The formal baseline reload remains unchanged; this display binding does NOT
replace its Reload_2 source with the approved D059 source. No new motion,
retarget, finger solve, rig/rest/mesh/weights/texture/camera/ammo logic edit.
Original WeaponAppearance remains authoritative and hidden visually during this
unsaved proof; new visual/old-authoritative equivalence is not fully verified.

## Actual image review — overall gate fails

All8 motion-test images plus the earlier actual idle image inspected. Ordinary
holding is reviewable with fitted grip/native textures; no large sleeve fragment
across center in the inspected idle/look/forward/stop/return views. This is NOT
continuous reload sleeve/contact acceptance.

`walk_left.png` visibly places the weapon very low, with most arms/hands leaving
the viewport. Actual recorded left-walk camera-local gun Z spans-31.22 to-16.57cm;
at request-31.09cm vs the idle sampled range-19.93 to-14.79cm. Hand-relative gun
and holding locals still match. The binding is coherent but current direct
full-body source motion is not accepted as the desired first-person presentation.
Do not blame hand shape, assert a particular root/shoulder cause, change camera,
scan assembly offsets or select this candidate based on numerical checks alone.

Reload/return images were captured after completion. Mid-reload images were NOT
captured: an action-capture hook added after script startup was never executed
and has been withdrawn. Do not infer RLD-01/02 passes from these return images.
Shooting/recoil, sprint/prone/jump, moving reload, death/reset, interruption,
near-wall, FPS and packaged/teammate tests remain unrun.

## Retained test diagnostics

The ordinary AnimBP graph author stopped after menu and ModifyBone output-pin
capability failures; zero native packages. No retries of that route.
C++ idle v1 constructor-keyword harness error and v2 unnormalized quaternion
comparison are retained. Installed UE Quat.h and unit_bias_v1 explain all30 v2
differences to3.64e-8degree residual; temporary normalized operands fix the read
calculation, not config/pose. Idle v3 captures a passing idle, then exact-equality
camera assertion rejects a2.84e-14cm tail; the existing1e-6cm observer tolerance
allows the declared final motion test. No native model/pose/threshold sweep or
crash occurred. Preserve these errors rather than treating exit0 as acceptance.

## Closeout / next bounded work

All528 **current map_recovery** size/SHA guards exact, including the known retained
V6 saved-rate difference; source V18 blend/config unchanged. Formal map remains
SHA2791b4a7…ad68519. No task UE/Blender process remains; A releases native slot.
No new native package/map/selection/Catalog/release/commit/push/deletion. Public
code is generic; config/screenshots/binaries remain ignored, single-workspace
evidence. `cpp_evidence_v1` inventories are diagnostics, not restore authority.

Current full-body native proof launcher is stop-locked under AN006. Next needs a
different, documented existing-motion FP upper-body/source-space compatibility
mechanism with first cause evidence and an early lateral-view check. Search the
existing purchased native catalog first, reuse mature motion, preserve accepted
hand/gun data and all stopped-route protections. Independently inspect reload
mid-phase before adoption. Human viewing may use a separately authorized manual
entry, not a stopped repair/test rerun. Conditional old-copy cleanup is deferred
until formal adoption and dependency audit, not permission to delete vendor,
selected-baseline or unique failure/restore files.
