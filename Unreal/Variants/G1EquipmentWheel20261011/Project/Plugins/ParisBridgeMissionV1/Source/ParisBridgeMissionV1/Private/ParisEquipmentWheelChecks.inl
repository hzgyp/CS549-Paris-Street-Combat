// Opt-in check. Drives the same digital wheel pair and mouse events as SceneViewport.
void WheelInput(AParisBridgePlayerController* PC,bool Down){const auto K=Down?EKeys::MouseScrollDown:EKeys::MouseScrollUp;Tap(PC,K);PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::MouseWheelAxis,IE_Axis,Down?-1.f:1.f));}
void PrimaryInput(AParisBridgePlayerController* PC,bool Down){PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::LeftMouseButton,Down?IE_Pressed:IE_Released,Down?1:0));}
double WheelShots=0;
void EquipmentWheelCheck(UWorld* W,AParisBridgeMission* M,FEquipmentSession& S,AParisBridgePlayerController* PC,ACharacter* P,float DT){
    CheckClock+=DT;
    if(CheckStep==0){if(M->Phase!=TEXT("Ready"))return;auto* D=Display(W,P);if(!D||!Flag(D,TEXT("Initialized"))){if(CheckClock>20)FinishCheck(W,false,TEXT("formal_FP_timeout"));return;}M->StartMission();HoldBrains(W);PC->SetControlRotation(FRotator(20,0,0));
        if(!Expect(W,S.SelectedSlot==0,TEXT("default_rifle")))return;
        WheelInput(PC,true);if(!Expect(W,S.SelectedSlot==1,TEXT("physical_wheel_down_one_step_not_two")))return;
        WheelInput(PC,true);if(!Expect(W,S.SelectedSlot==2,TEXT("wheel_smoke")))return;
        WheelInput(PC,true);if(!Expect(W,S.SelectedSlot==0,TEXT("wheel_wrap_rifle")))return;
        WheelInput(PC,false);if(!Expect(W,S.SelectedSlot==2,TEXT("wheel_up_reverse")))return;
        WheelInput(PC,false);WheelInput(PC,false);if(!Expect(W,S.SelectedSlot==0,TEXT("reverse_wrap_rifle")))return;
        // Old gameplay shortcuts must no longer cause a hidden throw.
        PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::G,IE_Pressed,1));PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::G,IE_Released,0));PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::Q,IE_Pressed,1));PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::Q,IE_Released,0));
        if(!Expect(W,S.ThrowKind.IsEmpty()&&S.Balls.IsEmpty(),TEXT("G_Q_retired")))return;
        WheelInput(PC,true);CheckStep=1;CheckClock=0;return;
    }
    if(CheckStep==1&&CheckClock>.3){auto* D=Display(W,P);auto* Gun=Cast<UPrimitiveComponent>(Obj(D,TEXT("Gun")));if(!Expect(W,S.SelectedVisual.IsValid()&&Gun&&!Gun->IsVisible()&&S.ThrowKind.IsEmpty(),TEXT("selected_frag_drawn_without_preparation")))return;Picture(TEXT("01_selected_frag.png"));CheckStep=101;CheckClock=0;}
    else if(CheckStep==101&&CheckClock>.3&&!FScreenshotRequest::IsScreenshotRequested()){PrimaryInput(PC,true);CheckStep=2;CheckClock=0;}
    else if(CheckStep==2&&CheckClock>4.5){if(!Expect(W,S.ThrowStage==TEXT("Hold")&&S.Frag==2&&S.FragThrown==0&&S.Balls.IsEmpty()&&Num(P,TEXT("ShotSequence"))==0,TEXT("long_hold_no_cooking_spend_or_rifle_shot")))return;Picture(TEXT("02_hold.png"));CheckStep=3;CheckClock=0;}
    else if(CheckStep==3&&CheckClock>.25){PrimaryInput(PC,false);PrimaryInput(PC,false);WheelInput(PC,true);Tap(PC,EKeys::Escape);if(!Expect(W,S.SelectedSlot==1&&S.ReleaseQueued,TEXT("release_cannot_be_cancelled_by_wheel_or_escape")))return;CheckStep=4;CheckClock=0;}
    else if(CheckStep==4&&S.ThrowKind.IsEmpty()&&CheckClock>2){if(!Expect(W,S.Frag==1&&S.FragThrown==1&&S.SelectedSlot==0&&Num(P,TEXT("ShotSequence"))==0,TEXT("release_spends_once_auto_rifle_no_leaked_shot")))return;Tap(PC,EKeys::LeftMouseButton);WheelShots=Num(P,TEXT("ShotSequence"));CheckStep=5;CheckClock=0;}
    else if(CheckStep==5&&CheckClock>.7){if(!Expect(W,Num(P,TEXT("ShotSequence"))==1&&Num(P,TEXT("LoadedAmmo"))==7,TEXT("original_rifle_fire_after_throw")))return;WheelShots=Num(P,TEXT("ShotSequence"));WheelInput(PC,false);PrimaryInput(PC,true);CheckStep=6;CheckClock=0;}
    else if(CheckStep==6&&CheckClock>.9){WheelInput(PC,true);PrimaryInput(PC,false);CheckStep=7;CheckClock=0;}
    else if(CheckStep==7&&S.ThrowKind.IsEmpty()&&CheckClock>1.2){if(!Expect(W,S.SelectedSlot==0&&S.Smoke==2&&S.SmokeThrown==0&&Num(P,TEXT("ShotSequence"))==WheelShots,TEXT("held_switch_cancels_without_spend_or_release_shot")))return;WheelInput(PC,true);PrimaryInput(PC,true);CheckStep=8;CheckClock=0;}
    else if(CheckStep==8&&CheckClock>.2){Tap(PC,EKeys::Escape);PrimaryInput(PC,false);CheckStep=9;CheckClock=0;}
    else if(CheckStep==9&&S.ThrowKind.IsEmpty()&&CheckClock>1.2){if(!Expect(W,S.SelectedSlot==0&&S.Frag==1&&S.FragThrown==1&&Num(P,TEXT("ShotSequence"))==WheelShots&&!ParisCombatUI::IsOpen(PC),TEXT("escape_cancel_no_spend_menu_or_shot")))return;WheelInput(PC,false);PrimaryInput(PC,true);PrimaryInput(PC,false);CheckStep=10;CheckClock=0;}
    else if(CheckStep==10&&S.ThrowKind.IsEmpty()&&!S.Clouds.IsEmpty()){if(!Expect(W,S.Smoke==1&&S.SmokeThrown==1&&!S.Clouds.IsEmpty()&&S.SelectedSlot==0,TEXT("quick_click_smoke_unique_commit")))return;WheelInput(PC,false);PrimaryInput(PC,true);PrimaryInput(PC,false);CheckStep=11;CheckClock=0;}
    else if(CheckStep==11&&S.ThrowKind.IsEmpty()&&CheckClock>2.2){if(!Expect(W,S.Smoke==0&&S.SmokeThrown==2,TEXT("smoke_inventory_exhausted_normally")))return;WheelInput(PC,false);PrimaryInput(PC,true);Tap(PC,EKeys::R);Tap(PC,EKeys::RightMouseButton);CheckStep=12;CheckClock=0;}
    else if(CheckStep==12&&CheckClock>.4){if(!Expect(W,S.ThrowKind.IsEmpty()&&!S.SelectedVisual.IsValid()&&S.Smoke==0&&Num(P,TEXT("ShotSequence"))==WheelShots&&Num(P,TEXT("LoadedAmmo"))==7,TEXT("empty_selected_slot_does_not_fire_reload_or_throw")))return;WheelInput(PC,true);PrimaryInput(PC,false);CheckStep=13;CheckClock=0;}
    else if(CheckStep==13&&CheckClock>.4){if(!Expect(W,Num(P,TEXT("ShotSequence"))==WheelShots&&!HudInteraction(W).Contains(TEXT("NO GRENADES")),TEXT("empty_hold_switch_old_release_not_shot_or_stale_hint")))return;Tap(PC,EKeys::LeftMouseButton);CheckStep=14;CheckClock=0;}
    else if(CheckStep==14&&CheckClock>.7){if(!Expect(W,Num(P,TEXT("ShotSequence"))==WheelShots+1&&Num(P,TEXT("LoadedAmmo"))==6,TEXT("new_press_after_switch_uses_original_rifle")))return;WheelShots=Num(P,TEXT("ShotSequence"));Tap(PC,EKeys::Escape);if(!Expect(W,ParisCombatUI::IsOpen(PC),TEXT("menu_open")))return;WheelInput(PC,true);Tap(PC,EKeys::LeftMouseButton);if(!Expect(W,S.SelectedSlot==0&&Num(P,TEXT("ShotSequence"))==WheelShots&&S.ThrowKind.IsEmpty(),TEXT("paused_menu_swallows_wheel_and_mouse")))return;Tap(PC,EKeys::Escape);CheckStep=15;CheckClock=0;}
    else if(CheckStep==15&&CheckClock>.5){Picture(TEXT("03_final_hud.png"));CheckStep=16;CheckClock=0;}
    else if(CheckStep==16&&CheckClock>.3){FinishCheck(W,true,TEXT("Real wheel+axis pairing, long primary hold, unique release, empty slots, cancellation, rifle routing and menu isolation"));}
    if(CheckClock>30)FinishCheck(W,false,TEXT("wheel_state_timeout"));
}
