# Paris Street Combat

Assignment 2  Product Requirements Technical Specification and MVP

Yupu Guo (yg745), Group Leader  |  Yuqi Pu (yp549)  |  Jingdi Wu (jw2046)

## 1. Product requirements (PRD)

1.1. Problem and audience. For PC FPS players and CS549 reviewers, integrate UI, character/environment interactions and coordinated NPC behavior in France Liberation, reducing the varied terrain and interaction complexity of the Normandy concept.

1.2. Experience. Traverse connected streets with intermediate objectives; their sequence and locations remain open. Begin with 1 Allied player, 2 Allied NPCs and 3 German NPCs. Expand finite groups after pacing, navigation and performance checks; six is not a final cap.

## 1.3. User stories

As a player, I want synchronized run/aim/fire/reload actions so that motion and ammunition agree.

As a player, I want walls and soldiers to block shots so that cover has consistent consequences.

As a player, I want allies to coordinate and enemies to patrol/search on foot so that movement affects combat.

As a player, I want clear objectives and checkpoint retry so that progress and failure are understandable.

## 1.4. Feature priorities (MoSCoW)

| MoSCoW | Feature commitment |
| --- | --- |
| Must | Initial six; configurable objectives and NPC routes; ally follow/regroup; one rifle; four pillars; move/aim/fire/reload/damage; health/ammo/objective UI; win/fail/retry; Windows build. |
| Should | Checkpoints at selected safe objective boundaries; additional finite groups after testing; crouch if supported; impact/footstep audio. |
| Could | Hearing; custom tactical A*; exposure-weighted routes; ragdolls; improved hand IK. |
| Won't | Landing/ocean, multiplayer, driving, broad interiors, destructible buildings, custom detailed soldiers, complex squad commands, infinite waves, runtime LLMs. |

## 2. Technical specification

2.1. Stack. UE5; Blueprint visual scripting, C++ only if needed. Enhanced Input, UMG, Animation Blueprints, IK Retargeter, NavMesh, AIController/Behavior Trees, AI Perception and Niagara. Structs/Data Assets configure stages/NPCs; no external runtime library required.

2.2. Dependencies. Original asset: UE5.6; working copy: 5.8. Pin a tested version; retain ChaosVehiclesPlugin. Purchase compatible soldier/rifle rigs and clips separately. Survey routes, collision, sightlines and NavMesh; use fixed daylight/static cover. [1]

2.3. AI strategy and performance. ChatGPT/Codex and ImageGen assist offline planning/code/visuals; no runtime AI service. Target: 60 FPS at 1080p on i9-12900F / RTX 3080 / 32 GB Windows PC. Profile mean/p95 frame times, roster and active NPC counts; unmeasured.

![AI-generated street concept using official environment references](Visuals/paris-six-character-concept.png)

AI-generated concept (OpenAI ImageGen), informed by official Meshingun Studio France Liberation references. Initial roster; illustrative layout, not implemented gameplay. [1]

## 2.4. Pillars and implementation

| Pillar | Specific work | Implementation route |
| --- | --- | --- |
| Animation | Smooth idle/walk/run/aim; fire, reload, hit and death actions. | Adapt clips to soldier skeletons; Blend Spaces blend movement, Montages play actions. Reload events transfer ammo once; interrupted actions cannot update it later. [2] |
| Collision Detection | Block movement at walls; identify the first object hit by gunfire. | Capsules enclose moving characters. Trace from camera to aim, then muzzle to aim to detect cover. Apply one hit result; friendly-fire is a separate rule. [3] |
| Pathfinding & Navigation | Reach goals; follow/regroup; avoid crowding and recover from blocked paths. | UE NavMesh finds walkable routes; MoveTo follows them. Assign distinct destinations, avoid nearby NPCs and replan on blockage. Custom tactical A* is optional. [4] |
| NPC AI | Guard, patrol on foot, engage visible enemies, search and regroup. | Reuse a Behavior Tree with separate controller/Blackboard state per NPC. A squad coordinator assigns roles and support goals; perception drives individual decisions. [5, 6] |

2.5. Shared integration. UI reads authoritative health/ammo/objective state. Player/NPC weapons share hit rules; tracers are cosmetic. Configure purchased rigs, collision and CharacterMovement; reuse engine physics.

## 2.6. Mission flow and objective control

![AI assisted staged mission flowchart](Visuals/paris-mission-flowchart.png)

Proposed logic, not final geography. Six is an initial roster; checkpoint sites and any resupply/reinforcement rules remain open.

A Blueprint manager advances objectives once from player arrival or assigned-group defeat events. Proposed checkpoints save objective, player health/ammo and relevant NPC state; retry restores that snapshot, or starts fresh if none exists. Saving alone does not heal, refill or revive. Full restart remains available. [7]

## 3. Narrow vertical slice (MVP)

3.1. Core slice and hardest feature. Deliver a polished connected-street encounter with the initial roster, one rifle, basic UI and intermediate objectives. The hardest feature is integrating UI and physical interactions with the city while NPC movement, decisions and roles remain coordinated as numbers grow.

3.2. Midterm demonstration. Provide a Windows build, gameplay recording and logs. Show UI matching health/ammo, walls blocking movement/shots, correct interrupted reloads, ally regrouping and enemy sight/search. Check objective progression and checkpoint restoration. Compare independent NPC movement with coordinated destinations at bottlenecks; record stalls/frame times before adding NPCs.

3.3. MVP exclusions. Defer additional groups, complex squad commands, advanced cover tactics, physical bullets and citywide simulation. Final mission layout and checkpoint placement follow the editor survey and playtesting.

4. References  [1] France Liberation asset  |  [2] Animation Notifies  |  [3] Collision  |  [4] Navigation  |  [5] Behavior Trees  |  [6] AI Perception  |  [7] Event Dispatchers


- [France Liberation asset](https://www.fab.com/listings/dae418da-1969-444a-821c-c1f30a3f21b6)
- [Animation Notifies](https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-notifies-in-unreal-engine)
- [Collision](https://dev.epicgames.com/documentation/en-us/unreal-engine/collision-in-unreal-engine---overview)
- [Navigation](https://dev.epicgames.com/documentation/en-us/unreal-engine/navigation-system-in-unreal-engine)
- [Behavior Trees](https://dev.epicgames.com/documentation/en-us/unreal-engine/behavior-tree-in-unreal-engine---overview)
- [AI Perception](https://dev.epicgames.com/documentation/en-us/unreal-engine/ai-perception-in-unreal-engine)
- [Event Dispatchers](https://dev.epicgames.com/documentation/en-us/unreal-engine/event-dispatchers-in-unreal-engine)
