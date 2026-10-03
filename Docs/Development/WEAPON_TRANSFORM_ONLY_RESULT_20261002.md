# Rifle transform-only correction - 2 October 2026

Subsequent human result: Yupu confirmed remaining walking/reload errors and requested a small leftward gun shift for thumb contact. The previous map/inventory below is historical; continue under `RIFLE_ACTION_ATTACHMENT_IMPLEMENTATION_V3.md` and its dated result, preserving original poses and earlier evidence. The review launch was not approval.

## Decision and saved change

Yupu's live test rejected the previous finger-layer repair: severe clipping and degraded fingertips. Follow `WEAPON_TRANSFORM_ONLY_REPAIR_V2.md`. The player and two Allied NPCs now select the original unchanged `ABP_PC_Allied_Stride_v1`. Only the three existing M1 attachments' relative translation/rotation changed. No mesh, rig, finger/bone pose, source motion, IK, scale, camera, muzzle local point, combat/reload logic, German actor or navigation/AI configuration was edited.

Selected `fit_v1/hollow_fit_zero` at the existing `hand_r` attachment:

| Property | Value |
|---|---|
| Location, cm | `(-20.4106432204, 5.3663108935, -0.7460446158)` |
| Rotation, pitch/yaw/roll degrees | `(6.6221461749, 94.1690979707, -3.0445799424)` |
| Scale | `(1, 1, 1)`, unchanged |

`city_author_v1` saved only the current team root map: 2,703,808 bytes, SHA-256 `31214e4f54c6b0e01e1f65a2ec60037cc2a0578d06288ae2ffe94babb2bbea61`. All other 35 retained files and four source clips stayed hash-identical; the author exited 0 with no Error/Fatal/ensure matches. A closed-editor verified copy of the rejected pre-edit map is retained in private `WeaponTransformV2/BeforeTransformOnly`, not used to roll back navigation. The old finger-layer package remains hash-identical and **unselected/rejected**, not a dependency or an authorized repair route.

## Evidence and limits

Private evidence root: `Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/CityGameplay20261002/WeaponTransformV2/`.

- `fit_v1`: five rigid candidates, front/side/FP idle views. The selected center fit is preferable to the ±3 cm variants; original sampled hand/finger transforms stayed identical across placements. Numerical grasp centers are calibration estimates, not mesh-intersection proof.
- `phases_v1`: rejected phase evidence because repeated single-node setup left stale poses. Preserve it; do not cite its six labels as real pose coverage.
- `phases_v2`: six reinitialized static poses covering idle, shoot, source walking and three reload times, 18 captures; maximum left-hand displacement 65.970 cm. Each gun-only placement left the sampled source hands unchanged; all 36 protected native drafts and source clip bytes matched. Exit 0 and no Error/Fatal/ensure matches. Idle and fire fitting improve; source walking and generic reload still show contact mismatch. These are sparse static views, not a full cycle or live stride/contact pass. Reload framing crops the raised rifle. No M1-specific reload is established.
- `NavigationFoundation/transform_nav_v1`: bridge-disabled fresh city load, no rebuild/replacement; retained 391 complete sample paths, six starts projected and five NPC starts connected. Four actual Allied/German short/80 m MoveTo arrivals passed (2.765, 4.566, 27.086 and 27.656 game seconds), off-mesh request rejected and an actually moving request cancelled. Protected draft/vendor bytes unchanged; exit 0, clean Error/Fatal/ensure and navigation-registration/replacement checks. This is retained foundation regression, not avoidance/AI/mission/contact/performance acceptance.
- `Runtime/combat_transform_v1`: 15 cases/62 assertions, all three original Allied AnimClasses and rigid attachments, player original class after reload/death/reset, unchanged native bytes. However the rendering process exited with `-1073741819` after its normal shutdown log; no Error/Fatal/ensure matches or causal crash record was found. **Not a clean process pass.** Preserve the report/log/screenshots; repeat with an independent identity, do not hide the exit failure.
- `Runtime/combat_transform_v2`: independent bridge-disabled rendering repeat passed 15 cases/62 assertions, three original Allied classes, exact rigid attachment location/rotation/scale and player original class after reload/death/reset. Reload/ammo conservation and obstruction/damage/lifecycle checks passed; protected native/vendor bytes unchanged. Exit 0 with no Error/Fatal/ensure matches; initial/final real city HUD captures inspected. This clean repeat does not diagnose the earlier exit failure or establish geometry/full-cycle/input/FPS acceptance.

Human review remains required. Original generic stock/trigger contact, complete moving contact, walking head/helmet view, final FP/ADS presentation and weapon/history acceptance remain open. No fingers were curled to conceal mismatch and no camera/head changes were made. VFX, new actions, follow/patrol/trees/faction interaction and new packaging are outside this correction.

## Storage and handoff

`Assets/Integration/CITY_WEAPON_TRANSFORM_DRAFT_INVENTORY_20261002.json` records seven active city packages, retains the 28-file reload dependency inventory and separately lists the rejected unselected trial (36 retained files, 35 active). It is unpublished workspace metadata, **not Catalog/restore authority**. Older city/grip/navigation map hashes must not overwrite the new map. Current regressions must explicitly select the transform inventory. Preserve all originals, failed evidence, prior map versions and bridge binaries; no bridge change/build was required here.

No new immutable asset release, Catalog/allowlist selection, public playable build, Git commit or push occurred. Open the current city for human comparison only after automated engines exit; then pause without resuming AI/VFX/action implementation.

Closeout before human launch: all 16,606 selected city/character/motion local file sizes/SHA-256 passed `check_asset_storage.py --local` with the three explicit baseline IDs; all 36 current retained draft sizes/SHA also matched. The Git storage guard checked 17,273 manifest records/source paths; four changed Python scripts and three PowerShell runners parsed, and `git diff --check` passed. Ignored native Content exposed no untracked publishable package paths. All automated engines exited. No claim of immutable/remote publication follows from workspace checks.

Human review launched at 21:19 local through `run_paris_review.ps1`, normal process PID 11568, unique `human-review-20261002-211920.log`, bridge disabled. No human result/approval has been received. Pause here and preserve this user-owned session; launch is not a presentation pass.
