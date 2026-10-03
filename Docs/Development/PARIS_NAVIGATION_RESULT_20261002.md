# Actual Paris navigation — 2 October checkpoint

**Later retained-navigation work and stop override:** see `PARIS_NAVIGATION_FOUNDATION_IMPLEMENTATION_V1.md` and `PARIS_NAVIGATION_FOUNDATION_RESULT_20261002.md`. The user now requires finishing navigation only and then pausing before the joint decision/Behavior Tree and faction-interaction design. The team map has changed since the unsaved trials below: use `CITY_NAVIGATION_DRAFT_INVENTORY_20261002.json` for current draft hashes, not the old package map. Historical unsaved results below remain evidence, not permission to start follow/patrol/AI.

Owner `yg745`. Governing plan: `PARIS_NAVIGATION_AND_AI_IMPLEMENTATION_V1.md`. Existing Paris city, six retained Characters and accepted locomotion remain unchanged. Tests disable ParisEditorBridge and use standard UE navigation, not runtime C++. No shared Behavior Tree, whole-city route, mission, performance, historical/presentation or course pass follows from this checkpoint.

## Unsaved API and coverage results

- `api_v1`: commandlet exit 0, zero errors. No existing bounds/Recast actors. Standard editor volume factory creates a real brush with 100 cm extents; 2/3/4 scale gives 200/300/400 cm actual extents. Six Characters have 34 cm capsule radius; Allied full height 192.47 cm and German 190.53 cm. All 35 drafts/ten vendor maps unchanged.
- `coverage_v1`: preserved failure on protected deprecated scalar `AgentMaxStepHeight` before any native save. Installed UE 5.8 header moves step/cell configuration to per-resolution parameters. No helper/runtime C++ added. Guarded bytes unchanged.
- `coverage_v2`: ordinary full-editor frames and engine RebuildNavigation completed without script errors. Unsaved volume centered (-5542.82, 30, 200) cm with extents (11000, 11000, 500) cm, based on the prior sampled area plus margin. This is not the mission boundary. Recast radius 34 cm / height 193 cm / slope 45 degrees / tile 1000 cm / Static. Three resolution defaults: cells 38/19/19 cm, cell height 10 cm and max step 35 cm.
- Of **403** prior street-height candidates, **384** projected within query extent (100,100,120) cm; **127** had complete paths from the player's projected start. Unprojected/partial/disconnected points are not successes or final objectives. All six starts projected; all **five NPC starts** had complete paths from the player, lengths approximately 3.31–9.34 m. The original report's `six_starts_complete=false` includes a zero-length player-to-self native path (one point, IsValid=false), not a disconnected NPC. Preserve that raw report and interpret it explicitly; subsequent source separates six projections from five NPC paths.

Raw evidence stays in workspace `Evidence/CityGameplay20261002/NavigationAI/`; logs in ignored `tmp/paris-navigation-ai-20261002/`. No map/Blueprint save, extra asset tree, Catalog/allowlist change, immutable release, Git commit/push or automatic restoration. Current map checkpoint remains `CITY_PACKAGE_DRAFT_INVENTORY_20261002.json`. Original city and all earlier drafts are retained.

## Next evidence

`live_move_v1` reached the same editor coverage, then failed before any MoveTo request because its transient-only bounds/NavMesh did not duplicate into PIE. All protected native bytes stayed unchanged. The bounded correction uses an ordinary unsaved team-root trial volume for live PIE, still with no map save. Inspect the fresh `live_move_v2` report before asserting movement success.

`live_move_v2` confirmed that the corrected bounds/Recast duplicated into PIE, then failed before requesting movement on an incorrect Python helper-class name. Installed AIModule header explicitly declares `ScriptName="AIHelperLibrary"`; use that documented Python name. Preserve the failure and unchanged guarded bytes. No native asset/code graph was altered by this correction.

`live_move_v3` recorded **two successful native MoveTo requests and measured arrivals**: Allied 2.756 game seconds / 687.1 cm displacement / 26.8 cm remaining; German 6.163 seconds / 1,478.6 cm displacement / 25.4 cm remaining, native Idle. All protected bytes unchanged. Its log nevertheless contains a handled NavigationSystem CDO ensure. This is numeric movement evidence, **not a clean runtime pass**. The initial cleanup-order hypothesis was tested and rejected by v4 below; do not treat it as confirmed causation.

`live_move_v4` repeated both arrivals (Allied 2.387 s / 688.0 cm, German 6.243 s / 1,481.1 cm), unchanged protected bytes and normal shutdown. Waiting for actual game-world release did **not** remove the CDO ensure. Log timing places it during reflected navigation queries before teardown. Installed header's Within=World generated body requires a non-CDO world context; the Python class-level static-call editor guard is a candidate cause. V5 routes runtime navigation queries through the actual navigation-system object using reflected calls, retaining explicit world/query parameters. Verify the fresh result/log; do not suppress engine ensures or label v3/v4 clean.

## Clean bounded live result

`live_move_v5` completed both native MoveTo trials, normal editor shutdown and **no Error/Fatal/ensure matches**. Runtime query dispatch on the actual navigation-system instance resolves the prior diagnostic CDO ensure in this repeated case, without an engine patch/suppression or runtime bridge. All 35 draft/ten vendor-map hashes remained unchanged. Five initial NPC connections and the 403/384/127 coverage counts repeated. Actual results:

| Retained NPC | Complete path length | Arrival time (game s) | Displacement | Remaining horizontal distance | Native completion |
| --- | ---: | ---: | ---: | ---: | --- |
| Allied | 7.170 m | 2.432 | 6.879 m | 25.98 cm | Idle, arrived |
| German | 18.345 m | 6.183 | 14.787 m | 26.18 cm | Idle, arrived |

Requests used normal AIController, 30 cm acceptance, pathfinding enabled and partial paths disallowed. Position/speed/status traces were sampled over ordinary engine frames. No teleport, manufactured arrival, fixed-step bridge or model/animation replacement. This is a **bounded live navigation pass on an unsaved trial**, not a persisted/fresh-restored NavMesh, shared behavior tree, route/avoidance/stale-event comparison, packaged AI mission, visual contact/deformation or NAV-01/AI-01 completion.

All automated engines are closed. Post-package selected-baseline size/SHA checks passed 16,606 files; current seven/earlier 28 draft hashes remain intact. No native saving/publication, Git staging/commit/push or release authority changes occurred in navigation trials.

Historical next-work suggestion, superseded by the navigation-only stop override above: run bounded ordinary PIE MoveTo, save/fresh-load team-root navigation and later implement individual controllers/shared BT and coordination. The retained-navigation work is now separately recorded; shared AI/waiting/search/death/restore implementation remains paused pending joint design review. Unsaved path queries alone do not complete NAV-01/AI-01. Germans remain unarmed pending the accepted weapon kit; do not imply an armed enemy encounter test.
