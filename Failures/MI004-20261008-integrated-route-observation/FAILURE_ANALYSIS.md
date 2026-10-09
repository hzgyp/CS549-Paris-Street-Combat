# MI004 - Integrated route stops before the far bank

8 October 2026. [Chinese review](FAILURE_ANALYSIS_ZH.md).

integrated_v2 / instrument_v2 starts correctly, saves Ready serial1, queries a
complete4720.503cm native path, and runs original fire/reload. All three Germans
die from actual player shots; player HP100,16shots,2loaded/0reserve, both Allies
alive/no shots. Player then remains at(5192.965315,-20735.728885,224.358333)cm,
Crossing, until the declared180s round bound. Owned process exits normally0.
This FAILS full-loop acceptance; there is no Won/load/restart or human pass.

The previous travel_v4 PIE route passes4720cm-class travel without player fire
and with enemies isolated. Its path vertices through(5225.223529,-20748,
135.176471) match this new route exactly. The end point differs17.678cm; do not
blame that difference, cook geometry, reload, path following or collision without
new observation. This entry did not record movement status/next target/blocker,
so the stall's cause is presently unknown. Do not teleport, move goals, lower
capsules, edit geometry, disable collisions or declare the white point black yet.

Independent measurement defect: STARTFILE only sets the CSV filename in installed
CsvProfiler.cpp; it does not start capture. START/STOP arguments are case
sensitive; this observer also used lowercase stop. No CSV was captured, therefore
no FPS/performance result can be inferred from this run.

Private raw evidence/source/native wrapper is retained in MVPCloseoutV1/failures
under integrated_v2 and instrument_v2. Selected baseline assets/source unchanged.

Different bounded diagnostic: diagnose_v1 preserves the same saved six-person
world, native route, visible-target scripted input and original actions. It adds
read-only per-second velocity/movement mode/speed/capsule/path status/next target
and actual capsule sweep impact component, and stops after6s still in Ready away
from the goal, or the original180s/loss/error bound. This is cause observation,
not a whole-MVP proof retry or parameter search. Use FCsvProfiler native API
BeginCapture/EndCapture and verify IsCapturing; any diagnostic CSV remains
diagnostic, not three matched acceptance runs. Stop on drift/errors; only a new
cause-supported correction may precede another integrated attempt.

Later diagnosis (18:34 EDT): diagnose_v1 / instrument_v3 stops normally0 after
the declared6s Ready stillness. Repeated original capsule sweeps hit the exact
StaticMeshActor_1600.StaticMeshComponent0 in LV_NewsetDressing at0.100791cm.
Player Ready, walking, no root motion, speed cap300; native path7->8 remains
Moving before becoming Idle. This establishes a physical blocker, not reload
interruption or an unreachable-query failure. Why this collision is absent from
the usable route remains unmeasured; next is Ready-only component/nav metadata,
not another movement retry or blind navigation/geometry edit. Native CSV exists
(1,602,099bytes); it is a short failed diagnostic route, no PERF-01 pass.
