# Kar98k 本轮局部重建结果

2026-10-03。**有独立机械部件进展，但整枪没修完，也没装回木托。** 用户已批准局部机匣/照门/枪口重建，不再是未批准的提议。本轮使用 `blender-modeling-workflow` 技能，先文档/灰模、保留失败、一次结构纠正、干净重跑和重新导入。原 V7 枪模、木托、背带、球头、盟军 M1、游戏均未改。

## 两个早期停止

V8 找到真实156边闭环，选中1,884个机匣上部钢面；5张选区图检查过，没选木托/球头/背带。但顶部投影有3处交叉，不能平面填充。Python断言失败，Blender却退出0，**不算通过**；未删面、未补面。

V8B 不换选区，检查原曲面连接：1,020个物理顶点、2,903条边、欧拉数1、外边156条都匹配；但内部一条物理边连接四个面，UV副本坐标完全相同，不是精度分组误判。因此流形圆盘前置断言失败（退出1），没有继续曲面映射或重建。见 [GP007](../../Failures/GP007-20261003-kar98k-planar-patch/FAILURE_ANALYSIS.md)。这两条自动补面路线已停止，不能继续扫轮廓/容差或随便删面。

## 做出了什么

另做独立 V8C 部件，**没有叠到原枪上遮盖、没有切坏原木托**：机匣前后环/开口下托、枪栓主体/后盖/抽壳条/静止保险；照门底座/倾斜表尺/滑块/双肩缺口/销轴/刻度条；中空枪口/前箍/准星座和刀片。24个独立命名部件、10,104三角面、各自UV与轴心，两种自己的常量钢材；不借用M1商业贴图，不承诺程序材质自动导出。

第一次灰模照门楔块面环交叉，黑底/锯齿；只查边两面与正体积漏掉这个错误。保留首次源快照/8图。唯一一次结构纠正改正6个面的角点顺序，并增加凸面角点方向断言。重新检查8张灰模，圆柱曲面、机匣开口和枪口内孔比原软塌形体规整；8张钢材图和8张导入图也已检查。

**仍是部件候选，不是精修完成枪模**：原枪木托座、拉机柄/球头接合、完整枪栓运动未解决；照门数字/凸轮、保险与枪栓比例精度未验收。画面没有木托，前箍还没有木托支撑，不能把分件图说成整枪装配成功。临时1.105m基准和斜轴粗定位不是精确制造图，也不证明1944装备型号。

![重新导入后的独立机匣](D:/0.Rutgers/CS549/Project-New/Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-topology-v8/parts_audit_v1/fresh_receiver.png)

![独立中空枪口](D:/0.Rutgers/CS549/Project-New/Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-topology-v8/parts_audit_v1/fresh_muzzle.png)

## 验证与文件

- Blender5.2.2LTS；24个实体的边/体积/凸面/UV检查通过；GLB重新导入，三角拓扑/绕向、角点UV、材质、轴心检查通过。
- 位置/轴心最大误差0m，UV误差2.98023224e-8，法线方向误差0.03459591度（事先0.5度门槛）。
- 干净源码重跑GLB字节一致，SHA `6e49674ce0b0871df97951b1bd197c4cec540b7719276e174bc60b6f8a3376f4`；330,408字节。自包含blend232,161字节，无外部贴图。
- 新37张图全部实际查看；旧七份库存355个私有文件/49个源码、50个原生/动作、4个M1参考SHA全部不变。
- 所有自动Blender进程已结束；未开交互预览。仅有 use_nodes API弃用警告，无云端/积分、UE/游戏、SFTP/Catalog、commit/push。

[建模源码](D:/0.Rutgers/CS549/Project-New/Tools/AssetCreation/GermanRifleTopologyV8/parts.py) · [Blender部件](D:/0.Rutgers/CS549/Project-New/Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-topology-v8/parts_finish_v1/Kar98k_StandaloneMechanical_V8C.blend) · [GLB部件](D:/0.Rutgers/CS549/Project-New/Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-topology-v8/parts_finish_v1/Kar98k_StandaloneMechanical_V8C.glb) · [指标](D:/0.Rutgers/CS549/Project-New/Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-topology-v8/parts_finish_v1/metrics.json) · [导入验证](D:/0.Rutgers/CS549/Project-New/Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-topology-v8/parts_audit_v1/audit.json)

全部保留 LocalWorking；新哈希清单只是实验记录，不是生产baseline、组员自动恢复或德军枪模缺口关闭。当前在原木托接口门槛停止。后续需要明确的手工局部重拓扑/美术整合，先证明一个真实装配接口，再做整枪；或使用授权兼容成品枪模。不继续失败的自动补面、覆盖片和参数扫描。
