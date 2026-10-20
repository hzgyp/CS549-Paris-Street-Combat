# Project index

**Current launch path, 18 October 2026:** use [the formal tutorial launcher](Releases/Paris-Tutorial-1.0-20261017/PLAY_TUTORIAL.cmd). The root forwarding CMD has been removed at the human’s request; existing saves/settings and the formal package are unchanged. [Routing result](Docs/Development/MissionLoopV1/TUTORIAL_DIRECT_ENTRY_RESULT_20261018.md). Older dated version/acceptance notes below are retained as history.

<!-- prone-observer-candidate-20261014 -->
14October：[V观察与Z匍匐复查](Docs/Development/MissionLoopV1/PRONE_OBSERVER_RESULT_20261014_ZH.md)已准备独立试玩。平地原地V→Z通过，优化避墙镜头与拒绝提示；保留原地形保护，原人工精确现场待复测，正式86保持。

<!-- prone-transition-candidate-20261014 -->
14October[Z匍匐过渡93结果](Docs/Development/MissionLoopV1/PRONE_TRANSITION_RESULT_20261014_ZH.md)及[独立普通入口](tmp/Playtest-G1-ProneTransition-20261014/PLAY_PRONE_TRANSITION.cmd)已准备，17次同Game和65帧有限复验通过，人工待试玩；父受伤89整版已获认可，正式86保持。

<!-- player-damage-feedback-candidate-20261014 -->
14 October[玩家受伤反馈89独立试玩](Docs/Development/MissionLoopV1/PLAYER_DAMAGE_FEEDBACK_RESULT_20261014_ZH.md)：18次同Game检查及实际画面/混音通过，人工待审；[普通入口](tmp/Playtest-G1-PlayerDamageFeedback-20261014/PLAY_DAMAGE_FEEDBACK.cmd)，正式86保持。

<!-- player-damage-feedback-plan-20261014 -->
14 October玩家受伤反馈：[只读核查与待确认修复方案](Docs/Development/MissionLoopV1/PLAYER_DAMAGE_FEEDBACK_PLAN_20261014_ZH.md)。正式86已有血量/低血量变红，缺非致命瞬时提示与受伤音分支；建议红色边缘脉冲、扣血残影、重伤警告及短受伤音。方案未实施，正式入口不变。

<!-- grenade-formal-adoption-20261014 -->
14 October当前本机正式投掷/开发基线为已人工审核86版，使用 [PLAY_TUTORIAL.cmd](Releases/Paris-Tutorial-1.0-20261017/PLAY_TUTORIAL.cmd)。[采用与清理](Docs/Development/G1_GRENADE_BASELINE_ADOPTION_20261014_ZH.md)；原模型/原生动画/用户档保留，现有远端/教师交付不变。

<!-- grenade-pose-repair-v8-20261014 -->
**14 October最新进度：** [手雷初始姿势修复v8结果](Docs/Development/MissionLoopV1/GRENADE_POSE_REPAIR_RESULT_20261013_ZH.md)：旧手侧v3被用户拒绝，历史功能检查保留。新source86/Gamev8通过11项实际检查及25张过渡/持握/投掷画面复验，人工待审核，正式78保持；其他动作缺口暂缓。

<!-- grenade-hand-repair-v3-20261013 -->
[Grenade hand repair with traversal](Docs/Development/MissionLoopV1/GRENADE_HAND_REPAIR_RESULT_20261013.md) / [手雷与翻越一起试玩](Docs/Development/MissionLoopV1/GRENADE_HAND_REPAIR_RESULT_20261013_ZH.md)，source84/finalv3、九项最终Game检查通过，人工待审核，正式78保持。

<!-- grenade-hand-repair-v2-20261013 -->
[Grenade hand repair with traversal](Docs/Development/MissionLoopV1/GRENADE_HAND_REPAIR_RESULT_20261013.md) / [手雷与翻越一起试玩](Docs/Development/MissionLoopV1/GRENADE_HAND_REPAIR_RESULT_20261013_ZH.md)，source84/finalv2、九项最终Game检查通过，人工待审核，正式78保持。

<!-- traversal-input-repair-v13-20261013 -->
[Traversal input repairv13 / new manual entry](Docs/Development/MissionLoopV1/TRAVERSAL_INPUT_REPAIR_RESULT_20261013.md) · [翻越贴箱修复](Docs/Development/MissionLoopV1/TRAVERSAL_INPUT_REPAIR_RESULT_20261013_ZH.md) · [Confirmed grenade hand-side issue](Docs/Development/MissionLoopV1/GRENADE_HAND_SIDE_AUDIT_20261013.md). Human traversal review pending; formal78 unchanged. Earlierv8 references retain historical scope.

Current scope: an initial configurable six-soldier roster across a surveyed connected city area with configurable objectives, retry and full restart. Reach/Clear sequences are examples. NavMesh/MoveTo is the baseline; custom A* is optional and safe-boundary checkpoints are Should. Current work targets Assignment 3's running MVP and delivery evidence. Later finite NPC groups require pacing, navigation and performance evaluation.

## Active authority

- [Independent low-obstacle traversal, source83; human review pending](Docs/Development/MissionLoopV1/LOW_OBSTACLE_TRAVERSAL_RESULT_20261013.md) / [翻越回交结果，正式78保持](Docs/Development/MissionLoopV1/LOW_OBSTACLE_TRAVERSAL_RESULT_20261013_ZH.md) / [current candidate](Docs/Development/CURRENT_TRAVERSAL_REVIEW.json)

- [Team playtest restore and launch](Docs/Development/TEAM_PLAYTEST.md) / [组员中文试玩指南](Docs/Development/TEAM_PLAYTEST_ZH.md)
- [Team publication implementation](Docs/Development/TEAM_PLAYTEST_PUBLICATION_IMPLEMENTATION_V1.md) / [中文实施](Docs/Development/TEAM_PLAYTEST_PUBLICATION_IMPLEMENTATION_V1_ZH.md)
- [Verified native playtest publication](Assets/Sync/NATIVE_PLAYTEST_PUBLICATION_STATUS.json)
- [Team playtest publication result](Docs/Development/TEAM_PLAYTEST_PUBLICATION_RESULT_20261003.md) / [中文结果](Docs/Development/TEAM_PLAYTEST_PUBLICATION_RESULT_20261003_ZH.md)
- [Selected runtime dependency manifest](Assets/Sync/manifests/paris-gameplay-native-playtest.json)

- [Native first-person display migration](Docs/Development/CONTINUOUS_ARMS_NATIVE_IMPLEMENTATION_V1.md) / [中文实施](Docs/Development/CONTINUOUS_ARMS_NATIVE_IMPLEMENTATION_V1_ZH.md)
- [Selected native display result](Docs/Development/CONTINUOUS_ARMS_NATIVE_RESULT_20261003.md) / [中文结果](Docs/Development/CONTINUOUS_ARMS_NATIVE_RESULT_20261003_ZH.md)
- [Current 43 native file checkpoint](Assets/Integration/CITY_CONTINUOUS_ARMS_NATIVE_INVENTORY_20261003.json)
- [Remaining model and animation requirements](Docs/Development/ASSET_GAPS_20261003.md) / [明日咸鱼清单](Docs/Development/ASSET_GAPS_20261003_ZH.md)
- [Current character model refinement and action review](Docs/Development/CHARACTER_MODEL_ACTION_REVIEW_20261013.md) / [最新建模微调与动作审核状态](Docs/Development/CHARACTER_MODEL_ACTION_REVIEW_20261013_ZH.md)

- [Complete existing upper limbs experiment V3](Docs/Development/FIRST_PERSON_CONTINUOUS_ARMS_IMPLEMENTATION_V3.md) / [中文审阅](Docs/Development/FIRST_PERSON_CONTINUOUS_ARMS_IMPLEMENTATION_V3_ZH.md)
- [Continuous arms static result and accepted direction](Docs/Development/FIRST_PERSON_CONTINUOUS_ARMS_RESULT_20261003.md) / [中文结果](Docs/Development/FIRST_PERSON_CONTINUOUS_ARMS_RESULT_20261003_ZH.md)
- [Continuous arms motion validation](Docs/Development/CONTINUOUS_ARMS_DYNAMIC_IMPLEMENTATION_V1.md) / [中文实施](Docs/Development/CONTINUOUS_ARMS_DYNAMIC_IMPLEMENTATION_V1_ZH.md)
- [Continuous arms motion and muzzle result](Docs/Development/CONTINUOUS_ARMS_DYNAMIC_RESULT_20261003.md) / [中文结果](Docs/Development/CONTINUOUS_ARMS_DYNAMIC_RESULT_20261003_ZH.md)
- [Unselected continuous-arm derivative hashes](Assets/Integration/CONTINUOUS_ARMS_TRIAL_INVENTORY_20261003.json)

- [Mandatory failure-case review](Failures/README.md)
- [FP001 failure analysis and archive](Failures/FP001-20261003-first-person-view/FAILURE_ANALYSIS.md)
- [Archive implementation and verification order](Docs/Development/FAILURE_ARCHIVE_IMPLEMENTATION_20261003.md)
- [V3-based first-person rebuild V2](Docs/Development/FIRST_PERSON_PRESENTATION_REBUILD_V2.md) / [中文审阅](Docs/Development/FIRST_PERSON_PRESENTATION_REBUILD_V2_ZH.md)
- [V2 static result: self-obstruction, no candidate selected](Docs/Development/FIRST_PERSON_PRESENTATION_REBUILD_RESULT_20261003.md) / [中文结果](Docs/Development/FIRST_PERSON_PRESENTATION_REBUILD_RESULT_20261003_ZH.md)

- [Approved bounded rifle crosshair alignment and runtime-only review scope](Docs/Development/RIFLE_CROSSHAIR_ALIGNMENT_IMPLEMENTATION_V4.md)
- [Measured rigid fitting failure and unchanged city checkpoint](Docs/Development/RIFLE_CROSSHAIR_ALIGNMENT_RESULT_20261002.md)

- [Weapon holding, shot feedback and player actions implementation](Docs/Development/WEAPON_PRESENTATION_AND_PLAYER_ACTIONS_V1.md)
- [Gun-only walking/reload attachment implementation](Docs/Development/RIFLE_ACTION_ATTACHMENT_IMPLEMENTATION_V3.md)
- [Gun-only action trial results and residual contact gaps](Docs/Development/RIFLE_ACTION_ATTACHMENT_RESULT_20261002.md)
- [Current unpublished city/rifle-action draft hashes](Assets/Integration/CITY_RIFLE_ACTION_DRAFT_INVENTORY_20261002.json)
- [Historical transform-only correction and human residual-error report](Docs/Development/WEAPON_TRANSFORM_ONLY_RESULT_20261002.md)
- [Rejected finger-layer repair history](Docs/Development/WEAPON_GRIP_REPAIR_RESULT_20261002.md)
- [Historical rejected city/grip hashes](Assets/Integration/CITY_WEAPON_GRIP_DRAFT_INVENTORY_20261002.json)
- [Read-only player-action candidate and preservation record](Assets/Integration/PLAYER_ACTION_CANDIDATES_20261002_V2.json)

- [Assignment 3 asset-first MVP implementation v2](Docs/Development/ASSIGNMENT3_IMPLEMENTATION_V2.md)
- [Existing-city gameplay implementation v1](Docs/Development/PARIS_CITY_GAMEPLAY_IMPLEMENTATION_V1.md)
- [Actual-city setup/input results, 2 October](Docs/Development/PARIS_CITY_GAMEPLAY_RESULT_20261002.md)
- [Combat/HUD increment implementation](Docs/Development/PARIS_COMBAT_AND_HUD_IMPLEMENTATION_V1.md)
- [Actual-city combat/HUD result and human review](Docs/Development/PARIS_COMBAT_AND_HUD_RESULT_20261002.md)
- [Early actual-city Windows packaging work package](Docs/Development/PARIS_WINDOWS_PACKAGE_IMPLEMENTATION_V1.md)
- [Early Paris package readiness/result checkpoint](Docs/Development/PARIS_WINDOWS_PACKAGE_RESULT_20261002.md)
- [Paris navigation and shared AI work package](Docs/Development/PARIS_NAVIGATION_AND_AI_IMPLEMENTATION_V1.md)
- [Actual Paris navigation checkpoint](Docs/Development/PARIS_NAVIGATION_RESULT_20261002.md)
- [Navigation-only retained foundation work package and stop boundary](Docs/Development/PARIS_NAVIGATION_FOUNDATION_IMPLEMENTATION_V1.md)
- [Retained navigation result and outstanding limits](Docs/Development/PARIS_NAVIGATION_FOUNDATION_RESULT_20261002.md)
- [Historical seven pre-presentation retained-navigation draft hashes](Assets/Integration/CITY_NAVIGATION_DRAFT_INVENTORY_20261002.json)
- [Historical seven pre-navigation package-entry hashes](Assets/Integration/CITY_PACKAGE_DRAFT_INVENTORY_20261002.json)
- [Historical seven city/combat/HUD package hashes](Assets/Integration/CITY_COMBAT_DRAFT_INVENTORY_20261002.json)
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

14 October清理完成：[正式86采用与清理结果](Docs/Development/G1_GRENADE_BASELINE_ADOPTION_RESULT_20261014_ZH.md)，48目录已删除，D盘实测净增加15.37GiB；原源码/证据/资产/用户文件保留，平台formal86已读回。
