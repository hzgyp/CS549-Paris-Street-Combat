# GP010 — native weapon collision must be checked in PIE

4 October 2026. Integration package: `GERMAN_RIFLE_UE_AND_ACTION_REVIEW_V1.md`.
Private evidence is the single gameplay workspace's `Evidence/GermanRifleUEV1/`.
No commercial binary is stored here. Canonical map/release stays unchanged.

## Observed failure

`import_v3` imported 24,466 triangles and correct scale/muzzle frame. `author_v1`
compiled the new attachment Blueprint without graph errors. The source called
NoCollision on the initial CDO component before its final graph compile. In actual
fresh PIE `review_v2`, all three guns nevertheless reported
`CollisionEnabled.QUERY_AND_PHYSICS`, while unit scale and right-grip convergence
passed. This fails the explicit runtime collision gate. No physical blocking by
the gun was independently established, but the wrong effective mode is sufficient
to reject V1. Import/header/compilation or pose metrics cannot replace this check.
The exact compiler/profile/CDO cause was not isolated; do not assert one as fact.

V1 remains at `/Game/ParisCombat/Weapons/GermanRifleUEV1/BP_PC_GermanRifleAttachmentV1`,
unselected, SHA `a8f780587b69403a91bc6f512ab0214086d6c0d2903223d72e9e001ae30342ed`.
Do not overwrite or select it. The author source snapshot and failed report stay
at `author_v1/source.py` and `review_v2/result.json` in the private evidence root.

## Changed hypothesis / bounded correction

Build separately named V2. Apply default collision/profile settings after final
compile and explicitly call standard Actor SetActorEnableCollision(false) at
native BeginPlay. No source geometry, hand, animation, camera, ammo or map change.
Fresh-load and verify effective collision on all three actual instances, in idle,
walk and reload; stop if it still fails. Later result records govern acceptance.

## Associated harness failures

- Preflight initially assumed source motion guards had a stored size. They had
  SHA only; exact SHA verification now precedes recording actual size. The first
  task-owned engine was stopped during initialization before native import.
- `unreal.duplicate_object` was unavailable; use installed AssetTools duplication
  into a new private pipeline package, never change the engine-default asset.
- Editor labels were `PC_City_Enemy*`, not `PC_City_German*`; select known team
  character classes plus TeamId, still requiring exactly three unarmed instances.
- LoadedAmmo is protected on instances. Do not unlock/edit it for a test. Use
  original reset values; if necessary consume one round through the real shot
  interface, then invoke the existing reload request.

These errors are preserved, not counted as completed motion/reload tests. Engine
exit 0 alone was not acceptance. Existing input/body visual and historical/runtime
gates remain separate. Prior original files and accepted V15 bytes are protected.

## Later measured result and additional harness limitations

V2's actual `review_v3` has29samples/87actor records, allNoCollision. Maximum scale
deviation2.68221e-7 causes the strict equality raw summary to fail; preserve it.
Independent `review_validation_v1` uses declared1e-6 tolerance and passes without
editing raw evidence or geometry. Seven images are inspected, but early/mid
rendered poses appear repeated despite differing bone snapshots and recovery is
foreground-obstructed. Do not call those matched-phase reload/contact approval.

Combined combat_v1 retains three failed unarmed-negative assertions: the subject
now has WeaponAppearance, so actual fire consumes a round. The narrowly adapted
test-only v2 clears that reference for one negative call and restores it in
finally;16cases66assertions pass, exit0/clean matched error search. Source gameplay
graph/ammo logic unchanged; no NPC AI/auto-fire implemented. Read the paired
`GERMAN_RIFLE_UE_AND_ACTION_RESULT_20261004.md` / `_ZH.md` for human-review stop.

## 中文结论

导入面数／比例、蓝图编译和握点数值都对，仍不能推断枪碰撞已关闭；必须读实际
PIE实例。V1实际报告QUERY_AND_PHYSICS，所以拒绝。另建V2，在最终编译后设置
默认值，并在原生BeginPlay明确关Actor碰撞；重新实测而非靠脚本字段宣称成功。
碰撞默认失效的具体根因未单独确证。禁止修改受保护弹药字段来造测试条件。
