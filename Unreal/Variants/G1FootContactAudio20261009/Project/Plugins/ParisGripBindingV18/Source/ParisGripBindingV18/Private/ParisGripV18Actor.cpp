#include "ParisGripV18Actor.h"
#include "Camera/CameraComponent.h"
#include "Components/PoseableMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"
#include "TwoBoneIK.h"
#include "UObject/UnrealType.h"

namespace
{
bool ReadArray(const TSharedPtr<FJsonObject>& Obj, const TCHAR* Key, int32 Size, TArray<double>& Out)
{
    const TArray<TSharedPtr<FJsonValue>>* Values = nullptr;
    if (!Obj.IsValid() || !Obj->TryGetArrayField(Key, Values) || Values->Num() != Size) return false;
    Out.Reset();
    for (const auto& Value : *Values)
    {
        double Number;
        if (!Value->TryGetNumber(Number) || !FMath::IsFinite(Number)) return false;
        Out.Add(Number);
    }
    return true;
}
bool ReadTransform(const TSharedPtr<FJsonObject>& Obj, FTransform& Out)
{
    TArray<double> T, Q, S;
    if (!ReadArray(Obj, TEXT("t"), 3, T) || !ReadArray(Obj, TEXT("q"), 4, Q) || !ReadArray(Obj, TEXT("s"), 3, S)) return false;
    FQuat Rotation(Q[0], Q[1], Q[2], Q[3]);
    if (FMath::Abs(Rotation.SizeSquared() - 1) > 1.e-3 || S[0] <= 0 || S[1] <= 0 || S[2] <= 0) return false;
    Rotation.Normalize();
    Out = FTransform(Rotation, FVector(T[0], T[1], T[2]), FVector(S[0], S[1], S[2]));
    return true;
}
}

AParisGripV18Actor::AParisGripV18Actor()
{
    PrimaryActorTick.bCanEverTick = true;
    PrimaryActorTick.TickGroup = TG_PostUpdateWork;
    Pose = CreateDefaultSubobject<UPoseableMeshComponent>(TEXT("AcceptedPoseDisplay"));
    SetRootComponent(Pose);
    Pose->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Pose->SetOnlyOwnerSee(true);
    Pose->SetCastShadow(false);
    Pose->SetForcedLOD(1);
    Gun = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("AcceptedGunDisplay"));
    Gun->SetupAttachment(Pose, TEXT("hand_r"));
    Gun->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Gun->SetOnlyOwnerSee(true);
    Gun->SetCastShadow(false);
}

bool AParisGripV18Actor::BindExistingPose(AActor* InCombatant, USkeletalMeshComponent* InSource,
    UCameraComponent* InCamera, AActor* OriginalVisibleGun, USkeletalMesh* DisplayMesh,
    UStaticMesh* GunMesh, UParisGripV18Config* Config)
{
    auto Fail = [this](const TCHAR* Reason) { BindingError = Reason; return false; };
    if (Initialized) return Fail(TEXT("One-time binding already initialized"));
    if (!IsValid(InCombatant) || !IsValid(InSource) || !IsValid(InCamera) || !IsValid(OriginalVisibleGun)
        || !DisplayMesh || !GunMesh || !Config || !InSource->GetSkeletalMeshAsset()) return Fail(TEXT("Missing binding input"));
    if (!FindFProperty<FNameProperty>(InCombatant->GetClass(), TEXT("ActionState"))
        || !FindFProperty<FBoolProperty>(InCombatant->GetClass(), TEXT("IsDead"))) return Fail(TEXT("Authoritative action/lifecycle fields absent"));
    TSharedPtr<FJsonObject> Json;
    if (!FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Config->BindingJson), Json) || !Json.IsValid()) return Fail(TEXT("Invalid binding JSON"));
    const TSharedPtr<FJsonObject>* GunJson = nullptr;
    const TSharedPtr<FJsonObject>* SupportJson = nullptr;
    const TSharedPtr<FJsonObject>* Fingers = nullptr;
    TArray<double> Pole;
    if (!Json->TryGetObjectField(TEXT("gun_hand_relative"), GunJson) || !ReadTransform(*GunJson, GunInHand)
        || !Json->TryGetObjectField(TEXT("support_hand_relative_to_right"), SupportJson) || !ReadTransform(*SupportJson, SupportInRight)
        || !Json->TryGetObjectField(TEXT("fingers_local"), Fingers)
        || !ReadArray(Json, TEXT("elbow_pole_relative_to_right_cm"), 3, Pole)) return Fail(TEXT("Binding transform fields absent/invalid"));
    PoleInRight = FVector(Pole[0], Pole[1], Pole[2]);
    const FReferenceSkeleton& Ref = DisplayMesh->GetRefSkeleton();
    const FReferenceSkeleton& SourceRef = InSource->GetSkeletalMeshAsset()->GetRefSkeleton();
    SourceIndices.Reset(); Parents.Reset(); HoldingRotations.Reset();
    for (int32 I = 0; I < Ref.GetNum(); ++I)
    {
        const int32 Index = SourceRef.FindBoneIndex(Ref.GetBoneName(I));
        if (Index == INDEX_NONE) return Fail(TEXT("Display/source bone mapping incomplete"));
        const int32 Parent = Ref.GetParentIndex(I);
        const int32 SourceParent = SourceRef.GetParentIndex(Index);
        if (Parent >= I || (Parent >= 0 && (SourceParent < 0 || Ref.GetBoneName(Parent) != SourceRef.GetBoneName(SourceParent)))) return Fail(TEXT("Bone hierarchy mismatch"));
        SourceIndices.Add(Index); Parents.Add(Parent);
    }
    for (const auto& Item : (*Fingers)->Values)
    {
        const int32 Index = Ref.FindBoneIndex(FName(*Item.Key));
        FTransform T;
        if (Index == INDEX_NONE || !ReadTransform(Item.Value->AsObject(), T)) return Fail(TEXT("Accepted finger transform invalid"));
        HoldingRotations.Add(Index, T.GetRotation());
        if (Item.Key == TEXT("pinky_02_r"))
        {
            PinkyDistal = Index;
            PinkyScale = T.GetScale3D().X;
            if (!T.GetScale3D().Equals(FVector(PinkyScale), 1.e-4) || FMath::Abs(PinkyScale - 0.9) > 1.e-4) return Fail(TEXT("Accepted distal scale mismatch"));
        }
    }
    HandR = Ref.FindBoneIndex(TEXT("hand_r")); HandL = Ref.FindBoneIndex(TEXT("hand_l"));
    UpperL = Ref.FindBoneIndex(TEXT("upperarm_l")); LowerL = Ref.FindBoneIndex(TEXT("lowerarm_l"));
    if (HoldingRotations.Num() != 30 || PinkyDistal < 0 || HandR < 0 || HandL < 0 || UpperL < 0 || LowerL < 0
        || Parents[HandL] != LowerL || Parents[LowerL] != UpperL) return Fail(TEXT("Required accepted grip/support chain absent"));
    Combatant = InCombatant; Source = InSource; SetOwner(InCombatant);
    Pose->SetSkinnedAssetAndUpdate(DisplayMesh);
    Gun->SetStaticMesh(GunMesh);
    Gun->AttachToComponent(Pose, FAttachmentTransformRules::SnapToTargetNotIncludingScale, TEXT("hand_r"));
    Gun->SetRelativeTransform(GunInHand);
    Local.SetNum(Ref.GetNum()); Component.SetNum(Ref.GetNum());
    AddTickPrerequisiteComponent(Source);
    Pose->AddTickPrerequisiteComponent(Source);
    if (!UpdateNativePose()) return false;
    const FTransform OriginalGunInCamera = OriginalVisibleGun->GetActorTransform().GetRelativeTransform(InCamera->GetComponentTransform());
    const FTransform GunInComponent = GunInHand * Component[HandR];
    CachedAssemblyFrame = GunInComponent.Inverse() * OriginalGunInCamera;
    AttachToComponent(InCamera, FAttachmentTransformRules::SnapToTargetNotIncludingScale);
    Pose->SetRelativeTransform(CachedAssemblyFrame);
    Initialized = true;
    return true;
}

void AParisGripV18Actor::RebuildComponents()
{
    for (int32 I = 0; I < Local.Num(); ++I)
        Component[I] = Parents[I] >= 0 ? Local[I] * Component[Parents[I]] : Local[I];
}

bool AParisGripV18Actor::UpdateNativePose()
{
    if (!IsValid(Source) || !IsValid(Combatant)) { BindingError = TEXT("Source/lifecycle object lost"); return false; }
    const TArray<FTransform>& SourceComponents = Source->GetComponentSpaceTransforms();
    const FReferenceSkeleton& Ref = Source->GetSkeletalMeshAsset()->GetRefSkeleton();
    if (SourceComponents.Num() != Ref.GetNum()) { BindingError = TEXT("Native source pose not ready"); return false; }
    for (int32 I = 0; I < SourceIndices.Num(); ++I)
    {
        const int32 Index = SourceIndices[I], Parent = Ref.GetParentIndex(Index);
        Local[I] = Parent >= 0 ? SourceComponents[Index].GetRelativeTransform(SourceComponents[Parent]) : SourceComponents[Index];
    }
    ObservedAction = FindFProperty<FNameProperty>(Combatant->GetClass(), TEXT("ActionState"))->GetPropertyValue_InContainer(Combatant);
    if (!AdaptSourceLocalPose(CastChecked<USkeletalMesh>(Pose->GetSkinnedAsset())->GetRefSkeleton(), Local, ObservedAction, NativeDeltaSeconds)) return false;
    const bool Holding = ObservedAction == TEXT("Ready");
    HoldingAppliedAlpha = FMath::Clamp(GetGripWeight(Holding), 0.f, 1.f);
    FingerRotationErrorDegrees = 0;
    if (HoldingAppliedAlpha > 0) for (const auto& Item : HoldingRotations)
        Local[Item.Key].SetRotation(HoldingAppliedAlpha >= 1 ? Item.Value : FQuat::Slerp(Local[Item.Key].GetRotation(), Item.Value, HoldingAppliedAlpha).GetNormalized());
    Local[PinkyDistal].SetScale3D(Local[PinkyDistal].GetScale3D() * PinkyScale);
    RebuildComponents();
    SupportErrorCm = 0; LimbLengthErrorCm = 0;
    if (HoldingAppliedAlpha > 0)
    {
        const FTransform Target = SupportInRight * Component[HandR];
        FTransform Upper = Component[UpperL], Lower = Component[LowerL], Hand = Component[HandL];
        const double UpperLength = FVector::Distance(Upper.GetLocation(), Lower.GetLocation());
        const double LowerLength = FVector::Distance(Lower.GetLocation(), Hand.GetLocation());
        AnimationCore::SolveTwoBoneIK(Upper, Lower, Hand, Component[HandR].TransformPosition(PoleInRight), Target.GetLocation(),
            UpperLength, LowerLength, false, 1.0, 1.0);
        Hand.SetRotation(Target.GetRotation());
        const FTransform SolvedUpper = Upper.GetRelativeTransform(Component[Parents[UpperL]]);
        const FTransform SolvedLower = Lower.GetRelativeTransform(Upper);
        const FTransform SolvedHand = Hand.GetRelativeTransform(Lower);
        if (HoldingAppliedAlpha >= 1)
        { Local[UpperL] = SolvedUpper; Local[LowerL] = SolvedLower; Local[HandL] = SolvedHand; }
        else
        {
            // Blend rotations in parent-local space, preserving source segment lengths.
            Local[UpperL].SetRotation(FQuat::Slerp(Local[UpperL].GetRotation(), SolvedUpper.GetRotation(), HoldingAppliedAlpha).GetNormalized());
            Local[LowerL].SetRotation(FQuat::Slerp(Local[LowerL].GetRotation(), SolvedLower.GetRotation(), HoldingAppliedAlpha).GetNormalized());
            Local[HandL].SetRotation(FQuat::Slerp(Local[HandL].GetRotation(), SolvedHand.GetRotation(), HoldingAppliedAlpha).GetNormalized());
        }
        RebuildComponents();
        SupportErrorCm = FVector::Distance(Component[HandL].GetLocation(), Target.GetLocation());
        LimbLengthErrorCm = FMath::Max(FMath::Abs(FVector::Distance(Component[UpperL].GetLocation(), Component[LowerL].GetLocation()) - UpperLength),
            FMath::Abs(FVector::Distance(Component[LowerL].GetLocation(), Component[HandL].GetLocation()) - LowerLength));
        for (const auto& Item : HoldingRotations)
            FingerRotationErrorDegrees = FMath::Max(FingerRotationErrorDegrees, FMath::RadiansToDegrees(Local[Item.Key].GetRotation().AngularDistance(Item.Value)));
    }
    Pose->BoneSpaceTransforms = Local;
    Pose->MarkRefreshTransformDirty();
    Pose->RefreshBoneTransforms(nullptr);
    const bool Dead = FindFProperty<FBoolProperty>(Combatant->GetClass(), TEXT("IsDead"))->GetPropertyValue_InContainer(Combatant);
    Pose->SetVisibility(!Dead, true);
    ++NativePoseUpdates;
    return true;
}

void AParisGripV18Actor::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    NativeDeltaSeconds = DeltaSeconds;
    if (Initialized && !UpdateNativePose()) { Initialized = false; Pose->SetVisibility(false, true); }
}
