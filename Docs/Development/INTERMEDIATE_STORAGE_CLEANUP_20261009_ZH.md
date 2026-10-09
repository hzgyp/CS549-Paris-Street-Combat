# 中间文件空间清理 — 2026年10月9日

已完成：[实际结果](INTERMEDIATE_STORAGE_CLEANUP_RESULT_20261009_ZH.md)。

用户明确要求将不用的中间文件打包并删除，释放磁盘空间。
[英文原文](INTERMEDIATE_STORAGE_CLEANUP_20261009.md)。

已读失败案例：MI010 GPU启动、MI011无效录像、MI012打包集成、MI013被否定/
缺文字HUD，以及最新HANDOFF和G1/HUD结果。保留原日志、截图、失败记录、源码
快照和独有原件；退出成功不能代替归档回读认证。

不跟随目录链接的盘点显示，最近两个私有构建目录合计约198 GB。本次只改存储。
保留最终hud_v3和instrument_v13的Archive、三份用户试玩、用户存档、正式资产、
源码/FrozenSource、收据、日志、图、构建用Cooked输入和已发布历史。只清理逐项
列出的旧Archive复制、两份StagedBuilds复制及私有Intermediate/Build缓存。
不删除或进入Project/Content链接。旧Archive路径以清理清单恢复，原历史收据不改。

删除前对旧Archive/暂存包逐文件哈希；相同字节引用认证过的最终Archive，独有
程序/配置/启动文件打进私有ZIP。ZIP每项解压流回读核对SHA256。小型编译诊断
元数据一并打包；可重新生成的目标/PCH/编译缓存只记清单，不再保存重复副本。
提供按清单完整恢复Archive/暂存目标的命令。不用硬链接或可写链接修改保留基线。

早期检查：没有UE/游戏/构建进程、所有绝对目标在两个指定tmp目录内、目标及
祖先没有重解析链接、可恢复字节已认证、正式758源码/703保护准确。哈希不符、
出现未知大型独有Cooked、归档位置已占用、新进程或文件意外变化时，删除前停止。
使用PowerShell原生LiteralPath按已检查清单删除。结束核对保留身份、源码/保护、
ZIP回读、删除目录清单和实际剩余空间。不改游戏、不启动、不正式采纳、不提交/
推送Git、不远程发布。

私有记录位于Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/
Evidence/StorageCleanup20261009/run_v1。清理工具提供Prepare/Execute/Verify；
恢复工具只恢复明确指定清单目标，不覆盖已占用路径。

使用HANDOFF中记录的内置PowerShell7运行工具。恢复目标示例：
`tmp/g1-playtest-revision-20261008/candidate_v10/Archive`。
`restore_intermediate_archive.ps1 -Target <清单中的目标>`逐文件复制保留副本或
ZIP内容，并检查大小/SHA256。恢复用于查看/找回，不授权重跑已停止实验或覆盖
当前源码。Intermediate/Build由正常新构建再生成；Intermediate/Source和
Saved/Cooked输入继续保留在磁盘上。
