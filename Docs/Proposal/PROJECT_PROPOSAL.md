# Paris Street Combat

**CS549 - Current project proposal and implementation plan**

**Team:** Yupu Guo (yg745, team leader), Yuqi Pu (yp549), Jingdi Wu (jw2046).

Current course deliverables: [Assignment 1 PDF](CS549_Assignment1_Proposal.pdf), [editable DOCX](CS549_Assignment1_Proposal.docx), [Assignment 2 PDF](CS549_Assignment2_Proposal.pdf), and [editable DOCX](CS549_Assignment2_Proposal.docx). The older combined English and Chinese PDFs are historical versions, not synchronized translations of this revision. Assignment 2 approval and mentor-assignment email evidence remains pending.

## 1. Concept and product requirements

Paris Street Combat is a single-player first-person squad mission through a connected part of the existing WW2 - France Liberation city, fictionalized during the August 1944 liberation period. The earlier Normandy mission was too complex in scope because it combined sea, beach and fortified terrain with different movement, combat and environmental interactions. Compatible licensed soldier, rifle and animation assets will supply production content; the team develops character interactions, UI integration and NPC systems.

The four primary pillars are **Animation**, **Collision Detection**, **Pathfinding & Navigation**, and **NPC AI / Behavior Trees**. Rendering supports readable combat through the supplied environment, fixed daylight and restrained effects. Physics uses engine facilities; a custom dynamics solver is outside scope.

The initial configuration has six soldiers: one Allied player, two Allied NPCs and three German NPCs. **Six is a starting configuration, not the final population limit.** Combatants share behavior definitions with individual faction, role, encounter group, on-foot patrol route and search zone settings. The team may add finite NPC groups after evaluating pacing, navigation and performance. Casualties and ammunition carry forward during normal progression. A checkpoint retry restores an earlier snapshot; a new mission restores the initial configured state.

The route, objective order and checkpoint locations remain open. Reaching a location and clearing an assigned enemy group are example objective types. Reach rally A → Clear group B → Reach end C is only an illustrative sequence, not a fixed mission specification. The player leads while surviving allies follow and regroup; allied death need not prevent reaching an objective. Player death offers retry.

The team will first survey the city in Unreal, recording overhead captures, connectivity, collision, sightlines, NavMesh coverage and travel time. This determines the playable area, possible alternate approaches and expected duration; neither a one-block boundary nor a fixed duration is imposed. The surrounding city can remain visible without making every street or building navigable. Vendor documentation describes environment tools and materials, not a validated gameplay floorplan.

The audience is PC FPS players and course reviewers. Players should understand where they can move, why cover blocks a shot, when reloading permits firing and how NPCs respond to visibility. Reviewers should distinguish team-authored behavior and integration from engine facilities and purchased content.

| Priority | Requirements |
|---|---|
| Must | Initial six-soldier configuration with configurable population; connected mission area; intermediate objectives; automatic ally follow/regroup; movement, aim, fire, reload and damage; health/ammo/objective UI; four pillars; win/fail/retry; Windows package |
| Should | Checkpoints at selected safe objective boundaries; additional finite NPC groups after validation; crouch if clips support it; simple impact/footstep audio |
| Could | Gunshot hearing; custom tactical A* if useful; exposure-weighted routing; ragdoll death; improved hand IK |
| Excluded | Multiplayer, complex squad commands, civilians, weather, driving, ocean interaction, broad interiors, destruction, ballistic penetration, multiple player weapons, infinite waves, runtime LLM agents and new detailed character modeling |

One player rifle provides the initial combat loop. NPCs share weapon behavior with faction-appropriate visuals and compatible actions. Six unique rigs or animation systems are unnecessary. Exact units, date, uniforms and weapon variants remain asset-approval decisions; this is not a reconstruction of a documented individual battle.

### Mission progression and proposed checkpoints

![Proposed mission flow: start or resume, pursue an objective, update progress and continue or complete; player death retries the latest checkpoint or starts fresh when none exists.](Visuals/paris-mission-flowchart.png)

The [SVG flowchart](Visuals/paris-mission-flowchart.svg) and [editable Mermaid source](Visuals/paris-mission-flowchart.mmd) describe proposed logic, not vendor geography. We propose checkpoint saves at selected safe objective boundaries. Map size alone does not determine the need for checkpoints; traversal time, encounter difficulty and replay cost should guide placement.

A checkpoint records the active objective and completion state, player location/health/ammunition, and relevant NPC identities, alive/dead state, health, ammunition and positions. For the initial connected level, a Blueprint SaveGame record can hold persistent data. Restoring a checkpoint reconstructs that snapshot and reinitializes transient actions, navigation requests and perception safely. Deaths, shots and objective changes after that checkpoint are rolled back. Saving is not automatically healing, ammunition replenishment or ally revival: each would be an explicit mission rule. Resupply, reinforcement and checkpoint locations remain design choices for playtesting. Retry starts from the initial state when no checkpoint exists; a full new-mission restart is always available.

A Blueprint mission controller holds configurable objective records with their type, marker/trigger, assigned enemy group where needed and UI text. Reach checks the living player, including already-overlapping players when the stage activates. Clear counts a nonempty, fully registered assigned group; enemies walking out of a volume are not defeated. Earlier legitimate kills remain counted. Each objective advances once, death events are deduplicated and stale callbacks after retry are ignored. UI changes only after the corresponding gameplay state changes.

### Population growth and coordination

Grow the initial encounter in small finite increments after the six-character baseline is coherent. Assign each NPC a role, current goal, patrol route and search zone; adding more independent copies without coordination risks bunching and blocked passages. A lightweight squad coordinator assigns distinct reachable support destinations and can stagger movement through bottlenecks. Individual NPC controllers retain their own target and perception state.

Separate total mission population from simultaneous active AI. Profile movement stalls, decision updates, animation and CPU/GPU frame times before expanding. Later stages may activate predeclared finite groups, with each group's roster registered before its clearance test. Do not hide engaged NPCs to meet a budget or silently replace earlier casualties. Reinforcement should be an explicit proposed mission event, not automatic replenishment. Retain additions only if they improve pacing and remain readable and responsive.

## 2. Assets and technical stack

Use Unreal Engine with Blueprint visual scripting, Enhanced Input, UMG, Animation Blueprints, IK Retargeter, collision queries, NavMesh/MoveTo, AIController, Behavior Trees/Blackboards, AI Perception and restrained Niagara effects. Small C++ additions require a specific need. No external runtime library or online AI service is required. Version-control tooling has not been selected by the team. Vendor packages keep `/Game/WW2City` names; team content belongs under `/Game/ParisCombat`.

France Liberation supplies city geometry, materials, prefabs, lighting options and tools. Its official listing excludes cinematic trailer soldiers and some impact/explosion effects. Allied/German character visuals, player rifle/arms, motion clips and combat audio remain pending selection. Check skeletons, clips, sockets, first-person suitability, Physics Assets, engine support and rights before acquisition/integration. Retargeting adapts compatible motion; it does not guarantee arbitrary packs work together.

The original vendor project declares **UE5.6**; the active descriptor records **5.8**, and the workstation handoff records **5.8.2**. These observations are not compatibility tests. Pin a tested engine/plugin configuration on a compatibility copy, retaining the vendor-required ChaosVehiclesPlugin and preserving the original delivery.

**IK Retargeter** transfers motion between source and target skeletons using mapped body chains, with pose/alignment adjustments. It is useful when purchased animations and soldiers have different rigs; it may be unnecessary when the chosen pack already supplies compatible clips. **UMG** is Unreal's UI authoring system for widgets such as the crosshair, health/ammo display, objective text, checkpoint feedback and menus. These widgets read gameplay state rather than maintaining separate damage or ammunition calculations.

Unreal supplies rendering, skeletal evaluation, collision primitives, navigation and physical simulation. Purchases supply geometry and motion content. The team owns interaction rules, destination assignment, NPC priorities, coordination, objective/checkpoint logic and UI connections. AI tools may assist offline research, documentation, code/Blueprint work and debugging. The rejected AI-led, from-scratch detailed character-production route will not restart.

## 3. Four technical pillars

| Pillar | Specific work | Proposed implementation |
|---|---|---|
| **Animation** | Smooth idle/walk/run/aim; play fire, reload, hit and death actions; align hands and weapons. | Adapt purchased clips to soldier skeletons; Animation Blueprints and Blend Spaces blend movement; Montages control discrete actions. Timed reload events transfer ammunition once and are invalidated on cancellation. |
| **Collision Detection** | Prevent movement through walls/obstacles; detect cover and character hits correctly. | Configure character capsules, environment collision and hit bodies. Aim from the camera, then check the muzzle-to-aim path; the first obstruction determines one authoritative hit. Friendly-fire policy is separate. |
| **Pathfinding & Navigation** | Reach objectives; follow/regroup; avoid crowding; recover from blocked routes. | UE NavMesh/MoveTo provides route finding and execution. Author reachable destination assignment, local avoidance, bottleneck waiting and bounded replanning. Custom tactical A* is optional if it adds useful decisions or academic evidence. |
| **NPC AI / Behavior Trees** | Guard, patrol on foot, engage visible enemies, search and return to role; coordinate multiple soldiers. | Reuse a Behavior Tree definition with a separate AIController and Blackboard state for each NPC. AI Perception provides observations; a squad coordinator assigns roles/support goals while individuals make local decisions. |

### Animation

Purchased motion clips contain the poses for actions such as running or reloading. If their skeleton differs from the chosen soldier, use IK Retargeter and inspect feet, hands and weapon alignment. A Blend Space blends locomotion clips according to speed/direction, so walk-to-run transitions are gradual. An Animation Blueprint selects and combines the movement and action layers. Montages sequence individual actions such as reload or hit reaction.

An Animation Notify is a timed event in a clip. At the appropriate reload moment it requests the ammunition transfer. Gameplay checks that the character is alive, the same reload is still active and the transfer has not already occurred. Repeated input or duplicate events cannot award extra ammunition; cancellation before transfer leaves ammo unchanged, while cancellation after transfer preserves the completed transfer. A checkpoint retry clears pending actions and ignores events from the prior run. These rules connect visible motions, actual ammunition and UI.

### Collision Detection

A character capsule is a simple rounded collision shape around the body used by CharacterMovement to sweep through the world. Configure it and the city's collision so walls, cover, stairs and narrow passages behave consistently. Purchased visual meshes do not guarantee usable collision. Character hit bodies may use Physics Assets; ragdoll motion is optional.

For instant-hit gunfire, a camera trace first finds what the crosshair aims at. A second trace from the weapon muzzle to that point finds the first obstruction along the real firing line. This prevents a camera peeking around a corner from letting a gun shoot through a wall. An overlap/short query at the muzzle can also reject a muzzle embedded in geometry. One accepted discharge consumes one round and one authoritative hit decides damage and feedback; cosmetic tracers do not decide damage.

Collision is broader than deciding whether allies receive damage. Movement obstruction, cover hits, enemy hits and weapon clearance all belong here. A team filter separately decides whether an eligible character hit receives damage. A proposed beginner-friendly policy lets allied bodies block bullets without friendly damage; this policy remains adjustable and does not change the collision method.

### Pathfinding and navigation

A* is a graph-search method. A NavMesh is a representation of walkable space built from connected polygons. Unreal's navigation system searches this connectivity and follows a resulting route; NavMesh is not a rival to A*. Use the engine route solver as the baseline rather than automatically duplicating it. The assignments name pathfinding algorithms as examples but do not mandate a student-written solver.

The team's work is to survey navigability, project candidate destinations onto reachable ground, choose useful routes/goals and handle execution failures. Allies receive distinct reachable follow/support destinations. Use one chosen local-avoidance approach, plus waiting/priority at narrow passages and bounded replanning after a failed move or goal change. Avoidance alone cannot solve every corridor deadlock. Test independent movement against coordinated assignment and waiting to observe stalls, regroup time and crowding. Do not teleport delayed NPCs.

If instructor feedback or gameplay needs justify an extra tactical layer, author a small graph of verified junctions and use A* to choose among strategic routes; UE navigation still executes the local legs. Edge costs and heuristic assumptions must be stated, with a comparison such as Dijkstra on the same graph. This is optional, not a promised second pathfinding system or a claim of custom Unreal navigation.

### NPC AI and squad coordination

The Behavior Tree is a visual decision asset edited as nodes and connections in Unreal's Behavior Tree editor, not the city map. Selectors, sequences, tasks and conditions express priorities such as death, reload, engage, search, follow or patrol. Sharing the asset means reusing the decision recipe; each soldier has its own AIController instance, tree execution and Blackboard values. Do not synchronize personal target or last-seen keys across all NPCs.

**Patrol means walking between assigned waypoints**, pausing or looking around; it does not involve vehicles. Guard means hold an assigned area. Sight perception filters by faction and updates a soldier's own visible target and last-seen position. After sight is lost, the soldier searches reachable points near that observation for a bounded time, without knowing the unseen player's current position. It then resumes its role; allies regroup and Germans guard/patrol.

For more NPCs, a lightweight coordinator assigns goals, roles and distinct support destinations. Local controllers still decide how to move, reload, engage and react to obstacles. Reservations release when a goal changes, the NPC dies or the mission restores a checkpoint. This division reduces crowding without requiring synchronized identical behavior or a complex player command system. Scale gradually and profile update rates, path requests and animation costs.

## 4. Narrow vertical slice and hardest feature

The MVP is a polished playable encounter across a surveyed connected part of the city, initially using six soldiers, one player rifle, basic health/ammo/objective UI and configurable intermediate objectives. A Reach/Clear sequence illustrates the progression; the actual geography and final mission details remain open. Checkpoints at selected safe boundaries are a proposed Should feature, with a small restoration test planned before expanding the encounter.

The hardest feature is integrating **UI and physical character/environment interactions into the purchased city while NPC movement, decisions and roles remain coordinated as the population grows**. Correct code alone cannot judge collision gaps, rig alignment, sightlines, destination crowding or enjoyable encounter pacing. These require editor inspection, animation review and repeated playtests in the actual environment.

By the midterm, demonstrate a packaged Windows build, gameplay recording and debug logs. Show UI agreeing with damage/ammunition/objectives, walls blocking movement and shots, correct interrupted reloads, allies following/regrouping and enemies losing sight/searching. Exercise objective progression and the proposed checkpoint snapshot/restore path. Compare independent NPC destination choices with coordinated assignments at a bottleneck, then record movement stalls and frame times before adding NPCs. These are planned demonstrations, not completed results.

Keep additional groups, complex squad commands, advanced cover tactics, physical bullets and citywide simulation out of the initial slice. Reuse CharacterMovement and engine physics rather than writing a custom dynamics solver. The rendering/physics contribution is configuration and integration; vendor materials and Unreal rendering algorithms are not student-authored systems.

Target Windows at 1920 x 1080 and 60 FPS on the recorded i9-12900F / RTX 3080 10 GB / 32 GB desktop with a stated quality preset. Report mean/p95 frame times, active NPC count, settings and limitations. This is an unmeasured target.

## 5. Delivery gates and proposed ownership

1. **Dependency readiness:** select compatible licensed assets, pin engine/plugins, survey the city, validate collision/NavMesh and establish an initial Windows package.
2. **Complete playable loop:** integrate initial characters, motion/gunplay, UI, ally/enemy behavior, configurable objectives and retry.
3. **Four pillars and coordination:** refine animation events, hit resolution, navigation recovery and perception/behavior priorities; test distinct support goals at bottlenecks.
4. **Checkpoint and population tuning:** choose safe save boundaries and verify snapshot restoration; playtest pacing, compare small finite NPC additions and profile the complete encounter.
5. **Submission:** preserve the build, dependency instructions, demonstration, disclosures and actual approval correspondence.

Proposed ownership: Yupu Guo leads collision/gunplay and integration; Yuqi Pu leads animation and compatible rig/action integration; Jingdi Wu leads navigation/NPC AI and bounded environment setup. Roles require team confirmation. No course deadline or mentor identity is assumed. Assignment 2's actual concept/pillar approval and mentor-assignment email proof must accompany the report separately; this plan does not substitute for it.

## 6. Visual provenance and limits

Both proposals include the [street concept](Visuals/paris-six-character-concept.png) and the updated [game flowchart](Visuals/paris-mission-flowchart.svg). The street image was generated with OpenAI ImageGen using both official Meshingun Studio gallery images as appearance references. Its first-person view, two allies and three enemies illustrate the initial six-person configuration, not a final population cap. It is concept art, not a verified floorplan or implemented gameplay. The [prompt and input record](Visuals/STREET_MOCKUP_PROMPT.md) document its creation.

The flowchart is an AI-assisted conceptual visual rendered in code from the proposed objective/checkpoint rules. It shows general progression and retry without fixing mission geography. Exact locations require the editor survey. Earlier image versions remain archived provenance and are not embedded in the current reports. See [visual provenance](Visuals/README.md).

## Sources

- Course authority: `Course/Assignments/Assignment 1.docx` and `Assignment 2.docx`.
- [Meshingun Studio: WW2 - France Liberation](https://www.fab.com/listings/dae418da-1969-444a-821c-c1f30a3f21b6): environment features, excluded trailer content, required plugin.
- [Vendor documentation](https://docs.google.com/document/d/15GFarJQnrFBj0UlDT0GBIWS6xswP3kJXnVOzU1083T0/edit), archived as `WW2_France_Liberation_Official_Documentation.pdf` in the source asset's `文档教程（Documentation）/官方源文档归档（Official Source Archive）` directory. Printed pp.9, 14, 23 cover plugins/collision; p.70 marks audio controls inapplicable; pp.71-75 cover optimization/rendering.
- Epic: [IK Retargeting](https://dev.epicgames.com/documentation/unreal-engine/ik-rig-animation-retargeting-in-unreal-engine), [Animation Notifies](https://dev.epicgames.com/documentation/unreal-engine/animation-notifies-in-unreal-engine), [Traces](https://dev.epicgames.com/documentation/unreal-engine/traces-in-unreal-engine---overview), and [Physics Assets](https://dev.epicgames.com/documentation/en-us/unreal-engine/physics-asset-editor-in-unreal-engine).
- Epic: [Navigation System](https://dev.epicgames.com/documentation/en-us/unreal-engine/navigation-system-in-unreal-engine), [Behavior Trees](https://dev.epicgames.com/documentation/en-us/unreal-engine/behavior-tree-in-unreal-engine---overview), and [AI Perception](https://dev.epicgames.com/documentation/en-us/unreal-engine/ai-perception-in-unreal-engine).
