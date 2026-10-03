# First person display migration to Unreal runtime

Date: 3 October 2026. Owner: yg745. Yupu reports the preview model looks fine, but movement stutters; he explicitly requests migration into the formal UE-controlled version. This authorizes the bounded display integration and eventual team-map selection after fresh tests, not final FPS/MVP acceptance, NPC AI, VFX, ADS, new actions, asset publication or commit/push. [中文](CONTINUOUS_ARMS_NATIVE_IMPLEMENTATION_V1_ZH.md).

## Failure review and different mechanism

Read Failures/README.md, FP001 analysis and the complete-arm static/dynamic results. Keep accepted complete shoulder-to-hand mesh, original material bindings, `(22,22,-16)` cm grasp, source model/rig/finger poses/actions, camera `(25,0,60)` / FOV 90, saved V3 gun transactions and NPC representations. Do not revive masks, offset searches or finger repair. Replace editor Slate/Python display callbacks with a saved standard-node Blueprint actor and engine tick prerequisites; do not add runtime C++ without a demonstrated need. The observed memory pressure and suspected callback cost are not a measured stutter diagnosis or performance pass.

## Changes and storage

Create one separately named team Blueprint under `/Game/ParisCombat/Blueprints/ContinuousArmsNativeV1/BP_PC_ContinuousArmsNativeV1`, deriving from SkeletalMeshActor. Its owner-only arm component follows the original player mesh using LeaderPose. It spawns one owner-only, collision-free StaticMeshActor for the existing rifle and binds it to WeaponAppearance. Preserve the original V3 rifle as the world/source attachment input, hidden only from its owner. No animation, camera or model edits. The Blueprint uses explicit cached intermediate transforms rather than duplicating pure expression graphs. BeginPlay/init records source references once; engine PostUpdateWork tick follows source mesh and original gun. Dead hides display; reset restores visibility without reinitializing or changing the original AnimBP/ammo transaction.

Native bytes remain in the existing single writable SFTP workspace through the active Content alias. Unique evidence/source snapshots live under `Evidence/ContinuousArmsNativeV1/<identity>`. Guard all 42 existing native files and source FBX. Keep the map byte-identical during authoring/fresh tests. After those pass, preserve verified old city bytes privately and save only the new actor/reference in the existing team map; produce a new inventory. Never overwrite old inventory, original Blueprint, vendor files or release objects. No Catalog/allowlist/immutable release changes.

## Execution and acceptance

1. Confirm the user closed the preview, inspect Git/external hashes/ownership, fetch safely without merging dirty work. Author the new Blueprint with installed editor graph tools; Python is authoring/testing only, never a shipping per-frame dependency.
2. Compile/error-audit, save the new package and fresh-load with bridge disabled. Spawn the native actor once in PIE for tests; subsequent Python callbacks may observe/assert or drive test input but must not update display transforms/poses. Early check: initialized references/binding, original camera/AnimBP/finger correspondence and accepted holding. Stop if native tick fails or visible geometry changes; retain failed identities.
3. Regress four-direction movement, pitch/yaw, stationary/moving reload, visibility/death/reset and gunplay (16 cases/66 assertions including actual near-wall blocker). Check actual velocities, pose/contact proxies, no source changes and native tick update. Inspect actual game captures. Preserve generic M1 reload limitations rather than certify absent content.
4. Only after fresh native tests pass, select this bounded layer in the team map and hash/document it. Fresh-load the selected map and regress without a display-update Python path. A normal `-game` launch without Python/bridge verifies engine-controlled startup. Measure warmed frame times separately; migration alone is not proof of eliminating stutter. Do not silently lower city quality to mask it.

## Rollback and stopping

Author-v1 stopped before saving any package at a reflected function-name mismatch: Python `get_actor_transform` maps to C++ UFUNCTION `Actor.GetTransform`, not `Actor.GetActorTransform`. All 42 hashes remain unchanged. Preserve that report/exit; correct only the installed reflected name in a new author identity. A process exit 0 does not override a failed author report.

Author-v2 likewise stopped before saving: StaticMeshComponent.GetStaticMesh is a C++ getter, not a reflected UFUNCTION; use the Blueprint-readable StaticMesh property. Retain both failures and 42 unchanged hashes. Author-only startup now uses the engine Entry map to avoid compiling/rendering the whole city while constructing a new graph; all runtime, selection and gameplay tests still use the actual Paris map, not a replacement demo.

On author/test error keep the saved map V3 untouched and preserve new unselected drafts. Do not rerun occupied package identities. Before a selected-map save preserve verified prior bytes; after any failed save/regression stop with selection status and evidence rather than blindly copying old bytes over unique changes. User-owned engines are never killed; automated task engines use bounded waits/owned termination only. Pause for human review if final runtime framing differs or contact/geometry fails. No new detailed character production.

## Remaining asset report

Audit existing selected models and action candidates first. Produce synchronized EN/ZH gaps distinguishing missing model/parts, available but unintegrated animation, optional effects and undecided historical variant. No purchase or browser shopping is authorized in this package; Yupu will search Xianyu. Do not ask him to repurchase verified city/soldiers/generic movement or the accepted arms.
