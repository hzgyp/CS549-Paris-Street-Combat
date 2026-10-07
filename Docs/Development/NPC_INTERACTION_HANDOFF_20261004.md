# Lane B handoff — NPC interaction

4 October 2026. Execute only when the user opens/assigns this conversation.
Chinese review: [_ZH](NPC_INTERACTION_HANDOFF_20261004_ZH.md).
The new request resumes bounded NPC interaction after the historical navigation
pause; it does not authorize unrelated mission/asset/presentation work.

## Start here

Read AGENTS, HANDOFF, Failures/README, PARALLEL_GAMEPLAY_WORKFLOW_20261004,
NPC_BEHAVIOR_DRAFT_V1 revision3, TECHNICAL_DESIGN, Assignment3 goal/acceptance,
PARIS_NAVIGATION_FOUNDATION_RESULT_20261002, PLAYER_ACTIONS_RESULT_20261003 and
GERMAN_RIFLE_UE_AND_ACTION_RESULT_20261004. Review AN003/FP001 and the indexed
blocked-motion/navigation failures. The latest user split supersedes old global
AI-stop wording only within this handoff's scope; old plans remain historical.
Write a lane-specific implementation before edits: cases read, changed approach,
storage/packages, early check, tests and stopping condition.

## Independent scope / ownership

Own new source under Tools/Integration/NPCInteractionV1/, documents under
Docs/Development/NPCInteractionV1/, native packages under
/Game/ParisCombat/AI/NPCInteractionV1/, private evidence under workspace
Evidence/NPCInteractionV1/<unique-id>. Existing Content physical home remains
Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Content.
Do not edit shared combatant/player/FP owner/arms/clips, formal city, configuration,
Catalog/releases, AGENTS/HANDOFF or another lane's tools. Derived equipped NPC
trial classes use new names and preserve existing faction meshes/AnimBPs; inspect
actual parents/signatures rather than guessing them or using the player class.

Initially work offline while A owns the native slot. Before any UE author/test,
obtain the coordinator's explicit release/slot, check current processes and514
starting guards, then inventory B's additions. No simultaneous game/lab writers.

## Behavior to implement, in bounded stages

1. **B0 contract:** survey actual six-actor roster/parents/TeamId and shared entries.
   One AIController/BT definition, private controller/BB/memory per five NPCs;
   proposed action adapter has observable request/result/generation, not strings
   pretending to move/shoot. Define capability flags and decline missing actions.
2. **B1 one NPC:** faction-filtered sight, guard/foot patrol, ordinary MoveTo/stop,
   finite waiting/replan, lifecycle cancellation. Early proof: two NPCs cannot
   share last-seen memory; sight loss stops tracking hidden target coordinates.
3. **B2 two Allies:** distinct follow/regroup/support reservations, retain after
   arrival through idle/fire/reload, release on reassignment/failure/death/restore.
   Short pursuit bounds both player distance and accumulated chase movement;
   target switch/tree reevaluation cannot reset budget. Compare independent vs
   coordinated destinations on matched starts/goals/load. Use one avoidance method.
4. **B3 three Germans:** guard/foot patrol, observed-target combat intent, last-seen
   finite reachable search, timeout/no points returns to role; reacquisition only
   restores live target tracking. Unarmed actors can sense/move, never damage.
5. **B4 equipment/transactions:** reuse existing licensed M1 and accepted German
   model's tested nativeV2 candidate only after fresh per-faction equip/collision/
   muzzle/contact checks. No remodel/purchase or silent modern/M1 German substitute.
   RequestFire uses NPC origin/direction; preserve authoritative shot/reload/death.
   Generic full-body reload remains a provisional visual limitation, not FP repair.
6. **B5 six-actor interaction:** stop→face→legal fire, reload gating, recipient
   survival/death, target clearing/reservation release/stale callback rejection.
   Draft one shared FriendlyFireEnabled config and precise shared damage patch:
   on damages actual friendly once; off no friendly damage; bodies block in both,
   AI avoids friendly lanes; no faction change/retaliation. Coordinator applies
   shared-base integration, then test player and both factions as shooters.

Use draft decision trees and action leaves A00/A01/A02/A03/A04/A05/A07/A08/A10.
NPC jump/crouch/prone remain disabled; no ADS, hearing, reinforcement waves,
RL training, VFX, mission/checkpoint/pacing/publication work. Initial tuning10m
chase/15s search/follow3–6m/regroup10m/separation1.5m is configurable/provisional,
not a final user-specified distance/time. Retained NavMesh is not whole-city pass.

## Required proof and handoff back

Check actual continuous movement/stop and gait; complete paths only, two bounded
replans, no teleport/infinite retry. Check faction exclusion/private memory,
search timeout, chase budget, reservations after arrival and on death, stale
move/search/reload events, finite casualty persistence, unarmed rejection,
world/friendly obstruction, ammo conservation and friendly damage on/off.
Every trace maps condition→TaskID→action request→admission/reason→physical outcome.
Tree compile/BB values do not prove an action or finished AI.

Stop on ownership/hash conflict, unsupported graph authoring before expanding,
or capability/history choice needing user authority. Preserve errors and failed
identities. A missing FP fix does not block noncombat behavior; missing equipment
does block claims of armed combat acceptance.
Return own implementation/result, exact new file/dependency/hash inventory,
actual tests/failures, proposed shared damage/equip merge and compatibility limits.
Do not select/save the formal city, package, publish, commit or push automatically.
