from pathlib import Path
root=Path(__file__).resolve().parents[3]
p=root/'tmp/g1-tactical-equipment-20261010/candidate_equipment_wheel_v1/Project/Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private'
f=p/'ParisTacticalEquipment.cpp';t=f.read_text('utf-8')
t=t.replace('HideGun(W,P,true);\n    const FString Kind=SlotKind(S.SelectedSlot);','HideGun(W,P,true);\n    if((S.SelectedSlot==1?S.Frag:S.Smoke)==0){ClearSelectedVisual(S);return;}\n    const FString Kind=SlotKind(S.SelectedSlot);',1)
t=t.replace('S.SelectedSlot=(S.SelectedSlot+Wheel+3)%3;ClearSelectedVisual(S);','S.SelectedSlot=(S.SelectedSlot+Wheel+3)%3;ClearSelectedVisual(S);S.Notice.Empty();S.NoticeUntil=0;',1)
f.write_text(t,encoding='utf-8')
f=p/'ParisEquipmentWheelChecks.inl';t=f.read_text('utf-8')
t=t.replace('S.ThrowKind.IsEmpty()&&S.Smoke==0&&Num(P,TEXT("ShotSequence"))','S.ThrowKind.IsEmpty()&&!S.SelectedVisual.IsValid()&&S.Smoke==0&&Num(P,TEXT("ShotSequence"))',1)
t=t.replace('if(!Expect(W,Num(P,TEXT("ShotSequence"))==WheelShots,TEXT("empty_hold_switch_old_release_not_shot")))return;','if(!Expect(W,Num(P,TEXT("ShotSequence"))==WheelShots&&!HudInteraction(W).Contains(TEXT("NO GRENADES")),TEXT("empty_hold_switch_old_release_not_shot_or_stale_hint")))return;',1)
f.write_text(t,encoding='utf-8')
f=root/'Docs/Development/MissionLoopV1/EQUIPMENT_WHEEL_INPUT_IMPLEMENTATION_20261011_ZH.md';t=f.read_text('utf-8');t+='\n## v4 提示纠正（同日）\n\nMI044记录v3真实HUD在切回步枪后仍显示烟雾弹空库存Notice。沿用已读MI034，滚轮切换立即清除旧提示，空槽不显示外壳；新增无旧提示／无空槽道具断言并复看实际像素。保持原模型、挂接、投掷／枪械／存档函数及门槛，v3通过的输入结果和失败实图仍保留。最终统一Game重新验证相关回归。\n';f.write_text(t,encoding='utf-8')
print('Empty slot visual and switch hint fixed; original prepare/commit retained')
