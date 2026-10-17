// Explicit opt-in deformation coverage; ordinary entry receives no input.
double PoseMaxNativeChainAngle=0,PoseMaxNativeTranslation=0;
int32 PoseShotIndex=0,PoseComparedFrames=0;
FString PoseLastSourceTag;int32 PoseStableSourceFrames=0;
void PoseTrace(UWorld* W,FEquipmentSession& S,ACharacter* P){
    HandSample(W,S,P);
    auto* D=Display(W,P);auto* FP=Cast<UPoseableMeshComponent>(Obj(D,TEXT("Pose")));auto* Native=S.EquipmentPoseSource.Get();
    if(PoseLastSourceTag!=S.EquipmentPoseTag){PoseLastSourceTag=S.EquipmentPoseTag;PoseStableSourceFrames=0;}else ++PoseStableSourceFrames;
    if(!FP||!Native||PoseStableSourceFrames<2||Num(D,TEXT("HoldingAppliedAlpha"))>.00001||Num(D,TEXT("SourceTransitionAlpha"))<.99999)return;
    const auto& Ref=CastChecked<USkeletalMesh>(FP->GetSkinnedAsset())->GetRefSkeleton();
    const auto& Src=Native->GetSkeletalMeshAsset()->GetRefSkeleton();const auto& C=Native->GetComponentSpaceTransforms();
    for(int32 I=0;I<Ref.GetNum();++I){const int32 N=Src.FindBoneIndex(Ref.GetBoneName(I)),Parent=Src.GetParentIndex(N);if(Parent<0)continue;
        const auto Local=C[N].GetRelativeTransform(C[Parent]);const auto& Actual=FP->BoneSpaceTransforms[I];
        PoseMaxNativeTranslation=FMath::Max(PoseMaxNativeTranslation,FVector::Distance(Local.GetLocation(),Actual.GetLocation()));
        // Left arm IK owns these three rotations. Descendant twist/finger and
        // all torso/clavicle/right arm locals must retain native coherence.
        const FName Name=Ref.GetBoneName(I);
        if(Name!=TEXT("upperarm_l")&&Name!=TEXT("lowerarm_l")&&Name!=TEXT("hand_l"))
            PoseMaxNativeChainAngle=FMath::Max(PoseMaxNativeChainAngle,FMath::RadiansToDegrees(Local.GetRotation().AngularDistance(Actual.GetRotation())));
    }
    ++PoseComparedFrames;
}
void PosePicture(UWorld* W,FEquipmentSession& S,ACharacter* P,const TCHAR* Label){
    SleeveSample(W,P,Label);
    auto O=SleeveSamples.Last()->AsObject();O->SetNumberField(TEXT("capture_step"),CheckStep);O->SetNumberField(TEXT("action_clock"),S.ActionClock);
    O->SetStringField(TEXT("equipment_stage"),S.ThrowKind.IsEmpty()?TEXT("Ready"):S.ThrowStage);
    O->SetObjectField(TEXT("body_world"),SleeveTransform(P->GetMesh()->GetComponentTransform()));
    if(S.EquipmentPoseSource.IsValid())O->SetArrayField(TEXT("native_equipment_component"),SleeveTransforms(S.EquipmentPoseSource->GetComponentSpaceTransforms()));
    if(CheckMode==TEXT("pose"))Picture(*(FString(Label)+TEXT(".png")));
}
void FinishPose(UWorld* W,FEquipmentSession& S,bool Pass,const FString& Reason){
    auto O=MakeShared<FJsonObject>();if(SleeveReferences)O->SetObjectField(TEXT("references"),SleeveReferences);
    O->SetArrayField(TEXT("poses"),SleeveSamples);O->SetArrayField(TEXT("held_frames"),HandSamples);
    O->SetNumberField(TEXT("native_coherent_frames"),PoseComparedFrames);O->SetNumberField(TEXT("max_native_local_rotation_error_degrees"),PoseMaxNativeChainAngle);
    O->SetNumberField(TEXT("max_native_local_translation_error_cm"),PoseMaxNativeTranslation);O->SetNumberField(TEXT("max_arm_length_drift_cm"),HandMaxLengthDrift);
    O->SetBoolField(TEXT("fixed_step"),FApp::UseFixedTimeStep());O->SetBoolField(TEXT("pictures"),CheckMode==TEXT("pose"));
    FFileHelper::SaveStringToFile(JsonText(O),*(CheckOut/TEXT("POSES.json")),FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
    FinishCheck(W,Pass,Reason);
}
void GrenadePoseCheck(UWorld* W,AParisBridgeMission* M,FEquipmentSession& S,AParisBridgePlayerController* PC,ACharacter* P,float DT){
    CheckClock+=DT;
    if(CheckStep==0){if(M->Phase!=TEXT("Ready")||!Flag(Display(W,P),TEXT("Initialized")))return;M->StartMission();HoldBrains(W);PC->SetControlRotation(FRotator(0,0,0));CheckStep=1;CheckClock=0;return;}
    PoseTrace(W,S,P);if(CheckFinished)return;
    auto Settled=[&](){return Num(Display(W,P),TEXT("SourceTransitionAlpha"))>.9999;};
    if(CheckStep==1&&CheckClock>.4){PosePicture(W,S,P,TEXT("01_rifle_before"));CheckStep=2;CheckClock=0;}
    else if(CheckStep==2&&CheckClock>.3&&!FScreenshotRequest::IsScreenshotRequested()){WheelInput(PC,true);CheckStep=3;CheckClock=0;PoseShotIndex=0;}
    else if(CheckStep==3){const double Times[]={.03,.09,.22,.39,.79};const TCHAR* Labels[]={TEXT("02_frag_switch_first"),TEXT("03_frag_switch_010"),TEXT("04_frag_switch_023"),TEXT("05_frag_switch_040"),TEXT("06_frag_ready_level")};
        if(PoseShotIndex<5&&CheckClock>=Times[PoseShotIndex]&&!FScreenshotRequest::IsScreenshotRequested()){PosePicture(W,S,P,Labels[PoseShotIndex++]);}
        if(PoseShotIndex==5&&CheckClock>1&&!FScreenshotRequest::IsScreenshotRequested()){PC->SetControlRotation(FRotator(20,0,0));CheckStep=4;CheckClock=0;}}
    else if(CheckStep==4&&CheckClock>.5){PosePicture(W,S,P,TEXT("07_frag_ready_up20"));CheckStep=5;CheckClock=0;}
    else if(CheckStep==5&&CheckClock>.3&&!FScreenshotRequest::IsScreenshotRequested()){PC->SetControlRotation(FRotator(-20,0,0));CheckStep=6;CheckClock=0;}
    else if(CheckStep==6&&CheckClock>.5){PosePicture(W,S,P,TEXT("08_frag_ready_down20"));CheckStep=7;CheckClock=0;}
    else if(CheckStep==7&&CheckClock>.3&&!FScreenshotRequest::IsScreenshotRequested()){PC->SetControlRotation(FRotator(0,0,0));PrimaryInput(PC,true);CheckStep=8;CheckClock=0;PoseShotIndex=0;}
    else if(CheckStep==8){const double Times[]={.09,.29,.59,1.19};const TCHAR* Labels[]={TEXT("09_frag_start_010"),TEXT("10_frag_start_030"),TEXT("11_frag_start_060"),TEXT("12_frag_hold")};
        if(PoseShotIndex<4&&CheckClock>=Times[PoseShotIndex]&&!FScreenshotRequest::IsScreenshotRequested())PosePicture(W,S,P,Labels[PoseShotIndex++]);
        if(PoseShotIndex==4&&CheckClock>1.5&&!FScreenshotRequest::IsScreenshotRequested()){Tap(PC,EKeys::Escape);PrimaryInput(PC,false);CheckStep=9;CheckClock=0;}}
    else if(CheckStep==9&&CheckClock>1.6&&S.ThrowKind.IsEmpty()&&Settled()){PosePicture(W,S,P,TEXT("13_frag_cancel_return"));CheckStep=10;CheckClock=0;}
    else if(CheckStep==10&&CheckClock>.3&&!FScreenshotRequest::IsScreenshotRequested()){WheelInput(PC,false);CheckStep=11;CheckClock=0;}
    else if(CheckStep==11&&CheckClock>.8){if(S.SelectedSlot!=2){FinishPose(W,S,false,TEXT("smoke_not_selected"));return;}PosePicture(W,S,P,TEXT("14_smoke_ready_level"));CheckStep=12;CheckClock=0;}
    else if(CheckStep==12&&CheckClock>.3&&!FScreenshotRequest::IsScreenshotRequested()){PC->SetControlRotation(FRotator(20,0,0));CheckStep=13;CheckClock=0;}
    else if(CheckStep==13&&CheckClock>.5){PosePicture(W,S,P,TEXT("15_smoke_ready_up20"));CheckStep=14;CheckClock=0;}
    else if(CheckStep==14&&CheckClock>.3&&!FScreenshotRequest::IsScreenshotRequested()){PC->SetControlRotation(FRotator(-20,0,0));CheckStep=15;CheckClock=0;}
    else if(CheckStep==15&&CheckClock>.5){PosePicture(W,S,P,TEXT("16_smoke_ready_down20"));CheckStep=16;CheckClock=0;}
    else if(CheckStep==16&&CheckClock>.3&&!FScreenshotRequest::IsScreenshotRequested()){PC->SetControlRotation(FRotator(0,0,0));PrimaryInput(PC,true);CheckStep=17;CheckClock=0;PoseShotIndex=0;}
    else if(CheckStep==17){const double Times[]={.09,.29,.59,1.19};const TCHAR* Labels[]={TEXT("17_smoke_start_010"),TEXT("18_smoke_start_030"),TEXT("19_smoke_start_060"),TEXT("20_smoke_hold")};
        if(PoseShotIndex<4&&CheckClock>=Times[PoseShotIndex]&&!FScreenshotRequest::IsScreenshotRequested())PosePicture(W,S,P,Labels[PoseShotIndex++]);
        if(PoseShotIndex==4&&CheckClock>1.5&&!FScreenshotRequest::IsScreenshotRequested()){PrimaryInput(PC,false);CheckStep=18;CheckClock=0;PoseShotIndex=0;}}
    else if(CheckStep==18){const double Times[]={.09,.29,.39,.69};const TCHAR* Labels[]={TEXT("21_smoke_swing_010"),TEXT("22_smoke_swing_030"),TEXT("23_smoke_release_040"),TEXT("24_smoke_follow_070")};
        if(PoseShotIndex<4&&CheckClock>=Times[PoseShotIndex]&&!FScreenshotRequest::IsScreenshotRequested())PosePicture(W,S,P,Labels[PoseShotIndex++]);
        if(CheckClock>2.2&&S.ThrowKind.IsEmpty()&&Settled()){PosePicture(W,S,P,TEXT("25_final_rifle"));CheckStep=19;CheckClock=0;}}
    else if(CheckStep==19&&CheckClock>.4&&!FScreenshotRequest::IsScreenshotRequested()){
        const bool Pass=S.Frag==2&&S.FragThrown==0&&S.Smoke==1&&S.SmokeThrown==1&&Num(P,TEXT("ShotSequence"))==0&&Num(P,TEXT("LoadedAmmo"))==8&&Num(P,TEXT("ReserveAmmo"))==10&&HandMaxLengthDrift<.001&&PoseComparedFrames>100&&PoseMaxNativeChainAngle<.005&&PoseMaxNativeTranslation<.001;
        FinishPose(W,S,Pass,TEXT("Native torso/clavicle/twist/fingers retained; original-length left reach; switch/Ready/Start/Hold/Cancel/Far/return and +/-20 views captured. Visual review remains required."));}
    if(CheckClock>15)FinishPose(W,S,false,TEXT("pose_stage_timeout_")+FString::FromInt(CheckStep));
}
