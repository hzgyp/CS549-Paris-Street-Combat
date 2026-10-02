# Paris Street Combat - SFTP directory guide

English original and synchronized Chinese guide. Updated: 1 October 2026.
This is a directory guide, not an asset release manifest or a runtime acceptance report.

## English

| Directory | Contents | Use |
| --- | --- | --- |
| `baselines/` | Preserved original deliveries and historical baseline snapshots. | Recover or inspect originals. Never edit them in place. |
| `workspaces/<owner>/` | Editable working trees for accepted assets. They may include unfinished or unpublished changes. | Development by the reserved binary owner; not an authoritative release download. |
| `objects/sha256/<prefix>/<hash>` | Immutable per-file asset version bytes, addressed by SHA-256. Names may have no original extension. | Download only objects selected by the Git manifests; restore their recorded filenames/paths. Do not rename or reorganize objects manually. |
| `releases/<version>/` | Published version manifests: filenames, restore paths, sizes, hashes and dependencies. | Select the matching release through the Git catalog. These are manifests, not complete model packages. Keep old snapshots. |
| `incoming/` | Incomplete or pending-verification SFTP transfers. | Temporary upload staging only. Never restore from it or reference it in a published manifest. |

Common paths on this server:

- Original Paris city: `baselines/france-liberation-content/`.
- Preserved soldier/action deliveries: `baselines/character-original-intake/character-20261001-v1/`.
- Character compatibility/repair lab: `workspaces/yg745/character-ue582-v1/`.
- Active Paris gameplay asset workspace: `workspaces/yg745/paris-gameplay-v1/`.
- `workspaces/yg745/character-intake-20260930` is an alias to the preserved original baseline, not another editable copy.
- `baselines/historical-reference-subset/` is an older reference snapshot. Current history, document and gunplay versions are selected by the Git catalog, not this folder alone.

New deliveries physically start in the owner's local `Assets/LocalWorking/Intake/`, with processing/testing in LocalWorking. After the defined asset checks and sharing-rights gate pass, migrate originals and usable dependency-complete outputs to their appropriate SFTP locations, verify retained sizes/SHA-256 and final SFTP bytes, then remove only redundant LocalWorking material. Keep an alias only if a tool/editor needs it. Preserve originals, unique edits and release history.

For team synchronization, first select the intended Git revision and read `Assets/Sync/CATALOG.json` plus its active manifests. Download only missing/changed files from their exact `remote_path`; verify SHA-256/size and restore the recorded paths with affected editors closed. Preserve unsynchronized local changes. At work end, upload and verify new immutable versions before publishing matching Git manifests. Follow `Assets/TEAM_SYNC_WORKFLOW.md` in the source repository.

All published shared asset areas grant team read/create/change/delete access, but editing reservations and immutable-version procedures still apply. Do not concurrently edit the same binary or overwrite/delete published originals/versions. The SFTP chroot root and its service files remain protected; shared CRUD does not grant root or ACL administration. `.cs549-sftp-root`, `HOST_KEY_FINGERPRINT.txt` and `SERVER_STATUS.json` are service/identity/status files, not assets. Verify the server fingerprint when connecting; do not edit these files to resolve connection issues.

## 中文使用说明

目录按存储用途划分，不按地图、人物、动作分类。

| 目录 | 放什么 | 怎么用 |
| --- | --- | --- |
| `baselines/` | 保留不改的原始交付和历史基线快照。 | 查原版、恢复原版；不要直接编辑。 |
| `workspaces/<owner>/` | 已接收可用资产的可编辑工作目录，也可能含未完成、未发布的修改。 | 按已协调的二进制负责人开发；不能把这里当正式版本下载源。 |
| `objects/sha256/<前缀>/<哈希>` | 按 SHA-256 命名的不可变文件版本，可能没有原来的扩展名。 | 按 Git 清单下载，恢复清单中的文件名和路径；不要手工改名或整理。 |
| `releases/<版本>/` | 发布清单：文件名、恢复路径、大小、哈希、依赖。 | 通过 Git 目录索引选择对应版本；这里不是完整模型包，旧快照应保留。 |
| `incoming/` | 未传完或尚未核验的 SFTP 上传。 | 只作临时上传中转；不能用于恢复，正式清单不能指向这里。 |

常用位置：

- 巴黎大地图原版：`baselines/france-liberation-content/`。
- 原始士兵和动作：`baselines/character-original-intake/character-20261001-v1/`。
- 角色兼容性/修复测试工程：`workspaces/yg745/character-ue582-v1/`。
- 当前巴黎游戏资产工作区：`workspaces/yg745/paris-gameplay-v1/`。
- `workspaces/yg745/character-intake-20260930` 是原始基线的路径别名，不是第二份可编辑副本。
- `baselines/historical-reference-subset/` 是较早的资料快照；当前历史资料、文档和枪械参考版本以 Git 目录索引为准，不能只看该目录。

新下载的原始资源实体先放自己本机的 `Assets/LocalWorking/Intake/`，处理和测试也在 LocalWorking。通过约定的资产验证及授权共享门槛后，将保留的原始交付和可用的完整依赖输出迁入对应 SFTP 位置；核对保留文件的大小、SHA-256 和最终 SFTP 文件后，再清理 LocalWorking 的冗余内容。工具确实需要旧路径时才留链接。不能删除唯一原件、未同步修改或必要的版本历史。

组员同步前先选择 Git 版本，读取 `Assets/Sync/CATALOG.json` 和其中的有效清单。只下载缺失/变化的文件，按准确的 `remote_path` 取文件，核对 SHA-256 和大小后，在相关编辑器关闭时恢复到清单指定路径；先保护未同步的本地修改。结束工作时先上传、核验新的不可变版本，再发布对应 Git 清单。完整操作遵循源码仓库中的 `Assets/TEAM_SYNC_WORKFLOW.md`。

已发布的共享资产区给组员增删改读权限，但仍须遵守二进制编辑负责人和不可变版本规则：不要同时改同一个文件，不要覆盖或随意删除已发布的原件和版本。SFTP 根目录及服务文件保持受保护，共享增删改读不包括根目录或权限管理。`.cs549-sftp-root`、`HOST_KEY_FINGERPRINT.txt`、`SERVER_STATUS.json` 是服务标记、身份指纹和状态，不放模型；连接时核对指纹，不要为排查连接问题随意改这些文件。
