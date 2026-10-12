from pathlib import Path
root=Path(__file__).resolve().parents[3]
p=root/'tmp/g1-tactical-equipment-20261010/candidate_equipment_wheel_v1/Project/Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private'
f=p/'ParisEquipmentWheelChecks.inl';t=f.read_text('utf-8')
t=t.replace('Picture(TEXT("01_selected_frag.png"));PrimaryInput(PC,true);CheckStep=2;CheckClock=0;','Picture(TEXT("01_selected_frag.png"));CheckStep=101;CheckClock=0;')
t=t.replace('else if(CheckStep==2&&CheckClock>4.5)', 'else if(CheckStep==101&&CheckClock>.3&&!FScreenshotRequest::IsScreenshotRequested()){PrimaryInput(PC,true);CheckStep=2;CheckClock=0;}\n    else if(CheckStep==2&&CheckClock>4.5)')
t=t.replace('WheelShots==1&&Num(P,TEXT("LoadedAmmo"))==7','Num(P,TEXT("ShotSequence"))==1&&Num(P,TEXT("LoadedAmmo"))==7')
t=t.replace('TEXT("original_rifle_fire_after_throw")))return;WheelInput','TEXT("original_rifle_fire_after_throw")))return;WheelShots=Num(P,TEXT("ShotSequence"));WheelInput')
f.write_text(t,encoding='utf-8')
f=p/'ParisEquipmentChecks.inl';t=f.read_text('utf-8')
t=t.replace('real G/Q input;','real wheel/primary input;')
t=t.replace('TEXT("enemy_clear_alone_unlocks_with_active_equipment")))return;Tap(PC,EKeys::E);','TEXT("enemy_clear_alone_unlocks_with_active_equipment")))return;Tap(PC,EKeys::MouseScrollUp);if(!Expect(W,S.SelectedSlot==2&&S.ThrowKind.IsEmpty(),TEXT("selected_smoke_does_not_add_save_admission_gate")))return;Tap(PC,EKeys::E);')
f.write_text(t,encoding='utf-8')
f=root/'Docs/Development/MissionLoopV1/EQUIPMENT_WHEEL_INPUT_IMPLEMENTATION_20261011_ZH.md';t=f.read_text('utf-8')
t+='\n## v2 见证纠正（同日）\n\n已读 MI033 与新 MI043：截图请求后先等真实后续帧再按左键；步枪按键由原绑定下一帧处理，取值在已处理后进行。v1 失败只纠正见证，不改枪械、手部或保存门槛；v2 加选中烟雾弹仍可保存的检查。原失败身份保留，早期输入门槛及回归重新使用同一 v2 Game。\n'
f.write_text(t,encoding='utf-8')
print('Witness corrected; original gameplay retained')
