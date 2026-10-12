# MI036：假定原开始菜单Enter总是选择开始

2026-10-11。v4 `ui_pages_v4` 在正常关闭UI后未产生RESULT，Game exit0。日志明确是原 `PARIS_INTERACTION_MENU action=2 phase=Ready` 触发Exit，已经拍到前九页，不能把这次退出算通过，也不能称为崩溃。

UI探针从帮助/设置返回原Ready菜单后直接Enter。原菜单按当前MenuSelected执行，初始鼠标位置/原hover可能已经选中退出，MenuSelected并不保证为0。此前同一假设偶然通过，无法证明稳定。

保留v4源/Game、pause/equipment_pause通过记录及pages的无RESULT命令、日志、图片。v5仅改UI探针，明确用实际鼠标输入点击原开始按钮；不把MenuSelected写成0、不直接调用StartMission、不改原菜单选择、模型或存档。原UI的BEGIN MISSION按钮本来直接执行其清晰标注的动作。

最终同一Game重跑并核对真实开始、资源、菜单返回/确认、存档提示清除。停止条件为再出现不完整RESULT或意外退出；退出码0本身不能证明流程通过。
