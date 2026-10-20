# Restore the selected development checkout

20 October 2026. Use a fresh clone of the cleaned development repository and the exact Catalog in that checkout. This is private collaboration for Yupu Guo, Yuqi Pu and Jingdi Wu. Obtain the SFTP host/account, SSH identity and verified known-hosts file privately. Never put them in Git. No course submission is performed by these tools.

The selected game is tutorial1.0/source145/revision12: Game SHA256 `3bb90f646cbbfb3652bab5fcab23c0af2b3bd2d7add577028e6810a9c5576967`, source manifest `faa136ed3bbafa07e93253b3c6faefab6eb4380cc06e657ee9d3c67baa0a9c91`. The selected platform/NPC source is the 17–18 October implementation recorded in DEVELOPMENT_VERSIONS_20261020. The restored Paris rasters retain their original audit and blocked/unknown policy; this is no new survey or UE AI acceptance.

Use Python3.13 and Windows OpenSSH from the clone root. First inspect a plan:

```powershell
python Tools/Integration/restore_selected_development.py workbench plan
python Tools/Integration/restore_selected_development.py tutorial-source plan
```

Choose a profile:

| Profile | Selected external bytes | Placement |
|---|---|---|
| `workbench` | Exact missing historical source-manifest/usage/design context required by the published registry, plus all16 NPC candidate/status images and the original audit | Original checkout-relative paths. Enables a fresh metadata refresh and Paris 2D simulation. |
| `npc` | Only the17-file audited raster closure | Original `tmp/map-survey-overnight-20261013/collections/complete_v3/figures_v1` paths. |
| `tutorial-source` | Catalog-selected city/native/accepted model-action dependencies, source145 ZIP including the private licensed curve, current audio/UI/equipment and native overlay | New independent `tmp/Restored-Development-20261020/Tutorial/Project`; exact source manifest beside it. Old parent Editor DLLs are excluded. |
| `tutorial-game` | Existing reviewed tutorial1.0 archive | `tmp/Restored-Development-20261020/Game`; this downloads/extracts an existing build. |

For the chosen profile, run these steps separately, checking each exit status. Replace the angle-bracket values with privately obtained connection information; do not paste actual secrets into a public issue.

```powershell
python Tools/Integration/restore_selected_development.py workbench download --host <private-host> --user <private-account> --port 22222 --identity <private-key-path> --known-hosts <pinned-known-hosts-path>
python Tools/Integration/restore_selected_development.py workbench apply
python Tools/Integration/restore_selected_development.py workbench verify
```

Use the same three commands with `tutorial-source` or `tutorial-game` when needed. Objects stage under `tmp/Selected-Development-Restore/<profile>/objects`. SHA256/length and archive-member inventories are checked. Apply preflights conflicts and refuses different existing files or junction traversal; it never silently merges another workstation's binary workspace. Preserve conflicting edits and choose a fresh checkout. Failed partial downloads remain for diagnosis and must be moved aside before retry. Logs and receipts stay private in the staging directory.

The platform's Python/JS dependencies are installed separately with `Tools/AssetWorkbench/setup.ps1`; this is not a UE build. Start local-only with `Tools/AssetWorkbench/run.ps1 -BindAddress 127.0.0.1` and use authenticated Refresh index. Port8765 is the default; choose an unoccupied port. Local config/database/session/cookies/browser layouts are generated for that workstation, never copied from the owner's machine. Historical private media/native-cover caches and unresolved-rights intake/research originals are not included in this context package; unavailable optional previews retain their recorded scope. Existing published asset manifests remain the authority for permitted native originals.

For a source145 Editor, inspect the restored source/configuration and dependency closure, then build a matching UE5.8.2 Editor yourself before entry. Restoration is not Editor/PIE/runtime acceptance. The tool performs no compile/cook/Game launch or personal save migration. The owner's original formal entry remains `Releases/Paris-Tutorial-1.0-20261017/PLAY_TUTORIAL.cmd`; its existing UserDir/saves are unchanged. Second-machine restoration and play remain pending until a teammate actually tests them.

[中文说明](SELECTED_DEVELOPMENT_RESTORE_20261020_ZH.md). [Implementation](SFTP_RESTORE_STORAGE_IMPLEMENTATION_20261020.md) and [verification result](SFTP_RESTORE_STORAGE_RESULT_20261020.md).
