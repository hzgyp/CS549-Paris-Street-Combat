# Continuous arms motion validation result

Date: 3 October 2026. [Implementation](CONTINUOUS_ARMS_DYNAMIC_IMPLEMENTATION_V1.md). [中文结果](CONTINUOUS_ARMS_DYNAMIC_RESULT_20261003_ZH.md).

## Outcome and next review

The accepted static complete-arm direction remains usable in the inspected movement, pitch/yaw and reload phases. No exposed shoulder/forearm cuts, head/equipment intrusion or large sleeve failure was observed in the reviewed images. Stationary and moving reload finish and restore ordinary holding; death hides owner arms/rifle, reset restores the original Stride AnimBP and view. This is bounded internal verification, **not human dynamic/contact approval or a saved playable selection**.

The remaining concern is generic reload contact, not a new model deformation task. Middle/late reload has open support fingers near the receiver and does not provide a verified M1 en-bloc clip insertion/release. It remains the previously approved simplified diagnostic reload, not a completed weapon-specific first-person kit. Do not repair the original fingers or restart character production to conceal this gap.

## Actual motion coverage

Private motion evidence: `Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/ContinuousArmsV3/`. All 27 completed images from `dynamic_full_v3` and nine from `dynamic_tail_v1` were reviewed in phase sheets; ambiguous reload, extreme-pitch and reset images were also opened individually. The combined evidence is **two independently recorded batches**, not a clean whole-process pass for the failed full batch.

| Check | Actual evidence and limitation |
| --- | --- |
| Start, forward/backward/left/right, stop | Existing CharacterMovement input; four directions reach 300 cm/s, stopped sample is zero. Some forward-series frames slow against existing boxes. Not a complete free-walking gait-cycle or physical keyboard test. |
| Pitch 0/±30/±60 and yaw 45 | Normal holding retains lower-right rifle and continuous support sleeve, no observed own-body obstruction. Original camera position/FOV retained within declared floating-point tolerance. |
| Stationary reload | 108 recorded Reloading samples in completed full-batch coverage, before/middle/late/finished pictures; 2/16 becomes 8/10 with one original phase commit. |
| Moving reload | Tail run records 30 Reloading samples above 100 cm/s, maximum speed 300; second reload after one actual shot, final ammo 8/9 plus one spent round. |
| Fire | Original fire transaction invoked. No separately connected firing/recoil animation or muzzle flash was added or certified. |
| Death/reset | Owner display hidden on Dead; alive/Ready and `ABP_PC_Allied_Stride_v1_C` restored on reset. Tail's six checks pass, exit 0, no report errors. |

The completed full-batch subset has 656 sampled frames; tail has 212. Maximum sampled source/follower finger-local component difference across these batches is `1.7293e-12`; maximum alive rear-grasp proxy error is `0.0000058394` cm. These protect pose correspondence, not mesh-surface or M1-specific contact acceptance. Images freeze evaluated source/player and slow world time for settling; they are not a real-time recording or FPS measurement. The sampled-walk GIF is a diagnostic pose sequence, including collision stops.

## Visible muzzle and original gunplay

Bridge-disabled actual-city `arms_muzzle_v1` temporarily binds the displayed standard StaticMeshActor as WeaponAppearance. Original Blueprint shot/reload/lifecycle functions are unchanged, but their spatial input now comes from the visible gun. The original world gun remains available for source attachment computation and owner-hidden; NPC guns/animations stay V3.

**16 cases / 66 assertions passed**, including hostile/friendly/world/barrel blocking, cooldown/empty/busy/invalid/dead rejection, reload commit/busy protection, reset generation, authoritative HUD and ammo conservation. An actual 79 cm camera-distance blocker produces `Barrel blocked`; barrel/camera forward dot is `0.9999991002`. Original camera `(25,0,60)`/FOV 90 and original AnimBP survive reload/death/reset; display binding and fingers are retained. Engine exit 0; no Error/Fatal/failed-ensure/assert/Blueprint-loop matches in this run's log.

The ordinary display aims toward the 200 m camera-forward point. This does not certify close-target barrel convergence, ADS, wall-retraction presentation, physical input, mission, AI, performance or packaging. SHOWUI combat captures include editor chrome around the actual PIE game view/HUD; they are not matched-phase animation pictures or a standalone-build capture. Motion pictures are separately verified viewport-only evidence.

## Retained failures and corrections

| Identity | Result |
| --- | --- |
| `dynamic_early_v1` | Vendor BP_Building_Parent loop before arm setup, zero motion images; PIE teardown then task termination. Cause unverified, not a clean pass or model failure. |
| `dynamic_early_v2` | Numeric tests/exit 0, but stopped photograph is editor view; incomplete visual gate. |
| `dynamic_full_v1` | Cancelled after discovering that invalid early image; no acceptance. |
| `dynamic_early_v3` | Five inspected actual-game images, internal early gate passed, exit 0. Source freeze/slow world replaces SetGamePaused. |
| `dynamic_full_v2` | Editor runs but no script/PIE artifact observed within four minutes; cancelled, startup cause unverified. |
| `dynamic_full_v3` | Console dispatch works; 27 completed images then exact camera-vector assertion fails at yaw 45 on approximately 2e-13 cm roundoff. Preserved failed status despite exit 0. |
| `dynamic_tail_v1` | Declared 1e-6 cm/FOV tolerance, actual preload reload, remaining nine phases/six checks pass; no direct ammo injection, exit 0. |

Failed reports, snapshots, captures, logs and external REVIEW files remain private. No higher engine loop limit, offset sweep, opacity mask, source finger edit or vendor repair was used. Startup routing success does not diagnose earlier startup failures.

## Storage and handoff

All 42 retained native sizes/SHA and source exchange FBX hash match. Actual local hashes for the 721-file character integration baseline and 35-file selected rifle-motion baseline pass (756 files); the Git storage guard validates 17,273 selected manifest records, not all city bytes. Source parsers and CRLF-aware diff checks pass. All task-owned editors closed.

Saved city remains V3, SHA `d00056e8e65d3de6cf7c6af08fe9e52fa4e95e656bfe10a7392c03a82409f51f`. This increment creates **zero native packages** and saves no map; only the previous two arm-derivative packages remain unselected. All evidence stays in the existing single private workspace. No Catalog/allowlist/release, C++ bridge deployment, new actions/VFX/AI, packaging, commit or push.

Next required gate: Yupu reviews the new motion/contact direction, especially generic reload middle/late. Only afterward document native Blueprint owner-view integration/fresh runtime validation without diagnostic Python, then seek an explicit map-selection decision. Do not silently replace saved V3 or resume paused NPC behavior work.
