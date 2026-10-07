# Allied NPC — fixed marked grip / raised rifle and following support V7

5 October 2026. User confirms the marked interpretation and authorizes execution:
fixed right hand/grip point, raise the rifle muzzle, move the left support with
the gun through the whole arm, stop at actual index/trigger alignment. This
supersedes V6's no-extra-candidate/no-left-arm stop only within this new trial.

## Contract and preserved inputs

Actual Allied US paratrooper / original M1 / V3 attachment / original Allied
Stride Ready pose, native UE5.8 centimetres. No changed gun scale or source
model, topology, rig/rest lengths, weights, UV/materials, source motions,
right arm/hand/digit locals, left digit locals, camera, ammo/damage transactions.
Left shoulder/clavicle stays fixed; only source-length upper-arm/forearm/wrist
and their rigidly-following descendants may adjust in the new diagnostic pose.
Keep approved FP, German, B AI, formal map and Catalog exact (current611 guards).

Static comparison only, not new animation production or motion/playable-rig
acceptance. No native asset/map save, adoption, deletion, release, commit/push.
Tools/docs in Git; data/geometry/images in the existing ignored SFTP Evidence.
Old failures and all candidate identities remain intact.

## Read cases and different mechanism

Read Failures/README, AN002 and FP001 full analyses, character skill/shared
execution/form-fit reference, full weapon-hand guide, V6 plan/result, and the
reviewed stock-pivot/source-length left-chain math. Do not execute old stopped
owners, live skin reads, digit solvers, weight changes or player author scripts.

Unlike V6's fixed-left-hand gun lowering, this uses the NEW user-marked fixed
right stock/grip point and rotates toward the actual fixed index pad/trigger.
Preserve the source mature grasp, then follow the fitted weapon with the full
left arm. Use original-length two-link math, not detached hand translation.
No copied player pivot/offset/quaternions or angle scans.

## One candidate and early falsifiable gate

Reconstruct the current V6 recorded source skin offline from the full US FBX,
reference audit and native bone transforms; rest alignment <0.01cm and explicit
reflection parity. Identify an actual stock surface at the user's small box
near native pixel(726,456); the mark indicates a region, not calibrated depth.
If occluded/off silhouette, use nearest actual stock to that marked hand surface
once and verify the projected point remains in the marked region. Record this
assumption and actual coordinates. Stop on missing/mismatched surface/source.

ONE minimal3D fixed-pivot rotation from actual blade landmark to unchanged index
pad; cap30degrees, muzzle height must increase. No extra seating translation.
Record radius mismatch and nearest actual blade/stock/guard relationships.
Trigger nearest-distance screen <=0.3cm, pivot error <0.001cm, unchanged right
skin <0.001cm, digit local matrices <1e-8. A point match alone is not clearance.
Preserve right-stock/guard contact by inspecting real mesh; if regressed, retain
the explicit comparison unselected and stop without compensation.

Left wrist/orientation follows the same rigid gun change; shoulder fixed,
old elbow bend plane retained. Segment lengths within0.01cm, wrist target within
0.01cm, rigid palm tracking <0.05cm, no newly severe skin edges (>3x and >2cm
extra). Recheck elbow/cuff/shoulder and actual palm/grip, not bone endpoints only.
Stop if unreachable, broken cuff or required protected-input exception.

## Native presentation gate

If offline preservation/reach checks permit viewing, claim one native
slot after process/611 guard check. For this FROZEN comparison only, reuse an
uninitialized existing native actor's full PoseableMesh component as a container;
do NOT call its first-person binding, config, hand overrides, camera framing,
tick or production action algorithms. Copy the exact whole Allied source mesh,
materials and the exact RECORDED V6 whole-world pose; no mask/cut or model
replacement. Replaying this frozen pose avoids changing idle phase between
before/after. Original NPC animation driver is preserved, not overridden.
Validate baseline pose
parity before applying the new full-pose transforms. This container is not an
NPC runtime integration or source action replacement.

Capture matched V6 and candidate native front/right/top, trigger detail, left
support, reverse and full-arm context; verify all protected bones and rigid
gun/pivot/left-chain transforms. Open actual images and record texture-streaming
detail variation without retouch. Close only owned hidden editor normally,
fresh-check611 hashes, release slot and await human review. German remains next,
after Allied acceptance; no automatic formal selection or motion acceptance.

Contact-screen failure stops fitting/adoption, not a faithful static viewer of
this one explicit user-requested comparison. A candidate may be shown with that
failure clearly labeled; no new fitting parameters or second candidate follow.

## Display-only correction after first native preflight

The first viewer's public73-bone local-derived reads matched V6, but the actual
two baseline screenshots showed a reference-pose body/hands lowered. That is an
observed render-parity failure, not evidence that the candidate IK failed. Its
early gate stays closed; let its owned deadline close it normally. Preserve the
original entry, identity, images and hashes. No candidate was applied there.

Installed engine sources establish that SetBoneTransform marks refresh dirty,
whereas the renderer receives transforms through RefreshBoneTransforms in the
component tick. A paused world did not refresh this new container. A NEW V7b
viewing entry may enable ONLY the diagnostic Poseable component's native tick
while paused and AlwaysTickPoseAndRefreshBones, using the verified public
SetTickableWhenPaused/SetComponentTickEnabled methods. Actor/production ticks
remain off, no BindExistingPose, no original NPC animation/weight/action edit,
no recalculation of fitting. Exact same cached V6/V7 transforms and textures.
Wait at least one second/native refresh opportunity AFTER each pose application
and BEFORE the one-shot capture; exporting later cannot repair an already
captured stale pose. Actor/animation clocks remain paused throughout.

Require actual baseline images to show the recorded raised arms and parity with
V6 before the candidate. Add a readable reject/abort early gate. Stop on another
render mismatch without a third viewer. Resume only after first owned editor
normal closure,611 guards and slot recheck. This repairs presentation only, not
contact acceptance or motion integration.
