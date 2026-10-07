# Downloaded Xianyu asset catalog

2026-10-03 · yg745 · Local inspection; not a release manifest.

**4 October addendum:** new muzzle VFX68files; incoming motion delivery's298native
files and SourceFiles.zip are SHA-exact duplicates of RifleAnimsetPro, no new
motions. Section11 records the file/header/ZIP audit, not a live-game import.
Earlier bare-German-rifle gaps are historical: accepted/shared V15 now exists,
see [model guide](GERMAN_RIFLE_MODEL.md); do not repurchase a bare static model.

Scope: earlier soldier/action deliveries, ShooterStarter, D059, the 125-pack UE4 collection and the new MW2 gun library. Paris is listed separately as an existing dependency; its recorded origin is Meshingun Studio/Fab, not proof of a Xianyu transaction. Retired Normandy/Lux3D experiments are not production assets.

This review checks delivered-file presence/sizes, reads all 125 archive headers, and safely opens/renders the gun library. Earlier UE class/rig/duration facts come from dated real-load records, not a new runtime test of every action. Names, previews and import success do not prove historical or runtime fitness.

Images reference existing private local files, with no commercial bytes/screenshots copied into Git. Teammates need those private files to display images. New MW2 provenance/three-member sharing is unconfirmed; it stays LocalWorking. Previous attestations do not cover it automatically.

## 1. Delivery overview

| Bundle | Files | Original size | Present / coverage | Physical location relative to Assets |
| --- | --- | --- | --- | --- |
| German Soldier WWII | 104 | 294,224,744 B (0.274 GiB) | 104 | LocalShared/SFTP/baselines/character-original-intake/character-20261001-v1/CHAR-G-GermanSoldierWWII |
| US Paratrooper | 186 | 478,639,266 B (0.446 GiB) | 186 | LocalShared/SFTP/baselines/character-original-intake/character-20261001-v1/CHAR-A-USSoldier |
| Rifle Animset Pro | 300 | 473,464,019 B (0.441 GiB) | 300 | LocalShared/SFTP/baselines/character-original-intake/character-20261001-v1/ANI-TP-RifleAnimsetPro |
| D059 Rifle Pro - MoCap Pack | 1563 | 1,944,249,213 B (1.811 GiB) | 1563 | LocalShared/SFTP/baselines/rifle-pro-mocap-original/rifle-motion-20261002-v1 |
| ShooterStarter FPS Arm A | 607 | 3,154,499,065 B (2.938 GiB) | 607 | LocalWorking/Intake/2026-10-01/01_ShooterStarter_FPS_Arm_A |
| UE4 animation collection | 250 | 24,108,906,232 B | 125 archives + 125 previews | LocalWorking/Intake/2026-10-01/03_UE4_Animation_Collection/ |
| MW2_Guns_Asset_Library.blend | 1 | 2,364,179,404 B (2.202 GiB) | 1 | LocalWorking/Intake/2026-10-03/01_MW2_Guns_Asset_Library/ |
| MsvFx_MuzzleFlash_Pack (4October new candidate) | 68 | 78,239,739 B | File/header/SHA audit, not runtime | LocalWorking/Intake/2026-10-04/01_Muzzle_Flash_VFX/ |
| RifleAnimsetPro (4October repeat delivery) | 301 | 473,848,190 B | 298native + source ZIP SHA-exact repeats; no new motions | LocalWorking/Intake/2026-10-04/02_Firearm_Animations/ |

Sizes refer to originals, not deduplicated total storage. Adaptations, aliases and hash objects overlap. Presence/size checks are not a new full-original SHA audit.

## 2. German Soldier WWII

| UE class | Count |
| --- | --- |
| AnimSequence | 7 |
| MapBuildDataRegistry | 2 |
| Material | 6 |
| MaterialFunction | 1 |
| MaterialInstanceConstant | 18 |
| ObjectRedirector | 1 |
| PhysicsAsset | 2 |
| SkeletalMesh | 5 |
| Skeleton | 1 |
| StaticMesh | 1 |
| Texture2D | 56 |
| TextureCube | 1 |
| World | 2 |

Two complete German variants plus no-head/equipment meshes, 7 delivered actions and 56 Texture2D assets. Repaired integration baseline is character-ue582-v1; later translation/locomotion adaptation is recorded separately. MP40 is an SMG, not a rifle.

Meshes and rigs:

| Asset | Class | Bones | LOD / materials | Skeleton |
| --- | --- | --- | --- | --- |
| /Game/GermanSoldier/Meshes/Equipment/SK_WWII_GermanSoldier_equpA | SkeletalMesh | 69 | 1 / 5 | /Game/GermanSoldier/Meshes/SK_WWII_GermanSoldier_simple_Skeleton.SK_WWII_GermanSoldier_simple_Skeleton |
| /Game/GermanSoldier/Meshes/Equipment/SK_WWII_GermanSoldier_equpB | SkeletalMesh | 69 | 1 / 5 | /Game/GermanSoldier/Meshes/SK_WWII_GermanSoldier_simple_Skeleton.SK_WWII_GermanSoldier_simple_Skeleton |
| /Game/GermanSoldier/Meshes/SK_WWII_GermanSoldier_noHead | SkeletalMesh | 68 | 1 / 3 | /Game/GermanSoldier/Meshes/SK_WWII_GermanSoldier_simple_Skeleton.SK_WWII_GermanSoldier_simple_Skeleton |
| /Game/GermanSoldier/Meshes/SK_WWII_GermanSoldier_varA | SkeletalMesh | 69 | 1 / 10 | /Game/GermanSoldier/Meshes/SK_WWII_GermanSoldier_simple_Skeleton.SK_WWII_GermanSoldier_simple_Skeleton |
| /Game/GermanSoldier/Meshes/SK_WWII_GermanSoldier_varB | SkeletalMesh | 69 | 1 / 9 | /Game/GermanSoldier/Meshes/SK_WWII_GermanSoldier_simple_Skeleton.SK_WWII_GermanSoldier_simple_Skeleton |
| /Game/GermanSoldier/Meshes/Weapon/SM_WWII_MP40 | StaticMesh | — | — / 1 | — |

Reload/fire raw action names (name discovery only; recoil appearance/current binding are separate):

| Clip | Seconds | Root motion |
| --- | --- | --- |

![Historical native final-body capture; 2026-10-01](<LocalShared/SFTP/workspaces/yg745/character-ue582-v1/Evidence/Repair20261001/FinalNativeCaptures/german_A_three_quarter.png>)

## 3. US Paratrooper

| UE class | Count |
| --- | --- |
| AnimSequence | 5 |
| MapBuildDataRegistry | 2 |
| Material | 8 |
| MaterialFunction | 1 |
| MaterialInstanceConstant | 20 |
| PhysicsAsset | 1 |
| SkeletalMesh | 6 |
| Skeleton | 2 |
| StaticMesh | 2 |
| Texture2D | 83 |
| TextureCube | 1 |
| World | 2 |

Two complete US paratrooper variants plus no-head/equipment meshes, M1 Garand appearance, 5 delivered actions and 83 Texture2D assets. Existing M1 is a one-bone rigid appearance model, not evidence of independent bolt/en-bloc motion.

Meshes and rigs:

| Asset | Class | Bones | LOD / materials | Skeleton |
| --- | --- | --- | --- | --- |
| /Game/USParatrooper/Meshes/SK_WWII_US_Paratrooper_equipment | SkeletalMesh | 73 | 1 / 10 | /Game/USParatrooper/Meshes/SK_WWII_US_Paratrooper_simple_Skeleton.SK_WWII_US_Paratrooper_simple_Skeleton |
| /Game/USParatrooper/Meshes/SK_WWII_US_Paratrooper_no_helmet | SkeletalMesh | 73 | 1 / 6 | /Game/USParatrooper/Meshes/SK_WWII_US_Paratrooper_simple_Skeleton.SK_WWII_US_Paratrooper_simple_Skeleton |
| /Game/USParatrooper/Meshes/SK_WWII_US_Paratrooper_no_helmet_w_equipment | SkeletalMesh | 73 | 1 / 13 | /Game/USParatrooper/Meshes/SK_WWII_US_Paratrooper_simple_Skeleton.SK_WWII_US_Paratrooper_simple_Skeleton |
| /Game/USParatrooper/Meshes/SK_WWII_US_Paratrooper_simple | SkeletalMesh | 73 | 1 / 14 | /Game/USParatrooper/Meshes/SK_WWII_US_Paratrooper_simple_Skeleton.SK_WWII_US_Paratrooper_simple_Skeleton |
| /Game/USParatrooper/Meshes/SK_WWII_US_Paratrooper_simpleB | SkeletalMesh | 73 | 1 / 13 | /Game/USParatrooper/Meshes/SK_WWII_US_Paratrooper_simple_Skeleton.SK_WWII_US_Paratrooper_simple_Skeleton |
| /Game/USParatrooper/Meshes/Weapon/SK_M1_Garand | SkeletalMesh | 1 | 1 / 1 | /Game/USParatrooper/Meshes/Weapon/SM_M1_Garand_Skeleton.SM_M1_Garand_Skeleton |
| /Game/USParatrooper/Meshes/Weapon/SM_SMG_Thompson | StaticMesh | — | — / 1 | — |
| /Game/USParatrooper/Meshes/Weapon/Sm_M1_Garand | StaticMesh | — | — / 1 | — |

Reload/fire raw action names (name discovery only; recoil appearance/current binding are separate):

| Clip | Seconds | Root motion |
| --- | --- | --- |
| Prone_Reload_Rifle | 3.3333 | False |

![Historical native final-body capture; 2026-10-01](<LocalShared/SFTP/workspaces/yg745/character-ue582-v1/Evidence/Repair20261001/FinalNativeCaptures/allied_A_three_quarter.png>)

## 4. Rifle Animset Pro

| UE class | Count |
| --- | --- |
| AimOffsetBlendSpace | 1 |
| AnimSequence | 277 |
| BlendSpace | 1 |
| Material | 1 |
| MaterialFunction | 4 |
| MaterialInstanceConstant | 1 |
| PhysicsAsset | 1 |
| SkeletalMesh | 1 |
| Skeleton | 1 |
| Texture2D | 9 |
| World | 1 |

277 AnimSequences: in-place/root-motion, rifle locomotion, run/jump/crouch/prone, fire/reload/hit/death families. Exact raw names are in the native index. The current actual reload binding is Rifle_Reload_2, not D059.

Meshes and rigs:

| Asset | Class | Bones | LOD / materials | Skeleton |
| --- | --- | --- | --- | --- |
| /Game/RifleAnimsetPro/UE4_Mannequin/Mesh/SK_Mannequin | SkeletalMesh | 68 | 1 / 2 | /Game/RifleAnimsetPro/UE4_Mannequin/Mesh/UE4_Mannequin_Skeleton.UE4_Mannequin_Skeleton |

Reload/fire raw action names (name discovery only; recoil appearance/current binding are separate):

| Clip | Seconds | Root motion |
| --- | --- | --- |
| Rifle_Crouch_Reload | 2.0667 | False |
| Rifle_Crouch_Reload2 | 2.4000 | False |
| Rifle_Prone_Reload | 2.4000 | False |
| Rifle_Reload_2 | 2.1667 | False |
| Rifle_ShootBurst | 1.7000 | False |
| Rifle_ShootBurstLong | 2.7667 | False |
| Rifle_ShootGrenade | 0.8000 | False |
| Rifle_ShootLoop_Additive | 0.6333 | False |
| Rifle_ShootOnce | 0.8000 | False |
| Rifle_Crouch_Reload | 2.0667 | True |
| Rifle_Crouch_Reload2 | 2.4000 | True |
| Rifle_Prone_Reload | 2.4000 | True |
| Rifle_Reload_2 | 2.1667 | True |
| Rifle_ShootBurst | 1.7000 | True |
| Rifle_ShootBurstLong | 2.7667 | True |
| Rifle_ShootGrenade | 0.8000 | True |
| Rifle_ShootLoop_Additive | 0.6333 | True |
| Rifle_ShootOnce | 0.8000 | True |

## 5. D059 Rifle Pro - MoCap Pack

| UE class | Count |
| --- | --- |
| AnimSequence | 761 |
| Material | 2 |
| MaterialFunction | 4 |
| MaterialInstanceConstant | 1 |
| ObjectRedirector | 1 |
| PhysicsAsset | 1 |
| SkeletalMesh | 1 |
| Skeleton | 1 |
| StaticMesh | 1 |
| Texture2D | 12 |
| World | 1 |

761 AnimSequences including in-place/root-motion and standing/crouched single/burst/continuous fire, aim/relaxed reload. 70-bone mannequin; modern M4 preview is not selected as a WWII weapon. Selected SFTP baseline is 15 clips/33 native packages plus configuration, 35 files total, not the whole pack in game. Selection into a baseline is not a current reload switch.

Meshes and rigs:

| Asset | Class | Bones | LOD / materials | Skeleton |
| --- | --- | --- | --- | --- |
| /Game/Rifle_01/Character/Mesh/M4_Rifle_01 | StaticMesh | — | — / 1 | — |
| /Game/Rifle_01/Character/Mesh/SK_Mannequin | SkeletalMesh | 70 | 1 / 2 | /Game/Rifle_01/Character/Mesh/UE4_Mannequin_Skeleton.UE4_Mannequin_Skeleton |

Reload/fire raw action names (name discovery only; recoil appearance/current binding are separate):

| Clip | Seconds | Root motion |
| --- | --- | --- |
| W2_Crouch_Fire_Burst_IP | 1.0000 | False |
| W2_Crouch_Fire_Continuous_IP | 1.0000 | False |
| W2_Crouch_Fire_Single_IP | 1.0000 | False |
| W2_Stand_Aim_Reload_IP | 4.1333 | False |
| W2_Stand_Fire_Burst_IP | 1.0000 | False |
| W2_Stand_Fire_Continuous_IP | 1.0000 | False |
| W2_Stand_Fire_Single_IP | 1.0000 | False |
| W2_Stand_Relaxed_Reload_IP | 5.3000 | False |
| W2_Crouch_Fire_Burst | 1.0000 | False |
| W2_Crouch_Fire_Continuous | 1.0000 | False |
| W2_Crouch_Fire_Single | 1.0000 | False |
| W2_Stand_Aim_Reload | 4.1333 | False |
| W2_Stand_Fire_Burst | 1.0000 | False |
| W2_Stand_Fire_Continuous | 1.0000 | False |
| W2_Stand_Fire_Single | 1.0000 | False |
| W2_Stand_Relaxed_Reload | 5.3000 | False |

![Historical 15 selected source-clip diagnostic views](<LocalWorking/Validation/UE582/2026-10-01-weapons-v1/Evidence/Baseline20261002/source_motion_sheet_1.png>)

## 6. ShooterStarter FPS Arm A

| UE class | Count |
| --- | --- |
| AnimSequence | 14 |
| Blueprint | 5 |
| MapBuildDataRegistry | 1 |
| Material | 3 |
| MaterialFunction | 2 |
| MaterialInstanceConstant | 86 |
| PhysicsAsset | 7 |
| SkeletalMesh | 9 |
| Skeleton | 6 |
| StaticMesh | 27 |
| Texture2D | 128 |
| TextureRenderTarget2D | 1 |
| World | 1 |

Combined and split arm candidates with modern sleeves/gloves, modern rifle and attachments. Of 14 animations, 7 are demo-arm clips and 7 are weapon/attachment clips. Weapon Reload drives gun parts, not matched FP hand reload. The old direct D059 pose/framing trial failed; retain LocalWorking and do not replace accepted continuous arms.

Meshes and rigs:

| Asset | Class | Bones | LOD / materials | Skeleton |
| --- | --- | --- | --- | --- |
| /Game/ShooterStarter/Skeletal/Arm_A/SKM_FPS_Arm_A | SkeletalMesh | 68 | 4 / 2 | /Game/ShooterStarter/Skeletal/Arm_A/Skeleton/SK_FPS_Arm_A_Skeleton.SK_FPS_Arm_A_Skeleton |
| /Game/ShooterStarter/Skeletal/Arm_A/SKM_FPS_Arm_A_Left | SkeletalMesh | 68 | 1 / 2 | /Game/ShooterStarter/Skeletal/Arm_A/Skeleton/SK_FPS_Arm_A_Skeleton.SK_FPS_Arm_A_Skeleton |
| /Game/ShooterStarter/Skeletal/Arm_A/SKM_FPS_Arm_A_Right | SkeletalMesh | 68 | 1 / 2 | /Game/ShooterStarter/Skeletal/Arm_A/Skeleton/SK_FPS_Arm_A_Skeleton.SK_FPS_Arm_A_Skeleton |
| /Game/ShooterStarter/Skeletal/Weapon/Attachment/IronSight_A/SKM_IironSight_A_Back | SkeletalMesh | 3 | 1 / 1 | /Game/ShooterStarter/Skeletal/Weapon/Attachment/IronSight_A/SK_IironSight_A_Back_Skeleton.SK_IironSight_A_Back_Skeleton |
| /Game/ShooterStarter/Skeletal/Weapon/Attachment/IronSight_A/SKM_IironSight_A_Front | SkeletalMesh | 2 | 1 / 1 | /Game/ShooterStarter/Skeletal/Weapon/Attachment/IronSight_A/SK_IironSight_A_Front_Skeleton.SK_IironSight_A_Front_Skeleton |
| /Game/ShooterStarter/Skeletal/Weapon/Attachment/IronSight_A/SM_BackIronSight_Base | StaticMesh | — | — / 1 | — |
| /Game/ShooterStarter/Skeletal/Weapon/Attachment/IronSight_A/SM_BackIronSight_Head | StaticMesh | — | — / 1 | — |
| /Game/ShooterStarter/Skeletal/Weapon/Attachment/IronSight_A/SM_BackIronSight_Top | StaticMesh | — | — / 1 | — |
| /Game/ShooterStarter/Skeletal/Weapon/Attachment/IronSight_A/SM_FrontIronSight_Base | StaticMesh | — | — / 1 | — |
| /Game/ShooterStarter/Skeletal/Weapon/Attachment/IronSight_A/SM_FrontIronSight_Top | StaticMesh | — | — / 1 | — |
| /Game/ShooterStarter/Skeletal/Weapon/Attachment/Scope_A/SKM_Scope_A | SkeletalMesh | 1 | 1 / 1 | /Game/ShooterStarter/Skeletal/Weapon/Attachment/Scope_A/SK_Scope_A_Skeleton.SK_Scope_A_Skeleton |
| /Game/ShooterStarter/Skeletal/Weapon/Attachment/Scope_A/SM_Scoope_A | StaticMesh | — | — / 2 | — |
| /Game/ShooterStarter/Skeletal/Weapon/Rifle_A/Parts/SM_Barrel_A | StaticMesh | — | — / 1 | — |
| /Game/ShooterStarter/Skeletal/Weapon/Rifle_A/Parts/SM_Bipod_A_L | StaticMesh | — | — / 1 | — |
| /Game/ShooterStarter/Skeletal/Weapon/Rifle_A/Parts/SM_Bipod_A_M | StaticMesh | — | — / 1 | — |
| /Game/ShooterStarter/Skeletal/Weapon/Rifle_A/Parts/SM_Bipod_A_R | StaticMesh | — | — / 1 | — |
| /Game/ShooterStarter/Skeletal/Weapon/Rifle_A/Parts/SM_Body | StaticMesh | — | — / 4 | — |
| /Game/ShooterStarter/Skeletal/Weapon/Rifle_A/Parts/SM_Charging_Slide | StaticMesh | — | — / 1 | — |
| /Game/ShooterStarter/Skeletal/Weapon/Rifle_A/Parts/SM_EjectionPort | StaticMesh | — | — / 1 | — |
| /Game/ShooterStarter/Skeletal/Weapon/Rifle_A/Parts/SM_FlashLight_A | StaticMesh | — | — / 1 | — |
| /Game/ShooterStarter/Skeletal/Weapon/Rifle_A/Parts/SM_ForwardAssist | StaticMesh | — | — / 1 | — |
| /Game/ShooterStarter/Skeletal/Weapon/Rifle_A/Parts/SM_ForwardGrip | StaticMesh | — | — / 1 | — |
| /Game/ShooterStarter/Skeletal/Weapon/Rifle_A/Parts/SM_Grip | StaticMesh | — | — / 1 | — |
| /Game/ShooterStarter/Skeletal/Weapon/Rifle_A/Parts/SM_HandGuard_A | StaticMesh | — | — / 1 | — |
| /Game/ShooterStarter/Skeletal/Weapon/Rifle_A/Parts/SM_Mag_A | StaticMesh | — | — / 1 | — |
| /Game/ShooterStarter/Skeletal/Weapon/Rifle_A/Parts/SM_PEQ | StaticMesh | — | — / 1 | — |
| /Game/ShooterStarter/Skeletal/Weapon/Rifle_A/Parts/SM_Rifle_Ammo | StaticMesh | — | — / 1 | — |
| /Game/ShooterStarter/Skeletal/Weapon/Rifle_A/Parts/SM_Rifle_Ammo_Projectile | StaticMesh | — | — / 1 | — |
| /Game/ShooterStarter/Skeletal/Weapon/Rifle_A/Parts/SM_Rifle_Ammo_Shell | StaticMesh | — | — / 1 | — |
| /Game/ShooterStarter/Skeletal/Weapon/Rifle_A/Parts/SM_Stock_A | StaticMesh | — | — / 1 | — |
| /Game/ShooterStarter/Skeletal/Weapon/Rifle_A/Parts/SM_Suppressor | StaticMesh | — | — / 1 | — |
| /Game/ShooterStarter/Skeletal/Weapon/Rifle_A/Parts/SM_Switch | StaticMesh | — | — / 1 | — |
| /Game/ShooterStarter/Skeletal/Weapon/Rifle_A/Parts/SM_Trigger | StaticMesh | — | — / 1 | — |
| /Game/ShooterStarter/Skeletal/Weapon/Rifle_A/SKM_Mag_A | SkeletalMesh | 1 | 1 / 1 | /Game/ShooterStarter/Skeletal/Weapon/Rifle_A/SK_Mag_A_Skeleton.SK_Mag_A_Skeleton |
| /Game/ShooterStarter/Skeletal/Weapon/Rifle_A/SKM_Rifle_A | SkeletalMesh | 23 | 1 / 1 | /Game/ShooterStarter/Skeletal/Weapon/Rifle_A/SK_Rifle_A_Skeleton.SK_Rifle_A_Skeleton |
| /Game/ShooterStarter/Skeletal/Weapon/Rifle_A/SKM_Rifle_A_Assembled | SkeletalMesh | 23 | 1 / 17 | /Game/ShooterStarter/Skeletal/Weapon/Rifle_A/SK_Rifle_A_Skeleton.SK_Rifle_A_Skeleton |

Reload/fire raw action names (name discovery only; recoil appearance/current binding are separate):

| Clip | Seconds | Root motion |
| --- | --- | --- |
| AS_ThirdPersonIdle | 2.6333 | False |
| AS_ThirdPersonJump_End | 0.2000 | False |
| AS_ThirdPersonJump_Loop | 0.7000 | False |
| AS_ThirdPersonJump_Start | 0.4667 | False |
| AS_ThirdPersonRun | 0.6000 | False |
| AS_ThirdPersonWalk | 1.0000 | False |
| AS_ThirdPerson_Jump | 0.2000 | False |
| AS_Rifle_A_Aim_A_Activated | 1.0000 | False |
| AS_Rifle_A_Fire_A | 0.3333 | False |
| AS_Rifle_A_First_Use | 1.4333 | False |
| AS_Rifle_A_Reload | 2.9667 | False |
| AS_Rifle_A_Reload_Just_Mag | 1.7000 | False |
| AS_Rifle_A_Switch_To_Auto | 0.6333 | False |
| AS_Rifle_A_Switch_To_SingleFire | 0.6333 | False |

![Historical candidate reference mesh, NOT an accepted FP setup](<LocalWorking/Validation/UE582/2026-10-01-weapons-v1/Evidence/CandidateProbe_v2/reference_00_front_minus_y.png>)

## 7. UE4 collection: all 125 headers read, no bulk extraction

All 125 archive headers were read successfully. Member/native-file counts are NOT animation counts: .uasset may be a mesh, material, skeleton or Blueprint. Private catalog_facts.json contains exact member paths; see the native-name appendix. No bundled script/project is executed. Earlier CRC/size duplicate screening is not SHA equality.

| Archive | Members | Native files | Expanded MiB | Source formats | Preview |
| --- | --- | --- | --- | --- | --- |
| 2Handed Hammer Set.7z | 132 | 116 | 30.0 | — | 2Handed Hammer Set.png |
| 41 Animations For Monsters.7z | 68 | 59 | 19.2 | — | 41 Animations For Monsters.png |
| Adaptive Starts and Stops.7z | 51 | 50 | 32.2 | — | Adaptive Starts and Stops.png |
| Advance Cover Animations.7z | 79 | 65 | 24.7 | — | Advance Cover Animations.png |
| Adventure Game Animset.7z | 1056 | 1055 | 377.1 | — | Adventure Game Animset.png |
| Amplify Animation Pack.7z | 790 | 786 | 355.1 | .blend:1 | Amplify Animation Pack.jpg |
| Animated Modern Civilian Hands Pack.7z | 114 | 113 | 252.4 | — | Animated Modern Civilian Hands Pack.png |
| Archer Animset Pro.7z | 716 | 710 | 700.8 | — | Archer Animset Pro.png |
| Basic female movements.7z | 133 | 132 | 27.2 | — | Basic female movements.jpg |
| Capoeira Anim Set.7z | 73 | 61 | 47.6 | — | Capoeira Anim Set.png |
| Casual Animation Pack.7z | 46 | 45 | 19.1 | — | Casual Animation Pack.png |
| Chainsaw Attacks.7z | 68 | 67 | 20.6 | — | Chainsaw Attacks.jpg |
| Character Conversation.7z | 93 | 48 | 207.2 | .fbx:32, .mb:1 | Character Conversation.png |
| Character Interaction Add On Vol 01.7z | 170 | 169 | 102.1 | — | Character Interaction Add On Vol 01.png |
| City Animation of People Pack 1.7z | 44 | 42 | 29.5 | — | City Animation of People Pack 1.png |
| CITY PEOPLE.7z | 354 | 352 | 416.9 | — | CITY PEOPLE.png |
| CLazy Runner Action Pack.7z | 301 | 299 | 53.5 | — | CLazy Runner Action Pack.png |
| Close Combat Animset.7z | 123 | 120 | 31.0 | — | Close Combat Animset.png |
| Combat Knife Animation Kit.7z | 67 | 66 | 85.2 | — | Combat Knife Animation Kit.png |
| Conversion Animset ( TwinSword & TwinBlades).7z | 38 | 37 | 18.1 | — | Conversion Animset ( TwinSword & TwinBlades).png |
| Cover Animset Pro.7z | 188 | 186 | 236.5 | — | Cover Animset Pro.png |
| Cover System Tool.7z | 548 | 454 | 799.2 | — | Cover System Tool.png |
| Crafting Animations.7z | 65 | 64 | 19.9 | — | Crafting Animations.png |
| Cruel Sword Finisher Set.7z | 84 | 83 | 49.1 | — | Cruel Sword Finisher Set.png |
| Dialog Animations.7z | 48 | 47 | 23.7 | — | Dialog Animations.png |
| Dynamic Archer Set.7z | 55 | 53 | 17.2 | — | Dynamic Archer Set.png |
| Dynamic Locomotion + Blueprints.7z | 85 | 83 | 29.3 | — | Dynamic Locomotion + Blueprints.jpg |
| Dynamic Sword Animset.7z | 225 | 189 | 45.7 | — | Dynamic Sword Animset.png |
| Evil Magician Animations.7z | 31 | 30 | 14.1 | — | Evil Magician Animations.png |
| Farming And Mining Pack.7z | 169 | 168 | 222.0 | — | Farming And Mining Pack.png |
| Fast prototyping animation set.7z | 60 | 59 | 15.3 | — | Fast prototyping animation set.png |
| Fighter 3 Pistol.7z | 150 | 139 | 28.0 | — | Fighter 3 Pistol.png |
| Fighting Animset Pro.7z | 491 | 489 | 665.7 | — | Fighting Animset Pro.png |
| First Person baseball bat.7z | 69 | 68 | 29.7 | — | First Person baseball bat.jpg |
| First Person Crowbar.7z | 72 | 71 | 22.9 | — | First Person Crowbar.jpg |
| Flying Mage Set Volume 2.7z | 87 | 86 | 109.4 | — | Flying Mage Set Volume 2.png |
| FPP Melee Animset.7z | 398 | 395 | 497.1 | — | FPP Melee Animset.png |
| Frank Action RPG Sword 1.7z | 141 | 139 | 24.7 | — | Frank Action RPG Sword 1.png |
| Frank Assassin (Ninja).7z | 285 | 284 | 51.1 | — | Frank Assassin (Ninja).png |
| Frank climax's Katana.7z | 317 | 316 | 59.9 | — | Frank climax's Katana.png |
| Frank Damages.7z | 250 | 249 | 90.0 | — | Frank Damages.png |
| Frank RPG 2 Handed Combo.7z | 195 | 193 | 47.5 | — | Frank RPG 2 Handed Combo.png |
| Frank RPG Archer Combo Set.7z | 270 | 268 | 71.6 | — | Frank RPG Archer Combo Set.png |
| Frank RPG Dual.7z | 340 | 338 | 93.9 | — | Frank RPG Dual.png |
| Frank RPG Fighter.7z | 302 | 299 | 975.4 | — | Frank RPG Fighter.png |
| Frank RPG Gunslinger.7z | 171 | 169 | 80.3 | — | Frank RPG Gunslinger.png |
| Frank RPG Mage.7z | 255 | 253 | 468.8 | — | Frank RPG Mage.png |
| Frank RPG Spear.7z | 102 | 101 | 19.8 | — | Frank RPG Spear.png |
| Frank RPG Warrior Male.7z | 425 | 423 | 517.2 | — | Frank RPG Warrior Male.png |
| Frank Slash Pack.7z | 2032 | 1881 | 1030.7 | .fbx:150 | Frank Slash Pack.png |
| Full Mount Attacks.7z | 66 | 51 | 17.7 | — | Full Mount Attacks.png |
| General Purpose Animations Pack.7z | 191 | 190 | 34.9 | — | General Purpose Animations Pack.jpg |
| GhostSamurai_Bundle.7z | 2515 | 2514 | 800.6 | — | GhostSamurai_Bundle.jpg |
| Giant Monster Animset.7z | 253 | 251 | 257.2 | — | Giant Monster Animset.png |
| Grapple Component.7z | 301 | 245 | 66.7 | — | Grapple Component.png |
| GreatSword Animset.7z | 330 | 328 | 148.6 | — | GreatSword Animset.png |
| Grim reaper Set.7z | 156 | 155 | 63.2 | — | Grim reaper Set.jpg |
| Hammer Animation Set.7z | 123 | 121 | 37.1 | — | Hammer Animation Set.png |
| Have A Sit Animation Pack.7z | 405 | 404 | 57.1 | — | Have A Sit Animation Pack.jpg |
| Hostage Set.7z | 98 | 97 | 23.8 | — | Hostage Set.png |
| House Anim Pack.7z | 50 | 49 | 19.0 | — | House Anim Pack.jpg |
| Insane Aircombo Set.7z | 179 | 178 | 68.1 | — | Insane Aircombo Set.png |
| Insane Gun Sword Animset.7z | 182 | 181 | 61.0 | — | Insane Gun Sword Animset.png |
| Insane Gunner Set.7z | 263 | 261 | 73.2 | — | Insane Gunner Set.png |
| Japanese sword action.7z | 561 | 560 | 90.8 | — | Japanese sword action.png |
| Ladders and Ledges Animset.7z | 163 | 162 | 41.3 | — | Ladders and Ledges Animset.png |
| Launcher Animations.7z | 96 | 85 | 94.8 | — | Launcher Animations.png |
| Longsword Animset Pro.7z | 321 | 318 | 416.6 | — | Longsword Animset Pro.png |
| Loot Anim Set.7z | 89 | 88 | 22.0 | — | Loot Anim Set.png |
| Mage Animset.7z | 394 | 391 | 161.4 | — | Mage Animset.png |
| Magical Knight Set.7z | 222 | 220 | 90.1 | — | Magical Knight Set.png |
| Martial Arts Fight Game.7z | 216 | 215 | 38.2 | — | Martial Arts Fight Game.png |
| Mega Taunt Animation Pack.7z | 120 | 119 | 29.1 | — | Mega Taunt Animation Pack.png |
| Melee Weapon Stealth Finishers.7z | 61 | 60 | 20.7 | — | Melee Weapon Stealth Finishers.jpg |
| Mobility Pro  MoCap Pack.7z | 945 | 476 | 1074.6 | .fbx:458, .mb:2 | Mobility Pro  MoCap Pack.png |
| MOCAP 101 ANIMATIONS.7z | 353 | 352 | 416.9 | — | MOCAP 101 ANIMATIONS.jpg |
| MoCap Cycle Animation Pack 01.7z | 30 | 28 | 15.9 | — | MoCap Cycle Animation Pack 01.png |
| Modern Crossbow Animation Kit 426.7z | 314 | 172 | 120.7 | — | Modern Crossbow Animation Kit 426.png |
| Movement Animset Pro.7z | 393 | 392 | 97.7 | — | Movement Animset Pro.png |
| Ninja Pro - MoCap Pack.7z | 388 | 215 | 370.8 | .fbx:169, .mb:1 | Ninja Pro - MoCap Pack.png |
| Office Desk - MoCap Pack.7z | 120 | 55 | 78.0 | .fbx:38, .mb:1 | Office Desk - MoCap Pack.png |
| Open And Close Animation Pack.7z | 168 | 158 | 31.5 | — | Open And Close Animation Pack.png |
| Open World Animset.7z | 534 | 533 | 342.1 | — | Open World Animset.png |
| Oriental Spear Anim Set.7z | 97 | 96 | 23.4 | — | Oriental Spear Anim Set.png |
| Paladin Anim Set.7z | 193 | 192 | 70.8 | — | Paladin Anim Set.png |
| Pedestrian Walks.7z | 143 | 75 | 249.6 | .fbx:63, .mb:1 | Pedestrian Walks.png |
| Pedestrians.7z | 237 | 235 | 44.7 | — | Pedestrians.png |
| Pistol Animset Pro.7z | 238 | 236 | 326.9 | — | Pistol Animset Pro.png |
| Pistol Pro - MoCap Pack.7z | 472 | 236 | 457.6 | .fbx:218, .mb:1 | Pistol Pro - MoCap Pack.png |
| Pool Dives Animation Set.7z | 39 | 37 | 19.2 | — | Pool Dives Animation Set.png |
| Protector.7z | 463 | 462 | 212.3 | — | Protector.png |
| Punch! Animation Pack.7z | 64 | 63 | 19.1 | — | Punch! Animation Pack.png |
| Rapier Anim Set.7z | 167 | 166 | 59.7 | — | Rapier Anim Set.png |
| Realistic Female Player Anims.7z | 340 | 338 | 36.0 | — | Realistic Female Player Anims.png |
| Resource Gathering Animation.7z | 59 | 58 | 27.3 | — | Resource Gathering Animation.png |
| Rifle Animset Pro.7z | 300 | 298 | 451.5 | — | Rifle Animset Pro.png |
| Rifle Basic MoCap Pack.7z | 1676 | 786 | 1860.5 | .fbx:762, .ma:1 | Rifle Basic MoCap Pack.png |
| Rifle Pro - MoCap Pack.7z | 1564 | 786 | 1853.7 | .fbx:762, .ma:1 | Rifle Pro - MoCap Pack.jpg |
| Rolls and Dodges Animation.7z | 56 | 55 | 18.5 | — | Rolls and Dodges Animation.png |
| Rope Swing Climb.7z | 543 | 370 | 774.9 | .fbx:5 | Rope Swing Climb.png |
| Scared! - MoCap Pack.7z | 271 | 140 | 364.3 | .fbx:123, .mb:1 | Scared! - MoCap Pack.png |
| Side on Fighter - Animation Pack.7z | 94 | 93 | 24.6 | — | Side on Fighter - Animation Pack.jpg |
| Skydive and Parachute Kit.7z | 77 | 76 | 83.6 | — | Skydive and Parachute Kit.png |
| Stealth Finishers knife and hand.7z | 139 | 73 | 29.0 | — | Stealth Finishers knife and hand.png |
| Stylish Action Combat Animation Pack.7z | 159 | 157 | 38.8 | — | Stylish Action Combat Animation Pack.png |
| Superhero Flight Animations 426.7z | 358 | 345 | 311.8 | — | — |
| Supporter Motions.7z | 57 | 52 | 18.1 | — | Supporter Motions.png |
| Swimming Animation Set 422.7z | 60 | 41 | 33.6 | .fbx:18 | Swimming Animation Set 422.png |
| Sword Animset Pro.7z | 391 | 389 | 597.9 | — | Sword Animset Pro.png |
| Sword Shield Animset Pro.7z | 311 | 309 | 424.9 | — | Sword Shield Animset Pro.png |
| T Pose Zombie 2.7z | 89 | 87 | 120.0 | — | T Pose Zombie 2.png |
| The Mega Taunt Multi Pack.7z | 1230 | 1229 | 197.6 | — | The Mega Taunt Multi Pack.jpg |
| Twinblades Animset Base.7z | 76 | 74 | 21.8 | — | Twinblades Animset Base.png |
| Twinblades Animset Expansion.7z | 228 | 226 | 86.2 | — | Twinblades Animset Expansion.png |
| TwinDaggers Animset.7z | 356 | 354 | 105.1 | — | TwinDaggers Animset.png |
| TwinSword Animset Base.7z | 84 | 82 | 18.4 | — | TwinSword Animset Base.png |
| TwinSword Animset Expansion.7z | 291 | 290 | 94.3 | — | TwinSword Animset Expansion.png |
| Two Handed Sword.7z | 407 | 402 | 173.5 | — | Two Handed Sword.png |
| TwoSword Animation Set.7z | 106 | 105 | 18.7 | — | TwoSword Animation Set.png |
| Vampire Boss Set.7z | 83 | 82 | 22.0 | — | Vampire Boss Set.jpg |
| Wall Running Pack 425.7z | 50 | 43 | 22.1 | — | Wall Running Pack 425.png |
| Werewolf Animation Set.7z | 166 | 128 | 34.5 | — | Werewolf Animation Set.png |
| Witch Animation Set.7z | 124 | 123 | 56.2 | — | Witch Animation Set.jpg |
| Zombie Pro - MoCap Pack.7z | 640 | 330 | 674.2 | .fbx:303, .mb:1 | Zombie Pro - MoCap Pack.png |
| Zombie Starter MoCap Pack.7z | 105 | 52 | 130.0 | .fbx:35, .ma:1 | Zombie Starter MoCap Pack.png |

## 8. New MW2 gun library: does not fill the German WWII rifle gap

Opened file: 54 collections, including generic Collection and 53 weapon-labeled collections; 1,048 objects = 774 meshes + 274 armatures; no Actions. 1,571 image datablocks, 1,570 packed; remaining Render Result is not a missing external texture. Collections/rigs/attachments do not certify 53 UE-ready weapons or supplied animation.

Names and reviewed geometry indicate modern weapons, with no Kar98k/Gewehr/M1/MP40/StG candidates found. Even a German-designed modern gun is not 1944 equipment. Retain locally; no modern substitute, game import or SFTP publication. Possible game-export provenance is unverified and rights remain unknown.

| Collection label | Mesh objects | Rig objects | Raw triangles | Meshes without UV | Distinct materials | Bones per rig |
| --- | --- | --- | --- | --- | --- | --- |
| .50 GS | 12 | 6 | 35572 | 0 | 8 | 7; 2; 1; 22; 19; 1 |
| 556 Icarus | 17 | 5 | 55430 | 0 | 11 | 31; 33; 10; 1; 1 |
| BAS-P | 19 | 5 | 48230 | 0 | 14 | 1; 27; 37; 1; 15 |
| Basilisk  | 11 | 7 | 30508 | 0 | 9 | 3; 9; 1; 2; 25; 1; 1 |
| Bryson 800 | 13 | 4 | 22055 | 0 | 9 | 11; 7; 19; 2 |
| Bryson 890 | 16 | 5 | 46369 | 0 | 11 | 11; 9; 7; 16; 2 |
| Chimera | 13 | 5 | 26172 | 0 | 10 | 1; 27; 10; 1; 13 |
| Collection | 0 | 0 | 0 | 0 | 0 |  |
| EBR-14 | 13 | 5 | 34521 | 0 | 10 | 4; 31; 1; 9; 4 |
| Expedite 12 | 14 | 6 | 34576 | 0 | 12 | 1; 5; 1; 6; 30; 2 |
| Fennec 45 | 12 | 6 | 29188 | 0 | 10 | 1; 32; 9; 2; 6; 1 |
| FSS Hurricane | 13 | 5 | 47071 | 0 | 10 | 1; 23; 9; 56; 1 |
| FTac Recon | 11 | 5 | 35073 | 0 | 9 | 1; 29; 9; 14; 1 |
| HCR 56 | 16 | 5 | 33383 | 0 | 12 | 6; 1; 1; 35; 10 |
| JOKR | 19 | 2 | 28891 | 0 | 8 | 22; 2 |
| Kastov 545 | 12 | 5 | 32235 | 0 | 9 | 1; 26; 1; 10; 12 |
| Kastov 762 | 10 | 5 | 32589 | 0 | 8 | 10; 1; 26; 1; 12 |
| Kastov-74u | 12 | 5 | 30598 | 0 | 9 | 1; 25; 10; 13; 1 |
| LA-B 330 | 15 | 6 | 35542 | 0 | 12 | 7; 4; 9; 26; 1; 1 |
| Lachmann Sub | 18 | 5 | 29444 | 0 | 14 | 1; 22; 3; 10; 14 |
| Lachmann-556 | 14 | 5 | 37544 | 0 | 11 | 1; 21; 3; 36; 14 |
| Lachmann-762 | 19 | 5 | 27580 | 0 | 11 | 1; 21; 3; 10; 18 |
| LMS  | 21 | 6 | 52252 | 0 | 11 | 17; 3; 14; 22; 4; 1 |
| Lockwood 300 | 15 | 6 | 33710 | 0 | 12 | 6; 7; 26; 1; 2; 2 |
| Lockwood MK2 | 15 | 8 | 32281 | 0 | 13 | 2; 1; 22; 6; 1; 7; 1; 4 |
| M13B | 18 | 5 | 54413 | 0 | 12 | 1; 28; 36; 1; 16 |
| M16 | 13 | 5 | 60447 | 0 | 8 | 13; 18; 1; 27; 1 |
| m4a1 | 12 | 5 | 36194 | 0 | 10 | 1; 28; 1; 36; 14 |
| MCPR-300 | 17 | 7 | 39978 | 0 | 14 | 5; 3; 1; 10; 26; 1; 1 |
| Minibak  | 11 | 5 | 29166 | 0 | 9 | 27; 10; 4; 1; 1 |
| MP7 | 15 | 5 | 23722 | 0 | 12 | 4; 1; 10; 30; 1 |
| MX9 | 16 | 4 | 32164 | 0 | 11 | 1; 30; 11; 4 |
| P890 | 12 | 4 | 20380 | 0 | 6 | 9; 1; 14; 19 |
| PDSW 528 | 17 | 7 | 51021 | 0 | 11 | 6; 1; 1; 57; 10; 18; 1 |
| PILA | 15 | 2 | 46252 | 0 | 6 | 22; 9 |
| RAAL MG | 21 | 6 | 54405 | 0 | 14 | 4; 1; 31; 37; 2; 1 |
| RAPP H | 17 | 6 | 37530 | 0 | 13 | 1; 25; 24; 2; 13; 3 |
| REV G-80 | 23 | 1 | 49841 | 0 | 9 | 29 |
| RPG7 | 4 | 1 | 22387 | 0 | 3 | 14 |
| RPK | 13 | 5 | 30589 | 0 | 9 | 1; 26; 10; 15; 1 |
| SA-B 50 | 13 | 6 | 28200 | 0 | 9 | 1; 29; 1; 9; 3; 4 |
| sakin mg38 | 19 | 7 | 42644 | 0 | 15 | 37; 1; 37; 4; 2; 1; 1 |
| Signal 50 | 14 | 6 | 30440 | 0 | 10 | 5; 1; 9; 33; 1; 1 |
| SO-14 | 12 | 4 | 28617 | 0 | 8 | 3; 31; 9; 4 |
| SP-R 208 | 15 | 7 | 32708 | 0 | 11 | 1; 1; 27; 9; 1; 3; 4 |
| SPX-80 | 13 | 6 | 39676 | 0 | 11 | 4; 1; 9; 24; 1; 1 |
| STB 556 | 20 | 8 | 43297 | 0 | 16 | 1; 36; 34; 1; 1; 1; 1; 4 |
| Strela P | 9 | 1 | 18819 | 0 | 8 | 18 |
| TAQ-56 | 18 | 6 | 45534 | 0 | 12 | 9; 34; 13; 1; 4; 1 |
| TAQ-M | 14 | 5 | 40596 | 0 | 11 | 1; 1; 32; 11; 4 |
| TAQ-V | 16 | 6 | 33768 | 0 | 12 | 1; 34; 1; 9; 4; 3 |
| Vaznev-9K | 11 | 5 | 33982 | 0 | 8 | 1; 24; 10; 11; 1 |
| Victus XMR | 15 | 7 | 31646 | 0 | 13 | 4; 1; 6; 9; 20; 1; 3 |
| X12 | 11 | 5 | 14169 | 0 | 8 | 10; 1; 9; 13; 1 |

Counts use raw meshes, not evaluated modifiers/LOD/UE performance. Workbench views identify geometry; blue-gray diagnostic shading is not final PBR appearance. Packed textures do not certify materials.

![Lachmann-762 modern weapon geometry diagnostic](<LocalWorking/Validation/2026-10-03-asset-catalog-v1/Guns/views_v1/Lachmann-762_side.png>)

![SA-B 50 modern bolt-action geometry diagnostic](<LocalWorking/Validation/2026-10-03-asset-catalog-v1/Guns/views_v1/SA-B_50_side.png>)

![m4a1 modern weapon geometry diagnostic](<LocalWorking/Validation/2026-10-03-asset-catalog-v1/Guns/views_v1/m4a1_side.png>)

## 9. Actual use and avoid-repeat purchases

Later human review takes precedence: Yupu rejects current `Rifle_Reload_2` appearance. The earlier no-direct-replacement advice below is not visual acceptance. Next evaluate D059 Aim on the same target/M1/camera; no binding changed yet. A separate German rifle pilot is prepared, not a fix for M1 reload; see the updated comparison.

Actual three-clip comparison (42 phase images): current 2.17s, D059 aim 4.13s, relaxed 5.30s. Do not directly replace now; retain aim for a later same-target/weapon comparison, while relaxed starts/ends low and differs from current Ready. Empty-handed images on different source rigs do not accept M1 contact or FP quality. See the [reload comparison](../Docs/Development/RELOAD_COMPARISON_20261003.md).

![Current reload phases, upper rear and lower side](<LocalWorking/Validation/2026-10-03-asset-catalog-v1/Reload/compare_v4/current_allied_review_sheet_v2.png>)

![D059 aim reload source-rig candidate, not a gameplay replacement](<LocalWorking/Validation/2026-10-03-asset-catalog-v1/Reload/compare_v4/d059_aim_review_sheet_v2.png>)

Published playtest uses the existing Paris, US/German characters, RifleAnimsetPro actions and continuous arms; local PlayerActionsV6 drafts are not published. Rifle_Reload_2 is bound; D059 reloads are candidates. Burst/continuous clips existing does not mean they play in game or camera recoil is implemented. Reuse inventory before buying generic actions/modern guns. WWII German rifle and M1 moving bolt/en-bloc content remain open.

Paris context: 15,850 original Content files / 28,421,951,358 bytes; LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Content/WW2City. Not the new gun library; its transaction channel was not verified here.

## 10. Detailed indexes and evidence

- [Native asset / exact action index](XIAN_YU_NATIVE_ASSET_INDEX_20261003.md)
- [All archive native-name index](XIAN_YU_ARCHIVE_CONTENTS_20261003.md)
- [Private current facts JSON](LocalWorking/Validation/2026-10-03-asset-catalog-v1/Catalog/catalog_facts.json)
- [Private Blender object/rig/material/image inventory](LocalWorking/Validation/2026-10-03-asset-catalog-v1/Guns/views_v1/weapon_library_inventory.json)
- [Reload review](../Docs/Development/RELOAD_COMPARISON_20261003_ZH.md)
- [Original intake result](../Docs/Development/WEAPON_ASSET_VALIDATION_RESULT_20261001.md)
- [Selected rifle-motion baseline result](../Docs/Development/WEAPON_BASELINE_AND_RELOAD_RESULT_20261002.md)

## 11. 4 October muzzle VFX / duplicate motion intake

### 11.1 New flash and casing candidates

`LocalWorking/Intake/2026-10-04/01_Muzzle_Flash_VFX/`:68files,
78,239,739bytes (74.62MiB),67uasset+1umap. SHA/UE tags checked; bytes unchanged
after analysis. Actual header references use `/Game/MsvFx_MuzzleFlash_Pack/`, not
`/Game/Prefabs/`. All68headers have4.26.2/4.26.0 clues, not normalized or verified
as UE5.8 runtime content.

| Content/directory | Files | Observed scope/limit |
| --- | --- | --- |
| Prefabs | 10 | 4rifle flashes,3shotgun flashes,3casing-related candidates; NiagaraSystem/Emitter header hints, not fresh registry classes |
| Blueprints | 1 | BP_Ak47_Shot example, not executed/adopted as our gun logic |
| Maps | 2 | TestMap plus BuiltData, not our mission |
| Sources/Materials | 22 | Flash/smoke/Pyro/casings/example guns/ground masters and instances |
| Sources/Textures | 19 | Flash masks, smoke/explosion sheets, noise/swirl, AK47 textures |
| Sources/Meshes | 10 | Flash shapes,762mm/9mm/shotgun casings, AK47/M4/M1 carbine examples |
| Sources/Skeleton_Mesh | 3 | AK47 mesh/skeleton/physics-related packages; exact classes unverified |
| Sources/Animation | 1 | Anim_Ak_47, not accepted soldier recoil |

Exact prefab names keep vendor spelling:

- `Niagara_Riffle_MuzzleFlash_01`, `02`, `03`, `04`: rifle flash candidates first.
- `Niagara_Shotgun_Muzzle_Flash_01`, `02`, `03`: optional shotgun candidates.
- `Niagara_HiveShot_762MM`, `Niagara_HiveShot_9MM`, `Niagara_HiveShot_Shotgun`:
  actual header references identify their casing meshes/materials.

Flash/smoke candidates do not complete material-specific impacts or bullet decals.
No dedicated impact/decal kit identified here, but all Niagara sub-emitter behavior
was not inspected, so no stronger absence claim. M1 carbine is not our Garand;
modern AK/M4 do not replace existing guns, and generic casing labels do not prove
WWII mechanism/history. Select necessary effects/dependencies later, not the demo.

Local candidate only: no fresh UE5.8.2 load, emitted-image inspection, muzzle/rate/
direction calibration, performance, dependency-closure proof, upgrade/resave or
game binding. New VFX sharing rights unconfirmed. No SFTP move or receipt deletion.

### 11.2 Confirmed RifleAnimsetPro repeat, no new motions

`LocalWorking/Intake/2026-10-04/02_Firearm_Animations/`:301files,
473,848,190bytes (451.90MiB),297uasset+1umap+ZIP+promotional JPG+guide TXT.
Rehashed all300old originals against the existing original manifest successfully:

- All298native relative paths/sizes/SHA256 match; zero changed/new/missing files.
- SourceFiles.zip also matches exactly, SHA
  `9f0ddce451b29187eeccc86302137e7ee233e3ffd99f9a4bb7f4b36ec4bbc935`;
  324FBX/697,727,824expanded bytes, CRC passed, no unsafe paths, not extracted.
- Packaging differs through promotional/guide files, not new motions or native
  upgrades. No identifiable Release-version field found in motion originals;
  no title-based version claim.324FBX are not324new game actions.
-277AnimSequence names/durations are inherited from the dated actual UE inventory
  via SHA-identical originals, not a new277-clip load/playback. Original manifest
  is rifle-animset-pro-original.

Existing in-place candidates worth later review (prior UE durations, not new
target acceptance):

| Clip | Approx seconds | Meaning/limit |
| --- | --- | --- |
| Rifle_ShootOnce | 0.80 | Single-shot/recoil candidate, not confirmed currently triggered |
| Rifle_ShootLoop_Additive | 0.63 | Native4October audit says AAT_NONE despite name; not directly additive |
| Rifle_ShootBurst / Rifle_ShootBurstLong | 1.70 /2.77 | Burst family, not final M1 choice by default |
| Rifle_Reload_2 | 2.17 | Bound but human-rejected; repeated delivery adds no standing reload |
| Rifle_Crouch_Reload / Rifle_Crouch_Reload2 / Rifle_Prone_Reload | 2.07 /2.40 /2.40 | Sources only, low-pose firing/reload prohibition unchanged |
| HolsterRifle / EquipRifle | 1.80 each | Carry candidates, not accepted prone/back transition |
| Rifle_SprintStart / Rifle_SprintLoop / both stops | — | Existing family, buying twice cannot fix display attachment |

Reuse the existing licensed baseline; compare D059 reload on the actual target
separately. No new motion creation. Duplicate retained LocalWorking, not uploaded/
released/bound again; no deletion without a separate user request.

![Seller promotional image, not our runtime acceptance](<LocalWorking/Intake/2026-10-04/02_Firearm_Animations/主图.jpg>)

### 11.3 Evidence and limits

- [Receipt hashes and duplicate proof](Integration/XIAN_YU_INTAKE_AUDIT_20261004.json).
- [Private complete audit](LocalWorking/Validation/2026-10-04-xianyu-intake-v1/Audit/intake_audit.json),
  478,065bytes, SHA`c8497e1d…1c6d8b5`, ignored local evidence.
-412protected gameplay/model/source inputs unchanged. No UE launch, original/map
  resave, VFX/recoil/reload implementation, SFTP publication, commit or push.
  File-content discovery is not runtime acceptance.

### 11.4 Subsequent animation implementation

Receipt now has [DUPLICATE.md](LocalWorking/Intake/2026-10-04/02_Firearm_Animations/DUPLICATE.md),
without reupload; original301-file receipt statistics exclude this new marker.
Actual-target D059 reload shows severe obstruction/sleeve defects, unselected.
Rifle_ShootOnce owner authoring crashed twice, no saved owner, recoil still open.
Formal old Reload_2 dependency not physically deleted;507 protected files unchanged.
See [result](../Docs/Development/WEAPON_ANIMATION_REUSE_RESULT_20261004.md) and
[AN001](../Failures/AN001-20261004-existing-weapon-animation/FAILURE_ANALYSIS.md).
This later implementation does not rewrite the prior read-only receipt scope11.3.
