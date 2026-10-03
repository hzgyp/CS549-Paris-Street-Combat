# Native first person display migration result

Date: 3 October 2026. [Implementation](CONTINUOUS_ARMS_NATIVE_IMPLEMENTATION_V1.md). [中文](CONTINUOUS_ARMS_NATIVE_RESULT_20261003_ZH.md).

## Outcome

The accepted complete-arm display is now selected in the current team city as a standard-node Blueprint, not an editor Python display callback. The source soldier model/rig/finger poses/actions, camera `(25,0,60)` cm/FOV90, V3 rifle actor, gun transactions, NPCs and existing navigation content are preserved. Source mesh and V3 world gun are hidden only from the owning player; the new owner-only arms follow source LeaderPose and the spawned visible rifle supplies WeaponAppearance. UE PostUpdateWork actor tick with source mesh/original gun prerequisites updates cached transforms. No runtime C++ bridge or new gameplay system was added.

This is local integration, not packaged release, SFTP Catalog selection, final performance/course acceptance or complete M1-specific reload. New actions, ADS, NPC behavior and VFX remain outside this increment. No commit/push occurred.

## Bounded checks

| Check | Evidence |
| --- | --- |
| Author and compile | `author_v3`, new Blueprint 652,470 bytes, SHA `45a11672cf7f3a99bac7598a33357fb6dcd4f90fe3e8e064ed2a5430ff2a84d1`, no graph errors; original42 unchanged. |
| Native movement/poses | `motion_v1`, 462 observed frames, four directions reach >100cm/s; 49 samples are simultaneously moving >100cm/s and Reloading. Maximum rear-grasp proxy error 0.000005375cm; finger-local correspondence/camera guard pass. Two reload commits, dead display hidden and alive/Ready/original AnimBP after reset. Exit0, no report/errors matched in reviewed log. |
| Images | Six actual game images individually opened. Idle/reset retain continuous sleeve and lower-right holding. Unfrozen requests capture after phase changes: up/down are not exact requested pitch proof, reload image is completed holding and moving-reload image is later death hiding. Do not claim middle/late contact acceptance from these files. |
| Unselected native gunplay | `native_combat_v1`, 16 cases/66 assertions pass, actual79cm blocker and barrel/camera dot0.9999991002; exit0, reviewed log has no Error/Fatal/failed ensure/assert/Blueprint-loop match. Python does one-time native actor spawn and read-only observations, not display update. |
| Selection | `select_v1` adds one native display actor and serialized player reference only. V3 city backup matches original hash; 42 existing files except allowed map remain unchanged. New43-file inventory is `CITY_CONTINUOUS_ARMS_NATIVE_INVENTORY_20261003.json`. |
| Selected city fresh-load | `selected_combat_v1`, native actor already supplied by saved map. Same16 cases/66 assertions pass, 79cm blocker; original AnimBP/FOV90, display binding and finger-local delta9.37e-13 after reload/death/reset. Exit0, unchanged guarded files, clean reviewed error patterns. |
| Without Python | `game_no_python_v1` ordinary `-game`, PythonScriptPlugin and ParisEditorBridge explicitly disabled, completed600 engine frames and exited0. Actual1280x720 game image opened: new arms/rifle, centered crosshair and HP100/AMMO2/16/Ready HUD present. Error-pattern review clean. This is a startup image with texture preparation/blur, not final texture or warmed movement/performance acceptance. |

Saved city now has 2,707,948 bytes, SHA `2791b4a7f76b4b3d07f42286b6ad0156c3a185c2e3e795fa2446aaac0ad68519`. Prior V3 `d00056e8...09f51f` is historical, with verified private backup at `Evidence/ContinuousArmsNativeV1/select_v1/BeforeNativeSelection.umap`; never restore it automatically over this selection.

## Retained failures and limitations

Author-v1/v2 exited0 but reports failed before native saves: reflected Actor.GetTransform name differs from the Python method; StaticMeshComponent.GetStaticMesh is not a UFUNCTION, so use its Blueprint-readable property. Installed engine headers established corrections. Preserve both identities; no occupied assets were overwritten.

The user reported preview model appearance looks fine and requested this migration, not universal final contact or FPS approval. Generic source reload still lacks verified M1 en-bloc clip/bolt action. Native observation establishes correspondence and gameplay, not exact mesh-surface contact across every phase. The standalone game startup proof is not a recooked packaged build.

Memory-pressure warnings remain during actual city loading; native motion log records50 PSO creation hitches, none precached. These are real performance concerns, not a measured exclusive cause of the earlier user's stutter. No quality settings were reduced, and removing Python alone does not establish smooth movement or target/stress FPS.

All native/evidence bytes remain in the existing single private workspace. No vendor source package, animation, old Blueprint or camera setting changed. Newly missing asset requirements are [the English inventory](ASSET_GAPS_20261003.md) / [Chinese Xianyu checklist](ASSET_GAPS_20261003_ZH.md): articulated M1 parts/matching actions, German rifle candidate, optional shot effects; run/jump/slow/crouch/prone already have named candidates.

Final checks: actual756 selected character/rifle-motion source files verified locally; storage/Git metadata guard verifies17,273 selected records. All43 current native files and source exchange FBX rechecked after engines close. All task-owned engines closed. Python and PowerShell syntax checks passed. No remote publication or second-machine restore was performed.
