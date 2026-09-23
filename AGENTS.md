# Paris Street Combat - Project Instructions

## Authority and scope

- This is the active CS549 project at `D:\0.Rutgers\CS549\Project-New`.
- New sessions should read `HANDOFF.md` for the transition checkpoint, local dependency paths and remaining work, then check current Git state before editing. Its status snapshot is dated; later verified records take precedence.
- The team explicitly retired the Normandy landing implementation, its proposal, pipeline, system matrix, and character-production plans on 22 September 2026. They do not govern this project.
- Only three primary pillars are retained: **Rendering, Animation, Collision Detection**. History and bounded gunplay references are retained. AI/navigation support the encounter; they are not additional primary contributions.
- The playable setting is a small fictionalized Paris street encounter during the liberation period in August 1944. Normandy is historical background only. Date, player unit, enemy formation, and weapon variants must be recorded before historical asset approval.
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
- Reuse the existing France Liberation environment. Select a limited street encounter instead of building an entire city or making every building enterable.
- Baseline: one player weapon, one enemy character configuration, small enemy count, one objective, fixed lighting, win/fail/reset, packaged Windows build.
- No landing sequence, ocean interaction, dynamic weather, driving, cinematic army, complex allies/civilians, multiplayer, extensive interiors, or unrestricted destruction in the baseline.
- The planning reset does not constitute successful runtime validation. Stage and document now; perform runtime, compatibility, historical acceptance, performance, and packaging checks in the later pipeline gates. Never label untested content as passed.
- Historical FPS references copied under Reference/Gunplay are candidates, not a ready-to-import dependency closure. Do not execute their old build scripts against the new project without explicit adaptation to the new paths and scope.
- Do not rename existing `/Game/WW2City` packages on disk. Unreal references require editor-aware migration. Team-authored assets belong under `/Game/ParisCombat`.
- Preserve the original vendor package locally. The active working environment is `Unreal/ParisStreetCombat/WW2FranceLiberation.uproject`; its original filename is intentional.
- Yupu Guo is team leader and integration owner. Jingdi Wu owns environment/rendering. Proposed animation ownership is Yuqi Pu; confirm the assignment at kickoff without blocking document organization.

## Source control and vendor material

- The new repository is private. Privacy alone is not a license grant.
- Vendor `WW2City` content and associated external actor/object packages are intentionally excluded from Git. Record version, listing, local paths, hashes, and restoration instructions in Assets/.
- Do not upload raw commercial/vendor assets until acquisition rights and permitted team sharing have been verified. A local upload manifest or third-party tutorial is not proof of entitlement.
- Store permitted team-authored Unreal/model/audio binaries in Git LFS. Do not force-add ignored vendor content, engine caches, backups, local credentials, or unrelated files.
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
