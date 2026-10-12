#pragma once
#include "CoreMinimal.h"
#include "Animation/AnimSequence.h"
#include "Animation/Skeleton.h"
#include "Animation/AnimationPoseData.h"
#include "Animation/AttributesRuntime.h"
#include "BoneContainer.h"
#include "BonePose.h"
#include "Misc/MemStack.h"
#include "UObject/UnrealType.h"

// Same generic implementation in the two independent runtime modules.
// Curves are sampled from the existing private clip, never embedded pose data.
struct FParisExistingRecoil
{
    TArray<FTransform> Samples;
    double Duration=0,StartedAt=0,Age=0,SourceMaximumCm=0;
    int64 SeenShot=0,SeenGeneration=0,Starts=0;
    bool Observed=false,Active=false;
    FString Error;

    static int64 Number(UObject* O,const TCHAR* Name)
    {
        const auto* P=O?FindFProperty<FNumericProperty>(O->GetClass(),Name):nullptr;
        return P?P->GetSignedIntPropertyValue(P->ContainerPtrToValuePtr<void>(O)):0;
    }
    static double Real(UObject* O,const TCHAR* Name,double Fallback)
    {
        const auto* P=O?FindFProperty<FNumericProperty>(O->GetClass(),Name):nullptr;
        return P&&P->IsFloatingPoint()?P->GetFloatingPointPropertyValue(P->ContainerPtrToValuePtr<void>(O)):Fallback;
    }
    static bool Flag(UObject* O,const TCHAR* Name)
    {
        const auto* P=O?FindFProperty<FBoolProperty>(O->GetClass(),Name):nullptr;
        return P&&P->GetPropertyValue_InContainer(O);
    }
    static FName Action(UObject* O)
    {
        const auto* P=O?FindFProperty<FNameProperty>(O->GetClass(),TEXT("ActionState")):nullptr;
        return P?P->GetPropertyValue_InContainer(O):NAME_None;
    }
    bool Prepare(UAnimSequence* Clip)
    {
        if(!Clip||!Clip->GetSkeleton()){Error=TEXT("Existing shooting clip or skeleton absent");return false;}
        const auto& Ref=Clip->GetSkeleton()->GetReferenceSkeleton();
        const int32 Hand=Ref.FindBoneIndex(TEXT("hand_r"));
        Duration=Clip->GetPlayLength();
        if(Hand<0||Duration<=0){Error=TEXT("Existing shooting hand track absent");return false;}
        TArray<int32> Chain;
        for(int32 I=Hand;I>=0;I=Ref.GetParentIndex(I))Chain.Insert(I,0);
        if(Clip->IsValidAdditive()){Error=TEXT("Full existing shooting source required, not additive data");return false;}
        // Full runtime evaluation applies the source Skeleton's retarget rules.
        // Direct compressed bone extraction bypasses those rules and is not
        // equivalent to the editor's AnimationLibrary full-pose measurement.
        FMemMark Mark(FMemStack::Get());
        TArray<FBoneIndexType> Indices;
        for(int32 I=0;I<Ref.GetNum();++I)Indices.Add(static_cast<FBoneIndexType>(I));
        FBoneContainer Required;
        Required.InitializeTo(Indices,UE::Anim::FCurveFilterSettings(UE::Anim::ECurveFilterMode::DisallowAll),*Clip->GetSkeleton());
        Required.SetUseRAWData(false);
        Required.SetUseSourceData(false);
        Required.SetDisableRetargeting(false);
        FCompactPose Pose;Pose.SetBoneContainer(&Required);
        FBlendedCurve Curve;Curve.InitFrom(Required);
        UE::Anim::FStackAttributeContainer Attributes;
        FAnimationPoseData Data(Pose,Curve,Attributes);
        Samples.Reset();SourceMaximumCm=0;Error.Reset();FTransform First=FTransform::Identity;
        for(int32 S=0;S<=30;++S)
        {
            Pose.ResetToRefPose();
            FTransform World=FTransform::Identity;
            FAnimExtractContext Context(Duration*S/30.,false);
#if WITH_EDITOR
            Context.bIgnoreRootLock=true;
#endif
            Clip->GetAnimationPose(Data,Context);
            for(int32 I:Chain)
            {
                const FTransform& Local=Pose[Required.GetCompactPoseIndexFromSkeletonIndex(I)];
                World=Local*World;
            }
            if(S==0)First=World;
            FTransform Delta=World.GetRelativeTransform(First);
            Delta.SetScale3D(FVector::OneVector);
            if(Delta.ContainsNaN()){Error=TEXT("Nonfinite source shooting motion");return false;}
            SourceMaximumCm=FMath::Max(SourceMaximumCm,Delta.GetTranslation().Length());
            Samples.Add(Delta);
        }
        const double EndAngle=FMath::RadiansToDegrees(Samples.Last().GetRotation().AngularDistance(FQuat::Identity));
        if(SourceMaximumCm>8||Samples.Last().GetTranslation().Length()>.01||EndAngle>.05)
        {Error=FString::Printf(TEXT("Existing source gate: max %.9fcm end %.9fcm end-angle %.9fdeg"),SourceMaximumCm,Samples.Last().GetTranslation().Length(),EndAngle);return false;}
        return true;
    }
    FTransform Update(UObject* Target,double Now)
    {
        const int64 Shot=Number(Target,TEXT("ShotSequence")),Generation=Number(Target,TEXT("RestoreGeneration"));
        if(!Observed)
        {SeenShot=Shot;SeenGeneration=Generation;Observed=true;return FTransform::Identity;}
        if(Generation!=SeenGeneration||Shot<SeenShot||Flag(Target,TEXT("IsDead"))||Action(Target)!=TEXT("Ready"))
        {SeenShot=Shot;SeenGeneration=Generation;Active=false;Age=0;return FTransform::Identity;}
        if(Shot>SeenShot)
        {
            // Sequence changes, not input attempts, are authoritative.
            if(Shot-SeenShot!=1){Error=TEXT("Multiple unseen shots exceed bounded recoil observer");Active=false;}
            else if(Error.IsEmpty()&&Samples.Num()==31)
            {
                StartedAt=Real(Target,TEXT("NextShotTime"),Now+.25)-.25;
                Active=true;++Starts;
            }
            SeenShot=Shot;
        }
        if(!Active)return FTransform::Identity;
        Age=FMath::Max(0.,Now-StartedAt);
        if(Age>=Duration){Active=false;return FTransform::Identity;}
        const double Fraction=Age/Duration*30;
        const int32 I=FMath::Clamp(FMath::FloorToInt(Fraction),0,29);
        FTransform Delta;Delta.Blend(Samples[I],Samples[I+1],Fraction-I);
        return Delta;
    }
};
