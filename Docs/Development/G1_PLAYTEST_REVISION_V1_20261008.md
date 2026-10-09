# G1 human playtest revision V1

8 October 2026. Chinese review: [paired document](G1_PLAYTEST_REVISION_V1_20261008_ZH.md).
Authority: Yupu's packaged-playtest feedback requests restored run/prone/slow/jump,
more Allied separation, a clear-three-guards checkpoint circle with explicit save
confirmation, a readable designed HUD and an upper-right minimap.

Cases read: Failures/README; MI004-MI012, ML022, AN007; PLAYER_ACTIONS_RESULT and
PLAYER_ACTIONS_IMPLEMENTATION; FP formal V21; the V13 native-route/agent-coordinate
plans and actual closeout result. The older actions candidate had numeric passes
but incomplete human presentation acceptance. It is not an already accepted
production character. No stopped grip/action proof or recorder is reopened.

## Bounded preflight correction

candidate_v1 stopped before wrapper creation or any engine launch: the 3 October
V6 inventory hash ebf22a46...8e1f0 differs from current572a0d99...2fbe8,
1,355,976 bytes. RELOAD_INDEX_CONTACT_V6 and WEAPON_TRIGGER_ALIGNMENT_RESULT,
plus Evidence/ReloadIndexContactV6/map_recovery_v1/result.json, already record
the user's 4 October accidental save and retained unselected V6 rate change.
The current703-row epoch protects these same bytes. No unknown mutation or
automatic restoration is assumed. A distinct candidate_v2 explicitly uses this
retained version for the user-requested private action integration ONLY after
both recovery and current rows match exactly. Historical inventories stay intact.
Compile/startup must validate actual inherited camera, mesh/materials, resource
interface and ownership; any mismatch stops that mechanism. Old action passes
are historical and are not transferred to this changed version without testing.

## Diagnosed scope and protected baseline

9 October continuation: v2 stops at compile C2181 because the HUD logging macro
requires braces around if/else. No cook/runtime reached. Preserve its complete
failed wrapper. Distinct v3 fixes that exact syntax and adds a finite opt-in native
key/checkpoint observer, inert in normal play. It sends simulated engine press/
release events and native MoveTo/visible aim, never writes poses/resources/deaths.
This is new integration coverage, not a rerun of stopped AN007 full-motion proof.
Ordinary Ready startup must pass first; input and checkpoint tests are separate
240-second entries, stop on first assertion, actual images reviewed independently.

Source review also finds the old Ctrl+R restart conflicts with restored Ctrl
crouch and R reload. v3 is an early admission build, not delivery. The next
delivery revision removes that shortcut (F6 remains), with an explicit held-Ctrl
reload check; no weapon transaction is changed.

V4 may reuse V3 cooked content only after ordinary V3 Ready/image/integrity
admission. Freeze all exact V3 source first. Continue in that private build
checkout with exactly TWO .cpp implementation changes (shortcut/test), all
headers/native defaults/config/Content unchanged. Authenticate every reused
cooked/package file, rebuild the monolithic Game executable, and copy unchanged
packaged files into a NEW V4 folder with only that executable replaced. No header,
constructor/default, asset, config or serialization change permits this route. Record
the shared build path explicitly; V3 Archive, source snapshot and receipts remain
unchanged. This is content reuse for method-only compilation, not old binary or
test reuse. Every V4 runtime gate still runs on its own executable/hash.

V4 preparation stopped at its change-path assertion before build: Windows
backslash records were compared with slash literals. The two intended .cpp
changes had been written and V3 source frozen. No third source, header/config/
Content change or engine launch occurred. Retain this negative and frozen V3;
distinct V5 read-only admission reconstructs the two expected texts from frozen
V3 and verifies every other file byte-exact, then normalizes path spelling only.
No automatic rollback/reapplication or native tolerance change. The same bounded
method-only reuse rule above applies to V5; runtime gates use V5's own binary.

V13's recorded player is BP_PCParisPlayerV1. PC_Run/Slow/Jump/Crouch/Prone mappings
are present in DefaultInput.ini, but their implementation lives in the separate
BP_PCParisPlayerActionsV6 child, never integrated into this mission. A key mapping
alone therefore does not provide the action. The native mission HUD is a temporary
top-left text block; no minimap/checkpoint prompt exists. Won calls GateBrains(false)
and locks player movement, conflicting with walking into a later checkpoint zone.

The squad route also clamps both negative trailing arc positions to its first
point when the player has not advanced 450/700 cm. That can draw both Allies toward
the player's starting point. This is a source-based hypothesis until observed
with player stationary after Start; do not mislabel it as confirmed spawn movement.
Existing initial positions are about 4.6-4.7 m from the player, not zero separation.

Use a NEW private wrapper based on the exact tested V13 SourcePatch. Preserve its
single witnessed bridge exclusion, agent-feet preflight and far-bank settling.
Retain the user-controlled old extraction/build, original city/collision/nav,
models/rig/weights/materials, accepted FP/Allied/German fingers and grips, original
rifle/ammo/damage/reload/checksum/journal transactions. No canonical package save,
Catalog/source-contract update, model acquisition, commit/push/publication.

## Changes, in order

1. **Player actions.** Integrate the existing V6 child into the new mission wrapper
   before BeginPlay, reusing the same original gun/camera/display ownership. Verify
   exact mesh/material/scale/camera/resource compatibility first. Existing actions:
   WASD walk150, Shift run300, Alt slow65, Space jump, Ctrl crouch120, Z prone60
   (cm/s). Reuse native Blueprint action/collision logic; no new animation or pose
   driver. Keep standing-only fire/reload and bounded forward/back prone safety;
   do not silently enable unaccepted prone firing/strafe/yaw. Current approved FP
   source/hand bindings remain. Packaged startup and each physical input require
   fresh checks; prior V6 tool results are not this package's acceptance.
2. **Squad spacing.** Admit the existing trailing route only after enough forward
   arc exists for that member. Before then hold its original position, rather than
   collapse both goals onto the player. Observe actual stationary-start separation
   and crossing. If original placements themselves fail human spacing, select
   measured legal points under a separate placement admission, not a blind offset.
3. **Checkpoint.** After all THREE stable G1 guards have legitimate recorded deaths,
   show a ground circle at the already measured G1 anchor (180 cm radius) and its
   minimap marker. The original crossing/capture requirements still govern Won.
   Won stops NPC combat but keeps living-player movement/look available. Entering
   the circle shows “Save checkpoint? [E] Save [Esc] Later”. Do not save on entry.
   E uses the original safe-save/journal transaction once; unsafe state shows the
   original denial and permits retry. Leave/decline must rearm only on next entry.
   F5 requests that prompt, never bypasses the zone/confirmation. F9 loads; F6
   restarts; remove the conflicting Ctrl+R shortcut. New config/slot V5 rejects old schemas
   through the existing fingerprint validation. Save only standing/grounded/still;
   do not serialize an unsupported prone/airborne pose or manufacture resources.
4. **HUD.** Compact objective top-left; health bar and squad status bottom-left;
   large loaded rounds, reserve rounds, eight-round capacity pips and rifle identity
   bottom-right. Use actual Health/LoadedAmmo/ReserveAmmo/Capacity/ActionState only.
   Any full-load equivalent is derived from reserve/capacity with remainder shown;
   it is not an invented individual-magazine inventory. Low health/ammo use shape
   and readable labels as well as colour. Add contextual save question/status and
   compact controls help. Scale layout to viewport with safe margins.
5. **Minimap.** Upper-right, north-up in the existing map XY convention, player
   heading, living Allies, current objective and unlocked checkpoint. Reuse a
   static metric 2D texture generated from authenticated G1 saved NavMesh polygons;
   clearly distinguish navigable and blocked areas. This depicts that measured
   ground scope, not a full-height city survey. Cache the texture once and marker
   updates at 5 Hz; no additional per-frame scene camera on an already limited
   render thread. Enemy marks require actual player FOV and line of sight, never
   all hidden German actor coordinates. Verify XY/corner/heading/world mapping.

## Reference and visual direction

[Activision's WWII campaign HUD reference](https://support.activision.com/content/atvi/support/web/en/call-of-duty--wwii/articles/call-of-duty-wwii-campaign.html)
groups weapons/equipment, health/first aid and current objective. The
[official CoD HUD terminology](https://www.callofduty.com/guides/getting-started/call-of-duty-modern-warfare-iii-play-guides-getting-started-in-game-terms)
distinguishes loaded and reserve rounds, with weapon information bottom-right.
[PUBG's own no-HUD experiment](https://pubg.com/en/news/1687) identifies minimap,
compass and ammo as ordinary play aids. Use these information priorities; do not
copy commercial HUD artwork, modern tactical-sprint features or regenerate models.
Our proposed composition uses muted olive/cream/dark panels, an amber objective,
green Allies/checkpoint and red only for danger. Upper-right map follows Yupu's
placement request. A schematic preview is design, not a gameplay screenshot/pass.

## Early admission, verification and stopping

Before writing a new wrapper: exact V13 source/binary identity, canonical758/359/
703 and the explicitly authenticated retained V6 hash, no user engine overwritten/stopped. First compile and
ordinary startup must show the V6 player, same camera/grips/gun/resources, one
native route policy and one plan replacement. Stop at the first class/property/
ownership/asset/compile/strict-log mismatch, preserve the new failed identity.

Then check actual input press AND release, measured speed, jump/land, low ceiling
and forward-prone obstruction; wrong presentation/contact remains a visual failure
even if state toggles. Test stationary-start squad spacing before full original
55cm/25s/body gate. Check guards0/1/2 produce no checkpoint, three actual deaths
unlock once, entry does not save, decline/exit/reenter, E safe commit once, unsafe
denial, fresh load/resources/restart and old-fingerprint rejection. Inspect actual
Ready and post-clear HUD images at1080p and a smaller window; verify minimap XY,
visibility and marker deaths. No synthetic movie or numeric colour-only admission.

Do not relax original resource/collision/navigation bounds or claim60FPS. No
recording/performance sweep in this revision. On the first unmet early/core gate,
stop that mechanism, archive the negative and document the next different bounded
change. Human full motion/camera/contact and second-machine gates remain explicit.

## 9 October bounded terrain diagnostic after actions_v1

actions_v1 stops at prone_capsule after real walk150/run300/slow65, releases,
jump/land, crouch60 and held-Ctrl reload denial pass. Z leaves DesiredPosture0
at feet(2942.423,-20662.500,98.977). The existing safety check refused entry;
this is not proof of a missing key or proof of uneven ground. Record it unchanged.

Cases reread: MI012, PLAYER_ACTIONS_RESULT and source-author/test implementations.
Distinct V6 changes only the opt-in observer cpp: report actor scale, scaled versus
unscaled feet, actual original-size visibility box hits and three floor supports
(normalZ>=.97, height<=10cm); preserve thresholds/assets. Probe at most nine
near-start ground positions, require each footprint plus120cm forward crawl
corridor and a complete UE path. Select one qualifying position, physically
MoveTo it, settle, then use actual Z/W/releases. No teleport or geometry change.
Early gate: original feet frame parity and refusal/probe agreement; stop for
frame mismatch, no admitted site, partial/missed physical path or failed input.
This covers original terrain-restricted prone, not arbitrary bridge prone,
full-motion/contact/human acceptance. Independent checkpoint_v1 continues on V5.
Freeze V5 source first; V6 uses unchanged headers/defaults/config/cooked payloads
and a newly built executable. Do not relabel V5's failed action gate as a pass.

Checkpoint_v1 also stops: legitimate player death at bridgehead with all18 rounds
spent and no recorded guard death. No save gate reached. V6 observer separately
preloads by real R at the safe start, halts native movement when a visible target
exists, settles ACTUAL camera direction within.3degree before real input fire,
and resumes the same route afterward. Samples include actual shot outcome/health.
Stop at2seconds of unaligned camera, death or resource/path mismatch. This changes
the test driving strategy, never gun damage/ammo/enemy health or death ledger.

## V7: reuse measured safe site and test a real obstruction

actions_v2 stops at the declared120cm clear-crawl-corridor admission. Actual
scale1/feet delta0 and original refusal agree: rubble actor2031 intersects the
body; local supports include normalZ.938/.953 and18.66cm height delta. This is
confirmed local terrain restriction, not a missing binding or a general-city claim.
Nine-site probe finds TWO locally valid prone footprints, but forward120cm is
blocked. Retain the conservative negative; do not continue an offset/site search.

Distinct V7 uses ONE already measured site(1762.5,-20662.5,114.402), with its
measured+60cm clearance and+120cm obstruction actor2081. Require an original
complete UE path, real<=45cm arrival, actual clearance, then actual Z. Hold W
until the original predictive safety refuses movement; verify positive physical
travel, blocked flag and stable position for at least.7second. Verify S produces
real backward movement, key release stops, then stand/original reload/fire.
This replaces an unmet unobstructed120cm test with a separately declared actual
obstruction test; it does not waive original collision or change the old result.
Early/stop: no teleport, no candidate scan, no unsupported footprint, no movement
while blocked, no resource mismatch. V7 only changes opt-in observer cpp; no
header/default/asset/product behavior change. Game-only compile is sufficient
for this monolithic Development observer; Editor not rerun or claimed.

## V8 before build: actual ballistic visibility, not damage edits

Checkpoint_v2 stops at240s with health100, three living guards,18 shots exhausted,
and sampled ShotOutcome=World blocked1817 times. Camera alignment is.000101deg;
this is actual muzzle-to-target world occlusion, not a camera binding failure.
Stopped movement at the first eye-visible point kept firing from blocked cover.
No checkpoint gate reached. Retain logs/result; no third unchanged driver run.

V7 was prepared for the separate measured prone obstruction but never compiled.
Preserve its source/recipe as superseded-before-build, not a runtime failure.
Distinct V8 observer keeps that prone test and additionally uses read-only SAME
noncomplex camera/bullet rays and radius2cm noncomplex barrel/muzzle sphere sweeps as the original gun.
Continue the original native path while obstructed; halt/aim/fire by real keys
only after eye AND authoritative WeaponAppearance muzzle paths clear the target.
Fail immediately if finite original rounds exhaust. No weapon transforms, damage,
health/deaths, path tolerances or assets altered. Early gate remains exact query
policy, actual camera settle, real hits/deaths and original bridge bodies. Stop
on original loss, exhaustion or240s deadline; never force a death/save success.

## V9 product fix: future floor supports before movement integration

actions_v3 actually reaches the retained site, enters posture2/half34, crawls
17.251cm and stops with0cm drift. Backward input then remains blocked. Source
review identifies that the original function predicts the box but samples floor
supports at CURRENT feet; a step can cross into bad support and reject both axes.
Preserve this negative; the source hypothesis is tested by the next countercheck.

Cases reread: MI012, original V5 late-stop failure and V6 action source; installed
UE PlayerInput::ProcessInputStack calls PostProcessInput AFTER input delegates,
and Controller::AddPawnTickDependency orders movement after controller. V9 adds
a native PostProcessInput override to the PRIVATE mission controller only: reuse
the unchanged130x55x28cm swept body and all three normalZ.97/height10cm supports,
but check them at FUTURE feet before queued movement integrates. On refusal,
consume pending input and stop velocity. Never permit an action V6 refused.
Keep original input/posture clips, source packages, camera/grips/weapon logic.
One non-reflected virtual declaration plus cpp implementation changes; no UCLASS/
UPROPERTY/UFUNCTION/default/serialized schema/config/cook dependency changes.
Method-only Game rebuild reuses byte-verified cooked payload; no Editor claim.
Read-only native blocked witness is keyed to the current weak player pointer,
reset on every input pass; no per-frame pose driver or resource writes.

Early acceptance: actual prone forward positive movement, stable refusal, then
S back away and key-release stop; all original frame/terrain/resource gates stay.
Stop at any blocked drift, unchanged backward failure, original action rejection,
strict log or model/resource mismatch. No wider clearance/slope budget. Replay
checkpoint on final product binary because product input code now changes.

V8 checkpoint_v3 numeric loop passes actual9Hostile hits/three deaths, original
bridge gate, decline/reentry/unsafe denial/explicitSerial1/freshload/fullrestart.
Its prompt screenshot is captured after synchronous Escape already dismisses
the HUD; retain it as a decline/ring image, NOT viewed question proof. V9 adds
a one-second capture boundary before Start/Escape/load/restart; no action or
world mutation between Shot and the next decision. This is finite screenshot
verification, not reopening any stopped recorder/continuous-contact route.

## V10 observer placement correction, product V9 retained

actions_v4 stops at the declared10cm physical-travel assertion: actual9.80077cm
at60cm/s, zero blocked drift, future-floor refusal and ORIGINAL ProneClear=true.
The V9 prediction stopped earlier as designed; backward was not reached, so it
is not passed. Native SimpleMove settled40cm ahead of the intended safe anchor,
using the unchanged45cm arrival gate; the tiny crawl space fails this assertion.
Retain raw result, do not round up or shrink the10cm requirement.

Distinct V10 changes only the actions observer: after the same complete native
path/45cm arrival, real standing S input closes the remaining X gap to<=15cm
(with Y<=15cm,2s bound), releases and settles. Actual footprint must still pass
before Z; no teleport/new site/threshold/velocity/asset change. This places the
body at the already measured anchor rather than its navigation acceptance edge.
Same forward/refusal/S/release/reload/fire tests remain. Stop at placement/clearance
or original action gate. V9 product/header/config/cooked payload unchanged;
checkpoint_v4 independently tests the V9 product and visual decision boundaries.
Final ordinary entry validates the newly built observer-disabled executable.

Checkpoint_v4 on V9 exits3 at FIRST GPU frame before Ready/test events:
DXGI_ERROR_DEVICE_HUNG/removed, GPU page fault,4.865GB local usage versus9.285GB
budget; this is not evidence of VRAM exhaustion or a gameplay/save failure.
No result JSON/acceptance. Preserve launch/log/crash data. V9 actions_v4 had
already rendered/operated normally; cause remains unverified. Do not repeat a
renderer/recording variant or tune GPU flags. Final V10 qualification uses the
unchanged High1080/RT-off profile after ALL builds/hash/copy work and other
engines finish, without concurrent heavy preparation. This isolates conditions,
not a claimed GPU fix. Stop final entry if the device failure recurs.
