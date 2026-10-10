# Assignment 3 MVP Development Goal Version 1

Later10October selection: the user confirms the four pillars satisfy the current
MVP, approves the revised combined outline and requests the formal PDF, then
selects the restored two-page version. It integrates pillars/test results,
AI utility/asset adaptation and four roadmap items. Rejection/pending-discussion
notes below are earlier snapshots; preserve RP001 history. See
ASSIGNMENT3_DELIVERY_BUNDLE_20261010.md for current report/download/private ZIP.
Course-platform upload and independent reviewer download remain pending.

Latest10October: the day's report is rejected. The AI/modeling addendum
supplements the original four pillars; a future report must integrate both.
First record new gameplay with live UE performance on screen, then jointly
discuss the report. RP001 retains failed drafts/reason; game and teammate
playable acceptance are preserved.

10 October2026 scope/status addendum: the user confirms a teammate's second PC
runs the shared game and is playable; packaged second-machine validation passes
by human attestation. Keep current1player/2Allies/3Germans for performance and
dynamic bottleneck tests; do not execute the earlier population-expansion plan.
The report must include AI utility and near-ten-working-day model-adaptation
cost (team estimate), hand/weapon fit, missing German firearm/new-model
difficulties, purchased detailed assets and the stopped AI character route.
Do not name the procurement channel or claim low FPS proves hardware causality.
This addendum does not rewrite the submitted Assignment2 commitments below.

Dated update,8October2026: the user confirms Assignment2 and the Assignment3
deadline13October2026. Current selected midterm scope is bridgeC/G1 capture with
working safe-save/load (now Must); city-centre stages are deferred. Mentor evidence
was not separately supplied. Later G1/closeout results and the acceptance checklist
supersede the original untested readiness/task snapshots below; no whole-MVP or
course-ready pass follows from the confirmation.

Prepared 30 September 2026 for Paris Street Combat. This is the team's first implementation target, derived from [Assignment 3 MVP Implementation and Demo](../Assignment%203_%20MVP%20Development.docx) and the [current Assignment 2 MVP](../Proposal/CS549_Assignment2_Proposal.md). Work is planned; no gameplay, compatibility, performance or delivery result is claimed. The [acceptance checklist](ASSIGNMENT3_ACCEPTANCE.md) records what must be demonstrated.

## Goal

Deliver a running Windows prototype in a surveyed connected part of France Liberation that proves the Assignment 2 core challenge: UI, animation, gunfire and physical interactions agree with authoritative gameplay state while allied and enemy NPC movement and decisions remain coordinated. Start with one Allied player, two Allied NPCs, three German NPCs and one player rifle. A reviewer must be able to play a complete mission, observe all four pillars, fail/retry and restart, and inspect repeatable evidence of navigation coordination and performance limits.

This is a functional engineering slice, not a final polished game. A city fly-through, attractive UI, concept image or character render alone does not demonstrate the promised slice. The mission's actual route, objective order and duration follow the editor survey. Reach/Clear sequences are examples; the 2-3 minute course limit applies to the demo video, not the playable mission.

## Course requirements and project interpretation

| Assignment 3 requirement | Version 1 implementation or deliverable |
|---|---|
| Assignment 2 completed and approved | Verify actual completion/approval before claiming submission readiness. Existing evidence confirms Paris concept/pillars, but not mentor assignment or Assignment 2 completion/approval. |
| Build the Assignment 2 narrow vertical slice and core pillars | Integrate all four pillars and the complete initial mission in the actual city using the mechanisms below. Report any changed/cut commitment explicitly. |
| Implement the Technical Specification and target frame rate | Blueprint-first UE5 stack; test/pin engine and plugin versions. Demonstrate measured 1080p/60 FPS performance on the declared primary machine. |
| Applicable AI integration | Record actual offline ChatGPT/Codex/ImageGen assistance and its value/cost. No runtime LLM/API is proposed. If AI-created runtime assets are claimed as part of the MVP, include and validate them; proposal concept art and the stopped pilot are not runtime dependencies. |
| 2-3 minute real-time demo with explanation and stress test | Record the running build with voiceover or text overlays; show core interactions, coordinated navigation and a measured limit. Use actual captures and readable metrics. |
| 1-2 page progress PDF | Plan vs. Reality, AI Utility, Roadmap to Final, playable-build/run entry, video link and source-code link. Do not invent results or silently omit cuts. |
| Desktop delivery | Link to a drive/itch.io upload with a compiled executable or strict run instructions. The project target is a tested packaged Windows executable. Check distribution rights for bundled assets. |
| YouTube or Vimeo video link | Upload the accepted video only when authorized; verify reviewer access and duration. |
| Public GitHub source with build instructions | The user selected the same repository: move permitted asset/history bytes to private SFTP, preserve code/docs/config/hash records, remove their old Git history and verify matching manifests before public visibility. Unresolved-rights bytes remain local-only. See actual status in the [publication review](../Submission/PUBLICATION_REVIEW.md); no separate public repository is proposed. |

## Must scope

1. **Environment and dependencies:** the selected city area loads; its collision and NavMesh support the mission. Existing licensed compatible soldier/weapon/rig/action assets work together. Preserve `/Game/WW2City` and author team content under `/Game/ParisCombat`. Record historical configuration and asset provenance; temporary compatibility placeholders are identified and do not establish final acceptance.
2. **Player and shared combat:** move/look/aim/fire/reload/damage with one rifle; player and NPC weapons share obstruction/damage rules. Health, ammo, objectives and win/fail UI read authoritative state. The initial roster is configurable and correctly registered.
3. **Animation:** usable locomotion and combat actions with acceptable hand/weapon alignment. Guard the reload transaction so ammunition transfers once and interruptions, death and restore invalidate stale events.
4. **Collision Detection:** movement respects walls/cover. Camera intent plus muzzle-path/clearance checks resolve one accepted shot and one authoritative hit. Cover cannot be bypassed by the camera; hit effects and damage agree with that result.
5. **Pathfinding and Navigation:** NavMesh/MoveTo is the baseline. Assign reachable distinct follow/support goals, retain occupied reservations, use one avoidance approach, bottleneck waiting and bounded replanning. Demonstrate a comparison against independent destination choices; NPCs do not teleport to solve stalls.
6. **NPC AI:** share Behavior Tree definitions with separate controller/Blackboard/perception state. Allies follow/regroup and support; Germans guard/patrol on foot, engage eligible visible targets and search last-seen reachable points for a bounded time before returning to role. Death stops movement/attacks and releases assignments.
7. **Mission lifecycle:** configurable intermediate objectives, nonempty fully registered Clear groups, deduplicated deaths and once-only progression. Preserve casualties/ammo during normal progression. Player death offers retry from initial state when no valid checkpoint exists; full new-mission restart restores roster, ammo, objectives, timers and transient requests.
8. **Evidence and delivery:** tested Windows build, baseline and stress measurements, four pillar demonstrations, actual AI-use record, report/video and verified reviewer-accessible links. Code/config/manifests and asset versions must identify the same delivered build.

## Should and optional scope

Checkpoints at selected safe objective boundaries remain Should. If implemented, restore objective/player/NPC snapshots, roll back later changes and clear transient state; saving alone does not heal, refill or revive. If deferred, report the cut and demonstrate initial-state retry. Supported crouch and simple impact/footstep audio are Should. Additional finite groups may be evaluated after the initial mission passes; a stress-test load is not approval to expand the shipped mission.

Custom tactical A*, hearing, exposure-weighted routing, ragdolls and improved hand IK are optional. Do not make them prerequisites for this MVP. Multiplayer, vehicles, dynamic weather, landing/ocean, broad interiors/destruction, infinite waves, runtime LLMs and renewed detailed character production remain excluded.

## Execution order

Execution correction, 2 October: [implementation v2](ASSIGNMENT3_IMPLEMENTATION_V2.md) uses the presentation stack to integrate gameplay directly on the verified Paris map, characters and motions. A minimal loop simplifies features, not the asset foundation; cosmetic refinement is deferred. Yupu resumed continuous development, pausing only for genuinely human-required review/decisions. Follow [the city gameplay work package](PARIS_CITY_GAMEPLAY_IMPLEMENTATION_V1.md): survey Paris and integrate characters, rifle, input and authoritative UMG, then establish early packaging/performance evidence and prove the four pillars. The abandoned route/caches are deleted; see [the cleanup record](ASSET_FIRST_CLEANUP_20261002.md). The goal is unchanged; incomplete items are not passed.

| Step | Work and exit evidence | Proposed lead |
|---|---|---|
| 1 Readiness | Safe Git/SFTP checks, dependency versions/rights, city survey, collision/NavMesh evidence, rig/weapon/action compatibility and first Windows package | Yupu integration; Jingdi environment/navigation; Yuqi rig/actions |
| 2 Complete loop | Initial roster, one rifle, authoritative health/ammo/HUD, configurable objectives and win/fail/retry/full restart function together | Yupu with both subsystem owners |
| 3 Four pillars | Verify action interruption, shot obstruction, independent/coordinated movement and bounded perception/behavior; fix integration failures | Yuqi animation; Yupu collision; Jingdi navigation/AI |
| 4 Performance and limits | Fixed baseline route/workload, target FPS measurements, bounded finite-load stress test; optional checkpoint evaluation and second-machine run | Yupu integration with team |
| 5 Delivery | Freeze build/source/asset identity; 2-3 minute annotated video; 1-2 page progress PDF; approved build/video/public-source access and build instructions | Yupu integration; each member supplies evidence |

Roles remain proposed until kickoff confirmation. Steps map to `DEVELOPMENT_PIPELINE.md` Gates 1-5. First complete the functional slice, then optional content. No official deadline is supplied by the Assignment 3 document; do not invent calendar commitments.

## Performance and stress method

Use the recorded i9-12900F / RTX 3080 10 GB / 32 GB Windows machine at 1920 x 1080 with declared quality/upscaling settings and exact build/engine/plugins. Warm shaders, then record the same full route and combat workload in three runs. Record mean/median/p95 frame time, average FPS, CPU/GPU timings, memory, hitches, roster/active AI and navigation stalls. The course target is 60 FPS; a proposed internal normal-load check is mean frame time at or below 16.67 ms, accompanied by p95/hitch disclosure. This check is not a claim that average FPS guarantees smoothness or that the course specified a p95 threshold. If the target is missed, record it as unmet and tune or report the deviation.

Run a separate finite configured stress scenario at a reproducible bottleneck, increasing active NPC load in measured steps between reset runs. Set a finite upper bound before testing; stop at that bound, a clear performance/navigation failure or instability. Show at least one observed limiting condition, without indefinite spawning, concealment of engaged NPCs or revival during a run. Compare independent versus coordinated destinations at matched loads. Record the tested limit, including if failure occurs in the initial roster; do not predeclare an unsupported maximum. Stress FPS may fall below the normal-load target, and that limit must be shown honestly.

## Submission and open items

Use the [acceptance checklist](ASSIGNMENT3_ACCEPTANCE.md) to record results rather than marking this plan complete. SFTP baselines were previously hash-verified on the server; second-machine restoration and Unreal validation are separate checks. New implementation work starts with the [team synchronization manual](../../Assets/TEAM_SYNC_WORKFLOW.md), including protection of ignored local edits.

Verify Assignment 2 completion/approval, mentor evidence and official deadline; select compatible finished soldier/rifle/action assets and historical configuration; perform the city survey and engine/package tests; resolve public-source access and permitted build distribution; produce and verify all delivery links. None is assumed complete merely because a plan or source folder exists.

Chinese review counterpart: [Assignment 3 Goal V1 in Chinese](ASSIGNMENT3_GOAL_V1.md). Keep scope, priorities and acceptance conditions synchronized when editing either version.
