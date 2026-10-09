# MI003 - 已编译观察器没有加载

2026年10月8日。[英文原稿](FAILURE_ANALYSIS.md)。

instrument_v1编译成功；integrated_v1正常进入G1原生Ready，却没有观察器标记／样本，
没有调用Start。停止收据记录脚本任务尝试0次，仅停止本轮PID11232，退出-1是主动
停止，不能称作G1资产崩溃。本身份不证明完整循环、帧率或存档。源码／收据／日志／
烘焙字节保留在私有MVPCloseoutV1失败归档。

原因：只换单体Game可执行文件不会改变已烘焙的纯内容项目描述；其Modules未列
新Game模块，StartupModule未获调用。已装引擎LaunchEngineLoop.cpp按项目及启用
插件描述加载；ModuleManager.cpp在单体构建中关闭Module Load控制台命令，不试
该命令，不重跑停止身份。

不同的有界机制：instrument_v2仅在独立包装工程内，把命令行启用的观察器放进
已启用ParisBridgeMissionV1模块启动入口。仅模块实现和Build.cs依赖两项接线不同；
ParisBridgeMission.cpp／头文件及原玩法、枪械、AI、模型／姿态源码精确不变。
烘焙内容逐字节复制package_v2，正式项目／插件／原生资产不改。早验需60秒内
看到明确CLOSEOUT_MODULE_ACTIVATED及实际世界样本，否则停精确自有游戏。路径、
资源、不传送、180秒和三轮标准不变。本测试不构成正式模块／地图采用或发布。
