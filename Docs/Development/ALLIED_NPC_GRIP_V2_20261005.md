# Allied NPC trigger contact — bounded fitting plan

5 October 2026. The user supplies marked Allied/German native side views and
requests Allied completion first. German fitting is deferred until Allied human
acceptance. This authorizes a new pair-specific fitting investigation, not a
copy of player settings or a restart of the rejected finger solvers.

## Inputs, protection and storage

Target the actual `PC_City_Ally1` pair recorded in
`NPC_GRIP_BASELINE_V1_RESULT_20261005.md`: the adapted simple US paratrooper,
original US skeleton, Allied Stride AnimBP, original M1 and V3 attachment.
The supplied arrow asks for the right index to meet the actual trigger region.
It does not establish penetration depth, a final rotation angle or the cause.

Preserve source mesh/rest rig/weights/UV/materials/actions, all right-hand locals,
camera, accepted first-person V20, German packages, B controllers/BT/BB, shared
combat transactions, formal map and Catalog. New generic tools/docs live in Git;
private diagnostic data/images live only in the existing SFTP workspace under
`Evidence/AlliedNPCGripV2`. No publish/delete/commit/push in this stage.

## Cases read and different mechanism

Read Failures/README, AN002, FP001, the failed trigger translation, the later
reflection-corrected trigger/support result, baseline capture plan/result,
parallel workflow and the complete weapon-hand guide including left support.

The old attachment derives a hollow from finger-bone averages and a heading from
both hands, without actual trigger geometry. First reconstruct THIS native pose
from recorded public bone transforms and the preserved full-body FBX. No stopped
live skin query. Verify rest-basis/unit parity before using surfaces. Identify
actual M1 blade/guard/stock and the actual right index/palm; do not reuse invalid
V1 normal labels or player contact points.

Then evaluate one contact-derived rigid gun transform with fixed firing hand,
translation AND rotation. Fit stock seating and trigger together rather than
minimizing only one point. If an acceptable gun fit exists, follow its support
frame with the whole original-length left arm. A numerical wrist match is not
skin contact. No isolated hand-mesh shifts, arm stretching, new motion, finger
solver or source-weight edit.

## Early falsifiable check and stopping conditions

Before fitting, match the full-body reference bones to recorded native rest data
within 0.01 cm, verify the actual native pose/weapon identity and inspect side,
top/reverse and full-arm context. Stop on source mismatch or coordinate ambiguity.

One derived candidate must improve pad-to-blade contact without new visible
stock/guard penetration or losing palm seating. Use 0.3 cm pad/blade distance as
a diagnostic screen, not a penetration-depth guarantee; report exact surface
crossings separately. Support fitting requires original arm lengths (0.01 cm
numeric gate), no new severe skin edges, no detached cuff and actual palm contact.
Reject a candidate on other-contact regression; no angle/offset sweep or relaxed
threshold. If the mature straight-index pose itself is incompatible, document
that evidence and request narrowly scoped existing-pose reuse before changing
NPC finger locals. Player's prior joint exceptions do not cover NPCs.

## Native and human gates

Only after offline evidence, reserve the serialized native slot, verify actual
process absence and the current combined size/SHA rows. New local unsaved
staging may compare the original Allied pair and candidate at matched phases,
using existing rendering and native update mechanisms. Keep German untouched.
First inspect textured static grip, then existing movement/fire/reload/return
and lifecycle/near-wall cases actually exercised. Python may prepare/observe,
never become the production per-frame driver. Stop on ownership/guard conflict;
do not close another user's editor or overwrite the formal map.

Give the user native before/after views before selection. Static/offline contact
does not close movement, combat, deformation or historical-variant acceptance.
Only after Allied acceptance and dependency checks should a separate formal
binding/release stage be proposed, followed by an independent German plan.

## Current guard reconciliation

The first read-only preflight against the immutable 555-row FP epoch correctly
reports two aliases of the shared Combatant as changed. Lane B's later verified
record and explicit `AUTHORIZED_SHARED_MUTATIONS_20261005.json` identify the
user-authorized friendly-fire change, backed up and regression-tested. Adopt the
611-row combined B inventory plus that exact mutation ledger for this new stage;
do not edit the immutable snapshot, ignore unspecified mismatches or roll back
the authorized shared file. B's latest result releases the native slot. Recheck
actual processes and combined guards before any later launch.

## User-directed translation-only review

The later 5 October instruction supersedes the fitting/rotation stage for this
review: do ONE translation that puts the actual blade at the unchanged right
index pad, then return textured three views. No rotation, support-arm IK,
finger/source-pose changes or further optimization. The preceding stock-pivot
candidate remains stopped (6.98 degrees; gap 4.98 to 3.90 cm; new stock crossings).

Reuse only its verified reconstruction landmarks, not its fitted transform.
Map the actual pad into the firing-hand frame and the actual blade into the gun
frame. In native Ready, verify unchanged index-local pose, freeze the world and
set gun position once by `pad_world - blade_world`. Rotation/scale/all character
bones must remain unchanged; target landmark residual below 0.01 cm and gun
stability below 0.01 cm are the early capture gates. Reject changed source locals,
wrong binding, guard conflict or unreadable/stale imagery. No offset samples.

Other contacts may become worse in this intentionally partial comparison; show
and record that honestly rather than automatically repairing them. Matching the
two landmarks does not prove whole-surface clearance, grasp, aim or gameplay.
Keep this unsaved, unselected and await the user's next marking after the views.

The first native translation entry stops before any movement/image because its
harness incorrectly assumes NoCollision. The actual captured V3 baseline has
a different collision mode. Preserve that failure/normal exit0/611 exact guards;
one verification-only correction checks equality with the recorded actual mode
instead. This is not a collision repair or permission to change it. Resume in a
fresh identity with the same ONE translation and all other checks unchanged.

That corrected entry reaches the actual native pose, then stops before movement
because the Python Transform constructor expects a Rotator, not the supplied
Quat. Preserve its native before-pose snapshot, normal shutdown and guards.
Replace only the coordinate-arithmetic interface with pure xyz/xyzw arithmetic;
test inverse roundtrips and index-local parity against the recorded real native
snapshot before another capture. No guessed new engine method or fit parameter.
