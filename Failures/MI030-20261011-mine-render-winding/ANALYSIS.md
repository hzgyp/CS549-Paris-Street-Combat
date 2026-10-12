# MI030：地雷导出完整，但 UE 外观验收失败

2026-10-11。用户拒绝旧格纹陷阱后，独立制作盘形地雷。Blender finish_v2 与 fresh GLB import 的形状、UV和烘焙PBR正常，10809三角形；但 candidate_mine_v1 的 UE 普通视距/40°近景呈现近黑表面，标记难以辨认。实际图保存在 `tmp/g1-tactical-equipment-20261010/checks/mine_visual_v1/`。程序检查仅证明构网格、加载三张1024贴图和位置提示；其 pass 不等于外观通过，另记 VISUAL_REVIEW.json=fail，停止该候选交付。

先检查实际导出UV处的PNG像素、法线数值及原生材质参数，不能用提高光照/截图曝光掩盖。UE 5.8 `StaticMeshOperations.cpp:45–48` 明确以 `CrossProduct(DPosition2,DPosition1)` 求三角面法线；本项目导出已经镜像Y，再换一次三角顶点，产生与这个原生惯例相反的朝向。v2 仅在构网格入口撤销多余顶点交换，保留 Blender 源、GLB、贴图、模型比例；以新的真实UE图验证，若仍过暗则停止并检查新证据，不叠加任意增亮。

v2 同时补上源检查发现的终态交互缺口：Won 后死亡必须关闭尚在显示的保存窗口，否则成功窗口会挡住死亡菜单和 F9/F6。原保存事务、清场规则、枪械和人物字节不变。保留 v1 编译源/收据/图片，采用新身份验证。

修订元数据工具曾误用 rows(Project)，遍历 Content junction 做大量只读哈希。确认准备/编辑完成后仅停止自有 Python PID24464，未停止游戏/Editor，未修改 Content；随后仅枚举 Config/Source/Plugins 完成记录。以后源比较不可遍历共享Content或编译缓存。

验收：同一位置与镜头下材质及标记可辨、正确落地接触/两米拆除、双方NPC、清场后真实危险致死/F9/F6、已消耗地雷和盟军伤亡新进程恢复。任一原保护漂移、仍黑/格纹或状态恢复错误即停止。测试夹具不等于人工自然交战/美术选定。
