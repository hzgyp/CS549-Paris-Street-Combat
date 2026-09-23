# Paris Street Combat

A CS549 single-player FPS project using an existing Paris/European city environment. The academic pillars are **Rendering, Animation, and Collision Detection**. The encounter is fictionalized within the August 1944 liberation of Paris; the Normandy landing is background context only.

**Team:** Yupu Guo (yg745, leader), Yuqi Pu (yp549), Jingdi Wu (jw2046).

## Current baseline

The team has approved the scope reset and an existing-assets-first production policy. This repository establishes the new proposal, technical design, development order, historical references, and selected gunplay reuse candidates. Detailed engine/gameplay validation is scheduled for later gates, not claimed as completed during this reset.

The former Normandy landing scope and all of its implementation plans are archived. AI-led from-scratch detailed character modeling is a rejected production route after the team's 38-iteration experiment. See [AGENTS.md](AGENTS.md) and the [scope decision](Docs/Decisions/SCOPE_RESET.md).

## Start here

Continuing in a new chat/window? Read [HANDOFF.md](HANDOFF.md) first for the complete project state, exact paths, remaining work and previous-session decisions.

| Document | Purpose |
|---|---|
| [Project proposal](Docs/Proposal/PROJECT_PROPOSAL.md) | PRD, priorities, three pillars, MVP, and cuts |
| [Two-page proposal PDF](Docs/Proposal/CS549_Paris_Street_Combat_Proposal.pdf) | Compact Assignment 2 report; email proof is separate |
| [Chinese proposal PDF](Docs/Proposal/CS549_Paris_Street_Combat_Proposal_CN.pdf) | Matching two-page translation for team review |
| [Development pipeline](DEVELOPMENT_PIPELINE.md) | Phase order, stop conditions, and deferred checks |
| [Technical design](Docs/Design/TECHNICAL_DESIGN.md) | System boundaries, shot/action contracts, evidence plan |
| [Asset inventory and restoration](Assets/README.md) | Existing city, reuse candidates, and missing dependencies |
| [Paris history](HistoricalReference/Paris1944/CONTEXT.md) | Timeline, unit constraints, and source links |
| [Submission status](Docs/Submission/STATUS.md) | Approval and instructor alignment still needed |
| [Full index](INDEX.md) | Directory and file navigation |

## Environment and source repository

Local workspace: `D:\0.Rutgers\CS549\Project-New`.

The working environment is `Unreal/ParisStreetCombat/WW2FranceLiberation.uproject`. Its primary city map is `/Game/WW2City/Maps/LV_Paris_WW2`. The project filename and vendor package paths are retained to reduce unnecessary asset-reference changes. Project association is 5.8; UE 5.8.2 is the team's installed baseline, with compatibility and packaged execution still awaiting the later checks.

The original vendor delivery remains in the local `WW2FranceLiberation---Version d20260630(UE5.6+)` directory. It is not a second active gameplay project. The organized working copy excludes generated caches from the original delivery.

**The city content is local-only and intentionally absent from GitHub.** A fresh clone contains the project descriptor/configuration, our documents and selected reference assets, but requires the correctly entitled environment package before opening the city. The missing soldier/weapon/action set is a separate acquisition and compatibility task. See Assets/README.md; do not assume a blank clone is a packaged game.

```powershell
git lfs install
git clone https://github.com/hzgyp/CS549-Paris-Street-Combat.git
cd CS549-Paris-Street-Combat
git lfs pull
```

Restore the environment using the recorded asset version and original `Content/WW2City` and external-actor package layout. Opening, packaging, and performance measurement occur in pipeline Gate 1 and later. No game build is included in this planning baseline.

## Deliberate limits

One small street area, one player weapon, one enemy configuration, basic combat behavior, one objective, fixed lighting, and reliable restart. AI/navigation support this experience. Vehicle driving, dynamic weather, landing/water, complex allied squads, broad destruction, multiplayer, and large interiors are outside the baseline.

## Archive

The former repository is [CS549-Normandy-Sim](https://github.com/hzgyp/CS549-Normandy-Sim). The original local project remains at `D:\0.Rutgers\CS549\Project` as a preserved archive. Historical source files and selected gunplay candidates were copied with provenance so that archiving does not delete the original record.
