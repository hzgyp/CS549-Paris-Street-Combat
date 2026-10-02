# Character and Weapon Integration Implementation Plan

Prepared 1 October 2026 for Paris Street Combat, after private release `character-20261001-v1` and source commit `37de536`. This document defines the next two work packages: **1, character integration in the Paris project; 2, weapon and action integration**. They cover part of pipeline Gate 1 and the early Gate 2 combat spine, not the entirety of either gate. All implementation and acceptance items below are **Not run** unless a later dated result explicitly records otherwise.

The [pipeline](../../DEVELOPMENT_PIPELINE.md), [technical design](../Design/TECHNICAL_DESIGN.md), [Assignment 3 goal](ASSIGNMENT3_GOAL_V1_EN.md), [acceptance checklist](ASSIGNMENT3_ACCEPTANCE.md) and [asset repair record](../../Assets/CHARACTER_COMPATIBILITY_AND_REPAIR.md) remain authoritative. This plan makes their next steps executable; it does not replace the mission survey, four pillars or delivery requirements.

Dated execution results: [1 October integration checkpoint](CHARACTER_INTEGRATION_RESULT_20261001.md). P0/P1 passed their bounded checks; P2 has a fresh-reopened six-actor diagnostic preview and sampled poses but remains partial. Follow the result's next action, not the preparation-only checkpoint at the end of this plan. No weapon/gameplay/performance acceptance is implied.

Later execution: [directional/stride/lifecycle checkpoint](CHARACTER_LOCOMOTION_LIFECYCLE_RESULT_20261001.md) and [P3 capability/human choice](WEAPON_CAPABILITY_REVIEW_20261001.md). Retarget, directional and bounded lifecycle work is implemented; P2 remains partial and P4 is not started. Continue ordinary implementation without intermediate permission requests, but do not bypass the documented missing-weapon/view/reload decision or asset-rights gates.

## Starting conditions and boundaries

- Active project: `Unreal/ParisStreetCombat/WW2FranceLiberation.uproject`. Pin UE **5.8.2**; use Blender **5.2.2 LTS** only for bounded exchange adaptation if needed. Blueprints remain primary; no new C++ subsystem is planned.
- The verified character baseline has 540 native UE packages, 148 textures, 19 FBX files, 12 Blender sources and two lab configuration files. Preserve native UE materials, skeletons and PhysicsAssets; Blender exchange is not an authoritative replacement for the native closure.
- Four adapted mesh candidates have persisted PBR eyes. Use one Allied and one German configuration initially, retaining the others as comparisons. Selection is provisional technical testing, not historical approval.
- The included M1 Garand is a rigid world-weapon candidate. A compatible first-person view, correct weapon-specific reload and ammunition props are **not** accepted. The generic rifle animation family alone does not close that gap.
- Yupu owns this local integration pass. Yuqi/Jingdi responsibilities remain proposed until kickoff confirmation. Teammates handle their own SFTP restoration; Yupu's local work does not wait for their reports. Each teammate still verifies their own files before editing, and second-machine acceptance remains required later.
- Do not restart detailed soldier generation, remodel heads/clothing, purchase assets automatically, enable new driving/multiplayer scope or run archived gunplay generators. No whole-city duplication or mutable `latest` release.
- Historical date, units, uniforms and weapon variant remain separate decisions in [RESEARCH_GAPS.md](../../HistoricalReference/Paris1944/RESEARCH_GAPS.md). Compatibility tests may use labeled provisional candidates; do not declare final historical or public-build distribution acceptance.

## Work package order and checkpoints

| Checkpoint | Work | Exit condition | On failure |
| --- | --- | --- | --- |
| P0 Local readiness | Git/SFTP state, ownership, engine/plugins and single physical working storage | Required local bytes verified; no unresolved overwrite conflict; engine and writable paths recorded | Preserve edits; resolve the exact missing file or storage conflict before migration |
| P1 Native character closure | Bring the complete native dependency closure into the active Paris project without package renaming | Fresh active-project load resolves meshes, materials, skeletons, physics and selected actions | Fix the bounded missing dependency/configuration; do not substitute lossy FBX |
| P2 Character presentation | Shared combatant shell, faction configurations, locomotion/action preview, six-actor renderer/contact checks | Repeatable textured, moving character test in a team-owned compatibility map | Record defects; make bounded adaptations only; no new detailed character production |
| P3 Weapon presentation decision | Inspect included rifle, animation contacts and player camera alternatives | A supported player view and selected rifle/reload representation are identified | Report a precise missing-asset list; keep unrelated character work usable |
| P4 Combat and action transaction | Input, aim, authoritative shots, ammo/reload events, death/cancel/reset | Repeatable shot and animation-event cases agree with state/HUD | Debug one owner/transaction at a time; no timer-based hidden ammo commit |
| P5 Save and release | Fresh reopen, bounded packaged smoke test and verified asset publication | Actual results, changed dependencies and versioned bytes recorded; matching source/configuration prepared | Retain unpublished work honestly; do not publish missing-byte references |

Do P0-P2 first. P3 decides whether the existing assets permit P4 or whether a weapon/view/reload gap must be resolved. A simple shooting placeholder may diagnose traces, but cannot pass first-person or reload presentation acceptance.

## P0 Local readiness and storage

1. Inspect `git status --short --branch`, fetch safely and compare ignored assets to the selected `Assets/Sync/CATALOG.json` manifests. Preserve differences before any restore. Record the starting revision/version, engine/plugins and named binary owner. Do not repeatedly download verified unchanged files.
2. Identify any running Unreal/Blender process and the exact project it holds. Close affected editors before relocation/restoration. Check free disk space for caches, temporary verification and a package; no numeric space budget is assumed until measured.
3. On this server, use one writable runtime tree under `Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Content/`. The existing active Content tree is still outside that physical tree. If relocation is needed, inventory/hash its exact contents, check for unique unsynchronized files, refuse an occupied destination, and move the existing tree on the same volume. Verify file count, size and SHA-256 afterward, then make `Unreal/ParisStreetCombat/Content` a checked junction to it. This is relocation, not a new full city copy; published baselines and originals remain unchanged.
4. Promote the verified character working directories into runtime Content without creating another complete editable lab copy. Preferred method, with both editors closed: relocate the unchanged mount roots `GermanSoldier`, `USParatrooper`, `RifleAnimsetPro` and `ParisCombat/Characters/Adaptation` from the lab to their identical runtime mount paths, verify every published native hash, and retain checked lab-root aliases to the same writable bytes. Refuse existing target conflicts; do not merge blindly. No `/Game` package identity changes are permitted through a filesystem move. Use Unreal's editor-aware migration/rename tools if any package identity or reference must change.
5. The lab and active project must never edit those shared physical packages simultaneously. Keep diagnostic maps out of runtime Content. Preserve original and immutable release bytes; never junction an editor to `/baselines` or `/objects`. Grant shared-account Modify to rights-cleared shared asset directories, keeping the OpenSSH root protected.
6. Record physical paths, aliases and ownership. At the next release, make runtime paths the native assets' authoritative restore destinations and record superseded lab paths explicitly. Preserve old immutable release manifests; do not create competing restore owners or blindly delete alias targets.

This task does not delete the original vendor delivery or private backups. Any additional redundant-copy cleanup requires enumerated targets, verified retained hashes and preservation of unique work.

## Work package 1 Character integration

### P1 Load and dependencies

Load the active project in UE 5.8.2 and establish its actual editor/automation entry point. Inspect required plugins, city load and the promoted 540-package character closure in this project, not merely the standalone lab. Report missing packages and shader/Blueprint errors separately. Preserve the vendor city, German, US and animation namespaces.

The four candidate adapted meshes are:

- `/Game/ParisCombat/Characters/Adaptation/Meshes/SK_WWII_GermanSoldier_varA_UE582_v1`
- `/Game/ParisCombat/Characters/Adaptation/Meshes/SK_WWII_GermanSoldier_varB_UE582_v1`
- `/Game/ParisCombat/Characters/Adaptation/Meshes/SK_WWII_US_Paratrooper_simple_UE582_v1`
- `/Game/ParisCombat/Characters/Adaptation/Meshes/SK_WWII_US_Paratrooper_simpleB_UE582_v1`

Verify eye bindings, all material/texture dependencies and the German-to-US texture dependency in a fresh session. Inspect skeleton/action compatibility in the target project. Do not force compatibility by relabeling bone names, overwriting the reference pose or assuming the lab's hierarchy test proves every clip/contact.

### P2 Components and tests

Create a team-owned compatibility map under `/Game/ParisCombat/Tests/`. Use a controlled floor, movement obstacles and spawn points for diagnosis, then test the same characters in representative actual city lighting and ground. This test area is not the final mission route; survey the connected city separately before selecting objectives.

Proposed team components, to be created only during implementation:

| Package or component | Responsibility |
| --- | --- |
| `Blueprints/Characters/BP_PCCombatantBase` | Character movement/capsule, common health/action lifecycle and explicit faction/role identity |
| `Blueprints/Characters/BP_PCPlayer` and `BP_PCNPC` | Player-specific camera/input or NPC configuration, sharing base contracts |
| `Blueprints/Components/BPC_PCHealth` | Damage acceptance, clamped health and one death transition |
| Skeleton-specific `Animation/ABP_PC_*` | Compatible locomotion and action presentation driven by authoritative state; no independent ammo counter |
| `Tests/BP_PCIntegrationHarness` | Repeatable inputs, state/notify counters and debug evidence; not production NPC AI |

Use a shared action contract across factions, with skeleton-specific animation assets where necessary. Choose idle/walk/run, aim/fire/reload, hit and death from the actual native library; record exact clip names, root-motion/in-place selection and missing capabilities. Do not apply root motion and movement twice. Crouch remains Should if supported. Do not use empty-handed playback to certify gun contact.

Test at representative distances and front/side views: mesh scale/orientation, capsule clearance, foot height/sliding, arm/elbow/knee deformation, helmet/equipment attachment, all textures and the four eye variants in actual daylight/shadow. Use one player-shaped actor, two allied and three German test actors for a six-actor baseline. Scripted harness motion is not an AI/navigation pass. Record preliminary frame/CPU/GPU/material observations without claiming the full-mission 60 FPS target or generating LODs before measurement.

Death stops accepted input/actions, movement and firing, transitions exactly once, and invalidates stale callbacks. Use the supplied death animation initially; full ragdoll recovery is optional, not an added blocker. Fresh-save/reopen before P2 acceptance.

### P2 implementation continuation on 1 October

The first diagnostic preview did not implement playable Characters. Continue with a shared native-Character Blueprint parent, player/NPC children and separate Allied/German animation Blueprints. Author identity/configuration in the shared shell; health/death and action arbitration still need their own subsequent implementation and tests before full P2 acceptance. Preserve the earlier preview map unchanged.

The actual 540-package registry contains no Blueprint or AnimBlueprint. The installed Python reflection exposes Blueprint creation, variables, compilation and subobjects but not the graph node creation/allocation needed for input and animation graphs. Local engine headers confirm those operations are C++ editor methods. This is the demonstrated need for a small **Editor-only** `ParisEditorBridge` plugin: it generates standard engine Blueprint nodes and runs a bounded diagnostic Game World. It must not supply a C++ gameplay parent, damage/ammunition system or runtime plugin dependency. Keep it disabled by default, enable only in the authoring/test process, build in an ignored empty host project without copying city/model assets, and retain reproducible source in Git. Generated gameplay uses normal Blueprint/native-engine nodes after the bridge unloads.

Implement walk/look requests in Blueprint, a diagnostic trailing player camera and in-place locomotion from measured velocity. The trailing camera is for movement testing, not final FPS presentation. Start with explicitly provisional idle/walk/run BlendSpace speeds of 0/150/300 cm/s; measure stride/contact rather than claiming those defaults eliminate sliding. Two skeleton-specific BlendSpaces reference the existing native clips without modifying them. BlendSpace bytes and diagnostic maps remain SFTP drafts; exact team-authored Blueprint logic may enter the source allowlist after verification.

Keep mesh scale at 1.0, rotate its native +Y forward axis to Character +X, and derive the vertical mesh offset from the native reference geometry/bounds and capsule dimensions. Do not lower/scale the entire actor arbitrarily to hide floating. Record capsule radius/half-height, mesh offset, actual floor gap, animation minimum geometry height and any remaining mismatch. Movement comes from CharacterMovement; do not also apply root motion.

Create a new team-owned movement test map, with one player and five independently configured NPC-shaped Characters, a broad floor and finite obstacles. It is not the final mission route. Compile all generated graphs, fresh-open their assets/map and verify actual parent/mesh/anim references. In a separate transient Game World, invoke the same Blueprint movement-request function and tick the engine at declared fixed steps; record settling, forward/side movement, stop/braking and wall contact. Assert stable capsule clearance and no wall penetration, and inspect front/side rendered evidence. This bounded harness is not PIE input-device, AI/navigation, city-ground or packaged-build acceptance. If the harness or bridge fails, preserve generated drafts and exact errors; fix a bounded cause before claiming success. Do not overwrite existing packages on rerun or resave purchased packages. No immutable publication or Git push is implied by local generation.

## Work package 2 Weapon and action integration

**2 October scope update:** Yupu approved useful baseline publication and a simplified reload diagnostic slice. Follow [the bounded continuation plan](WEAPON_BASELINE_AND_SIMPLIFIED_RELOAD_V1.md). This resolves the previous human reduced-presentation choice; it does not clear historical FP arms/contact, M1-specific moving parts, German rifle or final presentation. The marker for simplified reload is explicitly a placeholder animation-phase event, not physical en-bloc insertion. Keep P4 transaction guards and timeout-cancels-only semantics below.

### P3 Inspect before choosing

Record the included world weapon's package, dimensions/orientation, available bones/moving parts, textures, grip/muzzle transforms and ammunition props. Check selected native action clips with the weapon attached, especially trigger/support-hand contact and reload mechanics. Do not call the generic rifle reload an M1 en-bloc reload without inspecting it.

Evaluate a bounded existing-full-body first-person camera test first if its head clipping, sleeves, arms, aiming and contacts are viable; otherwise identify a coherent licensed first-person arms/rifle/action kit gap. This is a feasibility check, not approval of an unsuitable third-person mesh as first-person content. No face/body remodeling to force the camera solution. Final weapon variant and historical configuration remain provisional until separately decided.

Output a capability matrix: player camera/arms, world rifle, fire/aim, reload mechanism, required clip/round/bolt parts, NPC grip and enemy rifle. Mark each `Available`, `Needs bounded adaptation`, `Missing` or `Not tested`, with source/evidence. If a required capability is missing, give Yupu the exact delivery/rig/action requirement; do not purchase, generate a detailed replacement or silently mark the presentation passed.

### P4 State and ammunition

Proposed packages: `Blueprints/Components/BPC_PCWeapon`, `Blueprints/Input/PC_*`, `Animation/Montages/AM_PC_*` and a debug HUD under `UI/`. Weapon configuration holds the selected rifle, capacity/reserve, cadence, range and attachment points. Do not decide a historical ammunition mechanism from arbitrary debug values.

The weapon component owns ammo and accepted shots. Health owns damage/death. The action coordinator owns legal Ready/Aiming/Firing/Reloading/Dead transitions; locomotion remains separate. The AnimBP/montage reports guarded events; UI displays those authoritative values. Input requests an action rather than playing unrelated montages directly.

Reload transaction:

1. Reject reload when dead, already reloading, full or without usable reserve. Start a unique ActionID tied to the current restore generation.
2. The selected reload animation reaches a documented physical insertion/commit moment. Dispatch its notify carrying the expected action identity; verify live state, action identity, generation and not-yet-committed status.
3. Transfer ammo once using the chosen weapon's documented rule. For a simple bounded debug capacity model, transfer is `min(capacity - loaded, reserve)`; this is not proof of partial M1 reload mechanics.
4. Cancel before commit without ammo change; cancel after commit without repeating/refunding the transfer. Duplicate/stale notifies do nothing. Death/restart invalidate pending actions. A timeout cancels and reports a stuck action; it never manufactures an ammo commit.

Shooting follows the technical design: reject illegal input/cadence, resolve camera intent then muzzle path/clearance, assign one accepted ShotID, consume one round and apply at most one damage result. Feedback uses the same hit position/normal/surface. Document the inside-wall rejection/clearance policy before testing; do not permit camera-only damage through cover. Confirm movement, obstruction and target filtering policies independently; the shooter must not hit itself and an invisible capsule must not incorrectly shield the visible target.

Use a single health reset/restore generation for stale-event rejection. Repeat firing/reload/death/reset from controlled initial state. This package proves the local combat/action contracts; full objectives, ally behavior, enemy perception/navigation and checkpoint saving follow their later implementation work.

## Acceptance and evidence

Use `Not run`, `Pass`, `Fail`, `Blocked` or `Deferred optional`. Record tester/date, Git revision, asset versions, engine/plugins, exact input/settings, expected/actual result, defects and evidence paths. Store raw images/videos/logs outside Git; publish permitted evidence bytes with verified version records when authorized.

| Test | Procedure and required result | Course mapping |
| --- | --- | --- |
| INT-CHAR-01 | Fresh active-project load resolves all required native dependencies and persisted eye/material bindings | ENV-01 and ASSET-01, partial evidence only |
| INT-CHAR-02 | Front/side locomotion and hit/death at representative distances; no gross joint collapse/detached equipment; capsule and visible mesh contacts reviewed | ASSET-01 and ANI-01, partial |
| INT-CHAR-03 | Four face variants under actual city daylight/shadow; six-actor presentation and declared renderer/settings recorded | ASSET-01; preliminary performance only |
| INT-WPN-01 | Supported player view and exact rifle/rig/reload/props/contact matrix; no unlabeled placeholder pass | ASSET-01 |
| INT-ANI-01 | Repeated reload, duplicate notify, missing notify/timeout, interruption before/after commit, death and stale event after reset; exactly one permitted transfer | ANI-01 |
| INT-COL-01 | Open target, wall/corner, muzzle-inside-cover and window/frame cases; one accepted-shot/ammo/damage result matching obstruction policy | COL-01, partial |
| INT-STATE-01 | Health/ammo/HUD agree after each action; reset three times without duplicate events or residual firing | UI-01 and RESET-01, partial |
| INT-BUILD-01 | Bounded packaged Windows compatibility smoke test outside the editor; assets load and the accepted local action cases work | BUILD-01, partial; not the full mission or second machine |

For action tests, use playback rates 0.5, 1.0 and 1.5, and controlled frame-rate cases 30/60/120 where the machine can sustain them. These are planned stress inputs, not measured performance or new course targets. Record unsupported cases rather than treating the setting alone as a test result.

Keep [ASSIGNMENT3_ACCEPTANCE.md](ASSIGNMENT3_ACCEPTANCE.md) statuses unchanged until each complete criterion is demonstrated. This work cannot pass NAV-01, AI-01, OBJ-01, full LOOP-01, PERF-01 or course delivery simply by producing animated characters.

## P5 Publication and next action

### Recovery rules

- Before changing a native package, record its accepted version/hash and the immutable recovery object. A checkpoint is a version reference plus verified bytes, not another full city copy.
- If relocation fails, keep editors closed, record which exact paths moved and rehash the retained files. Repair the alias or restore the prior placement only after validating both exact paths and refusing an occupied destination. Do not recursively delete a junction or its target to undo the move.
- If a character/material/action adaptation fails, preserve the changed files as a clearly named ignored draft, then restore only the affected verified previous-version files with editors closed. Keep unrelated edits. Remove a newly generated package only after confirming it is task-owned, no required reference depends on it and its diagnostic recovery version is retained.
- If P3 identifies a required weapon/first-person gap, retain accepted P1/P2 work and report the missing component. Do not conceal the gap with a generic reload, discard the entire character integration or restart soldier production.
- If upload fails, keep local files and draft metadata; if Git publication fails after upload, keep verified immutable objects. Never publish references to incomplete transfers or rewrite the previous release in place.

### Handoff

Save and close editors, enumerate changed/new native dependencies and text configuration, then fresh-open the target project. Publish only permitted changed/new asset bytes as new immutable SFTP objects and verify final hashes before updating the complete manifests. Existing originals/releases remain unchanged. Record native restore paths, transitional aliases, retired paths and one editing owner. Shared CRUD does not permit casual overwrite of published versions.

Small team-authored Blueprint **logic** may enter Git only after an exact owner/path/classification entry in `Assets/Sync/GIT_CODE_ALLOWLIST.json` and the 10 MiB cap/guards pass. Purchased/native meshes, textures, animation sequences, montages, exchange files and diagnostic binaries remain SFTP bytes. Do not whitelist a referenced purchased model as code. Generated caches stay ignored. Do not commit/push or publish a new release merely because this plan was written; follow the current task's publication authorization.

Write a dated implementation result under `Docs/Development/` with completed checkpoints, actual tests, missing assets and next bounded action. Do not convert this plan into a success report. After local character/weapon acceptance, continue the city survey/readiness and the configurable combat/mission spine; the final mission area, AI budget and performance limits still require measurement.

**Latest implementation checkpoint:** P0/P1 completed, followed by initial previews and a shared Blueprint Character/locomotion draft. Read [the movement result](CHARACTER_MOVEMENT_RESULT_20261001.md): numeric movement/collision passed but full P2 has not. Initial preparation of this plan changed no Unreal assets; subsequent implementation did create the documented local drafts.

**Next bounded P2 actions, before weapon integration:** diagnose German source/target reference poses, pelvis/leg translations and existing translation-retarget settings without resaving vendor packages. Use that evidence to select a bounded engine-native retarget adaptation on new team-owned drafts, preserving existing skeleton names/reference poses and immutable baselines. Do not substitute a constant actor drop for the phase-varying contact gap. Introduce verified backward/lateral native clips and velocity direction into locomotion, then test complete gait cycles, transitions and measured planted-foot/stride contact. Preserve current drafts/hashes and uniquely identify new evidence; fresh-load and repeat fixed-step movement/contact tests before declaring improvement. Shared health/death/action ownership, actual input/camera and city-ground checks still follow their P2 gates. No immutable publication or commit/push is implied.

### Continuous implementation: contact and directional locomotion

The team authorizes continued implementation under this manual, with a stop only at a required human decision. Routine diagnostic/repair checkpoints do not require another approval.

1. Record complete source/target reference transforms and translation-retarget modes using a read-only editor diagnostic. Inventory native directional actions and installed UE 5.8 retarget APIs. Keep the v3 movement evidence intact.
2. If proportions differ, construct source/target IK Rig and IK Retargeter drafts under `/Game/ParisCombat/Animation/RetargetDraft/`. Match named chains and reference poses; retain all vendor skeletons and packages. Batch-export a bounded set of locomotion and hit/death actions to new target-specific native sequences, never overwriting existing packages. Record mappings, settings and warnings. Do not replace contact correction with arbitrary mesh/capsule lowering.
3. Build new two-axis locomotion drafts with actual pawn velocity in actor-local forward/right axes. Include idle and verified forward/backward/lateral/diagonal actions; reject missing or misdirected clips. Preserve the previous one-axis draft for comparison. Keep root motion disabled for this CharacterMovement-driven slice.
4. Sample complete cycles and transitions at 30/60/120 steps per second. Measure visible boot contact as well as capsule clearance, per-frame foot positions and planted-foot drift. Review front/side captures and finite geometry. Contact/stride defects remain explicit failures; numeric movement alone does not clear them.
5. Continue shared Blueprint health/death/action ownership and P3 capability inspection when this bounded locomotion work is viable. Escalate only a genuine missing licensed capability, required historical/asset choice, unavailable human acceptance or publication authority—not an ordinary intermediate milestone.

All new native drafts and raw evidence use the existing canonical SFTP workspace. Add ignore rules before generation, preserve original bytes and record fresh-load hashes. This section is a plan, not a claim of passed tests or released assets.

After stride regression, create a separate six-Character `P2_CharacterStride_20261001` diagnostic map using existing V2 lifecycle classes and explicit per-instance calibrated AnimClass/mesh settings. Preserve the prior lifecycle/movement/preview maps and class defaults for comparison. Verify those overrides in a fresh bridge-disabled load; configure spawned combatants explicitly in later integration rather than assuming every class default has switched to this profile. The diagnostic map is not the Paris city or a mission.

**Bounded shared lifecycle draft:** create new child Blueprints under `Blueprints/Characters/LifecycleDraft/`, retaining prior movement classes. The base owns Health/MaxHealth, IsDead, ActionState, ActionID and RestoreGeneration. Reject non-positive and post-death damage; clamp health, enter death once and invalidate pending action identity. Disable movement and capsule obstruction on death, play the existing finite death clip (no ragdoll claim), and restore animation-blueprint mode, collision, movement, health and action identity on an explicit controlled reset. Player/NPC children reuse this owner. This slice initially supports Ready/Dead only, not a completed firing/reload coordinator or checkpoint snapshot. Test damage, repeated death, negative damage, three resets and restored movement/AnimInstance. A reset test restores a controlled test transform separately and does not claim mission/checkpoint restoration. Keep first-person/weapon acceptance under P3/P4.

**Stride calibration:** the source root-motion counterparts measure ~204 cm/s forward walk, ~216 cm/s right strafe and ~361 cm/s forward run, while diagnostic CharacterMovement uses 150/300 cm/s. For each moving sample, derive its original planar distance / native duration and account for sequence RateScale. Duplicate the two directional BlendSpaces/AnimBPs to uniquely named `_Stride_v1` drafts and set only sample playback scale to requested sample speed / measured source speed. Retain in-place playback and CharacterMovement as sole translation owner. Refuse missing, zero-speed, additive or unexpectedly mismatched action counterparts. Compare complete cycles/drift with v5, preserving old drafts. The low-vertical-motion bone drift heuristic is not a sole-contact detector or an IK acceptance criterion. Review residual transition penetration separately rather than hiding it with actor offsets.

**Evidence-driven method selection:** `Evidence/P2/Retarget/reference_diagnosis_v1.json` shows essentially matching reference bone translations, but German root/pelvis use `Skeleton` translation while the source/Allied root/pelvis use `Animation`. Before building an unnecessary IK chain pipeline, compare poses with a temporary, restored root/pelvis mode override without saving originals. If confirmed, duplicate only the German skeleton and the two dependent adapted meshes into `RetargetDraft/GermanTranslationV1`, set root/pelvis to `Animation` on that new skeleton, and keep reference transforms, geometry, weights, materials and source action bytes unchanged. The extra mesh packages are necessary versioned adaptations in the same canonical store, not scattered working copies. Use original compatible in-place actions, retaining vendor native namespaces untouched. Validate fresh-load dependency/mode persistence and all four variants at complete-cycle sampling before selecting this branch.
