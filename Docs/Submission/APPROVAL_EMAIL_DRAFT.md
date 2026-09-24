# Approval email draft

Prepared but not sent.

**To:** Course Instructor, Danrui, and Sen using verified course addresses

**Subject:** [CS 549] Project Approval Request - Group Paris Street Combat

Dear Professor, Danrui, and Sen,

We propose revising our Normandy landing concept to Paris Street Combat, a single-player squad mission through a connected part of the existing WW2 - France Liberation city, fictionalized during the August 1944 liberation period. We will reuse the environment and compatible licensed soldier/rifle assets, allowing us to focus on character interaction instead of ocean, beach, fortification and detailed character modeling. The initial MVP roster is six soldiers: one Allied player, two Allied NPCs and three German NPCs. Six is a starting configuration, not a final population limit. We may add NPCs and finite encounter groups after evaluating mission pacing, navigation and performance. Defeated soldiers remain defeated across objective stages until a full mission restart.

Our proposed pillars are Animation, Collision Detection, Pathfinding and Navigation, and NPC AI / Behavior Trees. Our own work will implement synchronized action/ammunition state, camera-aim and muzzle-obstruction checks, a small shared A* route graph connected to Unreal navigation, and perception-driven behavior with faction rules. NPCs share an AIController and Behavior Tree, with individual team, role, encounter-group, patrol-route and search-zone settings. Allies automatically follow/regroup and use distinct temporary support positions during contact, with reachable waypoints and bottleneck wait/replan. Germans guard/patrol, search reachable authored points around the last observed target position for a bounded time, and reposition while alive. Rendering and physical simulation use Unreal and the acquired assets as supporting systems.

The MVP uses ordered intermediate objectives: reach rally point A, clear the assigned finite enemy group at area B, and reach end point C. Reach checks the living player, with allies following. ClearArea waits for its nonempty complete group roster to be registered and all members to be defeated; leaving the area does not count as being defeated. Player death during any playing stage causes failure. A full mission restart restores the configured roster, objective index, timers and group counters. The reports include the new game flowchart. Objective markers provide progression; checkpoint/save reload is outside the MVP.

We will survey connectivity, collision, sightlines, navigation and travel time in the editor before selecting actual locations, an alternate route, graph size and expected duration. Static cover, one player rifle and a packaged Windows build keep the initial implementation focused. We will test the full mission, objective order, group-counter correctness, ally catch-up and bottlenecks, sight loss, persistent actor state and each pillar's mechanism through repeatable comparisons. Any added NPCs or stages must pass the same tests and a measured performance check; infinite waves and automatic difficulty increases are outside the plan.

Please confirm whether this revised concept, scope and proposed technical depth are approved, and assign or confirm our mentor. The reports include the updated Assignment 1 concept and the Assignment 2 engineering plan.

Thank you for your guidance.

Best regards,

Yupu Guo (yg745, Group Leader)
Yuqi Pu (yp549)
Jingdi Wu (jw2046)

Attachments: `CS549_Assignment1_Proposal.pdf` and `CS549_Assignment2_Proposal.pdf`. Retain the actual response chain for the required approval and mentor evidence.
