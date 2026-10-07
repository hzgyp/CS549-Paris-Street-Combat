# Allied NPC — marked-web V6 comparison result

5 October 2026. Scope/cases/early check/stop:
[V6 plan](ALLIED_NPC_MARKED_WEB_V6_20261005.md).
Private evidence: `Evidence/AlliedNPCGripV2/marked_web_v6` in the existing ignored
SFTP workspace. No candidate native asset or formal map was saved.

## Actual change and preservation

Recreated V5 on the actual Allied/M1/V3 Ready pair. Native idle phase differs
slightly between launches; the measured surface points are mapped through the
actual right/left hand frames, not copied as an old world offset.

ONE whole-gun translation: world `(-1.0499496734,0,-1.7013766179)` cm (left/down
in the supplied right-side view), length1.999269cm. ONE minimal3D rotation:
12.095268degrees about the seated actual stock-neck point, axis
`(0.1394858651,0.8776678147,-0.4585225190)`. Offline V5 measurements gave
2.123838cm/11.746859degrees; this small difference is native-pose mapping, not an
angle sweep. Quaternion-to-Rotator roundtrip checked before movement.

All recorded character bones, hands/arms/fingers and gun scale remain exact.
Pivot drift0.000000118cm, ten native captures0cm gun drift. Original models,
weights, rig, source actions, materials, collision policy, first-person, German,
B AI/transactions, formal map and Catalog preserved.

## Visual result and limits

All ten1600x1000 original images and two equally-resized sheets opened: matched
before, translated-only, final front/right/top, trigger/support details and full
arms. Left palm/fore-end relationship is visibly closer and the gun lies more
nearly level in the fixed support grasp. No whole-grip acceptance inferred.

The chosen support landmark residual falls6.265097→0.983620cm. This is a fixed
point-pair residual, NOT nearest distance to the complete stock or penetration
depth. The visible hand/stock anchor faces retain4.485361cm lateral depth
difference; a side marker does not locate the hidden grasp centre exactly.

Right index/trigger regresses: retained pad/blade anchor gap1.315295→2.606150cm.
Actual detail shows index against stock side while blade/guard sit below it.
The firing hand is unchanged, but trigger contact is not. Candidate remains
unselected/partial; no automatic finger edit, angle increment or compensation.
Wait for the user's next marking. German waits for Allied acceptance.

Native texture detail still varies by capture (early side smoother, later
top/detail sharper) despite unchanged material paths; no retouch or texture
repair, exact cause unproved. Do not attribute sharpness to improved fitting.
No motion, fire, reload, lifecycle, near-wall or gameplay acceptance in this
static comparison; frozen diagnostics are not new playable rigs.

## Failures, closure and storage

Preserve the measurement-only horizontal-axis assertion failure: no gun/model
move or native crash. A new source retained alongside it corrects only the UE
camera cross-product parity. The additional underside measurement avoids the
camera-facing stock point's misleading depth gap, without another candidate.
No old stopped nearest-wrist solver or live skin query executed.

Native `errors=[]`, input hashes exact and611 combined guards before/after/fresh
closed-editor check exact. Owned PID46548 normal exit0/absent; no UE/Blender
process remains. New fresh-read verification retains the hand-relative candidate
transform and image hashes. Lane A RELEASES the serialized native slot.
No save/adoption/publication/deletion/commit/push; existing failures and sources
remain in place. Generic tools/docs only in Git, private geometry/images ignored.
