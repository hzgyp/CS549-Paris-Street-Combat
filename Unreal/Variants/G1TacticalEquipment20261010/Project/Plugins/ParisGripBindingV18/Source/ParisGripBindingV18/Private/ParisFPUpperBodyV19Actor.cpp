#include "ParisFPUpperBodyV19Actor.h"
#include "Animation/AnimSequence.h"
#include "Components/PoseableMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/SkeletalMesh.h"

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
    TArray<FTransform> Target = InOutLocal;
    if (Action == TEXT("Ready"))
    {
        const auto& Ref = HoldingSource->GetSkeletalMeshAsset()->GetRefSkeleton();
        const auto& Components = HoldingSource->GetComponentSpaceTransforms();
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
