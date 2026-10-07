# Standard Allied NPC asset contract

Current authority: 6 October 2026, [formal V18 result](ALLIED_NPC_FORMAL_V18_RESULT_20261006.md).
Yupu accepted the V16 native appearance. All standard Allies use this selection;
do not reintroduce the previous grip or use a frozen diagnostic mesh as a soldier.

## Required native references

| Role | Selected reference |
| --- | --- |
| Soldier class | `/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisAlliedNPCV1` |
| Original adapted mesh | `/Game/ParisCombat/Characters/Adaptation/Meshes/SK_WWII_US_Paratrooper_simple_UE582_v1` |
| Accepted grip configuration | `/Game/ParisCombat/Animation/AlliedGripV15/DA_PC_AlliedGripV16` |
| Accepted postprocess graph | `/Game/ParisCombat/Animation/AlliedGripV15/ABP_PC_AlliedGripPostV16` |
| Map policy | Native `ParisAlliedGripPolicy`, label `PC_AlliedApprovedGripV16` |
| Original rifle appearance class | `/Game/ParisCombat/Blueprints/WeaponAttachmentV3/BP_PC_RifleAttachmentV3` |
| Original M1 mesh | `/Game/USParatrooper/Meshes/Weapon/Sm_M1_Garand` |

The current `LV_ParisStreetCombat_V1` already contains the configured policy.
Place/spawn the selected Allied class, or a compatible subclass preserving its
TeamId0, mesh/skeleton and WeaponAppearance interface. The policy binds both
existing and later Allies; no manual Python preparation or per-NPC offset copy.
It preserves existing equipment and supplies the original M1 only when absent.
It cleans up adapters and only its own spawned rifles on target destruction.

For another mission/test map, include exactly one configured policy with the
references above and enable the `ParisNPCGripV15` plugin. Do not add independent
temporary adapters beside the policy or change the DataAsset to fit one instance.
Inspect native Ready/error logs and actual in-game appearance before release.
An incompatible rig or different weapon requires its own bounded calibration;
the policy is not a universal retargeter. Player and German grip offsets must
not be copied into Allies or vice versa.

## Storage and synchronization

Use Catalog-selected `paris-native-playtest-20261006-german-grip-v11` with the
city manifest. [TEAM_PLAYTEST.md](TEAM_PLAYTEST.md) / [中文指南](TEAM_PLAYTEST_ZH.md)
give the exact restoration workflow. Code/configuration/hash records come from
Git; commercial UE packages and matching UE5.8.2 Win64 modules come from private
SFTP. This Git revision includes the matching source/configuration/Catalog;
the dated adoption result retains its earlier pre-publication status.

Keep one writable asset home and its Content junction; do not duplicate complete
soldier/model directories for each NPC. Original skeleton/material/animation/
Blueprint dependencies remain required even though their old grip presentation
is no longer selected. Preserve original/recovery/failure evidence; this adoption
does not authorize deleting dependencies or changing source assets.

The Allied selection remains unchanged in the later German adoption. Before
another writer, use its current678-row private snapshot
`Evidence/GermanNPCFormalV14/selected_v1/result.json`, documented in
[German V14 result](GERMAN_NPC_FORMAL_V14_RESULT_20261006.md), explicitly replacing
historical map/DLL/Catalog guard authority. Shared source/AI/FP/German assets
stay protected. Full motion, recoil, lifecycle,
near-wall, FPS, Shipping and second-machine testing remain separate open gates.
