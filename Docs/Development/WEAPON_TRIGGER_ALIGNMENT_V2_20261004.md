# Trigger-pivot / support-surface calibration V2

4 October2026. User explicitly continues calibration after the first comparison,
suggesting trigger-index contact then lifting the floating support hand. Anatomical
roles are being clarified asynchronously: original orange=index_r/trigger hand,
blue=left support. No left-handed conversion or hand edits while that is unclear.
[Chinese review](WEAPON_TRIGGER_ALIGNMENT_V2_20261004_ZH.md).

User clarification received before execution: retain right index/trigger and
left support. The suggested support-hand lift refers to the LEFT limb, not a
left-handed conversion. Rigid first proof remains hand-unchanged; if needed,
record a bounded left-arm pose solve before its separate execution.

Read HANDOFF, failure index, AN003/004/005, FP001, rejected coarse finger result,
and trigger V1 result. Previous turn also reviewed AN001/002. Translation-only
stopped because support contact separated. User continuation permits a DIFFERENT
mechanism: actual trigger-pivot rigid rotation jointly constrained by the actual
support-palm/fore-end surfaces, not another offset grid or old two-hollow fitting.

## Implementation contract

- New WeaponTriggerAlignmentV2 source/evidence identities; preserve V1 and all528
  current native guards from map_recovery_v1. No UE writer needed for first proof.
- Same M1/owner FBX/native compressed reload poses, rig/weights/UV/geometry/actions
  unchanged. Use actual previously identified blade. Project its approximate
  landmark onto actual selected blade faces and the distal pad centre onto actual
  selected pad faces; record triangle IDs, normals and positions, not just bones.
- Derive trigger translation once; then keep that contact as pivot. At reload
  start, identify upper-facing dominant-hand_l palm faces, project their region
  centre to an actual triangle. Stock's lower-facing forward-fore-end faces come
  only from inspected component0. Intersect actual triangles with the sphere
  centred at trigger whose radius reaches the palm target; select the closest
  actual surface point and derive ONE minimal-arc rotation. Scale remains1.
  This is a geometric two-contact solve, not an arbitrary rotation/offset sweep.
- Early rotation limit15degrees. Inspect original/V1/V2 at0/2.2/4.1s with the same
  cameras, plus actual right-hand contact-only view if left overlaps during reload.
  Report cross-stock/guard/trigger separately; no closed-volume claim from signed
  nearest distances. No fewer-intersections-equals-pass claim.
- If two contacts require excessive rotation or other contact remains visibly bad,
  stop this candidate; no relaxed gate, model/weight/finger/camera/motion changes.
  Report actual residuals. User-authorized hand-lift idea is not yet an anatomical
  side-resolved rig implementation. If later resolved and needed, document exact
  bounded limb nodes and continuous forearm validation first, never translate only
  mesh vertices or detach a hand from the arm. Do not recreate detailed people.
- Whole unchanged arms should be shown alongside close-ups. Native adaptation
  requires B slot coordination and bridge-disabled fresh motion/lifecycle/near-wall
  checks; never rerun AN004/005 stopped integrations as acceptance. No NPC offset
  copy, formal-map selection, Catalog/release/package/purchase/commit/push.

Acceptance for this first proof: actual-surface landmark identities/unchanged
scale verified, index materially closer to blade without a new stock crossing
pattern, supporting palm no longer obviously suspended, and no new palm/thumb/
finger/forearm defects. Preserve failure/evidence and stop rather than silently
selecting. Other all-phase/runtime/gameplay acceptance remains separate.

Technical stop preserved before rendering: pivot_fit_v1 derives51.1044degrees,
exceeds15degree gate and exits without modifying inputs. Audit finds coordinate
fit determinant=-999997.6601 (Blender→UE reflection); raw triangle cross-product
normals were used without parity correction, selecting dorsal/upper stock rather
than support/lower faces. V1 landmark-side labels are therefore invalid, although
its visible placement conflicts remain real. ONE technical correction negates
normals after this verified reflection and reidentifies actual face regions;
render-only diagnostic winding follows the same parity. New pivot_fit_v2 identity,
unchanged solve/15degree limit/source bytes, not another parameter search. Preserve
v1 source/result and do not use its51degree value to claim physical impossibility.
