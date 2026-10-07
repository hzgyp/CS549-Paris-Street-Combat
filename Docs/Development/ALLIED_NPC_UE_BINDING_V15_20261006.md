# Allied NPC UE-native grip asset V15

6 October 2026. User accepts V14 appearance and authorizes UE-asset integration.
This is NOT a new German or first-person fitting task. Implementation starts only
after this plan. Existing dirty changes belong to their owners.

## Evidence and failure cases read

Read HANDOFF, current Git/611-row guard epoch, failure index and FP001,
AN001–AN007, V14 plan/result, the English weapon-hand guide and team asset-sync
workflow. Character-workflow, execution and form-review skill instructions read.
Installed UE5.8 source confirms per-component post-process AnimBP support and
linked-input evaluation. A native UAnimInstance alone cannot install the private
default linked-input pointer: use an actual NEW AnimBlueprint graph instead.

FP001: actual rifle transforms affect muzzle/collision even without transaction
edits. AN001/AN002: no stale external pose driver or live skin-weight query.
AN003: no stopped reload-owner author or unavailable reflected AnimGraph API.
AN004/AN005/AN007: no frozen endpoint or ammunition result masquerading as full
transition acceptance; no stopped FP proof, slower blend or camera/skin repair.
AN006: actual source/evaluated component and action identity must be measured.
V14 retains numerical index/blade crossings (10) and hidden-side limitations;
human posture approval does not erase them.

## Changed mechanism and asset scope

Create a separate generic `ParisNPCGripV15` runtime/editor plugin. Its editor
factory authors a NEW private UE AnimBlueprint: Linked Input Pose -> native
local-rotation adapter -> Output Pose. Original skeletal mesh, skeleton, UVs,
weights, vendor clips, animation blueprint and NPC driver remain unchanged.

The adapter applies ONLY the accepted V14 versus actual original V14 local
rotation differences on bilateral arm/wrist/twist bones plus the already
approved index_03_r. It does not author a new animation, translate/scale bones,
change other digits or freeze the whole body. Existing input actions continue
through the graph; this first candidate is state-independent (no Ready/reload
switch or newly invented blending curve). Large motion incompatibility stops
the candidate rather than prompting new pose/finger adjustments.

A new native wrapper targets named Allied NPCs only (never player/German).
It installs that post-process asset on the ORIGINAL visible skeletal component.
The EXISTING actual rifle follows its hand_r socket at the accepted measured
component-to-hand transform. Disable only that bound rifle's old competing
per-frame positioning tick; do not rewrite its Blueprint or combat transactions.
Preserve component-relative transforms when deriving the actor attachment.
Original gun remains `WeaponAppearance` and `GripMesh` remains the original mesh.
Record this gameplay-relevant attachment change and verify muzzle/near-wall.

## Ownership and protection

One physical asset workspace remains the existing private gameplay workspace.
New asset/config/evidence use unique V15 names; no source-model copies or asset
deletion. Generic source in Git, commercial pose data and native assets ignored.
No first-person plugin edits, B base/AI/BT/BB/German changes or commit/push.

Before writing, record all611 current rows and the descriptor's original bytes.
Only the `.uproject` plugin-enable field is an initial guard exception, recorded
with exact before/after SHA and semantically checked JSON diff. All other rows
must remain exact. No map write until actual motion/visual gates pass. Later
formal map/manifest selection needs a separate exact authorized ledger/rebase,
never a blanket guard ignore. Claim serialized A native slot only after engine
and current guard checks; release after owned normal closure and fresh checks.

## Early acceptance and stopping condition

1. Offline derive rotations from ACTUAL `fp_wrist_native_v14` before/after,
   reconstruct source-length local transforms and accepted gun-to-hand transform.
   Protected skeleton locals are not accidentally copied from different idle
   phases. Rotation adapter math must reproduce configured joints within0.01deg;
   fitted gun-to-hand residual <0.01cm/0.01deg.
2. Compile new plugin and graph through installed native UE editor APIs. Start
   one unsaved actual NPC comparison. Native graph must consume incoming pose,
   preserve every input local translation/scale and every unlisted rotation,
   and show the accepted static hand/gun/arm relationship without a new obvious
   tear. Runtime adapter audit <0.01deg; rifle relative <0.01cm/0.01deg. Other
   source bones are not a frozen world-coordinate gate during a live idle clip.
3. If graph capability/link/source/pose identity, guard or visual parity fails,
   stop before motion or formal adoption. Preserve exact failure and no retries
   of stopped authoring mechanisms; a compiler-only repair is not a new fit.

## Dynamic gate, then persistence

Use existing native movement and authoritative request functions. Inspect Ready,
walk, fire/recoil, reload middle/return, lifecycle and nearby obstruction.
Record action identity, velocity, shot/ammo outcomes, same evaluated hand and
gun relation, source-length preservation and native transition observations.
Sample low overhead in memory; write results outside the timed transition.
No per-frame Python pose or production driver. Do not change ammo to manufacture
a reload. Rifle transform must remain hand-relative through all actions.

Obvious detached grip, new major sleeve sheet, incorrect muzzle/obstruction,
ammo nonconservation, lost driver, source action failure or protected mutation
stops selection. Measure full-return events separately; frame time confounds
must be reported, not relabeled pass. Existing V14 residual contact and source
reload quality remain known limitations, not new refinement targets.

Only after actual native and visual checks may the new wrapper/config be saved
as the formal Allied selection; verify fresh reopening/native -game entry and
dependency closure. Asset release requires normal pinned SFTP byte/readback
workflow and matching metadata, not merely files in a mutable workspace. No
teammate test, FPS/Shipping or complete course completion claimed without tests.

## Early harness API correction (before any native fit)

`native_ready_v1`, PID52384, created/compiled the new AnimBP but stopped before
binding: Python World has no spawn_actor method. Owned normal exit0, no pose
samples or motion, all protected rows exact except the separately authorized
descriptor field. Do not relabel this as runtime success. The graph is retained
at SHA870b9440e95a6ffae006a78cbba23dd2954816cc77b105f0e9327d1a146125c2.
Use the already demonstrated editor actor fixture API for a NEW early entry:
pre-place the native wrapper with Target unset, then set its actual PIE Allied
target once. Reuse the exact saved graph, no factory rerun/asset rewrite, pose
algorithm, fitting, finger or source-motion change. This is a capability-only
harness correction, not permission to proceed past a failed native visual gate.
