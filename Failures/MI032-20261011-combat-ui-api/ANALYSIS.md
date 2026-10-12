# MI032 作战菜单的 UE API 编译失败

2026-10-11。新的独立 UI candidate_ui_v1 编译时访问了基类受保护的 bShouldPerformFullTickWhenPaused；另外把 UE5.8 GetPawn 返回的 TObjectPtr 用 auto* 接收，产生类型错误及级联格式校验错误。游戏尚未进入运行验证，不能称为原菜单、模型或存档问题。

保留 tmp/g1-tactical-equipment-20261010/candidate_ui_v1 的完整源、compiled-source-game、build-game.json/log、保护审计；本轮未改 native 或用户档。工具模板后续修订不覆盖该失败候选。

candidate_ui_v2 使用派生 controller 的非反射 setter 保存/恢复原暂停完整Tick位，并显式取得 APawn 指针。原反射字段/存档算法继续逐字保护；不增加 UPROPERTY，不更改暂停或资源验收阈值。新候选须独立编译与实际 UI/暂停/原枪械保存回归，旧失败不改标通过。
