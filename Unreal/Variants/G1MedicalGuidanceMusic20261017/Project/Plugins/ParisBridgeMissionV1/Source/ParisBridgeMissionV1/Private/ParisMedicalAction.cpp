// Existing native bandaging motion, isolated from gameplay and grenade presentation.
#include "ParisMedicalAction.h"
#include "ParisBridgeMission.h"
#include "ParisCrouchTransition.h"
#include "ParisProneTransition.h"
#include "ParisTraversal.h"
#include "ParisFirstPersonApprovedActor.h"
#include "Animation/AnimSequence.h"
#include "Animation/AnimSingleNodeInstance.h"
#include "Animation/Skeleton.h"
#include "Components/PoseableMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/Controller.h"
#include "UObject/UnrealType.h"

namespace ParisMedicalAction {
namespace {
const TCHAR* ClipPath = TEXT("/Game/ParisCombat/Animations/Medical20261017/AS_PC_HealBandages.AS_PC_HealBandages");
struct FState {
    TWeakObjectPtr<ACharacter> Player;
    TWeakObjectPtr<AController> Controller;
    TWeakObjectPtr<AParisFirstPersonApprovedActor> Display;
    TWeakObjectPtr<USkeletalMeshComponent> Motion;
    TWeakObjectPtr<USkeletalMesh> BodyMesh;
    TWeakObjectPtr<USkeletalMesh> DisplayMesh;
    TWeakObjectPtr<UAnimSequence> Clip;
    FString Generation;
    double Restore = -1, Posture = -1, Duration = 0, Elapsed = 0;
    bool RifleWasVisible = false;
};
TMap<TWeakObjectPtr<ACharacter>, FState> States;

double Number(const UObject* O, const TCHAR* Key) {
    const auto* F = O ? FindFProperty<FNumericProperty>(O->GetClass(), Key) : nullptr;
    if (!F) return -1;
    const void* V = F->ContainerPtrToValuePtr<void>(O);
    return F->IsFloatingPoint() ? F->GetFloatingPointPropertyValue(V) : F->GetSignedIntPropertyValue(V);
}
bool Context(ACharacter* P) {
    if (!IsValid(P) || !P->IsLocallyControlled() || !P->GetWorld() || P->GetWorld()->IsPaused()) return false;
    const auto* Dead = FindFProperty<FBoolProperty>(P->GetClass(), TEXT("IsDead"));
    const auto* Action = FindFProperty<FNameProperty>(P->GetClass(), TEXT("ActionState"));
    const auto* Restore = FindFProperty<FNumericProperty>(P->GetClass(), TEXT("RestoreGeneration"));
    const auto* Posture = FindFProperty<FNumericProperty>(P->GetClass(), TEXT("DesiredPosture"));
    const double Health = Number(P, TEXT("Health"));
    return Restore && Posture && Dead && !Dead->GetPropertyValue_InContainer(P) && FMath::IsFinite(Health) && Health > 0 &&
        Action && Action->GetPropertyValue_InContainer(P) == TEXT("Ready") && P->GetCharacterMovement() &&
        P->GetCharacterMovement()->IsMovingOnGround() && P->GetVelocity().Size() <= 2 &&
        !ParisCrouchTransition::Active(P) && !ParisProneTransition::Active(P) && !ParisTraversal::Active(P);
}
AParisFirstPersonApprovedActor* Display(ACharacter* P) {
    AParisFirstPersonApprovedActor* Found = nullptr;
    for (TActorIterator<AParisFirstPersonApprovedActor> It(P->GetWorld()); It; ++It) {
        if (It->GetOwner() != P || !It->Initialized) continue;
        if (Found) return nullptr; // Ambiguous presentation ownership fails closed.
        Found = *It;
    }
    return Found;
}
bool Mapping(USkeletalMesh* Body, USkeletalMesh* Visible) {
    if (!Body || !Visible) return false;
    const auto& Source = Body->GetRefSkeleton();
    const auto& Target = Visible->GetRefSkeleton();
    for (int32 I = 0; I < Target.GetNum(); ++I) {
        const int32 N = Source.FindBoneIndex(Target.GetBoneName(I));
        if (N < 0) return false;
        const int32 SP = Source.GetParentIndex(N), TP = Target.GetParentIndex(I);
        if ((SP < 0) != (TP < 0) || (SP >= 0 && Source.GetBoneName(SP) != Target.GetBoneName(TP))) return false;
    }
    for (const TCHAR* Landmark : {TEXT("spine_03"), TEXT("clavicle_l"), TEXT("clavicle_r"), TEXT("hand_l"), TEXT("hand_r")})
        if (Target.FindBoneIndex(Landmark) < 0) return false;
    return true;
}
UAnimSequence* NativeClip(ACharacter* P, AParisFirstPersonApprovedActor* D) {
    auto* Body = P->GetMesh() ? P->GetMesh()->GetSkeletalMeshAsset() : nullptr;
    auto* Visible = D && D->Pose ? Cast<USkeletalMesh>(D->Pose->GetSkinnedAsset()) : nullptr;
    if (!Mapping(Body, Visible)) return nullptr;
    auto* Clip = LoadObject<UAnimSequence>(nullptr, ClipPath);
    if (!Clip || !Clip->GetSkeleton() || !Clip->GetSkeleton()->IsCompatibleMesh(Body) ||
        !Clip->GetSkeleton()->IsCompatibleMesh(Visible) || Clip->HasRootMotion() ||
        !FMath::IsFinite(Clip->GetPlayLength()) || Clip->GetPlayLength() < .1 || Clip->GetPlayLength() > 30) return nullptr;
    return Clip;
}
bool SameLifecycle(const FState& S) {
    auto* P = S.Player.Get();
    auto* M = P ? AParisBridgeMission::Find(P->GetWorld()) : nullptr;
    return Context(P) && M && M->RunGeneration == S.Generation && P->GetController() == S.Controller.Get() &&
        Number(P, TEXT("RestoreGeneration")) == S.Restore && Number(P, TEXT("DesiredPosture")) == S.Posture &&
        P->GetMesh() && P->GetMesh()->GetSkeletalMeshAsset() == S.BodyMesh.Get() && S.Display.IsValid() && S.Display->Initialized &&
        S.Display->GetOwner() == P && S.Motion.IsValid() && S.Clip.IsValid() &&
        S.Display->Pose && S.Display->Pose->GetSkinnedAsset() == S.DisplayMesh.Get() && !S.Display->HasEquipmentPoseSource() &&
        S.Display->MedicalPoseUses(S.Motion.Get());
}
bool Sample(FState& S, double Age) {
    auto* Motion = S.Motion.Get();
    auto* Clip = S.Clip.Get();
    auto* Single = Motion ? Motion->GetSingleNodeInstance() : nullptr;
    if (!Single || !Clip || Single->GetCurrentAsset() != Clip) return false;
    Single->SetPlaying(false);
    Single->SetPosition(FMath::Clamp(Age / S.Duration, 0., 1.) * Clip->GetPlayLength(), false);
    Motion->UpdateComponentToWorld();
    Motion->TickAnimation(0, false);
    Motion->RefreshBoneTransforms();
    const auto& Bones = Motion->GetComponentSpaceTransforms();
    if (!Motion->GetSkeletalMeshAsset() || Bones.Num() != Motion->GetSkeletalMeshAsset()->GetRefSkeleton().GetNum()) return false;
    for (const FTransform& T : Bones) if (T.ContainsNaN()) return false;
    return true;
}
void Dispose(FState& S) {
    if (auto* D = S.Display.Get(); D && D->MedicalPoseUses(S.Motion.Get())) {
        D->SetMedicalPoseSource(nullptr);
        // Never reveal a rifle over a death/replacement action. Its normal owner wins.
        auto* P = S.Player.Get();
        const auto* Dead = P ? FindFProperty<FBoolProperty>(P->GetClass(), TEXT("IsDead")) : nullptr;
        if (P && Dead && !Dead->GetPropertyValue_InContainer(P) && Number(P, TEXT("Health")) > 0 && !D->HasEquipmentPoseSource())
            D->SetUnifiedRifleVisible(S.RifleWasVisible);
        D->RefreshUnifiedPresentation();
    }
    if (S.Motion.IsValid()) S.Motion->DestroyComponent();
}
void Prune() {
    for (auto It = States.CreateIterator(); It; ++It)
        if (!It.Key().IsValid()) { Dispose(It.Value()); It.RemoveCurrent(); }
}
}

bool Ready(ACharacter* P) {
    Prune();
    if (const auto* S = States.Find(P)) return SameLifecycle(*S);
    if (!Context(P) || !AParisBridgeMission::Find(P->GetWorld())) return false;
    auto* D = Display(P);
    return D && D->CanPresentMedicalPose() && NativeClip(P, D);
}
bool Begin(ACharacter* P, double Seconds) {
    if (!FMath::IsFinite(Seconds) || Seconds < .1 || Seconds > 30 || States.Contains(P) || !Ready(P)) return false;
    auto* D = Display(P);
    auto* Clip = NativeClip(P, D);
    if (!Clip || !D || !D->Gun) return false;
    FState S;
    S.Player = P; S.Controller = P->GetController(); S.Display = D; S.Clip = Clip;
    S.BodyMesh = P->GetMesh()->GetSkeletalMeshAsset(); S.Duration = Seconds;
    S.DisplayMesh = Cast<USkeletalMesh>(D->Pose->GetSkinnedAsset());
    S.Generation = AParisBridgeMission::Find(P->GetWorld())->RunGeneration;
    S.Restore = Number(P, TEXT("RestoreGeneration")); S.Posture = Number(P, TEXT("DesiredPosture"));
    S.RifleWasVisible = D->Gun->IsVisible();
    auto* Motion = NewObject<USkeletalMeshComponent>(P);
    P->AddInstanceComponent(Motion);
    Motion->SetupAttachment(P->GetMesh());
    Motion->SetSkeletalMesh(S.BodyMesh.Get());
    Motion->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Motion->SetCanEverAffectNavigation(false);
    Motion->SetHiddenInGame(true); Motion->SetVisibility(false); Motion->SetCastShadow(false);
    Motion->VisibilityBasedAnimTickOption = EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
    Motion->RegisterComponent();
    Motion->PlayAnimation(Clip, false);
    Motion->SetComponentTickEnabled(false);
    S.Motion = Motion;
    if (!Sample(S, 0)) { Dispose(S); return false; }
    D->SetMedicalPoseSource(Motion);
    D->SetUnifiedRifleVisible(false);
    States.Add(P, S);
    D->RefreshUnifiedPresentation();
    UE_LOG(LogTemp, Display, TEXT("PARIS_MEDICAL_ACTION begin clip=%s native_duration=%.6f treatment_duration=%.6f"), *Clip->GetPathName(), Clip->GetPlayLength(), Seconds);
    return true;
}
bool Tick(ACharacter* P, double Elapsed, double Seconds) {
    auto* S = States.Find(P);
    if (!S) return false;
    if (!FMath::IsFinite(Elapsed) || !FMath::IsFinite(Seconds) || !FMath::IsNearlyEqual(Seconds, S->Duration, .0001) ||
        Elapsed < S->Elapsed || !SameLifecycle(*S) || !Sample(*S, Elapsed)) {
        End(P);
        return false;
    }
    S->Elapsed = Elapsed;
    S->Display->SetUnifiedRifleVisible(false);
    S->Display->RefreshUnifiedPresentation();
    return true;
}
void End(ACharacter* P) {
    if (auto* S = States.Find(P)) {
        FState Old = *S;
        States.Remove(P); // Repeated/reentrant End cannot own the same component twice.
        Dispose(Old);
    }
    Prune();
}
void Shutdown() {
    for (auto& Entry : States) Dispose(Entry.Value);
    States.Empty();
}
}
