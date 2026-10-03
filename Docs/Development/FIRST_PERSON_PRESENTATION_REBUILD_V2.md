# First-person presentation rebuild V2 — implementation before authoring

Date: 3 October 2026. Owner: yg745. User authorized FP001 archival first, then restart on V3; COD WWII M1 Garand ordinary holding is the visual reference. Archive closeout is a prerequisite to executing this plan. Saved V3 is a functional starting point with known visual defects, not an accepted first-person solution.

## Required failure review

Read `Failures/README.md`, FP001 `FAILURE_ANALYSIS.md`, and the V4 aiming result. Changed hypothesis: the failed V1 placed the grasp far enough forward to expose the rear stock and forearm cuts. First investigate whether bringing the original held assembly closer and toward the lower-right frame can keep the torso/stock naturally behind or outside the frustum while preserving the uncut mesh and both original grasps. This is a bounded falsifiable pose/composition experiment, not a promise that rigid placement can solve every phase.

- No forced full-arm visibility, no V1 `(46,8,-13)` anchor, no inherited 9 cm capsules, no use of archived V1 packages.
- Do not create a full new pipeline before inspecting one normal holding view. Stop at a visual gate before extending dynamics or selecting the map.
- Numeric convergence and finger equality are constraints, not appearance acceptance. Use actual game-viewport captures; wait for screenshot completion before changing a case.

## Protected scope and storage

Preserve all original 40 retained native files and the seven archived files. Keep original model/rig/weights/source clips/finger local transforms, camera `(25,0,60)` and world FOV 90, centered crosshair, original input/HUD/ammo/reload/lifecycle/collision/navigation. No model scale change, detailed character production, NPC AI, ADS, new locomotion, VFX, Catalog/allowlist/release, commit or push.

New code: `Tools/Integration/ue_first_person_composition_v2.py` plus its dedicated launcher. New private evidence: `Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/FirstPersonRebuildV2/<unique identity>/`. Phase 1 creates only transient actors in actual-city PIE; no native packages or editor-map saves. If later accepted and extended, new team packages use `/Game/ParisCombat/.../FirstPersonViewV2/`, separate from V1. Native paths are ignored by Git. No archived script is executed from its relocated path.

## Phase 1: bounded composition probe

1. Start saved V3 in the actual Paris city, Editor Bridge disabled. Record baseline class/model/camera/native hashes and archive completion. Allow original idle evaluation, then freeze the source mesh for matched-phase comparisons.
2. Spawn an owner-only, collision-free SkeletalMeshActor referencing the same model and original materials; use the engine's standard `SetLeaderPoseComponent` to share the evaluated pose. The local installed UE header documents this API. Its ability to render this exact independent transform and preserve fingers must be measured, not assumed. No new AnimBP or C++ helper is needed for this probe. Keep original full-body world representation owner-hidden.
3. Spawn the same rifle geometry in the transient view. Preserve the source mesh-to-held-rifle relationship with one rigid transform. Orient the display barrel to a fixed far camera target solely for these static frames, retaining the centered crosshair. Test three declared grasp positions, camera-local cm: A `(22,22,-16)`, B `(26,25,-18)`, C `(30,28,-20)`. These are bounded diagnostic samples for near/right framing, not claimed COD parameters or final defaults.
4. Preserve original materials and full geometry; try no forearm clipping at all. Do not hide defects with new masks during this pass. Measure head/torso and arm positions and inspect whether their projection stays out of the desired view. If any body part intrudes or a pose looks unnatural, mark it failed rather than silently culling it.
5. Capture the source baseline and the three stable candidates, actual viewport/crosshair/HUD. Keep source pose frozen across candidates; measure finger local matrices, grasp proxy errors, camera and original `WeaponAppearance` binding. Wait after each capture; never attribute a later phase to an earlier request.

## Presentation versus gameplay contract

Phase 1 is a static visual diagnostic only: it leaves `WeaponAppearance` bound to the V3 gun, owner-hidden, and does not fire/reload/move the player. Thus it does **not** pass gameplay with the new visible muzzle. Record the display/world mismatch explicitly. After the ordinary holding visual gate, a separate plan increment must select/test a binding strategy that keeps visible direction, muzzle/barrel obstruction and original gun transactions consistent. Do not silently bypass walls or certify old gameplay passes for this new view.

## Acceptance, stop and later order

Capture correction, 3 October: `composition_v1` exited 0 with unchanged hashes and finger matrices, but direct inspection found the source/A/B images were editor views and C included editor chrome. Those files do not establish a matched visual comparison. Preserve the identity and source snapshot. The one bounded harness retry, `composition_v2`, uses viewport-only `Shot` without `SHOWUI`, waits 20 seconds after establishing the player/control rotation, then at least 60 frames and 5 seconds per frozen candidate. The candidate positions and protected scope do not change. Inspect each resulting image before assigning any visual result.

For phase 1, require unchanged native hashes and source fingers, original grasp retention within the source's existing proxy error, protected camera, stock/cut boundaries outside view, natural apparent arm continuation, clear world center and no own-body obstruction. Visual inspection governs the image; user acceptance remains necessary. If no declared candidate is usable, stop rigid framing and write the precise remaining constraint before evaluating compatible existing holding content or bounded upper-body display adaptation. No unbounded offset sweep or more masks.

After a selected static direction, separately evaluate original idle sway, starting/stopping and directional motion, pitch/yaw, fire/recoil, stationary/moving reload and lifecycle. A still image cannot clear those. Then implement/validate the muzzle interface, repeat near-wall plus combat/HUD regressions and only consider team-map selection after human review. Failure returns to saved V3 by ending PIE; never overwrite V3 or restore archived binaries over later unique work.
