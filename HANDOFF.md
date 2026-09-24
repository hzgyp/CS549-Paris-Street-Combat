# Paris Street Combat - new-session handoff

**Latest user correction:** six soldiers are the initial configuration, not a final population cap. The mission crosses a connected part of the existing city with ordered Reach rally A → Clear assigned group B → Reach end C objectives. Reach checks the living player; ClearArea requires a nonempty, fully registered finite group with zero living members. Player death causes failure. Full restart restores the configured roster, objective index, counters and timers; defeated actors stay defeated across stages. Objective markers are not checkpoint saves. Allies follow/regroup; Germans guard/patrol and search reachable points around last observed targets for a bounded time. All NPCs share AI code with individual team, role, encounter-group, patrol-route and search-zone configuration. Add finite groups/stages only after full-mission pacing, navigation and performance evaluation; no infinite waves or automatic difficulty increases.

**23 September 2026 revision:** read [the current proposal](Docs/Proposal/PROJECT_PROPOSAL.md) and [two assignment reports](Docs/Proposal/README.md) before the dated snapshot below. The four pillars are Animation, Collision Detection, Pathfinding and Navigation, and NPC AI / Behavior Trees; rendering/physics support them. Both reports now connect pillars to concrete work and implementation routes in tables. Both compact reports omit the planned-proof column; Proposal 2 retains the required midterm demonstration plan in §3.2. The initial roster is one Allied player, two Allied NPCs and three German NPCs. Actual map area, locations, duration and graph size require an editor survey. Both reports include the [formal game flowchart](Docs/Proposal/Visuals/paris-mission-flowchart.svg) and regenerated [street mockup](Docs/Proposal/Visuals/paris-six-character-concept.png). The mockup uses both official gallery images as appearance references; it does not establish vendor geography. Earlier ImageGen concepts remain archived provenance. No Unreal implementation, route validation, compatibility result, course approval or email submission is claimed. The new proposal's phased plan governs the next work; engine validation remains the first development gate.

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

The only primary academic pillars are **Rendering, Animation, Collision Detection**. Basic NPC behavior and navigation support the encounter. They are not additional pillars. Earlier threat-aware pathfinding, dynamic battlefield, weather and full-simulation proposals no longer govern this project.

Baseline: one bounded outdoor street, one player weapon, one enemy configuration with a small group, one objective, fixed lighting, movement/aim/fire/reload/damage, win/fail/reset and a packaged Windows build. The first complete encounter should last approximately **60-90 seconds**.

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
| Paris gameplay, three mechanisms, compatible soldier/weapon/action set | Planned, not demonstrated as implemented by this transition |
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
| Jingdi Wu | jw2046 | Existing environment/rendering responsibility retained |

The plan does not assume three equally experienced developers; Yupu may execute the critical path serially. Each member should understand one mechanism, its baseline, failure case and evidence.

GitHub owner: `hzgyp`. The old repository's two collaborators were invited to the new repository with the same **write** permission. At this handoff check:

- `Colossus-MKII`: accepted; current collaborator with write access.
- `xp771005`: pending invitation with write access.

The account-to-person mapping was not independently established here. Do not invent a mapping from these usernames to Yuqi/Jingdi. Recheck acceptance only when needed; do not send duplicate invitations.

## 6. Technical design to carry forward

| Pillar | Team-owned mechanism | Planned evidence |
|---|---|---|
| **Rendering** | Surface-driven hit feedback; position/normal and parameter control; effect lifetime and active-count limits | Generic vs surface-aware feedback under matched shots/views; visual evidence, GPU frame time and effect count |
| **Animation** | Move/aim/fire/reload arbitration; guarded animation events synchronize ammunition and action state | Timer-only vs event synchronization; repeated inputs, interrupted reloads, hand/weapon alignment |
| **Collision Detection** | Camera-intent query followed by muzzle-path obstruction query; a single authoritative hit/surface result | Camera-only vs two-stage query at walls/corners; false damage/blocking and different frame-rate conditions |

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
2. Confirm environment acquisition/usage rights and required plugins; select one small playable street and a fixed lighting preset.
3. Choose one existing historically appropriate soldier configuration and one compatible first-person gun/arms/action set. Record source, rig, reload requirements and usage rights. The city pack does not supply the trailer soldiers or a complete playable combat set.
4. Check the chosen assets in a small compatibility map and establish the first Windows packaging path. Record actual failures and decisions; do not hide missing dependencies behind a visual screenshot.
5. Update the readiness record and next action before moving into Gate 2.

Continue in the established order: **Gate 2 combat loop -> Gate 3 three mechanisms and comparisons -> Gate 4 quality/performance -> Gate 5 freeze and delivery**. Build the complete small loop before optional polish. A two-workday investigation checkpoint is a decision point, not a guaranteed schedule.

The team mentioned a late-November final deadline, but official dates, midterm timing, mentor and member availability remain unconfirmed. Reserve the final two weeks for freeze/regressions after dates are verified; do not silently expand scope because time appears available.

## 8. Documents and submission status

- [English two-page proposal](Docs/Proposal/CS549_Paris_Street_Combat_Proposal.pdf): intended course version.
- [Chinese two-page proposal](Docs/Proposal/CS549_Paris_Street_Combat_Proposal_CN.pdf): matching review translation requested by the user.
- [Long-form proposal](Docs/Proposal/PROJECT_PROPOSAL.md): implementation planning context.
- [Image source record](Docs/Proposal/Visuals/README.md): two official Meshingun Studio showcase views; retain attribution and do not relabel as team results.
- [Approval email draft](Docs/Submission/APPROVAL_EMAIL_DRAFT.md): prepared, not sent.
- [Submission status](Docs/Submission/STATUS.md): pending external requirements.

Assignment 2 calls for a report of at most two pages containing PRD, technical specification and narrow MVP, plus actual concept/pillar approval and mentor-assignment email proof outside that page limit. Never fabricate approval, mentor identity or test results. Prior approval of a Normandy concept cannot automatically be assumed to cover Paris. Do not send email without authorization.

Both PDFs currently include all three names/NetIDs, Yupu's leader designation, proposed roles, bold pillars, two scene references and the same planned mechanisms. Do not remove required disclosures or image attribution. Formal submission files must not include word-count notes, prompts or internal QA/generation commentary.

### Rebuilding the proposal

`Tools/build_proposal.py` produces both language versions together and checks page count, member names and embedded images. It uses ReportLab and pypdf, with Windows Arial/Microsoft YaHei fonts embedded. Use the bundled runtime if system Python lacks ReportLab:

```powershell
Set-Location -LiteralPath 'D:\0.Rutgers\CS549\Project-New'
& 'C:\Users\hzgyp\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' Tools/build_proposal.py
```

Apply the available PDF skill when editing PDFs, render and visually inspect all four pages, and keep both languages synchronized. Source strings for both compact versions live in the builder. The full Markdown proposal is a longer planning document, not a page-for-page transcript. Temporary PDF renders are under ignored `tmp/pdf-review/`.

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
