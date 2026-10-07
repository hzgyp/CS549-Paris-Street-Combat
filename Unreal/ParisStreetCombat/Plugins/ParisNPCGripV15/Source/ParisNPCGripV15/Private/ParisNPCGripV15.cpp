#include "ParisNPCGripV15.h"
#include "Animation/AnimInstanceProxy.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "GameFramework/Character.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"
#include "UObject/UnrealType.h"
#include "Modules/ModuleManager.h"

// Action access is game-thread only; worker graph consumes a proxy-owned bool.
struct FParisNPCGripProxy : public FAnimInstanceProxy
{
    using FAnimInstanceProxy::FAnimInstanceProxy;
    bool Ready=true;
    virtual void PreUpdate(UAnimInstance* Instance,float Dt) override
    {
        FAnimInstanceProxy::PreUpdate(Instance,Dt);
        auto* Owner=Instance->GetOwningActor();
        const auto* P=Owner ? FindFProperty<FNameProperty>(Owner->GetClass(),TEXT("ActionState")):nullptr;
        Ready=P && P->GetPropertyValue_InContainer(Owner)==FName(TEXT("Ready"));
    }
};
FAnimInstanceProxy* UParisNPCGripAnimInstance::CreateAnimInstanceProxy(){return new FParisNPCGripProxy(this);}
void UParisNPCGripAnimInstance::DestroyAnimInstanceProxy(FAnimInstanceProxy* P){delete P;}

void FAnimNode_ParisNPCGrip::Initialize_AnyThread(const FAnimationInitializeContext& C){InputPose.Initialize(C);}
void FAnimNode_ParisNPCGrip::CacheBones_AnyThread(const FAnimationCacheBonesContext& C)
{
    InputPose.CacheBones(C);
    for(auto& R:Rules)R.Bone.Initialize(C.AnimInstanceProxy->GetRequiredBones());
}
void FAnimNode_ParisNPCGrip::Update_AnyThread(const FAnimationUpdateContext& C)
{
    InputPose.Update(C);
    const bool Ready=static_cast<FParisNPCGripProxy*>(C.AnimInstanceProxy)->Ready;
    HoldingAlpha=FMath::Clamp(HoldingAlpha+(Ready?1:-1)*C.GetDeltaTime()/.15f,0.f,1.f);
}
void FAnimNode_ParisNPCGrip::Evaluate_AnyThread(FPoseContext& Output)
{
    InputPose.Evaluate(Output);
    const auto& Bones=Output.Pose.GetBoneContainer();
    HasValidInput=Output.Pose.IsValid();
    TArray<FTransform> Before;
    for(auto I:Output.Pose.ForEachBoneIndex())Before.Add(Output.Pose[I]);
    TSet<int32> Modified;
    for(const auto& R:Rules)
    {
        if(!R.Bone.IsValidToEvaluate(Bones)){HasValidInput=false;continue;}
        const auto I=R.Bone.GetCompactPoseIndex(Bones);
        const FQuat Q=AcceptedHolding ? FQuat::Slerp(Output.Pose[I].GetRotation(),R.Accepted,HoldingAlpha).GetNormalized()
            :(R.Delta*Output.Pose[I].GetRotation()).GetNormalized();
        Output.Pose[I].SetRotation(Q);Modified.Add(I.GetInt());
        AdapterError=FMath::Max(AdapterError,FMath::RadiansToDegrees(Q.AngularDistance(Output.Pose[I].GetRotation())));
    }
    for(auto I:Output.Pose.ForEachBoneIndex())
    {
        const auto& A=Before[I.GetInt()];const auto& B=Output.Pose[I];
        TranslationError=FMath::Max(TranslationError,FVector::Distance(A.GetTranslation(),B.GetTranslation()));
        ScaleError=FMath::Max(ScaleError,FVector::Distance(A.GetScale3D(),B.GetScale3D()));
        if(!Modified.Contains(I.GetInt()))
        {
            const FQuat AQ=A.GetRotation(),BQ=B.GetRotation();
            // Audit unit-quaternion TEMPORARIES; never normalize actual pose.
            RawProtectedAngle=FMath::Max(RawProtectedAngle,FMath::RadiansToDegrees(AQ.AngularDistance(BQ)));
            SourceQuatNormError=FMath::Max(SourceQuatNormError,FMath::Abs(AQ.SizeSquared()-1.0));
            ProtectedQuatComponentError=FMath::Max(ProtectedQuatComponentError,
                FMath::Max(FMath::Max(FMath::Abs(AQ.X-BQ.X),FMath::Abs(AQ.Y-BQ.Y)),
                    FMath::Max(FMath::Abs(AQ.Z-BQ.Z),FMath::Abs(AQ.W-BQ.W))));
            ProtectedRotationError=FMath::Max(ProtectedRotationError,
                FMath::RadiansToDegrees(AQ.GetNormalized().AngularDistance(BQ.GetNormalized())));
        }
    }
}
void UParisNPCGripAnimInstance::NativePostEvaluateAnimation()
{
    Super::NativePostEvaluateAnimation();++Evaluations;
    for(TFieldIterator<FStructProperty> P(GetClass());P;++P)
        if(P->Struct==FAnimNode_ParisNPCGrip::StaticStruct())
        {
            const auto* N=P->ContainerPtrToValuePtr<FAnimNode_ParisNPCGrip>(this);
            ValidInput=N->HasValidInput;
            HoldingWeight=N->HoldingAlpha;
            ProtectedQuatComponentError=N->ProtectedQuatComponentError;
            SourceQuatNormError=N->SourceQuatNormError;RawProtectedAngle=N->RawProtectedAngle;
            ProtectionError=FMath::Max(FMath::Max(N->TranslationError,N->ScaleError),N->ProtectedRotationError);
        }
}
AParisNPCGripActor::AParisNPCGripActor()
{
    PrimaryActorTick.bCanEverTick=true;PrimaryActorTick.TickGroup=TG_PostUpdateWork;
}
bool AParisNPCGripActor::Bind()
{
    if(!Target || !BindingConfig)return false;
    auto Fail=[this](const TCHAR* S){BindingError=S;SetActorTickEnabled(false);return false;};
    if(Target->IsPlayerControlled())return Fail(TEXT("Player cannot be a NPC grip target"));
    TSharedPtr<FJsonObject> J;
    if(!FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(BindingConfig->BindingJson),J) || !J)
        return Fail(TEXT("Invalid binding config"));
    // Existing accepted Allied configs have no team field and still require0.
    // The separately calibrated German config explicitly requires1.
    double ConfigTeam=0;
    J->TryGetNumberField(TEXT("expected_team_id"),ConfigTeam);
    if(ConfigTeam!=0 && ConfigTeam!=1)return Fail(TEXT("Unsupported configured NPC team"));
    const auto* Team=FindFProperty<FNumericProperty>(Target->GetClass(),TEXT("TeamId"));
    if(!Team || Team->GetSignedIntPropertyValue(Team->ContainerPtrToValuePtr<void>(Target))!=static_cast<int64>(ConfigTeam))
        return Fail(TEXT("Target team differs from calibrated config"));
    const auto* Weapon=FindFProperty<FObjectPropertyBase>(Target->GetClass(),TEXT("WeaponAppearance"));
    if(!Weapon)return Fail(TEXT("Original weapon property absent"));
    BoundGun=Cast<AActor>(Weapon->GetObjectPropertyValue_InContainer(Target));
    if(!BoundGun)return false;
    BoundMesh=Target->GetMesh();GunMesh=BoundGun->FindComponentByClass<UStaticMeshComponent>();
    const auto* Grip=FindFProperty<FObjectPropertyBase>(BoundGun->GetClass(),TEXT("GripMesh"));
    if(!Grip || Grip->GetObjectPropertyValue_InContainer(BoundGun)!=BoundMesh || !GunMesh)
        return Fail(TEXT("Weapon/source component identity mismatch"));
    if(BoundMesh->GetPostProcessInstance())return Fail(TEXT("Preserve existing post-process instance"));
    if(BoundMesh->GetSkeletalMeshAsset()->GetPathName()!=J->GetStringField(TEXT("source_mesh")))
        return Fail(TEXT("Wrong soldier mesh"));
    const auto V=J->GetObjectField(TEXT("gun_hand_relative"));
    const auto T=V->GetArrayField(TEXT("t")),Q=V->GetArrayField(TEXT("q")),S=V->GetArrayField(TEXT("s"));
    GunHand=FTransform(FQuat(Q[0]->AsNumber(),Q[1]->AsNumber(),Q[2]->AsNumber(),Q[3]->AsNumber()),
        FVector(T[0]->AsNumber(),T[1]->AsNumber(),T[2]->AsNumber()),FVector(S[0]->AsNumber(),S[1]->AsNumber(),S[2]->AsNumber()));
    if(!BindingConfig->PostProcessClass)return Fail(TEXT("Postprocess asset not set"));
    BoundMesh->SetOverridePostProcessAnimBP(BindingConfig->PostProcessClass,true);
    BoundMesh->SetDisablePostProcessBlueprint(false);
    const FTransform ComponentActor=GunMesh->GetComponentTransform().GetRelativeTransform(BoundGun->GetActorTransform());
    BoundGun->SetActorTickEnabled(false);
    if(!BoundGun->AttachToComponent(BoundMesh,FAttachmentTransformRules::KeepWorldTransform,TEXT("hand_r")))
        return Fail(TEXT("Gun socket attachment failed"));
    BoundGun->SetActorRelativeTransform(ComponentActor.Inverse()*GunHand);
    AddTickPrerequisiteComponent(BoundMesh);
    Initialized=true;return true;
}
void AParisNPCGripActor::Tick(float Dt)
{
    Super::Tick(Dt);
    if(!Initialized){Bind();return;}
    auto* Anim=Cast<UParisNPCGripAnimInstance>(BoundMesh->GetPostProcessInstance());
    // Main-animation mode changes recreate the postprocess instance. An instance
    // with zero evaluations has not produced an auditable pose yet. Bound this
    // wait, retain the attachment, and still reject invalid evaluated input.
    if(Anim && Anim->Evaluations==0)
    {
        ++PendingEvaluationFrames;
        if(PendingEvaluationStart<0)PendingEvaluationStart=GetWorld()->GetTimeSeconds();
        if(GetWorld()->GetTimeSeconds()-PendingEvaluationStart>.5)
        {BindingError=TEXT("New postprocess instance did not evaluate within0.5s");SetActorTickEnabled(false);}
        return;
    }
    PendingEvaluationStart=-1;
    if(!Anim || !Anim->ValidInput || Anim->ProtectionError>.0001)
    {BindingError=FString::Printf(TEXT("Native input/protection failure: eval=%lld valid=%d error=%.9f"),Anim?Anim->Evaluations:-1,Anim?Anim->ValidInput:false,Anim?Anim->ProtectionError:-1);SetActorTickEnabled(false);return;}
    ++NativeUpdates;
    const auto Actual=GunMesh->GetComponentTransform().GetRelativeTransform(BoundMesh->GetSocketTransform(TEXT("hand_r")));
    GunErrorCm=FVector::Distance(Actual.GetTranslation(),GunHand.GetTranslation());
    GunErrorDegrees=FMath::RadiansToDegrees(Actual.GetRotation().AngularDistance(GunHand.GetRotation()));
    if(Observations.Num()<4096)
    {
        const auto* P=FindFProperty<FNameProperty>(Target->GetClass(),TEXT("ActionState"));
        Observations.Add({GetWorld()->GetTimeSeconds(),Dt,Anim->HoldingWeight,P?P->GetPropertyValue_InContainer(Target):NAME_None,
            GunMesh->GetComponentTransform().GetRelativeTransform(Target->GetActorTransform()),
            BoundMesh->GetSocketTransform(TEXT("hand_r")).GetRelativeTransform(Target->GetActorTransform()),
            BoundMesh->GetSocketTransform(TEXT("hand_l")).GetRelativeTransform(Target->GetActorTransform())});
    }
    if(GunErrorCm>.01 || GunErrorDegrees>.01){BindingError=TEXT("Actual rifle lost hand-relative binding");SetActorTickEnabled(false);}
}
FString AParisNPCGripActor::ObservationJson() const
{
    TArray<TSharedPtr<FJsonValue>> Rows;
    for(const auto& O:Observations)
    {
        auto J=MakeShared<FJsonObject>();J->SetNumberField(TEXT("time"),O.Time);J->SetNumberField(TEXT("dt"),O.Dt);
        J->SetNumberField(TEXT("alpha"),O.Alpha);J->SetStringField(TEXT("action"),O.Action.ToString());
        for(const auto& Pair:TArray<TPair<FString,FTransform>>{{TEXT("gun"),O.Gun},{TEXT("right"),O.Right},{TEXT("left"),O.Left}})
        {
            const FVector V=Pair.Value.GetTranslation();TArray<TSharedPtr<FJsonValue>> XYZ;
            for(double N:{V.X,V.Y,V.Z})XYZ.Add(MakeShared<FJsonValueNumber>(N));J->SetArrayField(Pair.Key,XYZ);
        }
        Rows.Add(MakeShared<FJsonValueObject>(J));
    }
    auto Root=MakeShared<FJsonObject>();Root->SetArrayField(TEXT("observations"),Rows);
    FString Out;FJsonSerializer::Serialize(Root,TJsonWriterFactory<>::Create(&Out));return Out;
}
IMPLEMENT_MODULE(FDefaultModuleImpl,ParisNPCGripV15)
