# NPC combat V2 — 6 October 2026 checkpoint

## Authority and changed mechanism

Yupu resumes B-lane combat after formal Allied V16/German own V11 visual
selection. No grasp/model/animation/FP refinement, formal AI map adoption,
Catalog/publication/commit/push follows. Entry source: main912b0596; preexisting
DefaultEditor.ini presets remain outside this change. Cases read, early gates
and stopping rules: [implementation plan](NPC_COMBAT_V2_IMPLEMENTATION_20261006.md).
Retained causes: [NI001](../../../Failures/NI001-20261006-npc-combat-adapter/FAILURE_ANALYSIS.md).

Explicit current authority: GermanNPCFormalV14/selected_v1/result.json,
678 rows, SHA256 a298c06e258192ad6a97ca73ca46b48971f0895a0c796aefa55dc05aaf3e8f60.
All67 previous B packages match;20 new immutable B packages produce698 guards
and87 total B packages. Old555/611 snapshots/failed receipts are not rewritten.
GUARD_EPOCH_20261006.json records selection; no current map/DLL/Catalog rollback.

ActionGateV5 adds observed body Turn/current native LOS/live enemy admission
and typed possessed-Pawn trace ignore. V6 closes only live NPC gun Actor
collision at equipment configuration. V7 recognizes original Ready+one ActionID
advance with exact retained reload tokens/current task/request/generation,
one commit and ammo conservation. Supersession calls original guarded EndReload.
Original shared transactions, gun packages and poses remain unchanged.

CombatV2 is a new shared native BT service/controller with faction Pawn
derivatives; existing formal policies equip compatible spawns, no FP parameter
copy. Native identified Stop/Turn/original Fire/Reload perform the decisions.
No Python per-frame target/action/pose/health/ammo driver. Configuration/activation
is one-time fixture setup; Combat defaults OFF, not formal mission bootstrap.
Held bodies suppress inherited role movement, but death/generation changes still
reach original cleanup. Lost current LOS or role cutoffs release hold; native
Ally900/850cm limits and inherited bounded search are not relaxed.

## Fresh runtime proof

Private receipts: Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/
Evidence/NPCInteractionV1/<identity>. Logs/exits: tmp/npc-interaction-v1.
Commercial bytes remain private. Author compilation alone is not runtime proof.

- action_combat_runtime_v5_20261006: both selected policies bind; actual
  Stop/Turn, two35-damage hostile hits, friend/wall refusal without ammo loss,
  original0/16→8/8 reload with one observed commit.693 guards exact.
- action_combat_runtime_v6_20261006: seven checks/698 exact. Both factions
  repeat the above; completed request replay and original stale commit/end
  do not double commit. A real round then partial reload is superseded by
  a native task, returning original identity/Ready. Late tokens and waiting
  beyond original duration do not change ammo/commit.
- autonomous_runtime_v4_20261006: ten checks/698 exact. Both factions
  autonomously Stop/Turn/Fire/Reload; friendly-lane wait does not consume ammo,
  observed target death stops attacks. Original death cancels real autoreload;
  original reset preserves ammo and old generation is rejected. One player+
  two Allies+three Germans observed12seconds: both teams have new shots,
  four NPC casualties stop, no unrequested resurrection, and each NPC's
  Loaded+Reserve+ShotSequence=18. Python combat decision requests0; one stale
  admission probe counted separately. Not balance/crowd stress/FPS proof.
- autonomous_runtime_v6_20261006: the corrected finite350cm fixture passes
  all11 checks/698 exact, errors0/exit0. The dead target is removed; German
  legitimate live-player reacquisition is permitted and damage-checked rather
  than falsely requiring every target to stay null. Death during actual reload,
  original reset/stale rejection and the12-second six-actor interaction repeat.
  Joint new shots: Allies7/Germans9; four NPCs and player die, surviving German
  returns to role movement. All NPC ammo remains conserved; dead bodies stop.
  This is finite combat, not difficulty balance or player-death mission completion.
- selected_combat_regression_v1_20261006: actual five current-policy bindings,
  no historical manual staging; Player/Allied/German OFF/ON,21 original shots.
  OFF first friendly blocks without damage; ON one35 damage; hostile35;
  world blocks without damage. Original cooldown rejects immediate replay;
  reload conserves ammo, dead capsule NoCollision, repeat damage no second
  death.698 exact. This base transaction matrix is not autonomous FF ON proof.
- action_combat_runtime_v8_20261006: nine checks/698 exact, report errors0/
  normal exit0. Both selected factions' identified AI Fire admission refuses
  a live friendly lane with FF OFF AND ON, no ammo or health change. The full
  action/reload/replay/real supersession/late-token sequence also repeats.
  This is explicit AI admission under both modes, not simultaneous autonomous
  crowd behavior with FF ON.

Runtime tests disable ParisEditorBridge and reflect its absence, retain approved
native presentation modules. Completed runs above have errors0/normal exit0;
process exit alone is not acceptance.

## Failures and final follow-up in progress

Equipment collision assertions, false reload cancellation, pre-admission Stop
height and Object/Actor author-pin failure are retained. AutonomousV1 assumed
refill after reset; V2 incorrectly demanded one fixed enemy. V3 FAILS: after
friendly occlusion an Ally no longer submits actions; old telemetry lacks player
geometry. V4 shows its old650cm-behind player settles about440cm below street,
close to the900cm role cutoff. This supports a fixture-distance hypothesis,
not a full cause proof for V3. V5's nearer fixture passes both fights then
fails its null-target corpse assumption when the live player is legitimately
sensed. V6 passes the corrected per-target cleanup/damage check without
changing native limits. ActionV7's FF test fails before any actions because
an editor-only Blueprint loader is called during PIE; V8 retains the setup-time
class and passes the runtime query/actual AI OFF-ON gates. No shared asset is
changed. All failures remain preserved rather than renamed as passes.

## Boundaries and next integration

Numerical/native gameplay proof is not continuous grasp/contact, recoil,
clear-shot/muzzle corridor, near-wall/gait visual, chase-limit stress, whole
mission, FPS, Shipping, second-machine or course MVP acceptance. AN008 stopped
motion entries remain locked. Prior dated B1/B2/B3 proofs are not freshly rerun
in full; new wrappers do not accept every noncombat/crowd case. Formal AI
map/bootstrap selection, Catalog/release, packaging/demo remain separate.
No dependency deletion or matching Git publication this turn.

## Final audit and handoff

combat_v2_final_20261006_v1/result.json is a fresh read-only698-row exact
combined hash snapshot (not formal AI selection). Source preflight now persists
the actual rows for subsequent readers. All87 disk B packages are registered,
no unknown files. Ten model unit tests, Python directory compilation, launcher
PowerShell parsing, scoped tracked diff whitespace and nine untracked source/
doc trailing-whitespace checks pass. CRLF normalization warnings are not failures;
the unrelated preexisting DefaultEditor.ini diff remains untouched/excluded.

Actual Unreal process count0 at22:17:26EDT6October; all owned native jobs closed
normally0 even when their test gate failed. No user editor terminated. Lane B
releases its native slot; next writer explicitly protects current678 authority
PLUS the20 B additions/current87-package inventory, or the combined698 audit.
Do not restore historical map/Catalog/base bytes or overwrite occupied evidence.

Formal playable-map/bootstrap wiring remains outside this B handoff's automatic
save authority; request separate integration approval, preserving all existing
approved assets. Real visual/action/FPS and mission gates above remain open.
