# Selected HUD development baseline and retired packages — actual result

9 October 2026. [Chinese review](HUD_BASELINE_RETIRE_PACKAGES_RESULT_20261009_ZH.md).
[Implementation plan](HUD_BASELINE_RETIRE_PACKAGES_20261009.md) records the user
authorization, MI012/MI013 and previous cleanup cases read, differences, early
acceptance and stopping conditions.

## Development starting point

The user selects hud_v3 as the basis for subsequent development. Follow
[the current selector](CURRENT_DEVELOPMENT_BASELINE.json) and
[its explanation](CURRENT_DEVELOPMENT_BASELINE.md). The preserved playable entry
is `tmp/Playtest-G1-HUD-20261009/PLAY_G1_REVISION.cmd`, executable SHA256
`497221422d7754d562b4e6d11fd8cc50c9223e40b329b26c8c14391a98d1c42b`.
Start feature work from the exact forty-file snapshot under
`Unreal/Variants/G1HUDPlaytest20261009/Project` or its matching writable Project
under `tmp/g1-playtest-revision-20261008/candidate_v3/Project`. This authoring
folder's older name does not make it disposable. Original models, finger poses,
weapon/ammunition behavior and checkpoint schema remain unchanged.

The older canonical source758/native359 release remains the asset-restoration
anchor. The selected UI/source does not imply a freshly built Editor binary:
HUD compilation was Game-only. Build from the selected source before editor work.
Other motion, camera, performance, second-machine, video and course gates remain.

## Actual removal and measured space

Execution finished at **15:16:52 EDT**, exit0. All eleven authorized generated
directories are absent: two older non-HUD user trials, instrument_v13 Archive,
2 October package_v3 Archive and canonical Saved/StagedBuilds, and six failed
instrument_v1/v2/v6/v7/v14/v15 Archives. Parent source, logs, images, receipts,
failure analyses and user checkpoints remain. Neither original assets nor
published SFTP release/object history were removed.

| Measured item | Actual value |
|---|---|
| Removed logical files | 527 files; 92,911,616,130 bytes /86.531 GiB |
| New deduplicated recovery ZIP | 829,475,151 bytes /0.773 GiB |
| Actual net D: free-space increase from before preparation | 92,082,651,136 bytes /85.759 GiB |
| D: free after removal | 409,453,182,976 bytes /381.333 GiB |

The net measurement includes the new recovery ZIP. It is distinct from logical
file sizes; the executor records actual drive free space before preparation,
immediately before removal and after verification. Deletion uses PowerShell7
LiteralPath and an independent eleven-path whitelist; absolute workspace bounds,
reparse points, complete path/size/time inventories and active process checks
pass before removal. No engine/game was launched or terminated.

## Recovery and preservation checks

Private `Evidence/PackageRetirement20261009/run_v1` contains the frozen plan,
preparation pin, unique ZIP, deleted-target receipt, result, final verification
and read-only recovery receipt. Recoverable G1 payloads were hashed before
removal. Unique ZIP members were streamed back and hashed; reused ZIP members
were actually read and checked. Only the obsolete 2 October success payloads
are retired as generated output without a bit-exact restoration promise.

Seven references in the previous immutable cleanup plan depended on the removed
instrument_v13 Archive. The explicit
[recovery override](PackageRetirementV1/RECOVERY_OVERRIDE_20261009.json) maps them
to authenticated members of the existing private V13 ZIP, whose SHA256 is
`760dbf44028acae9486c3ff9f5883715d5cf17a1c6fe338f65f20c8caecf9d01`.
This single historical ZIP is retained solely as a recovery dependency. The old
cleanup plan/result bytes are unchanged. The actual PowerShell restoration tool
passes `-Target tmp/mvp-closeout-20261008/instrument_v11/Archive
-VerifyRecoveryOnly`, reading every declared recovery byte and exercising all
seven overrides without creating a target. Restoring evidence does not authorize
rerunning stopped experiments.

Before/after verification passes the 758-file canonical contract, 703 current
guards, exact forty-file selected snapshot/authoring/delivery agreement and
current executable SHA. All fifty selected trial files and forty-seven current
HUD Archive files retain their frozen metadata/inventories. The selected local
ZIP retains its recorded metadata; the already verified SFTP distribution was
not changed. Saves under `%LOCALAPPDATA%/ParisStreetCombat/G1PlaytestV5` were
not opened, overwritten or moved.

The earlier storage result's instruction to retain both final Archives and all
three user trials is historical. This later explicit authorization removes only
the two obsolete trials and V13 Archive after recovery remapping. Keep the HUD
Archive, latest HUD trial/local ZIP, current authoring/cooked inputs and required
recovery ZIPs. Git remains at `79421db822c344a693a682f1af6bc3e40cfa0119`; this task
does not commit or push the new selection/cleanup documentation and tools.
