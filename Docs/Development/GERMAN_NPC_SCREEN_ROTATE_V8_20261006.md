# German NPC V8 — small stock-side rotation toward the marked camera

6 October 2026. User says V7's adjustment is acceptable and marks the stock
side: turn that region a little toward the screen, reduce overlap and seat the
palm against the stock's left side. This is approval to continue local fitting,
not formal asset/native/motion adoption or a claim of zero contact errors.

## Reviewed cases / changed mechanism

Read current HANDOFF/618 guards, Failures index, V7 result, previously reviewed
GP010/AN002/AN008, calibration guide and character workflow. Retain V6 thumb,
V7 reference-path and shared-weight failures. Do not rerun their fits or V4's
failed clearance. New mechanism: ONE small outward 3D rotation from actual V7,
not another downward pitch or thumb edit. Keep its raised thumb and right hand.

## Landmarks and bounded default

Starting transforms: V7 `stock_down_v2/result.json` AFTER, reproduced by its
successful read-only `review_v1`. Source rest/weights/triangles remain V4's exact
cache; geometry is not copied into another physical asset store. The marked
image is the reverse view: viewer depth direction is its actual (0,40,12)cm
camera offset. Approximate screenshot red-box center is normalized (394/645,
(310-39)/476) in the image region. Raycast onto the actual unchanged gun from
the matched camera; require a wood triangle rather than guessing a stock box.
Screenshot resizing is not a calibrated measurement; record the inferred point.

Continue to use the actual trigger pivot from V7, because the user has not
requested moving that anchor. The red box is an observation point, not a new
fixed pivot. Axis = normalize(cross(marked wood - trigger, toward-viewer)).
ONE4-degree small comparison about that axis, sign proven by positive marked
point movement toward the viewer. No independent gun translation/scale, angle
sweep, thumb/digit solver, source weight or action authoring.

Left wrist/grasp follow the rigid gun change with original-length whole-left-arm
IK and mature digit locals, as in accepted V7. Preserve all right bone worlds,
thumb/grip pose, other body bones, approved FP/Allied/B/AI, source mesh/rest/
weights/lengths/UV/materials/actions, map and Catalog. The six cross-hand-weight
vertices are affected skin; do not call them fixed or weaken old assertions.

## Early checks / evidence / stop

Before fitting: reproduce V7's source pose and actual gun and identify marked
wood face. Trigger <0.0001cm, protected matrix/digit-local error <1e-8, left
source-length errors <0.0001cm, zero-LEFT-influence/distal right-index skin
<0.0001cm and no new severe edges (>3x AND >2cm-extra). Report shared boundary
vertices and mixed support tracking. Check actual thumb/index/palm/gun contact;
a fixed pivot does not protect the whole blade after rotation.

Fresh-process exact input/pose/geometry reconstruction precedes matched reverse,
right, top, support and full-arm diagnostic views. Inspect every original and
both labeled sheets. Record visible overlap, arm/cuff continuity and unknowns.
Serialized float quaternion/display reconstruction parity is separately
0.01cm/0.01degree; this does not change raw protection or contact thresholds.
Gray diagnostic materials do not prove UE texture or game binding. This is a
single requested directional comparison; remaining contacts are explicit, not
permission for another angle/offset/digit adjustment. If guards/protection,
wood landmark, reach or skin-edge checks fail, preserve evidence and stop.
If contact worsens, do not adopt or automatically compensate. No native entry,
source deletion, asset/map/package save, release/Catalog selection/publication,
commit or push; stop at the user's next marking. Formal German stays unarmed.

The one measured outward turn reports thumb wood44->57 and index whole73->52.
This tradeoff is not a full-contact pass; stop fitting after it. Read-only
reconstruction/rendering of this exact comparison is allowed for user review,
not selection or a compensating follow-up angle/translation/thumb change.
