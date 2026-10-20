# 教学正式版直接启动入口调整结果

2026 年 10 月 18 日。按用户要求，删除根目录多余 CMD，后续直接提供正式版目录中的启动路径，同步相关引用，保留现有存档，不重新构建。

当前入口：[PLAY_TUTORIAL.cmd](../../../Releases/Paris-Tutorial-1.0-20261017/PLAY_TUTORIAL.cmd)。完整路径为 `D:/0.Rutgers/CS549/Project-New/Releases/Paris-Tutorial-1.0-20261017/PLAY_TUTORIAL.cmd`。仍使用教学正式版 1.0、source145/revision12，以及原有 `%LOCALAPPDATA%/ParisStreetCombat/G1MedicalGuidanceMusic20261017` 存档目录和 `ParisCheckpointHistoryV1` 前缀。

只删除了一个文件：根目录 `PLAY_CURRENT_G1.cmd`。删除前已核对其绝对路径、普通文件属性及冻结哈希，使用 PowerShell 按精确路径非递归删除。根目录现在没有 CMD。原脚本、旧故障、修复和实测记录保留为历史证据。

更新了 18 个现有文档、选择器和工具文件。当前交接、项目说明、索引、正式版指南以及相关关卡/发布说明均改用正式目录入口；两个当前选择器的 `stable_local_entry` 与 `playable_entry` 一致。正式版发布工具也已取消生成、快照依赖和复制根目录转发脚本的逻辑，本次没有执行这些工具。旧的历史回执与当时的测试事实保留，并在相关说明中注明入口已撤下。

静态检查通过：记录了 13 项检查，其中 16 处正式入口 Markdown 链接均指向现有脚本；两个 JSON 选择器及三个修改过的 Python 工具语法正确。工具中仅保留一处用于匹配旧文本的历史入口字符串，不会生成或推荐根目录启动器。

保留校验通过：354 个实际用户文件（含 95 个存档及原设置）的文件集合与哈希完全一致；145 个选定源码文件、5 项正式版/源码保护项和 Git 暂存状态未变。正式 Game、正式启动脚本和源码清单未修改。没有存档迁移、动作/模型修改、重新编译或打包、启动游戏、替换 ZIP、Git 提交或 SFTP 同步。本次只验证入口与引用，沿用此前同一正式启动脚本的运行记录，不新增玩法验收结论。

实现说明：[TUTORIAL_DIRECT_ENTRY_IMPLEMENTATION_20261018.md](TUTORIAL_DIRECT_ENTRY_IMPLEMENTATION_20261018.md)。完整本地核对记录位于 `tmp/tutorial-direct-entry-20261018/` 的 `FREEZE.json`、`STATIC_CHECKS.json`、`PRESERVATION.json`、`RESULT.json`、`EDIT_ATTEMPT.json` 和 `before/` 原文件记录。首次编辑脚本在 CRLF 段落边界处停止，续处理核对原文件后完成剩余修改；失败尝试未删除入口或修改存档。
