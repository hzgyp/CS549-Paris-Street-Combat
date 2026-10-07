# 德军枪模 — 私有资产发布核验结果

2026-10-04。用户确认V15建模可用，另明确证明MW2允许本项目使用及三人组内
衍生文件共享。依据配对入库实施文档、同步手册和Blender依赖交付检查执行，
没有新增建模、精修或渲染。已读GP004/009及既有ACL/manifest字节失败记录。

## 发布结果

资产ID `german-rifle-model`，版本 `german-rifle-model-20261004-v1`，
已加入本地Catalog。16文件/200,288,247字节（约191.0MiB）：两份认可模型、
8张实际效果图、5份技术报告、README。不包含完整MW2/M1库、旧试验、人物或游戏原生资产。

SFTP工作目录：`/workspaces/yg745/german-rifle-model-v1/`。
`Model/GermanRifle_FineWood_V15.blend` 和 `.glb` 为模型；`Evidence/`放截图/报告，
README是使用说明。三人共享账号具名NTFS Modify，允许增删改读，编辑负责人仍yg745。
可变工作区不是版本权威；正式恢复按
`/releases/german-rifle-model-20261004-v1/german-rifle-model.json` 的哈希对象下载。

Git manifest：`Assets/Sync/manifests/german-rifle-model.json`，8074字节，SHA256
`963a7487565153d7c895b180db7797cf0d59a97387d2c939ef3c1d3cdaf60168`。
原有10个Catalog清单的身份/哈希及游戏选择保持不变。
详见[资产说明](../../Assets/GERMAN_RIFLE_MODEL.md)和
[发布收据](../../Assets/Sync/GERMAN_RIFLE_PUBLICATION_STATUS.json)。

## 实际核验及存储

- blend110,979,481字节 SHA b6c9afcd...2f26b8；GLB81,346,308字节
  SHA77f7fd8c...02b378f不变。24网格/24,466三角/~1.1073米。
  复用上轮实际fresh几何/材质/干净重跑记录，不重复运行。
- 只读fresh blend检查：14个实际面材质/36张使用图、48张图片全打包；
  无外部库/动作/音频/视频/缓存依赖。GLB36内嵌PNG，无外部URI。没有保存模型/原件。
- 14个最终LocalWorking模型/证据同盘移动，不复制；两份小文档/证明复制。
  16个工作区文件大小/哈希完全匹配计划，不留旧路径链接，不新增散落工作副本。
  旧诊断路径是当时来源记录，不是当前恢复位置。
- 发布16个新不可变对象，全部通过真实固定host-key认证本机SFTP下载并逐个比较
  SHA-256/大小；release manifest也上传/下载核验后才加入Catalog。
  工作区独有探针的创建/覆盖/改名/读回/删除通过，仅删除自有探针。每个文件
  具名共享账号Modify，chroot根SDDL完全不变。
- 已删除16份核验完的临时下载，共200,288,247字节；保留工作区和不可变对象可
  重新恢复。私有日志/收据保留，旧唯一试验、失败、原件及发布历史不删。
- 所选资产本地/Git保护检查通过；模型等二进制继续忽略，源码manifest与远端
  精确字节一致。本轮没有commit/push。

## 保留的诊断和限制

依赖检查v1把17个材质槽误算为14个实际面材质，虽Blender退出0但有traceback，
按失败处理。实际检查确认3个旧未用槽，改为实际面使用统计后的只读v2通过，
模型未改。旧脚本快照留私有目录。

同盘移动保留14个文件的保护ACL。目录式`(OI)(CI)`递归Modify显示成功，却没有
建立文件的具名ACE，严格检查停止，上传门槛在传输前拒绝。原文件已有
Authenticated Users Modify，不据此宣称SFTP真的拒绝过。精确16文件重核哈希，
逐文件直接授予共享账号Modify后通过；不重置继承、不改共享根ACL。

首次源码manifest的LF与远端生成文件CRLF不同；机械换行修正后恢复8074字节/
963a7487...精确一致，才选入Catalog，未覆盖不可变远端清单。新对象的管理员
服务端文件系统检查普通用户不可读，组合检查遇PermissionError停止；单独
本地/Git检查及所有认证SFTP下载通过，不为诊断放宽对象或根权限。

没有第二台机器、外网转发或运行时测试。已认可/共享的是静态模型；历史型号/
现代底子差异、完整机构/骨架/机械动作、UE5.8.2导入/mip/闪烁/接触/碰撞/FPS和
游戏接入仍单独待做，非已绑定动作套件或公开游戏包。现有native试玩恢复脚本
不会自动获取这项可选模型。Git元数据待另外授权commit/push。
