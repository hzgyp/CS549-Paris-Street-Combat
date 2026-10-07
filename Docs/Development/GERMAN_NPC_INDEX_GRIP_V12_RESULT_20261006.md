# German NPC V12 — index curl / whole-rifle fitting result

6 October 2026. **Partial local comparison, complete trigger-contact FAILED.**
Not a formal asset, playable rig, native/action result or human acceptance.
Plan and reviewed cases: `GERMAN_NPC_INDEX_GRIP_V12_20261006.md`.

## User decision and reference

User accepts the previous V11 lower-three appearance, asks to bend the firing
index without stretching, then move the whole rifle into renewed trigger
contact. This supersedes V11 pending visual review ONLY; its numeric overlaps
remain. V10 thumb approval is preserved. Supplied `WeaponTexturedViewsV17/
presentation_v2/three_views.jpg` shows the earlier FP V16 textured comparison,
not an Allied NPC calibration. Its hooked-index relationship is the visual
reference; no FP gun offsets or transforms are copied.

## Retained comparisons and failures

1. `source_probe_v1`: V11 skin/gun reproduced0cm; existing donor/native reference
   axes<=0.000230deg. Actual D0592.2s provides compatible curved locals.
2. `curl_then_translate_v1`:02/03 full existing reuse requires4.395630cm gun
   translation; stops before gun/left authoring at unchanged4cm early limit.
3. `complete_existing_grasp_v2`: complete01/02/03 reuse requires4.001552cm,
   also stopped. Read-only `root_limit_views_v1` reconstructs that single
   calculated failure:12 originals inspected, middle guard0→40/wood30→55;
   pad0.381→1.039cm. It is NOT a successfully selected over-limit candidate.
4. `paired_surface_v3`: nearest real pad/front pairing, same full source pose;
  3.456111cm translation but distal guard27/blade19 and middle guard50 fail.
   Curled-pad/root radius7.276cm vs blade/root9.458cm explains lost reach.
5. `distal_existing_grasp_v4`: wrong helper API (`tm.slerp` absent), fails BEFORE
   pose evaluation. Source/receipt retained. Distinct v4b corrects quaternion
   interpolation API ONLY; no failed fit rerun or changed gates.

## Latest delivered local comparison: v4b

Only index03 reuses one-half of the same mature existing D0592.2s rotation.
Verified local bend10.500155deg. Index01/02, right wrist/arm, accepted thumb and
middle/ring/little bone worlds/local posture are preserved. Local translation
unchanged, scale representation error remains negligible; no bone stretch,
source animation, mesh, topology, skin weights, UV or material change.

Entire gun translates1.051435cm, world(+0.790108,+0.026854,-0.693199)cm;
angle/scale exactly retained. LEFT original-length shoulder/elbow/wrist follows
the same rigid translation; all left digit local poses preserved. No detached
hand move.48 other serialized bone transforms exact, true-zero authorized
influence skin motion0cm; six original cross-hand-weight vertices move. Actual
three right boundary displacements0.01649/0.02474/0.01649cm; three LEFT-dominant
vertices1.0255–1.0349cm. Do not claim all right palm skin is fixed.

| Contact check | Original V11 | Latest v4b |
| --- | --- | --- |
| Full index stock / guard / blade crossing faces | 8 / 11 / 22 | 14 / 0 / 22 |
| Affected distal index stock / guard / blade | — | 0 / 0 / 22 |
| Selected local-pad mean blade gap | — | 0.344822cm |
| Thumb stock crossings | 57 | 50 |
| Middle / ring / little stock crossings | 30 / 32 / 39 | 46 / 42 / 43 |
| Middle / ring / little pad mean stock gap | .3813 / .4265 / .3266cm | .3357 / .4522 / .3820cm |
| Other four digits guard/blade crossings | 0 | 0 |
| New index-neighbor self pairs / severe skin edges | — | 0 / 0 |

Small terminal bend is visible, not a deeply curled whole index. Side/reverse
views still expose blade/pad overlap. Stock crossing counts worsen for index
root and lower-three even though their joints are unchanged; previous visual
approval does not automatically accept these changed gun contacts. Current
small correction is therefore retained for comparison ONLY, not a completed
fix. Do not resume stopped source-pose/offset scans or increase angles blindly.
Next needs a new bounded actual full-pad/blade/guard seating plan or user marking.

## Fresh review / measurement corrections

Separate Blender process reconstructs full69-bone original skin and16107-vertex
gun; saved skin error0.000144064cm/gun0. All12 original views plus three labeled
sheets opened: side/reverse/top/under, support and full-arm context before/after.
Static arms/cuffs remain continuous. Under/top partly hide contact; not hidden
clearance proof. Gray diagnostic colors only, no texture authoring or UE shader
parity. Editable scripts/pose JSON/full geometry evidence are NOT an exported
replacement animated character rig.

Retained v4b raw `index_chain_turn_after_deg` incorrectly inherits34.696deg from
the complete-source v2. Final independent checker corrects the interpretation:
01→02→03 HEAD-chain turn remains0.286948deg because only03 orientation changes;
verified distal LOCAL angular change is10.500155deg. Preserve raw receipt, do
not cite its inherited field as current bend. The checker's `index03_other_right_
skin_shared_vertex_count` uses a right mask that includes index itself; it is
not evidence of sharing with another digit. Use actual protected bones/full
skin masks and explicit cross-hand entries instead. Neither issue changes fit
geometry or turns a failed contact gate into a pass.

## Final state / private evidence

Private root: `Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/
Evidence/GermanNPCIndexGripV12/`. Latest `distal_existing_grasp_v4b`,
`final_views_v1`, `review_sheets_v1` and `final_check_v1` retain failures and
current verified comparison.618 formal Allied/FP/B/map/Catalog guards and
recorded input/image hashes exact; ten new Python tools parse. All owned
Blender processes normal exit0; no UE entry/native slot, A remains RELEASED.
Formal German remains unarmed; source/FP/Allied/B/AI/map/Catalog untouched.
No selection, export, package/map save, deletion, publication, commit or push.
