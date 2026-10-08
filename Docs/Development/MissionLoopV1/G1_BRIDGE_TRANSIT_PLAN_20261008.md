# G1 bridge transit correction — 8 October 2026

English source; synchronized Chinese: `G1_BRIDGE_TRANSIT_PLAN_20261008_ZH.md`.
Read MI001, ML010, NI003 and the G1 implementation before this correction.
TravelV2's player physically completes both legs; Allies arrive at the near-bank
slots33.54/39.37cm, then stop in the bridge's first half,2437.88/3022.50cm from
their far-bank HeldGoals with SquadFailed=true. Those goals are at
5396,-20463,306.23 and5491,-20121,266.23cm. This is a real group failure,
not a missing bridge or a failed query. Keep the failed receipt/route/captures.

Changed mechanism: add a mission-only narrow-bridge policy, rather than offset
or timeout retries in the original formation. Query the saved UE nav for the
same S→near-bank→far-bank corridor once; retain its shared centreline. While
crossing, two living Allies request original reserved policy goals450/700cm
behind the player's measured centreline progress. Their spacing is250cm,
exceeding the original150cm reservation requirement. Use original
PC_SquadRequestGoal, native MoveTo, collision/RVO and300cm/s; never position
an actor per frame or teleport. Grounded nav goals are supplied at feet height.
No custom A*, fabricated route completion or threshold relaxation.

Only the owned BP_PCG1ControllerV1 overrides PC_UpdateSquad through a native
mission hook. Outside bridge transit it calls its original parent. Busy actions
or current combat hold use the original hold endpoint; original sight, target,
fire/reload/damage and defender logic remain. Keep the narrow policy at T1;
release it after the player moves east beyond6500cm and all living Allies have
actually reached the far-side file goals. Dead Allies retain original release
handling and never respawn. Fresh load rebuilds the same saved-map centreline;
no previous-world pointer, action or trail is resumed.

Ownership: only new plugin source/DLL and owned controller change. Back up the
controller and authenticate a new owned-file admission receipt; retain the
heading receipt as history. Original map, all703 rows, placements, navigation,
models, fingers, rig, materials, accepted presentation and weapon rules remain
exact. Native source compile-only is isolated; installation/writer waits for an
empty engine slot. No commit/push.

Early acceptance: fresh native path is complete and matches both frozen bank
endpoints; Ready remains ten seconds with zero actions/resources/moves and five
selected bindings. Then both living Allies must physically reach their reserved
goals within55cm and25seconds after the leader's arrival; both must be east of
X5600 at the far-bank end. Repeat the same player route under the changed
mission policy, not the stopped original formation. Independent encounter still
uses the frozen T1 group and original combat.

Stop at the first bad query, premature action, guard drift, failed physical
arrival, created resources or native error. Preserve the bounded result; no
second spacing, side, position, speed or time sweep under this plan. The
lateral-projection explanation remains a hypothesis until this different policy
is measured, and a pass will not isolate every cause of the old failure.
