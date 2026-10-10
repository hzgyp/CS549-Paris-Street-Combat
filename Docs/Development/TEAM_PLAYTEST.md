# Restore and verify the unified Paris/G1 version

Later9October selection: start with [the current-build guide](TEAM_CURRENT_BUILD_20261009.md)
for the reviewed playable and exact42 source. This guide continues to govern
unchanged native359; its old Editor/native anchor is not the newer Game audio source.

8 October 2026. For the three entitled CS549 members only. Git supplies source,
configuration and version records; private SFTP supplies native asset/module bytes.
Use **paris-native-playtest-20261008-g1-npc-vfx-v1** with this matching Git revision.
[Chinese guide](TEAM_PLAYTEST_ZH.md). Teammates perform second-computer restoration
and gameplay verification; that gate is pending, not a publisher claim.

## Included version

The existing city, six original soldiers, accepted FP V20/Allied V16/German V11
grips and FineWoodV15 rifle, original firing/reload/damage logic, native NPC
follow/regroup/combat, visible recoil and selected muzzle flash. The current formal
Paris map and G1 bridgehead mission map are both selected. G1 includes start,
crossing, clearing/occupation, victory/loss, safe two-slot save/load and restart.
Models, fingers, source actions and locations are unchanged by publication.
Runtime needs neither Python preparation nor ParisEditorBridge. This is an
editor-backed test, not a new standalone EXE/Shipping build or complete MVP.

## Prepare source and local storage

Use Windows, **UE5.8.2 CL56702186**, Python3.10+ and Windows OpenSSH. Keep bundled
ACLPlugin/Niagara/MeshModelingToolsetExp/InterchangeAssets content installed. Obtain
the SFTP host/account and trusted fingerprint privately from Yupu; never copy his
private key or put secrets in arguments, Git or chat. Same engine version matters:
the selected Win64 DLL/modules target this editor build, not arbitrary UE5.8.

Preserve local source AND ignored asset edits and close UE/Blender before restore.
For a current clean clone use `git pull --ff-only`; never hard-reset/clean or merge
an old pre-cleanup asset-bearing clone. For that old clone, follow
Assets/TEAM_SYNC_WORKFLOW.md Section8 and make a fresh checkout. Run from your own
repository root; do not copy Yupu's absolute paths or Windows junctions.

```powershell
git rev-parse HEAD
# Use your NetID: yp549 or jw2046.
powershell -NoProfile -ExecutionPolicy Bypass -File Tools/Integration/initialize_playtest_storage.ps1 -Owner yp549
python Tools/Integration/restore_native_playtest.py plan
```

Initialization creates a local single writable Content home/junction only when
Content is absent. Existing in-repository junctions are retained. Existing physical
Content is refused rather than silently moved, merged or deleted.

## Download, apply and verify

Restore exactly two Catalog manifests: france-liberation-content and
paris-gameplay-native-playtest. City first download is approximately26.47GiB;
subsequent transfers fetch missing/changed files only. The native manifest supplies
models/materials/actions, current AI Blueprints, both maps, G1 controller, selected
effect/profile and all four matching runtime plugin DLL/modules. Blender originals,
experimental evidence, PDBs, caches and Yupu's saves are not needed to play.

First connect interactively and compare the fingerprint with the trusted private
value. Replace placeholders with privately supplied values:

```powershell
sftp -P 22222 YOUR_ACCOUNT@YOUR_PRIVATE_HOST
# Verify fingerprint, then: bye
python Tools/Integration/restore_native_playtest.py download --host YOUR_PRIVATE_HOST --user YOUR_ACCOUNT
python Tools/Integration/restore_native_playtest.py apply
python Tools/Integration/restore_native_playtest.py verify
```

Passwords are entered at the local OpenSSH prompt. If piped password prompting is
unavailable, use your own authorized key with `--identity C:/path/to/your/key`;
`--known-hosts` selects your pinned-host file. Never disable host-key checking.
All required downloads stage and pass size/SHA-256 before active placement.
Existing different files stop apply. After reviewing/preserving your work,
`apply --backup-conflicts` explicitly replaces only selected paths while retaining
verified backups under tmp/native-playtest-restore/backups-*. No mirror deletion.
Verification also checks the matched source contract, allowing normal Git CRLF/LF
conversion only. A mismatch means wrong/locally edited source or assets, not a
reason to bypass verification. Save the ignored verified.json result for feedback.

## Launch and test on your computer

```powershell
# Default: G1 bridgehead mission. CheckOnly opens no game.
powershell -NoProfile -ExecutionPolicy Bypass -File Tools/Integration/run_paris_native_preview.ps1 -CheckOnly
powershell -NoProfile -ExecutionPolicy Bypass -File Tools/Integration/run_paris_native_preview.ps1
# Separate original formal map:
powershell -NoProfile -ExecutionPolicy Bypass -File Tools/Integration/run_paris_native_preview.ps1 -Entry Formal
```

For another UE installation location, add `-EngineEditor 'E:/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe'`.
The launcher verifies selected source/native hashes, city sizes, UE version and
module BuildIds before ordinary -game with -DisablePython and no editor bridge.
No author/test scripts, map saves or automatic termination run. Close each visible
game yourself before launching another. First shader/texture preparation is not a
warmed FPS measurement. This is local single-player testing, not SFTP multiplayer.

WASD/mouse/left click/R retain original controls. G1: wait for Ready, Enter starts,
F5 requests save, F9 loads, Ctrl+R fully restarts; plain R still reloads. Follow HUD
safe-save eligibility/rejection messages. `-LoadSave` opens G1 with your own latest
valid local slot. Save files remain machine-local and are not copied from Yupu.

Teammates should verify readable initial view and all original characters/grips,
player+Allied bridge traversal, mutual encounter/fire/damage, G1 progression,
visible recoil/flash, one magazine and reload, non-default safe save, close/reopen
load, victory/loss and restart. Report actual failures; do not infer success from
hashes or reproduce private scripted fixtures to claim ordinary playthrough.

Return Git SHA, native asset version, UE version, restore verification output,
CheckOnly result and actual test findings/steps. Share screenshots/logs privately;
logs are in tmp/continuous-arms-native/human-native-*.log. Do not publish commercial
screenshots/raw logs. Until actual feedback arrives, second-machine restore/run,
whole mission, stress FPS, Shipping and course acceptance remain pending.

## Known supplier and gameplay limits

The read-only closure has no missing hard package and retains the same five
supplier soft-reference gaps recorded in the manifest. Do not fabricate fixes or
ignore new errors. Dedicated M1/contact/full-motion, destructive-equipment safety,
near-wall/whole-city visual reliability and measured performance remain bounded by
their dated results. Publication adds no new gameplay or visual acceptance.
