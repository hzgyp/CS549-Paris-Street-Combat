# German NPC right-thumb V6 — stopped local adaptation

6 October 2026. **No usable correction selected; no native test or formal
replacement.** The thumb pad can be raised above the stock, but both tested
root rotations increase proximal thumb/wood intersections. Retain the useful
V4 gun/hand baseline and the failed evidence; do not consume either failed fit.

## Authority, cases read and changed mechanism

The user stopped the gun-seating route and identified the initial right thumb
pose as incompatible with the grip. The subsequent “start” request authorizes
bounded right-thumb pose adaptation, not moving the gun again. Read the V6
implementation plan, HANDOFF/current 618-row epoch, Failures index, GP010,
AN002, AN008, V4 ordered-grip result, V5 paused measurement record, weapon-hand
calibration guide/left-thumb supplement and character workflow. The workflow
required actual skin/contact checks and multiview review, not only pad proximity.

V5 produced measurement only before the user's pause: no fitted gun candidate
or native entry existed. V6 preserves V4 `offline_v6` gun transform, left support,
right wrist/arm, index-trigger relationship and non-thumb bone transforms. Only
right-thumb local rotations were eligible to change. Source mesh, rest rig,
bone lengths/scales, weights, actions, materials and protected assets stay exact.

Early acceptance required improving real upper-stock seating without increasing
whole-thumb intersections, severe skin edges or thumb/other-digit self-contact.
This gate failed. The two distinct root hypotheses are stopped: no third root
angle, offset, distal-joint compensation or native entry under this plan.

## Existing animation comparison

Compared ten retained samples: Rifle_Idle at 0/0.4 seconds and the existing
D059 AimReload native derivative at 0/0.4/1.2/2.2/3.4/3.8/3.98/4.1 seconds.
Their reference hand/thumb axes agree with this German rig within 0.000143
degrees. This is verified compatible bone-basis reuse, not copied player offsets
or adoption of a stopped reload owner. These samples contain only two distinct
right-thumb grasps: Idle is the current low thumb, and the reload grasp is lower.
Neither is a usable exact replacement. This does not claim every animation in
the purchased libraries was exhaustively evaluated.

The first comparison exposed a 0.000233 cm cached-skin/reconstructed-matrix
encoding discrepancy. It is retained as an arithmetic limitation, not actual
source deformation or permission to loosen the unchanged-skin gate. Subsequent
root comparisons reconstruct BEFORE and AFTER from identical encoded protected
matrices; truly zero-thumb-influence skin displacement is then exactly zero.

## Two bounded root comparisons

Both preserve mature thumb_02/03 local bends and change only thumb_01 rotation.
The second has a different constraint, not an angle sweep of the failed first.

| Measurement | Baseline | Minimal 3D upper-surface lift | Pure elevation, original transverse heading |
| --- | ---: | ---: | ---: |
| Thumb root rotation | — | 37.8686 degrees | 34.3638 degrees |
| Whole-thumb/stock crossing faces | 76 | 131 | 97 |
| Mean measured distal-pad/upper-stock gap | 5.9088 cm | 0.6537 cm | 1.9753 cm |
| Signed pad height over measured upper stock | -5.3396 cm | +0.1331 cm | +0.1358 cm |
| Other-digit-shared skin maximum displacement | — | 1.5551 cm | 1.3169 cm |
| Truly unaffected skin / actual distal index skin | — | 0 / 0 cm | 0 / 0 cm |
| New severe edges / new thumb-other-digit self pairs | — | 0 / 0 | 0 / 0 |

Intersection face counts measure triangle crossings, not penetration depth or
complete grip quality. They nevertheless fail the unchanged early gate, and
the actual diagnostic views show the same proximal wood penetration. Seventeen
vertices share thumb and other-digit influences: their displacement must not
be described as fixed neighboring skin merely because other joint locals stay
fixed. The two thumb joint spans remain 3.8695/4.0621 cm within encoding precision.

No usable binding/geometry asset was authored or selected from these results.
The failed quaternions remain in private diagnostic receipts only. Both Blender
fit processes exited normally with code 0 while their internal result status
was `failed_preserved`; process exit 0 is not a successful fit.

## Read-only failure presentation

Reconstructed the retained pure-elevation failure without another solve, using
the full original 25,236-vertex/42,753-triangle skin and unchanged 24,466-triangle
gun. Matched BEFORE/AFTER right, reverse, top and full-arm context cameras gave
eight original images; all eight and the composed comparison sheet were opened.
Orange marks the right thumb, blue marks the protected index. Gray diagnostic
materials are not game textures or native shader parity. No source material/UV
was changed and no game-ready mesh was saved.

The first presentation stopped because a factory-reset scene had no World.
That failure is retained. A distinct presentation-only initialization supplies
a World and reproduces the same retained pose/cameras; it is not a contact-gate
override or another fitting attempt. The visible raised distal thumb with its
root occluded by wood confirms why the failed result cannot be adopted.

Private evidence root:
`Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/GermanNPCRightThumbV6/`

- `compare_v1/result.json`: existing-pose provenance and arithmetic limitation.
- `root_lift_v1/result.json`: first failed root lift.
- `vertical_lift_v2/result.json`: second failed root lift and protection checks.
- `failure_views_v1/result.json`: retained presentation initialization failure.
- `failure_views_v2/result.json`: eight diagnostic views, no native acceptance.
- `failure_views_v2/thumb_comparison.png` / `presentation.json`: labeled failure.

## Closure and remaining work

Fresh final verification: all 618 current formal guard rows exact; 28 retained
input references exact; six new tool scripts parse. No Unreal or Blender process
remained at the final process check. No native slot was claimed in V6; lane A
remains RELEASED. Formal German remains unarmed. Approved Allied/first-person/B,
source model/rig/weights/actions/materials, formal map and Catalog are untouched.
No publication, package save, selection, deletion, Git commit or push occurred.

This turn does not establish static grip acceptance, playable rig/motion,
reload/recoil/lifecycle, FPS/Shipping or second-machine acceptance. Any subsequent
attempt needs a different documented proximal/distal thumb relationship based
on the actual stock and skin, preferably human marking of the root direction;
do not repeat these root fits, move the protected gun/index or edit weights to
conceal the failure. User authorization to adapt the thumb is not revoked, but
these two particular hypotheses are stopped rather than silently retried.
