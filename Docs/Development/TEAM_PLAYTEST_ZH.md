# 组员恢复并验证当前巴黎／G1统一版本

10月9日后续选择：人工复验试玩与42文件源码先按
[当前版本指南](TEAM_CURRENT_BUILD_20261009_ZH.md)。本指南继续管理未改动native359；
旧编辑器/原生锚点不代表较新的Game音效源码。

2026年10月8日。仅供本项目三名获授权组员。Git提供源码、配置和版本清单，私有
SFTP提供原生资产及模块字节。使用 **paris-native-playtest-20261008-g1-npc-vfx-v1**
及本次匹配Git版本。[英文原稿](TEAM_PLAYTEST.md)。另一台电脑的恢复和实际运行
由组员验证；此项仍待反馈，不能把发布成功写成组员运行通过。

## 本版包含什么

现有城市、六名原人物、认可的FP V20／盟军V16／德军V11握姿及FineWoodV15枪械，
原射击／换弹／伤害逻辑，原生NPC跟随／重组／战斗、可见后坐力和选定枪口火焰。
同时包含当前正式巴黎地图与G1桥头任务地图。G1有准备／开始、过桥、清敌／占领、
胜负、安全双槽存档／读取与重开。发布不改模型、手指、源动作或地点；运行不需
Python准备或ParisEditorBridge。这是编辑器支持的试玩版，不是新EXE／Shipping
打包或完整MVP验收。

## 准备代码和本机目录

Windows、**UE5.8.2 CL56702186**、Python3.10+、Windows OpenSSH。保留UE内置
ACLPlugin／Niagara／MeshModelingToolsetExp／InterchangeAssets。SFTP地址、账号、
可信指纹由Yupu私下提供；不要复制他的私钥，不把秘密写进参数、Git或聊天。
发布DLL/modules针对这个UE构建，不能任意换另一版本。

同步前保留未提交源码及被Git忽略的资产修改，并关闭UE／Blender。当前干净克隆
可 `git pull --ff-only`；不要hard reset／clean，也不要合并仓库清理前的资产历史。
旧克隆按Assets/TEAM_SYNC_WORKFLOW.md第8节重新克隆。以下在自己的仓库根目录
运行，不照抄Yupu的D盘路径，也不复制他的Windows目录联接。

```powershell
git rev-parse HEAD
# Owner使用自己的NetID：yp549或jw2046
powershell -NoProfile -ExecutionPolicy Bypass -File Tools/Integration/initialize_playtest_storage.ps1 -Owner yp549
python Tools/Integration/restore_native_playtest.py plan
```

初始化仅在Content不存在时创建本机唯一可写资产目录及联接；已有仓库内联接保留。
已有实体Content会拒绝操作，不擅自迁移、合并或删除。

## 下载、恢复、核验

只恢复两个Catalog清单：france-liberation-content与paris-gameplay-native-playtest。
城市首次约26.47GiB，后续只传缺失／改变的文件。原生清单包含人物／材质／动作、
当前AI蓝图、两张地图、G1控制器、选定特效／配置及四个匹配运行插件DLL/modules。
试玩不需Blender原件、实验日志、PDB、缓存或Yupu的存档。

先交互连接，将显示指纹与私下取得的可信值核对。替换以下地址与账号：

```powershell
sftp -P 22222 YOUR_ACCOUNT@YOUR_PRIVATE_HOST
# 指纹一致后登录，然后输入bye
python Tools/Integration/restore_native_playtest.py download --host YOUR_PRIVATE_HOST --user YOUR_ACCOUNT
python Tools/Integration/restore_native_playtest.py apply
python Tools/Integration/restore_native_playtest.py verify
```

密码仅在本机OpenSSH提示中输入。若管道模式无法弹出密码提示，使用自己获授权
的密钥并附加 `--identity C:/path/to/your/key`；`--known-hosts`指定可信主机文件。
不能关闭主机校验。全部所需下载先暂存并核对大小／SHA-256，再放入实际目录。
已有不同文件时apply停止；回顾并保留修改后，`apply --backup-conflicts`才会明确
替换选中路径，并保留核验后的tmp/native-playtest-restore/backups-*备份，不镜像
删除。核验同时检查匹配源码，只允许正常Git换行转换。发现不一致就检查代码／
资产版本或本地修改，不能绕过检查。保留忽略目录中的verified.json供反馈。

## 在组员电脑启动和测试

```powershell
# 默认G1桥头任务；CheckOnly仅预检，不打开游戏
powershell -NoProfile -ExecutionPolicy Bypass -File Tools/Integration/run_paris_native_preview.ps1 -CheckOnly
powershell -NoProfile -ExecutionPolicy Bypass -File Tools/Integration/run_paris_native_preview.ps1
# 单独打开原正式巴黎地图
powershell -NoProfile -ExecutionPolicy Bypass -File Tools/Integration/run_paris_native_preview.ps1 -Entry Formal
```

UE安装位置不同可增加 `-EngineEditor 'E:/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe'`。
启动器先核对选中源码／原生哈希、城市大小、UE版本及模块BuildId，再普通-game
配合-DisablePython、不启用编辑器桥接。不会运行作者／测试脚本、保存地图或自动
结束窗口；每个窗口由自己关闭后再开下一个。首次Shader／贴图准备不等于预热后
FPS。本版是各自本机单人测试，不是通过SFTP联机。

WASD／鼠标／左键／R保持原操作。G1等Ready后Enter开始，F5请求存档，F9读取，
Ctrl+R全量重开，单独R仍是换弹。按HUD提示满足安全存档条件；拒绝原因会显示。
`-LoadSave`启动时读取自己的有效本地存档；存档不从Yupu电脑复制，也不自动跨机。

组员实际检查初始画面与原人物／握姿、玩家和盟军过桥、双方遭遇／射击／伤害、
G1推进、后坐／枪火、一弹匣与换弹、非默认状态安全存档、关闭重开读取、胜负及
重开。按真实结果反馈；哈希一致不能替代试玩，也不能借私有脚本夹具宣称自然通关。

反馈Git SHA、资产版本、UE版本、恢复核验输出、CheckOnly结果及实际问题／步骤。
截图／日志私下共享，日志在tmp/continuous-arms-native/human-native-*.log，不能
把商业截图或原始日志传公开Git。未收到真实反馈前，第二台恢复／运行、完整任务、
压力FPS、Shipping和课程验收均保留待验证。

## 已知局限

只读闭环没有缺失硬包；原供应商五个软引用缺口保留在清单。不捏造修复，也不能
忽略新增错误。专用M1／接触／完整动作、销毁装备安全、近墙／全城显示可靠性与
实测性能仍按各日期结果限定。发布没有追加玩法或画面验收。
