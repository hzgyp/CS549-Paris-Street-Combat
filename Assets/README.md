# Asset inventory and restoration

**4 October delivery receipt/audit:** both physical, Git-ignored folders now
contain user files. [Catalog Section11](XIAN_YU_ASSET_CATALOG_20261003_ZH.md)
records new VFX68files/78,239,739bytes and a confirmed RifleAnimsetPro repeat:
all298native files plus SourceFiles.zip match the existing original by SHA/size.
No new motions. VFX is not yet native-runtime accepted. Originals remain here:

- `Assets/LocalWorking/Intake/2026-10-04/01_Muzzle_Flash_VFX/` — muzzle-flash/fire VFX delivery.
- `Assets/LocalWorking/Intake/2026-10-04/02_Firearm_Animations/` — purchased firearm animation delivery.

Preserve original archives/package names/structures; no duplicate deletion.
File/header/ZIP audit only, no extraction, supplied-script execution, live UE
import, upgrade/resave, relocation or SFTP publication. The324FBX ZIP passes CRC
but repeats existing source. New VFX has UE4.26 header clues and its actual root
is MsvFx_MuzzleFlash_Pack; target compatibility/dependency/visual checks remain.
Use existing mature motions/no-new-animation policy. New VFX sharing rights need
confirmation before publication; existing licensed motion baseline remains valid.

**4 October German static model:** user-accepted V15 is published as
`german-rifle-model-20261004-v1` (16files/~191MiB), authenticated SFTP hash verified.
Read [model and download guide](GERMAN_RIFLE_MODEL.md) / [receipt](Sync/GERMAN_RIFLE_PUBLICATION_STATUS.json).
Single editable home `/workspaces/yg745/german-rifle-model-v1/Model/`, plus
immutable versions. Not yet UE/game/animated-kit/historical acceptance; no
further automatic appearance polish or another bare static-rifle purchase.

## Team synchronization (27 September 2026)

**1 October character publication:** the verified private release `character-20261001-v1` contains three preserved original deliveries (590 files) and the UE 5.8.2/Blender 5.2.2 integration baseline (721 files). Its four manifests are active in [the catalog](Sync/CATALOG.json). Read [download and restoration instructions](Sync/README.md#character-integration-baseline-on-1-october) and [actual publication checks](Sync/CHARACTER_PUBLICATION_STATUS.json). All shared areas grant team CRUD; originals/releases remain immutable by procedure. Teammate restoration and final gameplay/history/performance acceptance are separate remaining checks.

**Latest 1 October intake clarification:** new originals physically start in `Assets/LocalWorking/Intake/`; processing and validation remain in LocalWorking until their defined checks and sharing-rights gate pass. Then migrate retained originals and usable outputs/dependencies to the appropriate SFTP baseline/workspace/version locations, verify sizes/SHA-256 and final SFTP bytes, and remove only verified redundant LocalWorking material. Keep junctions only where needed by existing tools/editor paths. Already published city/character assets and runtime aliases stay in place. Follow [the synchronization manual, Section 6](TEAM_SYNC_WORKFLOW.md#6-new-assets-and-original-baselines); a directory or alias is not proof of acceptance or publication.

**30 September migration:** the user explicitly selected the same repository for public code/docs/config/hash records after removing its existing asset bytes/history. Current permitted model, historical and document/image bytes use private SFTP even when small. Read [the active catalog](Sync/CATALOG.json), [publication checks](../Docs/Submission/PUBLICATION_REVIEW.md) and [reclone/restoration procedure](TEAM_SYNC_WORKFLOW.md#8-rejoin-after-the-authorized-history-rewrite). Older Git/LFS ownership notes below are pre-migration snapshots. Local originals and private backups are preserved; 22 unresolved-rights reference files remain local-only with source links.

The selected workflow is **GitHub for code and small project files; SFTP for large models/assets, both originals and modified versions**. The mandatory [team synchronization manual](TEAM_SYNC_WORKFLOW.md) defines start-of-work checks, end-of-day publication, SHA-256 manifests, ownership, new-asset intake and recovery. Read it before changing assets. The user reports SFTP is working; the local service was also observed listening on TCP 22222. This does not establish vendor sharing rights or verify that any particular asset version has been published.

Git tracks version manifests; SFTP holds immutable file versions. Transfer only changed/missing files, not the entire environment on each edit. Existing migration/vendor inventories remain provenance records, not evidence of an uploaded, verified SFTP release. The server store and local external-asset working area are ignored by Git.

**First publication completed, 27 September 2026:** the original France Liberation Content tree (15,850 files, 26.47 GiB) and a rights-filtered historical reference mirror (66 files, 122.46 MiB) are now present in SFTP storage and hash-verified. See [published baselines and exact download paths](Sync/README.md) and the owner's [sharing attestation](Sync/RIGHTS.md). This is server-filesystem verification, not a teammate download or runtime test. Twenty historical files with unresolved sharing rights were excluded and listed in the historical manifest.

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

1. Clone the rewritten source repository into a new folder after preserving old work; configure Git guards and read the active catalog. Do not merge old asset-bearing history or run LFS restoration as the current asset workflow.
2. Obtain the recorded environment package from a source the team is entitled to use; record the receipt/license separately from published source files. Use SFTP only where permitted team sharing has been verified.
3. Follow the selected Git revision's manifests to restore the complete Content layout into `Unreal/ParisStreetCombat/Content`, including WW2City and applicable external-actor/object packages. Verify each downloaded file before replacement; preserve local edits. Do not substitute a lone main map or overwrite team project configuration blindly. If no verified SFTP manifest exists yet, use the entitled original delivery and report that synchronized restoration remains incomplete.
4. Compare the baseline against `VENDOR_DEPENDENCY.json` and the local file manifest, then apply the exact published modifications in the selected sync manifests. Migration hashes describe the original copy, not subsequent edits. The wrapper's date label is recorded as delivered metadata, not independently verified vendor version history.
5. Use the documented project descriptor. The vendor requires ChaosVehiclesPlugin; the organized descriptor enables the installed plugin. Gate 1 verifies actual compatibility, required sublevels and packaging.
6. Do not stage the commercial environment with `git add -f`. The selected private asset transport is SFTP, but redistribution still requires entitlement and sharing approval. Complete the manual's start-of-work checks before editing and its publication checklist before handoff.

## Retained gunplay

`Reference/Gunplay` contains selected team-authored Unreal Blueprint/weapon samples, source models, generator scripts and the earlier browser prototype. They are copied with file hashes and original paths. They remain outside the active Unreal Content tree because reference closure and gameplay compatibility are unverified. The old full repository is the dependency fallback, not an invitation to revive its entire scope.

## Assets still needed

- One finished Allied and one finished German infantry configuration, each with a usable full-body rig, plus compatible third-person rifle locomotion/combat actions. Reuse these across the initial roster; six actors do not require six different models.
- One first-person weapon/arms/action set, including the chosen weapon's actual reload behavior and required ammunition props; one suitable German NPC world rifle. Included bundle components need not be acquired twice.
- Surface feedback/audio resources if those retained or supplied are unsuitable.

Search existing assets first; favor a coherent compatible set. Exact historical variants follow the selected date/units. No purchase, acquisition license, compatibility result or final quality acceptance is inferred merely from a folder being present.

See the [30 September 3D asset audit and priority gaps](3D_ASSET_AUDIT.md) and its [Chinese model search checklist](3D_ASSET_AUDIT_ZH.md). Existing rifles are prototypes; the stopped Lux3D/MPFB pilot is not a production soldier/action set. The audit separates these from the present city dependency and does not authorize new acquisition or modeling.

The new soldier/action intake has a separate [compatibility test and repair plan](CHARACTER_COMPATIBILITY_AND_REPAIR.md). Its isolated UE 5.8.2 lab preserves originals and records actual loading, exchange, appearance/deformation and conversion evidence separately. Read its completion limits before treating an asset as accepted or publishing an adapted version.

## Registers

- `XIAN_YU_ASSET_CATALOG_20261003_ZH.md` ([Chinese catalog](XIAN_YU_ASSET_CATALOG_20261003_ZH.md), [English](XIAN_YU_ASSET_CATALOG_20261003.md)): detailed local Xianyu delivery contents, original/native action indexes, all 125 archive headers and private embedded diagnostic images. A catalog entry is not a runtime or rights pass; current reload bindings and unselected alternatives are separated.
- `ASSET_REGISTER.csv`: role, path, source and acceptance state.
- `VENDOR_DEPENDENCY.json`: local source/version and exclusions.
- `MIGRATION_MANIFEST.json`: copied-file provenance and hashes; includes an explicit not-validated status.
- `Sync/CATALOG.json`: current authoritative manifest paths, versions and manifest hashes. Select only these entries; old mirror manifests remain provenance, not competing restore authorities.
- `Sync/manifests/<asset-id>.json`: publication inventories selected by the catalog. Current releases are indexed in `Sync/README.md`; other local assets are not implicitly published.

The source repository contains code, document sources, configuration and hash metadata; see the publication-status record for actual visibility. It does not contain private SFTP asset bytes, the entire local city, engine installation, caches or a packaged game.
