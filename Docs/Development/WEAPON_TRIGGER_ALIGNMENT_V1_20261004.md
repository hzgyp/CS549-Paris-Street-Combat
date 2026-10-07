# Weapon trigger alignment V1 — rigid weapon first

4 October 2026. Yupu's latest screenshot/request supersedes the planned index
joint experiment: move the rifle relative to unchanged hands FIRST, using the
actual trigger, then consider finger correction only if necessary. The same
symptom occurs on NPCs. No right-index correction has been authored or run.
[Chinese review](WEAPON_TRIGGER_ALIGNMENT_V1_20261004_ZH.md).

Read HANDOFF, failure index, AN001–AN005, FP001, rejected coarse finger result,
V5 viewing record and V6 surface audit. The old hollow recalibration differs
only0.00218cm because it repeats the same rule. It is NOT a trigger-based fit
and does not disprove rifle-placement error. Retract the prior stronger cause
inference. Offline true surface crossings corroborate the screenshot, not their
cause. Source bytes and old evidence remain unchanged.

Recovery completed before fitting: canonical map2791b4a7...ad68519 restored
byte-exact; accidental map and V6 backed up. V6 saved rate remains unselected.
Current528 guards are `Evidence/ReloadIndexContactV6/map_recovery_v1/result.json`
`files`;527 prior records match and one V6 differs. All engines closed.

## Scope, storage, order

- Use the actual exported M1 triangles, unchanged owner FBX/native poses and
  existing hand-relative attachment. Identify the actual trigger/guard geometry
  from topology and inspected views; label ambiguous parts explicitly. No model,
  finger, weight, source-action, sleeve, camera, scale or transaction edits.
- A NEW `Evidence/WeaponTriggerAlignmentV1` / new source directory records
  current hashes, source copies, actual semantic contact landmarks and one
  trigger-derived rigid gun translation first. Keep original orientation/scale;
  do not reuse palm-hollow registration as the objective, sweep offsets or hide
  contact with camera movement. Compare before/after exact same poses/views.
- Readable side/opposite/top close-ups must show index/trigger, palm, thumb and
  other fingers together. Include support hand/whole rifle before declaring
  fit. Check start/operate/return/end and the natural native transition/movement
  only after the minimum fit proof passes. Gun position changes affect muzzle
  obstruction, so original ammo/lifecycle and near-wall tests are still required.
- Inspect Allied/German NPC weapon/hand/rig bindings separately. Reuse the
  contact definition, NOT one player's literal offset. Produce per-rig/weapon
  attachment parameters and coordinate changes with Lane B; do not modify its
  controller/BT/BB or overwrite shared native classes. NPC finding is included
  in this package, not authorization for unrelated AI.
- User confirms map/player saving was accidental and asks to restore formal
  map. With editors closed, preserve the accidental files, fetch only verified
  original map2791b4a7...ad68519 through existing pinned-host private SFTP if
  local immutable ACL denies reads, verify size/SHA then replace only that map.
  Retain V6's accidental saved rate as an unselected diagnostic change unless
  separately restored; formal map uses PlayerV1. Do not adopt the saved staging.

## Early checks / stop / rollback

First prove actual mesh identity/coordinate scale and trigger landmark. One
derived translation must visibly reduce finger-stock crossing and align with
the trigger WITHOUT unacceptable palm/thumb/other-finger/support separation.
If conflicting contact remains, record the conflict and stop this candidate;
do not conclude gun-only fitting generally impossible or silently edit fingers.
User reviews the spatial fit before further mechanism changes. Retain failed
and old candidates unchanged. All native authoring uses new names and guards;
no formal selection, Catalog/release/package/purchase/commit/push. Any required
bone change is deferred despite the preceding narrow finger permission.
