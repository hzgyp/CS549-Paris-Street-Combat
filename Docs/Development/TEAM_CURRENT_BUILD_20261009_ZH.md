## 2026-10-11：最新正式76版已同步SFTP

最新组员包 `/releases/paris-g1-playtest-20261011-gameplay-v1/Paris-G1-Gameplay-20261011.zip`；精确76源／运行资源／SHA及恢复步骤见[最新同步指南](TEAM_CURRENT_BUILD_20261011_ZH.md)。原老师audioV2下载及课程附件保留，以下旧日期文字为历史。衣袖遮挡待修；新的76版外机验证由组员进行。

## 11October2026 current local gameplay revision

The latest formal local revision is manually accepted76 `G1GrenadeEquip20261011`; read [current baseline](CURRENT_DEVELOPMENT_BASELINE.md). Minor sleeve occlusion remains. No new package sync happened in adoption; the SFTP course release below remains the earlier audioV2, not this76 source.

## 10October2026 current local revision

The current manually accepted local source is exact52 `Unreal/Variants/G1EnemyClearCheckpoint20261010/Project`; see [current baseline](CURRENT_DEVELOPMENT_BASELINE.md). Local entry `PLAY_CURRENT_G1.cmd`. The audioV2 SFTP download described below is the prior published/course revision and remains available; it does not contain the latest checkpoint repair. No new package sync occurred in this local adoption task.

# 当前私有试玩与源码

2026年10月9日。Yupu人工复验音效V2通过并选作开发基础。实际交付与清理见
G1_AUDIO_BASELINE_PUBLICATION_RESULT_20261009_ZH.md，[英文原文](TEAM_CURRENT_BUILD_20261009.md)。

保留未完成源码与Git忽略的资产后，对当前干净克隆执行`git pull --ff-only`。
旧含资产历史的克隆按安全重新加入流程处理，不合并旧历史。当前源码是
`Unreal/Variants/G1FootContactAudio20261009/Project`精确42文件，以基线选择器为准。

向Yupu私下获取SFTP账户/地址/可信指纹，下载
`/releases/paris-g1-playtest-20261009-audio-v2/Paris-G1-Audio-V2-20261009.zip`。
按Assets/Sync/manifests/paris-g1-packaged-playtest.json核对SHA256/大小，完整解压
至可写Windows目录，启动PLAY_G1_REVISION.cmd；操作/运行库见README_ZH.md。
试玩无需编辑器/Python，不含个人存档/凭据，商业烹饪资产仅供三名有授权组员
私下使用，旧HUD下载ZIP已退休。

编辑资产仍按TEAM_PLAYTEST_ZH.md恢复未改动的native359/城市；旧缓存编辑器DLL
不代表较新的Game音效源码。独立可写wrapper覆盖选定42文件Project相对路径，按
paris-g1-recorded-audio.json恢复33 WAV并复制至wrapper的Audio目录；
AUDIO_MANIFEST.json复制为Audio/PROVENANCE.json，AUDIO_CREDITS.txt复制为
Audio/CREDITS.txt。保留独特资产编辑，不编辑不可变SFTP对象。原制作工程/构建
记录描述实际本机准备，干净编辑器重新烹饪/另一台电脑重建尚未验证。

组员实测下载/解压/启动、走/跑/静步、跳跃/落地/M1/换弹声、G1三守卫清场及进入
圈确认保存、F9死亡终态与重开；反馈Git版本、ZIP哈希、引擎/运行库、观察及错误。
发布者哈希和Yupu复验不代替另一台电脑/性能/压力/视频/课程验收。不自动发组员消息。
