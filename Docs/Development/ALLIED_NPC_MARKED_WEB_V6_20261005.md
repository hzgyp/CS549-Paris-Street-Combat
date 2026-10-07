# Allied NPC — user-marked stock-web comparison V6

5 October 2026. The user asks to translate the whole rifle left/down in the
marked right-side view, then rotate around the firing-hand web to lower the
fore-end into the unchanged left support. The later `continue` resumes this
bounded comparison. This supersedes V5's no-rotation stop only for this trial.

## Contract and protection

Use the actual Allied US paratrooper / original M1 / V3 attachment / existing
Allied Stride Ready pose. Native UE 5.8 coordinates are centimetres; preserve
gun scale, every character bone, source mesh, rig, weights, UVs, materials,
actions, camera and transactions. No new motion, finger or arm correction.
Approved first-person, German, B controller/BT/BB, formal map and Catalog stay
protected. This is a static fitting comparison, not a playable-rig export or
motion/adoption test. No native asset save, deletion, publication, commit/push.

Generic scripts/docs live in Git. Commercial geometry, recorded landmarks and
actual screenshots remain in the existing ignored SFTP workspace under
`Evidence/AlliedNPCGripV2`; preserve previous identities and failed evidence.

## Cases read and changed mechanism

Read Failures/README, AN002 and FP001 analyses, the weapon-hand guide including
left support, Allied V2 plan/addendum, stopped stock-pivot reconstruction and
V5 result/source. AN002's live native skin read and stopped fitting solver are
not run. Reuse only reviewed offline FBX skin/math fragments and public native
bone transforms. FP001 numerical/visibility success does not replace images.

Unlike the old nearest-wrist/trigger-direction rotation, identify a real stock
neck point and actual hand-web region in the USER-marked V5 side camera. Use
source geometry to record depth and verify the stock region. The arrow is a
direction/region, not a calibrated displacement or exact hidden 3D landmark.
Choose one small left/down seating translation; then one minimal 3D rotation
around its seated stock-web point toward the actual left palm. Select the actual
fore-end underside nearest that palm after seating, not the camera-facing wood
surface: the latter is laterally displaced and a side-image match can leave a
large depth gap. This is landmark measurement, not another fitted candidate.
No angle grid,
offset sweep, automatic digit compensation or player numeric copy.

## Early checks, evidence and stop

Before native work, reconstruct the V5 frozen source pose from the preserved
full US FBX and recorded rest/bone transforms. Rest alignment must be <0.01 cm,
reflection parity explicit, weights untouched. Inspect real source-surface
landmarks and projected contact regions; stop on uncertain source identity,
missing geometry or frame mismatch. Bound seating translation to 4 cm and
rotation to 15 degrees. Report residual depth/contact separately; fitting a
screen point does not prove penetration clearance.

Native preparation recreates V5 and derives the ONE rotation using this native
Ready pose's fixed right-web pivot and fixed support-palm point. Check measured
pivot drift <0.01 cm, all character transforms exact, scale exact, and native
gun transform matches the computed rigid transform (<0.01 cm / 0.01 degree).
Use a source-verified quaternion-to-Rotator conversion, not the failed Transform
Quat constructor. Stop on API, ownership, deadline or 611-row guard conflict.

Inspect matched original, translated-only and final side images; final front,
right, top, trigger/support detail and full-arm context. Open actual originals.
Record index-to-trigger change and visible stock/guard/palm limitations instead
of repairing fingers. Visible regression prevents full acceptance, not retention
of this explicitly requested partial comparison. No automatic second candidate.

One native editor writer only: fresh process/611 combined guard check and explicit
HANDOFF slot claim before launch. Owned hidden editor alone may close normally;
never close a user/B editor. After process closure recheck hashes and release.
Await user's three-view review; German remains deferred until Allied acceptance.

Measurement-only correction: `marked_web_measure_v6` stops before ray selection
at the horizontal-axis assertion. Its generic right-handed camera cross product
points opposite the recorded UE side-camera screen-right. Retain that script and
failure unchanged. `measure_marked_web_v6b.py` changes ONLY this camera cross
order to the native UE screen-right convention; no movement/fit parameter change.
Fresh identity, original source/611 guards exact. No native crash or model edit.

The corrected rays identify actual 100%-hand-weight palm/web triangles and real
stock triangles. The native side's web/pivot visible faces differ laterally by
4.50 cm; keep and report this, not a hidden-depth acceptance claim. A further
read-only surface measurement uses the same preserved geometry to identify the
forward underside nearest the fixed left palm. No first fitted candidate was
rendered or natively executed by these measurements.
