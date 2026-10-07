# Paris Street Combat

A CS549 single-player FPS project using an existing Paris/European city environment. The proposed academic pillars are **Animation, Collision Detection, Pathfinding and Navigation, and NPC AI / Behavior Trees**. The encounter is fictionalized within the August 1944 liberation of Paris; the Normandy landing is background context only.

**Team:** Yupu Guo (yg745, leader), Yuqi Pu (yp549), Jingdi Wu (jw2046).

## Current baseline

**Approved first-person selection, 5 October:** the saved map now uses the
human-approved V20 grip/holding display with persistent native auto-binding.
[Result](Docs/Development/FIRST_PERSON_FORMAL_V21_RESULT_20261005.md) /
[中文结果](Docs/Development/FIRST_PERSON_FORMAL_V21_RESULT_20261005_ZH.md).
Catalog selects `paris-native-playtest-20261005-fp-v20`:228 private files,
224 objects reused/four new (~2.84MiB), all authenticated SFTP readback verified.
Ordinary Python-disabled native entry, saved-map movement/one reload and startup
precheck pass. Source publication awaits commit/push; no teammate/Shipping/FPS
pass claimed. Hands are frozen; sleeves remain deferred. Older checkpoints below
are historical. Use the updated team restore guides once matching Git is available.

**Current native team playtest, 3 October:** the saved Paris map now includes the UE-controlled continuous-arm display. The private `paris-native-playtest-20261003-v1` release is selected by [Catalog](Assets/Sync/CATALOG.json); all 206 non-city dependencies and its manifest were downloaded over pinned-host SFTP and verified. Existing city bytes remain in their prior manifest. Follow [team restore and launch](Docs/Development/TEAM_PLAYTEST.md) / [中文试玩步骤](Docs/Development/TEAM_PLAYTEST_ZH.md). Use UE5.8.2; Python/ParisEditorBridge are disabled during play. This is a restore-ready local-tested source/asset release, not a new EXE or an actual second-machine pass. Historical checkpoints below are superseded where they disagree.

**First-person failure archive, 3 October:** the prior candidate failed human visual review and is retired. Read [the mandatory failure index](Failures/README.md) and [FP001 analysis](Failures/FP001-20261003-first-person-view/FAILURE_ANALYSIS.md). Its seven native assets and exclusive tooling/documentation are archived with hashes; saved V3 and the previous 40 files stay protected. Archival validation precedes a new COD WWII-based first-person implementation. No source/asset publication is implied.

The [first V2 static result](Docs/Development/FIRST_PERSON_PRESENTATION_REBUILD_RESULT_20261003.md) stopped its three declared rigid placements because all showed own-body obstruction. It is historical failed evidence; the later continuous-arm native release above is now selected.

**Latest aiming experiment, 2 October:** Yupu approved a bounded upper-body layer. The [result](Docs/Development/RIFLE_CROSSHAIR_ALIGNMENT_RESULT_20261002.md) records accurate barrel/crosshair convergence and a clean 15-case/62-assertion actual-city runtime-only combat repeat. Contact and FP arm framing remain unaccepted; the three drafts are [unselected](Assets/Integration/PLAYER_AIM_TRIAL_INVENTORY_20261002.json). The saved city remains V3 below, with unchanged source model/rig/motions/camera/NPCs. Human review substitutes only the live PIE player; it never saves the editor map. No new release, package, commit or push.

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

Latest display: [native continuous-arm result](Docs/Development/CONTINUOUS_ARMS_NATIVE_RESULT_20261003.md). The saved map hash is `2791b4a7f76b4b3d07f42286b6ad0156c3a185c2e3e795fa2446aaac0ad68519`; the active release contains its actual dependency closure, not every retained experiment in the 43-file local checkpoint. The original stride/model/fingers/actions/camera and ammo transactions remain protected. Selected combat passed 16 cases/66 assertions; ordinary `-game` with Python/bridge disabled completed 600 frames. Dedicated M1 reload contact, human smoothness and warmed/stress FPS remain open. Earlier rifle-only attachment inventories are historical and must not overwrite this map.

Retained navigation foundation and user AI pause boundary: [navigation result](Docs/Development/PARIS_NAVIGATION_FOUNDATION_RESULT_20261002.md). The team map contains saved bounds/Recast data under explicit supported-agent configuration. Clean fresh-load `fresh_v4` passed four ordinary Allied/German short/80 m moves, unreachable rejection and in-flight cancellation; post-navigation combat/HUD passed 15 cases/62 assertions. Its `CITY_NAVIGATION_DRAFT_INVENTORY_20261002.json` map hash predates the later grip increment and must not overwrite it. Development remains paused before joint decision/Behavior Tree and faction-interaction design; follow/patrol/AI are not implemented. The earlier Windows executable below predates both navigation/grip; this is not whole-city/avoidance/AI/mission/FPS/package acceptance.

On 2 October, existing-city setup/input and combat/HUD passed their bounded tests; Yupu reported no problems during interactive review. The private Windows Development build cooked/staged/archived successfully and its actual executable started the intended team map/GameMode at verified 1920x1080. Combat/HUD regression passed 15 cases/62 assertions. Unsaved real-city NavMesh and two ordinary Allied/German MoveTo trials also passed, without establishing saved navigation/shared AI/mission completion. See [package results](Docs/Development/PARIS_WINDOWS_PACKAGE_RESULT_20261002.md) and [navigation results](Docs/Development/PARIS_NAVIGATION_RESULT_20261002.md). Tested provisional controls: WASD, mouse look, left mouse Fire and R simplified reload.

**The current gameplay entry now has a verified private SFTP restoration release.** Git still contains no commercial/native asset bytes or executable. Use the selected city and `paris-gameplay-native-playtest` manifests together, restore exact paths and verify before launching; a clone alone is insufficient. One-time authors and old draft inventories are not restoration tools. Second-machine execution is assigned to teammates and remains unverified. Binary authoring remains reserved to `yg745` until explicitly coordinated; shared-account CRUD is not permission for concurrent saves.

On the verified owner workstation, [the packaging tool](Tools/Integration/build_paris_windows.ps1) and [startup probe](Tools/Integration/probe_paris_package_startup.ps1) describe the tested private build workflow and guard current dependencies. Full AI/objectives/retry, matched warmed mission/stress performance, second-machine/reviewer delivery and bundled-asset distribution rights remain open. Preserve vendor package identities; do not rename maps/packages on disk. No Assignment 3 MVP/course completion is claimed.

## Deliberate limits

One surveyed connected city mission, one player weapon, an initial configurable six-soldier roster, automatic ally follow/regroup, basic enemy patrol/guard/search, configurable objectives, fixed lighting and full mission restart. NavMesh/MoveTo with reachable distinct goals, avoidance, waiting and bounded replanning supplies the navigation baseline; custom tactical A* is optional. Should checkpoints require tested snapshot restoration. Later finite groups must pass evaluation before inclusion. Defeated actors persist during normal progression; engaged actors are not hidden/despawned to meet a budget. Vehicle driving, dynamic weather, landing/water, complex squad commands, infinite waves, automatic difficulty increases, broad destruction, multiplayer and large interiors remain excluded.

## Archive

The former repository is [CS549-Normandy-Sim](https://github.com/hzgyp/CS549-Normandy-Sim). The original local project remains at `D:\0.Rutgers\CS549\Project` as a preserved archive. Historical source files and selected gunplay candidates were copied with provenance so that archiving does not delete the original record.
