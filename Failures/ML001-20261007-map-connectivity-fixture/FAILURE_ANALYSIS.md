# ML001 — occupied anchor approach and incomplete vertical inspection

7 October 2026. Governing plan: `Docs/Development/MissionLoopV1/MAP_CONNECTIVITY_IMPLEMENTATION_20261007.md`. Current map9ff/703 guards unchanged. No native candidate/package was authored, so there is no asset to move. Private raw source snapshot, captures, samples and log remain preserved under `Evidence/MissionConnectivityV1/current_traversal_v1_20261007/` and `tmp/mission-connectivity-v1/`.

## Actual failure

The current C1 query passes30/30 directed actor routes. Separate unsaved C3 fixture hides the original roster for bootstrap, checks100HP/2/16ammo/zero shots, disables combat, stops native brains and reveals everyone. Its first7 original-Allied approach legs pass. Leg8, Ally2-side approach to Enemy2, becomes Idle at XY100.936cm from the configured goal, foot-height error4.591cm. The unchanged admission limit is80+5cm. The entry correctly fails and stops; later legs/German cycle/highest-sample movement are NOT run. Owned engine exits0, native guards703 exact; launcher rejects the failed receipt. A partial cycle is not full mutual physical access.

The observer recorded Idle but did not bind the native MoveCompleted result. It cannot distinguish native success/acceptance semantics, Blocked/Aborted, remaining sensing callbacks or occupied-body interference. Earlier opposite approach to the same anchor passed79.557cm. A complete NavMesh query and directional discrepancy do not prove a disconnected map. These are hypotheses, not established causes. Do not expand80cm tolerance, teleport an occupied target, revive/refill a roster or relabel the run passed.

## Geometry observations and limits

The C2 rays identify the high(-3952,6000)cm sample as `SM_V_Roof_Broken_04b3`, with simple collision453.030cm and rendered-mesh complex hit397.987cm. At nearby same-XY(-4000,6000), the low simple trace starts inside that roof collision; a complex trace finds the road below. These are collision/mesh-layer differences, not verified building floors or stairs. Other samples include Landscape below a road, a Cube above a building floor, and an awning above rubble.43 stacked NavMesh sites cannot be called43 floors.

Three originals were opened. The overhead/oblique view shows destroyed structures/debris; the first side image is too dark to certify a connector, and no whole stair/entry can be established from those views. Preserve images unchanged; their existence/hit labels do not clear vertical traversal or all connector visibility.

## Stopped route and different next work

The full occupied-anchor cycle/reverse fixture is stopped. No automatic rerun or target/tolerance adjustment. A later occupancy diagnosis needs its own bounded plan and native completion-result observation before changing the admission contract.

Independent height question may proceed under `MAP_HEIGHT_PROOF_IMPLEMENTATION_20261007.md`: same original Ally starts at its saved position, native walks to the exact highest mutual C1 sample and back to its now-unoccupied own origin,30cmXY/35cmfoot-height limits unchanged. Add native completion-result observation, disable runtime sensing together with the already stopped brains to explicitly isolate terrain locomotion, and do not revisit/repair Enemy2. This is a different two-leg proof, not a successful rerun of C3 or a fix for leg8. No source assets/collision/NavMesh/poses changed; failures immediately stop and remain negative evidence.

Objective coordinates, full roster physical mutual access, simultaneous squad bottlenecks, building-floor access, human input, animation/contact, FPS/package and course gates remain open.

Later verified independent result: `height_walk_v1_20261007` passes only its two height legs, nativeSUCCESS2, original30cmXY/35cmheight limits, errors0/703exact/owned17496exit0. It does not visit the failed occupied Enemy2 anchor. The ML001 full-cycle failure and missing original completion reason remain unchanged; do not reinterpret the independent height pass or its inherited generic status label as an occupied-anchor repair.
