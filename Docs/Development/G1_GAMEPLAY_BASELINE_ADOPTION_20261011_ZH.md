# 完整玩法正式基线采用与过渡版本清理实施

2026-10-11。用户人工验证最新手持装备统一版，确认逻辑无问题，指出仍有衣服遮挡小问题，要求同步正式版并删除过渡版本。本次选择该原样版本，不顺带修姿势或衣袖。

## 已读记录与本次改变

已读AGENTS、HANDOFF、Failures索引、CURRENT_DEVELOPMENT_BASELINE、CURRENT_EQUIPMENT_INPUT_REVIEW，以及MI045端枪／空槽／手雷不可见、MI046旧枪握点取景失败与返回混合见证提前、MI047掌面遮挡。另读10月10日基线退休恢复契约和10月11日缓存清理实施／结果。失败记录、原图及原始收据不改写；本次增加人工采用记录和新的退休映射。

选定精确76文件 `Unreal/Variants/G1GrenadeEquip20261011/Project`，manifest SHA256 `9ac0620c0794c2cc64c0b701d50e7dba4a82941bee7d147be1f72cd604d9312d`，Game SHA256 `b5357cd4ff39454ec40d72ba96ce8ab379f0e039c83b6170263f631e45c4124d`。作者工程仍为 `tmp/g1-tactical-equipment-20261010/candidate_grenade_equip_v1/Project`（含final build_v4），普通入口仍在 `tmp/Playtest-G1-GrenadeEquip-20261011/PLAY_GRENADE_EQUIP.cmd`，不移动包或用户档。

更新正式选择器和已有稳定入口 `PLAY_CURRENT_G1.cmd`，将装备、手雷模型、死亡、UI当前记录关联到正式76身份，旧专项记录保留为历史。承接手雷／烟雾、地雷拆除、补给、战地手册、死亡倒地、库存轮换、现有模型／原枪械手指参数／枪械和全灭敌军圈内E保存逻辑。衣袖遮挡列入后续修复，不写成视觉完全通过；此次人工认可不扩展为新增大量NPC／第二机／Editor／课程验收。

## 早期验收

采用前核对76源码及匹配作者源码、普通100文件／Game、15项最终Game实际检查、1754原生保护、Catalog和全部现存用户文件。后续人工试玩产生的用户存档以本次最新冻结为准，不套用试玩前用户文件清单。只读核对现有引擎进程，不终止游戏或编辑器。

## 精确清理边界

冻结实际存在的目标清单后再执行，仅限：

- 七个被取代的普通试玩：TacticalEquipment、PressureMine、CombatUI、FieldManualUI、DeathPresentation、GrenadeModels、EquipmentWheel。
- `tmp/g1-tactical-equipment-20261010/candidate_*` 旧候选内Runtime／Archive，以及其Project内Binaries／Intermediate／DerivedDataCache（含插件同名派生目录）。只处理存在的目录，不进入Content链接；源码、compiled-source-game、Saved/Cooked、Config、Audio、原始检测目录及编译收据留存。
- 当前作者 `candidate_grenade_equip_v1` 和最终收据 `candidate_grenade_equip_build_v4` 全部保留。运行中Editor的 `candidate_full_v8`、`candidate_full_v16` 全部保留。上一正式enemy-clear52普通包保留一份，因为已有退休恢复映射仍引用其共享字节，不新增多份旧正式包。

不清理AssetWorkbench、SFTP、本机课程附件／已接受视频、原始商业模型／纹理／动作、所有用户存档及既有恢复ZIP。项目根目录不新增试玩包装器。

旧包／Runtime／Binaries按SHA256去重，共有字节引用当前保留包或上一正式包；唯一二进制及启动说明放入私有恢复ZIP，逐对象回读。缓存可重建，不保留大PCH／obj；其中小型源码／响应／JSON等诊断元数据在删除前逐项复制核验。逻辑删除量和磁盘实测净增分别记录，避免把hardlink大小当释放空间。

## 执行与停止条件

用原生PowerShell `Remove-Item -LiteralPath` 删除冻结目录。每个绝对目标必须在当前工作区及上述范围内，目标／祖先／后代不得为重解析链接；不对整个Project或候选根做递归删除。每项删除前核对清单、尺寸／时间及进程命令行；保留运行中的工程，未知或涉及目标的构建／游戏／编辑器会停止执行。路径越界、目标漂移、恢复回读不符、保留文件改变即停止，不能放宽门槛或删除证据。

完成后重算保留文件身份，核对所有删除目标不存在、当前源码／Game／用户档／原生／Catalog未改变，记录空闲空间及衣袖待修项，刷新资产资料索引。更新正式采用结果与交接记录。本次授权为本机正式采用与清理；Git提交、SFTP更新、课程PDF和视频发布沿用各自既有状态，不自动执行。

准备工具修订：第一次只读冻结在每个目录／文件上反复进行所有退休路径的Path检查，且先遍历当前／运行中工程的缓存再跳过，造成无用扫描。仅停止本次拥有的Python准备进程（52436），未进行任何删除；部分选择器快照留在 `tmp/g1-gameplay-baseline-adoption-slow-prepare-20261011`。第二次采用等价的精确路径／目录前缀检查，遍历前剪枝当前和运行中工程的缓存／易变目录；保护与退休范围不放宽，未终止UE或用户进程。

第二次只读预检遇到其他窗口正在运行的CityPreview命令行编辑器9680及其ShaderCompileWorker，因最初仅允许两个主Editor而在创建删除清单前停止。现已实读其工程路径位于独立AssetWorkbench目录，且不引用任何删除目标；后续允许有真实独立uproject的引擎／构建以及ParentProcessId明确属于它的shader子进程继续运行。涉及目标／无法识别拥有者／用户游戏仍停止清理，不能终止它们或把另一工程的运行当本版验收。

删除前日志保护修订：恢复ZIP生成完成后的回读发现运行中full_v16 Editor在根日志追加消息，固定整文件SHA门槛因此停止；未删除任何目录。初始清单与授权身份原样备份为retirement_initial_v1及RETIREMENT_INVENTORY_INITIAL；仅对full_v8／full_v16两份已识别实时日志保存完整快照，并逐项证实原冻结长度前缀SHA完全相同。后续允许这两份实时日志追加，仍保留原内容／快照，不删除日志；其他文件保护、删除清单和恢复映射不变。

恢复验证顺序：删除前逐唯一对象完整解压回读并核SHA。删除后恢复ZIP不在清理范围，重核其完整SHA及目录内对象尺寸、保留文件引用和全部保护文件；通过删除执行收据确认此前完整回读已通过，不对同一未改变的ZIP重复完整解压。

索引兼容修订：首次正式记录把schema_version提高至4，但现有资产平台构建选择器仅支持1／2／3，刷新因此失败并保留上次有效索引。新记录的新增字段不要求破坏原结构；修正为3，verified_runs保留字典，并补充平台已有checks数组。保存失败job及修正前选择器，重试平台刷新，不改游戏／源／资源或重启服务。正式资产关联增加已承接的地雷／手雷／烟雾；当前统一玩法槽也标记正式采用。

索引第二次失败保留：平台恢复实体ID仅按map路径生成，正式／UI／装备输入三个选择器同时填相同retirement_map造成唯一键冲突。恢复映射仍仅由正式选择器导入，两个评审选择器使用current_baseline及retired_playable_recovery_map作关联，不重复导入；不改映射字节／运行程序／平台服务。失败job和修正前两份选择器均留私有证据。
