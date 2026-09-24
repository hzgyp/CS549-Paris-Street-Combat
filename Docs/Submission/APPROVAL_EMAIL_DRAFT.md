# Approval email draft

Prepared but not sent.

**To:** Course Instructor, Danrui, and Sen using verified course addresses

**Subject:** [CS 549] Project Approval Request - Group Paris Street Combat

Dear Professor, Danrui, and Sen,

We propose revising our Normandy landing concept to Paris Street Combat, a single-player squad mission through a connected part of the existing WW2 - France Liberation city, fictionalized during the August 1944 liberation period. We will reuse the environment and compatible licensed soldier/rifle assets, allowing us to focus on character interaction instead of ocean, beach, fortification and detailed character modeling. The initial MVP roster is six soldiers: one Allied player, two Allied NPCs and three German NPCs. Six is a starting configuration, not a final population limit. We may add NPCs and finite encounter groups after evaluating mission pacing, navigation and performance. Defeated soldiers remain defeated across objective stages until a full mission restart.

Our proposed pillars are Animation, Collision Detection, Pathfinding and Navigation, and NPC AI / Behavior Trees. We will integrate purchased motion clips with action/ammunition state, configure character/environment collision and obstructed gunfire, use Unreal NavMesh with authored destination assignment and navigation recovery, and implement perception-driven behavior with individual NPC state. A lightweight squad coordinator assigns roles and distinct support destinations. Patrol means on-foot waypoint movement. Rendering and physical simulation use Unreal and the purchased assets as supporting systems; a custom tactical A* layer is optional if it adds academic or gameplay value.

The MVP is a playable encounter across connected streets with basic health/ammo/objective UI and intermediate objectives. Reaching a location and clearing an assigned finite group are example objective types; the final sequence and geography remain open. We propose checkpoints at selected safe boundaries: retry restores the saved player/NPC/objective state, with a start-of-mission fallback and full restart option. Saving alone does not heal, refill or revive; resupply/reinforcement rules remain open. The reports include the updated general flowchart. The hardest feature is integrating UI and physical character/environment interactions in the city while keeping NPC movement and decisions coordinated as numbers grow.

We will survey connectivity, collision, sightlines, navigation and travel time in the editor before selecting actual locations, an alternate route, graph size and expected duration. Static cover, one player rifle and a packaged Windows build keep the initial implementation focused. We will test the full mission, objective order, group-counter correctness, ally catch-up and bottlenecks, sight loss, persistent actor state and each pillar's mechanism through repeatable comparisons. Any added NPCs or stages must pass the same tests and a measured performance check; infinite waves and automatic difficulty increases are outside the plan.

Please confirm whether this revised concept, scope and proposed technical depth are approved, and assign or confirm our mentor. The reports include the updated Assignment 1 concept and the Assignment 2 engineering plan.

Thank you for your guidance.

Best regards,

Yupu Guo (yg745, Group Leader)
Yuqi Pu (yp549)
Jingdi Wu (jw2046)

Attachments: `CS549_Assignment1_Proposal.pdf` and `CS549_Assignment2_Proposal.pdf`. Retain the actual response chain for the required approval and mentor evidence.
