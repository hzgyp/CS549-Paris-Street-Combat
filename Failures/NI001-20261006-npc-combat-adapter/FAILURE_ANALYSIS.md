# NI001 — selected equipment and action-adapter mismatches

6 October 2026. B-lane combat continuation, not grasp refinement. Governing
plan: Docs/Development/NPCInteractionV1/NPC_COMBAT_V2_IMPLEMENTATION_20261006.md.
Private raw receipts remain in the one workspace Evidence/NPCInteractionV1;
commercial packages/logs are not added to Git.

## Retained evidence

- action_gate_author_v5_20261006 compiles five new packages under exact678 guards.
  Typed Pawn ignore and target/faction/live-LOS admission are authored, not yet
  autonomous combat proof.
- action_combat_runtime_v1_20261006 fails a component-only NoCollision assertion.
  Do not presume an Actor-level disable without reading it.
- action_combat_runtime_v2_20261006 records exact selected Allied M1/config/post-
  process, QueryAndPhysics and ActorCollision=true. Effective collision really
  remains enabled on this later compatible spawn. No shot attempted.
- action_gate_author_v6_20261006 closes only the new NPC adapter's live rifle
  Actor collision during equipment configuration; source gun/policy unchanged.
- action_combat_runtime_v3_20261006 verifies five selected-policy bindings and
  actual Allied Stop/Turn, two original hostile hits100→65→30 and ammo2→1→0,
  friendly/world rejection without ammo loss. Original reload finishes0/16→8/8,
  but adapter reports OriginalActionSuperseded, so overall run FAILS.

## Measured cause and changed mechanism

The original ParisReloadDraft.inl PC_EndReload deliberately sets Ready and
increments ActionID once, retaining ReloadActionID/ReloadGeneration. V4-V6
adapter falsely requires unchanged ActionID even at Ready. V7 accepts only
the matching retained transaction, current task/request/generation and normal
Ready+one-ID-advance terminal pattern, then requires one commit and conserved
ammo. Other ID/token changes remain cancellation. Task supersession uses the
original guarded PC_EndReload rather than allowing a cancelled reload to finish.

No health/ammo field, original transaction, animation, mesh, weight, grasp,
first-person, formal map or Catalog is changed. A corrected author or endpoint
ammo does not establish its runtime proof. Fresh dual-faction tests must pass;
preserve all prior receipts, packages and unsuccessful assertions. Source
compilation/transactions do not prove continuous motion, recoil, near-wall,
FPS, Shipping, teammate restoration or course MVP acceptance.

action_combat_runtime_v4_20261006 passes the full Allied action sequence with
correct original terminal identity. It fails the German external stop assertion:
the harness compares with pre-placement height, not the admitted Stop position.
German Stop was admitted atZ191.676cm while the earlier Allied placement baseline
differs1.787cm. The new harness starts drift measurement at actual admission;
the1cm limit and native StopOrigin remain unchanged. No body/nav asset repair or
successful German stop/action pass is inferred before the fresh run.

Fresh action_combat_runtime_v5_20261006 passes both factions with693 guards
exact and normal exit0. Each performs two native hits, friend/world rejection
without ammo loss, and one original0/16→8/8 reload with observed returned IDs.
Autonomous_author_v1_20261006 then fails before saving any package because a
Blackboard Object pin cannot connect directly to Controller.LineOfSightTo's
Actor pin. The next distinct author uses the verified combatant cast. This is
an author type mismatch, not autonomous runtime evidence or asset damage.

Autonomous_author_v2_20261006 saves five compiled packages, previous693 guards
exact. autonomous_runtime_v1_20261006 passes selected five private controllers,
both native Stop/Turn/Fire/Reload encounters, friendly no-ammo waits and observed
target-death attack cessation. It then FAILS the interruption fixture: lifecycle
reset preserves7/8ammo and3prior shots; one100HP target dies before7rounds are
exhausted, so reload never starts. This is a wrong refill assumption, not an AI
reload failure. The changed fixture presents three finite original opposing
bodies, records real remaining ammo, and preserves post-death ammo across reset.
Joint-shot assertions compare against each actual starting ShotSequence.

autonomous_runtime_v2_20261006 again passes the seven preceding checks but
fails acquire_interrupt: native sight selects the second legitimate Allied
target rather than the fixture's fixed first Allied. The new interruption
fixture accepts any of its three declared live opposing actors; the ordinary
single-target encounter still requires its exact target. No Blackboard write,
native sensing change or weakened ammunition/death guard is introduced.

autonomous_runtime_v3_20261006 fails earlier after the Allied friendly-lane
wait: sight memory remains true but CombatHold=false/Acquire and no further
decision. This run is not a full autonomous pass. The observer adds actual
current LOS, target/player/friendly geometry, LastSeenPosition, role distances
and equipment flags to distinguish a scene obstruction from a native gate.
No speculative AI threshold or pose change is made from the incomplete sample.

action_combat_runtime_v6_20261006 passes seven checks/698 exact: both factions'
completed reload replay/stale original tokens do not double commit; real partial
reload task supersession returns the admitted identity/Ready, and late callbacks
or elapsed original duration do not load ammo. autonomous_runtime_v4_20261006
passes ten checks/698 exact including native dual-faction combat, death during
reload, original reset and12-second six-actor finite interaction. Its geometry
supports a near900cm player-distance fixture hypothesis for V3, not full causal
proof: the old player placement settles about440cm below street height.

selected_combat_regression_v1_20261006 passes all21 original shots/three shooters/
two FF modes with current policies and no historical manual equipment staging.
autonomous_runtime_v5_20261006's nearer-player fixture passes both fights, then
FAILS the German corpse assertion: native sight correctly selects the live player
instead of leaving TargetActor null. The next harness requires the original
corpse to be absent, permits only that declared live opposing player, and checks
any additional shots against actual player damage. It does not stop correct
enemy reacquisition or permit continued shots into a dead target. Failed raw
receipt, six passed subchecks and exact698 guards remain retained.

autonomous_runtime_v6_20261006 passes all11 checks/698 exact, including corrected
per-target corpse/player reacquisition, real reload death/reset and joint finite
combat. action_combat_runtime_v7_20261006 FAILS before equipment/action tests:
the harness calls EditorAssetLibrary.load_blueprint_class during PIE. UE emits
"The Editor is currently in a play mode", then the policy query returns no
actors. One policy was correctly staged before PIE. The next harness retains
the class resolved during setup and uses runtime GetAllActorsOfClass only;
no policy asset or shared damage change follows. Failed evidence/698 exact and
normal process exit are retained; FF ON AI admission still needs a fresh run.

action_combat_runtime_v8_20261006 now passes all9 checks/698 exact/errors0/exit0:
both factions' real AI action admission refuses friendly lanes under OFF/ON,
and original action/reload/replay/task-cancel/late-token proofs repeat. No new
native asset repair or shared mutation is needed. Final read-only698-row audit
combat_v2_final_20261006_v1 is exact;87 disk B packages all registered, UE process
count0 at22:17:26EDT6October. These scoped successes do not erase prior failures,
prove V3's whole cause, or establish full visual/FPS/mission/formal selection.
