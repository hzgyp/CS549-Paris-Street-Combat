# Checkpoint 等待、保存与结果窗口

2026-10-10。本机原生检查及窗口截图审查完成，待用户实际键鼠复验。
用户对统一 v9 的整体修改、德军角落隐蔽布局认可；本轮延续该布局，未选择
整版为正式基线。依据、失败案例、早期门槛及停止条件见
[实施文档](G1_CHECKPOINT_DIALOG_IMPLEMENTATION_20261010_ZH.md)。

## 已完成的交互

- 入圈仍只询问。E 确认后若仍移动/蹲着/小队不稳定，显示等待窗口与真实原因，
  松键或站立仍有效，ESC/鼠标取消不写档。超过30秒显示未保存窗口。
- 就绪后显示 SAVING CHECKPOINT，窗口绘制先于原同步写入至少两个游戏帧。
  没有伪造进度百分比或固定长延迟。原函数仍独立复核所有安全条件。
- 完整写入并回读校验后出现 CHECKPOINT SAVED + OK 成功窗口；E SAVE / ESC LATER
  同时关闭。鼠标/Enter/Esc可确认，确认后本次进圈继续隐藏询问栏，重复E/F5不再次写入。
  离圈再进入仍可明确确认下一次保存。
- 磁盘写入失败显示 CHECKPOINT NOT SAVED + RETRY / CANCEL，不显示成功；鼠标重试
  调用同一原事务。保存/结果窗口阻止误射击、重复保存与未确认的重开/读档；松键事件
  继续交给原输入，关闭窗口恢复移动和视角。

## 实际证据

| 当前 Game 运行 | 检查数 | 结果 |
|---|---:|---|
| menu_v2 | 37 | pass_menu_input |
| checkpoint_v2 | 56 | pass_checkpoint_interaction |
| restore_v2 | 31 | pass_fresh_process_restore |

checkpoint_v2 从原真实旧 V5 journal 加载，实际按W进入等待，重复E不排第二次请求，
ESC取消；实际蹲姿等待30秒超时并鼠标取消。下一测试槽复制有效旧档并只读，真实
SaveGameToSlot失败；窗口保留原serial1，然后鼠标重试实际写入/回读serial2。
鼠标OK后询问栏隐藏且输入恢复，同次进圈E/E/F5不增加serial；出圈E无写入，
重新进入时移动中明确E并继续走出圆圈，请求取消且没有写入；再次进入仍无自动写入，
稳定后明确E才写serial3。F9读新档、F6回完整初始任务通过。
另一个新Game进程从隔离目录恢复serial3，六人身份/血量/弹药/射击/死亡值精确，
位置误差小于0.001cm，原终态尸体仍停播。

真实写入日志的 `(write_frame, drawn_frame)` 为 `[[2082, 2080], [2094, 2092], [2292, 2290]]`，仅后两次
成功，实际成功serial为2、3。SAVING、等待、超时、磁盘失败、成功及干净HUD的原始
1080p截图保留在 `tmp/g1-checkpoint-dialog-20261010/checks/checkpoint_v2/`，已查看
布局和文字，无文字代替成功窗口。自动输入、旧存档场景不是一次新的清场或自然交战录像；
统一v9的完整清场/小队过桥证据是既有结果，本轮未冒充重测。

## 身份与保护

- 新普通入口：`tmp/Playtest-G1-Checkpoint-candidate_v3-20261010/PLAY_G1_REVISION.cmd`；独立 UserDir `G1Checkpointv320261010`，V5前缀不变，未迁移或改写旧用户档。
- 只复查保存窗口可用 `tmp/Playtest-G1-Checkpoint-candidate_v3-20261010/PLAY_CHECKPOINT_REVIEW.cmd`，菜单选择 LOAD CHECKPOINT。它使用已验证serial3真实测试档和另外的隔离目录，守军已死亡，不是一轮新的清场；原普通新任务与旧用户存档不改。
- Game SHA256：`6d4127cdcfd4601265c6109b286d2a4743fdb5bdf65398d82678332a6b194c31`。
- 52文件 manifest SHA256：`243d55b46bb794fe7db2f798905509fe229b58884b1b3d181287b2e414077655`。
- 仅5份交互/HUD/非反射头/原生探针源改变；原反射声明、七个保存/恢复/资源/导航/输入
  区段精确；原模型/手指/枪械/音效/AI/固定布局文件及1754 native、父源/Game/Catalog/
  人工试玩后的文件保护全部通过。
- MI022保留首轮变量重名编译失败及独立修正身份。Game-only构建，不进入Editor或重烘焙。

首个独立 restore_v1 在第2帧、Ready前出现 DXGI_ERROR_DEVICE_HUNG 并退出3，未执行读档
测试。原日志/崩溃记录在MI022保留；GPU使用4394.25MB小于9285MB预算，不能断言显存
耗尽或等同MI014的MMU原因。限定一次不同身份、相同程序/设置的新 restore_v2 才实际
通过31项跨进程恢复检查；这不证明偶发GPU启动故障根因消失，也不作稳定性验收。

尚需人工确认窗口观感和物理鼠标/键盘。ADS/M1弹夹与衣袖、正向匍匐及后续玩法/大量NPC
工作没有在本轮修改。没有Git/SFTP/课程PDF/视频发布或清理。
