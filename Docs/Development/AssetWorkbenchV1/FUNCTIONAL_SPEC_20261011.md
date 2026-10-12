# Paris Street Combat Asset Workbench Functional Specification

Implementation note (2026-10-11): [V1 delivery, verification and limitations](IMPLEMENTATION_RESULT_20261011.md). The original design snapshot follows.

Date: 11 October 2026. Revision: 1.0. Status: design for review, implementation pending.

[中文审阅版](FUNCTIONAL_SPEC_20261011_ZH.md) · [Technical design](TECHNICAL_DESIGN_20261011.md)

## 1 Purpose and delivery boundary

The workbench will help the team find purchased and team-created assets, inspect their appearance and history, identify the exact versions used by a game build, and prepare clear requirements before acquiring or making another asset. Its first release is a local, read-only catalog with requirement templates. Later releases add controlled task registration and review.

The user authorized these functional and technical documents. This revision specifies future software; it does not implement a service, select a new game baseline, purchase an asset, publish files, or authorize another detailed character-production experiment.

V1 succeeds when a team member can open one of five representative asset families and find its provenance, relevant versions, actual game evidence, usage, unresolved issues and applicable creation requirements without searching several folders manually.

## 2 Existing foundation and current gaps

The project already records immutable asset files and hashes through [CATALOG.json](../../../Assets/Sync/CATALOG.json) and its selected manifests. [Team synchronization rules](../../../Assets/TEAM_SYNC_WORKFLOW.md) separate public source metadata from private asset bytes and local pending intake. The workbench must preserve these authorities.

The early [asset register](../../../Assets/ASSET_REGISTER.csv) still contains unselected soldier and first-person entries. Later integration records describe adopted assets. The [downloaded asset catalog](../../../Assets/XIAN_YU_ASSET_CATALOG_20261003.md) also records a repeated animation delivery verified against existing bytes. These are reasons to connect dated records and exact identities, rather than use a directory name or the most recent prose as current truth.

As of this design, the local selected gameplay baseline is enemy-clear v3, the latest UI selector identifies an unselected candidate_ui_v5, and the published playable Catalog entry remains audio V2. These are different selection scopes. The dashboard must show all three with their source and observation time; it must not collapse them into one global latest version. Future refreshes read the selectors again.

## 3 Users and responsibilities

| User | Main task | V1 capability |
| --- | --- | --- |
| Team member | Find content, understand compatibility and current usage | Browse, filter, compare, inspect evidence and copy a requirement template |
| Asset owner | Prepare a bounded acquisition or adaptation task | Read requirements, protected constraints and existing alternatives |
| Integration owner | Review exact versions and release dependencies | Inspect selectors, missing dependencies, conflicts and evidence scope |

These are workflow responsibilities, not new accounts or assignments. V1 runs for the current Windows user on localhost. Named reviews and authenticated multi-user access belong to later phases; an SFTP shared account is not a reviewer's identity.

## 4 Asset and version concepts

| Concept | Meaning and example |
| --- | --- |
| Delivery bundle | An acquired package or original batch, such as a soldier package containing meshes, materials and actions |
| Logical asset | A stable team concept, such as the German rifle appearance or pressure-mine prop |
| Asset revision | Immutable source/export file identities for one revision of that concept |
| Integration revision | Bindings, materials, sockets, adapters and configuration connecting assets to a particular game/source revision |
| Build selection | A specific source, executable and dependency selection for local formal use, a review candidate, or published distribution |
| Evidence | A dated result, image or review tied to exact subjects and a stated test scope |

A bundle can supply several assets, and one asset can depend on several bundles. A pose or runtime adapter change can create a new integration revision while leaving the model bytes unchanged. A version history can branch; a larger version number is not evidence of acceptance.

Usage claims must identify their basis: documented binding, scanned package reference, or observed runtime use. A dependency reference alone does not prove that a particular actor appeared in a running game. Where the relationship is unresolved, show it explicitly.

## 5 Pages and functional requirements

| ID | Page or capability | Required behavior |
| --- | --- | --- |
| FR01 | Overview | Show separate local formal, review-candidate and published selections; display index time, source health and unresolved mappings |
| FR02 | Asset library | Cards and list view; search Chinese/English names and IDs; filter category, origin, owner, lifecycle, rights, availability and build usage |
| FR03 | Asset detail | Show provenance, versions, dimensions and technical facts with their source, dependencies, actual usage, evidence and remaining issues |
| FR04 | Version comparison | Compare two exact revisions; show parent/branch, changed files and parameters, images and decision reasons; retain rejected and retired entries |
| FR05 | Build and usage view | Navigate build → integration → asset revision → files, and reverse to affected builds; explain the basis and completeness of every link |
| FR06 | Evidence and acceptance | Keep technical, visual, human, selection and publication results separate; show the exact subject, scope, date and evidence availability |
| FR07 | New asset requirements | Provide complete copyable templates for props, characters, weapons, animation, environment, VFX and audio; required fields have explanations |
| FR08 | Catalog health | Report stale sources, conflicting selectors, missing previews, unverified bytes, unknown rights and suspected duplicate deliveries |
| FR09 | Safe local browsing | Serve only registered, permitted previews; source-only clones remain useful; no model overwrite, restore, deletion or publication actions in V1 |
| FR10 | Refresh and provenance | Refresh registered metadata into a coherent snapshot; preserve the previous good snapshot after a critical import failure and explain the error |

### 5.1 Library and asset detail

Cards prioritize a representative image, asset name/category, source route, lifecycle and usage badges. Purchased, team-created and adapted-from-existing are separate origin labels; an adaptation retains links to its original sources. Audio uses a play control with duration when a permitted local file is available. No media autoplays.

Details use tabs for overview, versions, usage, evidence and requirements. A visible source link accompanies each important fact. Missing values say unknown, not zero or passed. Technical budgets and measured values appear in separate columns.

Counts distinguish logical assets, delivery bundles, file entries and unique byte objects. Repeated manifests and junction aliases must not inflate the number of models or physical storage estimates. V1 may leave physical disk usage unknown when it has only manifest sizes.

### 5.2 Preview and comparison

V1 uses existing approved-for-the-audience images and permitted local audio. Images identify whether they are vendor reference, Blender preview, fresh export inspection or actual UE capture. An image is associated with a revision and evidence record, not guessed from a filename.

Side-by-side comparison shows camera/context differences. A matched-view toggle is offered only when the records establish matching conditions. Missing pixels retain the evidence entry with a clear availability label. Historical views and rejected candidates remain readable.

Optional browser 3D preview is a later enhancement for reviewed GLB derivatives. It is a browsing aid; the UE screenshot and runtime evidence remain separate because materials, lighting and behavior can differ.

### 5.3 Build and usage view

The page initially offers the three selection scopes from FR01 and a selector for individual review streams. It displays full source and game identities in expandable details. It must distinguish a model's first adoption from the currently selected native asset package.

A path conflict, missing dependency, unresolved alias or outdated launch target creates a visible issue. Merely finding an unreferenced file does not make it safe to delete. Retired runnable files can instead have a recovery mapping; present that mapping without claiming that the original path exists.

## 6 Independent status dimensions

| Dimension | States or information |
| --- | --- |
| Lifecycle | intake, candidate, retained, rejected, retired; retirement concerns a stated revision or artifact |
| Rights | unknown, restricted, permitted for a stated audience/use; record source and attestation type |
| Availability | local, declared remote, verified remote at a date, missing, recoverable, inaccessible |
| Validation | not run, pass, fail, incomplete, inherited, unassessed; each result names its scope |
| Human review | pending, accepted, rejected, accepted with limitations; exact subject and decision reference |
| Selection | selected by a named channel/build, or unselected; derived from the authoritative selector |
| Publication | local only, recorded published, verification unavailable, or retired release |

There is no universal green accepted badge. An adopted model can retain a known contact limitation. A successful file transfer cannot pass visual review. A private team-sharing attestation does not establish permission for public asset downloads or every derivative.

Raw records remain unchanged. A correction or later decision links to and supersedes a specific earlier assertion while preserving both dates. An inherited result explains which unchanged files or behavior justify inheritance and which new checks remain open.

## 7 New asset requirement template

V1 offers the following template as copyable text. V1.1 may save and review structured task records. These fields guide both purchased intake and team work.

| Field group | Required content |
| --- | --- |
| Purpose | Asset name, owner, mission/use, intended camera, viewing distance, expected simultaneous instances and target build |
| Existing alternatives | Search results from current purchases and assets; reuse/adapt/buy/create route and reason |
| Historical identity | Period, faction/unit and variant when claimed; explicitly label fictional props or uncertain identity |
| Appearance | Silhouette, dimensions in cm, scale references, readable details, material intent and reference provenance |
| Technical budget | Target and hard limit for triangles/LODs, material slots, textures, memory where measurable; define by category and use |
| Integration | Engine/tool target, origin and axes, collision rules, skeleton/sockets, attachments, required actions and dependencies |
| Protected content | Exact existing assets, hand poses, rigs, clips, interfaces and gameplay transactions that must remain unchanged |
| Delivery | Editable source, exports, textures, dependency inventory, source/license record, normal-distance and detail images, fresh-import result |
| Acceptance | Named automated checks, UE visual/runtime cases, human review, measurement setup and evidence required for each |
| Stop and recovery | Failure cases read, what changes in this attempt, early acceptance check, stopping condition and preserved originals |
| Sharing | Intended recipients, allowed uses, evidence references and outstanding rights questions; private receipts stay private |

The template rejects blank budgets by requiring either a number/unit or an explicit reason why the field is not applicable. It does not impose one triangle limit on all assets. Existing asset measurements are examples, not automatically approved budgets for a new task.

For characters, require existing licensed mesh/rig/action candidates and bounded adaptation. The stopped AI-led detailed soldier production route remains closed. For animation, search existing purchased finished clips first and specify source clip/target rig; task registration does not authorize new motion creation, acquisition or integration.

### 7.1 Example of the pressure-mine family

The existing result describes a team-created fictional exterior prop with a 28 cm disc, 10,809 triangles and 1024 textures. These are historical measured/described facts for that asset, not a new production budget or a certified historical model. Link the [mine result](../MissionLoopV1/PRESSURE_MINE_RESULT_20261011_ZH.md), model review and exact game evidence.

Its Blender/GLB review, the dark UE candidate, and corrected UE integration must appear as separate evidence. The original model can be unchanged between the two UE integration revisions. Human adoption remains governed by the review/selection records.

## 8 Workflow and phase boundaries

| Phase | Delivered capability | Exit condition |
| --- | --- | --- |
| V1 early gate | Registered source ingestion and five representative families | Stable identities, separate channels and correct failed/missing evidence states before UI expansion |
| V1 complete | FR01–FR10 read-only pages and copyable requirements | All V1 acceptance cases pass; user can locate exact usage and evidence |
| V1.1 | Structured local task drafts, review decisions and metadata change proposals | Named decisions, conflict detection and recoverable draft writes; no automatic baseline selection |
| V1.2 | Optional reviewed GLB browsing and bounded UE metadata export | Preview provenance and fresh-engine compatibility verified for each supported route |
| Later shared deployment | Authenticated team access and a separately scoped release workflow | Audience-specific rights, authentication, audit and publication gates designed and tested |

The future intake flow is: search existing content → document need and route → preserve original delivery locally → create a bounded candidate → technical and UE checks → human review → explicit integration selection → separately authorized verified publication. Rejected candidates keep their identities and reasons.

V1 does not offer automatic asset generation, purchasing, native editing, bulk directory relocation, orphan deletion, SFTP upload, Git push, game launching or a general shell. These operations require their own implementation and authorization scope.

## 9 Acceptance plan

These are future checks, not completed results. The pilot covers German soldier/rig, Allied soldier/rig, first-person arms/weapon assembly, the pressure mine and recorded audio. All active Catalog groups appear in the group/file index; only these five families require curated semantic relationships initially.

| ID | Check | Expected result |
| --- | --- | --- |
| AC01 | Open the dashboard against current selectors | Local enemy-clear selection, UI candidate and published audio V2 are visibly distinct, each with provenance |
| AC02 | Find each pilot family from its Chinese or English name | Correct card, revisions and source reached; target is within 30 seconds in a human walkthrough |
| AC03 | Compare the mine's failed and corrected UE integrations | Failed image/result stays failed; unchanged model bytes are not labeled a remodel; current adoption is not invented |
| AC04 | Inspect a source-only clone or missing private preview | Metadata remains useful; missing/inaccessible evidence is shown without fake thumbnails or passed checks |
| AC05 | Inspect German visual selection and limitations | Adoption and remaining contact limitations coexist with their exact scopes |
| AC06 | Inspect animation repeat-delivery evidence | Duplicate byte relationship is shown; no automatic deletion and no counting it as newly usable motion |
| AC07 | Follow a selected build to its assets and back | Exact resolved links or explicit gaps; dependency reference is distinguished from runtime observation |
| AC08 | Copy a new prop or character requirement | Complete fields, applicable constraints, early gate and stop condition; existing-asset policy preserved |
| AC09 | Refresh malformed, changing or conflicting source metadata | Critical error preserves the last good snapshot; noncritical missing evidence appears as degraded availability |
| AC10 | Browse media and operate all V1 controls | Only registered permitted media; no source/asset writes; unsupported state-changing controls absent |
| AC11 | Inspect an exit-zero run without complete results | Incomplete or fixture error, never a pass inferred from exit code |
| AC12 | Check 1920×1080 and 1366×768 views | Search, filters, evidence labels and comparisons remain usable with keyboard and readable text |

Search performance target: warm local queries at p95 below 500 ms for a documented fixture containing at least 20,000 file entries. First-page interaction target: within 2 seconds after the service and index are ready. Measure metadata, media loading and full file verification separately; these are design targets, not current measurements.

## 10 Failure lessons and stopping conditions

Cases read for this design include [MI030](../../../Failures/MI030-20261011-mine-render-winding/ANALYSIS.md), [MI033](../../../Failures/MI033-20261011-ui-screenshot-timing/ANALYSIS.md), [MI035](../../../Failures/MI035-20261011-ui-restore-fixture-alias/ANALYSIS.md), [MI036](../../../Failures/MI036-20261011-ui-ready-selection-fixture/ANALYSIS.md) and [GP010](../../../Failures/GP010-20261004-german-rifle-native/FAILURE_ANALYSIS.md).

The changed approach is to bind each assertion to an exact subject and evidence scope, expose failures and uncertainty, and keep metadata indexing separate from source mutation. In particular, rendered pixels, runtime instance behavior and complete test results have distinct evidence requirements.

Before expanding the UI, the early gate must correctly distinguish all three selection scopes and represent the mine failure, a missing private file and an incomplete test. Stop the affected implementation step if it mutates protected files, confuses channels, promotes incomplete evidence to pass, exposes unapproved private media, follows an unregistered storage alias, or requires weakening an existing rights/validation rule. Preserve diagnostics and the last good index; correct the adapter or design before continuing.

## 11 Related project authorities

- [Project instructions](../../../AGENTS.md) and [handoff](../../../HANDOFF.md).
- [Storage and team synchronization](../../../Assets/TEAM_SYNC_WORKFLOW.md).
- [Current local development baseline](../CURRENT_DEVELOPMENT_BASELINE.json), [UI candidate](../CURRENT_UI_REVIEW.json) and [equipment candidate](../CURRENT_EQUIPMENT_REVIEW.json).
- [German usage](../GERMAN_NPC_ASSET_USAGE.md), [Allied usage](../ALLIED_NPC_ASSET_USAGE.md) and [downloaded asset catalog](../../../Assets/XIAN_YU_ASSET_CATALOG_20261003.md).

This document and its Chinese counterpart share revision 1.0, FR01–FR10 and AC01–AC12. Implementation changes must update both and the corresponding technical sections.
