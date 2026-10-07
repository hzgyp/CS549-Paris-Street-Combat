# Existing reload/recoil attempt result

4 October 2026, owner yg745. [Chinese review](WEAPON_ANIMATION_REUSE_RESULT_20261004_ZH.md).
[Plan](WEAPON_ANIMATION_REUSE_V1.md); [AN001](../../Failures/AN001-20261004-existing-weapon-animation/FAILURE_ANALYSIS.md).

## Outcome

Duplicate delivery marked. **No usable reload replacement or recoil fix completed.**
D059 failed actual first-person visual acceptance. Both recoil-owner authoring
attempts crashed before saving a native owner package. Stop this mechanism under
the plan's boundary: no further offsets, sleeve masks, camera edits or new motions.
Canonical map, protected models/fingers/actions, gun transactions and Catalog
remain unchanged. No commit/push or immutable publication.

Rifle_Reload_2 is withdrawn from the failed candidate's executable request only.
The formal route still references its original shared parent/published restore
dependency, so no commercial original was physically deleted. Retaining that
dependency does not override the user's appearance rejection. The failed candidate
is not adopted.

## Actual work and evidence

All298 native motion files and SourceFiles.zip match the old RifleAnimsetPro by
size/SHA. DUPLICATE.md now marks the receipt, with catalog11.2 updated. Downloads
retained; no duplicate import/upload. Character/deformation workflow required
same-target visual checks; no new keyframes or generated motion were authored.

| Identity | Actual result | Limit |
| --- | --- | --- |
| audit_v1 | Read-only native audit, exit0; parent references, poses and clip properties | Not visual acceptance |
| retarget_v1 | One native FK/pelvis retarget;4.133333s;30 original finger-local tracks restored, sampled max delta2.07e-7;4 new packages | Not sleeve/contact acceptance |
| author_reload_v1 | New child overrides PC_RequestReload; inherited transaction/lifecycle intact;1 package | Not map selection or full regression |
| reload_views_v1 | Failed freezing/capture attempt, retained even though engine exit0 | Cause not fully isolated |
| reload_probe_v1 | Transient editor request enters Reloading; duration/3.95s proposal correct | Not PIE functional coverage |
| reload_views_v2 | Six matched frozen actual-city PIE images inspected, exit0 | Actual visual failure; not continuous/walking acceptance |
| author_owner_v1/v2 | BlueprintEditorLibrary access violations, both exit3, no result/native owner on disk | No recoil validation/fix |

Valid reload positions .406/1.214/2.235/3.426/3.987 seconds remain Reloading. Last
capture observes ammo2/16→8/10, timeout count0. This one sampled transfer is NOT
full interruption/death/reset/conservation regression.3.95s is a conservative
generic completion proposal, not M1 clip insertion. Functional script prepared
but never run.

Ordinary holding is readable. Take/operate/return severely obstruct the view;
operate/complete show stretched triangular sleeve surfaces. Exact deformation
cause is unproved. Unchanged bytes do not imply good deformation.

![Rejected operating phase](../../Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/WeaponAnimationReuseV1/reload_views_v2/reload_operate.png)

Private evidence only; images are not public Git content. Holding and five reload
images live in the same private evidence directory.

## Recoil and next boundary

Owned Rifle_ShootOnce exists (.8s): generic source motion is not missing.
Rifle_ShootLoop_Additive actually reports AAT_NONE, despite its name. Attempted
native owner binding observes accepted ShotSequence, reuses ShootOnce and retains
holding FramingT so normal aim fitting does not cancel recoil. No camera shake,
gun/ammo rule change or runtime Python update.

Cross-compile stale pins were a V1 hypothesis. V2 compiles complete helpers in
dependency order and discards old handles, but crashes in BlueprintEditorLibrary
after the holding helper compiled. This correction does not prove the cause.
Stop this graph-authoring pattern; no third retry, engine patch or bridge enablement.
A future package must document a different native binding mechanism and prove
its smallest isolated graph before integration. Reload may separately assess
compatible mature upper-body composition; no low-pose clip was selected, no
low-pose restrictions lifted, and no purchase is authorized.

NPC reload, sprint separation, prone sling, trigger fingers and VFX remain open.

## Preservation

All507 protected prior files unchanged. Canonical map SHA
2791b4a7f76b4b3d07f42286b6ad0156c3a185c2e3e795fa2446aaac0ad68519.
Five failed native drafts remain in the single writable SFTP workspace, unselected
in [inventory](../../Assets/Integration/WEAPON_ANIMATION_REUSE_DRAFT_INVENTORY_20261004.json),
not Catalog/automatic restore authority. No distributable recoil or release.
Five exact new drafts have named shared-account Modify, root ACL unchanged; no
new authenticated remote CRUD test.
Images/logs/source snapshots/two crashes retained in place under AN001 manifest,
without duplicate large-asset copies. Launcher is stop-locked. All task engines
ended. Read AN001 and FP001 before future work; never overwrite occupied identities.
[Closeout verification](../../Failures/AN001-20261004-existing-weapon-animation/VERIFICATION.md)
records62 evidence hashes,507 protected files, syntax/links and exact-file access.
