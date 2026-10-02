# Asset-backed Paris gameplay checkpoint — 2 October 2026

Owner: Yupu (`yg745`). Follow `PARIS_CITY_GAMEPLAY_IMPLEMENTATION_V1.md` under the corrected Assignment 3 V2 plan. This is an integration checkpoint, **not M0/M1/MVP/course completion**. The removed standalone W1 route was not recreated.

## Verified foundation and saved increment

Main `3ecd7bb` was fetched with zero divergence; prior document edits were preserved. Targeted local size/SHA-256 verification passed **16,606** selected city/character/motion files (15,850 + 721 + 35). The 28 retained unpublished drafts remained unchanged. Metadata-only `Tools/check_asset_storage.py --git` also passed; it does not verify all remote bytes.

Saved **five new native packages / 1,449,626 bytes** in the sole writable `paris-gameplay-v1/Content` workspace: a team city entry, player, Allied NPC, German NPC and GameMode. Exact current hashes are in `Assets/Integration/CITY_GAMEPLAY_DRAFT_INVENTORY_20261002.json`, not active Catalog/restore authority. No new immutable release, allowlist expansion, Git stage/commit/push or vendor asset upload occurred.

The entry is an editor Save As of the vendor root World, not a second city geometry/texture tree. Eight original child levels are referenced: Day, VFX, StructureAsset, SetDressing, Proxy, SplineRoads, NewsetDressing and Powerline. Midnight/WarFog references were removed only from the team entry. Original city maps and all earlier 28 drafts stayed unchanged. Global default maps still name the original city pending playable-view verification.

Six Characters are staged on independently traced road surfaces: one Allied player, two allies and three Germans. Retained meshes, stride AnimBPs and guarded lifecycle/reload logic are reused. The player has one capsule-attached camera (25 cm forward, 60 cm up, FOV 90, controller rotation). Three existing M1 appearance meshes attach to Allied `hand_r`; new instances are Movable/NoCollision, not edits to the source rifle. Germans remain unarmed; neither side has accepted weapon-specific first-person/reload presentation.

The new player graph compiled/saved four legacy compatibility axis events and R reload using the installed BlueprintGraphEditor API. Existing EnhancedInput player/component classes are retained. Requests call existing movement/look/guarded-reload functions. No fake diagnostic Fire is bound. No new editor C++ or runtime plugin dependency was introduced.

## Actual evidence and limitations

Raw evidence is ignored under the workspace `Evidence/CityGameplay20261002/`; logs under `tmp/paris-city-gameplay-20261002/`.

| Check | Actual result | Does not establish |
| --- | --- | --- |
| `Survey/structure_v3.json` | Read-only inventory/queries: 8,316 actors, 441 samples, 234 clear adjacent sampled capsule segments | Whole-city navigability, NavMesh, mission or travel time |
| `Setup/author_v4.json` | Six Characters/three rifles saved; original ten maps and earlier 28 drafts unchanged | Runtime/input, FP grip, combat, AI or mission |
| `Setup/input_v1.json` | Five K2 bindings compiled/saved; other four setup files/earlier drafts unchanged | Physical keyboard/mouse |
| `Setup/reopen_v2.json` | Bridge-disabled actual nine-level fresh load, six Characters, teams, camera and attachments passed | Runtime/package acceptance |
| `Setup/reopen_v3.json` | Above plus current input graph fresh load; guarded bytes unchanged | Runtime/package acceptance |
| `Survey/views_v2/capture.json` | Six real-city PNGs generated/reviewed; map hash unchanged | FPS, gameplay exposure, accepted camera/weapon presentation |
| `Runtime/pie_v5/pie.json` | Correct possessed player/six Characters/three rifles; forward movement, braking, look and single guarded reload worked; all guarded native bytes unchanged; normal exit | Physical keyboard/mouse, precise contact, combat/AI/mission, FPS or packaged acceptance |

Overhead views show the existing dense multi-block city, connected streets and ruins, not a final mission boundary. Static commandlet views are dark and show problematic framing; they were superseded for player appearance by actual PIE evidence, not deleted. The **actual game viewport** `Runtime/pie_v5/idle_game_viewport.png` has normal daylight exposure and a visible provisional M1. Matched SceneCapture remains darker than the game viewport and is not exposure authority. The saved 25 cm-forward camera has a clear idle view; keep it unchanged rather than saving the tested 45 cm variant, which moves the weapon further offscreen. Visible finger/grip mismatch remains deferred under the approved simplified diagnostic presentation, not final FP-kit acceptance.

Actual PIE numeric evidence: 1.514 game seconds of forward requests moved approximately **427.3 cm**, followed by zero velocity after braking. The look request changed yaw from 0 to 25 degrees (legacy input scale). Reload changed Ready → Reloading → Ready, loaded/reserve **2/16 → 8/10**, with **one** commit and total ammo conserved at 18. This is one actual-city smoke case, not a repeat of the previous exhaustive interruption/stale-event regression or a physical R-key test. All five runtime images were viewed; all engine processes exited.

## Preserved failures and bounded corrections

- Structure v1/v2 failed Python reflection assumptions before native saves; v3 uses installed APIs.
- First original-city capture stopped during cold Nanite/mesh cache processing. Its incomplete report is preserved. Concurrent read-only capture/new-package writer caused RAM pressure; subsequent engine processes run serially.
- Author v1 rejected an invalid sixth road placement before writes. V2 saved four Blueprints, then generic World duplication stalled in pending cache processing; their exact partial hashes were preserved, not vendor rewrites.
- V3 recovered task-owned files, reparented only new Allied/player children to remove inherited diagnostic camera/input dependencies, and completed supported root Save As. Unsaved rifle attachment then failed on Static mobility. V4 hash-verified the five saved v3 files, fixed only new instance mobility and saved the roster.
- Reopen v1 failed an overly narrow eight-level assertion. V2/v3 correctly preserve/check the actual nine-level set including empty vendor SetDressing rather than deleting it.
- Actual-city PIE v1 reached the correct GameMode/world but failed a Python `PlayerController.get_pawn` name assumption before sampling. It ended PIE/exited with guarded native bytes unchanged. The corrected v2 uses GameplayStatics pawn lookup; no PIE pass is yet inferred. Offscreen editor viewport-override ensures in v1 logs are preserved and require review.
- PIE v2 verified possession of the correct player, six team Characters and three owned rifles, then failed the Python glue lookup for BlueprintInternalUseOnly deferred-spawn UFUNCTIONs. It ended/exited with hashes unchanged. V3 uses installed UFUNCTION reflection, removes the unnecessary realtime-override call that caused the v1 ensures, and adds actual viewport/unsaved camera-variant comparison. This correction is not a new runtime bridge or native asset change.
- PIE v3 sampled the possessed player (Ready, health 100, ammo 2/16) but the installed ExecutePythonScript runner auto-exited before warmup. Preserve it as incomplete; five current packages and 28 old drafts independently rehashed unchanged. V4 explicitly sets the installed EditorPythonScripting keep-alive flag for its bounded asynchronous loop; completion/failure still ends PIE and quits the editor.
- PIE v4 was stopped during reentrant FunctionalTesting screenshot preparation, not a native/gameplay pass. All 33 draft hashes independently remained unchanged. V5 adds a callback reentrancy guard, requests the ordinary game-viewport screenshot without FunctionalTesting's editor-work flush, and schedules movement/reload/capture phases by actual game time (separate bounded wall timeout).

## Remaining work

S1's actual-city smoke evidence was reviewed; keep the saved camera and defer grip polish. S2 proceeds under `PARIS_COMBAT_AND_HUD_IMPLEMENTATION_V1.md`. It saved the common shot Blueprint, authoritative UMG widget, three reparented city children and changed entry; current seven-package hashes are `Assets/Integration/CITY_COMBAT_DRAFT_INVENTORY_20261002.json`. The five-file S1 inventory above is now historical evidence, not current restore authority. S2 adds a documented Editor-only UMG-template helper for a demonstrated protected-Python-property gap; normal runtime graphs still require bridge-disabled tests. Its runtime result is separate, not implied by saving.

Physical input acceptance, NavMesh/MoveTo, individual NPC BT/controllers and squad roles, survey-selected finite objectives/restart/checkpoint rules, early city packaging, performance/stress/second-machine and Assignment 3 deliverables remain open. Historical/weapon gaps and public bundled-build rights require their recorded human gates; private team sharing is not public distribution permission.
