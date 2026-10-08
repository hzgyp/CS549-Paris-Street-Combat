# Purchased muzzle flash integration

7 October 2026. The user requests visible firing flames using the purchased
MsvFx_MuzzleFlash_Pack. This work covers the current player and supported Allied
and German rifles. Preserve accepted meshes, rigs, weights, grips, recoil, weapon
equipment, ammunition, damage, AI, navigation and the current map. No asset
publication, Git commit/push or supplier example-gun gameplay is implied.

## Cases and asset baseline

Read Failures/README, AN001, AN008 and AN009. Failed Blueprint owner construction
is not reused. Ready is not a shot event: read the real committed ShotSequence
and RestoreGeneration, never mouse input or an AI request. Denied shots produce
no effect and binding must not replay old shots. AN009's map-loading reentry and
occluded/dark images require load before callback registration, frozen observer
sources and readable actual images rather than file-existence checks.

The 4 October intake audit records 68 packages, 78,239,739 bytes and four rifle
Niagara prefabs at /Game/MsvFx_MuzzleFlash_Pack. Its UE4.26 headers are not UE5.8
compatibility proof. Rehash the exact intake, preserve it, copy only the candidate
effect dependency closure into a separate private test project under its actual
package root, and exclude AK47/M4/carbine examples, shell effects and demo maps.
Header reference scans are preliminary; native registry/load/compile and runtime
tests must establish actual dependency closure. Purchase authorizes this local
evaluation, not a group license finding or public commercial-byte publication.

## Changed mechanism

Use a separate native Niagara presentation adapter, not another grip/recoil
binary rewrite. First prove purchased systems load and run finitely in the
installed UE5.8.2. Measure their forward axis, dimensions, timing and dependencies
before selecting a rifle-compatible one-shot variant. Preserve original intake;
any needed version conversion is a private candidate, never an overwritten
receipt. Do not replace a missing or broken purchased effect with a generated one.

The adapter observes supported combatants in a game world, binds to the actual
visible rifle component and uses a separately measured rifle-local muzzle
profile. Effects remain attached while recoil moves the gun, do not control
hits or ammunition, and clean up on death/reset/world teardown. First-person
and NPC visibility must be verified separately. Record visual and authoritative
shot muzzle transforms; do not assume the legacy actor-local (0,83.23,0) point
fits every accepted rifle or silently change combat traces to conceal a mismatch.
A muzzle-authority discrepancy needs its own bounded correction before claiming
ballistic/near-wall acceptance. Rendering attachment alone is not that acceptance.

## Early acceptance and stopping

Before city entry, load the four purchased candidates and their dependencies in
an isolated Entry world, verify native system readiness, a finite discharge,
correct flame origin/axis and actual rendered images. Stop on missing hard
references, failed Niagara compilation, perpetual emission, native crash, source
hash drift or unknown conversion requirements. Retain failures rather than
resaving originals or forcing them into Git.

After the early gate, test real one-shot/cooldown rejection, repeated shots,
empty/busy/dead rejection, reload/death/reset cleanup and no historical replay
for player/Allied/German representatives. Observe one effect per committed shot,
actual attachment drift and component cleanup. Inspect readable normal player
and NPC images, then a fresh original-project regression. No claims of all-NPC,
stress FPS, complete contact/near-wall, Shipping or teammate acceptance follow.

Protect the current 703 rows and the purchased source inventory during candidate
work. Never start a second native engine or stop another window's engine. Prepare
offline while the map survey owns the slot. Local adoption, after verification,
may add the selected private dependency closure/profile/new plugin and its exact
enable entry with backups and an explicit narrow ledger; no formal map save,
existing display-DLL replacement, Catalog/SFTP publication or dependency deletion.

## Preliminary reference correction

Read AN010 before the second preparation. The first scanner equated every
serialized /Game string with a hard dependency and stopped on the absent
Niagara_Small_MuzzleFlash_01. No candidate or native entry was created. The new
preparation records unresolved names separately and copies only present graph
nodes; native hard/soft classification and system readiness still decide
compatibility. This is not permission to ignore a missing hard dependency or
declare that the supplier pack is fixed. Preserve all68 originals and703 guards.

The native v1 gate then reveals a real hard dependency omitted by that regex:
the present Sm_Root_Muzzle_Flash_0, whose numbered FName is not its raw string
base. v1 stops before system loading with owned exit0/strict0; it is not a pass.
A different v3 preparation seeds the exact native hard-reference receipt into
the copy graph. Only authenticated existing supplier bytes may be added. The
next native gate must still have no missing hard references; no supplier graph
repair, renamed surrogate or compatibility waiver is allowed.

Native v2 closes25 actual dependency records and loads four valid CPU systems,
but its NullRHI readiness assertion fails. Installed NiagaraSystem.cpp rejects
readiness when FApp::CanEverRender is false. Different v3 uses the real renderer
and a finite readiness wait; no graph mutation/readiness override is permitted.
It is still an Entry asset gate, not rendered flame or firing acceptance.

## Asynchronous compilation observer correction

Read AN010's native v3 failure together with AN001, AN008 and AN009. Real
rendering exposes ordinary asynchronous compilation: all four systems report
compiling=true when the observer asserts valid. Installed NiagaraSystem.cpp
IsValidInternal inspects compiled system/emitter scripts; this in-flight sample
does not establish final compilation failure. Preserve v3 owned12472 exit0,
strict0, exact703/68 and its negative result; do not rerun that assertion order.

The different native_assets_v4_20261007 keeps real rendering, dependency and
class gates but treats explicitly outstanding compilation as pending before
checking final validity. Record state transitions. Early acceptance requires all
four systems to be loaded, have emitters, finish compilation, be valid and ready
within the unchanged180-second bound. A noncompiling invalid system fails
immediately; a readiness/compilation timeout still fails. No graph/asset resave,
compile-status override, original-byte change or effect execution is authorized
by this observer correction. Runtime/visual integration remains a later gate.

## Isolated finite effect gate

Native v4 now passes four final valid/ready systems with exact703/68 and normal
owned39760 exit0/strict0. The next effect_render_v1_20261007 is a new unsaved
Entry PIE fixture, not a city firing proof. A diagnostic-only private build adds
a safe game-thread component completion/bounds query; no system-instance or
skin buffers are accessed. Load/compile before callbacks, disable temporary
background throttling and restore its original value at closure. Instantiate
each authenticated candidate once with defaults and no deactivation/graph edits,
record actual completion and native 1600x900 renders at finite age thresholds.
Early acceptance requires an actual spawned active component, readable original
flame images and natural completion within8game-seconds; no forced destruction
counts as completion. Stop on perpetual emission, invalid system, native/log
failure, no game-time progress, or protected-byte drift. Keep all failed frames
and receipts. Direction/size remain measurements, not a selected profile or
permission to modify accepted rifle/grip/ballistics.

## Controlled pulse alternative

Read AN010's default-emission failure before effect_pulse_v1_20261007. Rifle01
does not self-terminate by8.007209game-seconds, so its default-start path remains
stopped. One original image shows flame; four early images are black. A different
bounded presentation control activates each candidate once, requests ordinary
Deactivate at0.10game-seconds and lets native existing particles finish. Preserve
graphs and supplier defaults; no Destroy/DeactivateImmediate is counted as
completion. Record actual activation/stop/completion ages and original renders.
Early acceptance requires visible short-pulse flame for each admitted candidate,
native complete within8seconds, no continuing active emitter and exact703/68.
Stop on delayed/invisible pulse, persistent tail, runtime/log failure or source
drift. Do not sweep activation duration or call this default self-termination.
Only an admitted candidate may inform a later native real-shot adapter revision.

## Remaining untested rifle variants

Read AN010's pulse failure, AN001, AN008 and AN009. Pulse v1 activates only01:
ordinary Deactivate is requested at0.161489seconds and native complete is true
at0.218597seconds, but all three original frames are black. Subsequent Python
destroy_component() omits the required Object argument and prevents02–04 from
running. Keep01's default and pulse paths stopped; fixing cleanup does not
admit its invisible discharge.

The different remaining_pulse_v1_20261007 evaluates only02–04, once each under
the same requested0.10-second window and8-second completion limit. Its source
must reject01 and require the actual prior negative receipt. Installed UE5.8
ActorComponent.h exposes K2_DestroyComponent(UObject* Object); pass the completed
component itself through reflected call_method, only AFTER real IsComplete.
Capture the asset-owned exposed float defaults through the typed parameter-store
API in a new independent diagnostic build. This is read-only asset metadata,
not a parameter override, graph edit or live system-instance buffer query.

Early acceptance still requires readable short-pulse flame AND native completion
for an admitted variant. Stop each failed variant; no duration sweep, warmup,
01 replay, default-start retry or runtime enabling. If none of the three original
variants is visibly usable, preserve all results and diagnose the recorded
metadata before proposing a different mechanism or asking for specific authority
to change parameters. Current703/68 stay exact.
