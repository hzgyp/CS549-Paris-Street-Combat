# Paris Street Combat

**CS549 - Project specification and MVP definition**

**Team:** Yupu Guo (yg745, team leader), Yuqi Pu (yp549), Jingdi Wu (jw2046).

Two-page reports: [English submission version](CS549_Paris_Street_Combat_Proposal.pdf) and [Chinese review translation](CS549_Paris_Street_Combat_Proposal_CN.pdf). Both include the team panel and two environment reference views; [image provenance](Visuals/README.md) distinguishes supplier illustrations from team implementation results.

## 1. Project concept

We will build a compact single-player first-person combat encounter in a fictionalized Paris street during the liberation period in August 1944. Normandy provides historical background; no landing sequence is playable. Existing environment and compatible character/weapon assets provide the visual foundation. The team focuses on coherent interaction and explainable implementations of **Rendering, Animation, and Collision Detection**.

The experience follows one short loop: enter a bounded street, use corners and cover, engage a small enemy group, complete an objective, and restart. We will select the exact date, units and equipment from historical references before approving the final assets. We do not claim an exact recreation of a historical street or incident.

## 2. Product requirements

### Problem and audience

A convincing FPS depends on agreement between what the player sees, the weapon's animated state, and where a shot can physically travel. A high-quality environment alone does not solve those interaction problems. Our target audience is PC FPS players and course reviewers evaluating real-time graphics and interaction mechanisms.

### User stories

- As a player, I want to move and aim around street cover so that positioning affects the encounter.
- As a player, I want a wall in front of my muzzle to block my shot even when the crosshair sees past it, so that cover behaves consistently.
- As a player, I want firing and reloading to match weapon animation and ammunition state, so that repeated or interrupted actions remain predictable.
- As a player, I want recognizable surface-specific impact feedback so that I can understand what a shot hit.
- As a player, I want clear win/fail conditions and restart so that I can replay the encounter.
- As a reviewer, I want matched technical views and recorded comparisons so that I can distinguish team-authored behavior from supplied assets and engine capabilities.

### MoSCoW priorities

| Priority | Scope |
|---|---|
| Must | One bounded outdoor street encounter; one player weapon; movement, aim, fire, reload, damage, win/fail/reset; one enemy configuration with basic detection/attack behavior; reliable cover/shot collision; synchronized action/ammo state; bounded surface feedback; three pillar comparisons; packaged Windows build |
| Should | Crouch where compatible animation is available; minimal enemy movement; basic spatial audio; unobtrusive objective/health/ammo UI; an additional encounter segment within the same asset area after the MVP passes |
| Could | One additional feedback refinement or a second short approach, only after all Must items and packaging work |
| Won't | Playable Normandy landing; custom detailed character production; dynamic weather/day-night; ocean simulation; driving; complex allies/civilians; broad interiors; unrestricted destruction; multiplayer; open-world city; runtime LLM NPCs |

## 3. Technical specification

### Stack and boundaries

Windows desktop, Unreal Engine 5.8.x (installed working baseline 5.8.2), Blueprint-first gameplay, Unreal materials/Niagara, Animation Blueprints/Montages with retargeting when required, collision traces and Physical Materials, Enhanced Input, UMG, and simple engine-supported NPC behavior. Git and Git LFS track team-authored material. Blender is reserved for bounded adaptation of acquired assets rather than a new character-production pipeline.

The locally supplied WW2 - France Liberation environment is the starting asset dependency. Its vendor package is not the team's modeling contribution and is excluded from the source repository pending rights verification. Soldier characters and some promotional combat VFX are not supplied by that pack. Exact asset/engine compatibility is a future development check.

### Three primary contributions

| Pillar | Team-authored mechanism | Baseline and evidence |
|---|---|---|
| **Rendering** | Surface-driven impact selection, correct placement, reusable parameters and bounded feedback lifetime/count | Generic impact versus surface-aware feedback under identical view/shot conditions; GPU frame time and active feedback count |
| **Animation** | Move/aim/fire/reload state arbitration and ammunition changes synchronized to a guarded animation event | Timer-only reference versus action-event synchronization; repeated input, interrupted reload and hand/weapon alignment evidence |
| **Collision Detection** | Camera-intent query followed by muzzle-path obstruction query, with consistent hit and surface results | Camera-only reference versus two-stage query; wall/corner and near-cover cases, false hits/blocking and frame-rate consistency |

The engine supplies rendering, skeletal animation, collision queries and navigation. Purchased assets supply geometry, textures and selected motions. The team owns the integration rules, Blueprint mechanisms and controlled comparisons. AI/navigation remains supporting gameplay, not a fourth pillar. Technical depth will be aligned with the instructor/mentor.

### AI strategy

AI supports research, documentation, scripts, Blueprint assistance, debugging and evidence collection. No runtime AI service is required. The team has discontinued AI-led from-scratch detailed character production after its unsuccessful 38-iteration project experiment. Missing models will be addressed through compatible existing assets, limited adaptation, professional assistance or scope reduction.

### Performance constraints

Target: Windows, 1920 x 1080 at a declared quality preset, aiming for 60 FPS on Yupu Guo's i9-12900F / RTX 3080 10 GB / 32 GB desktop. This is an unmeasured target. Later evidence will record frame-time distribution, hitches and GPU memory on the fixed encounter and a second machine. Lighting, shadows, loaded map area and effects budgets will be adjusted to measured costs.

## 4. Narrow MVP

A 60-90-second playable street-corner encounter: the player uses one gun against a small group using one enemy configuration, interacts with solid cover, reloads, receives damage, reaches a clear success/failure state and restarts. Fixed lighting and a limited outdoor area constrain the content budget.

**Hardest feature:** keeping muzzle obstruction, hit feedback and weapon/ammunition animation consistent during close-cover combat and interrupted actions, using compatible acquired assets.

**Midterm proof plan:** a Windows package running outside the editor, a complete encounter and three resets, a fixed set of corner/reload cases, matched pillar comparisons and declared performance captures. A teammate will reproduce the run. These are future acceptance checks, not completed results.

The MVP excludes driving, allies, civilians, moving doors, weather, destruction, multiple weapons, broad interiors and extra street segments. New features must not displace core interaction correctness.

## 5. Delivery and collaboration

Yupu Guo leads integration and the proposed collision/gunplay work; Jingdi Wu continues environment/rendering ownership; Yuqi Pu is proposed for animation/action integration. Each member maintains one explainable mechanism and its evidence. The full development order and dependencies are in DEVELOPMENT_PIPELINE.md and Docs/Design/TECHNICAL_DESIGN.md.

The final demonstration will show a short encounter, repeatable technical comparisons, the boundaries between acquired assets and team work, and limitations. The late-November final target is a team planning assumption pending the official course schedule. Assignment 2 requires the compact report plus actual concept/pillar approval and mentor-assignment email proof; the new setting must be communicated in that approval chain.

## References

- [WW2 - France Liberation, Meshingun Studio](https://www.fab.com/listings/dae418da-1969-444a-821c-c1f30a3f21b6)
- [The Liberation of Paris, Musee de la Liberation](https://www.museeliberation-leclerc-moulin.paris.fr/en/museum/la-liberation-de-paris)
- [Paris municipal historical event map](https://www.paris.fr/en/pages/relive-the-liberation-of-paris-through-an-interactive-map-36122)
- Local assignment authority: Course/Assignments/Assignment 2.docx.
