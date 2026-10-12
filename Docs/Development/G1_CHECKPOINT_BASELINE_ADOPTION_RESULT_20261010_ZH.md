# 清场checkpoint正式基线合并与清理结果

2026-10-10，用户最新人工复验通过，enemy-clear v3 已正式选作开发基线。
累计菜单、速度/弹药、德军角落布局、HUD/audio和最新成功保存窗口及清场规则均承接。
模型/手指/枪械/导航/AI和原存档校验字节不变，本轮没有改Game或52文件源、重编译或新引擎运行。

正常入口：项目根目录 `PLAY_CURRENT_G1.cmd`，指向 `tmp/Playtest-G1-EnemyClear-candidate_v3-20261010/PLAY_G1_REVISION.cmd`。
后续制作从 exact52 `Unreal/Variants/G1EnemyClearCheckpoint20261010/Project` 或当前
`tmp/g1-enemy-clear-checkpoint-20261010/candidate_v3/Project` 开始。Game `b40409b08830cc0e1d306ceab0575d7e61db382f50853426bbda58d08f385079`；manifest `66d8c6e3fc005090ebe44e31f6a8dabd0fdbe1871ffed613cb3769f5b334508a`。
用户存档未移动/清空；1754原生保护文件、Catalog、当前源/Project/试玩和保留源/失败/图片/原收据核对通过。
精确源/manifest及恢复清单已登记Git不转换行尾规则；失败索引原历史行字节保留，仅增加本轮说明。

删除19个旧普通试玩目录、旧版本派生编译缓存和本机旧audioV2完整ZIP，共217个精确目标。
清单逻辑体积254.51GiB，不能当作实际释放量（旧包共享hardlink）。
唯一文件恢复包5.81GiB；包含不同的Game/PDB/启动器/说明，
共有文件复用当前保留字节，所有恢复条目均逐项回读。扣除新恢复包后磁盘实测净增加
97.05GiB。原样保留旧源码/用户存档/失败日志图像/检测结果、cooked输入、legacyV13和旧唯一恢复包。

恢复见 [精确清单](G1CheckpointBaselineAdoption20261010/RETIREMENT_INVENTORY_20261010.json)、
[路径映射](G1CheckpointBaselineAdoption20261010/RECOVERY_MAP_20261010.json)、
[机器结果](G1CheckpointBaselineAdoption20261010/RESULT_20261010.json)。
旧audioV2恢复工具已加入新的保留路径解析，原历史清单不改写；真实旧启动器恢复和跨代共同DLL解析通过。
Intermediate/DDC只保留尺寸/时间清单，可从原源重建，不承诺逐字恢复这些缓存。

没有终止用户进程或进入Editor，没有自动commit/push、远端清理/发布、视频/PDF修改。
课程SFTP下载、已批准视频和旧第二机记录仍指向先前audioV2；最新52文件尚未同步成新的远端试玩包。
旧小队通行测试属于历史路径证据，当前存档任务门槛只要求登记敌军全灭。
后续Editor须构建匹配版本；人工通过不扩大为新的性能/大规模NPC/第二机/课程验收。
