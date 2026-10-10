# Paris black/white planning grid — measured result

**Retired for current planning, 10 October 2026:** the user discards this 1 m
edition because coarse sampling can misidentify space. Use only the
[25 cm planning maps](FINE_GRID_RESULT_20261007.md). No 1 m figure is admitted to
the current Git document-image set. The dated measurements and private failure
evidence below remain historical, not authority to select new gameplay sites.

7 October 2026. The finite geometric survey, binary planning masks and offline coordinate tool are produced. Formal-role mapping records7 passed legs,1 negative and10 unmeasured; it is not a successful18-leg acceptance. Browser UI review is blocked by its file-protocol security policy. Script/data checks pass; interactive manual review remains open. No final spawn, objective, encounter site or playable boundary is selected.

Read the implementation, roundtrip and runtime-quarantine plans and ML001/ML003/ML006–ML014 before extending this work. Selected output is private `Evidence/MapGridV1/full_v1_20261007/derived_v3` and `artifact_v3`. Earlier derived/artifact versions are historical. All original models, skeletons, finger poses, weapons, actions, native grip/recoil/AI logic, map navigation and Catalog remain protected. All703 protected rows and both previous survey helper binaries are exact. No formal map save or Git publication.

## What the grid means

The aligned frame is1008×1008 one-meter cells, covering generated navigation within X/Y−50400..50400cm. Original one-bit PNGs use one pixel per meter in both axes. UI zoom changes display size only. +X is right; +Y is up. With zero-based column c and row r:

`X=-50400+(c+0.5)*100`, `Y=50400-(r+0.5)*100` centimeters.

Z is the measured standing feet height of the selected native city support; it is never inferred from a flat image. Five overlapping surface orders preserve separate heights/identities at the same XY. They are not named floors; matching surface order at two locations does not imply the same floor. The exported capsule center uses the maximum reference half-height96.23316cm; actual placement must use the chosen actor's own half-height (German95.26415cm). Original feet XYZ and native sample scope/IDs/polygon references remain primary.

Black includes collision, nonwalkable/unsupported surface, height mismatch, proxy/non-city support, absent saved navigation, insufficient purpose space/sight, another selected group/layer, coarse unmeasured narrow areas and runtime quarantine. Black means blocked or not admitted under the active filter, not universal physical impossibility. White certifies the sampled cell center and measured graph/filter conditions, not every point in its square or every possible path-arrival offset.

Saved and expanded navigation are independent collections. Expanded navigation was rebuilt only in the disposable survey world. Current white points resolve directly to original saved samples/links. Cross-scope sight association is restricted to identical XY/support and feet≤0.01cm apart, retaining both original Recast heights. There are46,013 saved and83,855 expanded city nodes;45,650 physical-point associations. Two normalized nodes at one failed XY are quarantined. Road-connected groups number632 saved/721 expanded; many coarse groups are small. Non-road components remain black. Group counts are conservative graph evidence, not proof that all streets are physically disconnected.

## Native and planning evidence

| Native batch | Recorded | Admitted by its native predicate |
|---|---:|---:|
| Saved polygon/grid-center samples | 156,083 | 154,671 geometry-clear |
| Saved directed cardinal links | 157,242 | 135,495 |
| Expanded polygon/grid-center samples | 1,025,709 | 1,017,643 geometry-clear |
| Expanded city directed links | 268,040 | 236,215 |
| Declared140cm two-way sight pairs | 62,567 | 58,439 |

Native geometry-clear includes outer non-city supports; these do not become city planning white cells. Aliased polygon samples are retained, then normalized by actual support. Link admission requires both native surface reach and straight capsule clearance; reciprocal pairs define groups. No diagonal corner shortcut. Native full entry owned36052 closes exit0/strict log0, static vehicles drift0, protected rows exact. The independent raw audit checks every row and finds no false predicate admissions; it does not establish actual walking everywhere.

Lowest city surface, all road-connected groups, saved navigation, after quarantine:

| Purpose | White cells | Additional geometric condition |
|---|---:|---|
| Walk candidate | 38,545 | City support/capsule and reciprocal road connection |
| Spawn candidate | 37,586 | At least3 separate1m-spaced stations within2m, local reciprocal paths, feet difference≤20cm |
| Task candidate | 17,609 | Center and four1m cardinal stations, each native reciprocal link, feet difference≤20cm |
| Encounter candidate | 35,265 | Local stations, two exits, same-group peer stations and native two-way visibility5–20m |

These counts span different groups. The tool defaults to the largest road-connected saved group; choose the same group when planning mutual reachability. No group is selected as the final mission region. Encounter filters are declared-height geometric sight evidence, not formal AI detection, clear gunfire, damage or balancing.

Independent planning audit checks129,868 normalized node identities/coordinates, actual-point associations, reciprocal components after exclusion,40 pure binary images and275,238 white admissions across purpose/surface/scope filters. Coordinate roundtrip error0cm. Nine meaningful unit checks pass, including wall-separated assembly, one-way/scope-specific navigation, stacked identity and runtime-negative exclusion. Offline source syntax/data contract checks56 filter combinations, both scopes' white coordinates/native IDs and black-negative reasons. HTML has no external data requests. This check is not browser rendering or a successful click/download test.

## Actual formal-role result and failure

The first7m road route passes outward/return with original player, Allied1 and German1:6 legs. Player outward on the second connection also passes. Max successful endpoint XY29.868948cm/feet6.494317cm under the original35cm limits. The next player return-source standing check detects original road capsule overlap at requested feet[14750,-13650,94.59449408012526]cm, despite valid walking floor and within-tolerance position. It stops before a return request. Remaining Allied/German/local/height cases are unmeasured; the selected height route is not runtime-admitted.

ML014 preserves this failure and quarantines column651,row640 in both scopes/all surfaces. Actual arrival differs from the exact clear grid center; no retry, reposition, collision removal or tolerance change. Groups and local filters are rebuilt without the cell. All7 native walking captures exist; the contact sheet and two originals were inspected as scene/position context. Darkness and individual static frames do not certify complete motion/contact. Owned22308 closes exit0/strict log0, resources/profiles/possession/703 protections exact.

ML012 retains compile, transient-inventory and unbound Editor movement-owner failures; different documented native corrections pass early_v3. ML013 retains the erroneous43-cell cross-scope mask and matching source snapshot in a private failure directory. Pre-runtime artifact_v2 is historical. Public failure manifests record exact private paths/hashes; private commercial-derived raster/data/HTML/screenshots remain ignored. Native logs and immutable receipts are preserved.

## Use and remaining admission

Open private `artifact_v3/PARIS_GRID_TOOL_20261007.html` locally. Select saved versus expanded scope, one connected group, surface order and purpose. Pan/zoom; inspect a white cell's actual feet XYZ and a black cell's reason. Add named draft points and export JSON; this never writes the Unreal map. Local draft storage is optional and export remains the portable record. The20,730,376byte offline file decompresses locally and needs no background server. Tablet layout and touch controls are authored but not device-tested.

Browser automation cannot visit `file:` URLs; the IAB attempt times out and Edge explicitly rejects the protocol. A prior loopback server launch was also rejected by automatic tool policy with no detailed reason. Neither was bypassed. The static image was visually inspected, source/data checks pass, but UI interaction, actual download and tablet performance remain manual review gaps.

Before adopting draft sites: inspect the same physical layer/group and test original-role standing and arrival offsets, then squad occupancy/traffic and actual opponent detection/fire at the selected sites. ML014 requires a new bounded arrival/collision plan before any failed-site retest. Expanded candidates require an explicit saved-navigation decision before gameplay adoption. Sub-meter passages/unsupported upper areas need separate measurement; do not relabel unknown black as proven obstacle. Whole-map role walking, final placements, mission loop, FPS/package/course acceptance remain open.
