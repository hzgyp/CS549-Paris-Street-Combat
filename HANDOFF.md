# Paris Street Combat - new-session handoff

**2 October source-publication follow-up:** Yupu authorized committing/pushing the accumulated source/configuration/documents/hash records and requested a Chinese review of the next high-level workflow before more implementation. Asset bytes remain SFTP-only. The proposed emphasis is the integrated playable loop, not more cosmetic/model/animation refinement. Await his workflow confirmation before starting the next work package; Git remote success is verified separately, not inferred from this note. Earlier no-commit statements below describe the validation checkpoints when written.

**Latest checkpoint, 2 October 2026:** Read `Docs/Development/WEAPON_BASELINE_AND_SIMPLIFIED_RELOAD_V1.md` and `WEAPON_BASELINE_AND_RELOAD_RESULT_20261002.md`. D059 fifteen generic source motions passed 465 pose samples/90 reviewed views, 33 UE5.8.2 resaves and minimal fresh load. **35 files / 18,974,540 bytes** are now CATALOG-selected as `rifle-pro-mocap-ue582-selected`, with bundled ACLPlugin required. Original D059 and the single writable lab were moved once to SFTP; elevation repaired shared Modify, root ACL unchanged. Both manifests/all 35 files/original sample and workspace CRUD passed actual SFTP verification. Removed only 753 proven-identical discovery files (135,629,202 bytes); retained originals/evidence/history, old lab Content mount is a writable-workspace junction. All 2,420 original deliveries and 25 prior gameplay drafts remain hash-identical. New simplified-reload shared/player/NPC Blueprints passed **18 groups/432 assertions**, three bridge-disabled fresh loads and reviewed `Views_v2` static poses. Private diagnostic snapshot freezes all **28 native drafts / 12,743,253 bytes** as verified immutable objects, with `Assets/Integration/RELOAD_DRAFT_SNAPSHOT_20261002.json` (not CATALOG-selected production/automatic restore authority). New workspace files passed actual SFTP reads and CRUD. Preserve failures: first pure-node authoring error, v20 without editor binary, snake-case fresh harness failure, stale Views_v1; accepted evidence is author_v2, probe_30/60/120_v1, fresh_v2 and Views_v2. All commandlets exited. Do not rerun occupied publication/author/snapshot identities. No Git staging/commit/push. Next bounded P4 work updates its implementation document, binds actual input/HUD, attaches/tests the provisional world rifle, and implements trace/obstruction/damage. FP contact/history, German rifle, public-build rights, city/input/performance/package gates remain open; no new purchase or character generation.

**Latest selective weapon-intake checkpoint, 1 October 2026:** read `Docs/Development/WEAPON_ASSET_VALIDATION_V1.md` and `WEAPON_ASSET_VALIDATION_RESULT_20261001.md`. Yupu supplied all three deliveries and confirmed private original/derivative sharing among three members. Full intake preservation verified 2,420 files / 29,207,654,510 bytes, zero changes; all 25 prior gameplay drafts still match hashes. Physical local discovery lab is `Assets/LocalWorking/Validation/UE582/2026-10-01-weapons-v1/`, with 1,076 actual UE5.8.2 asset loads, two preserved diagnostic capture iterations and Blender5.2.2 fresh FBX metrics. Four collection catalogs were inspected without extraction; Rifle entries substantially overlap existing/direct deliveries (CRC/size screen only). Dedicated arm geometry is a candidate, not an accepted FP kit: materially different reference rotations, failed tested FP framing, modern sleeves/gloves, no matching weapon-specific FP reload and no German rifle. The human WWII weapon-kit versus explicitly simplified diagnostic presentation choice remains before production P4; do not automatically choose a modern gun, certify M1 reload, or rerun/restage occupied evidence. New candidates remain LocalWorking/unpublished. `Assets/Integration/WEAPON_INTAKE_DIAGNOSTICS_20261001.json` is hash-only diagnostics, not active Catalog/restore authority. No saved adaptation/native-release resave, SFTP publication, asset cleanup, live asset edit, commit or push; all probe commandlets exited. Earlier empty-intake/P3 absence snapshots are superseded only where these verified findings say so.

**Latest intake-flow clarification, 1 October 2026:** Yupu requires new original model/animation deliveries to physically start in `Assets/LocalWorking/Intake/`, with processing/testing in LocalWorking. After the defined asset checks and sharing-rights gate pass, migrate preserved originals and usable dependency-complete outputs into the appropriate SFTP baseline/workspace/version locations, verify retained sizes/SHA-256 and final SFTP bytes, then remove only verified redundant LocalWorking material. Keep a checked junction only if tools/editor paths require it; no alias by default. This supersedes the blanket physical-SFTP-home instruction for new intake; already published city/character assets and runtime aliases stay in place. `AGENTS.md`, `Assets/TEAM_SYNC_WORKFLOW.md` Section 6 and `Assets/README.md` now reflect this rule. The new three-folder weapon/animation intake is physically at `Assets/LocalWorking/Intake/2026-10-01/`, not a junction: the prior private SFTP intake was same-volume moved back after deleting only its exact verified alias. Its sole instruction file matched before/after SHA-256/size; three asset destinations were empty at that check, no model bytes were deleted, and the prior SFTP intake path no longer exists. No asset import/acceptance, sharing, active catalog change, commit or push was performed. Existing unpublished gameplay drafts remain untouched.

**Latest directional/lifecycle and P3 checkpoint, 1 October 2026:** read `Docs/Development/CHARACTER_LOCOMOTION_LIFECYCLE_RESULT_20261001.md` and `WEAPON_CAPABILITY_REVIEW_20261001.md` in the same directory. German persistent float was traced to root/pelvis translation retarget modes and corrected on separate native drafts; directional gait and measured stride-rate copies are saved. Both animation profiles passed twelve fixed-step numeric cases each (42,000 total poses); this is not measured FPS/contact/PIE/package acceptance. Shared Blueprint Ready/Dead damage/reset checks passed twelve cycle checks across two profiles; bridge-disabled fresh reopening passed sixteen new packages and six stride-scene Characters. Transition penetration/sliding, city/input/performance/package checks remain unresolved. All 25 local drafts (12,181,561 bytes) are inventoried in `Assets/Integration/LOCAL_DRAFT_INVENTORY_20261001.json`, explicitly not a published/restorable release. P3 found no accepted coherent FP rifle/reload kit; the tested eye-level full-body camera is occluded. Yupu requires continuous work except human-required gates: next is his choice of a coherent weapon/FP kit or explicit temporary reduced presentation before P4, not automatic procurement or detailed character production. No new immutable release, Catalog/allowlist change, staging, commit or push. Preserve existing drafts and aliases; old checkpoints below are superseded where contradicted.

**Latest movement checkpoint, 1 October 2026:** read `Docs/Development/CHARACTER_MOVEMENT_RESULT_20261001.md`. Shared native-Character Blueprint shell/player/NPC, two velocity-driven AnimBPs/BlendSpaces and a six-Character diagnostic map are saved as eight unpublished local drafts (313,338 bytes), solely in the existing SFTP runtime workspace. Fresh load with Editor-only ParisEditorBridge disabled passed. Twelve fixed-step numerical movement/braking/wall cases passed; this is not PIE/input-device/performance/package acceptance. German visible idle/walk geometry still floats ~11–19 cm; speed-only locomotion uses the wrong gait for lateral movement. Next is bounded retarget/contact/directional diagnosis and repair under the revised implementation plan, then shared lifecycle and weapon feasibility. Do not lower the actor arbitrarily, resave vendor skeletons, rerun generation/resume over current drafts, or repeat one-time relocation. Earlier failed harness/capture evidence is preserved. All commandlets exited; no new immutable release/catalog/allowlist/commit/push. Prior checkpoints below are historical snapshots.

**Current runtime-integration checkpoint, 1 October 2026:** Yupu authorized starting the implementation plan. P0 is complete: 15,850 city files plus 540 native character packages were same-volume moved with full before/after SHA-256/size checks into `Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Content/`; active Content and four lab mount paths are verified junction aliases. Originals/releases remain unchanged, root ACL remains protected and the new workspace passed actual local shared-account SFTP CRUD. P1 fresh active-project UE 5.8.2 load passed 540/540 with zero errors and four persisted eye bindings; city World object loaded, not a city streaming/rendering/NavMesh/gameplay pass. Read `Docs/Development/CHARACTER_INTEGRATION_RESULT_20261001.md` for dated evidence and P2 status. Yupu owns binary edits across both aliases; never open lab/game as simultaneous writers. No new immutable release, catalog rewrite or commit/push is implied.

**P2 follow-up, same session:** six SkeletalMeshActor previews were saved/fresh-reopened with all mesh/action defaults retained; 84 sampled native poses were finite with key-action variation. Controlled group textures and eight separately filled reference-pose face views were reviewed. Some feet are elevated in animation frames; grounded movement/capsule contact and full P2 remain unaccepted. Initial dark head screenshots are preserved. The sole new native package is the ignored local diagnostic map `/Game/ParisCombat/Tests/Integration/P2_CharacterPreview_20261001` (not published). Next: shared combatant Blueprint/configuration and grounded movement, followed by weapon/view/reload feasibility. No playable character/AI/combat, city-lighting, performance or packaged-build pass is claimed. See runtime `work_state.md` and the dated result before editing; do not rerun one-time storage migration.

**Current implementation-document checkpoint, 1 October 2026:** asset publication is committed/pushed at `37de536`. Yupu chose to continue this conversation and requires implementation documentation before action. Read `Docs/Development/CHARACTER_AND_WEAPON_IMPLEMENTATION_V1.md` for local readiness, single physical runtime storage, character dependency/presentation integration and weapon/action contracts with acceptance/failure gates. It covers part of Gate 1 and early Gate 2, not a complete mission. Teammates handle their own restoration; do not wait for their reports to start Yupu's local work, but still verify local dependencies and retain later second-machine checks. This document-preparation task changed no Unreal assets and did not begin runtime integration. Next checkpoint is P0/P1, not a new modeling experiment or automatic asset purchase.

**Current publication checkpoint, 1 October 2026:** Yupu explicitly confirmed new-bundle private three-member original/derivative sharing. `character-20261001-v1` is published and final-server verified: 590 original files plus 721 integration-baseline files. Original intake was moved (not copied) to `Assets/LocalShared/SFTP/baselines/character-original-intake/character-20261001-v1/`; both former intake paths resolve through junction aliases. Repair workspace remains the sole writable lab and is now shared-account Modify. Root ACL unchanged. Actual SFTP downloaded all four release manifests and UE/PNG/FBX/Blender samples with matching SHA-256; workspace create/overwrite/rename/read/delete passed and probes were removed. `Assets/Sync/CATALOG.json` now selects four additional manifests; use `Assets/Sync/README.md` and `CHARACTER_PUBLICATION_STATUS.json`. The dated private/pending notes below are superseded. No teammate restoration, historical/gameplay/performance/package acceptance or later 1/2 integration work is claimed. Source/docs/tools and exact hashes are the Git publication; inspect the actual commit for its status. Do not publish model bytes or private credentials.

**Shared-permission follow-up, 1 October 2026:** Yupu requested all-member CRUD in published SFTP areas, then matching Git commit/push before later character/weapon integration. Actual local SFTP create/overwrite/rename/read/delete tests passed in baselines, objects, incoming and releases; four downloaded probes matched SHA-256 and remote probes were removed without changing existing assets. The permission-tool source now avoids blanket exposure of private/unknown directories; it has not been run to change ACLs. The new German/US Paratrooper/Rifle Animset Pro sharing license record is still missing. The CRUD instruction is not license evidence. New character publication/catalog changes and Git commit/push remain pending that confirmation; no later integration was started.

**Latest checkpoint, 1 October 2026:** Yupu ordered recorded character-defect repair and permitted SFTP publication before Paris character/weapon integration, with one physical asset storage home. The 590-file character intake and sole UE/Blender lab were moved, file-by-file SHA-256/size verified, into owner-private `Assets/LocalShared/SFTP/workspaces/yg745/character-intake-20260930/` and `character-ue582-v1/`. Old `Assets/LocalWorking` intake/lab paths are junction aliases. Root ACL stayed unchanged; the collaboration SFTP account cannot read this private workspace. It is not a shared release. Repairs cover persisted simple-PBR eye bindings on four adapted meshes, normalized German exchange weights, portable texture paths and seven 30 fps exchange clips with native-second durations. Fresh UE loads 540 non-diagnostic dependency/adaptation packages; all headers are UE 5.8.2. Final native regression: 300 finite poses, 80 views, zero test errors; 24 final body/head captures. Repaired exchange: 12 meshes, seven actions and 12 reopened editable sources, no missing file images. All 590 originals match their recorded bytes. Removed 150.25 MiB of superseded task-generated exports/diagnostic scenes and regenerable lab caches, not originals/history/city files. Read `Assets/CHARACTER_COMPATIBILITY_AND_REPAIR.md` and its canonical `Evidence/Repair20261001/repair_handoff.json`. New-bundle three-member sharing confirmation remains pending; do not publish to the active catalog, grant source access or claim SFTP synchronization. No Git commit/push or gameplay integration occurred. Existing city layout outside this character batch remains unreconciled with the new physical-storage policy. Blender 4.5 was uninstalled in the prior task; the active test runtime is 5.2.2 LTS, superseding the older availability note below.

**Verified migration/publication outcome, 30 September 2026:** all 15,927 selected asset/document files were source/server SHA-256 and size-verified; the city was unchanged, 77 other files are selected by private SFTP manifests, and 22 unresolved-rights originals remain local-only. After the rewrite-only check found retained GitHub bytes, Yupu explicitly authorized deleting/recreating the same-name repository. It is now public, with cleaned main history restored and a fresh clone audited (2.66 MiB source pack before final status update). All ten original old Git commits, a sampled removed raw blob and all 29 inspected orphaned LFS objects are inaccessible through the new repository. Read `Assets/Sync/PUBLICATION_STATUS.json`. Local originals, the private SFTP store and private Git/LFS/source backups are retained. Both team write invitations need acceptance after recreation. Never undo the cleaned history by pushing an old clone.

**Latest storage/publication instruction, 30 September 2026:** Yupu rejected a separate public repository and authorized moving previously uploaded asset/history/document bytes to private SFTP, removing their Git/LFS history in this same repository, retaining code/docs/config/hash metadata, and making source public only after verification. This supersedes older preserve-LFS/private-repo planning notes. `Assets/Sync/CATALOG.json` selects current authoritative manifests; `PUBLICATION_STATUS.json` and `Docs/Submission/PUBLICATION_REVIEW.md` record actual results. Source and local assets were backed up; never merge an old asset-bearing clone into cleaned history. Follow the manual's rejoin procedure and configure source guards. Goal V1 is now a Chinese review version with synchronized `ASSIGNMENT3_GOAL_V1_EN.md`; all implementation tests remain unrun. The character experiment remains stopped and local-only. Source visibility does not grant vendor/SFTP rights or establish a working game.

**Current checkpoint, 30 September 2026:** development now targets [Assignment 3 goal version 1](Docs/Development/ASSIGNMENT3_GOAL_V1.md) and its [acceptance checklist](Docs/Development/ASSIGNMENT3_ACCEPTANCE.md), based on `Docs/Assignment 3_ MVP Development.docx`. Active pipeline/design/README/ownership records were corrected: NavMesh/MoveTo is the baseline, custom tactical A* is optional, safe-boundary checkpoints are Should, and Reach/Clear sequences are examples selected after the city survey. Both original and active descriptors associate with UE5.8; UE5.8.2 remains a recorded baseline awaiting compatibility/package validation. Blender 5.2.2 LTS was installed and background-start verified on 30 September; 4.5/configuration remain available. No character production was resumed.

Paris concept/pillar approval is evidenced by the user's 28 September email screenshot; mentor assignment and Assignment 2 completion/approval are not established by that screenshot. SFTP city/historical baselines and the three-member sharing attestation are recorded in `Assets/Sync/README.md` and `RIGHTS.md`; the older pending-rights/catalog notes below are historical. Assignment 3 requires public GitHub source; the subsequent same-repository migration/publication authorization and actual publication-status file govern this requirement. Never expose vendor content or private correspondence. A running MVP, map survey, compatibility tests, performance pass and package remain unverified. The next implementation session starts with safe Git/external-asset synchronization and Gate 1. Prior report/source edits are preserved in the migration; unrelated permission scripts and stopped experiments remain local. No course submission is made by this task.

**Synchronization decision — 27 September 2026:** SFTP is working according to the user; the local `sshd` service was observed running and listening on TCP 22222. The selected workflow is **GitHub for code/small project files, SFTP for large models/assets**, with Git-tracked hashes and version locations. Read [Assets/TEAM_SYNC_WORKFLOW.md](Assets/TEAM_SYNC_WORKFLOW.md) before editing and at day end. Preserve local asset edits, upload/verify changed files before publishing manifests, and keep one editor per binary. Existing LFS history remains compatible; new large assets do not go into LFS. This supersedes the older undecided Git/LFS status below. No complete SFTP asset catalog, external-client restoration test or vendor sharing permission is established by this note.

**Latest user correction — 23 September 2026:** simplify the presentation and keep technical terminology explanations in chat. Slide 2 introduces only France Liberation. The hardest work is integrating UI, character/environment interactions and combat into the city, then coordinating NPC movement and decisions as groups grow. The user has not selected Git/LFS for version control; do not present it as a commitment.

**Current implementation direction:** four pillars remain Animation, Collision Detection, Pathfinding and Navigation, and NPC AI. UE NavMesh/MoveTo is the baseline; a separately written A* graph is optional, not an assignment requirement. Reuse Behavior Tree definitions with individual controller/Blackboard state. Patrol means movement on foot. A simple squad coordinator can assign separate positions and roles; individual routes alone do not establish cooperation.

**Mission and saves:** six soldiers (one player, two allies, three enemies) are the initial configuration. The connected mission route, final objective sequence and NPC counts follow editor survey and playtesting. Reach/Clear are configurable examples. Proposed checkpoints save selected player/NPC/objective state at safe boundaries. Retry restores that snapshot and rolls back subsequent changes, or starts again if none exists. Saving does not inherently heal, refill ammunition or replace casualties; supply/reinforcement rules remain open. Full new-mission restart remains available. Do not restore the earlier blanket checkpoint exclusion or infer it from map size.

Read the current [proposal](Docs/Proposal/PROJECT_PROPOSAL.md), [assignment reports](Docs/Proposal/README.md) and [presentation](Docs/Presentation/README.md). The revised proposals retain the pillar/work tables, concept image and generalized flowchart. No Unreal implementation, map validation, course approval or performance result is claimed. The city mockup is concept art using official references, not gameplay or verified geography.

**Historical snapshot below — 22 September 2026.** Earlier one-street, three-pillar, one-objective, fixed-six and old-PDF/build instructions are superseded by the current notes and proposal links above. Preserve this snapshot as a transition record; do not treat its old scope as current instructions. This is an internal handoff, not a course submission.

## 1. Start here

**Active workspace:** `D:\0.Rutgers\CS549\Project-New`

**Private repository:** https://github.com/hzgyp/CS549-Paris-Street-Combat

**Branch:** `main`

Work directly in this saved project when continuing on the primary desktop. A source-only worktree or fresh clone will not contain the local city dependency. Do not create another project copy simply to open a new chat.

The user is Yupu Guo, the team leader. They are moving this work into a new window and intend to close the earlier windows. Read this file and the active documents rather than relying on unavailable chat history. Opening a new chat does not itself establish an Unreal connection.

If the session starts in a ChatGPT mirror such as `C:\Users\hzgyp\.codex\.chatgpt-projects\...`, use the active workspace explicitly for all project commands. Synced `sources/` files in that mirror are read-only references. Do not write project work there or in the archived Normandy directory.

### First-session read order

1. [AGENTS.md](AGENTS.md): binding scope, asset policy and rejected modeling route.
2. This handoff, [README.md](README.md) and [INDEX.md](INDEX.md).
3. [Current proposal](Docs/Proposal/PROJECT_PROPOSAL.md).
4. [Development pipeline](DEVELOPMENT_PIPELINE.md) and [technical design](Docs/Design/TECHNICAL_DESIGN.md).
5. [Asset restoration guide](Assets/README.md), [team ownership](Docs/Decisions/TEAM_AND_OWNERSHIP.md) and [submission status](Docs/Submission/STATUS.md).

Start with `git status --short --branch` and `git log -5 --oneline` in the active workspace. Preserve any changes made after this handoff. Check remote state before integrating new teammate work. Do not rerun the transition/migration scripts.

## 2. Approved direction

The previous Normandy landing implementation was retired after the team judged its modeling and interaction scope infeasible. The replacement is **Paris Street Combat**: a compact, single-player FPS encounter in a fictional Paris street during the **August 1944 liberation period**. Normandy remains historical background only.

The current primary academic pillars are **Animation, Collision Detection, Pathfinding and Navigation, and NPC AI / Behavior Trees**. Rendering and physical simulation are supporting engine/asset systems, not team-authored pillars. The team uses existing licensed environment and character assets rather than claiming original modeling or rendering technology.

Baseline: a surveyed connected city route, one player rifle, an initial roster of one Allied player, two Allied NPCs and three German NPCs, ordered Reach/Clear/Reach objectives, fixed lighting, movement/aim/fire/reload/damage, ally follow/regroup, bounded enemy patrol/search, win/fail/full restart and a packaged Windows build. Actual area, route length and duration follow the editor survey rather than a preset one-block or 60-90-second limit.

Exclude landing/ocean interaction, dynamic weather, driving, custom detailed character production, cinematic armies, complex allies/civilians, broad interiors, unrestricted destruction, multiplayer, an open-world city and runtime LLM NPCs. Availability of a vendor feature does not add it to the scope.

### Rejected production route

The user tested AI-designed modeling tasks executed by another AI over one night, spending roughly $200 and reaching 38 iterations. The character remained unusable for the intended quality. The team explicitly rejected this route for this project.

Do not resume Refine38, generate another detailed soldier from scratch, or attempt to fix that production approach through more tokens, models, prompts or skills. Use existing licensed compatible assets first, then bounded adaptation, professional help or a scope reduction. This is a project production decision, not a claim that all AI modeling is impossible.

## 3. What exists and what is still a plan

| Item | Current state |
|---|---|
| Scope reset, proposal, pipeline, technical design | Written and committed |
| New private GitHub repository | Created and pushed; `main` is the active branch |
| English and Chinese proposal PDFs | Two pages each; three-member panel, bold pillars, two attributed scene images; page layout checked |
| Paris city environment | Original delivery preserved locally; working copy organized under `Unreal/ParisStreetCombat` |
| Project configuration | Engine association `5.8`; ChaosVehiclesPlugin enabled; initial default maps point to the vendor Paris map |
| Historical references | Paris index and open questions created; Normandy references retained only as background |
| Selected old gunplay assets/scripts | Copied into `Reference/Gunplay` with provenance; not integrated into the active city |
| Paris gameplay, four pillar mechanisms, compatible soldier/weapon/action set | Planned, not demonstrated as implemented by this transition |
| Scene load, Blueprint compilation, play, packaging, performance, second-machine reproduction | Deferred; no successful validation claimed |
| Unreal editor automation connection for this project | Not established or verified in this handoff; do not assume an old bridge is connected |
| Course approval, assigned mentor and actual approval email evidence | Pending confirmation; an email draft exists, but it has not been sent by this task |

The organized city is not a finished FPS. The PDF pictures are supplier showcase images, not team gameplay screenshots. A source clone alone is not the full environment or a runnable packaged game.

## 4. Exact local paths and repository boundaries

| Purpose | Path relative to the active workspace |
|---|---|
| Active Unreal descriptor | `Unreal/ParisStreetCombat/WW2FranceLiberation.uproject` |
| Main city map | `Unreal/ParisStreetCombat/Content/WW2City/Maps/LV_Paris_WW2.umap` |
| Preserved original delivery | `WW2FranceLiberation---Version d20260630(UE5.6+)` |
| Asset inventory | `Assets/ASSET_REGISTER.csv` |
| Environment dependency inventory | `Assets/VENDOR_DEPENDENCY.json` |
| Copy provenance and hashes | `Assets/MIGRATION_MANIFEST.json` |
| Retained gunplay candidates | `Reference/Gunplay/` |
| Workstation records | `Reference/Workstations/` |
| Active history | `HistoricalReference/Paris1944/` |
| Background history | `HistoricalReference/NormandyContext/` |
| Course source requirements | `Course/Assignments/Assignment 1.docx`, `Assignment 2.docx` |
| Retirement record | `Archive/TRANSITION_RECORD.json` |

Unreal map package: `/Game/WW2City/Maps/LV_Paris_WW2`. Preserve vendor package names and external-actor/object layout. Team content belongs under `/Game/ParisCombat/{Maps,Blueprints,Animation,Materials,VFX,UI,Tests}`. Use editor-aware duplication/migration; never rename `.uasset` or `.umap` packages in Explorer to change their identity.

The recorded environment inventory contains 15,850 files and 28,421,951,358 bytes (about 26.47 GiB); this is a recorded inventory, not a fresh runtime check. The delivery label `d20260630 (UE5.6+)` is wrapper metadata, not independently verified vendor release history.

**Git intentionally excludes raw vendor city Content, external actor/object packages, the original delivery, engine caches and local credentials.** Entitlement and permitted team sharing still need confirmation; private GitHub visibility does not grant a license. Never force-add those ignored assets. Restore them from an entitled source using [Assets/README.md](Assets/README.md).

Git LFS tracks permitted binary types, including Unreal assets, model/audio files and PDFs. Keep one editor per shared Unreal binary. Do not assume two branches can safely merge concurrent edits to the same Blueprint or map.

Large JSON manifests contain thousands of records. Parse selected metadata or filter entries; do not dump complete manifests into the new conversation.

### Old project boundary

- Preserved old local project: `D:\0.Rutgers\CS549\Project`.
- Archived/read-only GitHub repository: https://github.com/hzgyp/CS549-Normandy-Sim.
- Old closure commit: `ccc4e9d2609508a4b82935403d6503093238a5d7`.
- Retained gunplay snapshot originates from old commit `7cadd764e565c2da160c935acddd8f333ef289b5`.

Do not edit, unarchive or restart the old project. Its proposals, pipeline, matrix, beach prototype and character plans are inactive. `Reference/Gunplay/BrowserPrototype` still depicts the old beach and is not a Paris demo. Retained generator scripts can contain `/Game/Normandy` paths and missing dependencies; read and adapt individual mechanisms before any execution.

## 5. Team and repository access

| Member | NetID | Responsibility |
|---|---|---|
| Yupu Guo | yg745 | Confirmed leader/integration owner; collision and gunplay implementation split proposed |
| Yuqi Pu | yp549 | Animation/action and compatible rig/weapon integration, proposed for kickoff confirmation |
| Jingdi Wu | jw2046 | Navigation/NPC AI and bounded environment setup, proposed for kickoff confirmation |

The plan does not assume three equally experienced developers; Yupu may execute the critical path serially. Each member should understand one mechanism, its baseline, failure case and evidence.

GitHub owner: `hzgyp`. The old repository's two collaborators were invited to the new repository with the same **write** permission. At this handoff check:

- `Colossus-MKII`: accepted; current collaborator with write access.
- `xp771005`: pending invitation with write access.

The account-to-person mapping was not independently established here. Do not invent a mapping from these usernames to Yuqi/Jingdi. Recheck acceptance only when needed; do not send duplicate invitations.

## 6. Technical design to carry forward

| Pillar | Team-owned mechanism | Planned evidence |
|---|---|---|
| **Animation** | Move/aim/fire/reload arbitration; guarded animation events synchronize ammunition and action state | Timer-only vs event synchronization; repeated inputs, interrupted reloads, hand/weapon alignment |
| **Collision Detection** | Camera-intent query followed by muzzle-path obstruction query; a single authoritative hit/surface result | Camera-only vs two-stage query at walls/corners; false damage/blocking and different frame-rate conditions |
| **Pathfinding and Navigation** | Student A* over surveyed junctions with NavMesh path-length costs; MoveTo leg execution, bounded replanning and destination reservations | A* versus Dijkstra on matched routes; cost equality, expansions, blocked-route recovery and ally bottlenecks |
| **NPC AI / Behavior Trees** | Shared controller/tree with per-NPC faction, role, group, patrol route and search zone; ally follow/regroup and bounded enemy search | Repeatable faction, sight-loss, search-expiry, death, regroup and distinct-route scenarios |

Blueprints are the primary implementation method. C++ needs a demonstrated reason. Unreal supplies the renderer, skeletal runtime, collision queries and navigation; purchased assets supply geometry/materials/motions. The team's contribution is the bounded mechanisms, integration rules and controlled comparisons. Do not claim ownership of Lumen, Nanite or vendor master materials.

Important contracts already designed in `Docs/Design/TECHNICAL_DESIGN.md`:

- **Shot:** hitscan baseline; reject illegal input, compute camera aim, query muzzle obstruction, consume one round for an accepted discharge, apply damage once, emit one authoritative feedback payload. Cosmetic tracers do not decide damage. Define the inside-wall muzzle-clearance policy during implementation.
- **Action:** a reload transaction has an ID and one guarded ammo-commit event. Cancellation before/after commit must not duplicate, refund or invent ammunition. Ignore stale animation notifies after cancellation/reset.
- **Feedback:** use the authoritative impact point, normal and physical material; bound particle/decal lifetime and count; clear or recycle at reset.
- **Encounter:** explicit Ready/Playing/Won/Lost states and reset generation; clear actors, timers, damage/action state, ammunition, effects and objective state. Enemy shots obey obstruction and stop after death.

Target, not measured result: Windows at 1920 x 1080, declared quality preset, aiming for 60 FPS on the primary i9-12900F / RTX 3080 10 GB / 32 GB desktop. Current free disk space has not been remeasured for this handoff. Pin exact engine/plugin versions after the readiness checks; the recorded installed baseline is UE 5.8.2.

## 7. Next development work

**The next development phase is Gate 1, dependency and environment readiness.** The user explicitly postponed detailed runtime checks during the planning reset. This handoff does not claim those checks passed, and reading it is not a reason to launch an unattended validation campaign.

When development resumes, execute a bounded readiness session:

1. Inspect current Git changes and teammate updates; identify the active descriptor and installed engine. Determine the actual editor/automation connection, if any, rather than reusing an old window's state or endpoint.
2. Confirm environment acquisition/usage rights and required plugins; survey connected routes, collision, sightlines, NavMesh coverage and travel time before selecting the mission area and fixed lighting preset.
3. Choose one existing historically appropriate soldier configuration and one compatible first-person gun/arms/action set. Record source, rig, reload requirements and usage rights. The city pack does not supply the trailer soldiers or a complete playable combat set.
4. Check the chosen assets in a small compatibility map and establish the first Windows packaging path. Record actual failures and decisions; do not hide missing dependencies behind a visual screenshot.
5. Update the readiness record and next action before moving into Gate 2.

Continue in the established order: **Gate 2 combat/mission spine -> Gate 3 four pillar mechanisms and comparisons -> Gate 4 quality/performance -> Gate 5 freeze and delivery**. Build the complete initial mission before optional roster or stage growth. A two-workday investigation checkpoint is a decision point, not a guaranteed schedule.

The team mentioned a late-November final deadline, but official dates, midterm timing, mentor and member availability remain unconfirmed. Reserve the final two weeks for freeze/regressions after dates are verified; do not silently expand scope because time appears available.

## 8. Documents and submission status

- [Assignment 1 proposal](Docs/Proposal/CS549_Assignment1_Proposal.pdf): current two-page Assignment 1 report.
- [Assignment 2 proposal](Docs/Proposal/CS549_Assignment2_Proposal.pdf): current two-page PRD, technical specification and MVP report.
- [Long-form proposal](Docs/Proposal/PROJECT_PROPOSAL.md): implementation planning context.
- [Image source record](Docs/Proposal/Visuals/README.md): two official Meshingun Studio showcase views; retain attribution and do not relabel as team results.
- [Approval email draft](Docs/Submission/APPROVAL_EMAIL_DRAFT.md): prepared, not sent.
- [Submission status](Docs/Submission/STATUS.md): pending external requirements.

Assignment 2 calls for a report of at most two pages containing PRD, technical specification and narrow MVP, plus actual concept/pillar approval and mentor-assignment email proof outside that page limit. Never fabricate approval, mentor identity or test results. Prior approval of a Normandy concept cannot automatically be assumed to cover Paris. Do not send email without authorization.

Both current assignment PDFs include all three names/NetIDs, Yupu's leader designation, the four pillars, the AI-generated street concept and the mission flowchart. Do not remove required disclosures or visual attribution. Formal submission files must not include word-count notes, prompts or internal QA/generation commentary.

### Rebuilding the current assignment proposals

`Tools/build_assignment_proposals.py` produces the current Assignment 1 and Assignment 2 DOCX/Markdown sources. Render each DOCX through the documents workflow, inspect both pages, and copy only the accepted PDFs into `Docs/Proposal/`. The older English/Chinese `CS549_Paris_Street_Combat_Proposal*.pdf` files and `Tools/build_proposal.py` are superseded 22 September provenance and must not overwrite the current reports.

```powershell
Set-Location -LiteralPath 'D:\0.Rutgers\CS549\Project-New'
& 'C:\Users\hzgyp\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' Tools/build_assignment_proposals.py
```

Apply the documents and PDF workflows when rebuilding, render and visually inspect all four report pages, and keep each PDF synchronized with its DOCX and Markdown source. The full Markdown proposal is longer implementation context, not a page-for-page transcript. Temporary renders belong under ignored `tmp/proposal-review/`.

## 9. History questions and working style

Before final historical asset acceptance, settle exact playable date, player unit, enemy formation, rifle/reload variant, uniform/insignia and the visible street dressing. Use `HistoricalReference/Paris1944/RESEARCH_GAPS.md` to constrain research to objects actually visible in this encounter. Normandy weather is not evidence for August Paris; unknown values remain unknown. Marketing renders are not historical proof.

The user is new to game development and 3D. Explain the dependency and purpose of each significant step so implementation does not become a black box. Make global project judgments rather than turning an incidental example into the main contribution. The user prefers concrete work and dislikes repeated permission questions for already authorized routine actions.

Project documents are English; conversation can be Chinese and requested Chinese review translations are permitted. Preserve the team's scope decisions. Do not purchase assets, send messages, or infer new scope from vendor materials without the relevant user authorization. Persist useful decisions and evidence in the repository so another window can continue.

## 10. Source-control checkpoint

Before this handoff was added, `main` was clean at **`6bea000`**, already pushed:

- `c88fae8`: establish Paris scope, technical plan and asset baseline.
- `6cd6a88`: record completed Normandy archive and Paris transition.
- `6bea000`: add prominent team panel, scene references and Chinese proposal.

This handoff and its index links are intended as the next commit. Use `git log` for its actual hash; do not treat `6bea000` as forever-current HEAD. Repository invitations are server-side state, not Git commits. Credential-manager authentication worked for Git/GitHub operations; never print or store credentials in handoff files.

Before ending a future session, update: actual completed work, unresolved blockers, next bounded action, changed asset/Blueprint ownership, and the relevant commit/build identity. Do not silently convert scheduled checks into completed results.
