# UE原生第一人称显示迁移结果

日期：2026年10月3日。[实施文档](CONTINUOUS_ARMS_NATIVE_IMPLEMENTATION_V1_ZH.md)。[英文原件](CONTINUOUS_ARMS_NATIVE_RESULT_20261003.md)。

## 结果

认可的连续手臂已通过标准节点Blueprint接入当前团队地图，不再由编辑器Python每帧更新。原人物/骨架/手指/动作、相机`(25,0,60)`cm/FOV90、V3世界枪、弹药/射击/换弹事务、NPC和已有导航内容保持。源身体和世界枪仅对玩家自己隐藏；新手臂LeaderPose跟随源姿态，生成的可视枪绑定WeaponAppearance。引擎PostUpdateWork tick依赖源网格/原枪，用缓存变换更新显示。不新增运行时C++或bridge依赖。

这是本机集成，不是打包发布、Catalog选择或性能/课程验收。没有新增动作、ADS、AI、VFX，没有commit/push。

## 实际验证

- author-v3：新Blueprint652,470字节，SHA`45a11672...a84d1`，编译无图错误，原42文件不变。
- motion-v1：462帧观察，四方向速度超过100cm/s；49帧同时处于换弹且移动超过100cm/s。最大右握点代理误差约0.000005375cm，手指/相机保护通过；两次换弹提交，死亡隐藏，重置后活着/Ready/原AnimBP。退出0，报告和检查日志无错误。
- 六张实际游戏图逐张打开：idle/reset保持连续衣袖和右下构图。未冻结截图有阶段延迟，up/down不能证明恰好目标俯仰，reload实际为完成持枪，moving_reload实际为后续死亡隐藏。不能用它们认证中后段换弹接触。
- native-combat-v1：新原生Actor一次性生成后自行tick，Python只观察；16项66断言通过，包括79cm近墙阻挡、枪管/相机方向dot0.9999991002。退出0，检查日志没有Error/Fatal/ensure/assert/Blueprint循环。
- select-v1：只在团队地图新增显示Actor/玩家引用。旧V3地图已验证备份，其他原42文件保持；新43文件库存为`CITY_CONTINUOUS_ARMS_NATIVE_INVENTORY_20261003.json`。
- selected-combat-v1：保存地图重新加载后，使用地图自带Actor，16项66断言再次通过，79cm近墙测试通过。换弹/死亡/重置后原AnimBP/FOV90/枪口绑定保留，手指差约9.37e-13。退出0、哈希不变、日志检查干净。
- game-no-python-v1：普通`-game`显式禁用PythonScriptPlugin与ParisEditorBridge，完成600引擎帧，退出0，错误模式检查干净。1280x720实际游戏图已打开，显示新手臂/枪、中央准星及HP100/AMMO2/16/Ready HUD。图为启动期，含贴图准备提示/模糊，不是最终贴图或预热移动性能验收。

当前地图2,707,948字节，SHA`2791b4a7f76b4b3d07f42286b6ad0156c3a185c2e3e795fa2446aaac0ad68519`。旧V3的`d00056e8...09f51f`为历史，已在私有`select_v1/BeforeNativeSelection.umap`备份；不能按旧库存覆盖当前选择。

## 失败和未完成项

作者v1/v2退出0但报告失败，未保存原生包：Actor反射名与Python名不同，静态网格getter不是UFUNCTION；已核对安装头文件修正并保留两个失败身份，没有覆盖已占用资产。

用户认可预览模型并授权迁移，不等于全部动作接触或性能通过。泛用换弹仍缺M1漏夹/枪机专用动作，代理握点/手指对应不是所有网格表面接触验收。普通游戏启动也不是重新打包的独立安装包。

城市加载仍有内存预算警告；motion日志实际记录50次PSO创建卡顿，均未预缓存。它们是性能风险证据，不能推断为早先卡顿的唯一根因。未降低画质；去除Python不自动证明移动流畅或目标/压力FPS通过。

所有字节只在原有SFTP单工作区。供应商源包、动画、旧Blueprint和相机参数没变。明日采购缺口见[中文清单](ASSET_GAPS_20261003_ZH.md)：M1可动零件/配套动作，德军步枪候选，可选射击反馈。跑跳慢走蹲匍匐已有动作候选，不要重复买。

收尾核对：实际本机756个已选择人物/动作文件验证；Git存储守卫核对17,273条所选记录。关闭引擎后重新核对当前43原生文件及源交换FBX。所有本任务引擎已关闭，Python/PowerShell语法检查通过。没有远程发布或第二台机器恢复测试。
