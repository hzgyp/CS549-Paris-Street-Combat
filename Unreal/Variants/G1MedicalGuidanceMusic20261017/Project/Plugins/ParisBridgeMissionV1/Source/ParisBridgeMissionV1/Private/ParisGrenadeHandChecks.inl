// Opt-in actual input/pose/prop/release check. No normal-entry fixture or input.
TArray<TSharedPtr<FJsonValue>> HandSamples,HandAssertions;
double HandOriginalLengths[4]={},HandMaxLengthDrift=0;
TWeakObjectPtr<AActor> HandCover;
double HandFrameDelta=0;
void HandPicture(const TCHAR* Name){if(CheckMode==TEXT("hands"))Picture(Name);}
TArray<TSharedPtr<FJsonValue>> HandVector(FVector V){TArray<TSharedPtr<FJsonValue>> R;for(double X:{V.X,V.Y,V.Z})R.Add(MakeShared<FJsonValueNumber>(X));return R;}
void FinishHands(UWorld* W,bool Pass,const FString& Why){
    auto& S=Session(W);auto* P=UGameplayStatics::GetPlayerCharacter(W,0);
    auto R=MakeShared<FJsonObject>();R->SetStringField(TEXT("status"),Pass?TEXT("pass_native_grenade_hands"):TEXT("failed_grenade_hands"));R->SetStringField(TEXT("reason"),Why);
    R->SetStringField(TEXT("scope"),TEXT("Original wheel/primary/Escape/V input; NPC brains paused; temporary visibility-only cover ignores Pawn for isolated release-clamp check. No refill, no body/finger/native edits, not natural combat."));
    R->SetArrayField(TEXT("samples"),HandSamples);R->SetArrayField(TEXT("assertions"),HandAssertions);R->SetArrayField(TEXT("events"),S.Events);
    R->SetNumberField(TEXT("max_fp_arm_length_drift_cm"),HandMaxLengthDrift);
    R->SetBoolField(TEXT("fixed_simulation_step"),FApp::UseFixedTimeStep());R->SetBoolField(TEXT("screenshots_enabled"),CheckMode==TEXT("hands"));
    R->SetNumberField(TEXT("frag"),S.Frag);R->SetNumberField(TEXT("smoke"),S.Smoke);R->SetNumberField(TEXT("frag_thrown"),S.FragThrown);R->SetNumberField(TEXT("smoke_thrown"),S.SmokeThrown);
    for(const TCHAR* K:{TEXT("LoadedAmmo"),TEXT("ReserveAmmo"),TEXT("ShotSequence"),TEXT("Health")})R->SetNumberField(K,Num(P,K));
    R->SetStringField(TEXT("action"),Name(P,TEXT("ActionState")).ToString());
    FString J;FJsonSerializer::Serialize(R,TJsonWriterFactory<>::Create(&J));FFileHelper::SaveStringToFile(J,*(CheckOut/TEXT("RESULT.json")),FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
    if(HandCover.IsValid())HandCover->Destroy();CheckFinished=true;FPlatformMisc::RequestExit(false);
}
bool HandAssert(UWorld* W,bool Pass,const FString& Name){
    auto R=MakeShared<FJsonObject>();R->SetStringField(TEXT("name"),Name);R->SetBoolField(TEXT("pass"),Pass);HandAssertions.Add(MakeShared<FJsonValueObject>(R));
    if(!Pass)FinishHands(W,false,Name);return Pass;
}
bool HandSample(UWorld* W,FEquipmentSession& S,ACharacter* P){
    auto* D=Display(W,P);auto* FP=D?Cast<UPoseableMeshComponent>(Obj(D,TEXT("Pose"))):nullptr;
    if(!FP)return HandAssert(W,false,TEXT("FP_pose_present"));
    int32 I=0;
    for(const TCHAR* Side:{TEXT("l"),TEXT("r")}){
        const FVector U=FP->GetSocketLocation(FName(*(FString(TEXT("upperarm_"))+Side))),L=FP->GetSocketLocation(FName(*(FString(TEXT("lowerarm_"))+Side))),H=FP->GetSocketLocation(FName(*(FString(TEXT("hand_"))+Side)));
        for(double Length:{FVector::Distance(U,L),FVector::Distance(L,H)}){if(HandOriginalLengths[I]==0)HandOriginalLengths[I]=Length;HandMaxLengthDrift=FMath::Max(HandMaxLengthDrift,FMath::Abs(Length-HandOriginalLengths[I++]));}
    }
    auto* A=S.Held.IsValid()?S.Held.Get():S.SelectedVisual.Get();if(!A)return true;
    auto* Mesh=GrenadeMountComponent(W);auto* C=A->GetRootComponent();
    const bool Correct=Mesh&&C->GetAttachParent()==Mesh&&C->GetAttachSocketName()==TEXT("hand_l");
    auto R=MakeShared<FJsonObject>();R->SetNumberField(TEXT("time"),W->GetTimeSeconds());R->SetStringField(TEXT("stage"),S.ThrowKind.IsEmpty()?TEXT("Ready"):S.ThrowStage);
    R->SetNumberField(TEXT("action_clock"),S.ActionClock);R->SetNumberField(TEXT("frame_delta"),HandFrameDelta);
    R->SetStringField(TEXT("model"),S.ThrowKind.IsEmpty()?S.SelectedVisualKind:S.ThrowKind);R->SetStringField(TEXT("socket"),C->GetAttachSocketName().ToString());
    R->SetBoolField(TEXT("actual_body"),Mesh==P->GetMesh());R->SetArrayField(TEXT("model_center"),HandVector(A->GetActorLocation()));
    if(Mesh){R->SetArrayField(TEXT("left_hand"),HandVector(Mesh->GetSocketLocation(TEXT("hand_l"))));R->SetArrayField(TEXT("right_hand"),HandVector(Mesh->GetSocketLocation(TEXT("hand_r"))));}
    if(Mesh&&ParisActionBindings::Display(P)&&ParisActionBindings::Display(P)->UnifiedObserver()){
        const double NativeError=FVector::Distance(Mesh->GetSocketLocation(TEXT("hand_l")),P->GetMesh()->GetSocketLocation(TEXT("hand_l")));
        R->SetNumberField(TEXT("visible_vs_native_left_hand_cm"),NativeError);
        if(S.ThrowStage==TEXT("Release")&&S.ActionClock>=.26&&S.ActionClock<.45)
            if(!HandAssert(W,NativeError<.0001,TEXT("visible_release_hand_matches_original_native_body_frame")))return false;
    }
    HandSamples.Add(MakeShared<FJsonValueObject>(R));
    return Correct||HandAssert(W,false,TEXT("visible_model_remains_on_actual_active_left_hand"));
}
bool HandReleaseAssert(UWorld* W,FEquipmentSession& S,int32 Count,bool ExpectedClamp){
    TArray<TSharedPtr<FJsonObject>> Releases;
    for(const auto& E:S.Events)if(auto O=E->AsObject())if(O->GetStringField(TEXT("kind"))==TEXT("release_origin"))Releases.Add(O);
    if(!HandAssert(W,Releases.Num()==Count,TEXT("unique_release_count_")+FString::FromInt(Count)))return false;
    const auto& R=Releases.Last();
    if(!HandAssert(W,R->GetStringField(TEXT("hand"))==TEXT("hand_l")&&R->GetBoolField(TEXT("clamped"))==ExpectedClamp,TEXT("active_left_origin_and_cover_state_")+FString::FromInt(Count)))return false;
    if(!HandAssert(W,R->GetNumberField(TEXT("release_rotation_delta_degrees"))<.001,TEXT("visible_release_orientation_continuity_")+FString::FromInt(Count)))return false;
    if(!ExpectedClamp&&!HandAssert(W,R->GetNumberField(TEXT("visible_bounds_centre_delta_cm"))<.001,TEXT("actual_visible_mesh_centre_does_not_jump_")+FString::FromInt(Count)))return false;
    if(!ExpectedClamp&&!HandAssert(W,R->GetNumberField(TEXT("centre_to_spawn_cm"))<.00001,TEXT("projectile_begins_at_visible_model_not_camera_")+FString::FromInt(Count)))return false;
    return HandAssert(W,R->GetNumberField(TEXT("action_clock"))>=.375&&R->GetNumberField(TEXT("action_clock"))<.45,TEXT("release_during_measured_native_forward_swing_")+FString::FromInt(Count));
}
void GrenadeHandCheck(UWorld* W,AParisBridgeMission* M,FEquipmentSession& S,AParisBridgePlayerController* PC,ACharacter* P,float DT){
    HandFrameDelta=DT;
    CheckClock+=DT;
    if(CheckStep==0){
        if(M->Phase!=TEXT("Ready")||!Flag(Display(W,P),TEXT("Initialized")))return;
        if(!HandSample(W,S,P))return;M->StartMission();HoldBrains(W);PC->SetControlRotation(FRotator(0,0,0));
        Event(W,TEXT("fixture"),TEXT("Hand audit uses original input and real resources; NPC brains paused only for isolated visual checks"));
        WheelInput(PC,true);CheckStep=1;CheckClock=0;return;
    }
    if(!HandSample(W,S,P))return;
    auto Restored=[&](){return S.SelectedSlot==0&&S.ThrowKind.IsEmpty()&&!S.EquipmentPoseSource.IsValid()&&Num(Display(W,P),TEXT("HoldingAppliedAlpha"))>.9999&&Num(Display(W,P),TEXT("FingerRotationErrorDegrees"))<.0001;};
    if(CheckStep==1&&CheckClock>1){
        if(!GrenadeFrame(W,S,PC,TEXT("Frag_left_ready")))return;HandPicture(TEXT("01_frag_left_ready.png"));CheckStep=2;CheckClock=0;
    }else if(CheckStep==2&&CheckClock>.3&&!FScreenshotRequest::IsScreenshotRequested()){PrimaryInput(PC,true);CheckStep=3;CheckClock=0;
    }else if(CheckStep==3&&S.ThrowStage==TEXT("Hold")&&CheckClock>1.2){
        if(!GrenadeFrame(W,S,PC,TEXT("Frag_left_hold")))return;HandPicture(TEXT("02_frag_left_hold.png"));CheckStep=4;CheckClock=0;
    }else if(CheckStep==4&&CheckClock>.3&&!FScreenshotRequest::IsScreenshotRequested()){PrimaryInput(PC,false);PrimaryInput(PC,false);CheckStep=5;CheckClock=0;
    }else if(CheckStep==5&&CheckClock>.18){HandPicture(TEXT("03_frag_left_windup.png"));CheckStep=6;
    }else if(CheckStep==6&&S.ThrowStage==TEXT("Release")&&S.ActionClock>=.30&&!S.ThrowCommitted){HandPicture(TEXT("04_frag_left_forward_swing.png"));CheckStep=7;
    }else if(CheckStep==7&&CheckClock>2&&Restored()){
        if(!HandAssert(W,S.Frag==1&&S.FragThrown==1&&S.Smoke==2,TEXT("frag_once_release_and_original_rifle_return"))||!HandReleaseAssert(W,S,1,false))return;
        HandPicture(TEXT("05_frag_rifle_return.png"));CheckStep=70;CheckClock=0;
    }else if(CheckStep==70&&CheckClock>.3&&!FScreenshotRequest::IsScreenshotRequested()){
        WheelInput(PC,true);WheelInput(PC,true);Tap(PC,EKeys::V);CheckStep=8;CheckClock=0;
    }else if(CheckStep==8&&CheckClock>1&&!FScreenshotRequest::IsScreenshotRequested()){
        if(!HandAssert(W,S.SelectedSlot==2&&ParisActionBindings::Display(P)&&ParisActionBindings::Display(P)->UnifiedObserver()&&GrenadeMountComponent(W)==ParisActionBindings::VisibleBody(P),TEXT("smoke_current_visible_body_left_mount")))return;
        HandPicture(TEXT("06_smoke_body_ready.png"));PrimaryInput(PC,true);CheckStep=9;CheckClock=0;
    }else if(CheckStep==9&&S.ThrowStage==TEXT("Hold")&&CheckClock>1.2){HandPicture(TEXT("07_smoke_body_hold.png"));CheckStep=10;CheckClock=0;
    }else if(CheckStep==10&&CheckClock>.3&&!FScreenshotRequest::IsScreenshotRequested()){PrimaryInput(PC,false);CheckStep=11;CheckClock=0;
    }else if(CheckStep==11&&CheckClock>.18){HandPicture(TEXT("08_smoke_body_windup.png"));CheckStep=12;
    }else if(CheckStep==12&&S.ThrowStage==TEXT("Release")&&S.ActionClock>=.30&&!S.ThrowCommitted){HandPicture(TEXT("09_smoke_body_forward_swing.png"));CheckStep=13;
    }else if(CheckStep==13&&CheckClock>2&&Restored()){
        if(!HandAssert(W,S.Smoke==1&&S.SmokeThrown==1,TEXT("smoke_unique_actual_body_release"))||!HandReleaseAssert(W,S,2,false))return;
        Tap(PC,EKeys::V);CheckStep=14;CheckClock=0;
    }else if(CheckStep==14&&CheckClock>.8){
        if(!HandAssert(W,Restored()&&!Display(W,P)->IsHidden(),TEXT("observer_returns_original_FP_rifle")))return;
        HandPicture(TEXT("10_original_FP_return.png"));CheckStep=140;CheckClock=0;
    }else if(CheckStep==140&&CheckClock>.3&&!FScreenshotRequest::IsScreenshotRequested()){
        WheelInput(PC,true);PrimaryInput(PC,true);CheckStep=15;CheckClock=0;
    }else if(CheckStep==15&&CheckClock>.2){Tap(PC,EKeys::Escape);PrimaryInput(PC,false);CheckStep=16;CheckClock=0;
    }else if(CheckStep==16&&CheckClock>1.6&&Restored()){
        if(!HandAssert(W,S.Frag==1&&S.FragThrown==1&&S.Smoke==1,TEXT("cancel_left_preparation_without_spend")))return;
        HandPicture(TEXT("11_cancel_rifle_return.png"));CheckStep=160;CheckClock=0;
    }else if(CheckStep==160&&CheckClock>.3&&!FScreenshotRequest::IsScreenshotRequested()){
        WheelInput(PC,true);PrimaryInput(PC,true);PrimaryInput(PC,false);CheckStep=17;CheckClock=0;
    }else if(CheckStep==17&&S.ThrowStage==TEXT("Release")&&S.ActionClock<.15&&!HandCover.IsValid()){
        FVector Eye;FRotator View;PC->GetPlayerViewPoint(Eye,View);auto* A=W->SpawnActor<AActor>();auto* C=NewObject<UBoxComponent>(A);A->AddInstanceComponent(C);A->SetRootComponent(C);
        C->SetBoxExtent(FVector(1,100,100));C->SetCollisionEnabled(ECollisionEnabled::QueryOnly);C->SetCollisionResponseToAllChannels(ECR_Ignore);C->SetCollisionResponseToChannel(ECC_Visibility,ECR_Block);C->SetCanEverAffectNavigation(false);C->RegisterComponent();
        A->SetActorLocation(Eye+View.Vector()*10);A->SetActorRotation(View);HandCover=A;
        Event(W,TEXT("fixture"),TEXT("Temporary 2cm-thick camera-forward visibility cover at10cm, Pawn ignored; tests real3.3cm release sweep, no native map/capsule change"));
    }else if(CheckStep==17&&S.ThrowCommitted){
        if(!HandReleaseAssert(W,S,3,true)||!HandAssert(W,S.Frag==0&&S.FragThrown==2,TEXT("covered_throw_commits_once_with_original_inventory")))return;
        if(HandCover.IsValid())HandCover->Destroy();HandCover.Reset();CheckStep=18;CheckClock=0;
    }else if(CheckStep==18&&CheckClock>2&&Restored()&&!FScreenshotRequest::IsScreenshotRequested()){
        if(!HandAssert(W,HandSamples.Num()>100&&HandMaxLengthDrift<.001,TEXT("continuous_original_arm_lengths_through_affected_actions")))return;
        if(!HandAssert(W,Num(P,TEXT("LoadedAmmo"))==8&&Num(P,TEXT("ReserveAmmo"))==10&&Num(P,TEXT("ShotSequence"))==0&&S.Smoke==1,TEXT("original_ammunition_and_finite_equipment_conservation")))return;
        FinishHands(W,true,TEXT("Original left native hand matches prop through FP/body preparation/hold/swing; actual model-centre release, near-cover clamp, cancel/observer/rifle return and original resources"));
    }
    if(CheckClock>20)FinishHands(W,false,TEXT("hand_case_timeout_step_")+FString::FromInt(CheckStep));
}
