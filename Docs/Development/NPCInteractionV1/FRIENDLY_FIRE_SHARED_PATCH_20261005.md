# Authorized shared friendly-fire patch

5 October 2026. The user explicitly permits this window to integrate the shared
change and regression-test player, Allied and German shooters. This narrowly
supersedes the handoff's coordinator-only shared-write rule. It does not authorize
map selection, NPC grip fitting, first-person/reload repair, publication or Git.

## Cases read and changed mechanism

Read the NPC handoff, parallel plan, current approved FP V21 and NPC baseline,
Failures/README, AN003/FP001, native combat author/test, German native V2 records
and this lane's sight/movement/pure-node failures. Preserve original ammo,
cooldown, reload, death/generation, traces, body blocking and hostile damage.
Patch only the existing friendly-hit terminal in `PC_DoShot` of
`/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisCombatantV2`.

One new B-owned world policy Actor supplies `FriendlyFireEnabled`, default false,
through a public native setter. All inherited shooters read the same world Actor;
no per-shooter copied switch. Missing policy means false. Friendly OFF retains
the old blocked result/no damage. ON calls the original `PC_ApplyDamage(35)` once
for a living friendly hit and reports `Friendly hit`. Neither setting changes
TeamId or target selection. Dead actors receive no duplicate damage/death; keep
their original death posture/collision rather than a new tall standing blocker.
AI still requires a clear friendly-free firing corridor independently of this
damage permission; this patch alone is not autonomous combat acceptance.

## Exact targets, recovery, early check and stopping condition

Before authoring, verify all current guards and no external UE process. Back up
the actual shared package and record its original size/SHA. Its two known paths
are aliases to one physical Content file, not permission to edit two unrelated
assets. Verify exactly one old `Friendly blocked` setter and its one incoming
exec edge; change only its continuation, leaving the entire old graph present.
Compile before the only shared save. Save only the new policy and shared base,
never Save All. A failed in-memory author leaves the old base unsaved.

After save, compare every protected path. Exactly the authorized shared-base
aliases may change; all map/FP/Catalog/old B/source/weapon paths must remain exact.
Record old/new rows in a deliberate mutation ledger used by later B preflight.
Do not suppress arbitrary mismatches or rewrite the historical 555-row snapshot.

Fresh actual-city tests use the original fire/reload/damage/reset entries with
player and both NPC factions: OFF/ON friendly hit, hostile hit, friendly/world
blocking, one ammo charge/one damage, cooldown, dead-body no second damage and
team stability. Stage the existing normalized German V2 gun unsaved, no fitting
or new gun. These transaction tests do not approve visible NPC hand contact.

Continue cause-specific API/test repairs within this scope. Stop the relevant
writer on a different protected change, concurrent owner, ambiguous target or
need for a new asset/visual decision; preserve backup/evidence and ask the user.

## Author API correction

Native compiler warnings show `GetActorOfClass` is BlueprintCallable with an
exec pin, not a pure getter. The initial author preserved the old OFF path but
left the new query pruned; author success is not ON runtime acceptance. The
separate exec-edge repair inserts that existing query between the original
friendly setter and policy cast, without removing nodes or changing damage.
Preserve both author backup/hash epochs. The squad author receives the same
cause-specific correction in new V2 packages. Later graph-only author launches
use NullRHI to avoid irrelevant material/DDC work; actual-city tests still use
normal RHI, and neither is visual acceptance by itself.

Regression v1 passes Player OFF friendly blocking but schedules the next shot by
wall time while game time/cooldown lag during editor stalls. V2 uses actual
NextShotTime and passes that hostile35 hit; the next case incorrectly expects
PC_ResetLifecycle to refill spent ammo. The original function preserves ammo,
so v3 requests and waits for the original reload when the next fixture needs
rounds. No direct ammo/health writes or shared transaction repair are warranted.
All original failures/case data are retained; do not label these legal rejections
as native damage defects. Conservation includes rounds loaded+reserve+shot count.

V3 verifies Player ON35 once/hostile35, then fails an extra assumption that the
dead friendly still blocks a standing-height shot. The retained native lifecycle
source explicitly disables the capsule on death, and its original test requires
`dead_capsule_not_obstructing`. Preserve that behavior, not a new corpse wall.
Next regression records actual corpse collision and verifies no repeated damage/
death through the original entry. This corrects an unrequested harness assumption,
not the required live-friendly blocking or single-damage threshold.

Next direct regression also inserts an unsaved BlockAll engine cube between each
shooter and its hostile target, under both FF settings. Early acceptance requires
original shot admission/ammo consumption, `World blocked`, and no target damage;
the original game-time cooldown and reload refill are respected. No city save,
new collision system, NPC autonomous combat, gun fitting or human-grip approval.
ActionGate V1 additionally failed resolving a pawn-only public function from a
controller self context before any asset save. V2 uses the already proven typed
external Blueprint-call mechanism; preserved V1 evidence is not runtime failure.

Exact declaring-owner correction subsequently compiles ActionGate V3, without
changing the original transaction parent. Direct combat/default-gate tests now
launch with command-line DisablePlugins=ParisEditorBridge (verified in local
UE5.8 PluginManager source); absence of its authoring reflection class is checked.
This does not edit the project/config or disable the approved FP runtime module.
Python supplies test stimuli/observations, never a pose/AI/damage simulation.
