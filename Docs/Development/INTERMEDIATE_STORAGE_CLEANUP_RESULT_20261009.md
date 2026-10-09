# Intermediate storage cleanup — actual result

9 October 2026. [Chinese review](INTERMEDIATE_STORAGE_CLEANUP_RESULT_20261009_ZH.md).
[Implementation plan](INTERMEDIATE_STORAGE_CLEANUP_20261009.md) records the user
authorization, MI010–MI013 cases read, bounded differences and early/stop gates.

## Space and retained material

Removed26 explicitly listed private targets:15 superseded Archives,2 duplicate
StagedBuilds copies and9 Intermediate/Build caches. No Project/Content junction
was followed or removed. All1,446 removed file rows are recorded:727 packaged
files are fully recoverable,486 small compiler metadata files are also archived,
and233 rebuildable cache files regenerate through a new build.

| Measured item | Actual value |
|---|---|
| Removed logical files | 170,374,532,920 bytes /158.674 GiB |
| Unique ZIP | 2,427,851,267 bytes /2.261 GiB;256 SHA256-readback entries |
| Actual net D: free-space increase, after archiving | 167,947,878,400 bytes /156.414 GiB |
| D: free after deletion | 334,340,759,552 bytes /311.379 GiB |

Space receipt timestamp:10:37:08 EDT. GiB matches the usual Windows displayed
capacity convention; the raw byte values distinguish net space from logical
file size. A fresh final drive inventory agrees within8 KiB of the receipt.

Keep the final hud_v3/instrument_v13 Archives and all three user trial folders;
208 recorded trial-file metadata/entry identities remain exact. Saves, authoring
source/FrozenSource, cooked build inputs, failure logs/images/source, original
commercial assets and published history remain retained. The HUD trial still
starts from tmp/Playtest-G1-HUD-20261009/PLAY_G1_REVISION.cmd.

## Verification and recovery

Every removed packaged file was hashed before deletion. Equal bytes reference
retained final Archive files; unique bytes use ZIP entries. All256 ZIP entries
were streamed back and SHA256 checked. Post-removal53 retained reference files
were fully rehashed; canonical758-source/703-protection checks pass before/after,
and40 current private authoring source files match the HUD delivery. All26 targets
are absent. Path gates reject workspace escape, formal assets, the actual Content
junction, both retained final Archives and authoring source. Execute exits0.
Fresh process inventory finds no Unreal/game/build process; none was launched or
terminated. Git HEAD remains b8a3a6a1ba1f730730be23f6fa1d801787d58165; no commit/push.

Private Evidence/StorageCleanup20261009/run_v1 contains plan.json, ZIP,
result.json, deleted_targets.json, safety_gate.json, final_verification.json
and a Chinese recovery README. Restore a declared Archive/staging target with
Tools/Archive/restore_intermediate_archive.ps1 using bundled PowerShell7. It
copies and checks exact bytes without overwriting an occupied destination.
Keep the two final Archives because the recovery manifest references them;
migrate and authenticate those references before a later cleanup of those bases.
Historical build/failure receipts are unchanged; removed old Archive paths now
require recovery before direct inspection. Restore does not authorize replaying
stopped experiments. Next compilation may take longer as caches regenerate.

The preparation console initially reported0 GiB because Measure-Object did not
read OrderedDictionary fields; the full plan always recorded the correct bytes.
An independent raw-row sum verifies158.674 GiB and matching1,446 file totals;
explicit Int64 accumulation corrects reporting before deletion. No target or
archived bytes changed for that correction. Cleanup establishes storage integrity,
not new gameplay/performance/human/course acceptance or formal asset adoption.
