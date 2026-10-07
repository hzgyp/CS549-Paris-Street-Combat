# Parallel gameplay work allocation

Latest slot checkpoint: [V5 result](RELOAD_REPAIR_V5_RESULT_20261004.md).
A's initial two native observations are finished/all engines closed; A explicitly
releases the initial slot for user-opened B. A/C work offline while B owns the next
slot. Recheck actual processes/ownership before launch; later A tests are scheduled.

4 October 2026. User authorizes this conversation to continue action repair and
requests handoffs for other conversations to implement NPC interaction in parallel.
The user will open those conversations; none has been created, messaged or started.
Chinese review: [_ZH](PARALLEL_GAMEPLAY_WORKFLOW_20261004_ZH.md).

## Human review: open reload defects

| ID | Confirmed observation | Cause/status | Acceptance |
| --- | --- | --- | --- |
| RLD-01 | Right index finger penetrates the gun during reload | Human-confirmed; exact contact phase/cause unmeasured | Same target/gun: no visible finger penetration through a full cycle; preserve holding contact |
| RLD-02 | Sleeve fragments obscure the camera | Human-confirmed and earlier phase images; skin/bone/projection cause unproved | No spikes/fragments or large own-body obstruction, at original camera, idle/moving reload |
| RLD-03 | Reload end jumps into ordinary holding | Human-confirmed discontinuity; missing source clip is the user's hypothesis, not established | Continuous finish→hold in uninterrupted native playback, including rifle motion; no pose pop |

Source-mannequin preview approval remains valid. AN003 game target is visually
rejected; formal map and selected native release are unchanged. Current map SHA:
`2791b4a7f76b4b3d07f42286b6ad0156c3a185c2e3e795fa2446aaac0ad68519`.
514 native-file guards include unselected diagnostics, not a restore manifest.
Human preview PID6968 is now absent; verify actual processes at every launch.
The prior REV-01 sprint/gun separation, REV-02 prone carry, REV-03 NPC trigger
contact and REV-04 recoil remain open; this split does not mark any repaired.

Lane A natural_end_v1 additionally finds a **temporary-preview timing defect**:
body Reload_2 ends at2.166667s, display D059 at4.133333s, diagnostic commit3.95s
cannot occur in body phase. Observed0commits/ammo unchanged2/16, Ready after4.637568s.
This is not a defect claimed for the unchanged formal baseline. Consecutive switch
samples show14.2417cm gun translation in52.684ms; missing source motion remains
unproved. Timing_sync_v1 tests original duration/commit with rate-only synchronization,
not a new trajectory or direct ammo assignment. B uses unchanged verified transactions.

## Work lanes and file ownership

| Lane | Owner | Writes | Does not write |
| --- | --- | --- | --- |
| A: action repair | This conversation | New ReloadRepairV5 documents/tools/packages/evidence | NPC tree/controller/config; shared combat base, official map and releases |
| B: NPC interaction | User's new NPC conversation | New NPCInteractionV1 AI/controller/BT/BB/tasks/coordinator, draft equipment adapters and its documents/tools | FP owner/arms/reload clips; shared combat base and official map |
| C: regression/integration preparation | Optional third conversation | New ParallelGameplayV1 test plans/harness/results; read-only static dependency/contract checks | Production Blueprint/mesh/map/config/manifest; no release selection |

Read the [A plan](RELOAD_REPAIR_V5_20261004.md),
[B handoff](NPC_INTERACTION_HANDOFF_20261004.md) and
[C handoff](INTEGRATION_TEST_HANDOFF_20261004.md).
Each recipient writes its own scoped implementation before authoring and reports
its exact new files/hash inventory, tests, failures and pending merge requests.
Only this coordinating conversation updates AGENTS/HANDOFF/common plans after
review; other lanes do not overwrite shared metadata or silently commit/push.

## Real concurrency and single native writer

```text
A: reload diagnosis/repair -----------\
B: NPC decisions/adapters -----------+--> serial city integration --> regression --> human review
C: contracts/test preparation -------/
```

Code, documents, offline asset/log inspection and deterministic tests can run
concurrently. This host's game and labs alias the same writable SFTP Content;
different namespaces/maps or conversations do NOT isolate Unreal writers.

- Initial native author/test reservation belongs to lane A. B/C may work offline,
  but may not launch another Unreal writer or save packages while A holds it.
- A releases the reservation explicitly after normal engine shutdown and guard
  review. B can then request a scheduled native slot, followed by C runtime tests.
- Reservation is coordination, not an implemented mutex. Launchers must also
  inspect actual Unreal processes; no concurrent launch race or forced shutdown.
  If ownership is ambiguous, keep working offline and ask the coordinator/user.
- Existing user-owned preview blocks all other writers until closed/discarded.
- Do not copy the26GB foundation or create another physical asset repository.
  Native drafts stay in the single workspace Content; use distinct new package
  paths and unique private Evidence/log identities. Originals/releases immutable.

## Shared integration contract

NPC intent ends in admitted physical actions, not Blackboard labels. The proposed
adapter reports Started/Running/Completed/Rejected/Cancelled plus reason, TaskID,
RequestID and RestoreGeneration; these must not replace original reload ActionID.
Treat the adapter as to-be-authored, not an existing runtime API.
Existing verified entries include PC_RequestFire(AimOrigin,AimDirection),
PC_RequestReload, PC_ApplyDamage(Amount), PC_ResetLifecycle; inspect live signatures
before wiring. AI uses NPC origin/direction, not PC_PlayerFire/camera rays.
No direct ammo/health assignment, BT timeout-generated damage/ammo or repeated
requests while an existing action is Running. Reset is mission/test-owned.

Lane B can build behavior on the unchanged shared full-body action foundation;
it need not await FP cosmetics. Firing/reload acceptance still needs per-faction
weapon/contact/transaction checks. Initial tree disables NPC jump/crouch/prone and
falls back to idle/wait for unavailable actions. Source German model is accepted;
its native attachment is an unselected tested candidate, not final trigger/history
acceptance or a selected equipped formal city. Never invent an invisible gun.

FriendlyFireEnabled is B's design/prototype responsibility, but its shared player+
both-faction damage integration changes shared combat code. B proposes a precise
patch/test contract; coordinator alone schedules and applies the shared merge.
Do not claim global on-mode behavior from NPC-only damage or old off-mode tests.

## Merge gate and stopping conditions

Native drafts remain unselected. First serialize unsaved city integration of A/B,
then C's fresh gameplay/action/AI checks and human visual review. Only a separately
documented coordinator selection can save the formal map; publication/packaging/
Catalog/commit/push requires its own authority and verified bytes.
Stop native writes on guard/ownership conflict, preserve unique work, never restore
historical map hashes over newer work. Review AN001/002/003/FP001 before A; B/C also
read player-action blocked-motion failures and navigation's failed/rebuilt loads.
Successful compilation/functional checks do not clear visual, mission, FPS,
second-machine, packaging or Assignment3 completion.
