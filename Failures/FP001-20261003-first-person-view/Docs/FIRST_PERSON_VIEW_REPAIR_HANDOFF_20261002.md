# First person arms and camera occlusion repair handoff

## Purpose and latest decision

Yupu completed the runtime aiming preview and confirmed two unresolved visual defects: the arms extend outside the view, and movement obstructs the camera. This handoff prepares the next conversation to diagnose and repair those two defects without undoing the existing assets or tested gunplay. This turn changes documentation only; it does not implement another repair or approve the aiming trial.

The synchronized Chinese review is [FIRST_PERSON_VIEW_REPAIR_HANDOFF_20261002_ZH.md](FIRST_PERSON_VIEW_REPAIR_HANDOFF_20261002_ZH.md). Project root: `D:\0.Rutgers\CS549\Project-New`. Date: 2 October 2026. Binary owner: `yg745`.

## The two defects

| Defect | Confirmed evidence | Next diagnostic requirement |
| --- | --- | --- |
| Arms outside the frame | User review confirms poor arm framing. Earlier actual-city captures also show reduced arm visibility despite accurate barrel convergence. | Record camera-space hand, elbow and rifle positions and screen projections at matched poses. Identify whether the runtime upper-body rotation, component placement or existing motion causes the cropping. |
| Camera obstructed during movement | User review confirms obstruction while moving. Earlier records mention head or helmet intrusion, but this latest review does not identify the exact occluding mesh. | Capture movement start, sustained movement and stop; identify the obstructing mesh and pose phase before choosing a remedy. Do not assume that every obstruction is the head. |

Neither root cause is established by this handoff. Numerical aiming accuracy does not pass framing, contact or camera-occlusion acceptance. Remaining support-hand separation and generic reload contact limitations must not be presented as resolved merely because this handoff focuses on two visual defects.

## Saved city and preview are different

The active project is `Unreal/ParisStreetCombat/WW2FranceLiberation.uproject`, pinned to UE 5.8.2. The saved map is `/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1`, still on the V3 gun-only attachment and original `ABP_PC_Allied_Stride_v1` for the player and two Allied NPCs. Its recorded SHA-256 is `d00056e8e65d3de6cf7c6af08fe9e52fa4e95e656bfe10a7392c03a82409f51f`.

The reviewed V4 variant exists only as a runtime PIE substitution of the player:

- Animation class: `/Game/ParisCombat/Animation/WeaponAimingV4/ABP_PC_PlayerRigidAimV4`.
- Rifle actor: `/Game/ParisCombat/Blueprints/WeaponAimingV4/BP_PC_PlayerRifleAimV4`.
- Standard `spine_03` LookAt control plus residual rifle convergence; original locomotion graph and local finger poses retained. Reload uses the original single-node action and V3 wrist policy. NPC classes and rifles are not substituted.
- Camera `ParisPlayerCamera`: local location `(25,0,60)`, FOV 90; centered crosshair unchanged.

Closing PIE does not save/select V4. The ordinary game review launcher loads saved V3, not this aiming preview. The other draft `ABP_PC_PlayerAimV4` is an unselected existing-AimOffset comparison with contact defects, not the reviewed fallback.

## Read first and preserve the current workspace

Read `AGENTS.md`, `HANDOFF.md`, then these focused records:

1. [V4 implementation scope](RIFLE_CROSSHAIR_ALIGNMENT_IMPLEMENTATION_V4.md) and [measured result](RIFLE_CROSSHAIR_ALIGNMENT_RESULT_20261002.md).
2. [Current saved city inventory](../../Assets/Integration/CITY_RIFLE_ACTION_DRAFT_INVENTORY_20261002.json), [retained dependency snapshot](../../Assets/Integration/RELOAD_DRAFT_SNAPSHOT_20261002.json) and [unselected aiming inventory](../../Assets/Integration/PLAYER_AIM_TRIAL_INVENTORY_20261002.json).
3. [Gun-only action result](RIFLE_ACTION_ATTACHMENT_RESULT_20261002.md) and `Assets/TEAM_SYNC_WORKFLOW.md` for storage and recovery constraints.

The recorded guard covers 37 retained files plus three aiming drafts, 40 total. The three new packages total 702,473 bytes; their exact paths, sizes and hashes are in the aiming inventory. These inventories preserve local drafts; they are not Catalog-selected teammate restoration authority. Check current bytes before editing, and preserve any newer unique changes instead of overwriting them with old hashes.

Physical writable Content is `Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Content`; the project Content directory aliases those same bytes. Do not create another full asset copy, relocate this workspace or run concurrent lab/game writers. Commercial models and native trial bytes stay outside Git. The working tree contains numerous modified and untracked files from this conversation; inspect `git status` and retain them. Last observed HEAD was `137993ac47ef1b1de0810c30f0e491a7244826b8`; recheck rather than resetting to it.

The earlier human preview was PID 6184. No UnrealEditor process was returned by the handoff turn's process check; this is an observation, not authority to terminate a later user session. Inspect actual processes again before launch.

## Reproduction and evidence

With affected editors closed, run from the project root:

```powershell
& .\Tools\Integration\run_paris_aim_preview.ps1
```

The launcher opens the real city with `ParisEditorBridge` disabled, generates a fresh review identity and substitutes only the live PIE player. Click the PIE viewport; WASD moves, mouse looks, left click fires, R reloads, Esc ends PIE. Do not save the editor map to persist a transient substitution.

Relevant source entry points:

- `Tools/Integration/ue_player_aim_human_preview.py` and `ue_player_aim_runtime_preview.py`: guarded staging and runtime-only selection.
- `Tools/Integration/ue_player_rigid_aim_author.py` and `ue_player_rifle_aim_author.py`: authoring of the reviewed classes.
- `Tools/Integration/ue_paris_combat_pie.py`: optional runtime aiming regression, enabled by `CS549_PLAYER_AIM_PREVIEW=1` with the current V3 checkpoint. Use a new evidence identity and inspect its other environment requirements before execution.

Private evidence root: `Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/CityGameplay20261002/`.

- `Runtime/combat_aim_preview_v2/combat.json`, `hud_initial.png`, `hud_hostile_hit.png`: actual-city regression and captures.
- `RifleCrosshairV4/rigid_live_v1/`: measured fallback poses, including `aim_idle_fit_fp.png` and `aim_idle_fit_front.png`.
- `RifleCrosshairV4/human_preview_v1.json`; launch log `tmp/paris-city-gameplay-20261002/human-aim-preview-20261002-233027.log`: earlier human preview readiness, not acceptance.

## What must be retained

The independent bridge-disabled city regression passed 15 cases and 62 assertions, exit 0, with ammunition conservation, blocked/friendly/invalid firing, guarded reload phase, death/reset and retention of the trial player class. Camera/NPC selections and all 40 guarded bytes were unchanged. This is bounded gameplay evidence, not a visual pass.

The fallback's sampled maximum barrel error was about 0.000100 degrees; sampled support separation still reached 4.82 cm. `rigid_live_v1` exited abnormally during shutdown (`-1073741819`); retain that failure even though the independent city run exited cleanly. Earlier lower-body comparisons used different playback times and do not prove phase-aligned equivalence. Consult the result document rather than rerunning every old prototype or claiming a complete animation pass.

Do not remodel the soldier/arms/rifle, edit original rig or source motions, revive the rejected finger layer, offset the crosshair or replace the WWII rifle. Do not disable gameplay collision or obstruction checks to conceal a view defect. Existing camera settings remain the baseline; any proposed camera/FOV change, separate view representation or owner-only visibility treatment must be explicitly scoped and documented before implementation, with approval sought if it exceeds the existing authorization. Do not simply hide the whole body or select failed aiming drafts as the solution.

NPC AI, follow/patrol, faction interaction, new movement features and shot VFX remain outside this repair. No Blender remodeling, asset acquisition, immutable release, Catalog change, packaging or Git publication follows automatically from this handoff.

## Suggested next work and acceptance

First reproduce both defects in the real city and write a bounded repair implementation document: prerequisites, changed components/nodes/packages, diagnostics, rollback and acceptance. Diagnose at matched motion phases before choosing a remedy. Prefer a small adaptation of existing assets; candidate remedies are not decisions already approved here.

Compare idle, forward/backward/sideways movement, start/stop transitions, normal looking up/down, turning, firing, stationary/moving reload and death/reset. Record view captures and relevant camera-space measurements. Arms and grip should remain readable in the intended framing; no own-character mesh should intermittently obscure the central view during normal movement. Preserve centered barrel/shot agreement and right-hand attachment, and disclose any residual support-hand or reload contact gap.

After a change, rerun affected combat/lifecycle cases and verify unchanged NPC/navigation dependencies; regress navigation if touched. Keep the existing gameplay obstruction behavior. Check engine exit/logs, not only saved reports. Request Yupu's actual-city visual review before choosing the variant for the saved map. A later saved selection needs fresh-load regression and updated local hash inventories; release synchronization is a separate authorized operation.

This handoff does not claim either defect fixed, full motion acceptance, performance/package acceptance or Assignment 3 completion. No native asset edit, new implementation, commit or push is performed in this documentation turn.
