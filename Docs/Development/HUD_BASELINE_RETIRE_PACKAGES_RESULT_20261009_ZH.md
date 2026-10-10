# HUD开发基线选择与旧包退役——实际结果

2026年10月9日。[英文原文](HUD_BASELINE_RETIRE_PACKAGES_RESULT_20261009.md)。
[实施流程](HUD_BASELINE_RETIRE_PACKAGES_20261009_ZH.md)记录本次授权、已读的
MI012/MI013及旧清理案例、区别、早期验收和停止条件。

## 后续开发起点

用户选定当前hud_v3为后续开发基础，已写入
[当前基线选择](CURRENT_DEVELOPMENT_BASELINE.json)及
[中文说明](CURRENT_DEVELOPMENT_BASELINE_ZH.md)。试玩入口保留：
`tmp/Playtest-G1-HUD-20261009/PLAY_G1_REVISION.cmd`，程序SHA256仍为
`497221422d7754d562b4e6d11fd8cc50c9223e40b329b26c8c14391a98d1c42b`。
后续功能从`Unreal/Variants/G1HUDPlaytest20261009/Project`的原样40项源码，
或匹配的可写`tmp/g1-playtest-revision-20261008/candidate_v3/Project`开始。
工作目录名字较旧，但它不是废弃包。模型、手指姿态、枪械/弹药逻辑和存档
协议原样保留。旧正式758项源码/native359仍是资产恢复锚点。

此前HUD仅编译Game；旧Editor缓存不代表本HUD已经在编辑器中生效。后续
编辑器工作需从选定源码编译并实测。本次选择不新增动作/镜头/性能/第二台
电脑/视频/课程验收。

## 实际清理与空间

**15:16:52 EDT执行完成，退出码0**。11个授权生成目录均已不存在：两份旧
非HUD试玩、instrument_v13 Archive、10月2日package_v3 Archive及正式
Saved/StagedBuilds、六份失败instrument_v1/v2/v6/v7/v14/v15 Archive。
父目录源码、日志、截图、回执、失败分析及用户存档保留；原始资产和已发布
SFTP release/object历史保留。

| 实测项目 | 实际数值 |
|---|---|
| 删除文件逻辑大小 | 527项；92,911,616,130字节 /86.531 GiB |
| 新去重恢复ZIP | 829,475,151字节 /0.773 GiB |
| 从准备前算起，D盘实际可用空间净增加 | 92,082,651,136字节 /85.759 GiB |
| 删除后D盘可用空间 | 409,453,182,976字节 /381.333 GiB |

净增加已扣除新恢复ZIP，不把逻辑大小冒充释放空间。实际回执分别记录准备
前、删除前和删除后的可用字节。仅用PowerShell7 LiteralPath及独立11路径
白名单删除；工作区绝对路径、重解析点、完整文件集合/大小/时间和活动进程
检查均通过。本次未启动或终止游戏/引擎。

## 恢复与保留核对

私有`Evidence/PackageRetirement20261009/run_v1`保留冻结清单、准备认证、
唯一文件ZIP、实际删除/空间回执、最终核对和只读恢复记录。可恢复G1载荷
删除前逐项哈希；新ZIP成员逐项回读，复用的旧ZIP成员也实际读回认证。
仅10月2日旧成功包按生成输出退役，不承诺其逐字节恢复。

前次不可改写清单有7项依赖旧instrument_v13 Archive，现通过明确的
[恢复覆盖账本](PackageRetirementV1/RECOVERY_OVERRIDE_20261009.json)转接到
已校验的私有V13 ZIP，其SHA256为
`760dbf44028acae9486c3ff9f5883715d5cf17a1c6fe338f65f20c8caecf9d01`。
这一份旧ZIP仍是恢复依赖，因此保留；它不是第二个活动试玩版本。原plan/
result字节未改。真实恢复工具执行`-Target
tmp/mvp-closeout-20261008/instrument_v11/Archive -VerifyRecoveryOnly`通过，
逐项读回全部声明恢复字节、实际覆盖7项转接，目标目录仍不存在。恢复历史
资料不授权重跑已停止实验。

删除前后758项正式源码、703项当前保护记录、选定/工作/交付三处40项源码
一致性及当前游戏SHA均通过。50项最新试玩和47项HUD Archive的完整集合及
冻结元数据保留，本地共享ZIP元数据原样；此前已认证的SFTP共享版未改动。
`%LOCALAPPDATA%/ParisStreetCombat/G1PlaytestV5`中的用户存档未打开、覆盖或移动。

前次清理要求保留两份最终Archive及三份试玩是历史快照。本次新授权在恢复
转接后只退役其中两份旧试玩及V13 Archive；继续保留HUD Archive、最新试玩/
本地共享ZIP、工作源码/烹饪输入及必要恢复ZIP。Git仍为
`79421db822c344a693a682f1af6bc3e40cfa0119`；本次新基线/清理文档和工具未提交推送。
