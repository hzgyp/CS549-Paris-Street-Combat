# Paris Street Combat

Assignment 2  Product Requirements Technical Specification and MVP

Yupu Guo (yg745), Group Leader  |  Yuqi Pu (yp549)  |  Jingdi Wu (jw2046)

## 1. Product requirements (PRD)

1.1. Problem and audience. For PC FPS players and CS549 reviewers, make animation, gunfire, cover and NPC decisions agree. Reuse France Liberation to simplify the varied terrain and interactions of the earlier Normandy mission.

1.2. Experience. Traverse connected streets through Reach/Clear objectives and an alternate approach. Begin with 1 Allied player, 2 Allied NPCs and 3 German NPCs; six is not a final cap. Add finite groups/stages after pacing, navigation and performance checks. Casualties persist between stages.

## 1.3. User stories

As a player, I want synchronized run/aim/fire/reload actions so that motion and ammunition agree.

As a player, I want walls and soldiers to block shots so that cover has consistent consequences.

As a player, I want allies to follow and enemies to patrol/search so that city traversal affects combat.

As a player, I want intermediate objectives so that I know where to go and which group to defeat.

## 1.4. Feature priorities (MoSCoW)

| MoSCoW | Feature commitment |
| --- | --- |
| Must | Initial six; configurable Reach/Clear stages and NPC routes/search zones; ally follow/regroup; one rifle; four pillars; move/aim/fire/reload/damage; health/ammo/objective UI; win/fail/reset; Windows build. |
| Should | Additional enemy groups/stages after validation; crouch if supported; simple impact/footstep audio. |
| Could | Checkpoint saves; hearing; exposure-weighted routes; ragdolls; improved hand IK. |
| Won't | Landing/ocean, multiplayer, driving, broad interiors, destructible buildings, custom detailed soldiers, complex squad commands, infinite waves, runtime LLMs. |

## 2. Technical specification

2.1. Stack. UE5; Blueprint visual scripting, C++ only if needed. Enhanced Input, UMG, Animation Blueprints, IK Retargeter, NavMesh, AIController/Behavior Trees, AI Perception and Niagara. Structs/Data Assets configure stages/NPCs; Git/LFS; no external runtime library.

2.2. Dependencies. Original asset: UE5.6; working copy: 5.8. Pin a tested version; retain ChaosVehiclesPlugin. Purchase compatible soldier/rifle rigs and clips separately. Survey routes, collision, sightlines and NavMesh; use fixed daylight/static cover. [1]

2.3. AI strategy and performance. ChatGPT/Codex and ImageGen assist offline planning/code/visuals; no runtime AI service. Target: 60 FPS at 1080p on i9-12900F / RTX 3080 / 32 GB Windows PC. Profile mean/p95 frame times, roster and active NPC counts; unmeasured.

![AI-generated street concept using official environment references](Visuals/paris-six-character-concept.png)

AI-generated concept (OpenAI ImageGen), informed by official Meshingun Studio France Liberation references. Initial roster; illustrative layout, not implemented gameplay. [1]

## 2.4. Pillars and implementation

| Pillar | Specific work | Implementation route |
| --- | --- | --- |
| Animation | Run/aim transitions; fire, reload, hit and death actions. | Retarget purchased clips; Blend Spaces + Montages. Guarded Notifies commit ammo once per reload ID; cancel stale actions. [2] |
| Collision Detection | Character/wall contact; bullet hits on cover and soldiers. | Capsules + camera-aim and muzzle-clearance/obstruction traces. First blocker controls damage; allies block shots without friendly damage. [3] |
| Pathfinding & Navigation | Routes between goals; ally follow/regroup and bottleneck handling. | Student A* at surveyed junctions; NavMesh path lengths as costs, Euclidean heuristic. MoveTo executes legs; reserve distinct destinations. [4] |
| NPC AI | Guard/patrol, sight-driven combat, bounded search, return to role. | Shared Behavior Tree; per-NPC team, role, group, patrol route and search zone. Private Blackboard; search near last seen position. [5, 6] |

2.5. Shared integration. Player/NPC weapons share ammo and hit rules; tracers are cosmetic. Configure purchased rigs, collision and clips; reuse CharacterMovement and engine physics.

## 2.6. Mission flow and objective control

![AI assisted staged mission flowchart](Visuals/paris-mission-flowchart.png)

Initial MVP: 1 player + 2 allies + 3 enemies. Add configured groups/stages after validation; objective markers do not imply checkpoint saves.

A Blueprint mission manager evaluates Reach/Clear stages from overlap/death events. Reach checks the player. Clear requires a registered, nonempty assigned group with zero survivors; leaving the area does not count. Deduplicate events, include earlier kills, and recheck state on stage activation. Full restart rejects stale callbacks and restores the configured roster. [7]

## 3. Narrow vertical slice (MVP)

3.1. Core slice and hardest feature. Deliver a polished, playable three-stage mission with the initial roster, one rifle and an alternate approach. The hardest feature is keeping squad navigation, combat and objective progression consistent through the full mission.

3.2. Midterm demonstration. Provide a packaged Windows build, gameplay recording and debug logs. Show allies following/regrouping, enemies losing sight and searching, walls blocking shots, and interrupted reloads updating ammo correctly. Compare A*/Dijkstra route costs. Demonstrate ordered objectives, persistent casualties and full restart, including early kills and duplicate events. Record frame times and path failures before expanding the roster.

3.3. MVP exclusions. Cut additional groups/stages, checkpoint saves, advanced cover tactics, physical bullets and citywide simulation. Keep the core mission functional before expanding content.

4. References  [1] France Liberation asset  |  [2] Animation Notifies  |  [3] Collision  |  [4] Navigation  |  [5] Behavior Trees  |  [6] AI Perception  |  [7] Event Dispatchers


- [France Liberation asset](https://www.fab.com/listings/dae418da-1969-444a-821c-c1f30a3f21b6)
- [Animation Notifies](https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-notifies-in-unreal-engine)
- [Collision](https://dev.epicgames.com/documentation/en-us/unreal-engine/collision-in-unreal-engine---overview)
- [Navigation](https://dev.epicgames.com/documentation/en-us/unreal-engine/navigation-system-in-unreal-engine)
- [Behavior Trees](https://dev.epicgames.com/documentation/en-us/unreal-engine/behavior-tree-in-unreal-engine---overview)
- [AI Perception](https://dev.epicgames.com/documentation/en-us/unreal-engine/ai-perception-in-unreal-engine)
- [Event Dispatchers](https://dev.epicgames.com/documentation/en-us/unreal-engine/event-dispatchers-in-unreal-engine)
