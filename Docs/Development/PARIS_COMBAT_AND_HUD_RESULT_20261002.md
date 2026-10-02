# Actual Paris combat/HUD checkpoint — 2 October 2026

Later packaging-entry cleanup and the current map hash are recorded in `PARIS_WINDOWS_PACKAGE_RESULT_20261002.md` and `CITY_PACKAGE_DRAFT_INVENTORY_20261002.json`. This report's seven-file S2 inventory remains historical hash evidence for the pre-cleanup map, not current restoration authority. The six Blueprint/widget files and combat logic are unchanged by that cleanup.

Post-cleanup `combat_pie_v8` repeated the 15 cases / 62 assertions with bridge disabled: all passed, ammo/reload conserved, guarded bytes unchanged, initial/reload/final HUD captures reviewed. The later private package startup also ran at verified 1920x1080. These outcomes supersede pending post-cleanup regression, not full AI/mission/performance/presentation acceptance.

Owner `yg745`. Governing documents: `ASSIGNMENT3_IMPLEMENTATION_V2.md`, `PARIS_CITY_GAMEPLAY_IMPLEMENTATION_V1.md` and `PARIS_COMBAT_AND_HUD_IMPLEMENTATION_V1.md`. This increment uses the accepted existing city/characters/motions and provisional M1 appearance; the withdrawn standalone laboratory was not recreated. It is **not M0/M1/MVP/course completion**.

## Saved native increment and storage

Current seven packages total **1,882,258 bytes**; exact hashes are `Assets/Integration/CITY_COMBAT_DRAFT_INVENTORY_20261002.json`. One writable physical home remains `Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Content`; active project Content aliases it. Packages comprise the team Paris entry, player/Allied/German children, unchanged GameMode, new common shot Blueprint and standard UMG widget. The five-file S1 inventory is historical after four files changed; do not restore it over this increment.

The new common combatant inherits the retained guarded lifecycle/reload logic. Only the three city children were reparented; Allied/German meshes, calibrated AnimBPs, German capsule/mesh offsets, teams, roles, possession and the 25/0/60 cm player camera remain. Six capsules block Visibility; three existing Allied M1 actors are per-instance appearance references. Germans remain unarmed and cannot fire without a weapon reference. Left mouse calls camera-intent/physical-muzzle Fire; R calls the existing reload. Global default maps remain the original vendor entry pending physical input/usability review.

Gameplay remains Blueprint. UMG-template authoring needed a documented tiny **Editor-only**, disabled-default bridge v22 helper because WidgetTree is protected from installed Python. It creates standard Canvas/TextBlock templates in new unsaved widgets only. K2 HUD reads authoritative health/ammo/action/shot state; generated runtime classes/functions do not call the bridge. Bridge-disabled PIE successfully loads and runs the new content. No C++ gameplay class or abandoned W1 helper was introduced. The earlier v21-restoration cleanup record remains a historical checkpoint, not the current helper deployment.

All native files remain ignored, unpublished workspace drafts, alongside the preserved earlier 28. No new immutable release, Catalog/allowlist change, Git stage/commit/push, asset duplication/relocation or vendor resave occurred. Current inventory is not automatic restore authority or a proven minimal cooking closure.

End-of-test selected-baseline local size/SHA verification passed **16,606 files** (city 15,850, character 721, selected motions 35), with Git storage checks. Current seven package sizes/hashes, 17 integration-script syntax trees, review-launcher syntax and `git diff --check` passed; native paths remain ignored. All automated engine processes exited before the interactive human review.

## Actual results

Raw ignored evidence: workspace `Evidence/CityGameplay20261002/Setup` and `Runtime`; logs in `tmp/paris-city-gameplay-20261002`.

`combat_pie_v6` completed **11** actual-city request cases with all recorded assertions passed, ordinary reload/UMG and guarded native bytes unchanged; engine exit 0. This uses the normal full-editor PIE frame loop, six retained Characters and existing city collision, not a blank test map, fixed-step bridge diagnostic or physical input injection.

| Check | Observed result |
| --- | --- |
| Hostile shots | Health **100→65→30→0**, one loaded round and sequence increment per accepted shot; death state entered |
| Same-frame duplicate/cooldown | Rejected; no additional round, sequence or damage |
| Ally between player and enemy | Friendly blocked; spends one accepted round, neither ally nor enemy damaged |
| Existing road/world obstruction | World blocked; no enemy/friendly damage |
| Barrel swept across existing road | Barrel blocked despite camera seeing enemy; no damage |
| Empty / Reloading / dead player | Rejected; ammo/sequence/damage unchanged |
| Zero aim direction | Rejected without consumption |
| Lifecycle reset/new generation | Same-frame new-life request clears stale cooldown and safely applies the clamped final damage |
| Ordinary reload after two shots | **0/16→8/8**, one animation-phase commit; Ready restored |
| Authoritative HUD | Initial `HP 100 AMMO 2/16 Ready`; final `HP 100 AMMO 4/8 Ready`, sequence 6, last rejected request |

Four `Shot SHOWUI` viewport PNGs were reviewed: existing city, retained soldiers/rifle, centered aim mark and readable bottom-left authoritative status. HighResShot scene-only output omits UI and is not HUD-visibility evidence. The screenshot named `hud_hostile_hit` shows the immediately subsequent cooldown rejection; actual hostile damage is proven by the case state, not that label alone. Cosmetic hand contact and weapon-specific FP/reload remain unaccepted and deferred.

`combat_pie_v7` completed **15 cases / 62 case assertions**, all passed, with no Python errors, engine Error/Fatal/ensure lines and normal exit 0. It independently repeats v6 and adds rejection while **Reloading with eight loaded rounds already committed**, NaN/Inf input rejection, missing-German-weapon rejection and aggregate conservation. Initial total ammo 18 equals final loaded/reserve **4/8** plus **six** accepted rounds; one reload commit, no manufactured ammo. Target is actually Health 0 / IsDead true / ActionState Dead. Native bytes remained unchanged; all four new SHOWUI PNGs were reviewed. This is bounded combat/HUD evidence, not fifteen completed missions or physical input.

## Defects corrected and preserved evidence

- HUD v1/v2 stopped on protected WidgetTree; v3 stopped on an unavailable numeric-conversion function. Only the new shared package was saved. Bounded Editor helper and installed `FTrunc` resolved those API gaps.
- V4 saved the widget, then stopped before child writes on enum naming. V5 confirmed a struct shadows the enum; read-only inspection established `CollisionResponseType.ECR_BLOCK`. V6 completed guarded child/input/map saves, retaining successful partial bytes rather than overwriting them.
- Combat PIE v1/v2/v3 stopped on UMG wrapper naming, editor class-loading prohibition in active PIE, and non-instance-editable ammo respectively. V1's abnormal shutdown code is retained; v2/v3 exited 0. None passed combat. Subsequent tests use ordinary Blueprint requests, not relaxed mutation protection.
- Combat PIE v4 failed hit/obstruction classification. Exact-contact muzzle endpoints missed; a 2 cm extension avoids surface-termination loss while retaining first blockers. V5's matched Python original/extended queries confirmed this defect but Blueprint still failed.
- Saved graph audit found automatic arithmetic promotion had erased disconnected scalar operands: intended vector-times-distance became vector-times-vector with empty B inputs, yielding zero-length intent rays. Scalar fix v1 stopped unsaved on an invalid title expectation. V2 wires explicit uniform `(s,s,s)` scale vectors (mathematically scalar multiplication) for 20000 cm, 0.1 cm and 2 cm. Other 34 drafts stayed unchanged. V6 verified the corrected runtime behavior.
- V5's below-road barrel fixture did not cross the road in the intended direction. V6 starts above the real road and points down; actual Python sweep and Blueprint Barrel blocked result agree. Failed evidence was not deleted or relabeled as passed.

## Human review and following work

On 2 October, after the interactive review launch, Yupu reported that he tried it and found no problems. Record the bounded physical-input/provisional-view/HUD usability review as **Pass (user report)**, not a measured instrumented test of every control or final weapon-specific presentation. No precise duration/FPS or additional scenarios were supplied. `Tools/Integration/run_paris_review.ps1` opens this same asset-backed map with the bridge disabled; it does not author/save native content or establish packaged/FPS acceptance. No engine process remained at the following work-package preflight.

Interactive review launch was issued at 15:50 local time, PID 30236, log `tmp/paris-city-gameplay-20261002/human-review-20261002-155017.log`. The log confirms the intended GameMode/world came up for play and loaded in 48.92 seconds. It also records a vendor showcase `BP_Category_Platform` compiler error about Editor Subsystems: the world continued loading, but this is an unresolved standalone/cooking dependency defect, not a clean standalone pass. Trace its dependency/Editor-only exclusion in the early packaging work package before changing any preserved vendor package. The later user report clears bounded usability only; standalone and packaged acceptance are not inferred from launch.

Following the user review: execute `PARIS_WINDOWS_PACKAGE_IMPLEMENTATION_V1.md`, then NavMesh/MoveTo, separate NPC controllers/shared BT/perception, distinct squad destinations, finite objectives and mission retry/restart. No mission route has been selected from a complete navigation/travel-time survey yet. Weapon-specific presentation/history, German rifle, final dependencies/public bundled-build rights, performance/stress/second machine and Assignment 3 deliverables remain open.
