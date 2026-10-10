# Select the HUD development baseline and retire obsolete packages

9 October 2026. [Chinese review](HUD_BASELINE_RETIRE_PACKAGES_20261009_ZH.md).
Authorization: the user selects the latest local HUD version for future development
and permits removal of previous unused packaged versions.

## Cases read, change and early acceptance

Read HANDOFF, Failures index, MI012 missing player capabilities, MI013 rejected HUD/
missing Canvas text, the HUD publication result and the prior storage cleanup/
restore contract. This attempt selects tested hud_v3 as the active functional and
visual development base. It does not modify its code, original models, finger
poses, gun/resource/save logic, map or native assets, and does not rerun an engine.
Selection is explicit in CURRENT_DEVELOPMENT_BASELINE.json and session entry docs.
The exact forty-file published source is the immutable starting snapshot; the
existing matching private Project is the active writable authoring workspace.
The old canonical source/native release remains a protected asset restoration
anchor, not the starting gameplay/HUD code for future feature work.
The selected Game executable is verified; its changed source was compiled for
Game only. Cached Editor binaries do not establish this HUD in the editor. A
later editor entry must build from the selected source and verify the result.

Early gate: current HUD executable hash49722142…d1c42b, fifty current trial files,
forty published and forty authoring source identities, canonical758 and protected
703 identities all pass; affected game/editor/build processes must be absent.
Retain the latest extracted trial, HUD Archive, selected local/SFTP ZIP, native
Content, current authoring/cooked inputs and every source/log/image/save record.
User selection supersedes pending UI-baseline review only; it is not whole motion,
performance, second-machine, natural combat, video or course acceptance.

## Exact retirement scope

Retire eleven explicitly named generated directories after a frozen file inventory:
old8October and9October non-HUD trial folders; instrument_v13 Archive;
2October package_v3 Archive and canonical Saved/StagedBuilds; six archived failed
instrument_v1/v2/v6/v7/v14/v15 package Archives. Do not remove their parent source,
build receipt, logs, images or failure analysis. The user authorization supersedes
earlier keep-old-trial/Archive snapshots only for these generated directories.
Repository clones' unrelated Archive folders and all published SFTP history are
excluded. Reject reparse points, unexpected paths/files or active writers.

Recover old valid/failed G1 bytes through the existing verified private V13 ZIP,
retained latest HUD Archive, prior unique cleanup ZIP and a new small unique-file
ZIP. Hash every removed G1 file, reuse only exact size/SHA matches and stream-check
each used ZIP member. Old2October regenerated payloads are retired with sizes/
times, executable hashes and original build/source evidence retained; exact byte
restoration of that obsolete success package is not promised. No original/native
asset or unique unfinished source is treated as a rebuildable package.

Before deleting instrument_v13 Archive, create an authenticated recovery override
for the seven old retained references, backed by exact old V13 ZIP members. Keep
the original cleanup plan/result byte-identical; update the restore helper to use
the checked override without rewriting historical receipts. Preserve the one
old private ZIP that is still needed as a recovery dependency. It is not a second
active playable version. No remote release/object pruning or permission changes.

## Execute, verification and stopping conditions

Prepare is nondestructive and writes SHA/size/time inventories, new ZIP and
recovery remap. Execute uses PowerShell7 and LiteralPath inside a hard-coded
workspace whitelist, checks absolute paths/reparse descendants, active processes,
plan identity, exact input inventories and all referenced backup bytes first.
Recheck idle state before each recursive removal; stop on a mismatch or failure.
Never automatically stop a user game. Require all eleven targets absent and the
latest trial/source/assets/restore references exact after deletion. Report actual
free-space increase and record the private before/after receipts.
No Git commit/push, engine acceptance or asset publication is part of this step.
