# Paris Street Combat

A CS549 single-player FPS project using an existing Paris/European city environment. The proposed academic pillars are **Animation, Collision Detection, Pathfinding and Navigation, and NPC AI / Behavior Trees**. The encounter is fictionalized within the August 1944 liberation of Paris; the Normandy landing is background context only.

**Team:** Yupu Guo (yg745, leader), Yuqi Pu (yp549), Jingdi Wu (jw2046).

## Current baseline

**23 September proposal revision:** the current [two assignment reports](Docs/Proposal/README.md) and [detailed proposal](Docs/Proposal/PROJECT_PROPOSAL.md) specify an initial roster of one Allied player, two Allied NPCs and three German NPCs. Six is not a final population cap. They supersede the earlier three-pillar scope in the dated handoff, pipeline and technical-design snapshot. Rendering/physics support the four selected pillars; the revision is a plan, not completed gameplay or course approval.

The mission moves across a connected part of the existing city through ordered intermediate objectives: **Reach rally A → Clear assigned group B → Reach end C**. An Unreal map survey selects actual locations and any alternate route. Reach checks the living player; ClearArea waits for its nonempty finite roster to be fully registered and have zero living members. Player death causes failure; full restart restores the configured roster and mission state. Allies follow/regroup; enemies patrol, search around last observed targets and reposition. Individual route/search settings use shared AI code. Additional NPCs, finite groups and stages depend on full-mission pacing, navigation and performance tests.

The former one-block, fixed-duration, fixed-node-count and final-six assumptions are superseded. Both proposals connect pillars to concrete work and UE5 routes in a table, and include the [formal game flowchart](Docs/Proposal/Visuals/paris-mission-flowchart.svg) plus the regenerated [street concept](Docs/Proposal/Visuals/paris-six-character-concept.png). The concept uses both official gallery images as appearance references; the flowchart is generated in code from mission rules. Neither verifies vendor geography or implemented gameplay. Earlier text-only concepts remain provenance only. See the [visual records](Docs/Proposal/Visuals/README.md).

The team has approved the scope reset and an existing-assets-first production policy. This repository establishes the new proposal, technical design, development order, historical references, and selected gunplay reuse candidates. Detailed engine/gameplay validation is scheduled for later gates, not claimed as completed during this reset.

The former Normandy landing scope and all of its implementation plans are archived. AI-led from-scratch detailed character modeling is a rejected production route after the team's 38-iteration experiment. See [AGENTS.md](AGENTS.md) and the [scope decision](Docs/Decisions/SCOPE_RESET.md).

## Start here

Continuing in a new chat/window? Read [HANDOFF.md](HANDOFF.md) first for the complete project state, exact paths, remaining work and previous-session decisions.

| Document | Purpose |
|---|---|
| [Project proposal](Docs/Proposal/PROJECT_PROPOSAL.md) | PRD, priorities, four pillars, technical routes, MVP, and cuts |
| [Assignment 1 proposal](Docs/Proposal/CS549_Assignment1_Proposal.pdf) | Two-page concept, roster, pillar/work table, street mockup and game flowchart |
| [Assignment 2 proposal](Docs/Proposal/CS549_Assignment2_Proposal.pdf) | Two-page PRD, technical table, MVP and visuals; email proof is separate |
| [Editable proposals and version notes](Docs/Proposal/README.md) | Word/Markdown sources and superseded report status |
| [Development pipeline](DEVELOPMENT_PIPELINE.md) | Phase order, stop conditions, and deferred checks |
| [Technical design](Docs/Design/TECHNICAL_DESIGN.md) | System boundaries, shot/action contracts, evidence plan |
| [Asset inventory and restoration](Assets/README.md) | Existing city, reuse candidates, and missing dependencies |
| [GitHub + SFTP team workflow](Assets/TEAM_SYNC_WORKFLOW.md) | Mandatory start/end synchronization, large-asset versions, ownership and recovery |
| [Paris history](HistoricalReference/Paris1944/CONTEXT.md) | Timeline, unit constraints, and source links |
| [Submission status](Docs/Submission/STATUS.md) | Approval and instructor alignment still needed |
| [Full index](INDEX.md) | Directory and file navigation |

## Environment and source repository

Local workspace: `D:\0.Rutgers\CS549\Project-New`.

The working environment is `Unreal/ParisStreetCombat/WW2FranceLiberation.uproject`. Its primary city map is `/Game/WW2City/Maps/LV_Paris_WW2`. The project filename and vendor package paths are retained to reduce unnecessary asset-reference changes. Project association is 5.8; UE 5.8.2 is the team's installed baseline, with compatibility and packaged execution still awaiting the later checks.

The original vendor delivery remains in the local `WW2FranceLiberation---Version d20260630(UE5.6+)` directory. It is not a second active gameplay project. The organized working copy excludes generated caches from the original delivery.

**Code and small project files go to GitHub; large models/assets go to SFTP (decision: 27 September 2026).** The city content remains intentionally absent from GitHub. A fresh clone requires the correctly entitled external environment package and any versioned asset changes before opening the city. SFTP availability does not grant vendor redistribution rights. Follow the [team synchronization manual](Assets/TEAM_SYNC_WORKFLOW.md) before editing and at every end-of-day handoff. The missing soldier/weapon/action set remains a separate acquisition and compatibility task.

The LFS commands below restore existing tracked objects only; new large models and asset packages use SFTP plus Git-tracked manifests. Existing LFS history is not migrated by this decision.

```powershell
git lfs install
git clone https://github.com/hzgyp/CS549-Paris-Street-Combat.git
cd CS549-Paris-Street-Combat
git lfs pull
```

Restore the environment using the recorded asset version and original `Content/WW2City` and external-actor package layout. Opening, packaging, and performance measurement occur in pipeline Gate 1 and later. No game build is included in this planning baseline.

## Deliberate limits

One surveyed connected city mission, one player weapon, an initial configurable six-soldier roster, automatic ally follow/regroup, basic enemy patrol/guard/search behavior, ordered Reach/ClearArea objectives, fixed lighting, and full mission restart. An authored A* graph at real route decisions and shared behavior trees provide the navigation/AI contributions. Later finite groups are data-configured and must pass evaluation before inclusion. Defeated actors remain defeated across stages, and engaged actors are not hidden/despawned to meet an AI budget. Vehicle driving, dynamic weather, landing/water, complex squad commands, infinite waves, automatic difficulty increases, checkpoint/save reload, broad destruction, multiplayer, and large interiors are outside the baseline.

## Archive

The former repository is [CS549-Normandy-Sim](https://github.com/hzgyp/CS549-Normandy-Sim). The original local project remains at `D:\0.Rutgers\CS549\Project` as a preserved archive. Historical source files and selected gunplay candidates were copied with provenance so that archiving does not delete the original record.
