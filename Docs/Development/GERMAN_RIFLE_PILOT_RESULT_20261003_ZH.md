# 德军枪模试验结果：有底模，尚未通过正式可用验收

2026-10-03。[英文记录](GERMAN_RIFLE_PILOT_RESULT_20261003.md)。本轮只做德军枪；玩家M1换弹、人物、地图、NPC行为、UE与SFTP/Catalog都没动，未提交或推送。

## 结论

Kar98k底模已生成，轮廓能认出来，值得保留。但Blender减面/分件版还不能作为正式资产：木质表面出现明显三角状贴图斑块，拉机柄切口锯齿状，分开的只是外露柄而非完整枪栓；机匣与准星也偏软塌。**不把德军枪械缺口标为已补齐，不上传SFTP、不接入正式游戏。**

按原实施稿“一次云生成、最多两轮有限适配”停止本次修改，保留原底模和失败证据，不继续无限精修。这不是说AI绝对不能做机械模型，而是本次自动适配未满足验收。

## 已完成与实际费用

- 打开核对巴黎解放博物馆同一把1943年Kar98k的四张CC0原照片：双侧、机匣顶面和底面局部。来源：[馆藏2019.1.1](https://parismuseescollections.paris.fr/en/node/860143)。馆藏的替换背带、缺准星护罩/清洁杆已注明；不是自动批准为德军标准装备。没有上传咸鱼商业资产。
- 实时API余额260与赠送账目吻合；任务3919866报价和实扣均20赠送积分，剩240。没有充值/付费/追加生成或收费分割服务；赠送有效期未在余额接口暴露。钥匙、令牌、签名URL只在ignored状态目录。
- 原始GLB约17.17MB、299,479三角、一个网格/UV/材质、两张内嵌2048²贴图，原始字节未变；首次斜摆取景不合格，保留为诊断，后续修正的是检查坐标而非形体。
- 第一轮减面分柄约2.9万三角，发现源/导出差13个面和invalid-mesh警告；第二轮显式清理这13个重复面后，源与GLB均28,884三角（枪身27,486、拉机柄1,398）。修复过程中有重复面诊断日志，不能称构建全程无错误。
- 干净Blender5.2.2重导入的14项基础检查通过：名称/父子关系、三角数一致且≤30k、Blender网格结构、有限坐标/UV、约1.105m长度、贴图/材质/内嵌资源、轴心、分柄时枪身不变、恢复静止、输入字节不变等。GLB约7.81MB，打包贴图的.blend约11.12MB。
- 从原始GLB重新跑第二轮脚本，输出GLB SHA完全一致：`5ecc94326f18df9a217986dd6b1c1724e8c71e278bb3da7e541522562bab1d56`。这是复现检查，不是第三轮几何修复。
- 六张灰模与四张PBR最终图均实际查看；无光照纯颜色对照仍有斑块，说明不能只归咎高光，支持焊接/减面后的颜色UV传递缺陷。尚未进一步分离焊接还是减面单独造成。
- 分柄静止/爆炸视图证明分开了外露柄，也暴露切口不干净；它不是拉栓/换弹动作。焊接后仍有枪身119边界/947非流形边、柄35/38，需专项结构复核，不能称闭合机械模型。
- 原有43原生资产与7动作草稿的前后大小/SHA全吻合。Blender作业退出0，未启动Unreal；功能/导出数字通过不等于画面与完整枪械通过。

使用Blender建模技能的参考、灰模、多视角、材质与新鲜导入检查，正是为了把这些缺陷找出来，而不是凭一张漂亮图通过资产。

## 文件与截图

全部实体仍在 `Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-v1/`。没有新建SFTP可用副本；未验收资源不迁移为baseline。源码和不含秘密的大小/SHA清单在Git工作区，尚未提交。

[原始GLB](../../Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-v1/incoming/kar98k-base-v1.glb) · [底模展示.blend](../../Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-v1/evidence/incoming_v2/incoming_inspection.blend) · [未通过适配.blend](../../Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-v1/exports/reproduced_v2/Kar98k_WorldCandidate_v2.blend) · [未通过适配GLB](../../Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-v1/exports/reproduced_v2/Kar98k_WorldCandidate_v2.glb) · [可重跑源码](../../Tools/AssetCreation/GermanRiflePilot/adapt_rifle.py)。详细清单：`Assets/Integration/GERMAN_RIFLE_PILOT_INVENTORY_20261003.json`，不是Catalog或恢复权限。

原底模斜视，未批准为生产资产：

![Kar98k底模](../../Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-v1/evidence/incoming_v2/pbr_three_quarter.png)

适配版右侧，可见三角斑块：

![减面缺陷](../../Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-v1/evidence/adapt_v2_fresh/pbr_right_side.png)

分件切口缺陷（爆炸图，不是拉栓动作）：

![拉机柄切口](../../Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-v1/evidence/validate_v2/handle_exploded_not_reload.png)

后续先读[GP001案例](../../Failures/GP001-20261003-kar98k-pilot/FAILURE_ANALYSIS.md)，选择保UV的有界适配/重拓扑或成熟授权资产，不重复焊接减面扫参数。若改成保留高模作静态NPC枪，属于调整本次减面/完整活动部件目标，仍需明确复核以及后续UE、性能、历史检查；不自动开第三轮或再花积分。
