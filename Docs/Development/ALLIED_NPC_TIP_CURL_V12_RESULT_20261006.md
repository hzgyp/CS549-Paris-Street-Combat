# Allied NPC — additional user-marked fingertip curl V12 result

6 October 2026. Local comparison generated and original native views inspected.
Plan: `ALLIED_NPC_TIP_CURL_V12_20261006.md`. Not formal grip/action acceptance.

## Scope and local result

Read HANDOFF/Git, Failures/README, AN002/FP001, V11 result and Blender character
workflow/execution/form-fit references. Latest user marking explicitly permits
ONE further fingertip bend, not automatic resumption of the V11 pose/axial
scans. Actual native V11 after bones/gun are the baseline; original V10 and
existing licensed D0592.2s index03 rotation supply the interpolation reference.
Only index_03_r changes: existing-action strength one-third -> one-half.
Local translation unchanged; scale representation error2.14e-8. No new source
motion, arbitrary bend axis, root/middle joint adaptation, rig/model/weight/
UV/material/action/first-person or gameplay change.

| Offline check | Actual result |
| --- | --- |
| Additional / total source-directed distal curl | 3.499989 / 10.500102degrees |
| Every other bone / other local transform / right wrist | 0 matrix delta |
| Gun transform | exact BEFORE/AFTER native JSON; no movement/rotation |
| Unaffected skin | 0cm |
| New severe skin edges / index-neighbor self crossings | 0 / 0 |
| Maximum extra skin edge length | 0.066648cm |
| Reference-local frame error | <0.001, compatible source frame |
| Pad–blade distance | 0.148096 -> 0.046708cm |
| Index stock/guard/blade crossing faces | 0/0/9 -> 0/0/10 |
| Fresh full saved skin / gun reconstruction max error | 0.00000183 / 0.00000302cm |
| Source triangles / current guards / retained input hashes | exact / all611 exact / exact |

No new stock/guard entry or self-contact; local DEFORMATION comparison gate
passes. The blade-crossing count increases9 ->10; closer pad alone is not
clearance, penetration depth or physical trigger actuation. Complete local
trigger-contact gate remains FAILED. Other digits keep original poses and
identical stock21/57/69/38 crossings, guard/blade0; no full-grasp claim.
One Blender process normal exit0, no error or new fit scan; previous failures
remain unchanged. Private `tip_curl_v12/result.json`/`geometry.npz` contain full
saved transforms/skin and provenance, not a replacement playable rig.

## Native review

Completed serialized unsaved `tip_curl_native_v12`, owned PID6444 normal exit0.
Matching V11 baseline inspected before candidate. All12 original1600x1000
views and four labeled sheets opened: front/right/top/reverse, trigger
right/reverse/top/underside, before/after full arms. Small distal inward turn
is visible, not whole-index curl; reverse still exposes blade/pad contact.
Wrist/arms/cuffs remain continuous in inspected STATIC views. Top occludes
the contact and is not clearance proof. Native materials stay original;
texture detail varies over captures, not authored texture improvement.

Native readback: protected bone position0cm, gun position0cm/angular change
within0.01degree, actual additional distal curl3.500049degrees. Fresh native
checker verifies all12 distinct original images, saved pose/gun parity,
retained hashes and611 current combined guards. Full offline fresh reconstruction
and expanded viewer syntax/contracts pass. No native/Blender processes remain;
lane A RELEASED. Original NPC driver/FP binding/source asset unchanged.
No formal map/package save, selection, deletion, publication, Git commit/push.
Approved FP/B/German/AI/map/Catalog protected; German deferred. Actual action/
runtime binding and human whole-grasp acceptance are not tested by this static
comparison. No automatic further angle/offset/source adaptation authorized.
