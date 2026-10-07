# German NPC V13 — reuse the approved Allied grasp

**RETIRED BY USER, 6 October 2026:** the user rejects the effect and requests
return to the previous refined German model/parameters. Do not execute this
plan. Read `GERMAN_NPC_ALLIED_GRIP_V13_RESULT_20261006.md` and resume V11 instead.

## Authority and scope (6 October 2026)

Yupu explicitly requests transferring the approved Allied hand-pose parameters
to the German hands, then fitting the actual German rifle. This supersedes the
earlier individual German digit preservation only for this new comparison.
No hand mesh transplant, new animation, rig/weight/rest/length/material edit,
formal NPC selection, map save, Catalog update, deletion, commit or push.

Use the complete approved Allied V14 native holding snapshot underlying the
selected V16 config, not an arbitrary D059 reload phase. Copy corresponding
**local rotations**, by bone name, of the 30 digit joints. Retain German local
translations/scales and the original German wrists initially. This is a pose
parameter transfer, not an Allied world-transform or gun-offset copy.

## Read cases and changed mechanism

Read HANDOFF, current Git state, Failures/README, the weapon/hand calibration
guide, Allied formal V18 result and AN008 analysis, and German V12 result.
V12's source-phase/closest-patch translations left blade and lower-grip
problems; those stopped solvers are not rerun. AN008 shows that additive pose
deltas are not stable across different source poses; a later native layer must
use accepted locals and release/blend for existing actions, not lock the grasp
through reload. AN002's risky live skin query is not used. The new mechanism is
the already human-accepted Allied grasp plus a German-specific rigid gun fit.

## Sequence

1. Verify the accepted Allied config against its full native snapshot. Verify
   corresponding hierarchy and native reference frames for both hands.
2. Transfer digit local rotations. Reconstruct the complete German skin with
   its original 69-bone weights/rest geometry; compare actual bent index and
   palm/thumb/lower-three appearance, not just joint values.
3. Fit the actual German rifle using its real trigger and stock surfaces,
   translating and rotating as one rigid object. Use Allied hand-relative gun
   orientation only as a reference; derive German translation from German
   surfaces and the transferred grasp. Do not resize the gun/fingers or copy
   Allied offsets. Follow the support wrist using the original-length arm
   chain; retain the reused digit locals.
4. Fresh reconstruct saved parameters and render matched right/reverse/top
   views, trigger detail and full-arm context. Inspect every delivered image.
   Preserve incomplete contact honestly; static views are not native/action
   acceptance. Do not run stopped UE launchers or touch formal assets.

## Early acceptance and stop

Before fitting, require all 30 parent mappings to agree, reference translation
error <0.001 cm and rotation error <0.001 degrees. The accepted config's local
rotations must agree with its approved full snapshot within 0.001 degrees.
Transferred local translation/scale error <1e-6, rotation error <0.001 degrees;
protected bones remain exact. Stop on incompatible frames or corrupted inputs.

Produce one complete parameter-transfer comparison, then at most one
surface-derived rigid seating correction based on inspected views. No angle,
offset or individual-digit search grid, no arbitrary source-phase sweep. Stop
on unreachable original-length support arm, new severe skin edges (>3x old
length AND >2 cm added), visibly broken hand/arm or source/guard mismatch.
Existing small overlaps are recorded separately from obvious penetration and
do not justify silently changing finger rotations or weights. If the reused
grasp cannot fit the actual stock, record that limitation and request review.

## Storage and protection

Code/documentation live in Git paths; private pose data, images and diagnostic
blend remain in the single ignored SFTP workspace under
`Evidence/GermanNPCAlliedGripV13`. Check all 618 current approved guards before
and after. Original V11 human visual acceptance and V12 failed results remain
in place. Current formal German remains unarmed until separate UE adoption.

## Donor clarification after actual views

The first conventional Allied NPC V14/V16 transfer reproduces its relatively
straight index; its actual gray views do NOT match the curled grasp in the
user's explicitly linked `WeaponTexturedViewsV17/presentation_v2/three_views.jpg`.
That linked image is the Allied first-person presentation, not the NPC pose.
Retain the first comparison; do not call it the requested successful grasp.

Use the linked presentation's subsequently accepted/current native first-person
grasp config (`LeftSupportV20/reuse_pose_v2/binding.json`, V18 right grasp/V20
left thumb). This is the user's requested reference, not an arbitrary player
offset copied into an NPC. Verify its underlying reference basis, transfer ONLY
30 local rotations; specifically **do not transfer the FP pinky 0.90 scale**.
Register the actual German trigger/stock against corresponding donor gun
surfaces. Both hands are reconstructed with German bone lengths/weights. A
bounded final whole hand/gun assembly orientation may use the original German
firing direction with continuous original-length arms if necessary; no separate
finger solving. This donor correction is based on inspected evidence, not an
angle/source-phase scan or permission to modify the accepted first-person asset.

The full-body reverse/top closeups are occluded by the torso. A separate
presentation-only hand/weapon view may isolate existing hand triangles with
unchanged vertices/UV/materials; keep the full body and arm context visible in
separate images. This is not a runtime mesh cut, skin fix or omission of a
known contact defect. Portable jacket appearance differs from the native camo;
do not author/recolor textures to conceal this or claim UE shader parity.
