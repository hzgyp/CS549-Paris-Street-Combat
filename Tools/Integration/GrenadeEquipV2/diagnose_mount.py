from pathlib import Path
root=Path(__file__).resolve().parents[3];p=root/'tmp/g1-tactical-equipment-20261010/candidate_grenade_equip_v1/Project/Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private'
f=p/'ParisEquipmentWheelChecks.inl';t=f.read_text('utf-8').replace('&&S.ThrowKind.IsEmpty()){if(!Expect(W,S.Frag','&&S.ThrowKind.IsEmpty()&&Num(Display(W,P),TEXT("HoldingAppliedAlpha"))>.9999){if(!Expect(W,S.Frag').replace('&&S.ThrowKind.IsEmpty()){if(!Expect(W,S.Smoke','&&S.ThrowKind.IsEmpty()&&Num(Display(W,P),TEXT("HoldingAppliedAlpha"))>.9999){if(!Expect(W,S.Smoke')
visual='''
    if(CheckMode==TEXT("visual")){
        if(CheckStep==0){if(M->Phase!=TEXT("Ready")||!Flag(Display(W,P),TEXT("Initialized")))return;M->StartMission();HoldBrains(W);PC->SetControlRotation(FRotator(20,0,0));WheelInput(PC,true);CheckStep=80;CheckClock=0;}
        else if(CheckStep==80&&CheckClock>1){Picture(TEXT("frag_with_hand.png"));CheckStep=81;CheckClock=0;}
        else if(CheckStep==81&&CheckClock>.3&&!FScreenshotRequest::IsScreenshotRequested()){auto* D=Display(W,P);auto* Pose=Cast<UPoseableMeshComponent>(Obj(D,TEXT("Pose")));Pose->SetVisibility(false,false);Picture(TEXT("frag_without_hand.png"));CheckStep=82;CheckClock=0;}
        else if(CheckStep==82){auto* D=Display(W,P);auto* Pose=Cast<UPoseableMeshComponent>(Obj(D,TEXT("Pose")));Pose->SetVisibility(false,false);if(CheckClock>.3&&!FScreenshotRequest::IsScreenshotRequested()){Pose->SetVisibility(true,true);WheelInput(PC,true);CheckStep=83;CheckClock=0;}}
        else if(CheckStep==83&&CheckClock>1){Picture(TEXT("smoke_with_hand.png"));CheckStep=84;CheckClock=0;}
        else if(CheckStep==84&&CheckClock>.3&&!FScreenshotRequest::IsScreenshotRequested()){auto* Pose=Cast<UPoseableMeshComponent>(Obj(Display(W,P),TEXT("Pose")));Pose->SetVisibility(false,false);Picture(TEXT("smoke_without_hand.png"));CheckStep=85;CheckClock=0;}
        else if(CheckStep==85){auto* Pose=Cast<UPoseableMeshComponent>(Obj(Display(W,P),TEXT("Pose")));Pose->SetVisibility(false,false);if(CheckClock>.3&&!FScreenshotRequest::IsScreenshotRequested()){Pose->SetVisibility(true,true);FinishCheck(W,true,TEXT("Opt-in render isolation: same actual pose/mount/camera, hide only hand render; no ordinary-game visibility change, no contact acceptance"));}}
        if(CheckClock>15)FinishCheck(W,false,TEXT("visual_diag_timeout"));return;
    }
'''
key='    if(CheckStep==0){if(M->Phase!=TEXT("Ready"))return;';assert key in t;t=t.replace(key,visual+key,1);f.write_text(t,encoding='utf-8')
f=p/'ParisTacticalEquipment.cpp';t=f.read_text('utf-8').replace('if(CheckMode==TEXT("wheel")){EquipmentWheelCheck','if(CheckMode==TEXT("wheel")||CheckMode==TEXT("visual")){EquipmentWheelCheck');f.write_text(t,encoding='utf-8')
f=root/'Failures/MI046-20261011-grenade-view-anchor/ANALYSIS.md';t=f.read_text('utf-8');t+='\nv2补充：正常Frag就绪／Hold的投影已入画、显示源非持枪，回枪第一轮通过；实际图中Frag仍被手部大量遮挡，不通过外观。随后第二次真实投出已经扣到0，但夹具在ThrowKind刚清空时即要求原握姿Alpha=1，忽略现有0.25秒显示返回混合而提前失败。后续夹具等待实际Alpha完成（保留30秒截止）而不改变原混合／库存门槛；新增独立手部渲染显隐诊断以判断道具遮挡，普通入口不隐藏手部。v2原源／Game／RESULT／实图保持。\n';f.write_text(t,encoding='utf-8')
f=root/'Docs/Development/MissionLoopV1/GRENADE_EQUIP_REVISION_IMPLEMENTATION_20261011_ZH.md';t=f.read_text('utf-8');t+='\nv3只读显隐诊断：v2图中的Frag仍不能清楚辨认，先保留姿势／挂接／镜头，在独立夹具短暂隐藏手部渲染并保留道具取图，确认遮挡来源后才改挂接。普通玩法不隐藏手、原0.25秒混合与门槛不变，回枪见证等待实际Alpha完成。\n';f.write_text(t,encoding='utf-8')
print('Render isolation and actual rifle-blend completion witness authored')
