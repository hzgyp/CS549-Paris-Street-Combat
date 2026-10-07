# V13: explicitly requested additional10degree pivot comparison

4 October2026. [Chinese review](WEAPON_TRIGGER_PIVOT_V13_20261004_ZH.md).
Status: ONE additional static20degree comparison completed; contact gate failed,
stopped/unselected. Actual result: WEAPON_TRIGGER_PIVOT20_RESULT_20261004.md.

Yupu reviewed10degrees, considers the direction correct, and explicitly requests
another10degrees. This supersedes V12's no-increased-angle stop ONLY for this
single total20degree offline comparison. V12 remains a failed/unselected10degree
candidate, not accepted by the user's direction comment. No autonomous angle scan.

Reviewed HANDOFF/current Git, Failures/README, full AN003/AN004/AN005/FP001,
V12 actual result/implementation and the existing inspected M1 reference record.
The changed hypothesis is exactly the user's proposed larger total rotation,
not a new finger/weight fix or claimed measured ideal angle. Retain the source
baseline and actual-pivot/axis definition from V12 landmarks_v1 unchanged.

## Scope and order

1. New tools Tools/Integration/WeaponTriggerPivotV13 and private evidence only
   in the existing single workspace Evidence/WeaponTriggerPivotV13. Review/reuse
   pure V12 helpers, never execute the stopped V12 author identities.
2. One total20degree rotation about the SAME actual trigger pivot and SAME axis
   from original D0590s/V2 rifle/V3 approved index. Compute directly from that
   baseline, not by cumulatively reskinning or moving the previously corrected
   arm. Right hand/right arm/finger locals/scale remain unchanged.
3. LEFT hand follows gun position+orientation; original-length left upper/lower
   arm and original elbow side solve again from the unchanged source baseline.
   No stretching, mesh/rig/weight/source-motion/camera/transaction changes.
4. Keep the V12 actual-contact/continuity screen unchanged: right skin<0.0001cm,
   finger local matrices<1e-10, pivot/bone-length error<0.001cm, left-palm tracking
   <0.02cm, no new severe edges (>3x AND >2cm extra), index wood/guard0,
   blade<=baseline22/pad gap<=0.2cm, non-index wood total<=baseline99 and no new
   previously clear digit penetration. Also report10degree counts separately.
   Counts are not penetration depth or acceptance; inspect actual skin.
5. Render matched right/opposite/top/bottom/oblique, whole rifle/support/arms.
   Present the prior10degree and new20degree images at exactly the same camera,
   lighting and scale; open ambiguous originals. Do not hide shoulder sheets,
   finger crossings, the support hand or cuff boundaries to claim a pass.
6. Save a new frozen static comparison blend, independently fresh-open and
   verify evaluated geometry/input/native hashes. Static skin is not a playable
   rig/action export. Protect all528 current recovery records and old diagnostic
   files; no old-file rollback or overwrites.

## Stop, handoff and exclusions

Retain the requested comparison even if contact fails; then stop, no third angle,
translations/digit compensation/weight edits/relaxed gates. Source bytes and all
old trials remain. Next is user visual comparison, not automatic adoption or
continuous reload/movement/aiming. No UE slot/native/map/NPC/B/BT/BB/Catalog/
release/package/commit/push or new motion creation. AN004/005 and FP001 remain
stopped. Future native/aim integration still requires a bounded plan and serial
editor coordination after a compatible static grip is actually established.
