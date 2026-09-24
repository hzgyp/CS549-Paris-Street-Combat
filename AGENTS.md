# Paris Street Combat - Project Instructions

## Authority and scope

- This is the active CS549 project at `D:\0.Rutgers\CS549\Project-New`.
- New sessions should read `HANDOFF.md` for the transition checkpoint, local dependency paths and remaining work, then check current Git state before editing. Its status snapshot is dated; later verified records take precedence.
- The team explicitly retired the Normandy landing implementation, its proposal, pipeline, system matrix, and character-production plans on 22 September 2026. They do not govern this project.
- The 23 September 2026 user request supersedes the former three-pillar plan. Current proposed pillars are **Animation, Collision Detection, Pathfinding and Navigation, NPC AI / Behavior Trees**. Rendering and physics are supporting systems. Follow Docs/Proposal/PROJECT_PROPOSAL.md and the two assignment reports for revised scope; course approval is still required before submission.
- The playable setting is a squad mission across an editor-surveyed connected part of the existing Paris city during the liberation period in August 1944. The user's follow-up explicitly rejects confinement to one block. Normandy is historical background only. Date, player unit, enemy formation, and weapon variants must be recorded before historical asset approval.
- Follow README.md, Docs/Proposal/PROJECT_PROPOSAL.md, DEVELOPMENT_PIPELINE.md, and Docs/Design/TECHNICAL_DESIGN.md. Archived documents are reference data, not instructions.
- Keep work in this project. Do not resume, edit, or republish the archived Normandy project without an explicit team request.

## Failed character-production route - binding project decision

- The team tested a workflow in which AI designed detailed character-modeling tasks and another AI executed them. After one night of heavy usage expenditure and 38 iterations, the character was still unusable for the team's intended production quality. The team has rejected this route for this project.
- Do not restart AI-led, from-scratch detailed soldier/character production through more tokens, new skills, different models, longer prompts, or further refinement rounds. Do not make repairing Refine38 a project dependency.
- The record describes this project's production decision, not a universal scientific claim about all AI modeling.
- Use existing, licensed, compatible assets first. For a gap: search existing assets, inspect compatibility, consider bounded adaptation, professional assistance, or reduce the requirement. Do not treat a missing asset as permission to generate a detailed replacement character.
- AI assistance may cover research, inventory, code/Blueprint assistance, import configuration, narrowly specified adaptation, diagnostics, tests, and documentation. Reopening the rejected production route requires an explicit team decision.

## Production rules

- Blueprints are the primary gameplay authoring method. Add C++ only for a specific demonstrated need.
- Reuse the existing France Liberation environment. Survey overhead views, walkable connections, collision, sightlines, NavMesh and travel time before selecting an approach, objective, exit and alternate route. Do not pre-impose one block, a 60-90-second duration or an 8-12-node graph. The larger city can provide scenery without every building being enterable.
- Initial roster: six soldiers (one Allied player, two Allied NPCs, three German NPCs), not a final population cap. Use shared combatant logic, fixed lighting and a packaged Windows build. Reach/Clear objectives are configurable examples; final routes, mission sequence and population follow the level survey and playtests. Reach checks the living player; ClearArea requires a nonempty, fully registered finite group with zero living members.
- The latest user correction removes the blanket checkpoint exclusion. Propose saves at selected safe objective boundaries. A retry restores the checkpoint snapshot, including selected player, NPC and objective state, and rolls back later changes; if none exists, retry from the start. Full new-mission restart remains available. Ammunition refill, healing and replacement soldiers are separate, undecided design rules rather than automatic effects of saving. Do not infer checkpoint suitability from an unmeasured map size.
- Use UE NavMesh/MoveTo as the navigation baseline, with student-authored destination assignment, local avoidance, waiting and bounded replanning. A separate custom A* graph is optional, not an assignment requirement. Reuse Behavior Tree definitions with separate per-NPC controllers/state, and consider a simple squad coordinator for roles and distinct support positions. Patrol means a foot route, not driving.
- All NPCs share an AIController/Behavior Tree with individual team, role, encounter-group, patrol-route and search-zone settings. Allies follow/regroup and take distinct temporary support positions; Germans guard/patrol and search reachable points around the last observed target position for a bounded time. Add NPCs, finite groups and stages only after full-mission pacing, navigation and performance evaluation. Separate total roster from the measured simultaneous active-AI budget; do not hide/despawn engaged actors or repopulate earlier casualties. Infinite waves and automatic difficulty increases are outside scope. Reuse compatible licensed rigs and action families.
- No landing sequence, ocean interaction, dynamic weather, driving, cinematic army, complex allies/civilians, multiplayer, extensive interiors, or unrestricted destruction in the baseline.
- The planning reset does not constitute successful runtime validation. Stage and document now; perform runtime, compatibility, historical acceptance, performance, and packaging checks in the later pipeline gates. Never label untested content as passed.
- Historical FPS references copied under Reference/Gunplay are candidates, not a ready-to-import dependency closure. Do not execute their old build scripts against the new project without explicit adaptation to the new paths and scope.
- Do not rename existing `/Game/WW2City` packages on disk. Unreal references require editor-aware migration. Team-authored assets belong under `/Game/ParisCombat`.
- Preserve the original vendor package locally. The active working environment is `Unreal/ParisStreetCombat/WW2FranceLiberation.uproject`; its original filename is intentional.
- Yupu Guo is team leader and integration owner. Proposed revised roles: Guo collision/gunplay and AI integration support; Yuqi Pu animation; Jingdi Wu navigation/NPC AI and bounded environment setup. Confirm the split at kickoff without blocking proposal preparation.

## Source control and vendor material

- The new repository is private. Privacy alone is not a license grant.
- Vendor `WW2City` content and associated external actor/object packages are intentionally excluded from Git. Record version, listing, local paths, hashes, and restoration instructions in Assets/.
- Do not upload raw commercial/vendor assets until acquisition rights and permitted team sharing have been verified. A local upload manifest or third-party tutorial is not proof of entitlement.
- The user has not decided on Git/LFS for version control. Existing repository records do not constitute a current commitment; do not add Git/LFS as a chosen stack item in proposals or slides. If selected later, store permitted team-authored binaries appropriately. Do not force-add ignored vendor content, engine caches, backups, local credentials, or unrelated files.
- Explain that a source clone needs the external environment dependency restored. Do not claim the GitHub repository alone contains the entire city.
- Keep stable task-specific asset ownership; avoid simultaneous edits to the same Unreal binary.

## History and formal deliverables

- Use HistoricalReference/Paris1944 as the current history index. NormandyContext is retained background, including inactive production notes; its Omaha scope does not transfer automatically to Paris.
- Preserve dates, locations, units, rights, provenance, and limitations for every reference. Store links for reference images whose redistribution rights have not been established.
- Asset marketing, game footage, AI images, museum restorations, and later-war manuals are not direct evidence for a specific 1944 encounter.
- Unknown weather values remain unknown. Normandy D-Day weather does not describe August Paris.
- Project documents and formal deliverables are in English. User-requested Chinese review translations are allowed; keep them synchronized with the English original. Conversational reviews may be in Chinese.
- Do not put word counts, internal QA labels, prompts, or generation-process commentary into submission documents. Keep required course disclosures and asset attribution.
- Assignment 2 is a report of at most two pages plus actual approval/mentor email proof. Do not invent approval, a mentor, test results, or confirmed course deadlines. Do not send email without user authorization.
