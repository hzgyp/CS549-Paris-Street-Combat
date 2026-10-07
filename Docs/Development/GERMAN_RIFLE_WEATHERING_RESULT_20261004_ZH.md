# 德军枪模 V11：轻度做旧结果

2026-10-04。使用 Blender 建模技能，按 V11 中英文方案进行。用户已认可 V10 整枪形体，本轮只改纹理。新做旧效果尚未收到用户复核；不是历史/游戏/共享资产验收。

木托增加稀疏顺纹擦痕、轻微油色/包浆与光泽变化；钢材增加细划痕及不完全均匀的粗糙度。保留原钢材法线细节，没有锈斑、大块剥落或新增几何。初始擦痕过弱，保留 preview_v1 和源码快照后只作一次宽度/对比修正，最终保持克制；普通整枪距离变化不强，近看材质稍不均匀。未重启 Aholo、坐标分材质或细节堆砌。

## 实际检查和文件

- 原始24部件的拓扑、UV、网格法线、修改器、父级、世界变换逐项指纹完全相同。V10批准版 blend SHA `5895c9631dedcab873c63670055bf90330a2b467d654ea734acfa68de72849a6`、GLB SHA `795967ab635064139c69a4e46ffacfce222b992e275a7ffec5043cb974642323` 制作后均未变。
- 显式应用原修改器导出，新进程打开独立 blend/导入 GLB。`audit_v1` 通过、退出0：24名称、24,466三角、1.107304×0.079198×0.183007米、17张内嵌图片，无外部图片/Action。作者与导入位置最大误差0米，UV5.96e-8、法线0.0411594度；与V10导出比较位置0米、UV5.96e-8、法线0.0334681度。不宣称法线逐位相同或全局自交证明。
- 实看初始前后四图、最终作者六图、最终新鲜导入六图，包含双侧、斜侧、顶、底、机匣。没有明显丢贴图、钢木误涂或新破面。干净 `repeat_v1` 重跑和 `repeat_audit_v1` 属性/嵌入PNG字节一致检查通过；整GLB哈希不同，原因未证明，不宣称逐字节可复现。重跑六张图未重复人工逐张检查。
- 导出仍提示多纹理节点使用首个sampler；新鲜图已实际查看。World.use_nodes 未来弃用提示非本轮错误。所有任务Blender进程已结束。

[Blender模型](D:/0.Rutgers/CS549/Project-New/Assets/LocalWorking/Experiments/GermanRiflePilot/20261004-spr-weather-v11/finish_v1/GermanRifle_SPR_Weathered_V11.blend)：23,109,377字节，SHA `7f9283212611c8753efc3b3c0a8ae2bb69a60e8c011856478589e0214e444b42`。

[GLB模型](D:/0.Rutgers/CS549/Project-New/Assets/LocalWorking/Experiments/GermanRiflePilot/20261004-spr-weather-v11/finish_v1/GermanRifle_SPR_Weathered_V11.glb)：21,605,816字节，SHA `f979fb6a5ad4a725553d73804c3f3efd7a793e55c16129164223bd69ccb55a8d`。

[可重跑源码](D:/0.Rutgers/CS549/Project-New/Tools/AssetCreation/GermanRifleSPR_v11/main.py)。只读约13MB批准版，不重新打开/复制/保存2.2GiB原库；本轮没重新审计原库/游戏/M1/旧枪整批哈希。通用 V10 audit 仅增加可选文件名/基线几何/PBR-only参数，旧默认行为不变；V10 main和二进制未改。新草稿元数据 `Assets/Integration/GERMAN_RIFLE_WEATHERING_DRAFT_INVENTORY_20261004.json` 不是生产、恢复或SFTP清单。

下面是实际 GLB 新鲜导入效果：

![整枪](D:/0.Rutgers/CS549/Project-New/Assets/LocalWorking/Experiments/GermanRiflePilot/20261004-spr-weather-v11/audit_v1/fresh_pbr_quarter.png)

![近景](D:/0.Rutgers/CS549/Project-New/Assets/LocalWorking/Experiments/GermanRiflePilot/20261004-spr-weather-v11/audit_v1/fresh_pbr_receiver.png)

本轮到此停止，不再加微细节。未改变游戏/M1/动作/UE、未云调用或扣积分、未SFTP/Catalog/commit/push。所有产物 ignored LocalWorking；源码/哈希/文字记录可进入Git。存储保护检查通过17,479条已选择清单元数据，未作远端/全量本地字节复核。仍需 MW2 使用/衍生共享许可确认、现代机匣差异与具体历史变体、完整枪机/骨架/动作、握持和UE/碰撞/LOD/性能测试；不能据此关闭正式德军枪械缺口。
