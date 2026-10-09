# MI002 - G1打包范围误含退休草稿

2026年10月8日。[英文原稿](FAILURE_ANALYSIS.md)。

package_v1成功编译四个现有运行时插件及Windows游戏，但Cook退出1、UAT退出25。
新构建工具错误地把整个/Game/ParisCombat列为必烘焙目录，带入已退休的
BP_PCSquadReservationV3；它指向不存在的BP_PCNPCSquadV3，造成9条编译错误
（3类失效引脚／转换）。BehaviorV1／V2缺少旧树的提示和其他草稿警告也保留。
本身份没有获得打包启动或完整任务结果。

原因是把开发资产库存当作运行时依赖闭包。选定入口的扫描通过，不能证明父目录中
全部历史包都可打包。这属于构建范围错误，不能据此认定当前G1 AI或地图连通失败。

原始工具、配置、准备／构建收据及完整日志保留在私有
Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/MVPCloseoutV1/failures/package_v1/。
原生输入保留，不修复／删除／重存；停止旧身份，不自动刷新节点、增加重定向或
忽略错误重试。下一身份重新核对当前源码／原生资产和703保护。

不同的有界修正：package_v2只沿G1地图硬依赖烘焙，额外显式包含实际动态加载的
枪口配置目录及现有InPlace步枪动作目录，保留被引用引擎资源。早验是零错误完成，
并确认烘焙集合不含退休V3 reservation；之后独立打包启动确认六人原生Ready及
实得1920x1080。必要依赖缺失、编译／运行错误、输入漂移即停止；不降低玩法、
弹药、存档、路径、帧率或人工验收门槛。
