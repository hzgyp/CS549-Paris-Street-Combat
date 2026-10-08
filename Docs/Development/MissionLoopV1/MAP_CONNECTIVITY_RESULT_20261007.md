# Current map connectivity — measured checkpoint

7 October 2026. [Chinese review](MAP_CONNECTIVITY_RESULT_20261007_ZH.md). Governing [bounded plan](MAP_CONNECTIVITY_IMPLEMENTATION_20261007.md). Priority remains connectivity/vertical inspection before placing mission objectives.

## Confirmed current query result

`current_query_v1_20261007` used the saved team map `9ff18c1339ee1de61add8a15acebd56512617ed69547de668b7d59ee1772d65b` without PIE, save, navigation rebuild or actor movement. The owned engine exited0; launcher log review found no Error/Fatal/ensure/navigation registration failures. All703 current guards remained exact. Original models/grips/actions/gunplay/AI packages/configuration/Catalog were unchanged.

| Measurement | Actual result | What it establishes |
| --- | --- | --- |
| Six saved actors | Player, two Allies, three Germans; unique IDs, 100 health, 2/16 ammo | Actual current placement/configuration queried. |
| Directed roster queries | **30/30 complete**, partials rejected | Every saved actor location has a queried route to every other location under its requesting Character context. Actual physical walking is separate. |
| Retained supported agent | Radius34cm, height193cm, slope45° | Current navigation profile; actual capsule half heights96.233cm Allied/player and95.264cm German. |
| Coarse multi-height samples | **1,854** deduplicated XYZ nodes; **449** complete outward and return paths to player | A sampled mutual-query component; not percentage of city area or coverage of every narrow surface. |
| Complete outward/return path-node Z | World **56.628–443.410cm** | Retain height; highest query sample is about3.33m above the player's projected110.226cm. Does not yet prove a traversable staircase or building floor. |
| Nominal bounds / sample extent | XY420×420m; volume world Z−300 to700cm; XY10m/Z1m seeds, projection extent80/80/60cm | Diagnostic window, not selected mission boundary. Returned projected surfaces can extend slightly beyond nominal volume height; observed maximum751.711cm. Do not treat the volume ceiling as an exact surface cutoff. |

## Layered-surface finding

The receipt's raw `same_xy_multiple_height_cells=99` groups by rounded1m XY and25cm Z; it is **not** a floor count. Separate post-analysis uses XY rounded to1cm and a193cm minimum upper/lower gap, identifying **43 stacked sample sites**.38 have neither extreme connected to the player, three have only the upper extreme connected, and two have only the lower extreme connected. **None has both extremes connected** in this coarse survey. This does not rule out unsampled stairs or intermediate surfaces.

At world XY(−4000,6000)cm, lower `sample_0950` is Z114.603cm and not connected to the player; upper `sample_0951` is Z420.783cm and has complete outward/return queries. At XY(5000,−950)cm, the lower110cm surface is connected and the upper510cm surface is not. Flattening these surfaces into one XY cell would lose required connectivity information.

The appropriate export is therefore **XY + surface height/identity + directed connections**. A simple single-layer display can be used for a selected area only after overlapping surfaces are excluded or explicitly separated. Keep Unreal NavMesh as the authority; no custom A* or fixed floor-height bins are introduced.

![Current query coverage, bounded actual height trajectory and retained failed anchor result](../../../Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/PureMapSurveyV1/Visuals/current_visual_v2_20261007.svg)

This figure is a diagnostic point/path view, not a road basemap, collision clearance map or floor plan. The green/gray points and30/30 matrix are C1 queries. The blue curve connects504 recorded original-Allied height-walk position samples, not an invented street. The separate height pass and failed occupied cycle are labeled below; neither changes the query matrix into physical all-pairs acceptance. The original query-only v1 figure/evidence is retained unchanged.

## Geometry and physical entry

`current_traversal_v1_20261007` **FAILS** at physical leg8. Seven original-Allied approaches pass; reverse-side approach toward Enemy2 stops Idle100.936cm from the goal, outside unchanged80+5cm admission, with4.591cm foot-height error. The observer did not record native completion reason, so collision/occupied body/remaining sensing/acceptance semantics are not proven causes. No full roster physical mutual-access pass follows. All703 guards exact, owned engine exit0; launcher rejects the failed receipt. Read [ML001](../../../Failures/ML001-20261007-map-connectivity-fixture/FAILURE_ANALYSIS.md). Full occupied-anchor launcher is locked; no tolerance change or automatic rerun.

The eleven paired simple/complex surface probes reveal distinct kinds of stacked surfaces:

| Site | Geometry observation | Admission consequence |
| --- | --- | --- |
| XY(−4000,6000)cm / highest neighbor | High collision is broken roof `SM_V_Roof_Broken_04b3`; low simple ray starts inside its collision while complex ray reaches the road. Highest simple/complex surface hits453.030/397.987cm differ55.044cm. | Not a verified second storey/stair. Retain collision-versus-visible-mesh discrepancy and require actual movement/contact review. |
| XY(−8000,12000) and(−3000,−7000)cm | Unconnected low Landscape below connected road geometry. | Surface layers need not be usable building floors. |
| XY(5000,−950)cm | Connected building floor below an unconnected Cube collision surface. | Do not place an enemy on the upper sample merely because it projects. |
| XY(7000,0)cm | Connected rubble below an unconnected awning. | An awning surface is not an admitted floor. |

All three original captures were opened: overhead/oblique views expose destroyed structures/debris, while the first side capture is too dark to verify an entrance. No whole stair/entry visibility or full vertical topology pass is claimed.

`height_walk_v1_20261007` **passes its two bounded height legs** under [the height plan](MAP_HEIGHT_PROOF_IMPLEMENTATION_20261007.md). Original Ally starts at saved spawn, reaches the exact C1 highest sample XYZ(−3952,6000,443.410)cm, then returns home. Both legs record native `PathFollowingResult.SUCCESS`; no target, acceptance, collision, model, grip or ammunition adjustment was made. Combat/brains/runtime sensing are stopped only in this unsaved terrain fixture; this is not autonomous combat navigation acceptance and does not retry or repair the failed Enemy2 cycle.

| Actual native leg | Queried length | Game time | Final XY distance / foot-height error |
| --- | --- | --- | --- |
| Original Ally spawn → exact highest sample | 184.066m | 64.133s | 26.991 / 13.883cm |
| Highest sample → original Ally home | 183.650m | 66.007s | 28.844 / 18.030cm |

Both satisfy unchanged30cmXY (+5cm measurement margin) and35cmfoot-height limits. Sampled actual capsule feet span world Z56.905–460.200cm: **height-varying terrain locomotion exists**. The high endpoint is still collision-supported broken-roof geometry, with the retained55.044cm simple/complex hit discrepancy; movement success does not certify visible foot contact, stairs or usable building floors. Final receipt errors0, strict log errors0, protected703 rows exact, owned engine17496 normal exit0; no engine remained at the post-run process check. All six actors retain100HP/2/16/zero shots. No save/rebuild or native asset/config/Catalog change.

The planned original-Allied/original-German anchor cycles and reverses use80cm approach tolerance for occupied actor locations. The highest unoccupied sample uses30cm. This is explicit approach evidence, not standing inside another body. Simultaneous two-Allies mission bottlenecks, player physical input, unsampled higher structures and final objective placement remain open.

## Retained evidence and next gate

All raw evidence stays private/ignored under `Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/MissionConnectivityV1/`:

- `retained_analysis_v1_20261007/analysis.json`: historical391/1157/51/1 counts and source hash. It does not supersede current C1.
- `current_query_v1_20261007/query.json`: current actor positions,30 full directed routes,1,854 XYZ nodes/paths, live navigation receiver and exact guard result.
- `current_visual_v1_20261007/analysis.json`: source hash,43 stacked samples and vector/raster hashes.
- `current_visual_v2_20261007/analysis.json`: preserved-input hashes and final vector/raster with504 recorded height-trajectory samples and separate physical pass/failure labels.
- `current_traversal_v1_20261007/`: separate geometry captures/physical receipt; status must be read from its final receipt and clean log/exit.
- `height_walk_v1_20261007/traversal.json`: two native successful height legs, original resource checks, positions/samples and exact guard result; immutable run source/captures alongside it. Not an occupied-anchor repair. Its inherited generic status label contains “anchor”; the actual scope/planned moves/completions/summary are the two height legs above, not a full-anchor pass.

Source Markdown/SVG and tools are local, uncommitted/unpublished changes. No asset publication or new manifest epoch follows. Select objective/spawn/enemy anchors only after their relevant geometry and physical edges pass; map regions outside those checks remain unverified.

Current decision: use a **2.5D diagnostic view** (XY overview, actual Z/surface identity and directed verified connectors), while retaining native3D navigation. Do not invent floor numbers or convert the city to a flat gameplay graph. Existing six-position queries pass, but the occupied-anchor physical cycle fails and no final objective coordinates have been admitted. The next bounded work is native completion/occupancy diagnosis for ML001, followed by actual forward/return checks of proposed mission anchors and simultaneous squad bottlenecks. All mission anchors must belong to the same mutually reachable component for the relevant original agent profiles and must separately pass physical arrival; projection or a green query line alone is insufficient.
