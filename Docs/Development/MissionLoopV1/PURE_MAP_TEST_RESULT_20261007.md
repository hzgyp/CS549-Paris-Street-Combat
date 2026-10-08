# Pure map connectivity test result

2026-10-07 19:16 UTC. The [workflow](PURE_MAP_TEST_WORKFLOW_20261007.md) preceded execution.
**All28,684 finite scheduled cases are recorded and independently audited; this
does not establish whole-map mutual connectivity.** [Chinese review](PURE_MAP_TEST_RESULT_20261007_ZH.md) is synchronized.

| Verified scope | Result |
| --- | --- |
| Isolated environment | 8 loaded levels/23,037 blockers;15 gameplay actors removed only in unsaved memory;runtime original player/NPC/project gameplay actors0. Car obstacle retained with test-only stationarity. |
| Full-domain export | 11,828 active/exported tiles/invalid0;27,836 polygons/15,543 regions/47,176 directed edges/2,231 query SCCs. |
| Finite coverage | 28,684 records:26,497 passed movements/1,119 standing-only passes/1,068 negatives or cached rejections;unmeasured0. Controls excluded from denominator. |
| Height/narrow tags | Height:1,584 recorded/1,322 passed/262 negative. Narrow:2,644 recorded/2,431 passed/213 negative. Tags overlap and are not additive denominators. |
| Physical evidence | Native Character/AIController/Manny unarmed display;per-case request/controller/SUCCESS/actual endpoint/CurrentFloor audit. Passed feet Z-7.87..118.52m. |
| Directed groups | 1,027 SCCs of passed-edge endpoints only;largest sizes:7,592, 2,762, 76, 71, 67, 58, 29, 23. Other surfaces are not proven physically disconnected. |
| Closure | Latest ownedPID51328 exit0/strict log0/703 exact;static car component/bounds/collision exact/simulation disabled/max drift0. |

Ten-metre tiles and reciprocal native adjacency preserve XYZ/exact-poly surface,
raw center and directed connections.1,049 tileXY locations contain stacked
regions; do not round Z or call Recast layers0–5 six floors.2.5D aids reading while
UE retains3D navigation. Existing BasicShapes/outer proxy supports are test geometry,
not automatically a Paris mission area.

![Finite movement and height evidence](../../../Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/PureMapSurveyV1/Visuals/PURE_MAP_FINITE_RESULT_20261007.svg)

## Height conclusion

At least one actual height connector is walked both ways. Case07537 walks from
road feet0.90m to6.99m;07910 returns from7.04m to0.90m. Both nativeSUCCESS/
request match/all sampled states walking. Endpoint XY/feet errors20.963/20.641cm
and0/8.808cm meet unchanged35cm limits. High initialization/standing alone is not
an access route; other roofs/interiors/stair entrances remain evidence-dependent.

The full case trajectory samples include37 MOVE_FALLING observations;
do not describe every record as entirely walking. Passed endpoints separately
require walking/grounded state. The all-sampled-walking claim above is limited
to those two example legs.

![Reciprocal height example](../../../Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/PureMapSurveyV1/Visuals/PURE_MAP_HEIGHT_CONNECTION_V2_20261007.svg)

## Negative interpretation

| Reason | Count |
| --- | --- |
| native_completion_or_endpoint_failed | 335 |
| source_previously_rejected_no_retry | 243 |
| source_not_safe_standing_surface | 433 |
| runtime_query_missing_or_partial | 30 |
| native_request_not_started | 18 |
| native_stall_deadline | 8 |
| previously_rejected_exact_surface_query_no_retry | 1 |

Negatives mean no pass under this specification, not automatically impassable
terrain. AlreadyAtGoal starts no traversal; endpoint/source/query rejections have
different meanings. Cached source rows are not new physical attempts. Evidence
SCCs do not prove complete separation;navigation-external collision, unloaded
content and unidentified interiors remain unknown.

Read and preserve [ML001–ML007](../../../Failures/README.md). ML005's400 polluted
records are excluded;ML006's7311 center-only cases are diagnostics, not merged.
Only authenticated equivalent old negatives survive. V12 admits11633 remote
prefix cases only, quarantines12 suffix records/one initialization. ML007 retains
API/repr-address/parity and diagnostic reentrancy failures;V17 numeric snapshots
and near-car gate precede continuation. V18's stop was later than assumed and
remote11637 was repeated once;retain the fact and audit its same-fixture prefix
before reuse. See [static plan](PURE_MAP_STATIC_VEHICLE_PLAN_20261007.md) and
[chronological notes](PURE_MAP_TEST_RESULT_EXECUTION_NOTES_20261007.md).

## Subsequent layout

All existing positions remain temporary tests;no final spawn/objective/Allied/
German placement is chosen. Propose Paris candidates from evidence groups, then
test original FP/Allied/German profiles, simultaneous squad bottlenecks and mission
returns. A solitary default character pass is not squad acceptance.

Broad execution uses NullRHI fixed20ms application/80ms world steps and600cm/s;
no real-time rendering/FPS/original300cm/s/visible-contact acceptance. Formal9ff
map remains2,720,990bytes;authorized3-display-DLL local increment adopted, other
700 rows/models/fingers/guns/actions/AI/Catalog exact. No formal save/adoption/
commit/publication. Raw receipts/logs/template/PNG/binaries stay private in
Evidence/PureMapSurveyV1;fixed_static_vehicle_v20_20261007/audit_v1.json authenticates the full chain.
