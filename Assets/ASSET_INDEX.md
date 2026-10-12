# 资产索引 / Asset index

本项目查找资产资料的首入口。先查本页和完整目录，按资产ID打开来源、版本或动作记录；索引无结果时再定向搜索。不要先递归扫描整个工作区、tmp或全部压缩包。

## 目录与预览

| 需要查找 | 入口 |
| --- | --- |
| 全部资产、包名、中英文名称、分类 | [完整资产目录](Registry/ASSET_DIRECTORY.md) |
| 资产ID、别名、父包、关联、版本、来源文档、manifest | [结构化索引](Registry/asset-index.json) |
| 包内文件/对象 | [库存登记](Registry/assets/inventory.json)的`members[asset_id]`；当前数量见生成目录，下方命令可筛选 |
| 动画包的包内动作 | 本机`Assets/LocalWorking/AssetWorkbench/private-records/animation-packs.json`；原生AnimSequence目录，下方命令可筛选 |
| 3D、动画播放、实际截图、音频 | [启动资产平台](../Tools/AssetWorkbench/run.ps1)，进入`/assets/<asset-id>`；[使用说明](../Tools/AssetWorkbench/README_ZH.md) |
| 原始采购/交付、文件夹、重复交付说明 | [采购与交付目录](XIAN_YU_ASSET_CATALOG_20261003_ZH.md)、[资产登记CSV](ASSET_REGISTER.csv) |
| 私有资源的精确文件/哈希/恢复 | [当前Catalog](Sync/CATALOG.json) → 对应`active_manifests[].path`；[恢复与同步规则](TEAM_SYNC_WORKFLOW.md) |

生成目录中的数量随平台刷新更新。完整目录和JSON由登记源生成，来源哈希用于发现过期；不会把“已登记”“可预览”或“来源文件名相同”视为已在游戏采用。

## 常用资产定位

| 资产ID / 范围 | 资料入口 |
| --- | --- |
| `german-soldier` 德军 | [模型、原生绑定与采用记录](../Docs/Development/GERMAN_NPC_ASSET_USAGE.md) |
| `allied-soldier` 盟军 | [模型、M1与握姿记录](../Docs/Development/ALLIED_NPC_ASSET_USAGE.md) |
| `first-person` 第一人称手臂/步枪 | [正式V21记录](../Docs/Development/FIRST_PERSON_FORMAL_V21_RESULT_20261005.md) |
| `german-rifle` FineWood步枪 | [模型/版本/恢复](GERMAN_RIFLE_MODEL.md) |
| `rifle-animation`、`d059-rifle-pro` | [原生动作历史索引](XIAN_YU_NATIVE_ASSET_INDEX_20261003.md)、[交付来源](XIAN_YU_ASSET_CATALOG_20261003_ZH.md) |
| `ue4-animation-collection`、`anim-*` | [全部动作包](Registry/ASSET_DIRECTORY.md#动作)；每包有独立资产ID。`anim-rifle-animset-pro`与`rifle-animation`有关联但不是同一登记条目 |
| `mw2-library`、`mw2-*` | [全部武器登记](Registry/ASSET_DIRECTORY.md)、[来源与限制](XIAN_YU_ASSET_CATALOG_20261003_ZH.md) |
| `pressure-mine` 自建地雷 | [制作与实际UE结果](../Docs/Development/MissionLoopV1/PRESSURE_MINE_RESULT_20261011_ZH.md) |
| `frag-grenade`、`smoke-grenade` 新道具模型 | [模型制作/来源/结果](../Docs/Development/MissionLoopV1/GRENADE_MODELS_RESULT_20261011_ZH.md)、[当前输入／正式采用记录](../Docs/Development/CURRENT_EQUIPMENT_INPUT_REVIEW.json)、[当前统一版](../Docs/Development/CURRENT_UI_REVIEW.json)；平台可直接查看PBR 3D及模型v1/滚轮整合v4记录 |
| `smoke-effect`、`ammo-box` | [装备整合结果](../Docs/Development/MissionLoopV1/TACTICAL_EQUIPMENT_RESULT_20261011_ZH.md)、[当前装备选择器](../Docs/Development/CURRENT_EQUIPMENT_REVIEW.json) |
| `muzzle-flash` | [枪口效果使用记录](../Docs/Development/MuzzleFlashV1/MUZZLE_FLASH_ASSET_USAGE_ZH.md) |
| `recorded-audio`、`explosion-audio`、`cue-*` | [当前声音记录](../Docs/Development/CURRENT_AUDIO_REVIEW.json)、[库存版本](Registry/mappings/inventory-history.json) |
| `paris-city` 巴黎二战地图 · France Liberation | [完整地图、场景层与游戏派生图](../Docs/Development/AssetWorkbenchV1/CITY_MAP_ASSET_USAGE_20261011_ZH.md)、[25cm测绘结果](../Docs/Development/MissionLoopV1/FINE_GRID_RESULT_20261007_ZH.md)、[Catalog](Sync/CATALOG.json)中的`france-liberation-content`；平台“地图”分类、69个关卡/场景层及真实城市预览 |

## 版本和当前游戏使用

1. 正式开发来源读[当前正式选择器](../Docs/Development/CURRENT_DEVELOPMENT_BASELINE.json)。统一候选读[当前UI选择器](../Docs/Development/CURRENT_UI_REVIEW.json)，按其指向继续读专项选择器，例如[玩家死亡表现](../Docs/Development/CURRENT_PLAYER_DEATH_REVIEW.json)。最新文件内容优先于旧文档中的状态快照。
2. 单项资产历史读[核心资产版本](Registry/mappings/history.json)与[库存版本](Registry/mappings/inventory-history.json)，用`asset_id`定位。失败、停用、未人工采用仍保留，不能按文件名日期自动选为正式版。
3. JSON索引的`usage_references`是平台已登记的家族关联；`usage_rules`是源代码查找规则。它们不是新的场景扫描，也不是全部最新候选的完整覆盖。需要确切使用时，在选择器固定的源码/manifest中定向核对。

## 不启动平台也可检索

以下命令从项目根目录运行；可用任意Python 3.10+，本机项目Python路径如下。

```powershell
$assetPython = 'Assets/LocalWorking/AssetWorkbench/runtime/venv/Scripts/python.exe'
& $assetPython Tools/AssetWorkbench/asset_index.py '地雷'
& $assetPython Tools/AssetWorkbench/asset_index.py --asset german-soldier
& $assetPython Tools/AssetWorkbench/asset_index.py 'Reload' --members --asset d059-rifle-pro --limit 10
& $assetPython Tools/AssetWorkbench/asset_index.py 'WalkFwdLoop' --animations --asset anim-rifle-animset-pro
& $assetPython Tools/AssetWorkbench/asset_index.py --check
```

输出含匹配总数；默认最多20项，可调`--limit`。资产/成员查询仅需源码登记；原生动作查询需要本机私有动作目录，缺失会明确报告。查3D副本或图片路径时，按资产ID读取本机`private-records/models.json`、`media.json`，不要扫描所有输出目录。动画缓存的`current.json`定位当前已验证的转换报告；缓存不是生产原件。

## 更新约定

新增、替换、弃用资产或更新版本/使用关系时，更新相应Registry与原始来源记录，然后在平台点击“刷新索引”。平台快照、`Registry/asset-index.json`及`Registry/ASSET_DIRECTORY.md`自动同步，无需另跑命令。第一次建立平台索引也使用同一流程。

不要直接修改生成文件。分类入口变化时同步维护本页。查询会检查登记源与当前选择器指纹，过期即提示通过平台刷新；来源变化、写入失败或取消时保留上一份有效结果，页面显示失败原因。命令行的`--build`仅保留给无界面维护，日常使用平台刷新即可。

索引只存导航元数据，不复制原件、购买凭证或登录信息；私有资料缺失应按[同步规则](TEAM_SYNC_WORKFLOW.md)恢复，不能声称文件已在本机。平台预览范围见[动画包预览结果](../Docs/Development/AssetWorkbenchV1/ANIMATION_PACK_3D_RESULT_20261011_ZH.md)。
