# 当前开发基础

2026年10月9日。Yupu人工复验最新音效V2通过，明确选作后续开发基础。以同名JSON
选择器为准；HUD40、AV42及旧Foley42源码保留作历史锚点，旧可运行包可以退休。

试玩入口`tmp/Playtest-G1-Foley-V2-20261009/PLAY_G1_REVISION.cmd`。后续源码从精确
42文件`Unreal/Variants/G1FootContactAudio20261009/Project`或一致的制作工程
`tmp/g1-foot-contact-audio-v2-20261009/candidate_v2/Project`开始。源码清单哈希
2ff88f0e74040b46e8b7c26750602c56556857a06b45db96c28f297f534b468b；程序哈希
53ab36d9da1975a2f8e1109fcf6745cc40e96d371fc89fbfa009139b91950aec。保留Content
junction和烹饪输入，不因旧目录名称删制作工程。进入编辑器前必须从选定源码构建，
原编辑器缓存DLL不能代表当前Game版本。

SFTP版本`paris-g1-playtest-20261009-audio-v2`，下载
`/releases/paris-g1-playtest-20261009-audio-v2/Paris-G1-Audio-V2-20261009.zip`。
完整解压后启动，92成员含原88文件试玩、双语操作、源码身份及微软运行库。独立
33音效清单在Assets/Sync/manifests/paris-g1-recorded-audio.json；重建先恢复其
RuntimeAudio精确路径，再复制WAV至可写wrapper的Audio目录。城市/人物/枪械原生
清单与source758/native359保持原样作依赖恢复和保护锚点。Git源码不含商业Content，
发布不证明编辑器重新烹饪成功。

选定版本包含玩家落脚阶段音效、起跳/落地、M1实录枪声、已改善的换弹录音和直接
恢复死亡终态；保留原HUD、模型、手指、动作、枪械/资源/存档逻辑。人工音效复验
通过，数值验证仍为20稳定落脚通过、9混合过渡未评估。德军实录来源、物理接触、
自然转身、性能/压力、组员电脑、视频和课程验收仍单独处理。

旧本机/SFTP试玩包按G1_AUDIO_BASELINE_PUBLICATION_20261009双语计划/结果及冻结
清单清理。旧路径请查G1AudioPublicationV2/RECOVERY_MAP_20261009.json，用当前
字节和小型唯一文件ZIP恢复。保留旧V13恢复ZIP、源码/日志/图像/原始视频/存档/
失败证据及资产原件。人工通过结束音效复查暂停；后续演示仍需先修正自然转身，
本次发布没有新增录屏。
