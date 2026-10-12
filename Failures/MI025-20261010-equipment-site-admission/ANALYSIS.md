# MI025：装备点位不能用二维白格替代真实 UE 通行验收

2026-10-10，独立候选 `candidate_full_v6`。`sites_v6` 正常退出，但结果是 `failed_sites`，首组位置未通过 ground/capsule/full-path 检查。原收据保留在 `tmp/g1-tactical-equipment-20261010/checks/sites_v6`，Game SHA-256 为 `cecb6522150dc5f157734ea19b53a90edb007ed9f399c17f297d7d4c37828a4d`。

原诊断只记录组索引0，不能区分 Trap1 与 Supply1，也没有各项失败详情，因此目前不推断是建筑、导航还是净空。二维规划候选不等于已验证设施点位。没有改导航、地图碰撞、角色胶囊或降低阈值。

下一次先进行有限、只读的实际地面/完整胶囊/原生完整路径测量，记录每个点位及具体失败项。候选清单同时包含原位置和现有 G1 已知路线锚点；不得反复微移失败位置求通过。选择不同点位需要新的源身份，并重新验证绕行和存档圈净空。

早期门槛是四个固定点位均获真实 UE 支撑、standing capsule 和非 partial 路径，同时 G1 正常路线可绕过两处陷阱。失败则停止该身份，不将正常 exit 或生成了道具视为验收。

`candidate_full_v7` 的匹配 Editor 构建 exit6，未运行地面诊断。新增 overlap 清单再次遗漏 `Engine/OverlapResult.h`，重复了已记录 MI021 的类型前置条件；不能将“已经读过”当作落实检查。接入文件在原首头前插入新 include，也触发 Editor 首头顺序检查。v8 显式包括类型定义、将对应首头放回首位；不关闭编译检查或修改碰撞标准。旧 compiled-source-editor 与 build-editor.json/log 保留。

v8 的14点有限只读测量确认原 Trap1 被 StaticMeshActor_2035 阻挡，原 Supply1 被 StaticMeshActor_135 阻挡；两点完整路径可获但站立胶囊不通过。替代点 Trap1=(6637.5,-20137.5)、Supply1=(1812.5,-21162.5) 与保留 Trap2/Supply2 均通过相同标准。最终仍需四点复验及 G1 绕行检查，不降低标准。

v9 接入脚本的匹配串错误把 LF/CRLF 及缩进边界视为同一形式，assert 停止；调用端没有检查 Python exit 又继续启动构建。这是工具执行错误，未运行 gameplay。停止了已核实归属的 v9 编译进程，保留 build 收据及原编译源；持续开启的 Editor PID51148 未终止。v10 以换行后的完整边界定位并先完成 author，再另行 build。后续依赖步骤必须检查前项成功，不使用失败后仍继续的串行 shell 命令。
