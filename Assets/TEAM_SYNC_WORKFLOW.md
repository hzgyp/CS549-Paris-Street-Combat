# Team synchronization: GitHub + SFTP

Decision date: 27 September 2026; explicit existing Git/LFS asset migration authorized on 30 September. Applies to all three members and development agents in Paris Street Combat. Integration owner: Yupu Guo. The same repository becomes a public source repository only after asset byte removal, matching verified private SFTP manifests and publication checks. Older keep-LFS-history planning notes are superseded for this authorized migration.

## 1. Storage rules

| Material | Authoritative storage | Rule |
|---|---|---|
| Code, scripts, configuration, Markdown/document sources and SVG/Mermaid diagrams | GitHub | Commit normally; inspect staged content before publishing. PDF/DOCX/PPTX and raster outputs are SFTP bytes, not source exceptions. |
| Models, textures, animations, audio, archives, environment packages, research source bytes, document binaries and raster illustrations | Private SFTP | Store permitted original/changed bytes outside Git regardless of size; Git records paths/hashes/versions/rights. Unresolved-rights material stays local-only with source links. |
| Asset version catalog, SHA-256, sizes, restore paths, dependencies and ownership | GitHub: `Assets/Sync/manifests/<asset-id>.json` | One manifest per logical asset/dependency group; the selected Git commit determines exact versions. |
| Existing Git/LFS assets | Private SFTP after verified migration | The 30 September request authorizes removing their tracked bytes and rewriting asset history in this repository. Preserve private backups and local originals. No new asset bytes or LFS pointers enter public source. |
| Caches, editor autosaves, credentials, private keys, temporary transfers | Local, ignored | Not part of a shared source release. Back up valuable unfinished work separately. |

Routing convention: model/source-asset bundles and PDF/DOCX/PPTX/raster outputs use SFTP even when small. Markdown, code, SVG/Mermaid, configuration, catalogs, sources and hashes remain in Git. Small team-authored Unreal Blueprint logic is code, not a blanket model exception: register its exact path/owner/kind in `Sync/GIT_CODE_ALLOWLIST.json` before staging, with a 10 MiB source-code cap. Do not whitelist purchased assets, meshes, animations or archives. Existing retained gunplay binaries are migrated together as a reference dependency group. Binary code still needs one named editor.

Store downloaded model sources under ignored `Assets/LocalWorking/` by default. Restore runtime assets and document binaries to their exact manifest paths. Before publishing a new managed path, verify its ignore rule. Do not blanket-ignore all Blueprints. Ignore rules alone do not remove previously tracked bytes/history; the explicitly authorized migration verifies SFTP and backs up history before removal.

Vendor rights remain a prerequisite. A private server, modified texture or existing local copy does not grant redistribution permission. Record source/license and permitted recipients before sharing originals or derivatives. Unknown rights block upload; use an entitled acquisition route instead. Preserve the original vendor package. Do not revive the archived Normandy project to publish its assets.

## 2. Connection and current evidence

- Protocol: **SFTP over SSH**, not FTP/FTPS. Port: **TCP 22222**. The user reports external 22222 forwarding to local 22222 and successful SFTP use; no passive FTP port range is required.
- The local `sshd` service was observed running with automatic startup and IPv4/IPv6 listeners on 22222 during this update. The configuration identifies account `cs549sftp` and the chroot below. This is a local observation, not a new external connectivity or upload test.
- Server filesystem root: `D:\0.Rutgers\CS549\Project-New\Assets\LocalShared\SFTP`. Clients see `/`, not that Windows path.
- The 25 September permission report records writable child directories `/baselines`, `/incoming` and `/objects`. The root remains non-writable. Child Modify permission permits creation, replacement, rename and deletion without granting ACL administration. This update did not retest those permissions through a teammate login or inspect the live asset catalog.
- Obtain the current host/IP, login secret and server host-key fingerprint privately from Yupu. Verify the fingerprint before first connection; stop on an unexpected change. Never commit passwords/private keys or disable host-key checking. Do not put passwords in command arguments. Shared-account use still requires a named human owner in manifests; individual accounts can be introduced by the administrator separately.
- The server must be powered on, reachable and have enough free space. If its public address changes, obtain the updated endpoint privately. Never weaken permissions or expose FTP to work around an outage.

Client setup: choose SFTP, enter the privately supplied host, port 22222 and account, then verify the host fingerprint. Use `/incoming` for incomplete transfers. Do not enable automatic two-way mirroring, deletion propagation or unconditional overwrite. Git cannot see ignored local asset changes.

The root is deliberately protected. The current development shell could not enumerate it; that is not evidence that authenticated SFTP access is broken. Do not relax the root ACL just to make Git or an editor traverse it. `Tools/configure_cs549_sftp_permissions.ps1` is an administrator maintenance tool, not a daily synchronization command.

## 3. Version contract: hashes in Git, bytes in SFTP

`Sync/CATALOG.json` selects the current authoritative manifests and pins their SHA-256. Read only those active entries for restoration; the old `historical-reference-subset.json` is pre-migration provenance, not a competing storage owner. Before adopting another existing upload, verify bytes/rights and record its manifest. Do not rename/delete unknown server data automatically.

- `/baselines/<asset-id>/<version>/...`: preserved original deliveries, immutable by team policy. For large baselines, prefer a per-file inventory so one changed texture does not require replacing a whole archive.
- `/objects/sha256/<first-two-hash-characters>/<full-sha256>`: new or changed file bytes, immutable by team policy. Reuse an object only after verifying that it matches. These directories may be created inside the existing writable child directory as needed.
- `/incoming/<owner>/<unique-transfer-id>/...part`: incomplete uploads. Never reference these in a published manifest. Only clean up your own confirmed abandoned transfer; do not remove teammates' work.

For each logical asset, create a JSON manifest in `Assets/Sync/manifests/` during its first actual publication. This documentation change intentionally does not create an empty catalog and label it synchronized. Required information:

| Field | Meaning |
|---|---|
| `schema_version`, `asset_id`, `asset_version`, `owner`, `published_at` | Schema version 1, stable asset ID, unique release label, named editor/publisher and timestamp with offset. |
| `source`, `license_record`, `sharing_status` | Provenance and a non-secret entitlement reference; publication requires verified permission for the recipients. |
| `dependencies` | Other asset IDs and exact versions; list required plugins/engine compatibility separately if relevant. |
| `files` | Complete file inventory for this asset version, not just this day's changes. |
| `files[].path` | Exact workspace-relative restore path using `/`; no absolute paths, `..`, or paths outside the workspace. |
| `files[].storage` | `sftp` or `git`; a restore destination must not have two competing storage owners. |
| `files[].size_bytes`, `files[].sha256` | Exact byte length and lowercase 64-character SHA-256 of actual file bytes. |
| `files[].remote_path` | For SFTP files, an immutable baseline or hash-object location; never `/incoming` or mutable `latest`. |
| `files[].mirror_remote_path` | Legacy pre-migration field only. Current SFTP-owned assets use `remote_path`; never select an old mirror manifest instead of the active catalog. |
| `verification` | Method, verifier and time of remote-byte verification; runtime/import validation is a separate result. |
| `retired_paths` | Explicit paths removed/replaced since the previous version, with reason; review before local cleanup. |

Do not include secrets or raw purchase receipts. Historical migration/vendor manifests remain evidence of the original copy, not the current edited version. A release catalog must include unchanged required files as well as changed ones; dependency closure is not established by uploading only the visible model. No two manifests may claim conflicting versions at the same restore path.

The owner's France Liberation sharing attestation and the historical subset's item-selection rules are recorded in [Sync/RIGHTS.md](Sync/RIGHTS.md). Check the actual publication manifests before assuming a file has been copied. A rights-filtered historical mirror may omit source webpage snapshots and images while retaining their source links; inspect its `excluded_files` list.

Use a local SHA-256 and size check for each saved file. For example, replace this illustrative path with a real asset path:

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath 'Assets/LocalWorking/example/model.glb'
(Get-Item -LiteralPath 'Assets/LocalWorking/example/model.glb').Length
```

Verification means hashing the remote bytes via a trusted administrator check or downloading to a separate staging file and matching SHA-256 and byte length. A successful transfer dialog or equal file size alone is insufficient. This account is SFTP-only; do not assume SSH shell hashing is available. Check the final published object before committing its reference.

Example: changing one standalone texture requires a new object for that texture and an updated manifest entry; unchanged model files keep their previous hashes. If the texture is embedded in a `.blend`/GLB or Unreal package, transfer the entire changed file and any affected dependent packages. This is file-level incremental synchronization, not block-level delta transfer. SFTP itself does not provide version history or merging.

## 4. Mandatory start-of-work checklist

1. Confirm this workspace, the intended branch/revision and the named owner of the files you will edit. Reserve binary ownership with the team before editing; a local manifest edit is not a distributed lock. Shared write permission does not prevent collisions.
2. Inspect `git status --short --branch`. Also compare local external assets against the last restored manifests by hash: ignored files do not appear in Git status. Save and separately preserve unfinished asset edits before any restore. A Git stash alone does not preserve ignored models.
3. Fetch Git updates and integrate the intended revision only after preserving local work. Use a fast-forward update when applicable; stop on divergence or conflicts and coordinate with Yupu. Never use a hard reset, clean command or forced overwrite as a synchronization shortcut.
4. Read the manifests at that revision. Resolve required asset versions, rights and dependency closure. Download only missing or different files into an ignored staging directory; do not modify the active Content tree mid-transfer. If a manifest is absent/incomplete, obtain the entitled baseline and record the missing synchronization work; do not guess `latest`.
5. Verify every required staged file's hash and size. Close Unreal/Blender or other editors holding affected files. Back up conflicting local files outside the restore target, then restore only verified files to their exact paths. Review `retired_paths` explicitly; never delete unlisted files automatically. Preserve Unreal package identities and external-actor/object layout.
6. Confirm local assets match the active catalog's manifests and required source/configuration is present. Use `python Tools/check_asset_storage.py --local` with Python 3.10+ (or the bundled runtime), optionally selecting `--asset-id`. Record revision/versions. Only then edit affected assets. Report missing files/hash/ownership conflicts.

## 5. Mandatory task/end-of-day checklist

1. Save work and close affected editors. Compare against the starting manifests, including new textures/materials/rigs and changed dependency packages. Distinguish completed releases from unfinished local experiments. Keep one owner until handoff completes.
2. Check sharing rights, destination ignore rules and source provenance for every new asset or derivative. Register new originals through Section 6. Do not stage the local SFTP store or force-add ignored assets.
3. Hash the final saved files and record byte lengths. Upload only new/changed files to a unique `/incoming` location; leave published baselines/objects untouched. Verify uploaded bytes, then promote them to their immutable final location and verify that final object. If it already exists, verify/reuse it instead of overwriting it. Broken transfers remain unpublished.
4. Update the Git manifests with the full current inventory, exact remote locations, dependencies, owner, rights reference and verification record. Commit related code/configuration and manifests together where needed for compatibility. Check staged paths and sizes; no secrets, large model bytes or unavailable object references may enter the change.
5. When publication is authorized for the task, commit/push Git only **after** final SFTP objects are available and verified. A normal code-only change does not require re-uploading unchanged assets. Documentation editing alone is not permission for an agent to push or transfer assets.
6. Hand off the Git commit/branch, asset IDs/versions, changed paths, verification method, actual import/runtime test results, remaining work and ownership release. A teammate confirms restoration before dependent integration. Do not claim transfer success establishes engine compatibility.

If SFTP fails, keep the working files and a local draft manifest; do not publish references to incomplete uploads or move the bytes into Git as a workaround. If Git push fails after upload, retain the verified objects and local commit, coordinate integration, and retry Git publication when authorized. Unreferenced uploaded objects are safer than references to missing bytes. At day end, explicitly report any unpublished work and keep its ownership reserved.

## 6. New assets and original baselines

1. Assign a stable asset ID and owner. Record source, version, license/team-sharing scope, intended use and required engine/plugin/rig dependencies in the asset register and manifest. Apply historical/compatibility gates separately; storage availability is not acceptance.
2. Preserve the original delivery unchanged. Upload it once to a unique baseline location only if sharing is permitted. Inventory and verify every required file, or document an archive's hash plus the extracted-file inventory and restoration procedure. Do not substitute a single archive hash for later edited-file versions.
3. Work on a separate local copy. Publish changed files to hash-addressed objects, with manifests selecting baseline bytes for unchanged paths and new object bytes for modified paths. Do not edit the served baseline as your working copy.
4. Stage a teammate restoration and confirm paths, hashes and dependency completeness before calling that version synchronized. Record import/runtime results only after actually running those checks.

This applies equally to historical/reference assets, incoming purchased models, new permitted team-authored assets and Unreal-ready derivatives. Assets retained from the archived project still require provenance and rights review; do not republish the archived repository itself.

## 7. Conflict, rollback and backup

- Binary conflict: preserve both versions under distinct local/remote draft identities, stop editing that asset and let Yupu coordinate a chosen version or deliberate adaptation. Do not use last-upload-wins or claim Git can merge models.
- Rollback: select a previous Git revision and restore the exact objects referenced by its manifests after protecting current work. Review retired paths; changing a manifest does not automatically remove stale local files. Never roll back only the code while retaining incompatible new asset bytes.
- Retention: keep immutable originals and all published objects referenced by retained branches/releases. No automatic remote pruning. Removal requires owner review, reference checks, a verified backup and explicit authorization.
- SFTP is distribution, not backup. Its shared account can delete writable child content, so immutability is currently procedural, not enforced object-lock storage. Maintain a separate backup of baselines, published objects and valuable unfinished work; test recovery. This update does not claim such a backup exists.
- Tools: `Tools/check_asset_storage.py` verifies active catalog metadata, local hashes or administrator server bytes and checks Git/staged/history asset exclusions. `Tools/configure_git_hooks.ps1` installs local pre-commit/pre-push guards with a selected Python 3.10+ runtime. Upload/download, ownership and restoration remain manual; the checker is not an automatic downloader, lock service or binary merge tool. Never bypass a failed guard to reintroduce asset bytes.

## 8. Rejoin after the authorized history rewrite

Do not merge or push an old clone into the rewritten branch. Save uncommitted code separately and back up ignored asset edits; clone the same repository into a new sibling folder without deleting the old checkout. Follow the new catalog, restore only missing/different permitted SFTP files to staging, verify hashes and preserve conflict versions before placement. Reapply reviewed source changes as new commits, not an old-history merge. Configure guards with `Tools/configure_git_hooks.ps1`, then run the metadata/Git and local-asset checks. Keep old Git/LFS backups private and outside the new repository. This document is the teammate handoff; no messages are sent to teammates automatically.

Public source access does not grant access to private SFTP or redistribute vendor Content. Authorized team members obtain the endpoint/account privately. External reviewers need entitled dependencies or a separately licensed packaged build. The repo alone is not the full city or runnable game.
