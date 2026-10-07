# Restore and play the current Paris test version

This guide is for the three entitled CS549 team members. Git supplies source/configuration/version records; private SFTP supplies city, character, animation, gameplay and approved Win64 editor module bytes. Use the Catalog-selected `paris-native-playtest-20261006-german-grip-v11` release, not the owner's mutable workspace or an older packaged build. The synchronized Chinese guide is `TEAM_PLAYTEST_ZH.md`. This Git revision carries the matching generic source/configuration/Catalog; pull the matching remote revision before selecting this asset release. Source publication does not establish teammate runtime acceptance.

## What this version contains

The existing Paris city, six soldiers, basic movement/collision, shooting and original guarded reload, HUD, navigation foundation, human-approved V20 native first-person display, V16 grip for BOTH standard Allied NPCs, and V11 grip WITH FineWoodV15 rifles for all THREE standard Germans. Saved native policies also cover later compatible same-faction spawns; no Python preparation or gameplay bridge. NPC AI drafts remain separate/unselected; follow/patrol/faction decisions are not in this baseline. Sleeves and small German grip imperfections are deferred; dedicated M1 clip, full-return/lifecycle/near-wall, effects and stress FPS remain incomplete. See FIRST_PERSON_FORMAL_V21_RESULT_20261005.md, [Allied adoption](ALLIED_NPC_FORMAL_V18_RESULT_20261006.md) and [German adoption](GERMAN_NPC_FORMAL_V14_RESULT_20261006.md). This is not a complete mission/MVP or a standalone EXE.

## Prepare the checkout and engine

Use Windows, UE **5.8.2** (CL 56702186), Python 3.10+ for synchronization, and the Windows OpenSSH client. Keep the UE-bundled ACLPlugin, Niagara, MeshModelingToolsetExp and InterchangeAssets content installed; no paid third-party plugin or runtime bridge build is required. Obtain the SFTP endpoint/account and trusted SSH host fingerprint privately from Yupu. Do not send passwords/private keys in chat or commit them.

For a current clean clone, use `git pull --ff-only`. If your checkout contains old pre-cleanup asset-bearing history, follow `Assets/TEAM_SYNC_WORKFLOW.md` Section 8 and make a fresh clone instead. Preserve uncommitted source and ignored asset edits before synchronization; do not use hard reset/clean. Run the following commands from your checkout, not Yupu's absolute disk path.

```powershell
git rev-parse --short HEAD
# Set Owner to your own NetID, e.g. yp549 or jw2046.
powershell -NoProfile -ExecutionPolicy Bypass -File Tools/Integration/initialize_playtest_storage.ps1 -Owner yp549
python Tools/Integration/restore_native_playtest.py plan
```

The initializer creates a single local writable asset home under `Assets/LocalShared/SFTP/workspaces/<Owner>/paris-gameplay-v1/Content` and a project Content junction only when Content is absent. It preserves an existing in-checkout junction and refuses an existing physical Content directory rather than moving/deleting it. Coordinate such a migration separately. Do not copy the server computer's absolute junctions to another PC.

## Download and verify

The selected playtest includes294 files, including private FP/Allied/German grip
DataAssets/graph and DLL/modules under both `Plugins/ParisGripBindingV18/Binaries/Win64`
and `Plugins/ParisNPCGripV15/Binaries/Win64`. Do not substitute a module built
against another engine build. Generic plugin source and explicit project
enablement come from Git. German rifle mesh/material dependencies are included;
the optional Blender-source release is not needed for playing. Shipping builds
are not supplied.

Only two active manifests are needed for this playtest: `france-liberation-content` and `paris-gameplay-native-playtest`. The new manifest includes the required character/action/material/skeleton closure at the correct game paths; do not download every historical/source/lab baseline as a prerequisite. The first city download is approximately 26.47 GiB, plus the selected native dependencies. Subsequent synchronization transfers only missing/different files; SFTP is not gameplay streaming or binary block-delta transfer.

First connect interactively and compare the displayed SSH fingerprint against Yupu's privately supplied value before trusting the host. Substitute your private endpoint and account:

```powershell
sftp -P 22222 YOUR_ACCOUNT@YOUR_PRIVATE_HOST
# After fingerprint verification and login, enter: bye
python Tools/Integration/restore_native_playtest.py download --host YOUR_PRIVATE_HOST --user YOUR_ACCOUNT
python Tools/Integration/restore_native_playtest.py apply
```

Password mode runs in your own interactive terminal and lets OpenSSH prompt; no password is written to arguments/files. If your environment cannot prompt in piped SFTP, or you use automation, configure your own approved SSH public key and add `--identity C:/path/to/your/private_key`. `--known-hosts` can select an existing pinned host file. Never copy Yupu's private key. Failed transfers stay under ignored `tmp/native-playtest-restore/`; the all-file SHA check prevents applying partial/incorrect downloads. The generated `download.sftp` and `plan.json` contain exact mappings, not secrets.

Close Unreal/Blender before these operations. Existing different files make `apply` stop. Review and preserve your edits; if replacing them is intended, run `apply --backup-conflicts` to retain verified backups under ignored `tmp/native-playtest-restore/backups-.../`. Successful apply verifies all selected bytes and removes only its verified disposable transfer objects; it never deletes conflict backups, unknown Content or retired packages. Re-run `verify` whenever your restored state is uncertain:

```powershell
python Tools/Integration/restore_native_playtest.py verify
```

All members have shared-account CRUD on published SFTP child directories, but do not edit/delete published objects or releases. Team immutability and one binary owner are procedural rules, not filesystem object-lock protection. Continue using task/day-end synchronization before publishing your own changed binary versions.

## Launch and test

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File Tools/Integration/run_paris_native_preview.ps1
# For a different installation, append:
# -EngineEditor 'E:/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe'
```

The launcher checks selected gameplay hashes, city availability/sizes and the exact installed UE version; it opens the saved `/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1` with `-game`, Python and ParisEditorBridge disabled. It does not run one-time authors, test harnesses or save a map. `-CheckOnly` performs startup prerequisites without opening a game window. Full city SHA verification belongs to the restoration step, not every launch.

Click the game window. WASD moves; mouse looks; left click fires; R reloads; Alt+F4 closes. Allow initial texture/shader preparation; startup stutter is not a warmed FPS measurement. This is an independent local single-player playtest, not a multiplayer session over SFTP.

Report the Git SHA, release version, UE version, restore result, startup/log path and observations for movement/holding/fire/reload. Record black/missing materials or visible deformation with a screenshot and reproduction steps. Logs are in `tmp/continuous-arms-native/human-native-*.log`; share privately, not as public commercial screenshots or raw logs. Test at least one magazine/reload, forward/back/strafe movement, camera up/down and close-wall shooting. Do not mark teammate restoration/runtime acceptance complete until an actual teammate reports it.

## Known supplier references

Read-only audit found zero missing hard dependencies and five pre-existing dangling supplier soft references (material customizer, car animation alias, rope tint texture and road debug-library alias). Their exact paths/referencers are recorded in the release manifest. They are not repaired or hidden by this publication, and no claim of a pristine vendor pack is made. Unknown new errors still require investigation.
