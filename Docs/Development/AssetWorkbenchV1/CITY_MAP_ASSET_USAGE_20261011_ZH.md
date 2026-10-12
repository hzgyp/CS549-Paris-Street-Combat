# 巴黎二战地图 · France Liberation

资产ID：paris-city。供应商：Meshingun Studio。原始交付目录标记为d20260630（UE5.6+），本项目使用UE5.8；版本兼容不由目录标签单独证明。采购渠道未在本次核实，沿用Assets/Sync/RIGHTS.md中的既有项目三成员共享记录。

当前环境交付：france-liberation-content，版本git-assets-20260930-210133。精确manifest登记15,850个文件，共28,421,951,358字节（28.42 GB / 26.47 GiB），包含69个.umap。关卡数包括城市场景层、建筑预制关卡及示例图，不是69张独立可玩地图。完整原件与外部Actor保留在私有存储，平台不提供整包公开下载。

供应主关卡：/Game/WW2City/Maps/LV_Paris_WW2。主要场景层包括白昼/午夜/战争雾灯光、建筑与结构、代理、样条道路、电线、场景陈设与特效；原始供应主图的包引用可追溯这些层，不据此声称所有灯光场景同时采用。

游戏派生主图：/Game/ParisCombat/Maps/LV_ParisG1_Midterm_V1。此前基础派生图：/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1。两者的当前原生字节以Catalog的paris-gameplay-native-playtest清单为准。平台从当前选择器固定的Config/DefaultEngine.ini记录GameDefaultMap引用；正式/候选/历史发布关系显示在“游戏使用”。游戏源修订与地图原生版本分别登记，不能把新的Game版本说成整套供应地图新版本。

预览为当前选择器固定检查目录中的真实G1桥头/街区截图，标明已有实跑图与局部范围，保留25厘米规划图作为补充资料。原始像素及HUD保留；不是供应商海报，也不是全图总览。两次完整供应城市预览加载分别因600秒上限及实际内存门槛停止，失败保留；没有完成全图3D预览。预览不构成全城碰撞、导航、建筑内部、性能或新的运行验收。ML001的局部失败与有限高度结果保留；25厘米扩展测绘也不是全部地图运行通过。地图原件、原生游戏图、Catalog和用户Editor会话不改写。

资料入口：Assets/Sync/manifests/france-liberation-content.json、Assets/Sync/CATALOG.json、Assets/ASSET_INDEX.md及Docs/Development/CURRENT_DEVELOPMENT_BASELINE.json。新增或修改登记后通过平台刷新同步SQLite与JSON/Markdown索引。
