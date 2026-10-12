# 最新正式试玩与源码同步

2026-10-11，最新正式版为人工通过逻辑的76文件G1GrenadeEquip，衣袖遮挡仍待修。

## 直接玩最新版本

先正常git pull --ff-only，同步后以CURRENT_DEVELOPMENT_BASELINE.json为准。
通过已有团队SFTP账号／私下提供的密钥／固定可信主机指纹下载：

`/releases/paris-g1-playtest-20261011-gameplay-v1/Paris-G1-Gameplay-20261011.zip`

ZIP 8,499,470,074字节，SHA256 `42c20e46d3cda0511be0351e1733d6fd8bb469e700ebf7d5b3cf8a33f1c06349`；完整解压，运行PLAY_GRENADE_EQUIP.cmd。
无需安装UE／Python即可试玩，微软x64运行库按需安装。中文操作与正式采用状态见包内FORMAL_README_ZH.md。
SOURCE_VARIANT.json标记源码／Game；Game `b5357cd4ff39454ec40d72ba96ce8ab379f0e039c83b6170263f631e45c4124d`。不要只取exe，不复制他人存档。

本版包括手雷／烟雾的可用库存滚轮切换、左键长按准备／松开投出、地雷拆除／爆炸、有限补给、战地手册／小队UI、第三视角死亡倒地与原全灭敌军圈内E持久保存。原模型、枪械手指常量及原枪械／资源／存档保护；15项同一Game既有检查及用户逻辑验证通过，衣袖、细致全程接触、匹配Editor、新外机和大量NPC压测仍分开处理。

## 要继续源码开发

精确源在Unreal/Variants/G1GrenadeEquip20261011/Project，76文件，manifest `9ac0620c0794c2cc64c0b701d50e7dba4a82941bee7d147be1f72cd604d9312d`。
城市／原生359仍按TEAM_PLAYTEST_ZH.md恢复；其原Editor DLL不代表新的76源码。
新运行资源清单 `paris-g1-gameplay-runtime-resources.json` 位于Assets/Sync/manifests，包含私有Audio／Equipment／UI，Catalog固定字节。
可直接用已核验的完整解压包准备新的tmp制作工程：

```powershell
python Tools/Integration/G1GameplayPublication20261011/prepare_source_project.py --packaged-root 'C:/Games/Paris-G1-Gameplay-20261011'
```

它逐项验证包内文件，复制精确76源及资源，并联接已恢复的本机Content；不覆盖原工作，不复制旧DLL、不自动启动或保存UE。
随后使用本机UE5.8.2构建匹配Editor／Game。包和源码同步成功不表示新电脑已经验证，仍由组员实际试玩。

## 老师评阅包保留

老师旧下载仍为 `/releases/paris-g1-playtest-20261009-audio-v2/Paris-G1-Audio-V2-20261009.zip`，SHA `7a8c225ad66ea673e20d0259324c3b5fef25be25bb66fcdddb5344533bd26d7d`。原课程访问目录／私密附件ZIP／两页PDF／密钥保持原字节。
独立保留清单 `paris-g1-course-review-package.json` 将它与最新组员试玩区分；老师视频及此前外机证明属于原audioV2身份。
目前SFTP的旧HUD ZIP此前已删，剩下唯一较早试玩ZIP正是老师包，本次没有其它可安全删除的旧试玩字节。
未删除原生资产、原始包、workspaces／incoming、哈希对象历史或恢复依赖。
