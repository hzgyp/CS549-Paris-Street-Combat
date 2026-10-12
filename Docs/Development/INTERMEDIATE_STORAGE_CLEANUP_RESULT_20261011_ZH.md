# 中间构建缓存清理结果

2026-10-11，按用户清理空间要求完成。[实施文档](INTERMEDIATE_STORAGE_CLEANUP_20261011_ZH.md)先于删除建立。

删除160个旧 `Intermediate/Build` 目录，共9188个可重建文件；逻辑量159,012,361,069字节。磁盘实测净增加158,848,946,176字节，约 **147.94 GiB**。15:38完整性验证时D盘剩余292,679,974,912字节，约 **272.58 GiB**。同期其他工程仍在写入，实际净变化与逻辑文件量分别记录，不把共享文件大小当作释放量。

保留最新统一试玩入口 `tmp/Playtest-G1-DeathPresentation-20261011/PLAY_COMBAT_UI.cmd`、完整92文件试玩包、73文件精确源码及 `candidate_death_v6` 作者工程/缓存；正式enemy-clear52及普通Game不变。现有编辑器50836／51148继续运行，它们使用的 `candidate_full_v16`／`candidate_full_v8` 未清理。AssetWorkbench、Content链接、模型／手指姿态／枪械／存档逻辑、原用户存档和原生资产未修改。

4938项保留文件逐项SHA256验证通过，包括最新源码／试玩、正式源码与Game、1754项原生保护文件、用户文件、失败文档和原始检查证据。24项已完成游戏验证的结果文件身份保留；此次为文件清理，没有重新游戏验收，也没有改变人工复验状态。所有160个目标确已不存在。

5699份选定的源码／响应／JSON等构建元数据已复制并回读验证，位于私有 `tmp/storage-cleanup-20261011/BuildMetadata/`。旧作者工程源码、compiled-source-game、原编译日志／收据、Binaries／Runtime、失败原图／日志、存档／Cooked和历史恢复包均留在原位置。PCH、obj及其他已移除缓存以后可由原源重新构建，首次编译会较慢；不承诺缓存逐字恢复，也不授权重跑已停止的失败路线。

准备时外部用户目录只读盘点错误地复用了工作区路径限制，在任何删除前停止并修正；原负例收据保留。执行在67／106项后两次因瞬时全局UE构建暂停，原追加删除日志不改。Resume逐项核对原清单和已删除状态，再继续剩余条目。已明确识别的独立AssetWorkbench项目允许继续运行，未知构建或使用目标工程的进程仍会阻止删除。没有终止任何用户进程。

私有完整记录：`tmp/storage-cleanup-20261011/PLAN.json`、`INVENTORY.json`、`PROTECTED.json`、`METADATA.json`、`DELETED.jsonl`、`EXECUTION.json`、`RESULT.json`及两个停止收据。PLAN SHA256：`76a6ac9691aeffc81e7870531ac9f9619007290eea21cabab18018407535af68`；RESULT SHA256：`79002f5a017fcd07fac5343f18574de87084757a8d077d2d1884f0dce946212c`。

没有Git提交／推送、SFTP清理／发布、课程文档或视频改动。当前试玩包路径和正常入口保持一致。
