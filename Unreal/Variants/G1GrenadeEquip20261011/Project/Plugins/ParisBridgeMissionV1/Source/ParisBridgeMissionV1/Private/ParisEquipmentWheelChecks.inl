// Actual wheel/primary input; existing NPCs held only in this declared fixture.
void WheelInput(AParisBridgePlayerController* PC,bool Down){const auto K=Down?EKeys::MouseScrollDown:EKeys::MouseScrollUp;Tap(PC,K);PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::MouseWheelAxis,IE_Axis,Down?-1.f:1.f));}
void PrimaryInput(AParisBridgePlayerController* PC,bool Down){PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::LeftMouseButton,Down?IE_Pressed:IE_Released,Down?1:0));}
bool GrenadeFrame(UWorld* W,FEquipmentSession& S,AParisBridgePlayerController* PC,const FString& Kind){
    auto* A=S.SelectedVisual.IsValid()?S.SelectedVisual.Get():S.Held.Get();auto* D=Cast<AParisFPUpperBodyV19Actor>(Display(W,UGameplayStatics::GetPlayerCharacter(W,0)));
    if(!Expect(W,A&&D&&D->HasEquipmentPoseSource()&&S.EquipmentPoseSource.IsValid()&&Num(D,TEXT("HoldingAppliedAlpha"))<.001,TEXT("actual_grenade_source_not_rifle_grip_")+Kind))return false;
    FVector Origin,Extent;A->GetActorBounds(false,Origin,Extent);FVector2D Min(1e9,1e9),Max(-1e9,-1e9);bool Good=true;
    for(int32 I=0;I<8;++I){FVector2D V;Good&=PC->ProjectWorldLocationToScreen(Origin+Extent*FVector(I&1?1:-1,I&2?1:-1,I&4?1:-1),V);Min.X=FMath::Min(Min.X,V.X);Min.Y=FMath::Min(Min.Y,V.Y);Max.X=FMath::Max(Max.X,V.X);Max.Y=FMath::Max(Max.Y,V.Y);}
    int32 Width,Height;PC->GetViewportSize(Width,Height);const double Area=(Max.X-Min.X)*(Max.Y-Min.Y),Visible=FMath::Max(0.,FMath::Min(double(Width),Max.X)-FMath::Max(0.,Min.X))*FMath::Max(0.,FMath::Min(double(Height),Max.Y)-FMath::Max(0.,Min.Y));
    Event(W,TEXT("projected_model_min"),Kind+Min.ToString());Event(W,TEXT("projected_model_max"),Kind+Max.ToString());Event(W,TEXT("projected_visible_ratio"),Kind,Area>0?Visible/Area:0);
    return Expect(W,Good&&Max.X-Min.X>12&&Max.Y-Min.Y>16&&Area>0&&Visible/Area>.75,TEXT("actual_model_bounds_in_normal_view_")+Kind);
}
void EquipmentWheelCheck(UWorld* W,AParisBridgeMission* M,FEquipmentSession& S,AParisBridgePlayerController* PC,ACharacter* P,float DT){
    CheckClock+=DT;
    auto RifleRestored=[&](){auto* D=Display(W,P);return S.SelectedSlot==0&&S.ThrowKind.IsEmpty()&&!S.EquipmentPoseSource.IsValid()&&Num(D,TEXT("HoldingAppliedAlpha"))>.9999&&Num(D,TEXT("FingerRotationErrorDegrees"))<.0001;};

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
    if(CheckStep==0){if(M->Phase!=TEXT("Ready"))return;auto* D=Display(W,P);if(!D||!Flag(D,TEXT("Initialized"))){if(CheckClock>20)FinishCheck(W,false,TEXT("formal_FP_timeout"));return;}M->StartMission();HoldBrains(W);PC->SetControlRotation(FRotator(20,0,0));WheelInput(PC,true);if(!Expect(W,S.SelectedSlot==1,TEXT("physical_wheel_single_frag_selection")))return;CheckStep=1;CheckClock=0;}
    else if(CheckStep==1&&CheckClock>1){Picture(TEXT("01_frag_ready.png"));CheckStep=101;CheckClock=0;}
    else if(CheckStep==101&&CheckClock>.3&&!FScreenshotRequest::IsScreenshotRequested()){if(!GrenadeFrame(W,S,PC,TEXT("Frag_ready")))return;if(!Expect(W,S.EquipmentPoseTag==TEXT("Ready")&&S.ThrowKind.IsEmpty()&&S.Frag==2,TEXT("ready_loop_without_pin_or_spend")))return;CheckStep=2;CheckClock=0;}
    else if(CheckStep==2&&CheckClock>.3&&!FScreenshotRequest::IsScreenshotRequested()){PrimaryInput(PC,true);CheckStep=3;CheckClock=0;}
    else if(CheckStep==3&&CheckClock>4.5){if(!Expect(W,S.ThrowStage==TEXT("Hold")&&S.EquipmentPoseTag==TEXT("Hold")&&S.Frag==2&&S.Balls.IsEmpty()&&Num(P,TEXT("ShotSequence"))==0,TEXT("long_hold_loop_no_cooking_spend_or_fire")))return;if(!GrenadeFrame(W,S,PC,TEXT("Frag_hold")))return;Picture(TEXT("02_frag_hold.png"));CheckStep=4;CheckClock=0;}
    else if(CheckStep==4&&CheckClock>.3&&!FScreenshotRequest::IsScreenshotRequested()){PrimaryInput(PC,false);PrimaryInput(PC,false);CheckStep=5;CheckClock=0;}
    else if(CheckStep==5&&CheckClock>2&&S.ThrowKind.IsEmpty()&&Num(Display(W,P),TEXT("HoldingAppliedAlpha"))>.9999){if(!Expect(W,S.Frag==1&&S.FragThrown==1&&RifleRestored(),TEXT("frag_release_once_original_rifle_grip_restored")))return;WheelInput(PC,true);PrimaryInput(PC,true);PrimaryInput(PC,false);CheckStep=6;CheckClock=0;}
    else if(CheckStep==6&&CheckClock>2.2&&S.ThrowKind.IsEmpty()&&Num(Display(W,P),TEXT("HoldingAppliedAlpha"))>.9999){if(!Expect(W,S.Frag==0&&S.FragThrown==2&&RifleRestored(),TEXT("frag_exhausted_by_real_throws")))return;WheelInput(PC,true);if(!Expect(W,S.SelectedSlot==2,TEXT("forward_wheel_skips_empty_frag_to_smoke")))return;CheckStep=7;CheckClock=0;}
    else if(CheckStep==7&&CheckClock>1){Picture(TEXT("03_smoke_ready.png"));CheckStep=107;CheckClock=0;}
    else if(CheckStep==107&&CheckClock>.3&&!FScreenshotRequest::IsScreenshotRequested()){if(!GrenadeFrame(W,S,PC,TEXT("Smoke_ready")))return;CheckStep=8;CheckClock=0;}
    else if(CheckStep==8&&CheckClock>.3&&!FScreenshotRequest::IsScreenshotRequested()){WheelInput(PC,false);if(!Expect(W,S.SelectedSlot==0,TEXT("reverse_skips_empty_frag_to_rifle")))return;WheelInput(PC,false);if(!Expect(W,S.SelectedSlot==2,TEXT("reverse_available_smoke")))return;WheelInput(PC,true);if(!Expect(W,S.SelectedSlot==0,TEXT("forward_available_rifle")))return;WheelInput(PC,true);PrimaryInput(PC,true);CheckStep=9;CheckClock=0;}
    else if(CheckStep==9&&CheckClock>1.2){if(!GrenadeFrame(W,S,PC,TEXT("Smoke_hold")))return;Picture(TEXT("04_smoke_hold.png"));CheckStep=10;CheckClock=0;}
    else if(CheckStep==10&&CheckClock>.3&&!FScreenshotRequest::IsScreenshotRequested()){WheelInput(PC,true);PrimaryInput(PC,false);CheckStep=11;CheckClock=0;}
    else if(CheckStep==11&&CheckClock>1.2&&S.ThrowKind.IsEmpty()&&Num(Display(W,P),TEXT("HoldingAppliedAlpha"))>.9999){if(!Expect(W,S.Smoke==2&&S.SmokeThrown==0&&RifleRestored()&&Num(P,TEXT("ShotSequence"))==0,TEXT("cancel_ready_and_restore_without_spend_or_old_release_fire")))return;WheelInput(PC,true);PrimaryInput(PC,true);PrimaryInput(PC,false);CheckStep=12;CheckClock=0;}
    else if(CheckStep==12&&CheckClock>2.2&&S.ThrowKind.IsEmpty()&&Num(Display(W,P),TEXT("HoldingAppliedAlpha"))>.9999){if(!Expect(W,S.Smoke==1&&S.SmokeThrown==1&&RifleRestored(),TEXT("smoke_unique_release_and_rifle_restore")))return;WheelInput(PC,true);PrimaryInput(PC,true);PrimaryInput(PC,false);CheckStep=13;CheckClock=0;}
    else if(CheckStep==13&&CheckClock>2.2&&S.ThrowKind.IsEmpty()&&Num(Display(W,P),TEXT("HoldingAppliedAlpha"))>.9999){if(!Expect(W,S.Smoke==0&&S.SmokeThrown==2&&RifleRestored(),TEXT("both_grenade_types_exhausted_by_actual_input")))return;PrimaryInput(PC,true);for(int32 I=0;I<6;++I)WheelInput(PC,I%2==0);if(!Expect(W,RifleRestored()&&S.PrimaryHeld&&!S.SuppressPrimary&&!S.SelectedVisual.IsValid()&&!S.EquipmentPoseSource.IsValid(),TEXT("all_empty_wheel_no_slot_pose_hide_or_primary_state_change")))return;CheckStep=14;CheckClock=0;}
    else if(CheckStep==14&&CheckClock>.7){PrimaryInput(PC,false);if(!Expect(W,Num(P,TEXT("ShotSequence"))==1&&Num(P,TEXT("LoadedAmmo"))==7&&Num(P,TEXT("ReserveAmmo"))==10&&RifleRestored(),TEXT("remaining_rifle_original_fire_and_resource_rules")))return;Picture(TEXT("05_all_empty_rifle.png"));CheckStep=15;CheckClock=0;}
    else if(CheckStep==15&&CheckClock>.3&&!FScreenshotRequest::IsScreenshotRequested()){FinishCheck(W,true,TEXT("Native grenade ready/hold source and visible model projections; real depletion skips empty types both ways; only rifle leaves wheel and original grip/input unchanged"));}
    if(CheckClock>30)FinishCheck(W,false,TEXT("equip_pose_state_timeout"));
}
