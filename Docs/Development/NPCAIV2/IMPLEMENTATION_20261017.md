# NPC AI V2 — audit and finite offline implementation

17 October 2026. Owner: dedicated NPC AI chat. Status at authoring: audit complete within the read-only limits below; offline candidate planned. This document precedes candidate code. Authorization covers audit, design, an independent local simulation and source/static checks. No Game/Editor compile, cook, stage, engine entry, playable routing, save mutation, native/Content edit, shared-source merge, upload or publication.

## Entry, evidence and existing behavior

`CURRENT_TUTORIAL_SOURCE_PENDING.json` revision 10 selects `Unreal/Variants/G1AudioTutorial20261017/Project`; source manifest SHA256 `341e91b9bba31747b3e605af94edddc7687032fd97d39c1849e771b5a49f934c`, 143 files. Game SHA256 `5f4591d2daf7bce1e010ff36223e4548a442024f685580195376a5ecf825e546`. This source-only snapshot has no Content directory: native gameplay is an external dependency, not a source-clone capability. New offline files cannot replace the built package or inherited human acceptances.

Read actual AGENTS, HANDOFF_CURRENT, tutorial/action collaboration, README, DEVELOPMENT_PIPELINE, proposal, technical design and the historical queries `NPC AI`, `NPC interaction`, `navigation`, `shared decision`, `bounded search`. The old October 2 pause is superseded only by the current explicit NPC audit/offline candidate authorization; it is not engine/native integration permission. Historical implementation scripts are inspected as source, never executed.

| Area | Evidence | Audit finding and limit |
| --- | --- | --- |
| Controller/BT/BB | NPCInteractionV1 formal result and inventory; formal bootstrap author; selected bridge source `RetainedTree`, `RunBehaviorTree` | FormalCombatV1 derives from CombatV2 and has five controller instances/private BBs. Shared definitions are real; shared target memory is not evidenced. Disk hashes will be read back. No new native graph inspection/runtime is claimed. |
| Sensing | SightV4 invokes `ue_b1_sight_author_v2.py`; `PC_RecordSight`; selected `ParisEquipmentSightBridge` | PawnSensing, 0.25 s sampling, faction filter, last observed position/time, visibility expiry. Equipment bridge filters smoke before original sight broadcast. AI Perception hearing is a proposed extension; no current hearing callback implementation found in the inspected lane. |
| Enemy policy | SearchV9 author and retained search results | Five fixed offsets around frozen last seen, 15 s search deadline, guard/patrol return. This is bounded real behavior, but offset geometry and distance rules are simple; no measured cover utility or current EQS candidate selection evidenced. |
| Combat | CombatV2 author, action adapter NI001, formal result | Stop/Turn/Fire/Reload through original transaction IDs, health/ammo/cooldown/LOS gates; service 0.1 s. Legal targets can change; tests must not assume one fixed actor. NPC deaths and conserved resources are real historical results, not new simulation results. |
| Allies | SquadV4 author; selected `UpdateBridgeSquad` | Distinct projected reserved endpoints, follow/regroup, support offsets, finite chase; cutoffs 850 cm travel / 900 cm player distance, original acceptance envelope 1000 cm. Bridge specialization uses 450/700 cm lag and actual 55 cm arrival. Do not silently replace these accepted rules with simulator tuning. No dynamic utility/cover role allocator evidenced. |
| Tutorial | selected `ParisTutorialRuntime::Follow`, `Family` | Before combat, scripted noncombat follow every 0.8 s, fixed world offsets (-200,+/-110), complete path check and MoveTo; BT can be stopped. Tutorial visibility/collision gates intentionally precede combat. New AI must respect those gates and must never hide an already engaged actor to save performance. |
| Navigation | selected `UParisG1AgentPlan`, bridge hook, tactical equipment ownership | Native agent/feet start corrects a witnessed centre-vs-feet failure. Multiple movement owners exist: BT, bridge specialization, tutorial and temporary hazard evade. One arbiter/request generation is essential; stopping a Brain alone does not stop all movement writers. |

Source review is not a decompilation of cooked Blueprints, new render acceptance, physical travel, stress, PIE or second-machine acceptance. A missing feature means no implementation was found in this bounded evidence, not proof that every asset in the workspace lacks it. Asset-index CLI lookup failed before return with missing PIL in the default Python; existing registered snapshot was read directly without refresh or registry writes.

## Failures read and changed mechanism

- NI001: preserve original reload terminal identity (Ready with one ActionID advance), original conservation and cancellation; action leaves use existing adapter, not simulated damage.
- NI003: raw offset/projection/complete path are separate; actual capsule arrival remains necessary. Controller rotation versus actor heading matters. Test simultaneous two-body movement separately from sequential one-body tests.
- MI005: RequestSuccessful and SquadFailed=false do not establish travel; record measured progress and the owner/reason of explicit aborts. Waiting must run even outside the playing branch.
- MI006: start from GetNavAgentLocation; goals have explicit feet coordinates. A new target/goal cannot clear exhaustion every service tick.
- ML020: saved and unsaved expanded NavMesh differ; a static graph or expansion exhaustion is not an obstacle/travel verdict.
- MI027: bridge hook can call StopMovement independently of Brain; hazard override needs explicit finite ownership and recovery.

Early falsifiable acceptance: a target behind an occluder produces no sight event and its hidden movement cannot change enemy memory or destination. Stop the candidate on any hidden-location read, stale-generation admission, unbounded request sequence, collision penetration, same support goal, or protected source drift. Preserve failed runs/identities; repair with a new run identity.

## Algorithm and module boundaries

Use a shared priority BT definition with private Blackboard per NPC. Order: Dead/Frozen -> admitted action/hazard owner -> visible hostile combat -> finite memory investigation/search -> faction role. A state machine labels intent for debugging; it does not replace the BT action/cancellation contract. Sight acquisition requires live hostile, range, FOV and occlusion. Hearing supplies an event position and uncertainty, never a live target lock or fire permission. Squad reports are immutable timestamped observations and expire; they never expose a hidden Actor transform. A target invalidation event comes from the mission registry; ordinary death never resurrects it.

Enemy: Guard -> Alert -> Engage -> Investigate -> Search -> Return -> Guard; fresh sight can reacquire from any live state. Alert dwell and sight-loss grace reduce flicker; a search episode has a fixed deadline and finite point count. Repeated hearing in the same episode cannot extend that deadline. Patrol requires an authored verified route and uses walking; none is newly selected here.

Allies: Follow/Regroup or Support/Overwatch, independently sensed and independently executed. Follow positions are distinct projected points. During contact, two role-specific utilities score at most eight candidates and the coordinator exhaustively compares at most 64 pairs, rejecting shared/too-close goals. The first ally favors a useful covered support position; the second favors a separated observation/firing lane. This bounded two-agent assignment is sufficient for the initial roster; no Hungarian solver, learning policy, runtime LLM, or automatic reinforcement is justified. More actors require another budget/pacing/navigation evaluation.

Hard gates precede utility: correct scope/height layer, free capsule, complete reachable path, role/player distance budget and reservation ownership. With normalized features, Support utility = cover weight * threat occlusion + range weight * ideal engagement range + travel weight * short path + support weight * proximity to player. Overwatch changes weights and rewards LOS to the **observed** threat position. Target score uses observed range and freshness only. Ties sort stable IDs; incumbent goals require a configured score margin/dwell before switching. Existing ammo/health can be admitted inputs later, but no resource assignment is permitted.

UE EQS is appropriate for bounded candidate generation/tests once real cover data exists; a Blueprint scoring function is the initial implementation, with EQS optional underneath the same feature contract. UE AI Perception reports sight/hearing, BT/BB owns decisions, NavMesh/MoveTo owns production pathfinding. One production local-avoidance method (proposed Detour Crowd) is selected after capsule/runtime validation; do not stack RVO and Detour. The offline grid BFS is only a small geometry adapter, not Paris navigation, custom tactical A*, or UE avoidance validation. Its node budget is explicit; budget exhaustion is Unknown/BudgetExceeded, never Unreachable.

No new C++ is needed for this package. Python provides the executable rule oracle and finite test harness; replay JavaScript renders recorded results and cannot make AI decisions. Blueprint adapters later port the documented functions and must consume the oracle vectors; there is no second JavaScript simulation.

## Data flow and pseudocode

```text
registry + map adapter -> bounded sensed observations (id, position, time, sense, uncertainty)
each controller -> private target score/memory -> intent state + reason
ally coordinator <- timestamped private reports + reachable candidate scores
coordinator -> distinct reservations (owner, generation, destination, assignment)
intent -> move/action arbiter (owner, generation, request id, goal feet, deadline)
callback -> admit only matching current token -> progress/result -> bounded recovery
all stages -> deterministic evidence stream -> replay + UE conformance vectors

on sense_tick:
  filter live hostile within FOV/range; trace occlusion; score observed candidates
  update only observed target memory; expire sight; hearing writes event memory
on decision_tick:
  honor lifecycle and fixed search deadline; choose BT intent with hysteresis
  allies compare gated candidate pairs; retain occupied reservations on arrival
on move_tick:
  if matching goal changed materially and budget allows: request complete path
  measure displacement; stall -> bounded retry (two) -> Waiting(reason)
  ignore stale callback; never teleport, manufacture arrival or reset budgets per target
```

## Parameters and executable work package

`Tools/Simulation/NPCAIV2/policy.json` is the single tuning/feature contract. Simulation units metres/seconds; UE adapter multiplies positions by 100 and uses native agent/feet coordinates. Values are **fixture defaults**, not authorized replacement of existing 850/900/1000 cm rules. Fixed seed 54917; fixed step 0.1 s, perception 0.2 s, decision 0.5 s, max 30 s; view traces sampled 0.5 s, full traces retained. Sight 14 m / 120 degree FOV, hearing 10 m with explicit toy wall attenuation, loss grace 0.6 s, alert 0.5 s, search 6 s / <=4 points, memory 8 s, minimum replan interval 0.6 s, <=2 retries per move episode, <=8 attempts per NPC per 30 s, <=700 grid nodes per query, <=8 target/cover candidates. Exact numbers/readback belong to the config and results.

Sequence: freeze identities and source/native snapshots -> implementation EN/ZH -> reusable policy/navigation/scenarios -> generate finite runs and raw evidence -> invariant/comparison/frame-rate tests -> offline replay inspection -> result and hash/function handoff. New source is `Tools/Simulation/NPCAIV2`; evidence only `tmp/npc-ai-v2-20261017`; docs only this new NPCAIV2 lane. No trial executable/UserDir or shared Content changes. Do not invoke historical engine scripts. No automatic server, scheduler or recurring job.

Required fixtures: occlusion/loss/reacquisition; deadline expiry; hearing behind wall; invalid target; unreachable goal; physically stalled mover; simultaneous two-ally cover/follow; bottleneck ownership; threshold jitter; frame-rate scheduling and finite five-NPC load. Compare against direct chase/independent same-goal reference on identical geometry/timing. Metrics: illegal hidden reads, hidden-memory drift, transition count, search duration/points, expired/stale admissions, query/expansion/request counts, retries/waits, actual arrival error, pair separation, reservation retention/release, comparison collisions and wall-clock planning cost. Wall-clock timing is host Python only, not UE FPS.

## Map dependencies and integration gates

Read `tmp/map-survey-continuation-20261013/PROGRESS.json`, overnight queue/reservation and `collections/complete_v3/analysis_v1/ANALYSIS.json`. Queue complete, reservation finished, supervision/automation paused; authorization expired October 14 08:00 America/New_York. Saved: 69,664 measured XY / 621,536 unknown; expanded: 549,152 measured / 142,048 unknown, 1,386 components. Scopes remain separate. Expanded T2->T3 155.75 m is a static measured graph; CP1->T2 is in different measured components. Neither is NPC travel. A bridge no connecting landing and B player truck-bypass are retained human facts; AI/squad/both directions remain unverified. No new route, combat site, cover placement or map survey is selected.

Required survey handoff fields: map/package/source hash, scope (saved/expanded), layer/support Z, coordinate frame, agent capsule radius/half-height/step/slope, nav settings/hash, node/edge IDs, support/collision/occlusion policies, candidate cover surfaces/normals/peek points and rights, clearance/sweeps, partial/complete/unknown result, path length, directed physical route trials, player/each faction/both allies, bottleneck width/queue capacity, actual travel/stall/time/error, ownership and raw evidence IDs. Reject unmeasured cover as production input. `map_contract.json` records the interface and gate, not fabricated measurements.

Future integration: re-read combined selector -> reconcile all other lanes -> coordinator owns shared merge -> new team-owned Blueprint candidates -> verify private BB and single move owner -> fresh saved-map/NavMesh agent queries and capsule travel -> actual two-body bottleneck/cover/LOS/hearing/action tests -> generation/checkpoint resource regressions -> finite timing/pacing/performance -> human review. Build/playtest only after a later explicit human request. Detailed animation/contact/crouched fire are outside this increment.

## Acceptance, rollback and sources

Offline acceptance means all finite invariants, repeatable same-seed trace, matched comparisons, recorded actual toy displacement and working scrub/selection controls. It is not adoption or UE/map/course acceptance. Preserve the incumbent selected source, original earned saves, native models/motions/resources and every failed run. Rollback consists of leaving the independent candidate unselected; no delete or restore of shared bytes. Any future merge needs exact changed functions/files/hashes and a current-base reconciliation receipt.

Primary references checked October 17: [AI Perception](https://dev.epicgames.com/documentation/en-us/unreal-engine/ai-perception-in-unreal-engine) for sensed events and bounded age; [Behavior Tree overview](https://dev.epicgames.com/documentation/en-us/unreal-engine/behavior-tree-in-unreal-engine---overview) for event-driven Blackboard branches; [EQS](https://dev.epicgames.com/documentation/en-us/unreal-engine/environment-query-system-in-unreal-engine) for generated/tested candidates; [avoidance](https://dev.epicgames.com/documentation/en-us/unreal-engine/using-avoidance-with-the-navigation-system-in-unreal-engine) for separate RVO/Detour choices. These explain engine boundaries, not project runtime results.
