# NPC behavior design draft

**4 October execution handoff:** the user now requests scoped NPC interaction in
another user-opened conversation while this conversation repairs reload. Follow
`../Development/NPC_INTERACTION_HANDOFF_20261004.md` and the parallel workflow;
the prior design-only/global-pause statements below are historical, not runtime
acceptance. Three confirmed behavior choices remain unchanged. The German source
rifle model is now accepted, with a tested unselected nativeV2 candidate; older
blanket missing-model statements are superseded, while NPC trigger/contact,
historical/equip/armed-AI acceptance remain open. Noncombat behavior need not wait
for FP cosmetics; combat still requires per-faction capability tests. No tree was
implemented by this addendum; shared-base/map changes are coordinator-owned.

3 October 2026, revision 3. Yupu confirms short-distance Allied pursuit, configurable friendly damage and time-limited German search on sight loss. Organized as conditions, intent, executable actions and completion/rejection feedback: follow/patrol/search cannot remain abstract terminal labels. Keep the stable filename and synchronize the Chinese review. This is design only, not AI implementation, asset selection/publication or human visual acceptance. Retain the existing Paris assets and tested foundation.

## Action leaves and capability status

A-labels are design identifiers, not existing UE function names. Composite leaves execute in arrow order, after actor/rig/weapon/posture/collision/lifecycle admission. A rejected request must enter a defined idle/wait fallback, never merely update Blackboard and claim motion occurred.

| Label | Physical action | Evidence and integration limit |
| --- | --- | --- |
| A00 | Stop and idle; ordinary holding with a valid weapon | Reuse current stance/holding; unarmed actors create no hidden weapon/damage |
| A01 | Walk to an assigned point, then A00 | Existing stride/MoveTo foundation tested; shared NPC gait/request adapter pending |
| A02 | Run to an assigned point, then A00 | Player V6 functionally tested; per-faction NPC adapter pending; no running fire/reload |
| A03 | Low-speed walk to a check point, then A00 | Player V6 functionally tested; not stealth/hearing acceptance |
| A04 | Stop, stand, face target, hold and request authoritative shot | Player transactions/obstruction/ammo tested; NPC integration, existing Rifle_ShootOnce candidate adaptation and recoil/muzzle effects unaccepted; not ADS |
| A05 | Stop, stand, hold and simplified reload, then A00 | Existing conservation/interruption tested; generic clip, not M1-specific; NPC adapter pending |
| A06 | Jump, fall/land and restore legal idle/movement | Player V6 functionally tested; NPC NavLinks/landing unaccepted, disabled initially |
| A07 | Play death once, then remain Dead | Existing lifecycle tested; never restart death on every tree evaluation |
| A08 | Stop movement/attack, idle and wait with bounds | Stop capability exists; NPC reason/deadline/recovery pending, not a new wait clip |
| A09 | Mission-authorized reset/snapshot restoration | Unit reset tested, mission checkpoint restore unimplemented; no autonomous revive/refill |
| A10 | Face/turn while idle or moving | Proposed UE actor/controller orientation; NPC integration/foot contact untested; dedicated turn-in-place/head-eye scan clips unaccepted |
| A11 | Crouch/directional crouch-walk, stand when clear | Player V6 numeric pass, visual/faction NPC adaptation pending; initially disabled, no crouched fire/reload |
| A12 | Prone/forward-back crawl, stand when clear | Player V6 bounded collision pass, visual/NPC adaptation pending; initially disabled, no prone fire/strafe/yaw |

Stop/observe/face-target may be stance and orientation combinations, not dedicated animation files. Authoritative shooting, body shooting animation, muzzle flash and hit feedback have separate acceptance. Unverified hit-reaction/turn/victory clips remain explicit gaps, never assumed complete or permission for detailed character production. Evidence: `Docs/Development/PLAYER_ACTIONS_RESULT_20261003.md` and `WEAPON_PRESENTATION_AND_PLAYER_ACTIONS_V1.md`.

## Shared definitions and private state

Two Allied NPCs and three German NPCs use one shared AIController and Behavior Tree definition, with separate controller, Blackboard, target memory and action state per instance. Configure Team, Role, EncounterGroup, PatrolRoute and SearchZone. Additional finite groups depend on survey, pacing and measured performance; never use infinite replacement waves.

The tree selects intent, the action layer admits or rejects it, and navigation establishes reachability. Existing shot/damage/reload/death/restore interfaces remain authoritative. AI must not assign ammunition directly, shoot through obstruction or infer a hit from completed animation.

## Priority selector

Choose the first applicable branch, in order. A higher priority interrupts lower tasks, cancels the move request, releases reservations and invalidates stale callbacks by lifecycle generation.

```text
Per-NPC priority selector (first applicable branch, top to bottom)
|-- 1 Self dead?
|   `-- Cancel move/reload/reservation -> A07 death once -> remain Dead
|-- 2 Mission frozen/failed?
|   `-- Cancel task -> A08 stop/idle; await mission-authorized A09
|-- 3 Current action cannot be directly preempted?
|   |-- Legal reload running -> continue A05; no shooting
|   `-- Cancellation/transition required -> safely cancel/finish -> A08 -> reevaluate
|-- 4 Actually visible living hostile?
|   `-- Combat subtree, terminating in A00/A01/A02/A04/A05/A08/A10
|-- 5 Unexpired last-seen memory?
|   |-- Allied -> A00+A10 brief alert -> Allied role subtree, no unlimited chase
|   `-- German -> A01/A03 finite reachable check points -> A00+A10 inspection
|                deadline/points exhausted -> German role subtree
`-- 6 No combat/search task
    |-- Allied -> Allied role subtree
    `-- German -> German role subtree
```

Initial NPC policies never request A06/A11/A12. If an unexpected low posture persists, await legal restoration; blocked standing retains that posture plus A08, never forced uncrouch/fire. Death/freeze can still safely interrupt the action gate.

Move recovery is local to each MoveTo task, not a permanent global branch above combat: bounded waiting, at most two replans, then Waiting with a reason. No teleport or endless retry. Perception still updates while waiting; a newly visible hostile can abort the old move and enter legal combat, so a blocked route does not prevent reacting to an enemy in front.

Ordinary holding is not ADS; this increment adds no ADS. Initial AI combat uses accepted standing actions. Crouch/prone policies require both runtime action and rifle-contact acceptance, not merely player buttons.

## Combat subtree

```text
Visible hostile (recheck before each shot, no stale visibility admission)
|-- Allied has no valid living player, or short-pursuit distance envelope exceeded?
|   `-- Cancel chase move -> Allied role regroup/wait; visible hostile does not waive the bound
|-- No valid weapon? -> A00+A10 alert, no ammo use/invisible damage
|-- Weapon exists but loaded rounds zero?
|   |-- Reserve exists and action gate allows -> A05 standing reload -> reevaluate
|   `-- No reserve/cannot reload -> A08 with reason, no automatic refill
`-- Loaded ammunition available
    |-- Range/role envelope forbids shooting?
    |   |-- Allied approved reachable point and pursuit budget allows -> short-pursuit subtree
    |   |-- German approved reachable point within role -> A01/A02 move -> A00
    |   |-- Self already outside allowed role envelope -> role return subtree, no further chase
    |   `-- Inside envelope but no legal point -> A00+A10 alert
    `-- Range/role allows
        |-- World/friendly blocks sight or barrel/muzzle?
        |   |-- Alternate reserved point reachable -> A01 move -> A00 -> reevaluate
        |   `-- No legal point -> A08; keep sensing, no wall/friendly penetration
        `-- Fire paths legal
            |-- Running/low/reloading/cooldown? -> safely stop/restore -> A00 or continue A05
            |-- Facing not ready? -> A00+A10 turn; do not shoot yet
            `-- Ready standing and facing legal -> A04 shot -> A00 during cooldown -> reevaluate
```

Finding/reserving/querying points are prerequisites, not character-action leaves. Every result ends in movement/arrival-idle or rejection/wait. Use A10 for facing. Full ADS, leaning and wall-hugging/cover-specific clips are not implicit capabilities.

```text
A04 requests a shot; original transaction rejects or discharges
|-- Close-wall/friendly clearance rejects discharge -> no shot/damage; retain existing rejected-shot ammo policy
|-- Discharged shot first hits world -> no character damage -> shooter A00/reposition; effects pending
|-- Discharged shot first hits friendly -> read shared FriendlyFireEnabled
|   |-- Off -> no friendly health loss, no penetration to hostile behind
|   `-- On -> apply normal damage once to that friendly -> survival/death result below
`-- First hit hostile, or friendly with friendly damage enabled -> normal damage outcome
    |-- Recipient survives -> update authoritative health -> continue legal action
    |                        hit-reaction clip unaccepted, no invented stun/fall
    `-- Recipient dies -> A07 -> cancel its move/reload/reservation
                          other NPCs clear dead target; finite casualty ledger, no replacement waves
```

## Faction interaction

| Situation | Allies | Germans |
| --- | --- | --- |
| No enemy sight | Follow player at distinct positions; regroup when behind | Guard or foot patrol |
| Visible enemy and clear fire path | Allow short pursuit; stop at distinct support points and fire | Interrupt patrol and fire |
| Obstructed shot | Wait or move to reachable support; no wall penetration | Alert or choose another reachable firing point |
| Lost target | Brief alert then regroup; bounded separation | Inspect last seen area until timeout, then resume role |
| Friendly bottleneck | Later arrival waits and replans/reserves another point | Same bounded recovery |
| Casualty | Update genuine death ledger; no replacement spawning | Same persistence |

Confirmed: shared FriendlyFireEnabled covers the player and both NPC factions. On applies normal damage to an actually hit friendly; off prevents friendly damage. Friendly bodies block shots in both modes, never pass through to a hostile behind. Initial value retains the currently tested off mode; configuration switching/on-mode behavior is unimplemented and untested, not established by the old off-mode regression. AI avoids firing through friendly-obstructed lanes in both modes; an actual hit such as a friendly entering a previously clear shot path goes through the shared damage entry. Avoidance does not create global friendly immunity. Accidental friendly damage never changes Team or starts retaliation/defection. Faction-filter perception, never expose hidden enemy positions. Sound propagation, suppression, grenades, vehicles and complex tactics are out of the first slice.

## Allied role subtree

```text
Allied with no higher-priority task
|-- No valid living player? -> A08 stop/idle, await mission handling
|-- Player distance exceeds regroup threshold?
|   |-- Distinct regroup point has complete path -> A02 run there -> A00
|   `-- Unreachable/reserved bottleneck -> bounded recovery subtree
|-- Outside follow band, or moving player invalidates follow point?
|   |-- Own reserved follow point reachable -> A01 walk (A02 if catch-up allowed) -> A00
|   `-- Unreachable/reserved bottleneck -> bounded recovery subtree
`-- Already in suitable follow/support position
    |-- Another distinct point needed, clear of player firing lane -> A01 move -> A00
    `-- No move needed -> A00 ordinary holding+A10 legal alert direction
```

Confirmed: Allies may pursue a short distance while retaining player-support and regroup bounds. Remaining stationary in a suitable position is an actual valid action, not an AI failure.

```text
Allied short pursuit (entered from combat; only actually visible hostiles)
|-- Player invalid/dead, target dead/lost sight, or distance budget exhausted?
|   `-- Cancel chase move/reservation -> Allied regroup (A01/A02 -> A00), bounded recovery if blocked
|-- Reachable firing point within both player support range and chase-distance budget?
|   `-- A01 walk/A02 run to distinct point -> A00 stop -> A10 face -> A04 if legally admitted
`-- No legal point -> A00+A10 alert, never force pursuit; regroup if separated
```

Propose an initial AllyChaseMaxDistance of 10 m, bounding both separation from the current player and accumulated movement during this chase; follow/regroup retains the tuning below. Before each goal update check complete path and remaining budget, and monitor actual cumulative travel during movement. Moving the goal cannot evade the short-distance rule. Root reevaluation or target switching never resets chase origin/budget; only returning to the legal follow band and ending the chase permits a new chase task. Ten metres is a proposed street-test starting value, not the user's final chosen number. Sight loss ends pursuit, without adding Allied hidden-target search.

## German role subtree

```text
German with no higher-priority task
|-- Search just ended outside role position/route?
|   |-- Return point reachable -> A01 return -> A00
|   `-- Unreachable -> bounded recovery subtree
|-- Guard role?
|   |-- Away from guard point -> A01 return -> A00
|   `-- At guard point -> A00 idle+A10 bounded alert orientation
|-- Patrol role?
|   |-- Valid foot route and next point?
|   |   |-- Reachable -> A01 walk there -> A00+A10 brief inspection -> advance index
|   |   `-- Unreachable/blocked -> bounded recovery subtree
|   `-- Empty/invalid route -> A08 with reason, no random teleport
`-- Invalid role -> A08 and configuration error
```

Confirmed: Germans perform time-limited search on sight loss. Use only that NPC's last actually observed position/time and finite reachable check points. Arrival actions are A01 or optional A03, then A00/A10 inspection. Propose SearchDuration initially 15 seconds; deadline/point exhaustion cancels search movement, releases its reservation and returns to role. No reachable points also ends search into role/recovery, never an indefinitely blocked search branch. Reacquisition alone restores combat. The search label grants no hidden target coordinates.

## Navigation failure action subtree

```text
Current move failed/bottleneck occupied
|-- Dead/frozen? -> root A07/A08
|-- Visible hostile and combat allowed? -> cancel old move/reservation -> combat subtree
|-- Fewer than two replans used, task still legal?
|   `-- A08 short wait -> approved reachable point -> A01/A02/A03 movement
`-- Budget exhausted/no legal point -> A08 with reason
                                    reevaluate on perception/task/path change, not endless per-tick retry
```

One current action request and one valid move request per NPC. Stop must cease displacement. The prone failure shows why zero velocity/state labels alone are insufficient; test continuous positions and body clearance.

Retry budgets accumulate per behavior task ID, never reset merely by reevaluating the root. An unchanged target/rejection reason waits for changed conditions instead of resubmitting every tick. Observe Running actions without restarting clips or opening a new reload transaction.

## Coordination and navigation

A small squad coordinator manages destinations and bottleneck waiting, not omniscient enemy memory. Select distinct reachable support points using complete NavMesh paths, ground/body clearance and player firing-lane checks. Keep reservations after arrival; release on reassignment, failure, death or restore.

Provisional tuning: follow at 3–6 m, regroup beyond 10 m, destinations separated by at least 1.5 m. Adjust after actual-city measurements. First arrival proceeds through a bottleneck; later arrivals wait briefly and replan at most twice before Waiting. Choose one compatible local-avoidance method. Keep an independent-destination comparison with matched starts/goals/NPC counts; measure collisions, stalls, arrival times and failures against coordinated assignment.

## Blackboard and search

Each NPC stores Team, Role, Group, Home, PatrolIndex, TargetActor, LastSeenPosition, LastSeenTime, SearchDeadline, DesiredPosition, ReservationID, MoveRequestID, RetryCount, WaitingReason and RestoreGeneration. Stop updating last seen position immediately on sight loss. Confirmed target death clears TargetActor and its search memory; never keep searching for a known dead target. Reacquisition alone resumes live tracking. Allied brief-alert and German-search deadlines begin on actual sight loss, never reset on root reevaluation. Invalid Team/Role enters A08 with a reason, never defaults to an enemy faction or arbitrary role.

Configuration owns shared FriendlyFireEnabled; private NPC state additionally holds ChaseTaskID, ChaseOrigin and ChaseTravelDistance. Proposed initial SearchDuration is 15 seconds and AllyChaseMaxDistance is 10 m. Rifle ranges still follow actual weapon/city tests. All thresholds are configurable; do not prescribe whole-mission duration or city extent here.

## Action contract and next implementation

Propose a shared action adapter, **not an existing API**. Tasks submit the action label, destination/target, request ID and RestoreGeneration; the adapter returns Started, Running, Completed, Rejected or Cancelled with a reason. A-labels and new request IDs must remain separate from the original reload ActionID; never overwrite transaction identity.

Completion follows actual arrival/legal posture/original animation phase/transaction outcome, not BT timers that create ammo or damage. A changed behavior task/destination cancels old MoveTo and releases its reservation. Arrival/idle/fire/reload phases within the same support task retain that position, rather than admit another ally into it. Reload cancellation uses the original ExpectedActionID/Generation; precommit transfers nothing, postcommit does not refund, stale callbacks cannot recommit. Mission-level A09 restores selected player/NPC/objective snapshots; without a checkpoint start over. Unit-reset tests do not establish mission checkpoint restoration or automatic healing/refill.

Initial NPC requirements: standing idle/walk/run, holding, authoritative fire, simplified reload, death and restore. Verify player slow walk/jump/crouch/prone independently. NPC jumping needs additional NavLinks and landing validation and is deferred. Slow movement does not establish a stealth system. Missing WWII-specific reload/German rifle remains an explicit asset gap; no modern substitute.

This increment attaches new actions to a separate player trial class, not a verified German low-posture adaptation. Low posture currently rejects fire/reload; prone admits relatively flat ground and forward/back motion only. First-person run/jump retains existing ordinary holding, not a dedicated sprint lower/raise clip. AI implementation needs a shared action interface and per-faction character checks; never bulk-replace NPCs with the player trial class.

No matching German rifle is accepted yet. The firing branch must require a valid WeaponAppearance and ammunition interface; unarmed actors may perceive/alert/move, never create invisible damage. Perception/roles can be developed first, but the full two-faction combat loop depends on German weapon compatibility and historical review. No silent Allied-M1/modern substitute; see `Docs/Development/ASSET_GAPS_20261003.md`.

These three gameplay choices are confirmed. A future implementation still needs a separate AI work-package plan and relevant basic-action human review, then single-NPC perception/roles, two-Allied destination reservation/short pursuit, three-German search/fire, configurable friendly damage and six-character interaction/death/restore, and the mission loop. This confirmation does not automatically start development this turn or resume cosmetic refinement.

Require real-city native tests and trace/image evidence for private memory, faction filtering, obstruction, non-cheating sight loss, search timeout, distinct points, reservation release, bounded blockage recovery, death/stale callbacks and independent/coordinated comparison. Compilation does not pass AI, mission or performance gates.

Every leaf must trace condition -> behavior task ID -> requested A-action -> admission/rejection reason -> actual action and completion. Walk/run checks continuous displacement, gait and arrival; stop checks stable positions; turning checks orientation/foot contact; fire checks holding, legal shot path and one ammo/damage transaction; reload checks original phase commit/interruption conservation; death checks one-shot execution and old-task cancellation. Log labels, Blackboard values or expired timers never substitute for visible execution. Unaccepted actions stay out of the production tree and use the explicit idle/wait fallback.

## Confirmed rules and added acceptance

On 3 October 2026 Yupu confirmed short-distance Allied pursuit, friendly damage calculated when enabled and not when disabled, and time-limited German search on sight loss. Do not request these three choices again. Distance/time use configurable starting values pending tests.

Add tests: Allied pursuit stops before firing, regroup when player movement exceeds bounds, target loss/death returns to role, target switches cannot refresh distance budget; friendly damage on/off with the player and both NPC factions as shooters, checking friendly health, hostile behind, single ammo/damage application, friendly-death task cancellation and player-death failure; AI friendly-lane avoidance in both modes; German timeout/no-reachable-point returns to role and only reacquisition restores tracking. The switch controls damage alone, not collision, faction affiliation or original reload/death/restore transactions.
