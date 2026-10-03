# Team playtest publication result

Date: 3 October 2026. Scope: the user authorized fixed private asset publication and matching source push; second-machine testing belongs to teammates.

## Verified asset release

Catalog selects `paris-gameplay-native-playtest`, version `paris-native-playtest-20261003-v1`. It contains 206 non-city native dependencies, 540,314,845 bytes (515.28 MiB). Of those, 195 immutable objects were reused and 11 new objects / 5,694,247 bytes (5.43 MiB) uploaded. The existing 15,850-file city manifest was unchanged. No whole-city reupload, model migration or new gameplay authoring occurred.

All 206 final objects and the final manifest were downloaded over authenticated pinned-host SFTP and checked by SHA-256/size before Catalog selection. Manifest SHA is `ebb579c25d07d963103b2e8be4f7e9db21fee68fc1944ffb41cdaaf8c03a6999`; remote manifest is `/releases/paris-native-playtest-20261003-v1/paris-gameplay-native-playtest.json`. Shared-account create/overwrite/rename/read/delete passed on unique probe files in the new release; probes removed, protected chroot root ACL unchanged. All members share this account's CRUD, with published immutability still procedural.

## Local handoff checks

- Saved-map registry audit covered 15,436 existing packages, including 206 non-city packages. The first all-soft scan stopped on five dangling vendor references; the retained second audit records zero missing hard dependencies and the exact five vendor soft gaps. All 43 native checkpoint hashes stayed unchanged; none of the rejected FP001/aiming/finger packages were selected as runtime closure.
- Restore `plan` hashed all 16,056 required city/runtime files: zero missing/different files, zero downloads or conflicts. It preserves the existing Content junction and does not make a second full workspace.
- Launcher `CheckOnly` verified runtime hashes, city presence/size and installed UE5.8.2; no game window/native save. The latest runtime proof remains the earlier native migration result: selected combat16/66 and ordinary Python/bridge-disabled `-game`600frames, not a new packaged build.
- Six synthetic restore safety tests passed (path escape, placement/hash verification, default conflict refusal, explicit verified backup, invalid staged file refusal, manifest hash/duplicate ownership refusal). Python AST/PowerShell parse and staged storage guards checked; authenticated download mode was exercised for publication, not a teammate's password terminal.
- Removed 540,314,845 bytes of exact verified temporary publication downloads after adoption; final objects, owner workspace, originals, history and all evidence reports remain. Restore apply removes only its verified disposable staged objects and retains conflict backups.

Windows initially refused `.ps1` execution under the default policy. The documented process-scoped `-ExecutionPolicy Bypass` was tested without changing machine policy. The broad all-ref Git diagnostic found a private automatic `refs/codex/turn-diffs` tree containing the then-unignored Blueprint, not main ancestry or staged source. Keep it local; do not delete unique recovery data or mirror it publicly. Pre-push now checks every outgoing commit's complete ancestry, rejects private ref destinations and non-commit tags, and keeps the broad diagnostic available. Archived patch whitespace/line endings are explicitly byte-preserved, not reformatted.

## Source publication and teammate boundary

The matching source/configuration/manifests and failure records were committed and pushed as `9d05a85cdfa3811da772745ec18641838f7117ae`. The guarded push succeeded and `git ls-remote origin refs/heads/main` matched that SHA. A subsequent receipt-only commit records this verified event; it does not change asset versions. No commercial binary bytes, private keys, passwords or raw screenshots entered the source commit. Restoration and launch instructions: `TEAM_PLAYTEST.md` / `TEAM_PLAYTEST_ZH.md`.

Teammates still need to test external SFTP access, actual local recovery and game startup/physical input. Human movement smoothness, M1-specific reload/clip contact, warmed/stress FPS, new packaging, NPC behavior design and course acceptance remain open. No messages were sent to teammates.
