# Paris Street Combat

A CS549 single-player FPS project using an existing Paris/European city environment. The proposed academic pillars are **Animation, Collision Detection, Pathfinding and Navigation, and NPC AI / Behavior Trees**. The encounter is fictionalized within the August 1944 liberation of Paris; the Normandy landing is background context only.

**Team:** Yupu Guo (yg745, leader), Yuqi Pu (yp549), Jingdi Wu (jw2046).

## Current baseline

**Current development direction, 30 September 2026:** implement [Assignment 3 goal version 1](Docs/Development/ASSIGNMENT3_GOAL_V1.md), using its [acceptance checklist](Docs/Development/ASSIGNMENT3_ACCEPTANCE.md) and the current [Assignment 2 report](Docs/Proposal/CS549_Assignment2_Proposal.md). Begin with one Allied player, two Allied NPCs and three German NPCs; six is not a final population cap. All four pillars remain. Concept/pillar approval is evidenced in [submission status](Docs/Submission/STATUS.md); Assignment 2 completion/approval and mentor evidence still need confirmation. No running MVP or performance pass is claimed.

The mission crosses a surveyed connected part of the city with configurable intermediate objectives. Reach A -> Clear B -> Reach C is an example, not a fixed route/order. Reach checks the living player; ClearArea waits for its nonempty finite roster to be fully registered and have zero living members. Player death offers retry from a valid checkpoint if implemented, otherwise from the initial state; full new-mission restart remains available. Checkpoints at safe boundaries are a Should feature, without automatic healing/refill/revival. Allies follow/regroup; enemies patrol/search using separate per-NPC state. Later finite groups require pacing, navigation and performance tests.

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
| [Assignment 3 goal version 1](Docs/Development/ASSIGNMENT3_GOAL_V1.md) | Current running-MVP scope, work order, course deliverables and open prerequisites |
| [Assignment 3 acceptance](Docs/Development/ASSIGNMENT3_ACCEPTANCE.md) | Repeatable gameplay, performance, stress and delivery checks with evidence status |
| [Asset inventory and restoration](Assets/README.md) | Existing city, reuse candidates, and missing dependencies |
| [GitHub + SFTP team workflow](Assets/TEAM_SYNC_WORKFLOW.md) | Mandatory start/end synchronization, large-asset versions, ownership and recovery |
| [Paris history](HistoricalReference/Paris1944/CONTEXT.md) | Timeline, unit constraints, and source links |
| [Submission status](Docs/Submission/STATUS.md) | Approval and instructor alignment still needed |
| [Full index](INDEX.md) | Directory and file navigation |

## Environment and source repository

Local workspace: `D:\0.Rutgers\CS549\Project-New`.

The working environment is `Unreal/ParisStreetCombat/WW2FranceLiberation.uproject`. The original city/editor entry is `/Game/WW2City/Maps/LV_Paris_WW2`; the current local gameplay/packaging entry is `/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1`. The project filename and vendor package paths remain unchanged. The bounded integration/build tests below used UE 5.8.2; full mission/compatibility/performance acceptance remains open.

The original vendor delivery remains in the local `WW2FranceLiberation---Version d20260630(UE5.6+)` directory. It is not a second active gameplay project. The organized working copy excludes generated caches from the original delivery.

**Git stores code, Markdown/native diagrams, configuration and asset hash records; private SFTP stores model/historical/document/raster bytes.** On 30 September, the user authorized deleting and recreating this same-name repository after the history rewrite alone left old Git/LFS content retrievable. Cleaned source history was restored, a fresh clone verified, all 29 inspected old LFS objects became unavailable, and source visibility is now public. See [publication status](Assets/Sync/PUBLICATION_STATUS.json) and [publication review](Docs/Submission/PUBLICATION_REVIEW.md). A clone needs entitled external dependencies restored before opening the city. The [active catalog](Assets/Sync/CATALOG.json) pins exact manifests and restore paths. Public source access does not grant SFTP or vendor rights. The soldier/weapon/action set remains a separate compatibility task.

Old asset-bearing clones must not be merged or pushed after the history rewrite. Preserve unfinished work and clone into a new folder; use the [rejoin procedure](Assets/TEAM_SYNC_WORKFLOW.md#8-rejoin-after-the-authorized-history-rewrite). Keep private old Git/LFS backups outside source publication.

```powershell
git clone https://github.com/hzgyp/CS549-Paris-Street-Combat.git
cd CS549-Paris-Street-Combat
powershell -ExecutionPolicy Bypass -File Tools/configure_git_hooks.ps1
python Tools/check_asset_storage.py --git --history
```

Use Python 3.10+; the hook setup selects the bundled Codex runtime when available, or accepts `-PythonExecutable` with your actual interpreter path. Obtain SFTP credentials privately from Yupu. Restore the catalog's files to staging, verify SHA-256/size, preserve unsynchronized local changes and then place files at exact paths with affected editors closed. Run `python Tools/check_asset_storage.py --local` (or use the configured bundled runtime). PDF/DOCX/PPTX/images linked by documents also require this external restoration; their Markdown/build sources remain here. Unresolved-rights source references are local-only, not downloadable SFTP assets.

## Build and run status

On 2 October, existing-city setup/input and combat/HUD passed their bounded tests; Yupu reported no problems during interactive review. The private Windows Development build cooked/staged/archived successfully and its actual executable started the intended team map/GameMode at verified 1920x1080. Combat/HUD regression passed 15 cases/62 assertions. Unsaved real-city NavMesh and two ordinary Allied/German MoveTo trials also passed, without establishing saved navigation/shared AI/mission completion. See [package results](Docs/Development/PARIS_WINDOWS_PACKAGE_RESULT_20261002.md) and [navigation results](Docs/Development/PARIS_NAVIGATION_RESULT_20261002.md). Tested provisional controls: WASD, mouse look, left mouse Fire and R simplified reload.

**This is a source/configuration/documentation checkpoint, not a reproducible gameplay release.** Git contains scripts and draft hashes, not the seven new city/combat/HUD native packages or the private executable. `CITY_PACKAGE_DRAFT_INVENTORY_20261002.json` records unpublished workspace bytes, not an active restoration manifest. The active catalog restores the accepted external city/character/motion baselines, but not this new team gameplay entry. A fresh clone plus catalog restoration alone cannot run/package the new default entry yet. Do not restore old draft/map hashes over newer work, infer missing packages from `latest`, or treat one-time authoring scripts as a complete replay workflow. Wait for an explicitly verified, Catalog-selected gameplay handoff before teammate restoration of this increment. Existing local drafts stay reserved to `yg745`.

On the verified owner workstation, [the packaging tool](Tools/Integration/build_paris_windows.ps1) and [startup probe](Tools/Integration/probe_paris_package_startup.ps1) describe the tested private build workflow and guard current dependencies. Full AI/objectives/retry, matched warmed mission/stress performance, second-machine/reviewer delivery and bundled-asset distribution rights remain open. Preserve vendor package identities; do not rename maps/packages on disk. No Assignment 3 MVP/course completion is claimed.

## Deliberate limits

One surveyed connected city mission, one player weapon, an initial configurable six-soldier roster, automatic ally follow/regroup, basic enemy patrol/guard/search, configurable objectives, fixed lighting and full mission restart. NavMesh/MoveTo with reachable distinct goals, avoidance, waiting and bounded replanning supplies the navigation baseline; custom tactical A* is optional. Should checkpoints require tested snapshot restoration. Later finite groups must pass evaluation before inclusion. Defeated actors persist during normal progression; engaged actors are not hidden/despawned to meet a budget. Vehicle driving, dynamic weather, landing/water, complex squad commands, infinite waves, automatic difficulty increases, broad destruction, multiplayer and large interiors remain excluded.

## Archive

The former repository is [CS549-Normandy-Sim](https://github.com/hzgyp/CS549-Normandy-Sim). The original local project remains at `D:\0.Rutgers\CS549\Project` as a preserved archive. Historical source files and selected gunplay candidates were copied with provenance so that archiving does not delete the original record.
