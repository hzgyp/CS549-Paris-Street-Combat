# Paris Street Combat

Assignment 1  Group Formation Pillars and Concept

## 1. Group formation

| Group member | NetID | Proposed implementation responsibility |
| --- | --- | --- |
| Yupu Guo (Group Leader) | yg745 | Collision, gunplay and integration |
| Yuqi Pu | yp549 | Animation and character integration |
| Jingdi Wu | jw2046 | Navigation and NPC AI; environment setup |

Yupu submits for the group. Implementation roles will be agreed at kickoff, with integration support across pillars.

## 2. Project concept summary

We propose a single-player first-person squad mission through a connected part of Meshingun Studio's WW2 - France Liberation city, set during the August 1944 liberation period. Our earlier Normandy mission was too complex in scope because it combined sea, beach, and fortified terrain with different movement, combat, and environmental interactions. Reusing the existing city lets us focus on character interaction and NPC design. We will survey the level in Unreal and choose linked streets with an approach, a defended objective, an exit, and an alternative route. The actual geometry will determine the mission area and traversal time.

The initial configuration has six characters: one Allied player, two Allied NPCs, and three German NPCs. This is a development starting point, not a final population cap. We may add enemy groups and separately configured patrol/search routes after testing pacing, navigation, and performance. Allies accompany the player and regroup after corners. Enemies patrol, guard, investigate observed positions, and reposition during combat. Shared behavior logic supports different roles and routes without requiring a new AI system for every soldier.

Intermediate objectives guide the mission: reach a rally point, clear its assigned enemy group, then reach an endpoint. Additional arrival or clearance stages can be configured later. Clearing a stage requires its registered enemy group to be defeated; walking outside an area does not count as defeat. The objective display advances when the current condition passes. Player death causes failure, and restart restores the configured roster and all objectives. Progress between stages preserves casualties and ammunition.

The visual goal is coherent movement and combat across the environment. Running and aiming should blend naturally, reload events should agree with ammunition, and walls should block movement and gunfire. Allies must negotiate narrow passages without teleporting or overlapping, while enemies lose sight behind buildings and search only their last observed target positions. Fixed daylight and static cover keep these interactions readable. The mission uses selected connected routes within the larger city; it does not require every building to be enterable.

Licensed soldier/rifle assets and compatible clips provide visual content, while Unreal supplies rendering and physical simulation. We will integrate these resources with student-built gameplay and evaluate the encounter through repeatable tests and a packaged Windows build. Multiplayer, driving, ocean simulation, unrestricted destruction, and detailed character modeling remain outside scope.

## 3. Street concept and staged mission

![AI-generated street concept using official environment references](Visuals/paris-six-character-concept.png)

AI-generated concept (OpenAI ImageGen), informed by official Meshingun Studio France Liberation references. Initial roster; illustrative layout, not implemented gameplay. [1]

![AI assisted staged mission flowchart](Visuals/paris-mission-flowchart.png)

Initial roster: 1 player + 2 allies + 3 enemies. Add finite groups/stages after testing. Objective markers are not checkpoint saves; this flow shows logic, not map geometry.

## 4. Selected pillars and implementation plan

| Pillar | Specific work | Implementation route |
| --- | --- | --- |
| Animation | Run/aim transitions; fire, reload, hit and death actions. | Retarget purchased clips; Blend Spaces + Montages. Guarded Notifies commit ammo once per reload ID; cancel stale actions. [2] |
| Collision Detection | Character/wall contact; bullet hits on cover and soldiers. | Capsules + camera-aim and muzzle-clearance/obstruction traces. First blocker controls damage; allies block shots without friendly damage. [3] |
| Pathfinding & Navigation | Routes between goals; ally follow/regroup and bottleneck handling. | Student A* at surveyed junctions; NavMesh path lengths as costs, Euclidean heuristic. MoveTo executes legs; reserve distinct destinations. [4] |
| NPC AI | Guard/patrol, sight-driven combat, bounded search, return to role. | Shared Behavior Tree; per-NPC team, role, group, patrol route and search zone. Private Blackboard; search near last seen position. [5, 6] |

Integration and physics support. A Blueprint manager advances Reach/Clear stages from overlap/death events. Reuse compatible rigs/clips, CharacterMovement and engine physics; no custom dynamics solver.

References  [1] France Liberation asset  |  [2] Animation Notifies  |  [3] Collision  |  [4] Navigation  |  [5] Behavior Trees  |  [6] AI Perception  |  [7] Event Dispatchers


- [France Liberation asset](https://www.fab.com/listings/dae418da-1969-444a-821c-c1f30a3f21b6)
- [Animation Notifies](https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-notifies-in-unreal-engine)
- [Collision](https://dev.epicgames.com/documentation/en-us/unreal-engine/collision-in-unreal-engine---overview)
- [Navigation](https://dev.epicgames.com/documentation/en-us/unreal-engine/navigation-system-in-unreal-engine)
- [Behavior Trees](https://dev.epicgames.com/documentation/en-us/unreal-engine/behavior-tree-in-unreal-engine---overview)
- [AI Perception](https://dev.epicgames.com/documentation/en-us/unreal-engine/ai-perception-in-unreal-engine)
- [Event Dispatchers](https://dev.epicgames.com/documentation/en-us/unreal-engine/event-dispatchers-in-unreal-engine)
