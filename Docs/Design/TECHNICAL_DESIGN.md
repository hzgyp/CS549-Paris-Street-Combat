# Technical design - Paris Street Combat

**Latest scope correction:** use the current proposal's connected city mission with an initial configurable six-soldier roster, not a final population cap. Automatic ally follow/regroup, temporary support positions and the map-survey requirements remain. All NPCs share an AIController/Behavior Tree with individual team, role, encounter-group, patrol-route and search-zone settings and private per-NPC Blackboard state. Extra finite groups/stages depend on pacing, navigation and performance evaluation.

**Current mission contract, 23 September 2026:** the revised [proposal](../Proposal/PROJECT_PROPOSAL.md) governs the four pillars, shared A* graph and staged Reach rally A → Clear assigned group B → Reach end C mission. Reach checks only the living player and re-evaluates overlap on activation. ClearArea requires a nonempty fully registered EnemyGroupID with zero living members; unique death events update an actor-ID ledger, including earlier kills. Leaving a volume, despawning or unloading does not count as death. Only the current stage advances, once; player-death failure takes precedence. Full restart restores the configured roster, objective index, counters and timers and rejects stale callbacks. Earlier casualties persist across stages. Objective markers are not checkpoint saves.

This design follows the current four-pillar proposal. It is not evidence that any system has been implemented or validated.

## 1. Boundaries

The asset pack supplies the city geometry, materials and vendor utilities. Unreal supplies rendering, animation runtime, scene queries, navigation primitives and packaging. The team implements the four proposal pillars: animation state/event rules, collision and authoritative hit resolution, student A* route selection, and shared Behavior Tree/perception behavior. Rendering and physical simulation support presentation and runtime operation but are not primary authored pillars.

The active environment is Unreal/ParisStreetCombat/WW2FranceLiberation.uproject. Keep the vendor `/Game/WW2City` namespace unchanged. Future team content belongs in `/Game/ParisCombat/{Maps,Blueprints,Animation,Materials,VFX,UI,Tests}`. Use a team-owned encounter map or editor-aware duplication/migration when development resumes; do not rename binary package files in Explorer.

## 2. Proposed components

| Component | Owns | Must not own |
|---|---|---|
| Player controller / Enhanced Input | Move/look/aim/fire/reload commands, pause | Damage decisions hidden in UI or animation |
| Player character | Movement capsule, camera, weapon/hand attachment | Global mission completion |
| Weapon component | Ammo, accepted-shot cadence, reload transaction, authoritative shot result | Per-effect damage decisions |
| Animation Blueprint / action coordinator | Locomotion blending, action transitions, guarded notify dispatch, grip alignment | Independent authoritative ammo counter |
| Impact feedback component | Surface lookup, position/orientation, bounded decals/particles/audio | Hit detection or repeated damage |
| Health component | Damage acceptance and one death transition | Per-frame repeated objective updates |
| Shared NPC controller / Behavior Tree | Faction/role decisions, patrol, sight memory, bounded search, follow/regroup and route requests | Runtime LLM, private global mission state or unbounded squad tactics |
| Tactical route service | Surveyed graph, A* search, NavMesh path-length costs, reservations and bounded replanning | Combat damage, animation state or arbitrary citywide simulation |
| Mission controller | Roster/group registration, ordered Reach/Clear/Reach stages, win/fail and full-restart generation | Shader or bone manipulation |
| Debug/evidence view | Traces, action IDs, route costs/expansions, AI state, group counters and baseline selection | Shipping gameplay dependencies |

Use Blueprint interfaces for damage/target interaction and explicit event payloads for shot feedback. Data assets/tables may hold weapon tuning, surface mappings and encounter placements. Do not let every actor independently trace and decide the outcome of one shot.

## 3. Shot contract and collision pillar

Baseline shooting is hitscan. Cosmetic tracers do not determine damage; penetration, ricochet and physical bullet ballistics are out of scope.

Proposed sequence:

1. Reject input when dead, reloading, out of ammunition or inside the fire-rate interval.
2. Trace from the camera along the aiming direction to a fixed range to determine the intended aim point.
3. Trace from the muzzle to that point using the documented weapon obstruction channel, ignoring only the shooter's own permitted components.
4. Use the first physical muzzle-path hit as the authoritative hit, even if the camera sees an enemy beyond a corner.
5. Consume one round for an accepted discharge, assign one shot ID, apply damage once if appropriate, and dispatch one feedback event.
6. Visual feedback uses the authoritative hit position, normal and Physical Material. A miss cannot generate a hit effect or damage.

For a muzzle already inside a wall, line traces alone may be insufficient. Define a bounded muzzle-clearance check/weapon pose policy and validate it during Gate 3 rather than ignoring the containing geometry. The accepted-discharge versus blocked-action ammunition policy must remain consistent with animation and UI.

Suggested payload: shot ID, shooter, muzzle origin, camera aim point, hit actor/component, hit position/normal, surface type, and damage category. Damage is independent of rendering quality settings.

Define separate movement, weapon obstruction and perception policies. Decide explicitly whether glass, railings, vehicle shells and foliage block each policy. Decorative debris may be visually present without blocking the movement capsule; shootable cover must agree with its visible silhouette. An invisible player capsule should not unintentionally shield all visible enemy body regions.

Comparison: camera-only trace versus two-stage trace at identical positions. Cases include near wall, corner exposure, muzzle inside cover, window/frame, target behind solid cover and unobstructed target. Record expected/actual hits, false damage/blocking and repeated results at fixed frame-rate settings. These are scheduled tests.

## 4. Action contract and animation pillar

Acquire a compatible weapon/rig/action set before fine tuning. Separate first-person arms from third-person enemy representation when that reduces integration cost. Purchased animation clips are dependencies; state rules and event correctness are team work.

Proposed states: Ready, Aiming, Firing, Reloading, Dead; locomotion is a separate blended layer. Specify legal interruptions rather than allowing each input to play a montage independently.

A reload receives a unique transaction/action ID. A defined animation event commits ammunition exactly once. Cancellation before that event leaves ammunition unchanged; cancellation after commit does not reapply or refund it. Death cancels actions and timers. A stale notify from an earlier action or restart generation must be ignored. A timeout may safely cancel a stuck action and record an error; it must not silently manufacture an ammunition commit.

Start with one simple ammunition model appropriate to the selected weapon. Do not promise generic magazine handling before the actual historical weapon and action assets are chosen. Weapon-specific clips, sockets and moving parts are checked during asset compatibility work.

Comparison: a timer-only reference versus guarded animation-event synchronization under different playback rates and interruption points. Evidence includes duplicate/missing commits, state trace, event timing and observed hand/weapon attachment. Visual polish cannot substitute for correct action state.

## 5. Supporting rendering and impact feedback

Use a surface-to-feedback mapping for a small set of surfaces in the selected street, such as masonry, metal and wood. Start with existing permitted VFX/decal resources and implement team-owned selection, orientation, lifetime, count limits and parameter control. Do not claim to author the environment pack's master materials, Lumen or Nanite.

Impact effects must use the collision hit result. Surface normal drives orientation; decals should not spread across unrelated silhouettes. Effects have an explicit active-count cap and lifetime; clear or recycle them during restart. Decide limits from measurements rather than arbitrary ultra settings.

Use a fixed light/time preset for comparable evidence. Vendor wetness, snow, vehicles and filmic options do not become production requirements because they are available. If the vendor already supplies an identical feedback mechanism, document it and obtain instructor alignment on the bounded team extension rather than presenting it as original work.

Supporting validation may compare generic and surface-aware bounded feedback on the same camera path and shot sequence. Record GPU/CPU frame times, active effects and visual differences when useful, but do not present this as a primary pillar comparison. Profile city streaming, shadows, ray tracing and effects separately; storage size does not predict VRAM residency.

## 6. Pathfinding and Navigation pillar

Survey the selected connected mission area before authoring its tactical graph. Record junctions, walkable connections, NavMesh coverage, path lengths, bottlenecks, collision, sightlines and representative travel times. Graph size and route length come from this survey rather than a preset node or block count.

Implement student A* over the surveyed junction graph. Use NavMesh path length for edge cost where available and an admissible Euclidean-distance heuristic. Unreal NavMesh and `MoveTo` execute each selected graph leg; they do not replace the student route-selection layer. If a required leg is not navigable, reject it or invoke a bounded replan rather than teleporting or silently marking it complete.

Allies reserve distinct temporary support destinations and release reservations on arrival, failure, death or restart. Bounded wait/replan behavior handles bottlenecks; it must not create an infinite retry loop. The route service records request ID, start/goal, selected nodes, total cost, expansions, execution failures and fallback reason.

Comparison: run A* and Dijkstra on the same surveyed start/goal pairs. Verify equal optimal costs where a path exists, then compare node expansions and elapsed search time. Exercise blocked legs, unreachable destinations and ally bottlenecks. These are planned tests, not current results.

## 7. NPC AI / Behavior Trees pillar

All combat NPCs share an `AIController` and Behavior Tree. Per-NPC data identifies faction/team, role, encounter group, patrol route and search zone; each controller owns private Blackboard state. Do not store individual target memory in shared global variables.

Living allies follow/regroup around the player, request distinct reachable support positions during contact, and obey the same obstruction and damage rules as other combatants. German NPCs guard or patrol their configured routes, acquire valid opposing targets through AI Perception, and search a bounded set of reachable authored points near the last observed target position. Sight memory expires; search ends or returns the NPC to its role instead of becoming an unlimited chase.

The initial roster is one Allied player, two Allied NPCs and three German NPCs. Six is an initial configuration, not a final cap. Add only finite configured groups/stages after full-mission pacing, navigation and performance checks. Defeated actors remain defeated between stages, and engaged actors are not hidden or despawned to satisfy a performance budget.

Comparison: run repeatable cases for faction filtering, sight acquisition/loss, last-seen search expiry, patrol return, ally regroup, distinct support destinations, death and full restart. Compare the bounded behavior against a direct-chase reference and record incorrect target choices, stalls and state-transition failures.

## 8. Mission and restart systems

The enemy must obey occlusion, stop attacks after death, and reset. Player damage, enemy damage, objective and HUD updates use authoritative state/events. The mission has explicit Ready/Playing/Won/Lost states and a restart generation ID. Restart clears actors, damage flags, action IDs, timers, ammo state, effects and objective state before re-enabling inputs.

The initial ordered mission is Reach rally A -> Clear assigned group B -> Reach end C. Reach checks the living player and re-evaluates overlap when activated. ClearArea requires a registered, nonempty assigned group with zero living members; leaving the volume, unloading or despawning does not count as death. Deduplicate death events, include earlier kills, advance only the current stage once, and reject stale callbacks after full restart. No bunker destruction, driveable tank, door interaction or cinematic landing is carried over from the old plan.

## 9. Asset and engine integration

- The local city descriptor associates with UE 5.8. Test the installed 5.8.2 baseline later and then pin the team's exact version.
- The vendor page requires ChaosVehiclesPlugin. It is included in the organized project descriptor because the engine plugin is installed, but vehicle gameplay is out of scope and dependency compatibility is not yet tested.
- Both default map settings point to the vendor Paris map for initial environment access; the future team encounter/game mode is not implemented by this configuration change.
- Preserve the vendor's level/sublevel and external-actor package layout during restoration. Do not cherry-pick only the visible `.umap`.
- Commercial environment content is excluded from Git; retain the local source delivery, asset listing/version, entitlement evidence when available, and inventory hashes.
- Reference/Gunplay scripts and Blueprints may reference archived maps, character rigs, materials and helper modules. Inspect and adapt on purpose. No automatic source conversion or generator execution is part of this reset.

## 10. Evidence and performance plan

Target Windows at 1080p and a declared preset, aiming for 60 FPS on the primary desktop. Gate 4 records median and upper-percentile frame times, visible hitches, GPU memory, resolution/upscaling and hardware details. Run the same route and shot workload for baseline/comparison captures. Validate outside the editor and on a second machine.

Performance fallback order: reduce loaded area/optional scenery, bounded effect load, expensive lighting/shadow options, then presentation resolution/preset if required and disclosed. Do not alter hit correctness to improve frame rate.

For each of the four pillars keep: problem, engine/asset boundary, owned implementation, prediction, baseline, repeatable input, result and limitation. Actual results are stored only after measurement. Rendering/performance evidence remains supporting validation. No performance or interaction test was performed as part of this planning transition.

## 11. Demo plan

1. Briefly identify Paris liberation context and the asset/implementation boundary.
2. Play the initial three-stage mission with movement, combat, ally follow/regroup, enemy patrol/search, objectives and full restart.
3. Replay a wall/corner case with trace visualization.
4. Show a reload interruption with action/ammunition events.
5. Compare A* and Dijkstra on matched surveyed routes and show a blocked-route/bottleneck case.
6. Show sight loss, bounded enemy search and return-to-role behavior plus an ally regroup case.
7. Report supporting rendering/performance settings, limitations, team ownership and the source/build identity.

Keep a backup recording of the same frozen build. The later final demo must reflect actual results rather than the environment vendor's trailer or the former Normandy browser prototype.
