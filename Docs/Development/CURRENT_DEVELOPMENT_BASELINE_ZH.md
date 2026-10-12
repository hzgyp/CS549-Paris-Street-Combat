## 2026-10-11：最新正式76版已同步SFTP

最新组员包 `/releases/paris-g1-playtest-20261011-gameplay-v1/Paris-G1-Gameplay-20261011.zip`；精确76源／运行资源／SHA及恢复步骤见[最新同步指南](TEAM_CURRENT_BUILD_20261011_ZH.md)。原老师audioV2下载及课程附件保留，以下旧日期文字为历史。衣袖遮挡待修；新的76版外机验证由组员进行。

# 当前正式开发基线

2026-10-11，用户人工验证完整玩法统一版，确认逻辑无问题，要求正式采用；仍有衣服／衣袖遮挡小问题，保留为待修项。

正常入口 `tmp/Playtest-G1-GrenadeEquip-20261011/PLAY_GRENADE_EQUIP.cmd`；已有稳定入口 `PLAY_CURRENT_G1.cmd` 指向同一程序。包继续留在专用tmp目录。存档继续使用 `%LOCALAPPDATA%/ParisStreetCombat/G1GrenadeEquip20261011`，前缀 `ParisGrenadeEquipV2`；未移动、覆盖或合并旧用户存档。

当前精确76文件源 `Unreal/Variants/G1GrenadeEquip20261011/Project`，制作工程 `tmp/g1-tactical-equipment-20261010/candidate_grenade_equip_v1/Project/WW2FranceLiberation.uproject`（历史v1目录含final build_v4）。Game SHA256 `b5357cd4ff39454ec40d72ba96ce8ab379f0e039c83b6170263f631e45c4124d`；manifest `9ac0620c0794c2cc64c0b701d50e7dba4a82941bee7d147be1f72cd604d9312d`。源码和已验证可执行字节均不变。本次没有重新构建／进入Editor；现有两个Editor保持开启，不能把旧Editor DLL当76版。

承接手雷／烟雾、长按准备松手投出／取消、可用库存轮换、地图地雷爆炸与附近拆除、有限弹药补给、战地手册UI、人物小队信息及死亡倒地后重开。两种投掷物全耗尽时保持步枪；原步枪手指常量／持枪分支、人物模型、枪械／资源、原全灭敌军圈内E保存校验保持。原步行2.2／跑步4.5米每秒、8+10初始子弹保留。

已有15项最终Game检查及实际就绪／长按图通过，最新人工逻辑通过。当前人数短性能记录与隔离夹具不等于新增大量NPC、全程精细接触、第二机或课程验收。衣袖遮挡及其余表现／玩法／NPC压力工作留在待办。

七份旧普通试玩、旧Runtime／Archive／Binaries和闲置构建缓存按[实施](G1_GAMEPLAY_BASELINE_ADOPTION_20261011_ZH.md)及[结果](G1_GAMEPLAY_BASELINE_ADOPTION_RESULT_20261011_ZH.md)清理；原源码、失败／日志／图／检测、Saved/Cooked、资产及用户档保留。唯一旧二进制见[恢复映射](G1GameplayBaselineAdoption20261011/RECOVERY_MAP_20261011.json)，缓存有小型元数据备份、需要重新编译。上一正式52普通包保留一份支持既有恢复引用，不再保留七份过渡试玩。运行中full_v8／full_v16作者目录未动。

正式选择只在本机完成。本轮未commit／push或SFTP同步，原课程包／视频／外机记录仍属于更早的audioV2发布，不能视为最新76交付。早前状态属于有日期的历史，以JSON选择器为准。
