# Project index

Current scope: an initial configurable six-soldier roster across a surveyed connected city area with configurable objectives, retry and full restart. Reach/Clear sequences are examples. NavMesh/MoveTo is the baseline; custom A* is optional and safe-boundary checkpoints are Should. Current work targets Assignment 3's running MVP and delivery evidence. Later finite NPC groups require pacing, navigation and performance evaluation.

## Active authority

- [Assignment 3 asset-first MVP implementation v2](Docs/Development/ASSIGNMENT3_IMPLEMENTATION_V2.md)
- [Existing-city gameplay implementation v1](Docs/Development/PARIS_CITY_GAMEPLAY_IMPLEMENTATION_V1.md)
- [Actual-city setup/input results, 2 October](Docs/Development/PARIS_CITY_GAMEPLAY_RESULT_20261002.md)
- [Combat/HUD increment implementation](Docs/Development/PARIS_COMBAT_AND_HUD_IMPLEMENTATION_V1.md)
- [Actual-city combat/HUD result and human review](Docs/Development/PARIS_COMBAT_AND_HUD_RESULT_20261002.md)
- [Early actual-city Windows packaging work package](Docs/Development/PARIS_WINDOWS_PACKAGE_IMPLEMENTATION_V1.md)
- [Early Paris package readiness/result checkpoint](Docs/Development/PARIS_WINDOWS_PACKAGE_RESULT_20261002.md)
- [Paris navigation and shared AI work package](Docs/Development/PARIS_NAVIGATION_AND_AI_IMPLEMENTATION_V1.md)
- [Actual Paris navigation checkpoint](Docs/Development/PARIS_NAVIGATION_RESULT_20261002.md)
- [Current seven package-entry draft hashes](Assets/Integration/CITY_PACKAGE_DRAFT_INVENTORY_20261002.json)
- [Current seven unpublished city/combat/HUD package hashes](Assets/Integration/CITY_COMBAT_DRAFT_INVENTORY_20261002.json)
- [Historical five-package S1 checkpoint](Assets/Integration/CITY_GAMEPLAY_DRAFT_INVENTORY_20261002.json)
- [Asset-first correction and completed cleanup, 2 October](Docs/Development/ASSET_FIRST_CLEANUP_20261002.md)

- [New-session handoff](HANDOFF.md)
- [Agent rules](AGENTS.md)
- [Scope reset](Docs/Decisions/SCOPE_RESET.md)
- [Team and ownership](Docs/Decisions/TEAM_AND_OWNERSHIP.md)
- [Proposal](Docs/Proposal/PROJECT_PROPOSAL.md)
- [Assignment 1 proposal PDF](Docs/Proposal/CS549_Assignment1_Proposal.pdf)
- [Assignment 2 proposal PDF](Docs/Proposal/CS549_Assignment2_Proposal.pdf)
- [Editable reports and current version notes](Docs/Proposal/README.md)
- [Proposal image sources](Docs/Proposal/Visuals/README.md)
- [Current street concept](Docs/Proposal/Visuals/paris-six-character-concept.png)
- [Street concept prompt and reference inputs](Docs/Proposal/Visuals/STREET_MOCKUP_PROMPT.md)
- [Current game flowchart](Docs/Proposal/Visuals/paris-mission-flowchart.svg)
- [Editable mission flow](Docs/Proposal/Visuals/paris-mission-flowchart.mmd)
- [Pipeline](DEVELOPMENT_PIPELINE.md)
- [Technical design](Docs/Design/TECHNICAL_DESIGN.md)
- [Assignment 3 goal version 1](Docs/Development/ASSIGNMENT3_GOAL_V1.md)
- [Assignment 3 acceptance checklist](Docs/Development/ASSIGNMENT3_ACCEPTANCE.md)
- [Character and weapon implementation plan](Docs/Development/CHARACTER_AND_WEAPON_IMPLEMENTATION_V1.md)
- [Character integration results, 1 October](Docs/Development/CHARACTER_INTEGRATION_RESULT_20261001.md)
- [Directional locomotion and lifecycle results, 1 October](Docs/Development/CHARACTER_LOCOMOTION_LIFECYCLE_RESULT_20261001.md)
- [Weapon and first-person capability decision](Docs/Development/WEAPON_CAPABILITY_REVIEW_20261001.md)
- [Selected baseline and simplified reload plan](Docs/Development/WEAPON_BASELINE_AND_SIMPLIFIED_RELOAD_V1.md)
- [Verified baseline and bounded reload result, 2 October](Docs/Development/WEAPON_BASELINE_AND_RELOAD_RESULT_20261002.md)
- [Private diagnostic snapshot hashes (not Catalog restore authority)](Assets/Integration/RELOAD_DRAFT_SNAPSHOT_20261002.json)
- [Unpublished local draft hashes (not restore authority)](Assets/Integration/LOCAL_DRAFT_INVENTORY_20261001.json)
- [Submission status](Docs/Submission/STATUS.md)
- [Assignment 2 requirements review](Docs/Submission/ASSIGNMENT2_REQUIREMENTS_REVIEW.md)
- [Approval update email draft](Docs/Submission/APPROVAL_EMAIL_DRAFT.md)

## Assets and working environment

- [Asset policy, inventory and restoration](Assets/README.md)
- [3D asset inventory and acquisition gaps](Assets/3D_ASSET_AUDIT.md)
- [Chinese model search checklist](Assets/3D_ASSET_AUDIT_ZH.md)
- [Character compatibility tests and repair plan](Assets/CHARACTER_COMPATIBILITY_AND_REPAIR.md)
- [Current authoritative asset catalog](Assets/Sync/CATALOG.json)
- [Git/SFTP migration and source publication status](Assets/Sync/PUBLICATION_STATUS.json)
- [Source publication checks and recovery](Docs/Submission/PUBLICATION_REVIEW.md)
- [Asset register](Assets/ASSET_REGISTER.csv)
- [File copy manifest](Assets/MIGRATION_MANIFEST.json)
- [Local vendor dependency](Assets/VENDOR_DEPENDENCY.json)
- [Working project](Unreal/ParisStreetCombat/WW2FranceLiberation.uproject)
- [Gunplay reuse candidates](Reference/Gunplay/README.md)
- [Primary workstation reference](Reference/Workstations/PRIMARY_WORKSTATION.md)

## History and course

- [History index](HistoricalReference/README.md)
- [Paris context](HistoricalReference/Paris1944/CONTEXT.md)
- [Paris source register](HistoricalReference/Paris1944/SOURCES.csv)
- [Paris image reference register](HistoricalReference/Paris1944/IMAGE_REFERENCES.csv)
- [Open history checks](HistoricalReference/Paris1944/RESEARCH_GAPS.md)
- [Normandy background](HistoricalReference/NormandyContext/README.md)
- [Assignment 1](Course/Assignments/Assignment%201.docx)
- [Assignment 2](Course/Assignments/Assignment%202.docx)
- [Assignment 3 source requirements](Docs/Assignment%203_%20MVP%20Development.docx)

## Inactive provenance and reproducible document build

- [Archive index](Archive/README.md)
- [Transition record](Archive/TRANSITION_RECORD.json)
- [Current assignment proposal builder](Tools/build_assignment_proposals.py)
- [Current game flowchart builder](Tools/build_mission_flowchart.py)
- [Superseded combined proposal builder](Tools/build_proposal.py)

Only the active-authority documents govern new work. Files under Archive, Reference/Gunplay, and HistoricalReference/NormandyContext do not reactivate the former project requirements.
