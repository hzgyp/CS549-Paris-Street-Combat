# G1 squad request diagnostic and fixture correction

8 October 2026,19:10EDT. [Chinese review](MVP_G1_SQUAD_FIXTURE_DIAGNOSTIC_20261008_ZH.md).
Cases read: Failures/README, MI004, MI005, ML010, MI001 and the current closeout
and navigation trial plans. Original runtime, native assets and current703 remain
protected; this is another private wrapper, not formal gameplay adoption.

instrument_v7/squad_diagnose_v1 passes the original squad gate in round0, then
fails it in round1. Ally2 is3551.617cm from its held goal, path Idle; last request54
ends Aborted/328. Installed UE5.8 AIController.cpp StopMovement and
PathFollowingComponent.h identify328 as UserAbort|MovementStop|ForcedScript,
not native Blocked. This does not identify which policy invoked the stop.
The four-second NPC observer only covered playing, not regroup; the failed round
therefore stops at the original25s gate. Preserve that observation gap.
Moving samples hit the same debris with a walkable normal; a forward sweep hit
alone does not establish blocked NPC locomotion or mismatched nav collision.

The new cohort_nativefinish_v1/instrument_v8 corrects ONE test-input discrepancy:
on first entering the existing55cm far-bank window, leave the player's original
SimpleMoveTo request running to its natural endpoint instead of cancelling it.
The earlier successful PIE travel fixture also did not cancel it. Preserve the
same endpoint,55cm/25s squad gates, input roster, native AI and existing one-poly
trial exclusion. This is not evidence that cancellation caused the NPC failure.

Read-only observation now includes the actual controller and blackboard state
both at one-second samples and original NPC request completion: policy and squad
mode/goals, reservation IDs, PatrolEnabled, HasMoveGoal, DesiredPosition,
WaitingReason, RetryCount and HasVisibleTarget. No observer writes those values.
The full proof may run at most three fresh rounds. Stop at the FIRST original
bound, loss/error, missing observer/protected-input drift or invalid path; retain
failure. Do not add polygons, alter tolerances/timing/formation, restart aborted
NPC paths, resave assets or compensate based on unmeasured causes. On failure,
use the recorded state to propose a different bounded cause-specific correction.
This fixture's observation overhead is not unassisted human/FPS acceptance.

Early acceptance: source758/native359/current703 exact; no occupied native slot;
new build/entry identities; actual observer/1920x1080/Ready and original witnessed
polygon check pass before mission input. Natural movement finishing and both
Allies' actual original-gate arrival must be observed, never inferred from flags.
