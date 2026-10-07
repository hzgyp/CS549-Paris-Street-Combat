# Player actions result

3 October 2026. Local native trial, not a selected/published game revision. Implementation: `PLAYER_ACTIONS_IMPLEMENTATION_V1.md`; Chinese review: `PLAYER_ACTIONS_RESULT_20261003_ZH.md`.

4 October human review reports sprint hand/gun separation, proposed back-slung
prone carry/no firing, both factions' NPC index-trigger mismatch and absent visible
recoil. See [latest open issues](GERMAN_RIFLE_UE_AND_ACTION_RESULT_20261004.md#latest-human-feedback--open-issues-4-october).
Not repaired/retested; earlier numeric results do not pass human action review.

## Delivered scope

Reuse existing licensed motion clips, original character/rig/fingers and the Paris city. The current review pair is `BP_PCParisPlayerActionsV6` and `BP_PCActionOwnerViewV1`, not the earlier V1–V5 players. Seven new native Blueprint files are retained in the single SFTP workspace Content home; their identities/SHA/selection status are in `Assets/Integration/PLAYER_ACTIONS_DRAFT_INVENTORY_20261003.json`. No current-map save, default-map change, Catalog/release update, commit or push.

| Input | Capability | Trial configuration |
| --- | --- | --- |
| WASD | Existing directional walk | 150 cm/s, original stride AnimBP |
| Hold Shift | Directional run | 300 cm/s, existing calibrated run samples |
| Hold Alt | Low-speed walk | 65 cm/s; not a dedicated stealth clip or hearing system |
| Space/release | Jump and stop jump request | Existing start/fall/land; grounded admission, native CharacterMovement |
| Ctrl toggle + WASD | Crouch and four-direction movement | Engine crouch half-height 60 cm; 120 cm/s, original clips |
| Z toggle + W/S | Prone and forward/back crawl | Half-height 34 cm; 60 cm/s; padded long-body sweep and ground support checks |
| Left click / R | Existing fire/reload | Standing/grounded/not-running only; reject pending posture/jump requests |

The audit confirms the selected source clips use the existing UE4 mannequin skeleton and no root motion. This is not German-character adaptation acceptance. Runtime input/state/animation/collision runs in standard UE Blueprint nodes, with the Editor bridge disabled. Python only authors, stages and observes tests. Single-node posture playback changes only on clip/state change, not every frame. Returning to standing restores the original stride AnimBP. Jump/posture/run requests cancel the original guarded reload transaction, without editing that transaction or inventing ammunition.

Full body actions and first-person holding are separated. The complete arms follow an invisible native pose driver using the unchanged holding clip while Ready, and the original body reload pose while Reloading. The visible rifle remains the authoritative muzzle. Camera mount/FOV, original models, fingers and clips are unchanged; no IK/finger edits, opacity masks or offset sweeps.

## Actual evidence

Evidence stays private under `Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/` and logs under ignored `tmp/player-actions/`. These are tests in the actual city, with unsaved player/view substitution and temporary collision fixtures, not a new replacement level.

| Run | Result and boundary |
| --- | --- |
| `PlayerActionsV1/audit_v1` | Read-only defaults/clip/skeleton/root-motion audit |
| `author_v7`, `owner_author_v2` | New-only native packages compile/save; no graph errors; originals unchanged |
| `runtime_v8` | Earlier V4 passes 21 functional checks without screenshot freezing; superseded by current safety derivative |
| `runtime_v10` | Current V6: 2,410 observations, 40 phases, all 29 strict functional checks pass; exit 0, no matched runtime error/ensure/Accessed None/infinite-loop lines |
| `CityGameplay20261002/Runtime/actions_combat_v1` | Previous V5/new owner: 16 cases/66 assertions, ammo/reload conservation, lifecycle, friendly obstruction and near-wall muzzle obstruction pass; not the final V6 regression |
| `actions_combat_v2` | Current V6: all 16 cases/66 assertions plus ammo/reload conservation, fresh-load/lifecycle/native guards pass; near-wall blocker is 79 cm from camera; exit 0, no matched runtime error/ensure/Accessed None/infinite-loop lines |

Action coverage includes four-direction run/slow/crouch, jump ascent/descent/landing restoration, prone entry/crawl, low-ceiling standing refusal/recovery, wall-adjacent prone refusal, held-input crawl stopping, same-frame action rejection, early reload cancellation, one reload commit and crouch/prone death/reset. Numerical passes do not establish foot contact or visual transitions. Test-only start resets are not navigation success.

The strengthened wall run stops after 19.42 cm approach; its final four blocked samples have exactly unchanged positions and zero velocity. The assertion bounds every sampled displacement to 35 cm, not merely an early stopped frame. This is one bounded fixture, not whole-city or all-frame-rate prone safety.

Protected original 43 native files, published 206-file playtest bytes and 127 source-animation guards remain unchanged in the clean action run. Canonical map remains SHA `2791b4a7f76b4b3d07f42286b6ad0156c3a185c2e3e795fa2446aaac0ad68519`. New packages are local unselected drafts, not automatic teammate restore authority.

Final post-exit rehash covered 383 unique metadata paths (including aliases), zero mismatches. Preview CheckOnly verifies unchanged published gameplay, city availability/sizes, installed UE5.8.2 CL56702186, all seven drafts, source-animation hashes and author/runtime evidence hashes without opening a game. `check_asset_storage.py --git` verifies17,479 selected manifest records and tracked-source guard, not full local/server rehash. Action Python/JSON parsers and `git diff --check` pass. No Unreal processes remain at this checkpoint. Installed input-event constructors default to parent-binding override; actual keyboard/mouse remains a separate human test.

## Retained failures and limitations

Preserve first author hidden-parameter failure, first observer unavailable-accessor failure, uncalibrated V1, route-wall/prone-toggle setup failures, invalid editor/body captures, generic/protected editor-setting attempts and capture-interference run. The full-body jump owner image initially showed sleeve obstruction; the separate native holding mechanism supersedes that display candidate. One actual `actions_combat_v1/hud_initial.png` PIE viewport image was inspected: ordinary holding is visible without large head/sleeve obstruction. It is not multiview body, moving/reload or human visual acceptance.

**V5/runtime_v9 is safety-rejected despite 29 true tool checks.** Positional review found 49.12 cm approach and ongoing movement while the observer reported blocked/zero velocity. Stopping after CharacterMovement had already integrated was insufficient, and an any-sample assertion falsely passed. V6 admits forward input only after a predictive requested-direction sweep; pending-prone lateral/yaw requests are rejected. The strict current result supersedes, not deletes, that failure.

Open limits: crouch/prone fire/reload disabled; prone forward/back on relatively flat supported ground only, no side/yaw/steep terrain claim; no dedicated first-person run/jump lowering/raising clip or crouch/prone eye-height adaptation. Original camera stays mounted at `(25,0,60)` and FOV90; lowered capsule changes height, but anatomical prone eye height is not accepted. Low-posture gun contact, foot sliding, abrupt single-clip transitions and physical key combinations require human review. Generic M1 reload/contact and missing accepted German rifle remain asset gaps. NPC/German low-posture integration, AI, mission, stress FPS, packaged build and second-machine acceptance are not delivered here. Startup texture/DDC/memory/vendor warnings are retained, not a performance pass.

## Human review and behavior draft

Three current-V6 PIE viewport images (`hud_initial`, `hud_reload_complete`, `continuous_arms_near_wall`) were also opened and inspected. They show readable holding/HUD and the obstruction case, not matched-phase reload motion or body animation. No manual visual acceptance is inferred.

After final functional receipt, run `Tools/Integration/run_player_actions_preview.ps1` (`-CheckOnly` first). Click PIE viewport; controls above. Ctrl/Z toggle back when clearance permits; low poses cannot fire/reload. F8 can eject for external body inspection, Esc ends PIE. **Do not save the staged editor map.** One-time Python setup unregisters at ready; native Blueprint ticks own gameplay. The current published `run_paris_native_preview.ps1` still launches the previous selected version.

Review walk/run/stop, jump/landing, crouch/prone transitions and ground/gun contact, including close walls; then decide selection. No preview was auto-opened for the user by this increment. NPC design is `Docs/Design/NPC_BEHAVIOR_DRAFT_V1.md` / `_ZH.md`; joint behavior review must precede a separate AI implementation plan. Stop here for human visual review, not another polish loop or automatic AI/publication.
