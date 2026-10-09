# G1 witnessed navigation/collision correction

8 October 2026. [Chinese review](MVP_G1_NAV_COLLISION_CORRECTION_20261008_ZH.md).
This is a bounded private trial within the authorized MVP closeout, not formal
map adoption. Cases read: Failures/README, MI004, NI003 and ML022; the closeout
plan and original diagnose_v1/geometry_v1 receipts take precedence over guesses.

Evidence: original player repeatedly stops at feet(5192.972650,-20735.731259,
128.136620)cm. Its original capsule sweep hits StaticMeshActor_1600 at0.101cm.
This is SM_Debris_06b, BlockAll, four simple convex shapes, navigation-relevant.
Player/NavMesh radius34; height192.466/193; step45/35cm. Therefore a missing
navigation flag or mismatched agent dimensions is NOT established. A complete
native path demonstrably crosses a physically unusable part of its polygon.

Change ONE input to native pathfinding: mark only the polygon at the witnessed
blocked feet as UNavArea_Null in the isolated packaged world, before requesting
any movement. Preserve the city mesh/collision, capsule/speed, exact goals,
all character/grip/action/weapon/AI code and source map. This is conservative
exclusion of one physically failed navigation region, using UE's own navigation;
no offset search, custom A*, teleport, invulnerability or repeated repathing.
Record original area, projected point, exact polygon vertices and excluded ref.

Early acceptance: exact protected epoch; exact blocker still present at witness
under an original capsule sweep; projected point within50cm; only one existing
non-null polygon changes, followed by a complete native path to the SAME far-bank
goal. If it disconnects the route or another physical stall occurs, stop and
retain the negative; do not exclude more polygons or retry different witnesses.
Use navrepair_v1/instrument_v5, <=180s per round/700s total/6s Ready stillness.
Three fresh worlds must revalidate the witness/exclusion independently. Preserve
the original six-person mission input, save/load/restart and full resource checks.
This trial does not by itself prove natural two-sided combat, FPS, complete human
play or a persistently repaired shipping map. Require separate evidence/adoption
before a playable handoff can include it. Source baseline remains untouched.

Stopping condition: any early failure, missing/null/wrong polygon, strict error,
source/asset drift, real mission loss/error, or time/stall bound. No geometry,
grip, action, gun, health, ammunition or AI compensation follows from a failure.

Subsequent acceptance gap: navrepair_v1 reaches Won, saves, restores and restarts,
but first-round living Allies are still on the bridge at Won (bridge transit
complete=false). Do not count player-only arrival as squad passage. After this
finite run ends, cohort_v1/instrument_v6 retains the SAME exclusion/goals/input
but waits at the far-bank endpoint, requiring BOTH living Allies east ofX5600,
each within the original55cm of its native HeldGoal, SquadFailed=false, within
the original25s regroup window. Only then does the scripted player proceed to
G1. Native AI/formation/goals are never written by the fixture. Record held goal,
velocity and squad status. Stop on the first original cohort bound failure; no
more polygons, timing expansion or AI/formation compensation. This closes an
unmeasured acceptance condition; navrepair_v1 retains its narrower result.

cohort_v1 FAILS the original25s gate. MI005 is read and governs the next step.
The single-polygon route is stopped as a proposed complete repair; do not adopt
or add exclusions. squad_diagnose_v1/instrument_v7 is cause-only observation
under MI005's exact early gate/4s stationary or original bound, with no new
gameplay/nav correction. The original baseline remains selected.
