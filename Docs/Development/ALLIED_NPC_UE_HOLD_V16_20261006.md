# Allied accepted holding layer V16 — revised native mechanism

6 October 2026. Continuation of authorized UE-asset integration, NOT a new fit.
Read V15 plan and actual native_ready_v2 result, failure index/FP001/AN001–007,
V14 source/result, weapon-hand guide and character execution/form-review rules.

## Stopped V15 and measured cause

V15 graph/link/native source identity/protected locals and actual gun binding
worked. Owned PID22360 normal exit0,611 protected rows exact; original map not
saved. Source ABP_PC_Allied_Stride_v1 remains the original driver. Native
postprocess evaluates9 times, gun relative residual1.75e-13cm/0deg, protection
error3.42e-6deg. Actual Ready target residual reaches hand_r10.069deg,
upperarm_r5.993deg, hand_l4.110deg: planned3deg gate FAILS, before screenshots,
movement or selection. Retain V15 asset/source/build and both entry failures.

Comparing the actual source Ready frame with V14 reference shows source arm
locals vary by several degrees (right upperarm7.38/wrist7.27deg in the earlier
frame). A constant delta applied to an evolving existing input does not pin the
accepted holding posture. This is NOT a missing graph link, finger/weight
failure or reason to compensate new gun offsets. Do not rerun fixed-delta V15.

## Different bounded mechanism

New V16 private postprocess AnimBP, same proven input/output/actual source
component path. At Ready, reproduce accepted V14 LOCAL rotations for exactly
the same11 approved arm/wrist/twist/index03 bones. Lower body, torso, clavicles,
other fingers and every input translation/scale remain original. It is a static
accepted pose overlay atop mature motions, not a new animation clip or new fit.

During Reloading/Dead, release this overlay to the SAME original evaluated
input pose. Native local-space quaternion interpolation over0.15s (before tests)
at both state boundaries; no body-to-camera/reference frame switch, extra
translation, slower blend tuning or copied FP holding mechanism. Gun retains
the already-proved constant actual component-to-hand attachment throughout,
not the legacy Ready/Reload orientation switch. Different common-pose space and
actual weapon ownership address AN004/007; they do NOT establish transition
acceptance without full observation. If continuity fails, stop V16, no tuning.

Native proxy samples action state on the game thread; animation evaluation
consumes proxy values only. No worker UObject access, per-frame Python pose
or newly authored source motions. Record source overlay behavior: Ready upper
arm swing is intentionally replaced; leg locomotion/root motion remain original.
Existing reload quality and index-blade10 limitation remain open.

## Early gate / stop / completion

Ready accepted11 local rotations <0.01deg and existing gun relative
<0.01cm/0.01deg; every unlisted input rotation and ALL translations/scales
unchanged<0.0001. Inspect actual original mesh side/front/top/reverse/context.
Then short existing walk/fire/reload/Ready return; unchanged ammo conservation,
same pose/weapon component and continuous sleeves/grips. Low-overhead native
ring-buffer bone/gun observations, report only after timed motion. Continuous
return measured across full release/return; no partial endpoint pass. Declare
>3cm adjacent gun/wrist step on frames<=100ms a stopping discontinuity; longer
frames are recorded as confounded/unpassed, not excluded to claim continuity.

Obvious detached grip/new major cloth sheet, native input/reference/source
mutation, ammo error, near-wall/muzzle error or return discontinuity stops this
candidate before formal adoption. No second angle/finger/skin/camera/source
action correction. V15 stopped graph is retained immutable. No German/FP/B
changes, deletion, catalog publication or Git commit/push. Formal persistence
still conditional on actual native/visual gates and fresh reopening, with a
separate exact map ledger before its authorized selection.

## First motion fixture correction

`native_hold_v16_motion`, PID36752 normal exit0, stopped in fixture setup before
PIE: CollisionResponse.BLOCK is not the installed UE enum. No samples/motion,
all611 guards exact. Existing project fixture uses CollisionResponseType.ECR_BLOCK;
use this verified API and MOVABLE blocker in a new identity. Same V16 algorithm,
graph/config unchanged, no retry of failed transition or visual motion gate.
Early native Ready already has11 rotation errors0, actual gun2.03e-13cm/0deg,
all five original views inspected/no new obvious sleeve tear. Top muzzle/context
boots crop and existing contact limits remain. Early PID39132 normal exit0.

## Audit-only correction after real motion stop

`native_hold_v16_motion_b`, PID39324 normal exit0, stops at original SingleNode
reload after Ready/walk/one shot request. Gun remains attached; original source
mode actually switches to AnimSingleNodeInstance. Protection audit reports
0.151291deg on an unlisted quaternion. Retain failure; no full return/near-wall/
lifecycle/adoption claimed. First request consumes one round but reports Barrel
blocked: unobstructed fire NOT demonstrated.

Installed Quat.h confirms AngularDistance assumes unit input (acos(2*dot^2-1));
identical unnormalized input can report nonzero angle. Unlisted entries are
copied verbatim and not written by this adapter. Correct ONLY audit arithmetic:
compare normalized TEMPORARY copies for physical angle; also report raw
component delta, source norm deviation and old unnormalized angle. Do not
normalize actual pose, relax0.0001 tolerance or change11 rotations, blend,
weapon fit/actions/camera/weights. Retain old source/binaries in vacant build/
recovery identities. A NEW bounded entry must prove raw component difference0
during source reload before calling the old angle a false alarm. Actual mutation
still stops. V16b failure is not erased/completed. Hidden editor/background or
long-frame confounds do not establish full return/FPS. No automatic blend tuning
or retry if the actual transition then fails.

Audit17's new Ready observer stops before motion because UHT exports only the
first variable in a comma-separated UPROPERTY declaration. Correct the three
diagnostic property declarations individually (and the gun-angle diagnostic),
without altering pose/audit math. PID35780 normal exit0;611 guards exact and
V16 graph/config exact. Not evidence for/against reload; use a distinct entry.

## Native draft persistence (separate from selection)

After owned test closure, save a NEW `DA_PC_AlliedGripV16` referencing the exact
proven-Ready V16 AnimBP and unchanged accepted config, then fresh-read it in a
new empty-editor entry. This persists the user's requested UE asset format even
if dynamic selection remains stopped. It is an unselected draft, NOT a formal
map change, immutable release, native motion proof rerun or teammate sync.
Do not overwrite the graph/config/source or existing assets; check all611 rows
and exact graph/config hashes at save and fresh-read. Fail persistence on any
field/dependency/hash discrepancy. Retain native data bytes privately/ignored.
