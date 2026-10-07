# German NPC V10 — bounded existing-grasp thumb-tip curl result

6 October 2026. User accepts V9's gun/hand positioning and minor residual
overlap visually, then requests bending the marked right-thumb tip toward the
rifle surface. **Local curl delivered for review; no native/formal adoption.**
Read [plan/addendum](GERMAN_NPC_THUMB_CURL_V10_20261006.md), HANDOFF/618 epoch,
Failures, V9/V6 results, calibration guide and character workflow/references;
GP010/AN002/AN008 previously reviewed. Original root-lift/digit solvers remain
stopped. Early checks protect the accepted V9 assembly and distal skin.

## Existing-action reuse and retained failure

Use the verified compatible existing D059 AimReload derivative/cache at2.2s,
not a newly authored animation. Exact reuse of thumb02/03 local rotations
(5.916750/25.178485deg difference) reduces mean pad gap1.203669 ->0.726223cm,
but creates23 new distal stock-crossing faces/whole-thumb57 ->82. It fails the
declared distal-clearance gate, is preserved unselected in `distal_reuse_v1`,
and is NOT excused by accepted small proximal overlap. Four matched right/
full-arm failure views were opened; tip visibly enters the stock. No new severe
edges or self pairs in that comparison. Normal process exit0 is not a fit pass.

The different bounded surface-limited mechanism retains root01 AND02. Reuse
only source thumb03's shortest bend axis, limit its amplitude at the first
actual pad/wood-plane clearance0.08cm. Analytic fixed-joint LBS surface roots,
not an angle sweep, binary fit loop, new action track or root compensation.
Limiter actual distal vertex9524/wood triangle14879; original signed height
0.571181cm. Actual bend18.516955deg,73.5428% of the mature25.178485deg bend.
Actual triangle clearance is checked after the plane prediction.

## Final local checks

| Diagnostic | Accepted V9 baseline | Surface-limited curl |
| --- | ---: | ---: |
| Mean sampled distal-pad / upper-stock gap | 1.203669cm | 0.781363cm |
| Minimum sampled pad-face-center gap | 0.404509cm | 0.138166cm |
| Distal stock-crossing faces | 0 | 0 |
| Whole-thumb stock-crossing faces | 57 | 57 |
| New thumb/other-digit self pairs | — | 0 |
| New severe skin edges | — | 0 |

Mean and minimum gaps are sampled face-center measurements, not complete
surface enclosure. Pad is visibly more bent/closer, not a claim of complete
zero-gap grasp. Existing accepted proximal overlap remains. No further root,
gun-angle, offset or other-digit compensation is performed.

Only serialized `thumb_03_r.q` differs; its t/s and all other68 bone worlds,
including thumb01/02, right wrist/arms/index, whole left grasp/arm, and gun are
exact. Raw rotation column-scale floating residual1.50e-8; encoded scales are
identical, not a scale edit. True-zero-changed-influence and actual distal-index
skin0cm. No other-digit shared influences in this03-only change.24 vertices
share changed03 with unchanged thumb/hand bones and move up to0.299308cm;
do not claim every palm/thumb boundary vertex fixed. Maximum added skin edge
0.352541cm, no >3x AND >2cm-extra severe edges. Source rig/rest/weights/lengths/
mesh/UV/materials/action tracks untouched.

Fresh separate-process reconstruction skin error0.000000182cm/gun0; protected
bone worlds and true-zero-influence/distal index0. Existing0.01cm display budget
is separate from raw protection/contact gates. All ten original matched reverse,
right, top, support and complete-arm views plus two sheets opened. The tip bends
toward the upper stock, original root overlap remains, left grasp and overall
arm pose unchanged. No new visible gross arm/wrist separation; retained source
skin projections remain. Gray diagnostics do not verify UE materials or motion.

## Evidence / closure

Private root: `Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/
Evidence/GermanNPCThumbCurlV10/`. `distal_reuse_v1` retains the failed complete
reuse; `failure_views_v1` contains its four views. `surface_limit_v2/result.json`
and `diagnostic_geometry.npz` retain the bounded03-only configuration/geometry;
`review_v1` contains fresh reconstruction, ten originals, `three_views.png`,
`context.png` and layout-only `presentation.json`. No image contact retouch.

Final618 current guards and16 retained input rows exact, all16 output image
hashes exact, four tools parse. Four owned Blender processes exit normally0;
no Blender/UE engines at final check/no native slot claimed/A remains RELEASED.
Approved FP/Allied/B/AI/map/Catalog/formal German-unarmed state unchanged.
No usable mesh/native package, asset/map save, selection/release/publication,
deletion, Git commit or push. Static V9 human acceptance is distinct from
this new curl's review and native action acceptance. Stop at this local result;
motion/reload/recoil/lifecycle/FPS/Shipping/second-machine tests remain unrun.
