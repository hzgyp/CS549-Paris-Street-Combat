# MI035：把旧装备恢复用例名称误当作运行模式

2026-10-11。UI回归runner用 `restore_v16_equipment` 同时作为独立测试身份和 `-ParisEquipmentCheck` 模式；Game只接受 `restore_equipment`。v3返回 `failed_restore_v16_equipment` / `unknown_check_mode`，exit0。此结果不能视为旧v16存档不兼容，也不能算通过。

保留 `checks/restore_v16_equipment_ui_v3` 的复制seed、原命令、日志、结果。原地雷通过记录的实际launch模式为restore_equipment，独立身份用来说明seed来自旧v16。

修正runner仅将此项实际Mode映射为restore_equipment，保留独立身份和明确seed路径/hash。最终v4重新实际运行，使用原验证器和加载器；不修改存档版本、config、资源或迁移旧用户档。若仍失败则按实际原因停止，不能用别名错误掩盖兼容失败。
