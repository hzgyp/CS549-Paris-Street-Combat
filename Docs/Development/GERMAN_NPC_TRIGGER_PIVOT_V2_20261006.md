# German NPC trigger-pivot stock seating V2

Completed as a static comparison; see `GERMAN_NPC_TRIGGER_PIVOT_V2_RESULT_20261006.md`.
Original result/coverage failures retained; no occupied-entry rerun or further fit.

6 October 2026. User marks the V1 TOP view and requests: preserve index/trigger
position, use the trigger as the pivot, rotate the stock toward the fixed right
hand. This explicitly authorizes a new gun rotation, superseding V1's no-rotation
stop only within this trial. Both hands, arms and all digit poses remain fixed.

## Cases read and changed mechanism

Read Failures/README.md, GP010, AN002, AN008, the German translation V1
plan/result and the complete weapon-hand calibration guide. The character
workflow provides source-preservation/multiview checks. No stopped skin-query,
finger solver, motion proof or original production route is resumed.

V1 translated the trigger into the index region but left the stock outside the
grasp. This attempt uses the SAME actual Trigger_Donor point as an invariant
pivot. Register the user's cropped/resized TOP screenshot against V1's original
native TOP pixels. Locate the arrow's stock-side point on the real wooden stock;
derive ONE signed in-plane rotation toward the marked palm point, around the
top-view normal. Choose the angle analytically from those two pivot-relative
directions; no angle/offset grid, independent translation or hand compensation.
The pivot-compensating origin movement is part of the rigid rotation, not an
additional seating translation. Record the radial/depth limits of a 2D marking.

## Protection and storage

Adopt all 618 current guards from AlliedNPCFormalV18/selected_v1/result.json;
verify the accepted V1 images/pose/landmark proof and source gun hash. Preserve
the formally adopted Allies, first person, B assets/AI, original German mesh,
rig, weights, materials and actions. No map/package save, formal selection,
release/Catalog update, deletion, commit or push. Private evidence uses the
existing one SFTP workspace under Evidence/GermanNPCTriggerPivotV2.

Before native entry check slot/processes. Recreate V1's hand-relative gun
transform on the current native German idle; do not reuse old world position.
Pause whole world. Fresh BEFORE top/right views must show V1's trigger/index
and stock/grasp relationship before applying the ONE rotation. All source
index locals must match V1 within 0.05deg; gun scale and protected assets exact.

## Early check, order and stop

Image-registration raw grayscale RMS must stay below 0.035. Actual native gun
import bounds must match within 0.01cm; actual stock point projection within
15 native pixels of the marked stock end. Signed rotation must move the stock
toward the arrow head, improve its camera-plane distance and be at most 45deg.
Radial mismatch is reported, not corrected with scale/translation.

After the rotation: trigger-pivot displacement below 0.01cm, gun scale exact,
all character bone transforms exact and capture drift below 0.01cm. Inspect
matched front/right/top/reverse views, trigger/right-palm closeups and full
shoulder-elbow-wrist context. A fixed pivot is not a guarantee that the whole
trigger/guard geometry maintains skin clearance: report actual views, not full
grip acceptance from one zero-residual number. Left support may become worse;
leave it fixed and visible. No automatic finger/support/angle compensation.

Stop on source/guard/ownership mismatch, failed marking/axis/native BEFORE
parity, wrong effective collision, unreadable capture or 240-second native
deadline. Preserve a stopped candidate and failures; never overwrite an occupied
identity or repeat a failed fit. Close only the owned editor normally, recheck
guards, release Lane A and return the textured comparison for user review.

Preflight axis correction: the first projection used the mesh/root yaw instead
of the native capture's ACTOR yaw and exceeded 45deg before any candidate or
native launch. Preserve axis_preflight_failure_v1.json. Derive actor direction
from the retained front capture's eye minus target; correct only that camera
frame. Keep the same marking/pivot/analytic fit and 45deg limit, not a new angle
sample or threshold relaxation. Stop if the corrected proof still fails.
