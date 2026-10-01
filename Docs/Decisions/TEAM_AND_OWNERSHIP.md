# Team and ownership

| Member | NetID | Responsibility | Status |
|---|---|---|---|
| Yupu Guo | yg745 | Team leader; integration, collision/gunplay contracts and AI integration support | Leader confirmed; implementation split proposed |
| Yuqi Pu | yp549 | Animation/action integration; role and weapon compatibility | Proposed for kickoff confirmation |
| Jingdi Wu | jw2046 | Pathfinding/navigation, NPC AI and bounded environment setup | Proposed revised responsibility; confirm at kickoff |

Each member owns a small mechanism, its diagram/Blueprint entry point, a baseline, a counterexample, and recorded evidence. The leader may execute the critical path serially; the plan does not assume three equally experienced parallel developers.

## Handoffs

All three members must follow the [GitHub + SFTP synchronization manual](../../Assets/TEAM_SYNC_WORKFLOW.md) before development and at task/day end. GitHub carries code, small project files and asset manifests; SFTP carries large originals and changed asset versions. Confirm one named editor per binary before work; shared server write access is not an edit lock. Publish verified SFTP objects before the corresponding Git manifest, then hand off the Git revision, asset IDs, verification results and unresolved work. Yupu coordinates conflicting edits; do not automatically choose one person's binary over another's.

- Animation delivers action-state and reload-notify contracts for the selected rig/weapon pair.
- Collision/gunplay delivers a single authoritative shot/hit result and resettable health/ammo/objective state.
- Pathfinding/navigation delivers surveyed NavMesh coverage, reachable distinct destinations, reservations, one avoidance approach, bottleneck waiting and bounded MoveTo recovery. Compare independent versus coordinated movement. A tactical graph and A*/Dijkstra comparison are optional, only if implemented.
- NPC AI delivers the shared controller/tree, per-NPC configuration, ally follow/regroup and bounded enemy patrol/search behavior.
- Rendering, physical simulation and acquired models are supporting dependencies; the team still records configuration and performance evidence without claiming them as primary authored pillars.
- Everyone uses the same documented engine/asset versions and runs the later shared package; binary assets have one editor at a time.

Acquisition, historical checks, packaging, and demonstrations are shared responsibilities. Revisit ownership after the first compatibility session, without widening the agreed feature scope.
