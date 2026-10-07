# Existing reload and recoil animation implementation

4 October 2026. Owner yg745. [Chinese review](WEAPON_ANIMATION_REUSE_V1_ZH.md).
Status: implemented and stopped; reload visual failure and recoil authoring crashes,
unselected. See [result](WEAPON_ANIMATION_REUSE_RESULT_20261004.md). This package implements
the user's second work item, reload and recoil presentation, not the separate prone
back sling request. Existing purchased finished animations only; no new motion.

## Scope and removal

Mark the new RifleAnimsetPro receipt duplicate. Evaluate D059 Aim reload on the
actual Allied mesh, existing M1 and unchanged player camera. Replace the rejected
Rifle_Reload_2 binding in a separately named candidate. Reuse existing shoot motion
for visible hand and rifle recoil after a successful shot. Player is first; NPC
replacement requires the same compatibility and runtime checks on each team.

Remove the old reload from the candidate's executable binding, not from immutable
vendor baselines, published releases or shared parent Blueprints. Audit references
before any physical deletion. Shared originals and old saved checkpoints remain
rollback evidence. No source finger, rig, mesh, camera, weapon geometry, ammo or
damage rule modification. No keyframing or generated action, AI, muzzle VFX,
prone sling, trigger finger repair, map selection, Catalog change, release or Git
commit/push. Simplified generic reload is not a mechanical M1 en bloc simulation.

## Failure review and changed mechanism

Read Failures/README, FP001 analysis, GP010 analysis, RELOAD_COMPARISON_20261003_ZH,
PLAYER_ACTIONS_RESULT_20261003_ZH and the latest German rifle human review.
FP001 forbids hiding contact problems with masks or numerical convergence.
The earlier comparison used different characters and no rifle. This attempt uses
the same target, rifle and protected camera; inspect reference poses before
retargeting, never force a compatibility flag on the vendor skeleton. GP010
requires actual PIE instance collision checks, not only defaults. Prior phase
screenshots repeated despite different bone samples; freeze the evaluated pose
and verify actual viewport frames against the sampled joints, separately from
unfrozen functional tests. Native Blueprint owns all runtime animation and gun
updates; Python is authoring/testing only.

## Storage and sequence

1. Guard current accepted foundation, existing German trials and source motions;
   no concurrent editors. Snapshot exact file hashes before authoring.
2. Read-only native audit of D059 Aim reload and available shoot clips, hierarchy,
   reference pose, additive settings, existing graph bindings and references.
3. Early gate: target pose must actually deform and remain finite, with unchanged
   source bytes. Inspect full reload and recoil on the actual model with rifle.
   If incompatible, use bounded engine retarget into a new derivative identity;
   do not change vendor compatibility/reference pose or invent motion.
4. New private `/Game/ParisCombat/Blueprints/WeaponAnimationReuseV1/` candidate
   graphs and any required existing-motion derivatives use new names. Adapt
   bindings/attachment and event timing only. Keep old actor/map bytes untouched.
5. Reload transaction remains token/generation guarded. Determine its new safe
   commit point from inspected completion, not old 1.083 seconds or generic 50%.
   Use native animation position; timeout cancels and cannot create ammo. Recoil
   is triggered only after accepted fire, survives native update ordering and
   returns to holding; rejected shots and reload cannot produce recoil.
6. Fresh bridge-disabled actual-city tests: standing/walking reload, fire/recoil,
   repeated fire, interruptions, death/reset, stale/duplicate events, ammo
   conservation, near-wall blocking, collision and pose/camera/source protection.
7. Record exact candidate hashes and limitations. Human review decides the
   visible replacement before saved map/release selection. Keep raw failures.

Native drafts share the single ignored SFTP workspace Content, not a second
commercial asset copy. Evidence goes under that workspace's
`Evidence/WeaponAnimationReuseV1/`; Git contains tools/docs/hash metadata only.
New intake remains LocalWorking. Existing permissions/rights cover selected old
motion baselines; the new VFX receipt is not published in this package.

## Acceptance and stop

Functional checks cannot approve visual contact. Complete cycles must show changed
hand poses and coherent rifle motion, no large camera obstruction or detached
right grip; Ready/reload/fire transitions must be readable. Source model, finger
animation data and camera remain protected. Stop on incompatible pose, severe
clipping/obstruction or transaction regression. Permit one cause-supported
technical correction, retain failures, then report the concrete gap rather than
sweep offsets, generate animations or buy another generic pack. If the generic
motion improves presentation but not M1 mechanisms, state that distinction.

## Native audit and retarget checkpoint

Read-only audit found a shared live parent reference to Rifle_Reload_2; deleting
the vendor file would break it. The candidate overrides PC_RequestReload without
a parent call. D059 has up to49.85 degrees of upper-arm reference difference and
18.47 degrees at wrists on the actual soldier, so direct compatibility/rebinding
was rejected before playback. A single native FK/pelvis retarget uses explicit
spine/head/arm/leg chains and source/target preview meshes, auto-aligns the target
reference pose, disables IK solving and root-motion operations, and restores the
existing source finger-local tracks without pose edits. Its4.133333-second output
and30 finger tracks pass sampled delta2.07e-7; all507 guarded files unchanged.
The mounted `/Game/Rifle_01/` is a junction to the existing selected SFTP source
workspace, not a copied pack, and is never saved by these tools.

New player child binds only this derivative; inherited commit/cancel/poll/lifecycle
functions remain intact. Proposed commit3.95 seconds is conservative generic
completion, not M1 insertion; validate it in target views before selection.
ShootLoop_Additive actually reports AAT_NONE. Use the existing0.8-second
Rifle_ShootOnce on the independent owner pose driver, observed accepted ShotSequence,
and retain holding FramingT during that clip so ordinary aiming fitting does not
cancel the recoil. Camera is not shaken or moved. Reload and recoil target views
must precede selection; none of these authoring checks approves contact.

## Early visual gate rejection

reload_views_v1 failed after leader PauseAnims capture and produced an obstructed
holding image. reload_probe_v1 proves the override/defaults/request on a transient
instance, not a PIE pass. reload_views_v2 instead holds single-node playback rate
at zero while bone refresh continues;6 actual views and named native phases are
recorded. The true cause of all v1 differences is not fully isolated. Its raw
failure remains. V2 Ready is readable, but the new reload shows triangular sleeve
stretches and major self-obstruction at operating/complete phases. This is an
actual failed visual gate despite507 unchanged input files and late ammo transfer.
Do not select this D059 candidate, shift the camera, mask the sleeve or keep
retargeting/tuning it in this package. Exact deformation cause is not established.

The independent owned Rifle_ShootOnce recoil binding may still be authored and
tested on the original compatible holding pose. Any combined functional reload
test reports only transaction behavior on this unselected failed candidate,
never visible replacement approval. NPC replacements are deferred. A subsequent
reload implementation requires a different documented compatible existing-action
mechanism; no new animation or purchase is inferred.

## Independent recoil authoring correction boundary

author_owner_v1 exited 3 with a BlueprintEditorLibrary null-access crash, no
result and no native owner package on disk. Preserve its log, source and crash
context. Stale pin handles after an intermediate Blueprint compile are a
diagnosis hypothesis, not a confirmed engine root cause. One technical retry
uses new OwnerV2, complete helpers compiled in dependency order, and fresh graph
handles after compilation. Stop after another native crash; no engine patch or
bridge enablement. Avoid swallowing a reset-frame accepted shot while only
observing the original successful ShotSequence. Recoil views inspect original
compatible holding and Rifle_ShootOnce only; do not re-render/refine rejected
D059 reload.
