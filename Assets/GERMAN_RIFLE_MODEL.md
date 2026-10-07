# German rifle model — accepted static modeling baseline

Asset ID `german-rifle-model`; version `german-rifle-model-20261004-v1`.
On4October2026 Yupu accepts V15 modeling for use and confirms MW2 project use and
private three-member derivative sharing. No further appearance polishing is
planned. Rights record: [RIGHTS](Sync/RIGHTS.md#german-rifle-model-mw2-derived).

## What is supplied / supplied scope

- Editable packed Blender5.2.2 scene `Model/GermanRifle_FineWood_V15.blend`.
- Embedded-texture glTF2 binary `Model/GermanRifle_FineWood_V15.glb`.
- Selected actual source/fresh views, before/after comparison and technical
 reports in `Evidence/`. These are evidence, not additional game dependencies.
-24meshes/24,466triangles,14used materials/30primitives/36embedded PNGs,
 approximately1.1073m long, +X muzzle/+Z top in Blender, centered assembly root.
 Two wood-side map sets:4096×2048 stock /4096×1024 handguard. No Actions,
 operating rig or weapon-specific reload. Do not treat it as an animated kit.

Provenance: bounded adaptation of privately acquired MW2 SP-R receiver/bolt/
trigger/barrel parts, team-created wood/furniture/iron sights, and permitted
Allied M1 texture detail. It is not certified as an exact historical Kar98k;
modern donor differences remain documented. User modeling approval does not
establish UE import/lighting/mips/shimmer/FPS, collision/hand contact or gameplay.
Original M1, game city and current gameplay rifle are unchanged.

## Download / single working location

On this server the readable editable working bundle is:
`/workspaces/yg745/german-rifle-model-v1/` (SFTP client path).
Owner reservation is yg745; all three members have shared-account CRUD. Do not
edit simultaneously. This mutable location is NOT version authority.

For reproducible restoration, read the Catalog-selected
[manifest](Sync/manifests/german-rifle-model.json), or its private release copy
`/releases/german-rifle-model-20261004-v1/german-rifle-model.json`. Download each
`files[].remote_path` hash object to staging, verify exact SHA-256/size, then place
at `files[].path` relative to your clone with affected editors closed. Preserve
existing unique edits before placement. Do not download old rifle experiments
or the complete MW2/M1 sources just to open these self-contained model files.

The local model destination is
`Assets/LocalShared/SFTP/workspaces/yg745/german-rifle-model-v1/Model/`.
Run `Tools/check_asset_storage.py --asset-id german-rifle-model --local` using
Python3.10+ to verify the restored bundle. The current native-playtest restore
script intentionally restores only the runnable city/playtest; this optional
model must be selected/downloaded separately and is not in the selected UE
playtest. The4October unselected native integration/human-review candidate is
recorded in [UE result](../Docs/Development/GERMAN_RIFLE_UE_AND_ACTION_RESULT_20261004.md).

Future edits use this single workspace. Upload changed files as NEW immutable
objects/versions and update hashes; never edit an existing release/object or
unconditionally mirror deletions. No public model/texture binary redistribution.

## 中文速查

已认可的是静态枪模，非已绑定动作的UE枪械套件。SFTP打开
`/workspaces/yg745/german-rifle-model-v1/Model/`即可找到blend和GLB，贴图已打包。
`Evidence/`是实际效果图与验证记录。当前负责人yg745，三人都有增删改读权限，
但不能同时编辑。正式版本按Catalog/manifest逐文件哈希下载，不以可变工作区当版本。
现有试玩恢复工具不会自动下载或接入这把枪。10月4日已完成独立UE技术接入候选，
尚待人工持枪／动作复核和正式选择，见[中文结果](../Docs/Development/GERMAN_RIFLE_UE_AND_ACTION_RESULT_20261004_ZH.md)。
历史型号、专用动作／机械结构、接触和性能仍未完成。只限三人组内共享，不公开模型字节。
