# NPC Interaction V1 implementation

## Current formal integration, 7 October 2026

User permits local formal-map adoption and play regression. Follow the separate
[formal integration plan](NPC_FORMAL_COMBAT_IMPLEMENTATION_20261007.md) and
[actual results](NPC_FORMAL_COMBAT_RESULT_20261007.md): NI001/GP010/AN008/NI002
review, native bootstrap early gate and scoped stopping conditions. No new grip,
mission, SFTP/Git publication scope. Current703 guards use the explicit map ledger.

## Previous continuation, 6 October 2026

Yupu resumes combat development after both factions' formal visual selection.
Follow [the bounded combat V2 plan](NPC_COMBAT_V2_IMPLEMENTATION_20261006.md).
It adopts the current678-row GermanFormalV14 epoch, not older555/611 hashes.
Earlier pending-grip restrictions below are historical for those exact selected
assets. No fitting, formal map/Catalog change, publication or Git write follows.
Fresh results, including failed attempts, will be recorded separately.

## Current bounded continuation, 5 October 2026

The user authorizes this window's shared friendly-fire integration and direct
player/Allied/German transaction regression, but explicitly requires NPC grip
markings BEFORE autonomous combat is enabled. EquipmentHumanAccepted stays false;
no autonomous fire/reload, fitting, FP changes, formal city save, adoption,
Catalog/publication, commit or push. This narrow authorization supersedes the
older coordinator-only/shared-code ban, not any protected visual-production rule.

Read cases: failure index and navigation stop/resend failure; causal SightV4
obstruction; incomplete-path arrival 125cm from a raw off-NavMesh squad goal;
SearchV8 lazy pure-pin visited-counter ordering; type-promotion native crashes;
shared world-query exec pruning; game-clock cooldown/reset-not-refill regressions;
original death disables its capsule. Preserve all failed identities and packages.

Changes and early gates:

- B1 actual native full-path patrol/guard/bounded replans/death/restore pass in
  behavior_runtime_v3. Native sampling is not visual gait/contact acceptance.
- B3 SearchV9 increments visited count BEFORE its index; three actual Germans
  visit five points then return to guard/patrol before their fixed 15s deadline.
  A process-local BlueprintEditorSettings.bEnableTypePromotion=false/readback,
  finally restored to its original value, fixes author crashes. No Config save;
  the earlier console-command request was not evidence of the actual CDO setting.
- SquadV4 reserves actual projected NavMesh body-center points (own capsule
  half-height), uses original-length native movement/RVO only, and rejects dead
  sight candidates at the real OnSeePawn boundary. No hidden target polling.
  Actual follow/idle/original reload, replacement target preserves chase budget,
  and observed corpse clears memory pass subgates. In squad_runtime_v4 the death
  baseline preceded legal Regroup->Follow reassignment; next harness waits for
  stable Follow before recording death/survivor reservation identity. No asset
  change or acceptance relaxation. Remaining death/restore/matched comparison
  must still pass actual execution before B2 completion is claimed.
- One shared FF policy defaults OFF. Only the authorized two aliases of one
  combat-base file change; original 553 other approved rows remain exact, and
  old approved snapshot/map/Catalog are not rewritten. Direct three-shooter
  regression measures OFF blocking/ON one original 35 damage, original cooldown,
  reload/ammo conservation, corpse noncollision/no repeated death, and an unsaved
  world-blocking cube under both settings. Author success is not this regression.
- Separate native ActionGate Controller/BT observer carries TaskID/RequestID/
  Generation and real stop/original action feedback. Unarmed/unverified/human-
  pending equipment rejects without firing. V1 failed controller-self resolution
  of a pawn-only function with zero saved files; V2 uses the proven typed public
  external call and tests actual Stop/duplicates/death/restore cancellation only.
  Unexecuted fire/reload branches are not acceptance or enabled autonomous AI.

Early checks are exact guards, compile, native request rejection and body stop;
then real movement/transactions. Continue scoped API/harness repairs. Stop for
another writer, a real current-epoch conflict, new protected authority, or required
human choice. The grip-marking gate is explicitly required by the user, not a
self-imposed stop after an author error. The dated sections below are history.

Further diagnosed routing: UE CreateNodeFromName filters the exact function
owner, not an inheriting class. The original PC_RequestReload is defined on
BP_PCCombatantReloadV1; ActionGate V3 names that owner and the combat-base owner
of PC_RequestFire. Five new V3 packages compile/save with 601 old guards exact;
registered current guards are 606. No private-function/source mutation occurred.

combat_regression_v4 passes Player OFF/ON/world/corpse semantics, then finds a
spawned Allied pawn has no WeaponAppearance. The saved formal Allied gun is an
instance binding, not a pawn CDO default. Next fixtures clone the actual saved
PC_City_Ally1 pair's same mesh, gun class, LeftShiftCm and component config into
new unsaved same-rig Allies, with exact assertions. Never copy player grip
numbers or mark equipment accepted. The default ActionGate equipment-rejection
test uses that exact Allied fixture; its German fixture intentionally stays
unarmed. Early checks are exact source binding/config, original transactions;
stop or repair failed assertions, no threshold relaxation or formal save.

V3 static identity review finds an intervening rejected request can overwrite
reply IDs before the older admitted action completes. V4 strengthens only the
new adapter: terminal feedback restores Active IDs, same identity/different
Action rejects, and actual BB task supersession cancels. The native Stop test
inserts action-mismatch/busy rejection, then requires completion to retain its
original triple. This is real returned-ID checking, not echoed input. Preserve
V3/new V4 names, original shared transactions and the false equipment-human gate.

Same-task/generation older RequestIDs reject. One native BrainComponent restart
after PC_SetPatrol is a reevaluation stimulus, not a Python AI/movement loop; the
test requires naturally changed BB TaskID before asserting old Stop cancellation.
ActionGate V4 five-package author passes,606 previous rows exact; inventory is67
packages/current611 rows. The runtime then passes all five stop/identity/equipment
rejection checks/611 exact/exit0, human gate false. Final closed-editor audit,
ten model tests/Python compile/PS parse pass. Direct FF regression is21 shots,
not NPC autonomous combat; squad matched comparison does not show superiority.
Old remote manifest still has the original base hash: do not restore over the
authorized local FF change or claim this work published. Further activation
waits for requested grip markings, fitting/acceptance and actual autonomous tests.

Date: 4 October 2026. Lane B only. This work implements the bounded NPC handoff in
`../NPC_INTERACTION_HANDOFF_20261004.md`; it does not select the formal city,
change shared combat/player/reload code, publish assets, commit or push.

## Evidence read before authoring

- `HANDOFF.md`, `Failures/README.md`, the parallel workflow and Lane B handoff.
- `NPC_BEHAVIOR_DRAFT_V1.md` revision 3 and `TECHNICAL_DESIGN.md`.
- Assignment 3 goal and acceptance checklist; AI-01 and NAV-01 remain unpassed.
- `PARIS_NAVIGATION_FOUNDATION_RESULT_20261002.md`: retained 34/193/45 NavMesh,
  391 connected sample paths and four bounded MoveTo arrivals; this is not
  whole-city, avoidance or AI acceptance. Preserve the failed fresh_v1-v3 and
  supported-agent regeneration history.
- `PLAYER_ACTIONS_RESULT_20261003.md`: V5/runtime_v9 falsely reported blocked and
  zero velocity while the body advanced 49.12 cm. V6's continuous-position gate
  supersedes it; state labels and velocity alone never prove a stop.
- `GERMAN_RIFLE_UE_AND_ACTION_RESULT_20261004.md`: German rifle attachment V2 is
  an unselected candidate. Numeric grip/collision checks do not close trigger,
  reload-contact, recoil or historical acceptance.
- AN003 and FP001: numeric binding/contact or gameplay results do not substitute
  for target-view visual acceptance. Lane B will not edit arms, fingers, clips,
  camera, reload presentation or the shared player display.

## Changed approach

The earlier navigation work moved one actor at a time and stored no behavior
state. This attempt adds one shared controller/decision definition with private
per-controller Blackboard and memory, an observable action request contract and a
small reservation coordinator. It never treats a Blackboard label as a completed
move, shot or reload. Movement completion requires native path status plus sampled
continuous displacement/arrival. Sight loss freezes the last observed position;
it cannot continue reading the hidden target transform.

The first native operation is a disposable authoring-capability proof for an
actual Behavior Tree root/children and Blackboard keys. This is deliberately
earlier than character or city integration. If the installed editor APIs cannot
construct and compile the real tree, stop before producing controller or pawn
assets instead of substituting a tick-driven imitation.

## Ownership and storage

- Source: `Tools/Integration/NPCInteractionV1/`.
- Documents/results: `Docs/Development/NPCInteractionV1/`.
- Native packages: `/Game/ParisCombat/AI/NPCInteractionV1/` only.
- Private evidence: `Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/NPCInteractionV1/<identity>/`.
- Physical native bytes remain in the single gameplay workspace Content tree.

Planned new packages are `BB_PC_NPCInteractionV1`, `BT_PC_NPCInteractionV1`,
`BP_PCNPCControllerV1`, `BP_PCNPCActionAdapterV1`,
`BP_PCSquadCoordinatorV1`, task/service Blueprints, and derived trial Allied and
German NPC classes. No shared combatant, player, formal map, configuration,
Catalog, release or other lane package is writable.

## Contract and order

1. **B0 capability and interface audit.** Verify the 514-file starting guard,
   absence of another Unreal writer, actual parent classes, TeamId 0/1, roles and
   callable `PC_RequestFire(AimOrigin,AimDirection)`, `PC_RequestReload`,
   `PC_ApplyDamage(Amount)` and `PC_ResetLifecycle`. Prove that the installed APIs
   can author a real Blackboard and Behavior Tree in the new namespace.
2. **B1 single-NPC behavior.** Add faction-filtered sight memory, guard/patrol,
   complete-path MoveTo, stop, at most two replans and lifecycle cancellation.
3. **B2 Allied coordination.** Add two persistent distinct reservations,
   follow/regroup and a chase task whose cumulative distance and player-distance
   bounds survive target changes and tree reevaluation. Compare matched independent
   and coordinated goals using one avoidance method.
4. **B3 German behavior.** Add guard/foot-patrol and finite reachable checks around
   the private last-seen position. Timeout/no points returns to role; unarmed
   characters may perceive and move but cannot damage.
5. **B4 action/equipment adapter.** Recheck actual per-faction appearance,
   collision, muzzle and contact before admitting fire/reload. Return
   Started/Running/Completed/Rejected/Cancelled with reason, TaskID, RequestID and
   RestoreGeneration. Never assign ammo/health directly or reuse reload ActionID.
6. **B5 six-actor unsaved integration.** Use transient/unsaved actual-city staging.
   Verify stop-face-fire, reload gate, death/target/reservation cleanup and stale
   callback rejection. Produce a precise FriendlyFireEnabled shared-base patch and
   tests for the coordinator; do not apply that shared patch in Lane B.

## Early acceptance and stop conditions

The first falsifiable native check must produce a loadable Blackboard with private
keys and a real Behavior Tree with a root and executable child. Two controllers
must own different Blackboard components: writing LastSeenPosition/LastSeenTime on
one must not affect the other. After simulated sight loss, moving the hidden target
must not change either stored value. Compilation or a key value alone is not a
pass; the task trace must show condition -> TaskID -> request -> admission/reason
-> physical result.

Stop the affected path immediately if any of these occurs:

- another Unreal writer/user preview appears, ownership is ambiguous, or any of
  the current authoritative 528 hashes differs;
- actual Behavior Tree graph authoring is unsupported or a new-only early tree
  cannot fresh-load/execute;
- a move reports stopped/success while continuous position still advances, a
  partial path/teleport/unbounded retry occurs, or private memory leaks;
- valid faction equipment/contact cannot be re-established, or completing armed
  combat would require shared-base, player, reload, finger, camera or formal-map
  edits;
- a rights/history/presentation choice needs user authority.

On failure preserve the unique identity, logs and any new-only draft; do not rerun
an occupied identity or roll back the Content tree. No automatic package selection,
formal map save, package build, publication, commit or push.

## B1-V2 continuation (5 October 2026)

Read the failure index, the 49.12 cm zero-velocity advance in
`PLAYER_ACTIONS_RESULT_20261003.md`, the stable single native cancellation in
`PARIS_NAVIGATION_FOUNDATION_RESULT_20261002.md`, and B1 V1's 43.5573 cm drift.
V1 stopped only AIController movement while the looping BT remained alive. V2 first
stops native Brain/BT logic so the old request cannot be reissued, then calls
`StopMovement`. It does not modify B0/B1 assets, CharacterMovement settings, or gates.
The guard source changes to the verified 528-file recovery snapshot at
`Evidence/ReloadIndexContactV6/map_recovery_v1/result.json`, not the old aggregate.

Early check: same actual city, start/goal, and native MoveTo tree; after more than
100 cm real travel, Brain-stop then movement-stop must hold continuous body drift to
at most 1 cm for at least 0.75 seconds, with no old TaskID/RequestID movement. Stop
before B2-B5 if the Brain API is unavailable, the tree reissues, drift exceeds 1 cm,
528 guards differ, or a user preview reappears.

## B1-V3 native sight correction (5 October 2026)

The cases above and `b1_sight_runtime_v2` were reviewed. The observer, friendly,
and hostile all spawned in the actual city, but `TargetActor` stayed null for four
seconds and the log contained no Blueprint runtime error. V1 placed
`PawnSensingComponent` on the AIController, so the sensor did not have the intended
Pawn orientation/controller ownership. Preserve that failure; do not overwrite or
delete it, extend its timeout, or sweep actor positions.

This attempt creates only V2 packages. The controller retains the private
Blackboard, faction filter, last-seen writes, and 0.75-second visibility expiry.
Each Allied/German Pawn now owns its PawnSensing component, and its `OnSeePawn`
event forwards only the actually sensed Pawn to controller function
`PC_RecordSight`. It does not read a moved hidden target transform and does not
modify V1, B0, a shared character, the formal map, or configuration.

Early gate: in the same actual city, the Allied observer must never select the
Allied Pawn 250 cm ahead and must acquire the German Pawn 500 cm ahead within four
seconds. After moving that German 5 km away and waiting at least 1.25 seconds,
`HasVisibleTarget` must be false and `LastSeenPosition` may change by no more than
0.001 cm. If the native V2 event still does not fire, faction filtering is wrong,
memory follows the hidden target, any of the current 531 guards changes, or another
Unreal process appears, stop B1 and record the failure. Do not move-sweep, extend
the timeout, or enter B2-B5.

## B1-V3 authoring API correction (5 October 2026)

`b1_sight_author_v3` stopped before runtime: the new V2 controller was saved, but
the generic `Utilities|Casting|CastToActor` string could not create a node in this
graph context. The prior 531 guards remained exact. The V2 controller is now an
unselected protected failure artifact; no V2 Pawn, map save, or runtime acceptance
exists.

This attempt queries the actual `CastToActor` type id available to the current
Blueprint graph before retargeting it to the new controller class. All outputs use
new SightV3 package names so V2 is not overwritten. Sensor ownership, distances,
timeouts, faction gate, and frozen-memory acceptance remain unchanged. The early
gate is three error-free compiled V3 packages with the controller and Pawn component
ownership intact. If type-id discovery or retargeting still fails, stop without a
third authoring workaround.

## B1-V4 Python tooling probe (5 October 2026, explicitly requested)

The user asked to set up the Python tooling first and explain the current launch.
This attempt tests tooling only; it does not resume NPC asset authoring. Review of
the V3 log, the UE 5.8 `EditorToolset` descriptor, and its `blueprint.py` shows that
the project does not enable EditorToolset, so `editor_toolset` is not placed on the
embedded Python path. The required low-level
`BlueprintGraphEditor.list_available_nodes()` API is already exposed. V3 also
incorrectly supplied an object pin as context to `create_node_from_name`; Epic's own
implementation creates the cast with an empty context and wires it afterward.

Changed check: embedded UE Python lists the real node type id in an existing graph,
creates CastToActor with an empty context, retargets it to the existing SightV2
controller, and immediately removes it. It saves no Blueprint, enables no
experimental plugin, and changes neither `.uproject` nor Config. Acceptance requires
query, creation, retarget and removal to pass, all 532 guards to remain exact, and
the editor to exit. On any failure, preserve the probe and do not resume the V3
author or actual-city test.

## B1-V5 resumed sight author (5 October 2026, explicitly approved)

After `ue_python_tooling_v1` passed, the user explicitly approved rerunning the new
NPC sight author. The V1 runtime sight failure, partial V2 author failure, V3 import
failure, and successful V4 tooling probe were read. This attempt does not enable
EditorToolset. It uses the proven low-level node enumeration and empty-context cast
creation to connect each Pawn-owned `PawnSensingComponent.OnSeePawn` to the new
SightV3 controller's `PC_RecordSight`. It creates only three V3 packages, preserves
V1/V2, and changes no shared character, configuration, or formal map.

Author gate: the controller and both V3 Pawns compile without graph errors; sensing
belongs to each Pawn and not the controller; both faction Pawns use the same new
controller. All prior 532 guards must remain exact. Any author failure stops before
runtime. Only after registering three passing files as a 535-row guard may one fixed
actual-city test use a friendly at 250 cm and hostile at 500 cm. If sensing still
does not fire, faction filtering is wrong, or memory follows the hidden target, stop
without a position sweep, longer four-second gate, or B2-B5 work.

## B1-V6 cross-Blueprint call probe (5 October 2026)

The latest `HANDOFF.md` and `FIRST_PERSON_FORMAL_V21_RESULT_20261005.md` were read.
Lane A released the slot; its authorized formal-map and Catalog changes make the
old 533-row epoch historical. Lane B now consumes the 555-row current epoch at
`Evidence/FirstPersonFormalV21/selected_v1/result.json`, which already includes all
11 NPC drafts. The map and Catalog must not be rolled back.

V5 proved cast creation/retargeting. Its only failure was calling another Blueprint
controller's `PC_RecordSight` by bare function name from the Pawn graph. This check
saves nothing: query the function's real type id from the existing SightV3
controller graph, create the call in an existing Pawn graph with an explicit
declaring class, verify `self` and `SeenPawn` pins, and immediately remove it.
Acceptance requires query, creation, typed pins and removal to pass with all 555
guards exact and no map save. Failure stops; only a passing probe may author three
new SightV4 packages, never overwrite SightV1-V3.

## B1-V7 public-function probe (5 October 2026)

V6 discovered `CallFunction|PCRecordSight` under the exact 555-row guard, but an
explicit declaring class still could not create it in the Pawn graph; nothing was
saved. UE 5.8 source exposes `BlueprintGraphEditor.SetFunctionIsPublic()`, which the
V3 author never called. This probe only marks the existing V3 `PC_RecordSight`
public in memory, compiles it, then creates/verifies/removes the call in the Pawn
graph and exits without saving.

Acceptance requires `self` and `SeenPawn` pins after the public flag and all 555
guards exact. Failure stops. A pass permits a new SightV4 controller to mark the
function public before its first save and create only new V4 Pawns, without changing V3.

## B1-V8 resumed SightV4 author (5 October 2026, explicitly resumed here)

The user states the other window is paused and asks this work to continue. The latest
HANDOFF, AGENTS, and NPC grip three-view result were read; Lane A released, no UE or
Blender process exists, and the current 555-row epoch is exact. Grip images await
future markup, while this perception author changes no gun, hand, bone, material,
motion, or player numeric value.

Create only a SightV4 controller and Allied/German Pawns. Mark controller function
`PC_RecordSight` public before its first save. Each Pawn owns PawnSensing and connects
OnSeePawn using the V7-proven class function node
`Class|BPPCNPCControllerSightV4|PCRecordSight`. The author gate requires three
error-free compiled V4 packages, correct Pawn component ownership, and all prior 555
guards exact. Failure stops. A pass registers three files as 558 guards before one
fixed-distance actual-city test. Never overwrite V1-V3, change BT/BB, or save the map.
# B1-V9 causal repair and continuous progress — 2026-10-05

Later verified B3: SearchV8 author passes after exact CDO property
`bEnableTypePromotion` temporary false/restored true, never SaveConfig. The first
city test physically reached points but incremented SearchIndex before a lazy
pure `near` expression counted the old point. New SearchV9 counts first; fresh
`search_runtime_v2` visits five points per German, fixed15s deadline, frozen memory,
physical guard return/patrol resumption and no unarmed ammo/damage,581 guards.
Old native crashes/property lookup/SelectBool and counter failures remain retained.

Native B2 adds a two-slot reservation actor, common squad controller/BT services,
new per-faction Pawn derivatives, monotonic reservation IDs and only RVO. Idle/
fire/reload retain positions; reassignment/failure/death/restore release them.
One chase episode accumulates actual body travel across target/TaskID changes;
conservative operational cutoffs850/900cm retain the actual1000cm acceptance.
Original visible-target observation is overridden only in the new controller to
reject observed corpses and own death, without hidden-position/health polling.

SquadV1 missed GetActorOfClass's exec pin; its harness also used editor-only class
loading inside PIE. V2 repairs both and produces reservations1/2, but an off-mesh
formation goal reports Arrived125cm from the original reserved point. Next
versions project a real NavMesh endpoint and add the owned Character's actual
capsule half-height before reserving. V3 stops at a Pawn-to-Character property
type mismatch after saving one coordinator,595 current guards; the next version
casts the actual pawn before querying capsule height. No body threshold relaxation.
Matched comparison uses identical editor starts, two Pawns, candidate point pool
and RVO, changing only coordinated versus independent nearest selection; no
automatic claim of superiority/scalability.

The user explicitly authorizes shared FF integration and three-shooter regression.
See FRIENDLY_FIRE_SHARED_PATCH_20261005.md and the exact two-alias mutation ledger;
the original555-row snapshot stays immutable. One shared friendly terminal reads
one native world policy/default OFF; ON calls original damage35 once. The first
author's missing world-query exec edge is repaired separately with backups; all
other approved553 rows/old B/map/Catalog/weapon bytes stay exact. First regression
passes Player OFF blocking but its next shot uses wall-clock wait before the
native game cooldown elapses; the harness now checks actual NextShotTime. This
is not native damage failure or runtime ON acceptance. Graph-only authors use
NullRHI; actual-city tests retain normal RHI and neither establishes visual grip.

Later V10: real native Selector with Plan(full path), MoveTo(no partial), Arrival,
Wait and finite Failure/Wait fallback; root lifecycle service clears the move
decorator and requests on health/generation change. Default guard; public
PC_SetPatrol configures patrol without writing private runtime fields. Author
hidden-world-context and pure-method exec-pin failures are retained as two
unselected controllers. V3 eight-package author and V4 three config derivatives
pass; original packages/approved555 epoch remain exact, combined571 guards.
`behavior_runtime_v3` passes actual-city roundtrip,300cm/s,guard/death/restore0cm,
unreachable RetryCount2/PathExhausted and cleared old requests. Native movement
does not establish visual gait/contact. The earlier runtime loading reentrance
crash and rejected instance-field edit are preserved as harness failures.

Next German finite search uses the retained native BT tasks, frozen sight origin,
five candidates and a15s game-time deadline, then guard/patrol role return. No
fire/damage is fabricated for unarmed NPCs. Search author native crashes are
localized with stage/node logs; promoted operators fail across compiled graphs.
New process-local BP.TypePromo.IsEnabled=0 request uses fixed-signature authoring,
without Config/uproject/global user-setting edits or old-package rewrites. Tests
remain unpassed until fresh city evidence exists. Errors continue in scope;
stop only on writer/guard conflict, required protected mutation or human choice.

The user authorizes repair of intermediate in-scope failures and supersedes the
previous self-imposed pause after every failed attempt. Read: failure index,
navigation stop failure, B1 43.5573cm drift, SightV1/V4 acquisition failures and
V2/V3 author failures. Local UE source explicitly supports Controller-owned and
Pawn-owned sensing; the earlier ownership-cause claim was unproved. The hidden
target displacement of (5000,5000,0)cm is 70.71m, not 5km.

Change: an unsaved city causal probe records native delegate binding before a
read-only Python event listener, CouldSeePawn, controller LOS, actual blockers,
TeamId and Blackboard. It measures the original scene for two seconds, adds the
listener for two seconds, then moves the collinear friendly sideways and removes
overlapping original Allies in the test world, with a four-second acquisition
check. Python never writes NPC memory or drives sensing. Listener effects cannot
count as native asset acceptance. Early check identifies the failed stage; next
acceptance still requires a fresh listener-free acquisition and frozen loss
memory before full B1, B2 coordination, B3 search and B4/B5 integration.

Retain failed evidence and continue repair. Stop only for another writer,
conflicting current 558-row guards, a required protected/shared mutation outside
scope, or a necessary human asset/visual choice. No player, formal map, Catalog,
grip or previous package modification/publication.
