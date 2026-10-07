# German NPC V7 — marked trigger-pivot stock lowering result

6 October 2026. **Requested directional comparison produced; full grip/contact
NOT accepted, no formal/native selection.** Retain the raised V6 thumb, turn
the gun rear-stock end down 8 degrees about the actual trigger and follow with
the complete original-length left arm. This is a partial improvement, not a
usable replacement asset or permission to continue fitting automatically.

## Contract and reviewed cases

Follow [V7 plan](GERMAN_NPC_TRIGGER_LOWER_V7_20261006.md). Read HANDOFF/618 epoch,
Failures index, V6 and V4 results, GP010, AN002, AN008, weapon-hand guide and
character workflow. The user explicitly retains the raised thumb and draws
the stock-end downward arrow. This supersedes V6's stopped-pose consumption and
gun protection only within this new comparison; the old failed root rotations
were not rerun or relabeled successful.

Starting pose is V4 `offline_v6` plus the exact retained V6 pure-elevation
thumb quaternion arrays. ONE modest 8-degree pitch was the documented default,
not a measured final-fit angle or sweep. The actual trigger landmark remains
fixed. The arrow lowers the REAR stock; the opposite muzzle consequently rises.
No independent gun translation, yaw or scale; no further right-thumb/digit
rotation or source model/weight/rest/length/material/action edits.

## Measured comparison

- Trigger pivot residual 8.5265e-14 cm. Actual retained stock contact moves
  (+0.887001, -0.083539, -1.045733) cm, verifying the downward sign.
- All protected bone matrix entries differ by at most 2.7285e-12; fresh
  reconstructed right-world matrices are identical. Mature right thumb/other
  digit locals are retained; complete digit-local error 1.8190e-12.
- The left wrist/grasp follows the same rigid gun change. Left gun/hand-relative
  matrix error 9.0949e-13, wrist motion 1.240717 cm. Original upper/forearm
  lengths 30.340166/26.975170 cm, length errors below 7.5e-14 cm.
- New severe skin edges 0 under the unchanged >3x AND >2cm-extra definition;
  maximum extra edge length 0.240840 cm. Mixed left-digit skin tracking residual
  0.386901 cm: bone-relative agreement is NOT rigid skin agreement.

| Crossing-face diagnostic | Raised-thumb BEFORE | Stock-down AFTER |
| --- | ---: | ---: |
| Right thumb / wood | 97 | 44 |
| Right index / whole gun | 67 | 73 |
| Right index / wood | 22 | 29 |
| Right index / trigger blade | 21 | 20 |
| Left thumb / whole gun | 2 | 2 |
| Left index / whole gun | 84 | 84 |
| Left little finger / whole gun | 24 | 24 |

Other middle/ring/little crossing counts remain zero. Counts are triangle
crossings, not depth, and zero crossings alone are not enclosure. A fixed
trigger POINT does not preserve the entire rotated blade/stock relationship
with a fixed straight index. Thumb improvement does not close the remaining
44 thumb faces or the increased index crossings. BEFORE is a freshly encoded
raised-thumb reconstruction, not a relabeling of V4's earlier 69-index receipt.

## Source-weight boundary and preserved failures

`stock_down_v1` stopped before pose evaluation: a project-relative path helper
cannot record the user's Temp screenshot. The private preflight receipt and
original source remain. Distinct `stock_down_v2` corrects external-reference
bookkeeping only and evaluates the ONE 8-degree transform.

V2's blanket ANY-right-hand-weight skin assertion fails at 1.974245 cm. Preserve
that failed receipt. Read-only inspection identifies SIX source vertices with
cross-hand weights: three on the left support and three on the right palm/thumb
boundary. The right mask includes moving left-support vertices; however the
actual three right boundary vertices also move, so do not call all right skin
unchanged. No source weights were fixed or threshold loosened.

Distinct fresh-process `review_v1` reproduces the RETAINED transforms without
another fit. All true-zero-LEFT-influence skin and actual distal right-index
skin displacement are 0 cm. Right-side shared vertices 9437/11129/11130 move
0.235226/0.348936/0.232076 cm. The three left-side shared vertices move
1.974333/1.881285/1.867282 cm as the support follows. Complete source weights,
IDs and displacements are recorded. This is a boundary diagnostic, not a
promotion of V2's failed assertion or full-skin/contact acceptance.

## Actual images and closure

Opened all ten original BEFORE/AFTER reverse, right, top, support and full-arm
images and both labeled sheets. Stock sits lower under the raised thumb; the
right-side view exposes more of the proximal thumb rather than splitting it
visually with wood. Some penetration remains. Left support/arm are continuous
in these static views. Small palm/cuff skin projections remain visible as gun
occlusion changes; no source-level skin repair or complete hidden-seam proof.
Gray/orange/blue diagnostics are not game texture/native shader parity. Full
original 25,236-vertex/42,753-triangle skin and 24,466-triangle gun are used;
no detached hand, cut/mask or game-ready replacement mesh is authored.

Private evidence:
`Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/GermanNPCTriggerLowerV7/`

- `stock_down_v1/preflight_failure.json`: reference-path failure before fitting.
- `stock_down_v2/result.json`: ONE transform, contacts and failed blanket mask.
- `review_v1/result.json` / `diagnostic_geometry.npz`: read-only reconstruction,
  six shared-weight records and ten original diagnostic views.
- `review_v1/three_views.png` / `context.png` / `presentation.json`: marked review.

All three Blender processes exited normally 0; this does not make failed
receipts passes. Final check: 618 current formal guards exact, 12 input records
exact, four V7 tools parse, no Unreal/Blender engines. No native slot claimed;
lane A remains RELEASED. Formal German remains unarmed; approved Allied/FP/B,
source rig/weights/actions/materials/map/Catalog unchanged. No native entry,
asset/package/map save, formal adoption, release/publication, deletion, commit
or push. Await next marking; no automatic further angle/digit/offset correction.
Motion/reload/recoil/lifecycle/FPS/Shipping/second-machine gates remain untested.
