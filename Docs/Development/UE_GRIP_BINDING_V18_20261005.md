# V18 UE grip binding — bounded implementation

5 October 2026. User explicitly resumes UE binding of the visually accepted
V18 hand. This supersedes the previous offline-only checkpoint for this new
binding work, not any stopped solver, old owner or formal adoption gate.

## Read / preserve

Read HANDOFF/Git, Failures/README, AN001/002/003/004/005, FP001, V18 proportion
result, first-person acceptance record, the fitting guide, and Blender character
workflow/execution/form-review instructions. The accepted hand is fixed; source
mesh, rest skeleton, weights, textures, original action bytes, camera25/0/60/FOV90,
transactions, NPC work and all528 current recovery guards remain protected.

No detailed character creation, retarget rerun, live native skin extraction,
sleeve-weight/mask/cut experiment, offset scan, per-finger solver or new motion.
Reproduce the approved local grip rotations and pinky02 scale, without changing
their values; these are pose-binding data, not permission to refine the hand.

## Different native mechanism

Use a new ordinary AnimBP with engine CopyPoseFromMesh from the player's existing
native body animation. In the display layer, reuse the exact accepted existing
D059 local finger rotations and distal pinky scale; source mesh/rig/animations
need not be re-exported because they did not change. Engine TwoBoneIK follows
the accepted support-hand target relative to hand_r without stretching; the
support orientation is the accepted existing relative rotation. This is a
binding of an existing pose, not animation synthesis. Grip overrides/support
IK are active only during ordinary holding; reload reuses original native motion
without frozen gripping fingers. Distal scale remains a constant display adapter.

Unlike AN003, the new pose source is the existing body animation, not another
independent failed D059 derivative owner. Unlike AN004, the proposed new owner
caches ONE camera-local assembly frame at initial Ready calibration and attaches
to the unchanged camera; no Ready-time target/refit switch exists. The native
old gun view provides the initial presentation frame. The new visible M1 is
attached to the adapted display hand_r with the accepted V16 transform, so it
and the hand move together. Do not reassign WeaponAppearance: all authoritative
gun/near-wall/ammo transactions still use the original existing implementation.
Visual/native gameplay equivalence remains a separate acceptance question.

Generated commercial pose configuration and native packages stay in the single
ignored SFTP workspace. Public source contains generic binding code only.
New namespaces: Animation/GripBindingV18 and Blueprints/GripBindingV18.

## Steps / early checks / stopping conditions

1. Verify immutable inputs/528 guards; extract accepted local rotations and
   gun/support transforms into private configuration. Assert hierarchy, proper
   normalized rotations and0.90 distal scale; do not change source blend.
2. Serialized native slot: new-only minimal graph capability/compile, then fresh
   binding proof. Do not retain editor pin handles across compilation. No old
   AN launcher/author is called. Save only named new assets, never Save All/map.
3. Require actual local rotations/scale and hand-relative gun transform to match
   the accepted data (0.01cm/0.01degree), support target within0.2cm and no stretched
   arm. Check full original native materials, complete arms, LOD/binding and the
   protected camera in actual city views. Static hand approval is not a new
   mathematical clearance gate or a complete native visual pass.
4. Only after the early view passes, test existing movement and reload/fire,
   transition, lifecycle and near-wall behavior. No Python per-frame pose/weapon/
   framing updates; preparation and read-only observation are allowed. Native
   runtime control must be visible in saved graph inspection.

Stop if capability/compile fails after one source-supported technical correction,
or actual fitting/view/deformation fails. Preserve unique outputs; do not widen
finger/skin/camera scope or import frozen partial diagnostic meshes. Record any
unrun action tests. Conditional adoption/deletion follows complete actual
acceptance and dependency audit; no Catalog/release/commit/push is requested.

## Slot

Only current root thread active for this project; NPC thread is not loaded.
Actual engine process check is empty. Lane A claims the new binding slot before
launch and releases it after process and current guards checks. No other task
is created or dispatched. Do not close another user's editor.

## Retained technical author failure

anim_author_v1 exit0, no saved package: the naive menu search for `modifybone`
matched three Control Rig struct utilities rather than the engine controller;
the actual display label contains punctuation (`Transform (Modify) Bone`).
CopyPose and space conversion creation already passed. Preserve v1 and apply
ONE source-supported selector correction: normalize menu punctuation and restrict
ModifyBone/TwoBoneIK to Animation|SkeletalControls. No pose/angle/data change,
no native crash,528 guards exact. A second semantic/capability failure stops
authoring under this bounded plan.

## Second capability failure / different C++ binding (5 October)

anim_author_v2 cannot connect the ModifyBone output under the presumed
ComponentPose name. Exit0, zero packages,528 current guards exact. The ordinary
graph author route is stopped, including ue_anim.py/ue_owner.py; do not retry
pin probing or weaken this stopping condition.

The user request to continue UE binding is implemented instead by a new,
disabled-by-default runtime plugin, ParisGripBindingV18. Its native actor copies
the existing source component's bone transforms into an exact-mesh PoseableMesh
after the source tick. It applies the accepted constant local holding rotations,
the accepted distal proportion, and engine AnimationCore TwoBoneIK for the left
support chain without stretching. No native vertex/skin extraction, new action,
mesh/rest/weight change, or old graph owner occurs. Existing motion evaluation
remains UE-controlled; C++ handles only display binding/adaptation. On reload,
holding rotation/IK overrides are disabled; the unchanged native source action
plays. This is not approval of that action's final appearance.

The visible gun attaches to hand_r. The assembly frame is cached once from the
old visible gun/camera during initial Ready, never reset at action completion.
Original WeaponAppearance and transactions are not reassigned. Config is a
private JSON-backed data asset (commercial pose data outside Git); public code
is generic. First a host-editor BuildPlugin compile, then an unsaved city idle
proof with local-pose, socket, support/limb/camera/material checks. One technical
compile correction maximum. Stop at any second compile/capability failure or
failed actual idle fitting/view; retain unique evidence, no formal adoption or
old-copy deletion. Only after this early gate passes run movement/action tests.

Native cpp_idle_v1 binds successfully (true/empty BindingError), but its observer
fails at Unreal.Transform's unsupported translation constructor keyword before
capturing a sample. Engine shutdown is normal;528 guards exact. This is a
test-harness error, not an actual fitting failure. One verified harness-only
correction assigns the existing Transform fields instead (as in existing native
observers). C++ DLL/config/pose/frame/source remain unchanged; new cpp_idle_v2
identity retains v1. No second observer correction under this early proof.

### Read-only mathematical check revision, before any further launch

cpp_idle_v2 successfully binds; three native updates, gun relation3.36e-13cm,
support3.64e-13cm, original limb lengths2.95e-13cm, native finger rotation
2.96e-6degrees, original camera/materials/weapon/ammo intact. Observer stops
before screenshots because it passes non-unit imported quaternion values to
AngularDistance. UE5.8 Quat.h:1228 implements acos(2*dot*dot-1) without unit
normalization. `unit_bias_v1` independently predicts all30 reported differences
from the JSON quaternion norms; verify residual<1e-5degrees before launch.

The prior observer-only stop budget is explicitly amended for this proved
mathematical error, not a native capability/contact failure or an unproven
physical cause. Normalize TEMPORARY comparison operands only, preserve .01degree
gate/config/DLL/pose/frame/source exactly, and retain v2. A fresh cpp_idle_v3 is
limited to the same three real native views. No further observer revision if
this normalized verification fails, no physical fitting or old graph rerun.

cpp_idle_v3 passes actual idle (59native updates; gun2.33e-13cm, support
6.71e-13cm,30finger locals max2.42e-6degrees) and records idle.png. Inspected
actual city image: ordinary grip, full native materials and arms are reviewable,
no large sleeve fragment across center. Look-up also passes pose/socket checks
but observer's exact camera equality rejects59.99999999999997cm. This is not a
camera edit; all528 guards still match. Do not call this a complete three-view
or gameplay pass. Replace accidental exact equality with the project's existing
native observer tolerance1e-6cm (ue_continuous_arms_native_probe.py), not a relaxed
physical gate. DLL/config/pose/camera/source unchanged. This read-only numerical
correction is declared before a fresh test; stop actual physical/visual failures.

Early idle visual gate permits cpp_motion_v1: same three view angles, existing
forward/left walk/stop and existing native PC_RequestReload/natural return. Python
movement is test input only; all poses/attachments remain native. Read camera,
socket/support and native action/ammo samples; conserve total ammo with one
commit. Require natural Ready transition gun/wrist step<3cm under AN004's same
gate, no reframe/slowdown/extra blend if it fails. Record movement speed/captures;
shooting, sprint/prone/jump/death/reset/near-wall/FPS remain unrun. Not automatic
adoption even if numeric checks pass; inspect actual action images and human
comparison separately. No motion or source clip is replaced by this binding.
