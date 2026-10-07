# German NPC ordered grip V4 result

6 October 2026. Static ordered comparison delivered for human review; **full
grasp is not accepted and no formal German asset has been replaced**. The
reviewed candidate is `offline_v6` reproduced by `ordered_native_v2`, NOT the
failed `final_clearance_v7` or the rejected V2 large-angle result.

## Contract, cases and changed mechanism

Follow [the V4 plan](GERMAN_NPC_ORDERED_GRIP_V4_20261006.md) and
[weapon-hand calibration guide](WEAPON_HAND_CONTACT_CALIBRATION_GUIDE.md).
Read current HANDOFF/618-row epoch, failure index, GP010, AN002, AN008, German
V1/V2/V3 and accepted Allied V11/V13/V14/formal-usage records. The character
workflow required actual complete-arm/closeup review and original-length arm
checks rather than treating bone proximity as a completed grasp.

User authorized a modest further right-grip angle, then downward stock-pivot
rotation/support fitting, using Allied appearance as a reference. No Allied
offsets or digit numbers were copied. Existing German A mesh, skeleton, skin
weights, materials, Ready action and V15 rifle geometry/scale are preserved.
No finger local rotations, source action, camera/gameplay transaction or AI edit.
The native renderer uses the existing full mesh in a temporary Poseable display;
it is static diagnostic evidence, not a newly playable rig or animation asset.

## Ordered steps and early checks

1. From actual V3, rotate the gun another5degrees around the retained actual
   trigger point (total10degrees from V1). All character bones stay fixed here.
2. Around the marked stock/grip surface, lower the muzzle12degrees. Merely
   rotating the gun with fixed hands displaced the trigger2.059cm and worsened
   contacts, so that candidate was stopped. The distinct V6 mechanism carries
   the fitted right hand/gun pair together for this downward stage, with an
   original-length right arm chain. It does not bend the index to compensate.
3. Fit the whole original-length left arm to the actual fore-end while retaining
   its mature grasp and digit locals. The nominal palm target is0.3cm outside
   the measured wood point; this target is not proof of complete skin clearance.
4. Fresh native BEFORE right/top reproduced V3 and was opened before candidate
   capture. Fifteen original textured images plus four composed sheets were
   opened, including both sides, both contacts, shoulders/elbows and full body.

Native gun elevation changes14.6914->2.6914degrees, producing an almost
horizontal rifle. No rejected37.6degree endpoint transform was reused.

## Verified measurements, with limitations

Independent read-only `ordered_native_v2/verification.json` verifies:

- Actual extra yaw4.999996degrees and downward pitch12.000000degrees; trigger
  pivot during yaw0.000001124cm and stock pivot during pitch0.000000300cm.
- First yaw leaves all bones exact. Coupled pitch preserves right gun/hand
  relative pose to0.000134403cm/0.000001708degree in native representation.
- Native digit local difference0.000495858cm/0.000057628degree; offline local
  matrices remain unchanged within1e-8. Protected non-arm bone worlds are exact.
- Original upperarm/forearm lengths remain about30.340/26.975cm on both sides;
  native differences are below0.000126cm. Offline original-length checks are
  below3e-13cm. Right wrist moves3.553cm, left wrist5.914cm as whole arm targets.
- No new severe skin edge under the unchanged >3x AND >2cm-extra definition.
  This does NOT mean no cuff artifacts: small exposed skin chips are visible
  at the left cuff. All-positive-influence right-digit skin is not rigidly
  identical: maximum mixed-weight residual0.411046cm, with weights unchanged.
- All618 current approved guards and recorded source inputs remain exact;
  all15 captures have0cm gun drift and original materials are used. The actual
  staged weapon components use NoCollision. No live skinned-vertex query.

Crossing-face diagnostics remain unpassed (affected faces use every positive
digit weight; counts are not penetration depth or a human appearance verdict):

| Contact | V3 | Extra yaw | Final coupled pitch/support |
| --- | ---: | ---: | ---: |
| Right index, whole gun | 48 | 69 | 69 |
| Right thumb, wood | 91 | 76 | 76 |
| Left thumb/index/little, whole gun | reference retained | reference retained | 2 / 84 / 24 |

The extra yaw does not clear the index; the coupled downward step preserves
its first-stage relationship rather than falsely claiming zero intersections.
Right middle/ring/little have zero crossing counts but remain visibly loose:
zero intersections are not enclosure. Right palm/stock relationship and
straight index/guard/blade overlap remain deficient. Left support is visibly
closer under the fore-end, but local finger overlap is not solved.

## Failed comparisons retained

- `offline_v1`: native identity root is the FBX armature object, not a named
  bone. A correspondence-only correction verifies all other names/weights;
  reference alignment0.000258881cm, unchanged0.01cm gate.
- `offline_v2`: guessed TriggerGuard name mismatched actual immutable GLB
  parts. Correct actual Wood/Guard/Trigger membership only, unchanged bounds
  and24,466 triangles. No geometry rebuild.
- `offline_v3`: full fixed-left target requires20.652degrees downward, exceeding
  the12degree cap and still leaving3.828cm radial/depth residual; stopped.
- `offline_v4`: display conversion was-12.000000000000002degrees; V5 compares
  the same clamped cap in radians. No angle enlargement or new geometry.
- `offline_v5`: fixed-hand partial pitch shifts trigger2.059cm, right index
  crossings48->134 and left thumb stock crossings50. Stopped, not selected.
- `ordered_native_v1`: enum-string assumption differs from installed
  `<CollisionEnabled.NO_COLLISION: 0>`; stopped before any images. V2 compares
  the actual enum with unchanged NoCollision requirement. No engine crash.
- `final_clearance_v7`: the plan's ONE whole-left-arm0.499999cm outward
  correction increases crossings110->171 (thumb2->0, index84->115,
  little24->56). Failed before geometry/native publication. **Not used**;
  no opposite-direction offset, additional angle or finger retry follows.
- Two read-only verification attempts compared mixed-unit matrix entries to
  one newly introduced scalar and stopped (0.000127/0.000480 maximum).
  Retained attempt JSONs; corrected verification uses the original plan's
  separate0.01cm/0.01degree native parity limits, without changing fitting,
  source data, contact gates or candidate images.

## Evidence, closure and human-review boundary

Private evidence base:
`Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/GermanNPCOrderedGripV4/`.
Reviewed `ordered_native_v2`: `three_views.png`, `contacts.png`, `steps.png`,
`context.png`, fifteen original PNGs, `result.json`, `presentation.json`,
`verification.json` and retained failed verifier receipts. Evidence pixels are
laid out/resized only, not retouched. Step views explicitly label different
camera widths; no identical-framing or UE/full-PBR equivalence claim.

Owned native PID13300 (pre-capture failure) and PID29516 (15-image comparison)
both exit normally0, receipts under `tmp/german-npc-ordered-grip-v4/`. Final
process check finds no UE/Blender engines; Lane A RELEASED after618 guard check.
No native source driver, approved Allied/FP/B data, map/package, Catalog or
formal selection changed. Formal Germans remain unarmed; the existing rifle
was staged unsaved. No SFTP immutable release, asset/source deletion, Git
commit or push. New scripts/documentation and ignored evidence only.

Stop for user marking of this candidate. Overall posture improved, but this is
not a complete grasp/clearance pass and not formal adoption. No motion/reload/
recoil/lifecycle/near-wall/FPS/Shipping/second-machine testing was run. Further
fitting must address the actual remaining contact constraints in a new bounded
plan; do not revive the failed clearance, large-yaw or individual-digit solvers.
