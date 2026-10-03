# Assignment 3 MVP Implementation Version 2

**Latest 2 October execution limit:** Yupu requests navigation foundation only, then pause. Follow `PARIS_NAVIGATION_FOUNDATION_IMPLEMENTATION_V1.md`; do not automatically implement follow/patrol, decision/Behavior Tree, coordinator or faction interaction. The tree and both factions' interaction must first be jointly designed/reviewed. This supersedes continuous-execution wording below for the current work package, without dropping those eventual MVP requirements.

Corrected 2 October 2026 following Yupu's asset-first direction. Implement the Assignment 2 technical slice on the existing Paris environment, characters and motions. Minimal means fewer optional features, not replacement of the accepted asset foundation. Yupu has resumed development and authorized continuous execution, pausing only for genuinely human-required review/decisions. No unrun acceptance item is passed by this plan.

## Current state and cleanup boundary

Later resumed execution saved the actual-city setup/input and combat/HUD increments. Read `PARIS_CITY_GAMEPLAY_RESULT_20261002.md` and `PARIS_COMBAT_AND_HUD_RESULT_20261002.md`; Yupu's subsequent interactive review reported no problems, clearing the bounded input/usability human gate. Continue `PARIS_WINDOWS_PACKAGE_IMPLEMENTATION_V1.md`, not cosmetic refinement. A new narrow documented Editor-only UMG template helper was built after the historical cleanup below. It does not revive the abandoned route or add a runtime C++ dependency. Current seven native files remain unpublished drafts; broader milestone exits are open.

The standalone input/HUD laboratory route is withdrawn. Its generation/probe scripts and editor-bridge additions are removed; the bridge source and deployed binaries are restored to the pre-attempt version. The city remains the default editor/game map.

Cleanup is complete: the native laboratory packages, task-local builds/evidence/crash, abandoned scripts and residual Python caches are absent. The [completed cleanup record](ASSET_FIRST_CLEANUP_20261002.md) includes manual deletion and follow-up preservation checks. The abandoned attempt was never an accepted dependency or Catalog-selected release. Do not regenerate or continue it. Preserve the existing 28 earlier drafts and diagnostic snapshot, all vendor originals, accepted baselines and published releases.

Development is resumed on Yupu's direction. Follow [the city gameplay work package](PARIS_CITY_GAMEPLAY_IMPLEMENTATION_V1.md), verify Git/external asset state and ownership, and record actual survey results/exact new package identities before native writes.

## Scope and priorities

Use the verified France Liberation city, Allied/German character baselines and selected motions. Reuse locomotion, lifecycle and guarded simplified reload work; do not repeat completed asset diagnostics. Keep a visibly usable existing provisional WWII rifle. Record missing coherent FP kit, German rifle, contact and historical-configuration limitations; do not substitute a modern weapon or treat an empty-handed scene as rifle acceptance.

Freeze cosmetic work: face, fingers, magazine/bolt, advanced hand IK, texture polishing and scene beautification are deferred unless a defect blocks operation or required pillar evidence. Do not resume detailed character production. Start with one Allied player, two allies and three Germans using shared combatant logic. Survey the connected city before selecting routes/objectives; do not pre-impose one block or a video-length mission.

## Technology baseline

Follow presentation slide 5 and `Docs/Presentation/PRESENTATION_NOTES.md`: UE **5.8.2**, Blueprint gameplay, CharacterMovement, Animation Blueprints, IK Retargeter where needed, NavMesh/MoveTo, AIController, Behavior Trees, AI Perception, a small Blueprint squad coordinator, UMG and optional SaveGame. Enhanced Input is the bounded supplement already described in Proposal 2. Engine AutomationTool supplies Windows packaging. No runtime LLM or new external gameplay framework.

The existing ParisEditorBridge remains disabled-by-default and Editor-only. Any later authoring-tool change needs a documented need; generated gameplay uses normal Blueprint/engine runtime nodes and fresh-loads with the bridge disabled. No runtime bridge dependency or C++ gameplay shortcut.

## Milestones and exit evidence

| Milestone | Implementation | Exit evidence |
| --- | --- | --- |
| M0 Asset-backed readiness | Verify Git/assets/ownership and retained drafts; survey city connections, collision, sightlines, NavMesh and travel time; select mission setup; establish an early Paris Windows package/performance baseline | Actual surveyed locations, package result, settings/versions and limitations; no cosmetic-polish prerequisite |
| M1 Playable Paris loop | Existing characters/motions and rifle; input/camera, shots/damage, guarded reload, health/ammo/objective HUD, six combatants, objectives, win/fail/retry/full restart | Complete asset-backed city slice; three repeat runs with coherent HUD and no stale actions/objectives |
| M2 Four pillars | Animation interruption; camera/muzzle cover checks; distinct reachable destinations, waiting/recovery; shared BT with individual memory, ally support and bounded enemy search | Repeatable runtime cases; camera-only/two-query and independent/coordinated destination comparisons under matched conditions |
| M3 Performance and limits | Packaged normal route at 1080p, declared preset, three warmed runs, finite NPC stress scenario and second-machine run | FPS, mean/p95 frame times, CPU/GPU/memory, stalls, active-AI counts and observed limit; 60 FPS remains a measured target |
| M4 Submission freeze | Align source/assets/build, restoration instructions and credits; real-time video and progress report | 2–3 minute annotated demo with stress limit; 1–2 page PDF with Plan vs Reality, AI Utility and Roadmap; accessible build, video and public source links |

Packaging starts against Paris in M0 and repeats during M1. A fixture cannot satisfy playable-city/build acceptance. Private three-member asset sharing does not establish public bundled-build rights. Verify course prerequisites, mentor evidence and official deadline rather than inventing them.

## First work package: existing-city gameplay setup

Owner: Yupu (`yg745`). Source checkpoint before correction: `3ecd7bb`. Cleanup and user resumption are complete. Remaining prerequisites: affected editors closed, safely integrated source, current selected Catalog bytes verified, previous 28 drafts preserved, one binary owner and measured disk capacity. Do not wait for teammate restoration reports for local work; later second-machine acceptance remains required.

Storage: native Content has one physical writable home at `Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Content`; the active project aliases it. Keep immutable originals/releases separate. Never restore over ignored unfinished changes, copy the whole city or rename vendor packages on disk.

Planned team-owned additions belong under `/Game/ParisCombat/Maps`, `/Game/ParisCombat/Blueprints`, `/Game/ParisCombat/Input` and `/Game/ParisCombat/UI`. Record exact new package identities/dependency closure before writes. Choose the editor-supported gameplay-layer/entry method after inspecting the vendor map structure; do not assume a streaming layout. The setup must reference the existing city and accepted character/motion/weapon assets, not replace them with primitives. Preserve the original vendor map/external actors. Change global defaults/cook lists only after verifying an asset-backed Paris entry.

Order after resume:

1. Verify source, Catalog bytes, retained hashes and single-owner mounts. Survey overhead views, connected walkable routes, collision, sightlines, NavMesh and travel time. Record approach/objective/exit and an alternate route where supported.
2. Create the documented team-owned Paris gameplay setup. Configure one player, two allies and three Germans using existing meshes, locomotion/lifecycle and reload logic. Attach the provisional rifle; choose a usable bounded view without removing required assets to evade integration. Stop only for a genuinely unresolved human decision.
3. Connect move/look/aim/fire/reload and authoritative UMG state. Implement camera-intent/muzzle-path queries, one ammo decrement and at most one damage result per accepted discharge. Declare muzzle-inside-wall and faction-damage policy before testing. No timer-created ammo or fake-fire decrement.
4. Verify graph compilation, dependencies and bridge-disabled fresh load, then test actual input, rifle visibility, reload, obstruction, damage and HUD together in Paris game/PIE. Synthetic tests support, but do not establish, physical input/performance/full-loop acceptance.
5. Establish an early Windows package of this city setup and record settings, dependencies, failures and initial performance. Never package only a standalone laboratory or declare a complete mission from this stage.

Acceptance: required assets visible/usable in Paris; movement/camera, rifle attachment, reload, authoritative HUD and basic obstruction/damage pass recorded checks; bridge-disabled fresh load; actual Paris package result/limitations. Unrun/failed items stay Not run/Failed. This package is not full M0/M1 completion.

Failure/rollback: stop on hash/ownership conflict. Never overwrite earlier drafts, originals or immutable releases. Diagnose the smallest operational blocker on the real asset-backed setup. Roll back only task-owned editor changes and restore prior defaults if a new entry fails. Preserve unique valid work; no blanket restore or mirror deletion. Raw tests/builds stay ignored; Git stores code/config and verified metadata. Publication requires authorization and verified immutable remote bytes.

## Following work packages

Configure NavMesh/MoveTo, shared controllers/BT/perception, distinct support positions, waiting and bounded replanning. Connect finite registered groups and mission lifecycle: Reach checks the living player; Clear requires a nonempty fully registered group with zero living members. Test win/fail/full restart and stale events. Specify packages, storage changes, order, tests and rollback before each package.

Safe-boundary checkpoints are Should after the loop works. Retry restores the snapshot and rolls back later changes; without one it restarts. Saving must not implicitly refill, heal or revive. Expand finite rosters/stages only after full-route pacing, navigation and performance tests. No infinite waves, hidden engaged actors or replenished casualties.

Then prove all four pillars, compare baselines, measure normal/stress performance, test second-machine restoration and freeze Assignment 3 deliverables. Follow `ASSIGNMENT3_ACCEPTANCE.md`; diagnostics do not pass integrated requirements. Record actual AI utility/costs and disclose Assignment 2 deviations without treating disclosure as a waiver.
