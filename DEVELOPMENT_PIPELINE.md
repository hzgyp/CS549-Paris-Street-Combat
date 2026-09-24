# Development pipeline - Paris Street Combat

**Latest scope correction:** six soldiers are the initial roster, not a final cap. The connected city mission uses ordered Reach rally A → Clear assigned group B → Reach end C objectives and full mission restart. NPCs share AI code with individual team, role, encounter-group, patrol-route and search-zone settings. Follow the current proposal's map-survey gate before choosing area, duration or graph size; earlier compact-street assumptions below are superseded.

**Current delivery direction, 23 September 2026:** use the [proposal](Docs/Proposal/PROJECT_PROPOSAL.md) for all four pillars and the initial one-player/two-ally/three-German roster. First complete its three-stage mission with ally follow/regroup, bounded patrol/search, group registration and unique-death counting, and a full restart that restores the configured roster and objective state. Then consider small NPC increments and extra finite groups/stages after three successful full-mission runs, coverage of both verified approaches where available, no progression/navigation deadlocks, and performance within the declared budget. Keep total roster separate from the measured simultaneous active-AI budget; do not hide/despawn engaged actors or reset earlier casualties. Infinite waves, automatic difficulty increases and checkpoint/save reload are outside the baseline.

This replaces every earlier Normandy and three-pillar pipeline. It implements [the current proposal](Docs/Proposal/PROJECT_PROPOSAL.md) with Animation, Collision Detection, Pathfinding and Navigation, and NPC AI / Behavior Trees as the four primary pillars. Rendering and physical simulation remain supporting engine/asset systems. Detailed runtime validation is explicitly deferred until the named gates.

## Execution order

| Gate | Work | Completion evidence | If blocked |
|---|---|---|---|
| 0 - Direction and organization | New scope, proposal, architecture, history index, asset provenance, source control and old-project archive | New repository and documents; local city working copy; reference inventory; no runtime success claim | Resolve missing organization/source-control facts; do not silently add features |
| 1 - Dependency and environment readiness | Confirm asset entitlement; survey connected routes, collision, sightlines, NavMesh coverage and travel time; pin engine/plugins; restore vendor dependency on another checkout; choose compatible soldier/rifle/action assets; establish the first Windows package | Project loads the scene; survey evidence selects a viable mission route; required asset set works in a compatibility map; packaged start on target machine | Change asset or route, simplify the mission, or cut a requirement. Never restart detailed AI character production |
| 2 - Combat and mission spine | One player, one rifle, initial two allies and three enemies; shared health/attack rules; Reach/Clear/Reach progression; fail/win/full restart; adapt selected old gunplay only after dependency review | The initial mission completes and fully restarts; group registration, unique deaths, state ownership and Blueprint locations are recorded | Reduce optional behavior or route breadth while preserving the ordered mission and initial configuration |
| 3 - Four pillar mechanisms | Implement guarded animation events, two-stage obstruction checks, surveyed-graph A*, and shared Behavior Tree/perception behavior with per-NPC configuration | Matched comparisons, known failure cases, mechanism explanations, full-mission logs and midterm package | Strengthen the selected mechanisms; do not add an unrelated pillar |
| 4 - Quality and performance | Tune the full initial mission; check period assets; align hands/gun; tune collision, navigation and sight lines; profile lighting, loaded area and simultaneous active AI; test another machine | Recorded quality preset and frame-time distribution, route/path failures, fixed bugs and remaining limits | Reduce optional scenery/effects or later roster growth; swap incompatible assets; remove optional content |
| 5 - Feature freeze and delivery | Reproduce all comparisons, freeze source/build identity, prepare brief demo and backup capture, complete approval/report requirements | Demonstration build, source tag, credits, evidence and submission package | Fix regressions only; no new systems |

## Dependency chain

Environment restoration, map survey and asset/rig compatibility precede final gameplay integration. The shot-result contract is shared by collision and supporting feedback. The action-state contract is shared by animation, ammunition and input. Pathfinding supplies routes that NPC AI executes; mission progression consumes registered actor/death state. Reset correctness belongs to every system, not a last-minute cleanup task.

Old gunplay snapshots are material for Gate 2. Do not copy their whole project or execute their generator scripts into the new city. They contain old `/Game/Normandy` paths and may refer to archived characters, maps or helper scripts.

## Proposed cadence

- Use the next development session for Gate 1. A two-workday investigation window is a decision checkpoint, not a promise that all work fits in two days.
- Build the complete initial three-stage mission before adding roster growth, extra stages or visual polish.
- Prioritize the Gate 3 slice for the actual course midterm once its date is confirmed.
- Reserve at least the final two weeks before the actual submission deadline for Gate 5 and regression fixes.
- The team mentioned late November; official course dates and individual availability remain unconfirmed. Replan against verified dates without expanding scope.

## Definition of an accepted feature

1. It is a Must item or has explicit scope approval.
2. Its required model/rig/motion assets already exist and are usable under the selected license.
3. A member can explain the implementation and locate the relevant Blueprint/material/action state.
4. It has observable acceptance criteria and a reset path.
5. It works in the shared build, not just the author's editor session.

These are future implementation criteria. They do not block the present document/source-control reset.

## Cuts, in order

Remove unverified alternate approaches, extra stages/groups, extra ambient effects, crouch if unsupported by the selected rig, and optional polish. Preserve reliable shooting/cover, coherent actions/ammo, the surveyed A* route layer, bounded ally/enemy behavior, ordered objectives, full restart and four pillar evidence sets. Reduce content breadth before attempting new models or expensive simulation systems.

## Review handoffs

Supporting feedback receives the authoritative physical hit and surface type. Animation receives the accepted action state and returns guarded action events. Gunplay owns accepted shots/ammunition and receives animation completion/cancellation. Pathfinding owns graph search and route execution requests; NPC AI owns faction/role decisions and bounded search behavior. NPCs use the same damage and obstruction policy as the player. The mission owns objective and restart lifecycle.

Suggested owners and confirmation status are in Docs/Decisions/TEAM_AND_OWNERSHIP.md. Keep one editor per binary asset and coordinate integration in small commits.
