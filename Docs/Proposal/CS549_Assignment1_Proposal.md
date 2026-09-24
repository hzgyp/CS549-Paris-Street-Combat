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

We propose a single-player first-person squad mission through a connected part of Meshingun Studio's WW2 - France Liberation city, set during the August 1944 liberation period. Our earlier Normandy mission was too complex in scope because it combined sea, beach, and fortified terrain with different movement, combat, and environmental interactions. Reusing the existing city lets us focus on character interaction and NPC design. An Unreal editor survey of connectivity, collision, sightlines and travel time will determine the playable routes and objective locations.

The initial configuration has six characters: one Allied player, two Allied NPCs, and three German NPCs. This is a development starting point, not a final population cap. We may add finite groups after evaluating pacing, navigation and performance. Allies accompany the player, regroup and use distinct support positions. Enemies guard, patrol on foot, react to visible targets and search near their last observed positions. Shared behavior definitions and individual state allow different soldiers to coordinate without copying one another's actions.

Intermediate objectives guide progress through connected streets. Reaching a location and clearing an assigned enemy group are example objective types; the sequence and geography remain open. We propose checkpoints at selected safe objective boundaries. Retrying restores the saved objective, health, ammunition and relevant NPC state; a new mission restores the initial configuration. Saving does not itself heal, refill ammunition or replace casualties. Checkpoint locations, resupply and reinforcement rules will be selected through playtesting.

The visual goal is coherent movement and combat within the purchased environment. Running and aiming should blend naturally, reload actions should agree with ammunition, and walls should block movement and gunfire. Allies must negotiate narrow passages without teleporting or overlapping, while enemies respond to sight rather than knowing unseen player positions. Health, ammunition and objective displays must reflect the same gameplay state. These interactions and coordinated NPC movement are the main integration challenge as the population grows.

Licensed soldier/rifle assets and compatible motion clips provide visual content, while Unreal supplies rendering, navigation and physical simulation. We will configure these resources and build the gameplay, coordination and UI integration. A connected mission area provides the initial playable slice; not every city building must be enterable. Multiplayer, driving, ocean simulation, unrestricted destruction and detailed character modeling remain outside scope.

## 3. Street concept and staged mission

![AI-generated street concept using official environment references](Visuals/paris-six-character-concept.png)

AI-generated concept (OpenAI ImageGen), informed by official Meshingun Studio France Liberation references. Initial roster; illustrative layout, not implemented gameplay. [1]

![AI assisted staged mission flowchart](Visuals/paris-mission-flowchart.png)

Initial roster: 1 player + 2 allies + 3 enemies, expandable after testing. Flow and checkpoint policy are proposed; objective locations and resupply rules remain open.

## 4. Selected pillars and implementation plan

| Pillar | Specific work | Implementation route |
| --- | --- | --- |
| Animation | Smooth idle/walk/run/aim; fire, reload, hit and death actions. | Adapt clips to soldier skeletons; Blend Spaces blend movement, Montages play actions. Reload events transfer ammo once; interrupted actions cannot update it later. [2] |
| Collision Detection | Block movement at walls; identify the first object hit by gunfire. | Capsules enclose moving characters. Trace from camera to aim, then muzzle to aim to detect cover. Apply one hit result; friendly-fire is a separate rule. [3] |
| Pathfinding & Navigation | Reach goals; follow/regroup; avoid crowding and recover from blocked paths. | UE NavMesh finds walkable routes; MoveTo follows them. Assign distinct destinations, avoid nearby NPCs and replan on blockage. Custom tactical A* is optional. [4] |
| NPC AI | Guard, patrol on foot, engage visible enemies, search and regroup. | Reuse a Behavior Tree with separate controller/Blackboard state per NPC. A squad coordinator assigns roles and support goals; perception drives individual decisions. [5, 6] |

Integration and physics support. Connect UI, combat and coordinated NPC movement within the city. A Blueprint manager controls objectives and checkpoint state. Configure CharacterMovement, collision and engine physics; no custom dynamics solver.

References  [1] France Liberation asset  |  [2] Animation Notifies  |  [3] Collision  |  [4] Navigation  |  [5] Behavior Trees  |  [6] AI Perception  |  [7] Event Dispatchers


- [France Liberation asset](https://www.fab.com/listings/dae418da-1969-444a-821c-c1f30a3f21b6)
- [Animation Notifies](https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-notifies-in-unreal-engine)
- [Collision](https://dev.epicgames.com/documentation/en-us/unreal-engine/collision-in-unreal-engine---overview)
- [Navigation](https://dev.epicgames.com/documentation/en-us/unreal-engine/navigation-system-in-unreal-engine)
- [Behavior Trees](https://dev.epicgames.com/documentation/en-us/unreal-engine/behavior-tree-in-unreal-engine---overview)
- [AI Perception](https://dev.epicgames.com/documentation/en-us/unreal-engine/ai-perception-in-unreal-engine)
- [Event Dispatchers](https://dev.epicgames.com/documentation/en-us/unreal-engine/event-dispatchers-in-unreal-engine)
