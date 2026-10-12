# 完整玩法正式基线采用与本机清理结果

2026-10-11。用户人工确认逻辑无问题，最新手持装备finalv4正式采用。衣服／衣袖遮挡小问题保留为后续修复；本次没有改源码／Game或重跑引擎验收。

正式源精确76文件 `Unreal/Variants/G1GrenadeEquip20261011/Project`，Game `b5357cd4ff39454ec40d72ba96ce8ab379f0e039c83b6170263f631e45c4124d`，manifest `9ac0620c0794c2cc64c0b701d50e7dba4a82941bee7d147be1f72cd604d9312d`。已有稳定入口 `PLAY_CURRENT_G1.cmd` 指向不移动的 `tmp/Playtest-G1-GrenadeEquip-20261011/PLAY_GRENADE_EQUIP.cmd`。最新用户存档保持原目录／前缀。15项最终Game已有检查身份核对通过，原生1754、模型／原枪械手指参数／枪械／存档及原用户文件保持。

删除七个旧普通试玩及旧Runtime／Archive／Binaries／闲置编译缓存，共244个冻结目录，逻辑量365.76GiB。扣除私有去重恢复ZIP（7.25GiB）及元数据备份后，D盘实测净增加38.36GiB；hardlink及同期其他写入会使实际数与逻辑数不同。524份小型构建元数据保留，PCH／obj重新构建。完整退休清单SHA `08172013ec8c252d5873ec3f8ceb27839795202f418b2c247bee77ba7b41c19c`，恢复映射SHA `044f960d3ef1ec9fb83d797dd9b9340e3bf7e6c96c7e7fddf57e1825b74575ef`。

保留全部源／compiled-source-game、失败原收据／日志／图、Saved/Cooked、原资产／动作／模型／贴图／音频、全部用户档、已有恢复ZIP、最新作者工程及final build_v4。运行中full_v8／full_v16工程不动，两个Editor保持开启。上一正式enemy-clear52普通包只保留一份供已有恢复依赖使用，其源码／记录保持。所有目标已移除，12147项保留文件及最新用户文件逐项核对，唯一恢复对象回读通过。

实时Editor日志追加曾使初次回读停止，未删除目录；初始清单原样保留。仅两份已识别的活动日志使用完整快照与原冻结前缀SHA核验，允许引擎继续追加，不把活动日志全文件误称固定。其他保护文件、退休清单和恢复字节未放宽。

用户日志里的既有UVChannelData报告仍是handled Ensure（IsEnsure=true），最新手动会话日志正常退出；原文件保留，不称为新增崩溃或零警告通过。衣袖、精细全程接触／运动、大量NPC压力、匹配Editor和第二机仍是后续工作。人工逻辑通过不等于这些全部通过。

见[实施](G1_GAMEPLAY_BASELINE_ADOPTION_20261011_ZH.md)、[正式选择器](CURRENT_DEVELOPMENT_BASELINE.json)、[退休／恢复映射](G1GameplayBaselineAdoption20261011/RECOVERY_MAP_20261011.json)。本机采用没有Git提交／推送、SFTP清理／同步、课程PDF／视频改动；旧公开／课程交付属于旧audioV2发布身份。
