# Paris资产工作台 V1

10月18日墙角掩护与协同行动：盟军实际选择障碍后的藏身点及探出点，到位后交替掩护推进；德军目击者保持接触，队友沿可达路线左右包抄，失去目击后分区有限搜索。地图、行为树及回访显示分工、遮挡点和等待原因；「小队战术」开关可比较原基础分工。124项后端、43项客户端及原8766入口66项浏览器检查通过，人类已手动启动新版；保存布局及受保护数据保留。战术体验待人类评价，未接UE。[当前结果](../../Docs/Development/NPCAIMapMainV1/COVER_MANEUVER_RESULT_20261018_ZH.md)；保留[上一版小队结果](../../Docs/Development/NPCAIMapMainV1/SQUAD_RESULT_20261018_ZH.md)。

内部资产平台（原件只读）。[English](README.md) · [实施结果](../../Docs/Development/AssetWorkbenchV1/IMPLEMENTATION_RESULT_20261011_ZH.md)。

历史资料入口：`/research`。检索研究正文、来源、图片说明、机构和地点，支持中文主题词。可筛选巴黎、诺曼底背景和装备研究。图片显示来源、日期、权利及限制；允许展示的本地原件支持预览、放大和查看原图，权利未明确的保留来源链接。原文保持原语言。顶部搜索同时查询资产、玩法与资料。

现有“刷新索引”会重新读取 `Assets/Registry/research/library.json` 登记的 CSV 和 Markdown 目录，并与数据库、资产/玩法目录一起原子更新。[历史资料目录](../../Assets/Registry/HISTORICAL_DIRECTORY.md)。以后在这些登记来源中新增或修改资料即可，无需单独导入命令。本地查询示例：`python Tools/AssetWorkbench/asset_index.py --research "帆布" --limit 5`。源码克隆需要另行恢复原有参考图；资料入库不代表游戏采用或新的传播许可。

10月12日源码发布范围见[按功能Git同步记录](../../Docs/Development/GIT_FUNCTIONAL_PUBLICATION_20261012_ZH.md)：包含平台源码、工具与文档，不包含私有媒体、模型、动画缓存、配置或授权共享链接。历史实施结果保留各自日期与验证边界。

页头 **中文／English** 可随时切换，浏览器会记住选择，筛选、比较版本和当前模板保持不变。复制／下载的模板使用当前语言，来源文档保留原文。[双语更新记录](../../Docs/Development/AssetWorkbenchV1/BILINGUAL_IMPLEMENTATION_20261011_ZH.md)。

10月13日更新：资产使用状态对齐人工采用的袖子正式78版。新增 **玩法设计**（`/gameplay`），现有14条双语记录，包含当前规则、G1教程、M2/M3、桥后点位和A/B桥验证。详情可打开关联资产的3D、当前构建和来源文档，分别显示设计、实现与验证状态；方案和固定路线失败保持原状态。[实施文档](../../Docs/Development/AssetWorkbenchV1/GAMEPLAY_INTEGRATION_IMPLEMENTATION_20261013_ZH.md)。

玩法导航登记在 `Assets/Registry/gameplay/designs.json`，原始设计文档保持权威。“刷新索引”同一次更新平台快照、JSON索引、资产目录与玩法目录；来源文档更新后提示复核摘要，无需单独执行命令。平台代码升级时，停止已核对归属且无活动任务的自身服务，再用 `run.ps1 -NoBrowser -KeepAccessLink` 保留完整共享链接；重启后仅本机模式自动建立新会话，共享模式仍需用完整授权链接重新打开。

## 启动

在项目根目录的PowerShell运行：

```powershell
./Tools/AssetWorkbench/run.ps1
```

启动器复用自己的服务，或在后台启动Python并打开已认证的浏览器会话。默认端口8765；本机因该端口已有其他服务，配置使用8766。配置文件为`Assets/LocalWorking/AssetWorkbench/config.local.json`，内容为`{"port":8766}`。可以用`-Port 8767`选择其他空闲端口；不要停止不相关的监听服务。`-NoBrowser`只启动／复用服务。

10月17日本机访问：服务绑定 `127.0.0.1` 时，直接打开 `http://127.0.0.1:8766/` 或 `/npc-simulation` 即可，无需 token。页面自动创建／复用浏览器会话，仍保留地址、同源、CSRF 和 NPC 会话归属校验。共享模式（含其本机入口）仍需完整授权链接。[本机免 token 结果](../../Docs/Development/AssetWorkbenchV1/LOCAL_ACCESS_RESULT_20261017.md)。

启动地址的fragment含临时凭证，前端换取本机会话cookie后立即清除。共享时仅向授权成员提供`runtime/share-link.txt`中的链接；会话文件不作为共享资料。关闭网页不会停止服务，便于稍后检查。如需停止，先读取忽略目录`runtime/session.json`中的PID，确认该进程命令行包含本工作台venv及`-m app.cli serve`，再只结束这个进程。Windows的venv子进程可能显示为基础Python路径，不能只按可执行文件路径判断归属。

## 新机器安装

本机网络共享配置为`{"port":8766,"host":"0.0.0.0"}`。运行原启动器即可监听全部IPv4接口；可用`-BindAddress 127.0.0.1`选择仅本机模式（切换模式需重启服务）。共享地址使用本机实际IP，不能把0.0.0.0作为其他机器的访问地址。当前共享链接自动保存于私有`Assets/LocalWorking/AssetWorkbench/runtime/share-link.txt`，第一行为主网络接口地址。该链接含访问凭证，服务重启后需使用新链接。

防火墙配置脚本为`enable-sharing-firewall.ps1`，需Windows管理员权限；只开放当前服务程序的TCP端口，范围为Private/Domain网络的本地子网。远端页面保留会话、同源与CSRF校验；无凭证不会开放资产API。

路由器端口转发访问：在私有config.local.json中增加`"external_url":"http://你的公网IP:外部端口"`，重启本平台服务。该设置登记精确Host及外部端口，可与本机端口不同；当前直连转发支持HTTP。完整授权链接生成于`runtime/public-share-link.txt`，供组员复制使用。以管理员运行`./Tools/AssetWorkbench/enable-sharing-firewall.ps1 -Port 8766 -RemoteAddress Any`后，单程序/单端口规则可接收转发的外部来源；默认参数仍是LocalSubnet。公网IP变化时更新配置并重启，旧链接随服务重启失效。外网连通须由另一网络实际检查，局域网或路由器回环成功不能替代。

需要Windows、Python 3.13+、Node 22.12+、pnpm 11。实际测试为Python 3.13.7、Node 24.19、pnpm 11.25。在项目根目录运行：

```powershell
./Tools/AssetWorkbench/setup.ps1 -Python python -Pnpm pnpm
./Tools/AssetWorkbench/run.ps1
```

参数可使用Python和pnpm的完整路径，并将选定Node目录加入PATH。脚本在项目忽略目录建立venv，安装`requirements.lock`，按`frontend/pnpm-lock.yaml`冻结安装，再执行TypeScript检查及前端构建。首次下载依赖需要网络；不向全局环境安装依赖。已实际通过现有环境重复安装；尚未进行第二台干净机器安装。

## 数据位置与范围

- 源码映射为`Assets/Registry/registry.json`、`assets/pilots.json`、`assets/inventory.json`、`mappings/history.json`、`mappings/inventory-history.json`、`templates/requirements.json`。
- 项目Catalog、精确manifest及选择器仍为上游依据；SQLite只是投影，不能采用游戏基线。
- 自有生成数据位于`Assets/LocalWorking/AssetWorkbench/{cache,runtime,runs,private-records}`。前端`node_modules`、`dist`和测试输出同样被忽略。
- 可选私有预览位于`private-records/media.json`。`files`中每项登记`id`、`asset_id`、工作区相对`path`、`sha256`、`size_bytes`、`mime`、`audience: local_owner`、`label`、`kind`及审查后的`rights_basis`。只登记明确允许本机查看的媒体，不能放入密钥、采购凭证或无范围的文件夹清单。仅源码克隆不需要这个文件，缺失媒体显示占位；历史私有证据缺失不能变成通过。
- V1支持PNG／JPEG／WebP／WAV；读取时检查登记字节、文件签名和路径边界。Content junction不被默认信任；模型、纹理、文档、归档和脚本没有通用浏览器下载接口。
- 库存扩展现含229条资产/包记录：125个动画包、53个武器集合、33条运行音频及人物、城市、自建/改制装备等；包内50,151条资源可搜索。当前Catalog的13组均有文件索引。当前使用按正式版、候选、改制来源和未登记使用区分，源码引用不等于新运行验收。
- 来源以转义文本显示，私有媒体映射的原始片段被隐藏。本机展示供应商预览不构成公开传播授权。

新增或修改资产登记、版本、使用关系或上游文档后使用“刷新索引”，平台快照及JSON/Markdown资产资料索引一起自动更新，无需另跑命令。历史快照保持可读；关键元数据错误保留上一有效快照，可选证据缺失形成目录提示。“核验本机文件”只在限定容量内读取所选组，不恢复文件，不核验远端SFTP。登记了一张预览，不代表全部资产文件都存在本机。

## 开发与检查

在`Tools/AssetWorkbench`运行：

```powershell
../../Assets/LocalWorking/AssetWorkbench/runtime/venv/Scripts/python.exe -m app.cli index --metadata-only
../../Assets/LocalWorking/AssetWorkbench/runtime/venv/Scripts/python.exe -m pytest -q -s
```

服务已运行并生成会话文件后，在`Tools/AssetWorkbench/frontend`运行：

```powershell
pnpm run build
pnpm exec playwright test
```

UI测试使用已安装Google Chrome，从会话文件取得本机端口，截图保存到私有`Assets/LocalWorking/AssetWorkbench/runs`。覆盖搜索、来源、比较、构建用途、文件查询、规范复制、刷新、键盘操作及音频加载。截图未经项目精确路径审查不能发布。

技术实现为React／TypeScript＋Vite、FastAPI、SQLite DELETE日志。`catalog.py`适配明确来源，`store.py`原子激活不可变快照，`security.py`核对实际文件句柄，`main.py`提供有范围的认证接口，`cli.py`持有本机监听。选择动画可启动限定的UE/Blender转换，仅操作已登记的私有副本；不提供改写来源、删除资产、Git发布或SFTP写入操作。结构化任务编辑属于后续阶段。

## 全量动画包 — 2026-10-11

125个动画包均默认打开3D，包内25,219条原生AnimSequence可按名称/路径搜索并选择。支持播放/暂停、时间轴、速度、旋转、缩放、平移和复位；镜头跟随动作位移。中英文界面均可用。

125个默认动作已预转换。其他动作首次选择时使用本机UE 5.8与Blender 5.2转换，显示进度，完成后缓存；任务串行，失败明确提示。两个实测首次转换耗时41–45秒。目录全部可选，但当前实际转换和检查的范围为125个默认动作及3个额外动作，不能视为全部25,219条均已验收。

预览采用中性材质，不进行重定向或原生资产保存。Movement Animset Pro使用已标注的外部兼容预览人偶。本机需保留私有`animation-packs.json`、`native-covers-v1`中的副本工程及`animation-viewer-v1`缓存，纯源码克隆不带这些文件。原6个模型仍保留，另登记125个包默认模型。[实施与验证](../../Docs/Development/AssetWorkbenchV1/ANIMATION_PACK_3D_RESULT_20261011_ZH.md)。

## 3D 与动画 — 2026-10-11

德军、盟军、第一人称手臂、德军步枪、步枪动作库、候选压力地雷已接入“3D 与动画”。盟军/第一人称页面还可切换 M1 来源模型。左键旋转、滚轮缩放、右键平移；复位按当前姿态取景。人物有 7 段已有源动作，支持播放/暂停、时间轴和 0.25–2 倍速。步枪和地雷为静态模型。原图和音频可切换查看。

人物 3D 尚不包含 UE 服装迷彩/染色、最终握姿、挂枪和状态切换，因此不是当前游戏整合效果的完整复现。导出副本贴图上限1024；步枪和地雷使用原有 GLB 字节。

私有 `private-records/models.json` 登记6个自包含 GLB 的来源、版本、哈希和本机受众。专用接口校验会话、快照、安全路径、SHA-256、自包含格式及128 MiB上限。Three.js按需加载，离页释放GPU资源。保留登记表及私有 `3d/export-v3`；重新转换需在 `prepare_viewer_models.py` 使用新输出身份，再运行 `verify_viewer_models.py` 和 `register_viewer_models.py`，已有输出目录禁止覆盖。[3D实施结果](../../Docs/Development/AssetWorkbenchV1/VIEWER3D_RESULT_20261011_ZH.md)。

库存生成器为 `Tools/AssetWorkbench/import_inventory.py`，读取明确的现有采购/原生库存、实际媒体和原件哈希。完整重建会读取约24 GiB动画归档及2.36 GB武器原件；不解压、不保存原件。普通“刷新索引”只重新读取登记元数据。新到货应先更新来源库存再运行生成器，并重新构建前端翻译文件。原始图片/音频和新增诊断图均保存在忽略目录。详情中的“包含内容”支持包内搜索与分页，“浏览子资产”展开动画、武器或音频合集。

## 平台内实时二维 NPC 交互

10月18日调参：在实际行为树内修改跟随距离、德军视距／视角、丢失宽限和搜索时限，点击「应用到地图」作用于当前回合，保留时间、位置和记忆。地图视野及真实决策同步使用参数；回访保留历史值，本机保存布局包含已应用参数，旧布局兼容默认值。全屏编辑和连续播放保留。[参数结果](../../Docs/Development/NPCAIMapMainV1/PARAMETERS_RESULT_20261018_ZH.md)。

10月17日拖动／行为树更新：按住地图背景拖动平移，运行和回访均可使用；短按保留移动／摆放，拖角色保留摆位。平台内连接节点图与服务器实际执行使用同一树定义，可切换NPC、查看条件／动作／状态、点击节点看结果和黑板，并回访当时执行过程。移动成功必须实际到达，路径失败及有限恢复仍明确显示。[行为树与拖动结果](../../Docs/Development/NPCAIMapMainV1/BEHAVIOR_TREE_RESULT_20261017_ZH.md)。

10月17日显示修复：根据每0.1秒实际移动姿态连续绘制，不再每0.5秒跳一下；不预测位置、不跨过路径转角。暂停／回访／重置取消动画。本机测量绘制间隔中位数16.7毫秒，绘制耗时95分位0.4毫秒。[连续显示结果](../../Docs/Development/NPCAIMapMainV1/SMOOTH_DISPLAY_RESULT_20261017_ZH.md)。

侧栏「NPC交互」进入原生 `/npc-simulation`。点击空地让玩家寻路行走，拖动成员可暂停并校验摆位；盟军实际跟随/支援/掩护，德军依据视线发现目标并在丢失后调查、有限搜索、返回警戒。可查看路径、私有记忆、到达距离和时间轴，保存摆位与效果备注。三个预设，每回合120秒，离开页面暂停。巴黎已审计黑白图（临时扩展L0，180×240米）已作为主场景，白色允许二维通行/视线，黑色含未知区域按阻挡处理；保守净空与有界A*计算实际路径。支持整图/定位队伍、缩放平移、设置朝向；保存布局固定地图身份。其他表面不合并、不视为楼层。未接UE或伤害/弹药。当前仅本机服务模式开放。服务重启后内存会话失效，本机保存摆位保留。 [结果与证据](../../Docs/Development/NPCAIMapMainV1/RESULT_20261017_ZH.md)。
