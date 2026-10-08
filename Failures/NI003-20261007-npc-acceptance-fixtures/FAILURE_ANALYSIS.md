# NPC acceptance fixture failures and body-arrival findings

7 October 2026. Scope: existing FormalCombatV1 functional acceptance; no native
asset, formal map, selected model/grip or original action mutation.

accept_formal_roles_v1_20261007 passes five scoped checks under exact703 guards,
owned exit0. It proves reserved arrivals/retention/death ownership, three private
frozen-memory searches ending at23.954s against23.781s deadlines, and guard return/
patrol resume. It does not prove a complete new patrol roundtrip or gait visuals.

accept_formal_travel_v1_20261007 FAILS at its early path check. Five selected native
bootstraps/private brains pass, but the raw second formation destination
(-5882.823,-1320.000,193.463) has no complete path. No chase boundary is exercised.
703 guards remain exact, engine exit0. The fixture incorrectly demanded a route
to a raw offset whereas the actual SquadV4 controller first projects offsets with
200cm query extents and adds the requesting capsule half-height for body arrival.

The next fixture mirrors that existing projection for its finite start and early
destination checks, records raw/projected coordinates and the actual complete
path, and still stops on a missing/partial route. It does not enlarge the query
extent, alter the controller, relax1000cm chase limits, write Blackboard state,
move NPCs per frame or infer whole-city coverage. Preserve the failed identity and
copied source/log/receipt. A fresh actual cutoff and regroup proof is required.

accept_formal_travel_v2_20261007 FAILS the same early complete-path gate after
projection: the west offset projects to(-5928,-1349,230)ground, bodyZ326.233cm,
an elevated disconnected destination; the first Ally's groundZ114.094cm path is
valid. Projection success alone is not connectivity. Guards703 exact/owned exit0.
The read-only existing NavigationAI coverage_v2 identifies street-centerX
-5542.823cm, the midpoint of the saved two Allied X positions. The next finite
boundary fixture uses that surveyed centerline instead of the left-edge anchor.
It keeps the existing projection extent, both complete-path prerequisites and
1000cm acceptance; no navigation or combat asset mutation, no claimed cutoff yet.

accept_formal_travel_v3_20261007 passes both projected early paths, then FAILS
the actual-cutoff gate: one Ally returns at an inaccessible western goal while
the other reaches875.107cm in a later episode. The fixture's player Actor turn
did not set PlayerController control rotation. Actual Follow goal is400cm WEST
of the player, whereas the fixture checked NORTH-oriented goals; native squad
offsets use actual player rotation. This mismatch, rather than a proven chase
budget bug, invalidates the test. No 10m acceptance or target-switch pass follows.
703 exact, owned exit0. The next fixture sets the player's control rotation ONCE
with its declared facing, logs actual forward/world frame time/shot outcomes and
asserts heading agreement during chase. No per-frame player/NPC pose driver,
new angle search, AI or grip mutation. The launcher executes its unique private
script snapshot so later source edits cannot alter an entry during initialization.

accept_formal_travel_v4_20261007 FAILS overall. Actual player forward is north
and actual world frames are0.25s. Ally0 reaches892.826cm and regroups, but Ally1's
west body route fails at real movement despite a valid queried path. It never
reaches the requested cutoff, so no complete boundary pass or target-switch pass.
The log also contains a handled NavigationSystem class-default-object ensure from
the observer's CDO navigation call; not a crash or clean runtime.703 exact/exit0.
Existing foundation uses get_navigation_system(world), an actual live instance;
the next observer requires that instance and rejects Default__ identity.

Separate the hypotheses: two original Allies are measured sequentially on the
same actually traversed eastern lane for the SAME1000cm boundary; double-body
obstacle recovery remains a separate scenario. First Ally dies through original
damage after its measured regroup, and second has one declared original lifecycle
reset to release old slot1 before native slot0 registration. No direct health,
ammo, BB, goal or budget assignment, no replacement skin/gun, no automatic game
resurrection. This isolates per-brain bounds; it is NOT a simultaneous two-lane
navigation pass. Retain the physical western-route failure for navigation debt.

accept_formal_travel_v5_20261007 passes six FUNCTIONAL receipt checks: actual
target replacement retains each current episode/budget; cutoffs856.383/907.511cm,
physical regroup errors27.610/40.401cm,69actual0.25s chase samples,703 exact/exit0.
Overall launcher gate STILL FAILS because the observer log has the same handled
NavigationSystem CDO ensure. Do not promote its pass_* receipt to a clean gate.
Using a live projection receiver alone did not remove the error. All travel
fixtures, including V1 without projection, used the Python class path wrapper;
the unchanged native-only role fixture has no such ensure. This narrows the
suspect to observer API routing, not a demonstrated runtime AI fault.

The next entry follows the installed/foundation proven live-instance call_method
path route with an explicit actual PIE World, and uses that World in projection
and navigation lookup too. Log before/after each API to isolate any remaining
ensure; keep strict zero-error admission, geometry/budgets and old receipts.
The standalone long-frame check is0.25s/4FPS, not arbitrary-stall immunity or
normal performance. Log validation now serializes plain lines, not PowerShell
FileSystem metadata objects. No native dependency or map mutation.

V6's staged API logs localize the remaining handled ensure EXACTLY between
instance_begin and instance_end, at the Python CLASS GetNavigationSystem call;
live project/path calls follow without another ensure. The earlier attribution
to the class path wrapper was a suspect, not the demonstrated site. Installed
World.h declares transient NavigationSystem and its getter returns that property.
The next observer reads the actual PIE World's reflected NavigationSystem pointer
directly, rejecting Default__ identity; no class-default navigation lookup is
executed. It leaves the actual world manager, path/projection functions and AI
unchanged. V6 remains an overall failed entry regardless of functional subchecks.

V7 stops BEFORE movement: World.NavigationSystem is protected and cannot be read
through get_editor_property. No visibility bypass or native/property edit is
permitted;703 exact/owned exit0. Installed PyCore.cpp exposes the public
unreal.ObjectIterator(type) over object instances. The next observer selects
exactly one non-Default__ NavigationSystemV1 whose outer is the actual PIE World,
then retains V6's live receiver project/path calls. This changes only instance
discovery, preserves the protected field and strict error/boundary gates, and
stops before movement if a unique actual instance cannot be found.

V8 removes the observer ensure: strict log errors0,703 exact/owned exit0. First
Ally switches targets and cuts off907.793cm/regroups29.398cm, but the second loses
visibility and fails the actual-cutoff gate. The retained samples locate the
previous replacement body at exactly the next target's position; hiding did not
remove its collision. A dormant third German also remains in the walking lane.
These are unisolated bodies, not evidence that the bound is violated. The next
finite fixture parks all inactive Germans at distinct far locations initially
and after each cutoff, including the old replacement body, rather than merely
hiding them. Clear movement comparison only for declared relocations. Native
collision/LOS, target choice, budget and complete-path gates remain unchanged;
no per-frame target repositioning. Preserve V8's failed overall admission.

V9 parks the inactive bodies but still fails: even the first Ally acquires then
loses the sole target while remaining at its Follow goal. No clean boundary
acceptance follows. The hidden-body overlap in V8 was real but is not a sufficient
causal explanation for this new failure; do not repeat identical entries. New
read-only diagnostics record actual actor/controller turns, sensor range,
CouldSeePawn, controller LOS and eye-to-eye Visibility hit labels, following the
retained sight_causal_v1 mechanism. The next boundary entry must expose this cause;
other independent role/obstacle/combat checks can proceed first.703 exact/exit0.

roles_v2 passes actual two-body walking/arrivals, reservation/death and three
frozen-memory searches, but FAILS role-return comparison: the observer compared
settled3s bodies, not the controller's native GuardAnchor captured earlier. One
body reports native Arrived yet is57.351cm from that different reference. Future
comparison records BOTH references and tests the unchanged55cm criterion against
the actual native anchor, also used for patrol home. Walking originals inspected:
both body/leg positions change and arms remain visibly attached; motion blur and
the arrived camera cropping the left body prevent complete gait/contact proof.

The fixture diagnosis suspected incomplete movement-policy isolation; explicit
PC_EnablePolicy/PC_EnableSquad gates were added on nonparticipants. Current author
source ALSO sets PolicyEnabled and SquadEnabled in PC_EnableCombat. Therefore
the earlier claim that CombatEnabled=false itself cannot disable movement is NOT
established and must not be used as a proven cause. A one-shot PC_PolicyHold alone
does not disable future policy visits. New fixtures explicitly disable policy
once on nonparticipants, and squad
once on a parked Allied body. Explicitly re-enable German policy for the role
test, full policies for combat, and the second original squad body after its
declared lifecycle reset. No protected defaults/package/BB/pose mutation follows.

radius_v1 stops after its first sample: CouldSeePawn is not a Python-exported
method. The old diagnostic wrapped this API as optional, not evidence of export.
Do not unlock reflection; record actual eye turn/range/FOV dot geometry plus the
supported controller LOS and Visibility hit instead. No radius cutoff was tested;
703 exact/owned exit0. Retain this API failure separately from gameplay findings.

travel_v10 is the first CLEAN full boundary entry: strict log errors0/exit0,
six checks/703 exact. Both original Allies switch visible targets retaining the
current episode/travel, cut off904.178/872.118cm, physically regroup within
25.842/41.848cm, and43 actual0.25s chase samples stay below1000cm. This supports
the changed finite policy isolation, not proof of every earlier failure's sole
cause or concurrent western-route navigation. No native asset was changed.
Installed PawnSensingComponent.cpp uses sensor Actor rotation for FOV and eye
location to target body; record that dot separately from eye-to-eye view geometry.

roles_v3 still fails with57.161cm to the ACTUAL native guard anchor. The earlier
reference mismatch was not a sufficient cause. Native Arrived is not real body
arrival under the55cm gate; retain this functional defect and inspect actual path
endpoint/projection/collision before any AI or spawn correction. Other role tests
must be recorded independently instead of being silently skipped behind it.

blocked_v1 records BOTH originals stopping after two replans in15.699s with
released reservations. Recovery FAILS before its arrival check: the declared new
player location overlaps a hidden nonparticipant German and physically pushes it
67.975cm, violating continuity. Combat/policy gates do not remove collision.
All noncombat fixtures now park nonparticipants at distinct far positions ONCE
before movement; role participants are explicitly restored to native anchors
when their actual sensing/search test starts. This removes fixture overlap, not
a collision/LOS bypass, teleporting movement controller or native asset repair.
Both failed entries preserve703 exact/owned exit0/strict log errors0.

roles_v4 is CLEAN seven-check pass without native/map/spawn changes: real guard
errors43.848/49.156cm, physical home->destination->home, unreachable two replans
then stable wait, three searches fixed deadline23.631/end23.773s/visited2 each.
Nonparticipants are parked before the Allied movement stage, then role actors
are restored to their actual anchors; independent stage reporting and read-only
diagnostics are active. No out-of-gate Arrived sample occurs, so no path/collision
diagnostic fires. This does NOT establish a sole cause for V2/V3's57cm failures
or prove a native path defect repaired. Retain intermittent arrival/congestion
reliability debt; no identical retries, numerical tolerance increase, unmeasured
spawn correction or speculative native patch is warranted by this single pass.

The MissionConnectivityV1 owned query briefly occupied native slot after blocked_v1
ended. Our combat launch aborts before preflight/UE start; its foreign PID is never
terminated. After that query exits naturally, fresh703 protection revalidation
admits the serial combat entry. This is ownership enforcement, not a game failure.

blocked_v2 FAILS before blocked resolution: a dormant German placed at the guessed
far site(-12682.823,-2270) drops from193.463cm to146.704cm while XY stays fixed and
total velocity reaches302.734cm/s. This is consistent with falling at an unverified
parking floor, not established horizontal walk-speed failure. Preserve its strict
failed gate,703 exact/exit0. The next fixture parks at three distinct original
roster anchor sites with observed settled bodies, beyond the tested moving lane
but within existing floor evidence. Hidden collision remains enabled; player/target
parking also uses existing safe sites. No added floor, actor destruction, gravity
disable, velocity/continuity tolerance change, native map or AI change. The earlier
clean entries retain their actual far-site inputs; do not retrofit their receipts.

blocked_v3 is CLEAN: two replans per original Ally, released reservations and
stationary failed wait in15.686s; blocker removal plus one NEW player assignment
produces both distinct reserved BODY arrivals in4.529s. Floor-safe declared
parking removes the new fixture uncertainty, but does not repair or waive any
earlier failed entry.703 exact/strict log errors0/owned exit0. All six explicit
clean final identities are cross-audited separately; full visual/FPS/city and
intermittent body-arrival reliability are not promoted by this functional closure.
