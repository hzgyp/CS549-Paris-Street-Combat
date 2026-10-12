#include "ParisFPUpperBodyV19Actor.h"
#include "Animation/AnimSequence.h"
#include "Components/PoseableMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Camera/PlayerCameraManager.h"
#include "GameFramework/PlayerController.h"
#include "Kismet/GameplayStatics.h"

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
        EquipmentPoseSource=InSource;EquipmentFrameCached=false;
        if(InSource)AddTickPrerequisiteComponent(InSource);
    }
    EquipmentPoseLabel=Label;EquipmentExteriorHeightCm=ExteriorHeightCm;
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
    auto* EquipmentSource=EquipmentPoseSource.Get();
    const bool Equipment=EquipmentSource&&SourceFrameCached;
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
    if (Action != TEXT("Ready"))
        for (int32 I = 0; I < Target.Num(); ++I)
            if (DisplayRef.GetParentIndex(I) == INDEX_NONE) Target[I] = Target[I] * BodySourceToHolding;
    if(Equipment){
        if(!EquipmentFrameCached){
            TArray<FTransform> EquipComponent;EquipComponent.SetNum(Target.Num());
            for(int32 I=0;I<Target.Num();++I){const int32 Parent=DisplayRef.GetParentIndex(I);EquipComponent[I]=Parent>=0?Target[I]*EquipComponent[Parent]:Target[I];}
            const int32 Hand=DisplayRef.FindBoneIndex(TEXT("hand_r"));
            const int32 HoldingHand=HoldingSource->GetSkeletalMeshAsset()->GetRefSkeleton().FindBoneIndex(TEXT("hand_r"));
            if(Hand==INDEX_NONE||HoldingHand==INDEX_NONE){BindingError=TEXT("Equipment hand frame absent");return false;}
            auto* PC=UGameplayStatics::GetPlayerController(this,0);if(!PC||EquipmentExteriorHeightCm<=0){BindingError=TEXT("Equipment view contract absent");return false;}
            FVector Eye;FRotator View;PC->GetPlayerViewPoint(Eye,View);int32 Width,Height;PC->GetViewportSize(Width,Height);
            if(Width<=0||Height<=0){BindingError=TEXT("Equipment viewport absent");return false;}
            const double TanH=FMath::Tan(FMath::DegreesToRadians(PC->PlayerCameraManager->GetFOVAngle()*.5)),TanV=TanH*Height/Width;
            const double Depth=EquipmentExteriorHeightCm/(2*TanV*.24);
            const FVector Desired=Eye+View.Vector()*Depth+FRotationMatrix(View).GetUnitAxis(EAxis::Y)*(Depth*TanH*(2*.68-1))+FRotationMatrix(View).GetUnitAxis(EAxis::Z)*(Depth*TanV*(1-2*.70));
            EquipmentRootOffset=Pose->GetComponentTransform().InverseTransformPosition(Desired)-EquipComponent[Hand].GetLocation();
            EquipmentFrameCached=true;
        }
        for(int32 I=0;I<Target.Num();++I)if(DisplayRef.GetParentIndex(I)==INDEX_NONE)Target[I].AddToTranslation(EquipmentRootOffset);
    }
    if (PreviousSourcePose.IsEmpty()) PreviousAction = Action;
    else if (PreviousAction != Action)
    {
        TransitionFrom = PreviousSourcePose;
        TransitionFromGrip = ExistingGripWeight;
        TransitionElapsed = 0;
        PreviousAction = Action;
    }
    TransitionElapsed = FMath::Min(.25f, TransitionElapsed + FMath::Max(0.f, DeltaSeconds));
    SourceTransitionAlpha = TransitionElapsed / .25f;
    const float TargetGrip = Action == TEXT("Ready") ? 1.f : 0.f;
    ExistingGripWeight = FMath::Lerp(TransitionFromGrip, TargetGrip, SourceTransitionAlpha);
    if (TransitionFrom.Num() == Target.Num() && SourceTransitionAlpha < 1)
        for (int32 I = 0; I < Target.Num(); ++I) InOutLocal[I].Blend(TransitionFrom[I], Target[I], SourceTransitionAlpha);
    else InOutLocal = Target;
    PreviousSourcePose = InOutLocal;
    return true;
}
