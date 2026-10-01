# Published SFTP asset baselines

## Current asset authority after Git migration

The 30 September user request authorizes removing asset/history/document binary bytes from the same Git repository and moving permitted material to private SFTP before public visibility. `CATALOG.json` selects and hashes current active manifests: the fully reverified working city, `historical-reference-assets`, `gunplay-reference-assets` and `project-document-assets`. Restore exact per-file `remote_path` locations; most new files use immutable `/objects/sha256/<prefix>/<hash>` objects. Historical asset bytes reuse the previously verified baseline where identical.

The new non-city manifests contain 77 files and 160,983,910 bytes: 38 historical files (128,227,229 bytes), 24 retained gunplay files (5,612,645 bytes), and 15 project/course document and generated-image files (27,144,036 bytes). Source links and exclusion hashes replace 20 unresolved historical source files and two unchanged supplier reference JPEGs; their original local copies are preserved, not shared. Code, Markdown, SVG/Mermaid, configuration and metadata remain in Git. This is storage verification, not engine acceptance.

Follow `../TEAM_SYNC_WORKFLOW.md` and run `Tools/check_asset_storage.py --local` with Python 3.10+ after staging/restoration. The old historical mirror below is provenance only; it no longer controls asset storage. Old release folders/manifests remain immutable private snapshots and must not overwrite the current selected versions. Public source does not provide private connection credentials or vendor license rights.

## Original 27 September publication record

Published on 27 September 2026 by Yupu Guo's authorized local publication task. Files were copied directly into the local SFTP service's storage; no source files were moved, deleted or overwritten. Exact byte hashes and restore paths are in the manifests below.

| Asset | Files | Bytes | SFTP directory |
|---|---:|---:|---|
| Original France Liberation Content | 15,850 | 28,421,951,358 (26.47 GiB) | `/baselines/france-liberation-content/d20260630-initial-20260927-222549/` |
| Rights-filtered historical reference mirror | 66 | 128,413,050 (122.46 MiB) | `/baselines/historical-reference-subset/initial-20260927-222549/` |

## Download and restore

Connect using the privately supplied SFTP host/account on TCP 22222. The client paths above are relative to the SFTP root; do not enter the server's Windows drive path.

1. Read the [team workflow](../TEAM_SYNC_WORKFLOW.md), protect local changes, select the intended Git revision and close editors holding affected files.
2. The original 27 September map manifest remains at `/releases/initial-20260927-222549/france-liberation-content.json` as an immutable snapshot. The [current map manifest](manifests/france-liberation-content.json) is selected by `CATALOG.json`, whose `release_manifest` names its matching SFTP copy; do not assume it equals the old snapshot. Restore exact recorded files into `Unreal/ParisStreetCombat/Content/`, preserving paths and external-actor packages. Do not rename packages or replace project configuration. The `.uproject` and Config come from Git; this is not a standalone complete project download.
3. The [old historical mirror manifest](manifests/historical-reference-subset.json) and `/releases/initial-20260927-222549/historical-reference-subset.json` describe the original private snapshot only. Current historical assets are SFTP-owned under the catalog's `historical-reference-assets` manifest; do not use the old mirror's `storage=git` fields as current ownership rules.
4. Compare every downloaded file's SHA-256 and size against the manifest before restoring it. Fetch only missing or changed files on later synchronizations. This initial map release contains the original delivery, not a claimed snapshot of any later edited working copy.

The historical copy includes team notes/catalogs, recorded public-domain/government reference images, three U.S. government manuals and two CC0 shoe-reference images. Twenty items were intentionally excluded: two Met Office PDFs, one weather-chart image, archived third-party webpages and provider metadata with unresolved item-specific sharing rights. Source links and catalog caveats remain available; see `excluded_files` in the manifest. Legacy galleries may therefore link to omitted items. Paris references remain links, and Normandy production notes remain inactive background.

## Verification and limits

- Source and server bytes were compared using SHA-256 and file sizes. Final file counts matched the inventories. Both manifests were also copied to the SFTP releases directory and hash-compared.
- A PowerShell 5.1 dictionary-sum error interrupted the first manifest write after map copying/verification. Recovery reused the final files without overwriting them, rechecked source/server hashes and successfully published both manifests. No partial version is presented as the completed release.
- This verifies files on the server filesystem. A teammate SFTP download, external forwarding test, Unreal import/play/packaging, and backup recovery were not performed by this task.
- Map sharing is based on the owner's explicit three-member license attestation in [RIGHTS.md](RIGHTS.md), not independent receipt review. Do not share these paths outside the authorized project team.
- Asset bytes stay outside Git. Local manifest/document changes require normal Git review/publication; this asset-copy task did not commit or push them. The SFTP copies are already available independently.

Do not edit these baseline folders in place. Publish later modified files as immutable hash objects and update the Git manifests through the team workflow.
