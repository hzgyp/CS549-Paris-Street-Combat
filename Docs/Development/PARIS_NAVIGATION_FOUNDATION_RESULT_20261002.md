# Retained Paris navigation foundation — 2 October

Owner: `yg745`. Governing plan: `PARIS_NAVIGATION_FOUNDATION_IMPLEMENTATION_V1.md`. User boundary: finish navigation only, then pause before decision/Behavior Tree design, follow/patrol and both factions' interaction. All characters, locomotion, weapons and combat/HUD remain the retained asset-first setup.

## Saved navigation

`NavigationFoundation/author_v1` saved a real NavMeshBoundsVolume and Static Recast data in the existing team root `/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1`. No vendor level or gameplay Blueprint was saved. Author log has zero Error/Fatal/ensure matches and normal shutdown. A size/SHA-verified recovery copy of the prior 1,268,792-byte map is preserved in this run's evidence directory; do not restore it over the newer map without an explicit rollback.

- Bounds center (-5542.82, 30, 200) cm, extents (21000, 21000, 500) cm: 420 x 420 m diagnostic navigation window, not a mission boundary or whole-city acceptance.
- Ground survey: 41 x 41 points, 10 m spacing, retained real city collision. Street-height/slope filtering accepted **1,600** candidates; **1,549** projected, **391** had complete paths from the player and **1,157** had partial paths. The remaining projected point is the player-to-self one-point path; projection is not a complete-route success.
- All **six** initial Characters project; all **five** NPC starts have complete player connections. Longest sampled complete path: **352.544 m**; this is path length, not straight-line distance, selected mission or measured traversal time.
- Agent radius **34 cm**, height **193 cm**, slope **45 degrees**, tile **1000 cm**, Static generation. Supported resolution defaults retain cell sizes 38/19/19 cm, cell height 10 cm and step 35 cm. Capsules/actions are not replaced.
- First navigation save: **2,703,371 bytes**, SHA-256 `a4f7e5d637c816f08ec387062b4c9d8270152221d39469f92aa91357d9621c43` (historical after the supported-agent resave below). Six other city/combat/HUD and all earlier 28 drafts plus ten vendor maps stayed unchanged. Current seven-package hash checkpoint: `Assets/Integration/CITY_NAVIGATION_DRAFT_INVENTORY_20261002.json`; the pre-navigation package inventory is historical for this map.

Raw evidence/recovery remain in the single ignored SFTP workspace under `Evidence/CityGameplay20261002/NavigationFoundation/`; logs are ignored in `tmp/paris-navigation-ai-20261002/`. This is an unpublished local draft, not Catalog/restore authority or an immutable release.

## Fresh-load and runtime checks

`fresh_v1` failed the retained agent-settings assertion before movement, with protected native bytes unchanged. Installed UE 5.8 header marks radius/height/slope as configuration properties; engine defaults specify 144 cm height/44-degree slope. The map-only authoring change did not establish reproducible settings. A bounded project `DefaultEngine.ini` Recast section now pins radius 34 cm, height 193 cm and slope 45 degrees, matching the already built map. No engine/vendor/character patch or map rollback; preserve the failed report/log.

`fresh_v2` still rejected settings and measured radius **35 cm**, height **144 cm**, slope **45 degrees**. Recast defaults alone therefore were insufficient; the navigation system's supported-agent configuration remained the mismatch. A single explicit Default supported ground agent now pins 34/193 cm and Recast in project configuration, using installed `NavigationSystem.h`/`NavigationTypes.h` and [Epic's supported-agent API](https://dev.epicgames.com/documentation/unreal-engine/API/Runtime/NavigationSystem/UNavigationSystemV1). Both failed tests left protected native bytes unchanged.

`fresh_v3` restored correct 34/193/45 settings and identical coverage and completed all four native moves, off-mesh rejection and accepted-request cancellation. It nevertheless logged rejection/removal of the older serialized NavDataConfig. Its raw numeric report's pass label is superseded by this log review: regenerated-navigation evidence is **not a clean retained-load pass**. Its zero-displacement cancellation also does not establish in-flight cancellation. Preserve this identity; the correction and accepted fresh result are below.

`supported_agent_resave_v1` completed a normal full-editor/NullRHI navigation rebuild/save under the explicit supported-agent profile. Authoring process exited 0; protected native bytes stayed unchanged, and the identical 1,600/1,549/391/1,157 survey repeated. This does not claim image/animation/deformation acceptance. The prior map and full draft metadata are size/SHA-verified recovery material in this unique evidence directory. Only the team map changed: **2,703,589 bytes**, SHA-256 `4c77844f140b2d6450a13163af9abab4ca13c2d5883186e1aa6970f00f72c620`. The current seven-package inventory totals **3,293,084 bytes**.

### Accepted retained-load/live result

`fresh_v4` passed in a separate rendering-enabled, bridge-disabled normal editor/PIE process: exit 0, no Error/Fatal/ensure matches and **zero navigation registration/replacement warnings**. No bounds spawn, configuration rewrite or explicit RebuildNavigation was performed. Retained 34/193/45 settings and exact coverage summary repeated. All guarded native bytes stayed unchanged. Serial native AIController MoveTo used pathfinding, 30 cm acceptance and **no partial paths or teleport**:

| Retained NPC / trial | Complete path | Game-time arrival | Remaining distance | Native result |
| --- | ---: | ---: | ---: | --- |
| Allied short | 7.170 m | 2.761 s | 25.86 cm | Idle, arrived |
| German short | 12.578 m | 4.597 s | 16.03 cm | Idle, arrived |
| Allied longer | 80.444 m | 27.098 s | 21.41 cm | Idle, arrived |
| German longer | 81.586 m | 27.898 s | 26.49 cm | Idle, arrived |

An off-mesh goal 10 km away on each horizontal axis failed projection and native MoveTo returned Failed with partial paths disabled. Cancellation waited for **55.47 cm actual displacement** and native Moving, then StopMovement produced Idle, zero speed and zero further horizontal displacement over one game second. This is engine movement cancellation, not future BT/perception/reset-generation cancellation.

Conservative fixed-height capsule sweeps flagged 5/10 and 3/7 sampled segments on the longer paths; both actual Characters nevertheless completed those routes. These raw flags are retained, not filtered or called all-clear. Native step/capsule movement is stronger evidence for these traversals than this straight-segment screening, but the diagnostic does not identify the cause or clear every bottleneck/stair/pose. Review exact areas during final route/contact acceptance instead of editing vendor collision or declaring all-city walkability.

`combat_nav_v1` post-navigation combat/HUD regression passed **15 cases / 62 assertions** using the explicit new draft checkpoint. Engine exit 0; report `all_assertions_passed=true` and `native_bytes_unchanged=true`; zero Error/Fatal/ensure/navigation-registration matches. The final HUD/city/rifle image was reviewed. A one-off shell postcheck initially read the nonexistent generic `guarded_bytes_unchanged` field and failed; corrected read-only verification used the actual `native_bytes_unchanged` and `all_assertions_passed` fields and reviewed all 62 assertions. This was a wrapper check error, not a rerun/native fix or an engine test failure. No physical-input, final presentation or FPS pass follows from this regression.

All affected engines are closed. Native work remains unpublished and owned by `yg745`; no Catalog/allowlist change, immutable SFTP release, Git commit/push or new private archive. **Navigation foundation work is complete at this bounded checkpoint; development is paused at the user's requested boundary.**

Final local verification passed all **16,606** selected city/character/motion baseline files by size/SHA-256 and all **35** current/retained draft hashes. Paris Python/JSON and three PowerShell launchers parsed; whitespace checks passed. The map retains shared-account-capable Authenticated Users Modify ACL (no permission/root-ACL change). These are local checks, not remote-byte publication or teammate restoration.

## Limits and stop boundary

Partial/unprojected locations are explicitly unsuitable until separately investigated; do not pick an objective merely because it projects. The measured connected set is a foundation for later route design, not every road/interior/roof being walkable. Collision spot checks and live route success are bounded evidence, not blanket contact, full navigation avoidance/replanning or `NAV-01` acceptance.

No follow/regroup, patrol/search, shared controller/tree, perception, squad coordinator, automatic faction interaction, NPC firing or mission/checkpoint logic is implemented here. Those require the team's combined decision/Behavior Tree and faction-interaction design review before another implementation package. Public package rights, final German weapon, history, full-route/stress FPS and second-machine restoration stay open. The earlier Windows package predates this navigation save; it is not a packaged navigation increment. No new package/archive, Catalog selection, immutable publication, commit or push is implied.
