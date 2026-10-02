# Development pipeline - Paris Street Combat

**Actual 2 October increment:** existing-city setup/input, combat/HUD and Yupu's bounded usability review passed. The private Windows Development build now cooks/stages/archives successfully and starts the intended Paris map at verified 1920x1080; post-entry combat regression passed 15 cases/62 assertions. See [the package result](Docs/Development/PARIS_WINDOWS_PACKAGE_RESULT_20261002.md). Continue [navigation and NPC AI](Docs/Development/PARIS_NAVIGATION_AND_AI_IMPLEMENTATION_V1.md). Neither M0/M1 nor mission, warmed/stress performance, second-machine/public-delivery gates are complete; retain existing assets and current seven unpublished package hashes.

**Latest asset-first correction and resumption:** the playable MVP retains the verified Paris environment, characters and motions. Reduce optional functionality/polish, not the asset foundation. The mistaken standalone route is deleted; [completed cleanup](Docs/Development/ASSET_FIRST_CLEANUP_20261002.md) records removal and preserved hashes. Do not regenerate it. Yupu resumed continuous development on 2 October, pausing only for genuine human review/decisions. Follow [the existing-city work package](Docs/Development/PARIS_CITY_GAMEPLAY_IMPLEMENTATION_V1.md): survey Paris and integrate existing characters/rifle/input/HUD in the city. Main entry/playable-build acceptance use Paris.

**2 October execution update:** follow `Docs/Development/ASSIGNMENT3_IMPLEMENTATION_V2.md` for the approved playable-MVP sequence and presentation technology stack. Freeze accepted character/motion baselines; fix only operation/core-evidence blockers before optional polish. Establish packaging and baseline performance early, integrate the loop, prove all four pillars including coordinated/independent navigation comparisons, then measure stress limits and freeze the Assignment 3 deliverables. Earlier gate records are plans or dated evidence, not blanket passes.

**Current development target, 30 September 2026:** follow [Assignment 3 goal version 1](Docs/Development/ASSIGNMENT3_GOAL_V1.md) and its [acceptance checklist](Docs/Development/ASSIGNMENT3_ACCEPTANCE.md), derived from `Docs/Assignment 3_ MVP Development.docx` and the current Assignment 2 MVP. The deliverable is a running prototype with four pillar mechanisms, measured performance, a 2-3 minute real-time demonstration including a stress test, a 1-2 page progress PDF, and working build/video/source links. These are planned requirements, not completed results.

Six soldiers are the initial roster, not a final cap. Survey the connected city before choosing locations, duration or objective order; Reach A -> Clear B -> Reach C is an example. First complete the configurable mission with ally follow/regroup, bounded patrol/search, group registration, unique-death counting and full restart. Use NavMesh/MoveTo with authored destination assignment, local avoidance, waiting and bounded replanning; custom tactical A* is optional. Checkpoints at safe objective boundaries are a Should feature and require snapshot restoration tests if implemented. Before retaining additional finite groups/stages, require three successful full-mission runs, coverage of both verified approaches where available, no progression/navigation deadlocks, and performance within the declared budget. Keep total roster separate from simultaneous active AI; engaged actors and earlier casualties persist. Infinite waves and automatic difficulty increases remain excluded.

This replaces every earlier Normandy and three-pillar pipeline. It implements [the current proposal](Docs/Proposal/PROJECT_PROPOSAL.md) with Animation, Collision Detection, Pathfinding and Navigation, and NPC AI / Behavior Trees as the four primary pillars. Rendering and physical simulation remain supporting engine/asset systems. Detailed runtime validation is explicitly deferred until the named gates.

## Execution order

Before a work package changes assets or gameplay, write its implementation steps and evidence/failure gates. The next character and weapon/action packages are detailed in [the implementation plan](Docs/Development/CHARACTER_AND_WEAPON_IMPLEMENTATION_V1.md). They cover only part of Gate 1 and early Gate 2; the city survey, full mission, four pillars and delivery checks remain required. Teammates perform their own dependency restoration, without blocking Yupu's verified local work.

| Gate | Work | Completion evidence | If blocked |
|---|---|---|---|
| 0 - Direction and organization | New scope, proposal, architecture, history index, asset provenance, source control and old-project archive | New repository and documents; local city working copy; reference inventory; no runtime success claim | Resolve missing organization/source-control facts; do not silently add features |
| 1 - Dependency and environment readiness | Confirm asset entitlement; survey connected routes, collision, sightlines, NavMesh coverage and travel time; pin engine/plugins; restore vendor dependency on another checkout; choose compatible soldier/rifle/action assets; establish the first Windows package | Project loads the scene; survey evidence selects a viable mission route; required asset set works in a compatibility map; packaged start on target machine | Change asset or route, simplify the mission, or cut a requirement. Never restart detailed AI character production |
| 2 - Combat and mission spine | One player, one rifle, initial two allies and three enemies; shared health/attack rules; configurable intermediate objectives, HUD, fail/win/retry/full restart; adapt selected old gunplay only after dependency review | The selected mission completes and fully restarts; group registration, unique deaths, state ownership and Blueprint locations are recorded | Reduce optional behavior or route breadth while preserving the complete loop and initial configuration |
| 3 - Four pillar mechanisms | Guarded animation events, two-stage obstruction checks, coordinated NavMesh/MoveTo execution and shared Behavior Tree/perception with per-NPC state | Repeatable comparisons and failure cases demonstrate the Assignment 2 technical challenge in the actual city | Strengthen the selected mechanisms; custom A* is optional, not a replacement for working integration |
| 4 - Quality and performance | Tune the initial mission; check period assets and rig alignment; measure collision/navigation and frame times; test a second machine; evaluate Should checkpoints and finite population additions separately | Recorded settings, mean/p95 frame times, baseline and stress-test limits, bugs and remaining limitations; checkpoint evidence if implemented | Reduce optional scenery/effects or later roster growth; disclose unmet targets and optional cuts |
| 5 - Feature freeze and delivery | Freeze source/build/asset identity; record the 2-3 minute annotated demo with stress test; write the 1-2 page progress report; verify playable build, video and public source delivery | Assignment 3 checklist and working links, credits, build instructions and actual prerequisite evidence | Fix regressions only; resolve public-source access without exposing commercial assets or private correspondence |

## Dependency chain

Environment restoration, map survey and asset/rig compatibility precede final gameplay integration. The shot-result contract is shared by collision and supporting feedback. The action-state contract is shared by animation, ammunition and input. Pathfinding supplies routes that NPC AI executes; mission progression consumes registered actor/death state. Reset correctness belongs to every system, not a last-minute cleanup task.

Old gunplay snapshots are material for Gate 2. Do not copy their whole project or execute their generator scripts into the new city. They contain old `/Game/Normandy` paths and may refer to archived characters, maps or helper scripts.

## Proposed cadence

- Use the next development session for Gate 1. A two-workday investigation window is a decision checkpoint, not a promise that all work fits in two days.
- Build the complete initial mission selected by the survey before adding roster growth, extra stages or visual polish.
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

Remove optional custom A*, unverified alternate approaches, extra stages/groups, extra ambient effects, crouch if unsupported by the selected rig, and optional polish. Defer Should checkpoints with an explicit report entry if restoration is not ready. Preserve reliable shooting/cover, coherent actions/ammo/UI, coordinated NavMesh movement, bounded ally/enemy behavior, configurable objectives, full restart and all four pillar evidence sets. Reduce content breadth before attempting new models or expensive simulation systems.

## Review handoffs

Supporting feedback receives the authoritative physical hit and surface type. Animation receives the accepted action state and returns guarded action events. Gunplay owns accepted shots/ammunition and receives animation completion/cancellation. Navigation owns reachable destinations, reservations, avoidance, waiting and bounded MoveTo recovery; an optional graph layer owns its own search. NPC AI owns faction/role decisions and bounded search behavior. NPCs use the same damage and obstruction policy as the player. The mission owns objective, retry and restart lifecycle.

Suggested owners and confirmation status are in Docs/Decisions/TEAM_AND_OWNERSHIP.md. Keep one editor per binary asset and coordinate integration in small commits.
