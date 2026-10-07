# German NPC: user-marked gun translation V1

Completed as a static comparison; see
`GERMAN_NPC_TRANSLATION_V1_RESULT_20261006.md`. Do not rerun the occupied entry
or add a fit increment without a new user direction.

6 October 2026. User marks the retained German right-side image and requests
that BOTH hands stay fixed while the rifle moves into the indicated trigger
relationship. Interpret the arrow as the trigger region to meet the fixed right
index, consistent with the preceding Allied procedure. One translation only:
no gun rotation, arm/support IK, digit change, model/weight/material/action edit,
formal binding, map save, release, deletion or Git commit/push.

## Cases read and changed mechanism

Read Failures/README.md, AN002, GP010, AN008, NPC_GRIP_BASELINE_V1 plan/result,
the Allied translation-only addendum and the complete weapon-hand calibration
guide. The character workflow supplies multiview/source/deformation checks.
This does not rerun a stopped skin-query, grip solver or motion proof.

Use THIS German source pair, not Allied/player offsets. Resolve the marked
trigger point on the accepted GLB's actual Trigger_Donor surface, using its
verified native import frame and the retained orthographic camera. Register the
user's resized screenshot against the original pixels. The arrow's index end
defines the target in that camera plane; unseen depth is NOT established by
one image. Preserve the trigger's old view depth for this coarse translation
and explicitly report that limitation. Store the target in the original firing
hand frame so a fresh native idle does not borrow old world coordinates.

## Protection and storage

Explicitly adopt the CURRENT 618-row epoch from
Evidence/AlliedNPCFormalV18/selected_v1/result.json; old map/Catalog guards are
historical and never rollback instructions. Check all rows before/after, including
approved Allied policy, FP and B assets. Evidence lives only in the existing
private SFTP workspace under Evidence/GermanNPCGripV1; no model copies.

Lane A uses a new hidden owned editor only after process/slot checks. Formal
German remains unarmed. Stage the existing V2 attachment and exact V15 gun in
unsaved memory, with its original wiring/settings. Native idle drives the pose;
pause the whole world, inspect a fresh before image, move the gun ONCE, then
capture matched right/front/top/reverse/context/trigger views. Never save the
level, author a new pose, change collision or update the gun per frame in Python.

## Early acceptance and stopping condition

Verify original file hashes, native import bounds within 0.01cm, readable image
registration and actual trigger-surface provenance before launch. The native
pair/class/mesh/AnimBP/materials/collision must match the recorded source and
right index local rotations within 0.05deg. Before movement inspect the actual
textured right view. Stop on source/guard/ownership mismatch, unreadable/stale
capture, ambiguous registration, or the 240-second entry deadline.

After the ONE translation: all character bone transforms must stay exact, gun
rotation/scale unchanged, marked-point residual and capture drift below 0.01cm.
This is a partial positioning gate, NOT complete trigger/guard/palm/support
clearance, motion or gameplay acceptance. Other contacts may become worse;
show them without automatically compensating. Normally close only the owned
editor, verify guards and release Lane A, then wait for the next user marking.

Initial raw-pixel registration stops before native launch (gray RMS0.07958,
required0.035). Preserve registration_v1_failure.json. One presentation-only
correction initializes the same raw-pixel matcher from low-frequency silhouette
scales; final raw RMS threshold stays0.035. This is image-coordinate calibration,
not gun/pose sampling. If it remains ambiguous, stop before moving the gun.
