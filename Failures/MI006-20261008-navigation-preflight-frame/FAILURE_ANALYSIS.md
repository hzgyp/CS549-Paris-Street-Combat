# MI006 - Native candidate fails under the declared RT-off profile

8 October 2026. [Chinese review](FAILURE_ANALYSIS_ZH.md).
candidate_cohort_v1/instrument_v9 passes three original squad gates, captures,
Won saves/fresh loads and two restarts at RT-on. Preserve that bounded result.
candidate_rt_off_v1 changes ONLY startup -noraytracing on the same binary, High
1080p/100%/pool1536, same route/AI/gates. Hardware RT disabled is confirmed by
native log/metadata. It fails the FIRST25s regroup gate,79.556s/normalexit0.
The performance experiment stops; no complete RT-off performance pass is known.

Ally1 stalls at(2533.660320,-20872.277300,253.260785) body cm. HeldGoal
(5833.884,-20739.338,205.727), error3303.242cm,Idle/Ready/SquadFailed=true,
WaitingReason=PathExhausted/RetryCount2/ReservationID0. DesiredPosition remains
(4011.161,-20750.837,206.233). Request14 atworld40.703 returnsAborted3/328 as
the original goal changes to(4165.093,-20817.540,206.233). There are no subsequent
Ally1 native MoveTo requests; later policy goals change while DesiredPosition is
stale. Ally2 error32.782cm but bodyX5576.600 fails original far-sideX5600 gate.
Do not widen that gate, clear exhaustion or force another move to hide failure.

Original BP plan preflight uses GetActorLocation (capsule CENTRE), with the pawn
only as pathfinding context. Installed UE NavigationSystem.cpp:2215 passes the
supplied PathStart/PathEnd unchanged into FPathFindingQuery; context selects agent
properties/data, it does NOT substitute feet. Native AIController path building
starts at GetNavAgentLocation. This is a concrete coordinate-contract discrepancy,
not yet proof that it caused this particular rejection. Capsule half-height is
96.233cm. Do not assert an AI race or geometry obstruction without query evidence.

Different cause-only queries_v1/instrument_v10: Ready only, NO mission/movement,
fixed recorded failing start and three recorded original goals. Compare exactly
centre vs native agent/feet start and body-goal vs projected-feet goal (12 fixed
queries), using original NPC agent and UE navigation. Record actual default query
extent, projection, valid/partial/path ends. This is semantic coordinate diagnosis,
not an offset search. Native candidate constraint and all assets/AI stay exact.
Stop after observations plus2s or first early/source/strict error. No retry proof,
extra exclusion, goal/tolerance/capsule/speed/retry-budget/formation change.
Any subsequent correction requires its own bounded plan and these actual results.

Pre-entry instrument_v10 fails compilation C4800: two diagnostic JSON bool fields
receive int loop indices. Runtime queries0. Preserve the build/log/source; distinct
instrument_v11 uses explicit !=0 only, same12-query semantics and native candidate
bytes. No warning-policy relaxation, gameplay change or failed-identity rebuild.

queries_v1/instrument_v11 actually passes the finite diagnostic: all six centre queries invalid, all six feet-start queries complete, including unchanged goals; extent(100,100,120)cm. This establishes the witnessed preflight coordinate failure, not a broad nav-geometry diagnosis. Separate agent-coordinate plan governs the correction. instrument_v12 fails before runtime with C3535/C2440 because auto* cannot deduce TObjectPtr services/decorators. Preserve its source/log/receipts, including its stale overly broad AI-unchanged scope; no runtime test occurred. Distinct instrument_v13 changes those two range declarations to const auto&, retaining identical candidate logic. New build metadata states the G1 plan change explicitly; V12 raw metadata is not rewritten.
