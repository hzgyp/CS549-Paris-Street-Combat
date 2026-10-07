# V18 first-person acceptance and conditional adoption

5 October 2026. The user accepts the current hand appearance and requests an
overall first-person check, formal adoption if it passes, and removal of
superseded problematic copies only after that adoption.

## Scope and reviewed cases

Read HANDOFF, current Git state, Failures/README, AN003, AN004, AN005, FP001,
the V18 result and the Blender character workflow / execution / form-review
instructions. V18's accepted appearance is not reopened because of historical
contact counters. Preserve its exact hand, gun fit, source rig, weights and
textures. No individual-finger solver, sleeve-weight experiment, framing-offset
scan, new motion, stopped owner author/test or old launcher is resumed.

The preceding inspection blend is a static pose adaptation, not an imported
native animation system. Closeup diagnostic hand objects are not production
first-person meshes. Formal selection and cleanup therefore require evidence
from the complete arms and the protected first-person view, then real actions.

## Different mechanism / early check

First perform a read-only offline projection audit using the immutable camera
and display transforms actually recorded by the native sleeve comparison at
phase 0. Camera remains (25,0,60)cm, horizontal FOV90, aspect16:9. Use the
complete V18 arms, not the existing closeup partial objects. Reconstruct the
old source pose and gun in that same recorded frame as a calibration control;
require its calculated gun transform to match the recorded native gun within
0.01cm/0.001degree before interpreting the candidate rendering. Convert the
native left-handed basis explicitly, including winding/UV corner parity.

This is a projection of the proposed assembly in the recorded ordinary-holding
frame, not a new native/gameplay acceptance test. It changes no assembly pose,
camera, geometry, skin, materials, source actions or native package. Rendering
is diagnostic only; do not infer the full native PBR shader from portable nodes.

Early acceptance: complete-arm ordinary holding must retain a readable rifle
and natural arm silhouette without major sleeve/self obstruction of the center
view or visible detached/cut arm boundaries. Stop on a clear failure; preserve
the accepted grip and report the unpassed overall criterion, rather than
changing the hand or adopting partial meshes to hide it.

## Conditional later gates

Only after that early gate passes, document the exact source-to-native adapter
and reserve a serialized Unreal slot before import. Fresh runtime validation
must cover idle/walk/run, reload and its return, firing/recoil, prone carrying
and fire prohibition, interruptions/death/reset and near-wall weapon blocking.
Old version test results do not establish these gates for V18. The existing
AN004/AN005 failures remain open unless a different mechanism actually passes.

If the complete result passes, select and publish one verified shared asset
with hashes/dependencies and update binding/restore metadata. Audit references
before deleting only superseded disposable candidates; do not remove vendor
originals, selected-baseline dependencies or unique failure evidence. If any
gate fails or is unrun, do not promote, modify Catalog/formal map or delete.

Evidence: ignored single shared workspace
`paris-gameplay-v1/Evidence/FirstPersonV18Acceptance/projection_v1`.
No commit/push is requested.

## Projection viewer correction (not an asset repair)

projection_v1 reconstructs the recorded gun to0.00008742cm/0degrees, but its
portable two-sided Blender material shows a large shoulder backface which is
absent in the recorded native control. Preserve v1; do not judge adoption from
that discrepancy. One new `projection_v2` viewer explicitly enables backface
culling in disposable material copies and repeats the two unchanged projections.
Compare the old control silhouette with the immutable native screenshot before
interpreting the proposed pose. This is a renderer parity check, not permission
to hide faces, cut meshes or modify the actual asset/native material.

The one-sided v2 control exposes inside-out shading and cannot pass the control
comparison. Its reflection remained on a negative-determinant object transform
while polygon winding was also reversed. New `projection_v3` materializes that
coordinate reflection in disposable vertex coordinates with identity object
transforms, retaining the matched UV corners and correct reversed winding.
This removes renderer-dependent mirrored-object face handling, not any source
faces. Stop this viewer if the control still fails; no further corrections.

## Result — hand accepted, overall acceptance not established

At09:40EDT, all three diagnostic runs exit0/errors[];528 current recovery
size/SHA guards remain exact, including the known unselected V6 saved-rate
difference. Protected original V18 blend and all source inputs remain exact.
No Unreal slot or process, native package authoring, formal-map/Catalog change,
release, commit/push or file deletion occurred.

The user explicitly accepts V18's hand appearance. This is the current visual
hand baseline; do not restart finger/contact solvers because historical contact
face counters were not zero. Conditional formal adoption is a separate gate.

Six rendered projections were opened and inspected against the original native
phase0 screenshot. The gun transform control matches0.00008742cm/0degrees and
its projected silhouette aligns, but the shoulder display does **not** match:
the offline full-arm control shows a broad left shoulder surface where the
native reference has a different spiked sleeve silhouette. v2's one-sided
negative-transform view additionally has inside-out surfaces; v3's explicit
coordinate conversion fixes that latter appearance but not the shoulder
discrepancy. Cause of the remaining discrepancy is unproved; do not call it a
new V18 native failure or claim shader masking/weights as a diagnosed cause.
The offline viewer stops here, without further material/pose/camera tuning.

A fresh read of the accepted blend confirms72 source rig bones, original
armature modifier on the hidden complete source arms, pinky02 approximately
0.90scale, and **zero Actions / no active Action**. Its visible hand inspection
objects and complete frozen-arm object have no armature modifiers. It is an
editable static adaptation with the source rig retained, not a replacement
runtime animation asset. Do not set a visible frozen/partial object as the
game's character or assume motion has been exported.

Consequently, overall first-person acceptance is **not established**, not
passed and not a proven candidate-runtime rejection. Native movement/reload/
firing/interruption/near-wall tests were not run for V18. Prior AN004 return
discontinuity and AN005 sleeve obstruction records remain unresolved; neither
their old failed tests nor this static grip review tests a new V18 runtime.

Keep the accepted grip unchanged. Before conditional adoption, the next work
package must identify and validate a native existing-motion adapter for this
exact source rig/gun fit, with separate proof of complete-arm/source-material
parity in the real protected camera and existing reload return behavior.
That is implementation work, not another finger refinement or a reuse of
stopped owners/weight experiments. Coordinate one Unreal writer, new namespace,
guard audit and an early real-view gate. Cleanup remains conditional; no old
working restoration dependency or unique failure evidence has been removed.

### Evidence

- Immutable native control: `Evidence/ReloadRepairV5/sleeve_native_views_v2/phase_0.0_before.png`.
- Final disposable offline viewer: `Evidence/FirstPersonV18Acceptance/projection_v3/CompleteArmsProjectionOnly.blend`.
- Candidate projection: same directory `accepted_V18_first_person.png`.
- Accepted hand source stays `Evidence/WeaponPinkyLengthV18/distal_v1/RightPinkyDistalShorter.blend`, SHA256 `7a1d0520b11e7d9c8d29377c46909cfa2b65fea39254789e28eff083de404219`.

All paths above are within the ignored single `paris-gameplay-v1` SFTP workspace.
The diagnostic projection blend is not a publication, restoration or selection
authority. Preserve v1/v2 viewer differences as test evidence.
