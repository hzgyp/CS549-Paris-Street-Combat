# Player actions implementation

3 October 2026. Authorized scope: connect existing character actions, then prepare an NPC behavior draft. This is a local unpublished increment, not permission to implement AI, publish assets, commit, or push. The existing Paris map, characters and native first person presentation remain the foundation.

## Failure review and different approach

Read `Failures/README.md`, FP001 `FAILURE_ANALYSIS.md`, `WEAPON_PRESENTATION_AND_PLAYER_ACTIONS_V1.md`, and `CONTINUOUS_ARMS_NATIVE_IMPLEMENTATION_V1.md`. FP001 proves that numerical gun alignment and unchanged source hashes cannot establish visual acceptance. Rejected finger edits, rigid offset sampling and forearm masks will not be reused. This attempt changes input, movement configuration and selection of existing full body clips, not models, bones, fingers, camera placement, the original animation files or ammunition transactions. Runtime logic must be native engine Blueprint nodes; Python is authoring/testing only.

## Action scope and order

| Action | Existing content | Proposed input and bounded implementation |
| --- | --- | --- |
| Walk and run | Existing directional stride blendspace and rifle run clips | WASD; hold Shift for higher CharacterMovement speed, preserve existing stride calibration |
| Slow walk | Rifle walk clips; no dedicated stealth clip confirmed | Hold Alt; reduce speed, no stealth/hearing gameplay claim |
| Jump | Platformer start, fall and land clips | Space; grounded jump, engine falling state, no NPC jump route implementation |
| Crouch | Crouch idle and forward/backward loops | Ctrl toggle; engine crouch and blocked standing clearance |
| Prone | Prone idle and forward/backward loops | Z toggle; reduced capsule plus elongated body clearance checks, no capsule-only acceptance |
| Fire, reload and death | Current verified transactions and clips | Preserve existing logic; cancel reload before incompatible posture/jump changes and reject inappropriate action requests |

Read-only native audit first: record clip duration, skeleton, root motion, blendspace samples, Character defaults and inherited graph interfaces. Walk/run/slow actions can use the existing animation Blueprint. Separate pose loops may use engine single-node playback with restoration of the original stride class when returning to standing. Do not restart playback every frame; update only on state/clip change. If smooth transition/jump timing cannot be safely implemented using this bounded route, record the failed mechanism and use a separate animation graph rather than modifying source clips.

Run/slow speeds are provisional and will be selected against existing blendspace samples. Crouch and prone are player capabilities and reusable action interfaces, not automatic AI policies. Lateral prone may use bounded turning/forward movement rather than falsely claiming a dedicated strafe clip.

The installed authoring source establishes walk samples at 150 cm/s and run samples at 300 cm/s, not 600 cm/s. The retained new candidate therefore uses walk 150, run 300, slow 65, crouch 120 and prone 60 cm/s; it does not stretch the calibrated blendspace. Additional existing crouch left/right loops were found and are included. Prone yaw/side input is deliberately rejected pending compatible turn/side content and safe body sweeps. Standing-only firing/reload remains a trial restriction until low-posture contact is reviewed. Jump velocity is provisionally 360 cm/s; ground contact/visuals are tested separately.

The first author attempt failed on a hidden native crouch parameter; no asset was saved. The first saved derivative had uncalibrated speeds and is retained unselected, not published. Later derivatives have new identities. The first runtime observer used an unavailable Python accessor and failed before action assertions; its log is retained. These are tooling/candidate failures, not successful action tests.

### Full body and owner holding separation

The fresh runtime test observed working walk/run/jump/crouch and guarded cancellation, but mixed setup failures: the continuous route hit a wall, prone entry was legitimately refused, and the following toggle sequence incorrectly assumed entry succeeded. The body camera used an editor-world reference and its captures are invalid body-pose evidence. A frozen jump owner image shows sleeve obstruction; this candidate is not selected.

Before another trial, use a separately named owner-display derivative under PlayerActionsV1. Reuse the unchanged original holding clip on an invisible native pose driver and the existing rifle attachment class. Full body actions remain on the player mesh; the visible complete-arm mesh follows the owner holding driver while Ready, and follows the original body reload pose while Reloading. Keep original native view framing, camera and gun transactions, bind the visible muzzle as before, and preserve all original display/player/model packages. This is existing-pose selection, not bone/finger/IK or mesh editing. The runtime uses standard Blueprint nodes only. Add native tick prerequisites, retain driver/gun references, and clean them on EndPlay. Early check: source owner idle/reload poses, framing and gameplay regressions still agree; stop selection if obscured or ammo/obstruction regresses. Human dynamic review remains required.

The next test resets input-case starts explicitly, records actual posture entry rather than assuming toggles succeeded, uses a PIE-world body camera and measures representative head/hand/foot envelopes. Collision fixtures remain test-only in the real city and cannot establish city-wide prone clearance or nav acceptance. New trial map selection is deferred until runtime and internal view checks; Catalog/released map stay unchanged.

## Packages and storage

Final safety derivative adds native StopJumping on key release, and rejects firing/reload while a posture request or jump request is pending, not merely after the capsule changes. This closes same-frame action races without changing the original gun transactions. Use a new V5 identity; keep V1-V4 unselected. Functional acceptance runs do not pause/freeze/camera-switch for screenshots: capture interference is a harness failure, not a substitute for a clean run. Presentation inspection is a separate human gate.

Human review uses `run_player_actions_preview.ps1`: hash-check the published foundation and local drafts, stage the separate player/view in the unsaved real-city editor world, begin PIE, then unregister the one-time startup observer. Gameplay remains native Blueprint; the preview performs no animated Python updates, fixture spawning or map save. Do not save the staged editor map. The published `-game` launcher and Catalog remain the previous version until review and separate selection/publication.

New native packages use `/Game/ParisCombat/Blueprints/PlayerActionsV1/` and, only if needed, `/Game/ParisCombat/Animation/PlayerActionsV1/`. Native bytes stay in the single SFTP workspace Content home; source, reports and SHA inventories stay in Git. Never overwrite the published 206-file playtest release or Catalog. Keep the current city map and all 43 retained packages unchanged during authoring and runtime substitution tests. New player selection/map save requires bounded tests and visual review; a launcher may substitute the new class in PIE without saving the map. No commercial bytes or screenshots go into Git.

Implementation sequence: audit; author new player/action controller; compile and save only new packages; fresh-load in actual city with editor bridge disabled; test input/action combinations and gunplay/lifecycle; inspect body/first person views; document results and gaps; prepare the behavior draft. Preserve every failed identity rather than reusing its output path.

## Acceptance and stopping conditions

Adversarial review of runtime_v9 overrides its 29 true tool assertions: after reporting blocked/zero velocity, prone advanced to 49.12 cm toward a wall because the player actor stopped movement after the movement component had already integrated this frame. Its any-sample stopping assertion was inadequate; this is a real safety failure, not visual polish. New V6 intercepts forward input before AddMovementInput, records the requested prone axis for the predictive sweep, rejects pending-prone lateral/yaw input and keeps the previous packages untouched. Strengthen the wall check to bound every position and require stable final blocked positions. Early check: no motion through the padded body envelope under repeated held input; stop/unselect prone if it still advances. Re-run movement and gunplay with new identities before preview.

Early check: new classes compile, fresh-load without runtime bridge calls, and original source/published map hashes match. Stop native authoring if an unexpected package becomes dirty, existing source identity changes, a user-owned engine is open, or the runtime needs Python/bridge callbacks.

Tests must cover standing idle/forward/back/side run and slow walk; grounded/airborne jump and landing; crouch/prone entry, movement and blocked standing; body clearance around walls and low spaces; reload interruption before/after commit; no stale event ammo; death in each posture and restoration of standing movement; repeated requests; controller/display compatibility. Gameplay regression remains separate from pose/contact visual review. Record actual measured results only, inspect multiview evidence and explicitly mark untested human input or visual gates.

If prone cannot pass elongated-body obstruction or support contact, do not ship an unsafe pose disguised as completed prone; leave it unselected and report the runtime gap. If a first person action causes camera blockage or unacceptable rifle/hand separation, stop that selection and request human review. NPC behavior drafting can continue independently with those capabilities marked unavailable. No polishing loop or new character production is authorized.

Rollback means leave the published map/release untouched and stop using the separately named trial. Never restore old hashes over unique newer work.
