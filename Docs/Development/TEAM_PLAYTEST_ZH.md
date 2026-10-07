# 组员恢复并试玩当前巴黎版本

适用范围：本项目已获授权的三名组员。Git提供代码、配置和版本清单，私有SFTP提供地图、人物、动作、原生Blueprint和原生显示模块。固定试玩版本为 `paris-native-playtest-20261006-german-grip-v11`；不要复制yg745的可变工作区，也不要拿旧打包版替代。英文原稿：`TEAM_PLAYTEST.md`。本次Git版本包含匹配的通用源码、配置和Catalog；先拉取对应远程版本，再恢复SFTP资产。源码发布不等于组员运行已验收。

## 这一版能测什么

现有巴黎地图、六名士兵、基础移动/碰撞、射击、原换弹、HUD、导航基础、人工认可的V20第一人称显示层、两名盟军统一使用的V16握枪版本，以及三名德军统一使用的V11握姿和FineWoodV15枪械。保存的原生策略也会绑定后续新增的同阵营兼容NPC，不需要Python准备或每帧控制，也不需要ParisEditorBridge。NPC交互草稿独立、未采用；跟随/巡逻/双方决策未进入本正式版本。衣袖和德军细小握姿问题明确延期，专用M1动作、完整返回/生命周期/贴墙、效果与性能验收未完成。详见 FIRST_PERSON_FORMAL_V21_RESULT_20261005_ZH.md、[盟军正式采用结果](ALLIED_NPC_FORMAL_V18_RESULT_20261006.md)和[德军正式采用结果](GERMAN_NPC_FORMAL_V14_RESULT_20261006.md)。不是完整MVP或新的独立EXE。

## 准备环境与代码

安装Windows版 **UE5.8.2**（CL 56702186）、Python3.10+和Windows OpenSSH客户端；保留UE内置ACLPlugin、Niagara、MeshModelingToolsetExp及InterchangeAssets内容。无需付费插件。SFTP地址、账号和可信主机指纹由Yupu私下提供；密码和私钥不得放Git或聊天。

当前干净克隆可以 `git pull --ff-only`。如果还保留仓库清理前的旧资产历史，按 `Assets/TEAM_SYNC_WORKFLOW.md` 第8节新克隆，不要合并旧历史。同步前保留未提交代码和被Git忽略的资产修改；不要用hard reset或clean。以下命令在你自己的仓库根目录运行，不用照抄Yupu的D盘路径：

```powershell
git rev-parse --short HEAD
# Owner填你自己的NetID：yp549或jw2046
powershell -NoProfile -ExecutionPolicy Bypass -File Tools/Integration/initialize_playtest_storage.ps1 -Owner yp549
python Tools/Integration/restore_native_playtest.py plan
```

初始化工具仅在项目Content不存在时创建本机唯一可写资产目录 `Assets/LocalShared/SFTP/workspaces/<Owner>/paris-gameplay-v1/Content` 和Content目录联接。已有指向本仓库内的联接会保留；已有实体Content会拒绝操作，不会擅自迁移、合并或删除。遇到这种情况单独协调。不能复制服务器上包含绝对D盘地址的联接到另一台电脑。

## 下载与恢复

本版清单294个文件，包含第一人称/盟军/德军私有握姿DataAsset/图，以及
`Plugins/ParisGripBindingV18/Binaries/Win64` 和
`Plugins/ParisNPCGripV15/Binaries/Win64` 下的DLL/modules；不可替换成
其他UE版本编译的模块。通用插件源码和项目启用配置由Git提供，SFTP提供
匹配UE5.8.2的编辑器模块。德军枪械网格/材质依赖已包含，不需要额外下载
Blender源文件版本才能玩；这不代表已提供Shipping打包版本。

本轮只需两个Catalog清单：`france-liberation-content` 和 `paris-gameplay-native-playtest`。新清单已经包含所需人物、动作、材质、骨架和游戏逻辑的正确路径，不需要先下载所有历史资料、原始源文件和实验室基线。首次城市下载约26.47GiB，另加原生依赖；之后只下载缺失/改变的文件。SFTP不是游戏远程流式加载，也不会只传一个模型文件内部改变的字节块。

第一次先交互连接，核对客户端显示的主机指纹与Yupu私下提供的值，确认一致才接受。把示例替换成私下取得的地址和账号：

```powershell
sftp -P 22222 YOUR_ACCOUNT@YOUR_PRIVATE_HOST
# 核对指纹、登录后输入：bye
python Tools/Integration/restore_native_playtest.py download --host YOUR_PRIVATE_HOST --user YOUR_ACCOUNT
python Tools/Integration/restore_native_playtest.py apply
```

密码模式需要在自己本机交互终端运行，由OpenSSH提示输入，密码不写入参数/文件。如果终端的管道SFTP不能弹出密码提示，或需要自动化，可配置自己的获准SSH公钥，并增加 `--identity C:/path/to/your/private_key`；`--known-hosts`可指定已有的固定主机文件。不要复制Yupu的私钥。失败下载保留在忽略目录 `tmp/native-playtest-restore/`，全部所需文件大小/SHA验证成功后才允许放入Content。生成的 `download.sftp`、`plan.json` 给出准确映射，不保存密码。

操作前关闭UE/Blender。已有不同文件时apply默认停止；先回顾并保留你的修改。如果确认用发布版本替换，执行 `apply --backup-conflicts`，工具会验证并保留备份到 `tmp/native-playtest-restore/backups-.../`。成功恢复会核对全部文件，仅删除已验证的临时传输对象，不删备份、不明Content或历史资产。需要完整复核时执行：

```powershell
python Tools/Integration/restore_native_playtest.py verify
```

所有组员有共享目录增删改读权限，但不得直接改删objects/releases中的已发布版本。不可变版本和单个二进制编辑负责人是团队协作约定，不是文件系统锁。以后仍遵循开工前同步和收工后发布新版本的规则。

## 启动与反馈

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File Tools/Integration/run_paris_native_preview.ps1
# UE安装在其他地方时附加：
# -EngineEditor 'E:/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe'
```

启动器核对游戏依赖哈希、城市文件存在/大小和UE精确版本，再以普通 `-game` 打开已保存的 `/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1`，禁用Python与ParisEditorBridge。不执行一次性作者、测试脚本，也不保存地图。附加 `-CheckOnly` 可以只做预检、不打开窗口。城市完整SHA核验在恢复阶段完成，避免每次启动都再扫描26GiB。

点击游戏窗口：WASD移动，鼠标看方向，左键开火，R换弹，Alt+F4关闭。首次贴图/Shader准备会花时间；启动期卡顿不是预热后的FPS测量。这是各自本机的单人测试，不是通过SFTP联机。

反馈请附Git SHA、资产版本、UE版本、恢复结果、能否启动，以及移动/持枪/开火/换弹的问题。至少测一弹匣与一次换弹、前后左右移动、抬头低头和贴墙开枪。缺材质/形变问题附私下截图与复现步骤。日志在 `tmp/continuous-arms-native/human-native-*.log`，私下分享，不把商业截图或原始日志提交到公开GitHub。收到真实组员反馈前，不能填写“第二台机器恢复/运行通过”。

## 原供应商引用限制

只读审计未发现缺失硬依赖，但发现5个原有供应商软引用缺口（材质定制器、车辆动作旧别名、绳索着色贴图、道路调试库旧别名）。发布清单记录其准确路径和引用来源。本轮不修复或掩盖它们，不宣称供应商包没有缺陷；新增未知错误仍须调查。
