# Allied NPC — marked rearward move and existing fingertip curl V11 result

6 October 2026. Requested local CHANGE generated and inspected in original UE
textures; full trigger-contact gate FAILED. Comparison only, not formal asset
or human grip acceptance. Plan/addenda: `ALLIED_NPC_INDEX_CURL_V11_20261006.md`.

## Source and scope

User marks small rearward rifle movement and inward index-tip bend. This
explicitly permits local index rotation, superseding prior fixed-digit scope
ONLY here. Read current HANDOFF/Git, Failures/README, AN002/FP001, V10 result,
grip guide and Blender character workflow/execution/form-fit references.
Actual native V10 after pose and immutable full US rest/weights cache used.
Existing source2.2s D059 target action has EXACT matching reference-local
matrices for right hand/index chain; no player gun offsets copied to NPC.

Final private V11e retains gun angle/scale, moves it0.4cm toward stock along
current longitudinal axis, world(-0.333983,-0.026892,-0.218477)cm. Right index03
uses one-third interpolation toward EXISTING D0592.2s local rotation, ~7degrees.
Index01/02, right wrist/arm, all other digit locals remain unchanged. Whole
left arm follows using original segment lengths. No new action, scale/length,
mesh, weights, UV, material, source clip, camera or gameplay transaction edit.

## Retained attempts and limits

- V11: omitted mathutils.Matrix import in extracted helper; failed BEFORE pose
  evaluation. Preserve source/result; V11b corrects only import/new identity.
- V11b: all30 declared idle/D059 poses and strengths completed. Idle unchanged;
  whole-index curls cross guard or withdraw pad several cm. No accepted fit.
- V11c: exactly six source2.2s distal-only alternatives completed. Source03-only
  ~7degrees gives stock0/guard0/blade9; larger/two-distal variants fail. The old
  joint-position metric cannot see03-only curl; corrected distal orientation
  metric does not relax the unchanged contact gate. No source-action creation.
- V11d: new fixed7degree pose, analytic swept actual triangle clearance along
  rearward axis ONLY inside0..1cm; no clear interval, stopped/no candidate.
  V11e saves intervals[0,1] and swept pair evidence. Continuous SAT tests for
  separated parallel planes, actual plane touch and coplanar slide pass; they
  do not turn the native grip into an accepted fit.
- V11e: reconstructs original0.4cm/7degree local change ONLY for explicitly
  labeled comparison. Deformation/protection pass; contact stays FAILED.

All five Blender processes normal exit0, but actual result statuses distinguish
import/geometry failures from process success. No old stopped FP/reload author
or live native skinned-vertex query was executed. Preserve failed caches/input
sources and do not continue stopped pose/axial scans automatically.

## Actual checks

| Check | Delivered comparison |
| --- | --- |
| Offline existing index03 curl | 7.000012degrees; source21degrees at one-third |
| Native curl / rearward distance | 7.000102degrees / 0.399998cm |
| Native gun angular change | within0.01degree representation tolerance |
| Actual distal skin pad–blade gap | 0.148259cm; distance ALONE is not clearance |
| Full index stock/guard/blade crossing faces | 0/0/9, local contact FAILED |
| Protected native bones | position0cm; rotation within0.01degree |
| Protected offline bones / other digit-local matrices | 4.55e-12 / 1.82e-12 |
| Right wrist / unaffected skin | 1.36e-12 / 4.79e-12cm |
| Index03 influence shared with other right digit skin | 0 vertices in retained full cache |
| Left bone-segment length error | 7.32e-13cm |
| New severe edges / index-neighbor self pairs | 0 / 0; max extra edge0.133955cm |
| Fresh reconstructed saved skin / gun max error | 0.000210cm / 0.000040cm |
| Guards and retained input hashes | all611 current combined A+B rows exact |

Other thumb/middle/ring/pinky stock crossing faces21/57/69/38, guard/blade0.
They remain separate unfinished grasp problems, not repaired or accepted here.
Static local evidence does not verify firing, reload, locomotion or aiming.

## Native images and visual review

Unsaved `index_curl_native_v11`, owned PID6032 normal exit0. Proved paused
full-source Poseable refresh and public bone/gun parity, original NPC driver
untouched/no FP binding. Original V10 right/trigger baseline inspected before
comparison. All12 original1600x1000 views and four labeled sheets opened:
front/right/top/reverse, trigger right/reverse/top/under, before/after full arm.

Right side shows SMALL distal inward turn, not a deeply curled whole index.
Reverse exposes the blade still contacting/passing into the pad; do not call
this zero penetration or a fully correct firing grip. Wrist/cuffs/elbows/full
left chain look continuous in STATIC views. Top partly hides the contact and
cannot establish clearance. Native texture detail varies between captures
despite unchanged material paths; no retouch or texture improvement authored.

Fresh native verifier initially passed quaternion ARRAYS to a helper expecting
transform dictionaries. Corrected caller ONLY and rechecked existing saved
result, no geometry/native rerun. Retain this technical invocation failure;
it is not an engine crash or newly repaired source. One wrapper syntax command
also failed shell quoting before execution; stdin-based check then passed.

## Evidence and final state

Private root:
`Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/AlliedNPCGripV2/`.
Retain `index_curl_v11`, `index_curl_v11b`, `index_curl_v11c`,
`index_curl_v11d`, `index_curl_v11e` and `index_curl_native_v11`.
Final full NPZ/transforms are diagnostic evidence, not an exported playable rig.
Native originals plus `comparison.png`, `three_views.png`, `trigger_details.png`
and `arm_context.png` carry explicit failed-contact labels.

Fresh full geometry/native transforms/inputs/611 guards verified; owned process
closed normally, no UE/Blender processes remain, lane A RELEASED. No map/package
save, selection, deletion, publication, Git commit or push. Approved first
person, B/German/AI/BT/BB/map/Catalog and gameplay remain protected. German
deferred. User can mark the actual comparison; no automatic stronger curl,
extra direction/angle or adoption follows this result.
