# Intermediate storage cleanup — 9 October 2026

Completed: [actual result](INTERMEDIATE_STORAGE_CLEANUP_RESULT_20261009.md).

User explicitly requests packing and removing unused intermediate files because
disk space is running low. [Chinese review](INTERMEDIATE_STORAGE_CLEANUP_20261009_ZH.md).

Cases read: MI010 GPU startup failure, MI011 invalid recording content, MI012
packaged integration and MI013 rejected/missing-text HUD; also current HANDOFF
and the final G1/HUD results. Their raw logs, screenshots, failure records,
source snapshots and unique original assets remain retained. An exit code alone
does not establish a usable archive; readback must authenticate retained bytes.

The non-link-following survey identifies about198 GB in the two recent private
build roots. This attempt changes storage only. Keep the final hud_v3 and
instrument_v13 Archives, all three user trial folders, user saves, native assets,
source/FrozenSource, receipts, logs, images, cooked build inputs and published
history. Remove explicitly enumerated superseded Archive copies, two staging
copies and private Intermediate/Build caches. Do not remove any Project/Content
junction or traverse it. Old individual Archive paths become recoverable from
the cleanup manifest; historical receipts are not rewritten.

Before removal, hash every file from the superseded Archives/staging copies.
Equal content references an authenticated retained final Archive file; unique
program/config/launcher bytes go into a private ZIP. Read back every ZIP entry
and compare SHA256. Keep small compiler diagnostic metadata in that ZIP; record
regenerable object/PCH/cache files separately rather than storing another copy.
Provide a manifest-driven restore command for complete Archive/staging targets.
Never modify a retained baseline via hard links or writable junctions.

Early acceptance: no active UE/game/build process, all target absolute paths stay
within the two named tmp roots, no reparse point in a target or its ancestors,
all recoverable bytes authenticated, source758/protection703 exact. Stop before
deletion for any mismatch, unknown large unique cooked payload, occupied archive,
new active process or unexpected file change. Deletion uses native PowerShell
LiteralPath against the checked allowlist. Final checks cover retained identities,
source/guards, archive readback, removed-target inventory and actual disk space.
No game changes, launch, formal adoption, Git commit/push or remote publication.

Private cleanup records: Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/
Evidence/StorageCleanup20261009/run_v1. Tools/Archive/cleanup_intermediates_20261009.ps1
implements Prepare/Execute/Verify; restore_intermediate_archive.ps1 restores an
explicit manifest target to its old path without overwriting an occupied target.

Run these tools with the bundled PowerShell7 runtime named in HANDOFF. Example
restore target: `tmp/g1-playtest-revision-20261008/candidate_v10/Archive`.
`restore_intermediate_archive.ps1 -Target <recorded target>` copies each retained
or ZIP file and checks its exact size/SHA256. Restore is for inspection/recovery;
it does not authorize rerunning a stopped experiment or overwriting authoring
source. Intermediate/Build caches regenerate through a normal new build; retained
Intermediate/Source and Saved/Cooked inputs stay physically available.
