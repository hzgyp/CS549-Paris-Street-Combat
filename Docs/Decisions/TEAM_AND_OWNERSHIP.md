# Team and ownership

| Member | NetID | Responsibility | Status |
|---|---|---|---|
| Yupu Guo | yg745 | Team leader; integration and collision/gunplay contracts | Leader confirmed; implementation split proposed |
| Yuqi Pu | yp549 | Animation/action integration; role and weapon compatibility | Proposed for kickoff confirmation |
| Jingdi Wu | jw2046 | Environment, materials, rendering and bounded street selection | Existing environment responsibility retained |

Each member owns a small mechanism, its diagram/Blueprint entry point, a baseline, a counterexample, and recorded evidence. The leader may execute the critical path serially; the plan does not assume three equally experienced parallel developers.

## Handoffs

- Rendering delivers physical-surface mappings, bounded feedback assets and a performance capture recipe.
- Animation delivers action-state and reload-notify contracts for the selected rig/weapon pair.
- Collision/gunplay delivers a single authoritative shot/hit result and resettable health/ammo/objective state.
- Everyone uses the same documented engine/asset versions and runs the later shared package; binary assets have one editor at a time.

Acquisition, historical checks, packaging, and demonstrations are shared responsibilities. Revisit ownership after the first compatibility session, without widening the agreed feature scope.
