# 闲鱼已下载资产详细清单

2026-10-03 · yg745 · 本机盘点，不是发布清单。

**10月4日补录：** 新枪口特效68文件；新动作交付的298个原生文件及SourceFiles.zip
与已有RifleAnimsetPro逐项SHA完全相同，确定重复，无新增动作，详见第11节。
这次仅文件／包头／ZIP检查，未导入正式游戏。旧“德军枪模缺口”是当时记录；
目前V15静态枪已认可共享，见[现有枪模说明](GERMAN_RIFLE_MODEL.md)，不用重买裸枪。

范围：此前两批士兵/动作、ShooterStarter、D059、125包UE4动作合集及新MW2枪械库。巴黎地图另列背景依赖；现有记录指向Meshingun Studio/Fab，不能据此断言其交易渠道也是闲鱼。旧Normandy/Lux3D实验不列为可用生产资产。

本次：实际核对原文件存在/大小，读取125个压缩包内部目录，Blender安全打开新枪库并检查截图。旧UE类别/骨架/动作时长来自注明日期的实际加载记录，并非本次重新逐动作运行。资产名、宣传图、成功导入均不能证明历史正确或运行可用。

图片仅在本机私有目录中，Markdown直接引用已有图片，没有把商业资产或截图复制到Git。组员需要对应私有证据文件才能显示。新MW2包三人共享/来源授权尚未确认，保留LocalWorking；之前的共享确认不自动覆盖这次。

## 1. 下载批次总览

| Bundle | Files | Original size | Present / coverage | Physical location relative to Assets |
| --- | --- | --- | --- | --- |
| German Soldier WWII | 104 | 294,224,744 B (0.274 GiB) | 104 | LocalShared/SFTP/baselines/character-original-intake/character-20261001-v1/CHAR-G-GermanSoldierWWII |
| US Paratrooper | 186 | 478,639,266 B (0.446 GiB) | 186 | LocalShared/SFTP/baselines/character-original-intake/character-20261001-v1/CHAR-A-USSoldier |
| Rifle Animset Pro | 300 | 473,464,019 B (0.441 GiB) | 300 | LocalShared/SFTP/baselines/character-original-intake/character-20261001-v1/ANI-TP-RifleAnimsetPro |
| D059 Rifle Pro - MoCap Pack | 1563 | 1,944,249,213 B (1.811 GiB) | 1563 | LocalShared/SFTP/baselines/rifle-pro-mocap-original/rifle-motion-20261002-v1 |
| ShooterStarter FPS Arm A | 607 | 3,154,499,065 B (2.938 GiB) | 607 | LocalWorking/Intake/2026-10-01/01_ShooterStarter_FPS_Arm_A |
| UE4 animation collection | 250 | 24,108,906,232 B | 125 archives + 125 previews | LocalWorking/Intake/2026-10-01/03_UE4_Animation_Collection/ |
| MW2_Guns_Asset_Library.blend | 1 | 2,364,179,404 B (2.202 GiB) | 1 | LocalWorking/Intake/2026-10-03/01_MW2_Guns_Asset_Library/ |
| MsvFx_MuzzleFlash_Pack（10月4日新增候选） | 68 | 78,239,739 B | 文件／包头SHA检查；未运行 | LocalWorking/Intake/2026-10-04/01_Muzzle_Flash_VFX/ |
| RifleAnimsetPro（10月4日重复交付） | 301 | 473,848,190 B | 298原生＋源ZIP均与旧版SHA一致；无新增动作 | LocalWorking/Intake/2026-10-04/02_Firearm_Animations/ |

上表大小是原始交付，不要与整合版本相加当作唯一文件总量；整合文件、别名与对象版本有重叠。存在/大小核对不是本轮全旧包SHA校验。

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

有两套完整德军人物、无头/装备相关网格、7条原包动作、56张Texture2D。已修复整合基线在character-ue582-v1；德军平移动作适配有后续记录。MP40只是冲锋枪，不是德军步枪。

模型及骨架：

| Asset | Class | Bones | LOD / materials | Skeleton |
| --- | --- | --- | --- | --- |
| /Game/GermanSoldier/Meshes/Equipment/SK_WWII_GermanSoldier_equpA | SkeletalMesh | 69 | 1 / 5 | /Game/GermanSoldier/Meshes/SK_WWII_GermanSoldier_simple_Skeleton.SK_WWII_GermanSoldier_simple_Skeleton |
| /Game/GermanSoldier/Meshes/Equipment/SK_WWII_GermanSoldier_equpB | SkeletalMesh | 69 | 1 / 5 | /Game/GermanSoldier/Meshes/SK_WWII_GermanSoldier_simple_Skeleton.SK_WWII_GermanSoldier_simple_Skeleton |
| /Game/GermanSoldier/Meshes/SK_WWII_GermanSoldier_noHead | SkeletalMesh | 68 | 1 / 3 | /Game/GermanSoldier/Meshes/SK_WWII_GermanSoldier_simple_Skeleton.SK_WWII_GermanSoldier_simple_Skeleton |
| /Game/GermanSoldier/Meshes/SK_WWII_GermanSoldier_varA | SkeletalMesh | 69 | 1 / 10 | /Game/GermanSoldier/Meshes/SK_WWII_GermanSoldier_simple_Skeleton.SK_WWII_GermanSoldier_simple_Skeleton |
| /Game/GermanSoldier/Meshes/SK_WWII_GermanSoldier_varB | SkeletalMesh | 69 | 1 / 9 | /Game/GermanSoldier/Meshes/SK_WWII_GermanSoldier_simple_Skeleton.SK_WWII_GermanSoldier_simple_Skeleton |
| /Game/GermanSoldier/Meshes/Weapon/SM_WWII_MP40 | StaticMesh | — | — / 1 | — |

换弹/射击相关原始动作名（这里只筛名称；后坐视觉和实际绑定另验）：

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

有两套完整美军伞兵、无头/装备网格、M1 Garand外观，5条原包动作、83张Texture2D。现有M1为一骨骼刚性外观，不能据此证明独立枪机/漏夹可动。

模型及骨架：

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

换弹/射击相关原始动作名（这里只筛名称；后坐视觉和实际绑定另验）：

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

277条AnimSequence，含原地/根运动、持枪移动、跑跳蹲趴、开火、换弹、受击/死亡等家族；下方原始名表才是精确目录。当前真正绑定换弹是Rifle_Reload_2，不是D059。

模型及骨架：

| Asset | Class | Bones | LOD / materials | Skeleton |
| --- | --- | --- | --- | --- |
| /Game/RifleAnimsetPro/UE4_Mannequin/Mesh/SK_Mannequin | SkeletalMesh | 68 | 1 / 2 | /Game/RifleAnimsetPro/UE4_Mannequin/Mesh/UE4_Mannequin_Skeleton.UE4_Mannequin_Skeleton |

换弹/射击相关原始动作名（这里只筛名称；后坐视觉和实际绑定另验）：

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

761条AnimSequence，含原地/根运动及站立/蹲姿单发、点射、连射、瞄准/放松换弹。70骨mannequin；现代M4预览模型不选择为二战武器。15条动作/33原生依赖+配置共35文件已选SFTP基线；整个原包没有全量进入游戏。选中换弹不等于当前换弹已切换。

模型及骨架：

| Asset | Class | Bones | LOD / materials | Skeleton |
| --- | --- | --- | --- | --- |
| /Game/Rifle_01/Character/Mesh/M4_Rifle_01 | StaticMesh | — | — / 1 | — |
| /Game/Rifle_01/Character/Mesh/SK_Mannequin | SkeletalMesh | 70 | 1 / 2 | /Game/Rifle_01/Character/Mesh/UE4_Mannequin_Skeleton.UE4_Mannequin_Skeleton |

换弹/射击相关原始动作名（这里只筛名称；后坐视觉和实际绑定另验）：

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

候选双臂与左右分离网格，现代袖子/手套；现代步枪和附件。14条动画中7条是demo手臂动作、7条是武器/附件动作。武器Reload驱动枪械零件，不代表配套第一人称双手换弹。旧直接套D059的取景/参考姿态试验失败；保持LocalWorking，不用于替换已认可连续手臂。

模型及骨架：

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

换弹/射击相关原始动作名（这里只筛名称；后坐视觉和实际绑定另验）：

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

## 7. UE4动作合集：125包内部目录已读，无全量解压

125个压缩包全部内部目录读取成功；成员/原生文件数并不是动画条数，.uasset还可能是模型、材质、骨架、蓝图。完整原始目录见私有catalog_facts.json，原生包名索引见附录。仅按标题/内部名字筛选，不运行包中脚本或工程。四个旧重复筛查包的CRC/大小结果不是SHA相同证明。

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

## 8. 新MW2枪械库：不补二战德军步枪

文件实际打开：54个集合，其中Collection为泛用集合，另53个有武器标签；1048对象=774网格+274骨架；无Action。1571个image datablock，1570打包，剩余Render Result不是缺失外部贴图。集合、骨架/附件不是53套UE可用枪，也不证明动画存在。

名称及已检查外观均指向现代武器，未见Kar98k/Gewehr/M1/MP40/StG等二战候选。Lachmann等名称即使对应德国设计也不是1944装备。保留本机参考；不把现代枪作为德军武器替代，不直接迁入游戏/SFTP。来源可能涉及游戏导出，但本轮未验证，权利未知。

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

上表统计原网格，不含modifier求值/LOD/UE性能认证。Workbench图只供几何辨识，局部蓝灰诊断色不等于正式PBR贴图效果；贴图打包不等于材质正确。

![Lachmann-762 modern weapon geometry diagnostic](<LocalWorking/Validation/2026-10-03-asset-catalog-v1/Guns/views_v1/Lachmann-762_side.png>)

![SA-B 50 modern bolt-action geometry diagnostic](<LocalWorking/Validation/2026-10-03-asset-catalog-v1/Guns/views_v1/SA-B_50_side.png>)

![m4a1 modern weapon geometry diagnostic](<LocalWorking/Validation/2026-10-03-asset-catalog-v1/Guns/views_v1/m4a1_side.png>)

## 9. 当前使用与不应重复买的内容

后续人工复核优先：Yupu否决了当前`Rifle_Reload_2`的观感；下面“暂不直接替换”是较早的技术建议，不是视觉接受。下一步评估同角色/同M1/同镜头的D059 Aim候选；尚未更改绑定。另准备德军枪模试验，不能用它解决M1换弹，详见更新后的对比报告。

本轮实际比较三条换弹（42张相位图）：当前2.17秒，D059瞄准4.13秒，D059放松5.30秒。建议暂不直接替换；瞄准版保留为后续同目标士兵/同武器对照候选，放松版起止低持枪与当前Ready不同。不同源骨架的空手图不是M1接触或第一人称验收。完整理由见[换弹对比报告](../Docs/Development/RELOAD_COMPARISON_20261003_ZH.md)。

![当前换弹七相位：上排后方、下排侧方](<LocalWorking/Validation/2026-10-03-asset-catalog-v1/Reload/compare_v4/current_allied_review_sheet_v2.png>)

![D059瞄准换弹七相位：源骨架候选，未替换游戏](<LocalWorking/Validation/2026-10-03-asset-catalog-v1/Reload/compare_v4/d059_aim_review_sheet_v2.png>)

当前发布版使用现有巴黎地图、美军/德军角色、RifleAnimsetPro动作及连续手臂；本地PlayerActionsV6等尚未发布。换弹Rifle_Reload_2在用，D059两条换弹只是候选；原包连射/点射存在不等于当前已播放或镜头后坐已实现。先适配库存，不重复买通用动作/现代枪。德军二战步枪和M1可动枪机/漏夹专用内容仍未被这批解决。

巴黎环境参考：原生Content清单15,850文件/28,421,951,358字节，路径LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Content/WW2City；不属于此次新增枪库。素材交易渠道没有在本轮核实。

## 10. 详细索引与证据

- [Native asset / exact action index](XIAN_YU_NATIVE_ASSET_INDEX_20261003.md)
- [All archive native-name index](XIAN_YU_ARCHIVE_CONTENTS_20261003.md)
- [Private current facts JSON](LocalWorking/Validation/2026-10-03-asset-catalog-v1/Catalog/catalog_facts.json)
- [Private Blender object/rig/material/image inventory](LocalWorking/Validation/2026-10-03-asset-catalog-v1/Guns/views_v1/weapon_library_inventory.json)
- [Reload review](../Docs/Development/RELOAD_COMPARISON_20261003_ZH.md)
- [Original intake result](../Docs/Development/WEAPON_ASSET_VALIDATION_RESULT_20261001.md)
- [Selected rifle-motion baseline result](../Docs/Development/WEAPON_BASELINE_AND_RELOAD_RESULT_20261002.md)

## 11. 10月4日补录：枪口特效与重复动作包

### 11.1 枪口火焰／弹壳特效：新增候选

位置：`LocalWorking/Intake/2026-10-04/01_Muzzle_Flash_VFX/`。
68文件／78,239,739字节（74.62 MiB），67个uasset＋1个umap，全部已算SHA、
检查UE包标记并在分析结束后复核原字节未变。实际包内引用根为
`/Game/MsvFx_MuzzleFlash_Pack/`，后续不能随便摆成`/Game/Prefabs/`破坏引用。
68包头均找到4.26.2／4.26.0版本线索，未重存为UE5.8或验证其运行兼容。

| 目录内容 | 文件数 | 实际发现／边界 |
| --- | --- | --- |
| Prefabs | 10 | 步枪闪光4个、霰弹枪闪光3个、弹壳相关3个；包头含NiagaraSystem／Emitter，不冒称已通过原生加载 |
| Blueprints | 1 | BP_Ak47_Shot示例蓝图，未执行，不复制其现代枪械逻辑 |
| Maps | 2 | TestMap.umap＋TestMap_BuiltData.uasset，非我方关卡 |
| Sources/Materials | 22 | 闪光、枪口烟、Pyro、弹壳、示例枪／地面主材质和实例 |
| Sources/Textures | 19 | 闪光／遮罩、烟雾／爆炸序列图、噪声／Swirl及AK47贴图 |
| Sources/Meshes | 10 | 闪光形体、762mm／9mm／霰弹壳、AK47／M4／M1 carbine示例网格 |
| Sources/Skeleton_Mesh | 3 | AK47骨架／网格／物理相关包，实际类别仍待注册表核对 |
| Sources/Animation | 1 | Anim_Ak_47，不认定为我方人物后坐力动作 |

精确预制名保留卖家原拼写`Riffle`：

- `Niagara_Riffle_MuzzleFlash_01`、`02`、`03`、`04`：优先评估的步枪枪口候选。
- `Niagara_Shotgun_Muzzle_Flash_01`、`02`、`03`：霰弹枪候选，当前不必接入。
- `Niagara_HiveShot_762MM`、`Niagara_HiveShot_9MM`、`Niagara_HiveShot_Shotgun`：
  包头实际引用对应弹壳网格／材质，不是凭名猜成命中反馈。

能补的是枪口闪光／烟雾候选，不等于补齐材质专用命中／弹痕。目录未识别专用
表面命中／弹痕套件，但本次未检查全部Niagara子发射器，不作更强缺失断言。
M1 carbine不是当前Garand；AK47／M4不替换我方枪械；通用弹壳口径名不是二战
机械／历史匹配证明。后续只取所需特效及依赖，不整包搬示例工程。

状态：本机候选，未fresh-load UE5.8.2、未看实际发射画面、未校准枪口方向／
频率或测性能，原生依赖闭合未证明，未升级／绑定游戏。新特效组内共享授权
待确认，未迁入SFTP，未删任何收货文件。

### 11.2 RifleAnimsetPro：确定重复，没有新增动作

位置：`LocalWorking/Intake/2026-10-04/02_Firearm_Animations/`。
301文件／473,848,190字节（451.90 MiB）：297个uasset、1个umap、1个ZIP、
1张宣传jpg、1个使用说明txt。对照旧原清单及实际原文件，300个旧文件重哈希
全部匹配，比较结果如下：

- 新旧298个原生文件逐相对路径、大小、SHA-256完全一致：零差异、零新增、零缺失。
- SourceFiles.zip也完全一样，SHA
  `9f0ddce451b29187eeccc86302137e7ee233e3ffd99f9a4bb7f4b36ec4bbc935`。
  内部324个FBX／697,727,824字节，CRC全部通过、无危险路径；只读，不解压另存。
- 差别仅宣传图／说明等交付包装，无新动作或升级原生版本。原动作包头没有可识别
  Release版本字段，不能靠标题定版；324个FBX也不是324条新增游戏动作。
- 既有真实UE盘点记录有277个AnimSequence；通过原字节一致性关联旧名称／时长，
  不虚报本次重新加载／播放277个片段。原清单为rifle-animset-pro-original。

已有原地动作中，后续可继续评估：

| 动作 | 旧UE记录时长约秒 | 用途／限制 |
| --- | --- | --- |
| Rifle_ShootOnce | 0.80 | 单次射击／后坐候选，不等于当前已触发 |
| Rifle_ShootLoop_Additive | 0.63 | 名称带Additive但10月4日原生实查AAT_NONE，不能直接当叠加动作 |
| Rifle_ShootBurst／Rifle_ShootBurstLong | 1.70／2.77 | 连射家族，不自动用作M1最终动作 |
| Rifle_Reload_2 | 2.17 | 当前已用且用户否决观感，重复包没有新站姿换弹 |
| Rifle_Crouch_Reload／Rifle_Crouch_Reload2／Rifle_Prone_Reload | 2.07／2.40／2.40 | 库存源动作，不解除低姿态禁射／禁换弹 |
| HolsterRifle／EquipRifle | 各1.80 | 收取枪候选，不等于已适配匍匐背枪 |
| Rifle_SprintStart／Rifle_SprintLoop／两种Stop | — | 已有冲刺家族，再买一份不能修复显示挂接 |

动作继续从旧已许可baseline复用，换弹另看D059同目标对照，不自制新动作。
本次重复副本留在LocalWorking，未重复上传／发布／绑定；未经用户要求不删除。

![卖家宣传图，非我方实际运行验收](<LocalWorking/Intake/2026-10-04/02_Firearm_Animations/主图.jpg>)

### 11.3 本次证据与范围

- [新收货哈希与重复结论元数据](Integration/XIAN_YU_INTAKE_AUDIT_20261004.json)。
- [私有逐文件／包头／ZIP证据](LocalWorking/Validation/2026-10-04-xianyu-intake-v1/Audit/intake_audit.json)，
  478,065字节，SHA`c8497e1d…1c6d8b5`；原文件保持本机ignored存储。
- 412个受保护游戏／模型／源动作前后不变；未启动UE、未保存原包／地图、未实现
  特效／后坐力／换弹、未发SFTP、未commit／push。文件内容发现不等于运行验收。

### 11.4 后续动作实施检查点

下载动作目录已放[DUPLICATE.md](LocalWorking/Intake/2026-10-04/02_Firearm_Animations/DUPLICATE.md)，
不重复上传。原收货301文件统计不含本次新增标记。随后实际目标上的D059换弹
出现严重遮挡／袖片异常，不选中；独立Rifle_ShootOnce后坐力作者两次崩溃、
未落盘，尚未修复。旧Reload_2正式依赖未物理删除。507个受保护文件不变。
见[结果](../Docs/Development/WEAPON_ANIMATION_REUSE_RESULT_20261004_ZH.md)及
[AN001](../Failures/AN001-20261004-existing-weapon-animation/FAILURE_ANALYSIS.md)。
此后续实施不改变11.3对先前只读收货核对的历史范围。
