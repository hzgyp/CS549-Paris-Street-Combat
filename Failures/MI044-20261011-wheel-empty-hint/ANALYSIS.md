# MI044：空库存提示切回枪后仍残留

2026-10-11。candidate_equipment_wheel_build_v3／wheel_wheelv3 的输入断言均通过，但实际03_final_hud.png显示已经高亮 RIFLE、FRAG仍有1枚，画面中央仍是 NO GRENADES REMAIN。此前烟雾弹空库存产生的3秒Notice没有在装备切换时失效，属于情境提示范围错误；输入／库存／枪械没有失败。不得用JSON pass忽略实图。

保留v3原编译源、Game、运行结果及该图。新v4只在滚轮切换时清除旧Notice；空槽选中时不显示道具外壳。原准备／投出／库存／引信／模型文件／手部挂接／枪械／保存均保持。新增见证要求空槽无选中道具、切回枪后HudInteraction不再含NO GRENADES；再看真实HUD和帮助页。

本轮参考MI034的失效提示要求。早期门槛是实际状态与像素一致；停止条件是错误提示仍出现或为隐藏问题改变资源／保存／原枪械门槛。v3输入通过保留为对应Game证据，不改标视觉通过。
