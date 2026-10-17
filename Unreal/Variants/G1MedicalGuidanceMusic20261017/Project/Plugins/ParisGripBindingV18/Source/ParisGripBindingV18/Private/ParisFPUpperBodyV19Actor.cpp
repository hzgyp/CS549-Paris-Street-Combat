#include "ParisFPUpperBodyV19Actor.h"
#include "ParisSmokeGripContact.h"
#include "ParisFragGripContact.h"
#include "Animation/AnimSequence.h"
#include "TwoBoneIK.h"
#include "Components/PoseableMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Camera/PlayerCameraManager.h"
#include "GameFramework/PlayerController.h"
#include "Kismet/GameplayStatics.h"

#include "ParisReloadWorkspace.inl"
#include "ParisGrenadeWorkspace.inl"

AParisFPUpperBodyV19Actor::AParisFPUpperBodyV19Actor()
{
    HoldingSource = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("ExistingHoldingMotionSource"));
    HoldingSource->SetupAttachment(Pose);
    HoldingSource->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    HoldingSource->SetVisibility(false);
    HoldingSource->SetHiddenInGame(true);
    HoldingSource->SetCastShadow(false);
    HoldingSource->VisibilityBasedAnimTickOption = EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
    HoldingSource->SetForcedLOD(1);
}

void AParisFPUpperBodyV19Actor::SetEquipmentPoseSource(USkeletalMeshComponent* InSource,FName Label,double ExteriorHeightCm)
{
    if(EquipmentPoseSource.Get()!=InSource){
        if(EquipmentPoseSource.IsValid())RemoveTickPrerequisiteComponent(EquipmentPoseSource.Get());
        EquipmentPoseSource=InSource;EquipmentFrameCached=false;EquipmentReleaseFrameCached=false;
        if(InSource)AddTickPrerequisiteComponent(InSource);
    }
    if(EquipmentPoseLabel!=Label)EquipmentReleaseFrameCached=false;
    EquipmentPoseLabel=Label;EquipmentExteriorHeightCm=ExteriorHeightCm;
    if(!InSource){SmokeGripContactActive=false;FragGripContactActive=false;}
}

void AParisFPUpperBodyV19Actor::ApplySmokeGripContact(const FReferenceSkeleton& Ref,TArray<FTransform>& PoseLocal) const
{
    if(SmokeGripContactActive)ParisSmokeGripContact::Apply(Ref,PoseLocal);
}

void AParisFPUpperBodyV19Actor::ApplyFragGripContact(const FReferenceSkeleton& Ref,TArray<FTransform>& PoseLocal) const
{
    if(FragGripContactActive)ParisFragGripContact::Apply(Ref,PoseLocal);
}

bool AParisFPUpperBodyV19Actor::PrepareHoldingSource(USkeletalMesh* SourceMesh, UAnimSequence* ExistingHoldingClip)
{
    if (!SourceMesh || !ExistingHoldingClip || Initialized || !ExistingClipPath.IsEmpty()) return false;
    HoldingSource->SetSkeletalMesh(SourceMesh);
    HoldingSource->PlayAnimation(ExistingHoldingClip, true);
    ExistingClipPath = ExistingHoldingClip->GetPathName();
    AddTickPrerequisiteComponent(HoldingSource);
    return true;
}

bool AParisFPUpperBodyV19Actor::AdaptSourceLocalPose(const FReferenceSkeleton& DisplayRef,
    TArray<FTransform>& InOutLocal, FName Action, float DeltaSeconds)
{
    if (!HoldingSource->GetSkeletalMeshAsset() || ExistingClipPath.IsEmpty())
    { BindingError = TEXT("Existing holding source absent"); return false; }
    if(MedicalPoseSource.IsValid())return AdaptMedicalSourcePose(DisplayRef,InOutLocal,DeltaSeconds);
    auto* EquipmentSource=EquipmentPoseSource.Get();
    const bool Equipment=EquipmentSource&&SourceFrameCached;
    const bool WasEquipment=PreviousAction.ToString().StartsWith(TEXT("Grenade"));
    const bool EquipmentBoundary=Equipment!=WasEquipment;
    if(Equipment)Action=EquipmentPoseLabel;
    auto* MotionSource=Equipment?EquipmentSource:HoldingSource.Get();
    TArray<FTransform> Target = InOutLocal;
    if (Action == TEXT("Ready")||Equipment)
    {
        const auto& Ref = MotionSource->GetSkeletalMeshAsset()->GetRefSkeleton();
        const auto& Components = MotionSource->GetComponentSpaceTransforms();
        if (Components.Num() != Ref.GetNum())
        { BindingError = TEXT("Existing holding source pose not ready"); return false; }
        for (int32 I = 0; I < DisplayRef.GetNum(); ++I)
        {
            const int32 N = Ref.FindBoneIndex(DisplayRef.GetBoneName(I));
            if (N == INDEX_NONE) { BindingError = TEXT("Holding/display source mapping incomplete"); return false; }
            const int32 Parent = Ref.GetParentIndex(N);
            Target[I] = Parent >= 0 ? Components[N].GetRelativeTransform(Components[Parent]) : Components[N];
        }
    }
    if (!SourceFrameCached)
    {
        if (Action != TEXT("Ready")) { BindingError = TEXT("First source-space calibration requires Ready"); return false; }
        TArray<FTransform> BodyComponent, HoldComponent;
        BodyComponent.SetNum(Target.Num()); HoldComponent.SetNum(Target.Num());
        for (int32 I = 0; I < Target.Num(); ++I)
        {
            const int32 Parent = DisplayRef.GetParentIndex(I);
            BodyComponent[I] = Parent >= 0 ? InOutLocal[I] * BodyComponent[Parent] : InOutLocal[I];
            HoldComponent[I] = Parent >= 0 ? Target[I] * HoldComponent[Parent] : Target[I];
        }
        const int32 Hand = DisplayRef.FindBoneIndex(TEXT("hand_r"));
        if (Hand == INDEX_NONE) { BindingError = TEXT("Source-space hand landmark missing"); return false; }
        BodySourceToHolding = BodyComponent[Hand].Inverse() * HoldComponent[Hand];
        SourceFrameCached = true;
    }
    // Equipment already comes from a native motion component in the holding
    // source frame. BodySourceToHolding belongs only to gameplay-body poses.
    if (Action != TEXT("Ready") && !Equipment)
        for (int32 I = 0; I < Target.Num(); ++I)
            if (DisplayRef.GetParentIndex(I) == INDEX_NONE) Target[I] = Target[I] * BodySourceToHolding;
    if(Action==TEXT("Ready")&&!Equipment){
        ReadyWorkspace.SetNum(Target.Num());for(int32 I=0;I<Target.Num();++I){const int32 Parent=DisplayRef.GetParentIndex(I);ReadyWorkspace[I]=Parent>=0?Target[I]*ReadyWorkspace[Parent]:Target[I];}
    }
    if((Action==TEXT("Reloading")||Action==TEXT("Vaulting")||Action==TEXT("ProneEntering")||Action==TEXT("ProneExiting")||Action==TEXT("CrouchEntering")||Action==TEXT("CrouchExiting"))&&!Equipment&&!AdaptReloadWorkspace(DisplayRef,Target))return false;
    if(Equipment){
        const int32 Hand=DisplayRef.FindBoneIndex(TEXT("hand_l"));
        auto* Body=GetOwner()?GetOwner()->FindComponentByClass<USkeletalMeshComponent>():nullptr;
        auto* Camera=Pose->GetAttachParent();
        auto* PC=UGameplayStatics::GetPlayerController(this,0);
        if(Hand<0||!Body||!Camera||!PC||EquipmentExteriorHeightCm<=0){BindingError=TEXT("Equipment native body/camera frame absent");return false;}
        TArray<FTransform> EquipComponent;EquipComponent.SetNum(Target.Num());
        for(int32 I=0;I<Target.Num();++I){const int32 Parent=DisplayRef.GetParentIndex(I);EquipComponent[I]=Parent>=0?Target[I]*EquipComponent[Parent]:Target[I];}
        const FTransform CameraFrame=Camera->GetComponentTransform();
        if(!EquipmentFrameCached){
            const int32 UL=DisplayRef.FindBoneIndex(TEXT("upperarm_l")),UR=DisplayRef.FindBoneIndex(TEXT("upperarm_r")),Spine=DisplayRef.FindBoneIndex(TEXT("spine_03")),Pelvis=DisplayRef.FindBoneIndex(TEXT("pelvis"));
            if(UL<0||UR<0||Spine<0||Pelvis<0){BindingError=TEXT("Equipment anatomical frame absent");return false;}
            const FVector Right=(EquipComponent[UR].GetLocation()-EquipComponent[UL].GetLocation()).GetSafeNormal();
            const FVector Up=(EquipComponent[Spine].GetLocation()-EquipComponent[Pelvis].GetLocation()).GetSafeNormal();
            const FQuat NativeFrame=FRotationMatrix::MakeFromYZ(Right,Up).ToQuat();
            EquipmentPresentationFrame=FTransform(NativeFrame.Inverse());
            const double SpineHeight=CameraFrame.InverseTransformPosition(Body->GetComponentTransform().TransformPosition(EquipComponent[Spine].GetLocation())).Z;
            // Compensate the original camera's 25cm forward placement without
            // moving the live camera/body or raising shoulders with the hand.
            EquipmentPresentationFrame.SetTranslation(FVector(-5,0,SpineHeight)-EquipmentPresentationFrame.TransformVectorNoScale(EquipComponent[Spine].GetLocation()));
            EquipmentRootOffset=EquipComponent[Hand].GetLocation();
            EquipmentEntryHandCamera=CameraFrame.InverseTransformPosition(Pose->GetSocketLocation(TEXT("hand_l")));
            EquipmentEntryElapsed=0;
            EquipmentFrameCached=true;
        }
        if(Action==TEXT("GrenadeRelease")){
            EquipmentEntryElapsed=FMath::Min(.25f,EquipmentEntryElapsed+FMath::Max(0.f,DeltaSeconds));
            if(!EquipmentReleaseFrameCached){
                const int32 Spine=DisplayRef.FindBoneIndex(TEXT("spine_03"));
                if(Spine<0){BindingError=TEXT("Equipment release spine frame absent");return false;}
                // Use the actual mesh-to-view basis, not the asymmetric Loop
                // shoulder line. Keep the existing spine placement at entry.
                const FQuat MeshToCamera=(CameraFrame.GetRotation().Inverse()*Body->GetComponentQuat()).GetNormalized();
                EquipmentReleasePresentationFrame=FTransform(MeshToCamera);
                const FVector SpineNative=EquipComponent[Spine].GetLocation();
                const FVector SpineCamera=EquipmentPresentationFrame.TransformPosition(SpineNative);
                EquipmentReleasePresentationFrame.SetTranslation(SpineCamera-MeshToCamera.RotateVector(SpineNative));
                EquipmentReleaseFrameCached=true;
            }
            const FTransform ReleaseBodyFrame=EquipmentReleasePresentationFrame*CameraFrame.GetRelativeTransform(Pose->GetComponentTransform());
            for(int32 I=0;I<Target.Num();++I)if(DisplayRef.GetParentIndex(I)==INDEX_NONE)Target[I]=Target[I]*ReleaseBodyFrame;
            // The unmodified native arm supplies a reachable wrist. Adding
            // Loop displacement to the front-held wrist saturated reach and
            // flattened the overarm arc; no extra wrist IK runs in Release.
        }else{
        int32 Width,Height;PC->GetViewportSize(Width,Height);
        if(Width<=0||Height<=0){BindingError=TEXT("Equipment viewport absent");return false;}
        const double TanH=FMath::Tan(FMath::DegreesToRadians(PC->PlayerCameraManager->GetFOVAngle()*.5)),TanV=TanH*Height/Width;
        // Keep the hand inside its actual reach instead of using the longest
        // prop dimension to push the wrist past a fully extended arm.
        const double Depth=35.;
        const FVector Motion=EquipmentPresentationFrame.TransformVectorNoScale(EquipComponent[Hand].GetLocation()-EquipmentRootOffset);
        EquipmentEntryElapsed=FMath::Min(.25f,EquipmentEntryElapsed+FMath::Max(0.f,DeltaSeconds));
        const FVector CameraGoal=FVector(Depth,Depth*TanH*(2*.32-1),Depth*TanV*(1-2*.70))+Motion;
        const FVector Desired=CameraFrame.TransformPosition(FMath::Lerp(EquipmentEntryHandCamera,CameraGoal,double(EquipmentEntryElapsed/.25f)));
        const FTransform NativeBodyFrame=EquipmentPresentationFrame*CameraFrame.GetRelativeTransform(Pose->GetComponentTransform());
        for(int32 I=0;I<Target.Num();++I)if(DisplayRef.GetParentIndex(I)==INDEX_NONE)Target[I]=Target[I]*NativeBodyFrame;
        if(!GrenadeReach(DisplayRef,Target,Pose->GetComponentTransform().InverseTransformPosition(Desired))){BindingError=TEXT("Equipment native left reach absent");return false;}
        }
    }
    // Preserve the complete native grenade chain, including clavicles and
    // forearm twist bones. Rifle shoulder anchoring distorts this source pose.
    if (PreviousSourcePose.IsEmpty()) PreviousAction = Action;
    else if (PreviousAction != Action)
    {
        TransitionFrom = PreviousSourcePose;
        TransitionFromGrip = ExistingGripWeight;
        TransitionElapsed = 0;
        PreviousAction = Action;
    }
    // Rifle and grenade have different complete display frames. Blending their
    // root/clavicle transforms sweeps the sleeve through the camera near plane.
    // Frame boundaries switch coherently; the entry hand reach still eases for
    // 0.25s. Same-frame native action and original rifle transitions keep blending.
    if(EquipmentBoundary){TransitionFrom.Reset();TransitionFromGrip=Equipment?0.f:1.f;}
    TransitionElapsed = FMath::Min(.25f, TransitionElapsed + FMath::Max(0.f, DeltaSeconds));
    SourceTransitionAlpha = TransitionElapsed / .25f;
    const float TargetGrip = Action == TEXT("Ready") ? 1.f : 0.f;
    ExistingGripWeight = FMath::Lerp(TransitionFromGrip, TargetGrip, SourceTransitionAlpha);
    // Ease only the held-to-native Release handoff; the original quarter-
    // second duration and native animation/gameplay clocks remain unchanged.
    const float PoseBlendAlpha=Equipment&&Action==TEXT("GrenadeRelease")?SourceTransitionAlpha*SourceTransitionAlpha*(3.f-2.f*SourceTransitionAlpha):SourceTransitionAlpha;
    if (TransitionFrom.Num() == Target.Num() && SourceTransitionAlpha < 1)
        for (int32 I = 0; I < Target.Num(); ++I) InOutLocal[I].Blend(TransitionFrom[I], Target[I], PoseBlendAlpha);
    else InOutLocal = Target;
    PreviousSourcePose = InOutLocal;
    if(Equipment){ApplySmokeGripContact(DisplayRef,InOutLocal);ApplyFragGripContact(DisplayRef,InOutLocal);}
    // Shape correction is coupled to the existing prop-specific pose gate.
    // The original mesh basis and rifle/native release remain exactly zero.
    Pose->ActiveMorphTargets.Reset();Pose->MorphTargetWeights.Init(0.f,2);
    const bool ThumbActive[2]={Equipment&&FragGripContactActive,Equipment&&SmokeGripContactActive};
    const FName ThumbNames[2]={TEXT("ThumbWeb_Frag"),TEXT("ThumbWeb_Smoke")};
    for(int32 I=0;I<2;++I)if(ThumbActive[I]){
        auto* Morph=Pose->FindMorphTarget(ThumbNames[I]);
        if(!Morph){BindingError=TEXT("Selected thumb corrective missing");return false;}
        Pose->ActiveMorphTargets.Add(Morph,I);Pose->MorphTargetWeights[I]=1.f;
    }
    if(FParse::Param(FCommandLine::Get(),TEXT("ParisThumbProbe"))){
        const int32 Mask=(ThumbActive[0]?1:0)|(ThumbActive[1]?2:0);
        if(ThumbProbeMask!=Mask){UE_LOG(LogTemp,Display,TEXT("PARIS_THUMB_CORRECTIVE mask=%d action=%s mesh=%s"),Mask,*Action.ToString(),*Pose->GetSkinnedAsset()->GetPathName());ThumbProbeMask=Mask;}
    }
    return true;
}

void AParisFPUpperBodyV19Actor::SetMedicalPoseSource(USkeletalMeshComponent* MedicalSource)
{
    if(MedicalPoseSource.Get()==MedicalSource)return;
    if(MedicalPoseSource.IsValid())RemoveTickPrerequisiteComponent(MedicalPoseSource.Get());
    MedicalPoseSource=MedicalSource;MedicalFrameCached=false;
    if(MedicalSource)AddTickPrerequisiteComponent(MedicalSource);
}

bool AParisFPUpperBodyV19Actor::AdaptMedicalSourcePose(const FReferenceSkeleton& Ref,TArray<FTransform>& MedicalLocal,float DeltaSeconds)
{
    auto* MedicalSource=MedicalPoseSource.Get();
    if(!MedicalSource||!MedicalSource->GetSkeletalMeshAsset()||!SourceFrameCached||ReadyWorkspace.Num()!=Ref.GetNum())
    {BindingError=TEXT("Medical native source/accepted workspace absent");return false;}
    const auto& R=MedicalSource->GetSkeletalMeshAsset()->GetRefSkeleton();
    const auto& C=MedicalSource->GetComponentSpaceTransforms();
    if(C.Num()!=R.GetNum()){BindingError=TEXT("Medical source pose not ready");return false;}
    TArray<FTransform> Target;Target.SetNum(Ref.GetNum());
    for(int32 I=0;I<Ref.GetNum();++I){
        const int32 N=R.FindBoneIndex(Ref.GetBoneName(I));
        if(N<0){BindingError=TEXT("Medical display mapping incomplete");return false;}
        const int32 Parent=R.GetParentIndex(N);
        Target[I]=Parent>=0?C[N].GetRelativeTransform(C[Parent]):C[N];
    }
    if(!MedicalFrameCached){
        const int32 HL=R.FindBoneIndex(TEXT("hand_l")),HR=R.FindBoneIndex(TEXT("hand_r"));
        auto* Camera=Pose->GetAttachParent();
        auto* Body=GetOwner()?GetOwner()->FindComponentByClass<USkeletalMeshComponent>():nullptr;
        if(HL<0||HR<0||!Camera||!Body){BindingError=TEXT("Medical native camera/body frame absent");return false;}
        // Preserve the real mesh-to-view basis used by the native release.
        // A posed shoulder line is asymmetric (OG004), so it cannot define yaw.
        // One rigid transform preserves all native bimanual chain/contact;
        // no hand IK, finger edits, bone scaling or animation edits are applied.
        const FTransform CameraFrame=Camera->GetComponentTransform();
        // Rigid medical framing measured from v7 camera-space landmarks.
        const FQuat ToCamera=(FRotator(65,0,0).Quaternion()*(CameraFrame.GetRotation().Inverse()*Body->GetComponentQuat())).GetNormalized();
        const FVector Hands=(C[HL].GetLocation()+C[HR].GetLocation())*.5;
        FTransform Presentation(ToCamera,FVector(50,-8,-35)-ToCamera.RotateVector(Hands));
        MedicalViewFrame=Presentation*CameraFrame.GetRelativeTransform(Pose->GetComponentTransform());
        MedicalViewFrame.SetScale3D(FVector::OneVector);
        MedicalFrameCached=true;
    }
    for(int32 I=0;I<Ref.GetNum();++I)if(Ref.GetParentIndex(I)<0)Target[I]=Target[I]*MedicalViewFrame;
    const FName Label(TEXT("MedicalTreating"));
    if(PreviousAction!=Label){TransitionFrom=PreviousSourcePose;TransitionElapsed=0;PreviousAction=Label;}
    TransitionElapsed=FMath::Min(.25f,TransitionElapsed+FMath::Max(0.f,DeltaSeconds));
    SourceTransitionAlpha=TransitionElapsed/.25f;ExistingGripWeight=0;
    if(TransitionFrom.Num()==Target.Num()&&SourceTransitionAlpha<1)
        for(int32 I=0;I<Target.Num();++I)MedicalLocal[I].Blend(TransitionFrom[I],Target[I],SourceTransitionAlpha);
    else MedicalLocal=Target;
    PreviousSourcePose=MedicalLocal;
    Pose->ActiveMorphTargets.Reset();Pose->MorphTargetWeights.Init(0.f,2);
    return true;
}
