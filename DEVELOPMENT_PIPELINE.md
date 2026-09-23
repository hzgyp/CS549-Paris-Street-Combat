# Development pipeline - Paris Street Combat

This replaces every earlier Normandy pipeline. It implements [the new proposal](Docs/Proposal/PROJECT_PROPOSAL.md) with Rendering, Animation and Collision Detection as the only primary pillars. The present task establishes the baseline, organizes files and publishes source control. Detailed runtime validation is explicitly deferred.

## Execution order

| Gate | Work | Completion evidence | If blocked |
|---|---|---|---|
| 0 - Direction and organization | New scope, proposal, architecture, history index, asset provenance, source control and old-project archive | New repository and documents; local city working copy; reference inventory; no runtime success claim | Resolve missing organization/source-control facts; do not silently add features |
| 1 - Dependency and environment readiness | Confirm asset entitlement; select bounded street; pin engine/plugins; restore vendor dependency on another checkout; configure map/game mode; choose one soldier/gun/action set; first Windows package | Project loads required scene; required asset set works in a small compatibility map; packaged start on target machine | Change asset, simplify scene or cut requirement. Never restart detailed AI character production |
| 2 - Combat spine | One player, one weapon, one enemy configuration, health, basic attack, objective, fail/win/reset; adapt selected old gunplay only after dependency review | Short encounter completes and resets; state ownership and Blueprint locations recorded | Reduce enemy behavior, movement and encounter size; retain the core loop |
| 3 - Three pillar mechanisms | Implement bounded surface feedback, action-event synchronization and two-stage obstruction checks using shared shot/action contracts | Matched baseline comparisons, known failure cases, mechanism explanations and midterm package | Strengthen the selected mechanism; do not add an unrelated pillar |
| 4 - Quality and performance | Tune a single encounter; check period assets; align hands/gun; tune collision and sight lines; profile lighting, loaded area and effects; test another machine | Recorded quality preset and frame-time distribution, fixed bugs and remaining limits | Reduce loaded area/effects quality/count; swap incompatible assets; remove optional content |
| 5 - Feature freeze and delivery | Reproduce all comparisons, freeze source/build identity, prepare brief demo and backup capture, complete approval/report requirements | Demonstration build, source tag, credits, evidence and submission package | Fix regressions only; no new systems |

## Dependency chain

Environment restoration and asset/rig compatibility precede final gameplay integration. The shot-result contract is shared by collision and rendering. The action-state contract is shared by animation, ammunition and input. Reset correctness belongs to every system, not a last-minute cleanup task.

Old gunplay snapshots are material for Gate 2. Do not copy their whole project or execute their generator scripts into the new city. They contain old `/Game/Normandy` paths and may refer to archived characters, maps or helper scripts.

## Proposed cadence

- Use the next development session for Gate 1. A two-workday investigation window is a decision checkpoint, not a promise that all work fits in two days.
- Build the small combat loop before adding visual polish or a longer mission.
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

Remove optional approaches and extra street segments, extra ambient effects, unnecessary enemy navigation, crouch if unsupported by the selected rig, and optional polish. Preserve reliable shooting/cover, coherent actions/ammo, readable hit feedback, win/fail/reset and three pillar evidence sets. Reduce content breadth before attempting new models or expensive simulation systems.

## Review handoffs

Rendering receives the authoritative physical hit and surface type. Animation receives the accepted action state and returns guarded action events. Gunplay owns accepted shots/ammunition and receives animation completion/cancellation. NPCs use the same damage and obstruction policy as the player. The mission owns objective and restart lifecycle.

Suggested owners and confirmation status are in Docs/Decisions/TEAM_AND_OWNERSHIP.md. Keep one editor per binary asset and coordinate integration in small commits.
