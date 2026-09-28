# Asset inventory and restoration

## Team synchronization (27 September 2026)

The selected workflow is **GitHub for code and small project files; SFTP for large models/assets, both originals and modified versions**. The mandatory [team synchronization manual](TEAM_SYNC_WORKFLOW.md) defines start-of-work checks, end-of-day publication, SHA-256 manifests, ownership, new-asset intake and recovery. Read it before changing assets. The user reports SFTP is working; the local service was also observed listening on TCP 22222. This does not establish vendor sharing rights or verify that any particular asset version has been published.

Git tracks version manifests; SFTP holds immutable file versions. Transfer only changed/missing files, not the entire environment on each edit. Existing migration/vendor inventories remain provenance records, not evidence of an uploaded, verified SFTP release. The server store and local external-asset working area are ignored by Git.

## Production policy

Use existing models and compatible action sets. Fine-grained AI-led soldier production is rejected. A visually appealing model is not accepted until its required rig, weapon, animation, source rights and engine integration are understood. Detailed checks take place later; the current task organizes and records assets.

## Organized local environment

- Active project: `Unreal/ParisStreetCombat/WW2FranceLiberation.uproject`.
- Asset namespace: `/Game/WW2City`.
- Initial city map: `/Game/WW2City/Maps/LV_Paris_WW2`.
- Local source delivery: `WW2FranceLiberation---Version d20260630(UE5.6+)` at the workspace root.
- Working copy: source Config, Content and project descriptor copied without Saved, Intermediate, DerivedDataCache or Binaries. The source delivery is preserved unchanged.
- Only project metadata/configuration and inventory are tracked for the city. The vendor Content tree and the original delivery are excluded from Git.
- The source delivery's tutorial/upload manifests are preserved locally. They document a delivery, not our acquisition license or our runtime verification.

The pack contains city/environment/car resources and map components. Its [official listing](https://www.fab.com/listings/dae418da-1969-444a-821c-c1f30a3f21b6) excludes the trailer's soldier characters and some combat effects. No ready character/weapon/action set is claimed.

## Restore after cloning

1. Clone the repository and read the synchronization manual. Restore existing LFS objects where the selected revision uses them; legacy LFS compatibility does not authorize putting new large models in Git/LFS.
2. Obtain the recorded environment package from a source the team is entitled to use; record the receipt/license separately from published source files. Use SFTP only where permitted team sharing has been verified.
3. Follow the selected Git revision's manifests to restore the complete Content layout into `Unreal/ParisStreetCombat/Content`, including WW2City and applicable external-actor/object packages. Verify each downloaded file before replacement; preserve local edits. Do not substitute a lone main map or overwrite team project configuration blindly. If no verified SFTP manifest exists yet, use the entitled original delivery and report that synchronized restoration remains incomplete.
4. Compare the baseline against `VENDOR_DEPENDENCY.json` and the local file manifest, then apply the exact published modifications in the selected sync manifests. Migration hashes describe the original copy, not subsequent edits. The wrapper's date label is recorded as delivered metadata, not independently verified vendor version history.
5. Use the documented project descriptor. The vendor requires ChaosVehiclesPlugin; the organized descriptor enables the installed plugin. Gate 1 verifies actual compatibility, required sublevels and packaging.
6. Do not stage the commercial environment with `git add -f`. The selected private asset transport is SFTP, but redistribution still requires entitlement and sharing approval. Complete the manual's start-of-work checks before editing and its publication checklist before handoff.

## Retained gunplay

`Reference/Gunplay` contains selected team-authored Unreal Blueprint/weapon samples, source models, generator scripts and the earlier browser prototype. They are copied with file hashes and original paths. They remain outside the active Unreal Content tree because reference closure and gameplay compatibility are unverified. The old full repository is the dependency fallback, not an invitation to revive its entire scope.

## Assets still needed

- One approved enemy soldier configuration, with usable rig and basic motions.
- One first-person weapon/arms/action set, including the chosen weapon's actual reload behavior.
- Surface feedback/audio resources if those retained or supplied are unsuitable.

Search existing assets first; favor a coherent compatible set. Exact historical variants follow the selected date/units. No purchase, acquisition license, compatibility result or final quality acceptance is inferred merely from a folder being present.

## Registers

- `ASSET_REGISTER.csv`: role, path, source and acceptance state.
- `VENDOR_DEPENDENCY.json`: local source/version and exclusions.
- `MIGRATION_MANIFEST.json`: copied-file provenance and hashes; includes an explicit not-validated status.
- `Sync/manifests/<asset-id>.json`: create per-asset version manifests during verified publication, following the team manual. No complete live SFTP catalog is claimed by this documentation update.

The private repository contains team documents and permitted reference material. It does not contain the entire local city, engine installation, caches, or a packaged game.
