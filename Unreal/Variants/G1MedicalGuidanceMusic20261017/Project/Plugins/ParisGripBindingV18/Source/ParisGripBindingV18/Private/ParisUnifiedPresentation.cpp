#include "ParisFirstPersonApprovedActor.h"
#include "ParisActionBindings.h"
#include "Components/PoseableMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Character.h"
#include "TwoBoneIK.h"
#include "UObject/UnrealType.h"
#include "Serialization/JsonSerializer.h"

namespace {
FName Action(AActor* P){auto* F=P?FindFProperty<FNameProperty>(P->GetClass(),TEXT("ActionState")):nullptr;return F?F->GetPropertyValue_InContainer(P):NAME_None;}
bool Dead(AActor* P){auto* F=P?FindFProperty<FBoolProperty>(P->GetClass(),TEXT("IsDead")):nullptr;return F&&F->GetPropertyValue_InContainer(P);}
void Components(const FReferenceSkeleton& Ref,const TArray<FTransform>& L,TArray<FTransform>& C){C.SetNum(L.Num());for(int32 I=0;I<L.Num();++I){const int32 P=Ref.GetParentIndex(I);C[I]=P>=0?L[I]*C[P]:L[I];}}
bool Under(const FReferenceSkeleton& R,int32 I,FName Root){for(;I>=0;I=R.GetParentIndex(I))if(R.GetBoneName(I)==Root)return true;return false;}
void CopyArms(const FReferenceSkeleton& Ref,TArray<FTransform>& L,USkeletalMeshComponent* Source,bool UpperBody=false){
 if(!Source||!Source->GetSkeletalMeshAsset())return;const auto& R=Source->GetSkeletalMeshAsset()->GetRefSkeleton();const auto& C=Source->GetComponentSpaceTransforms();if(C.Num()!=R.GetNum())return;
 for(int32 I=0;I<L.Num();++I)if(UpperBody?Under(Ref,I,TEXT("spine_01")):(Under(Ref,I,TEXT("clavicle_l"))||Under(Ref,I,TEXT("clavicle_r")))){const int32 N=R.FindBoneIndex(Ref.GetBoneName(I));if(N>=0){const int32 P=R.GetParentIndex(N);const FTransform T=P>=0?C[N].GetRelativeTransform(C[P]):C[N];L[I].SetRotation(T.GetRotation());L[I].SetScale3D(T.GetScale3D());}}
 if(UpperBody){
  // Native rifle stride and grenade Loop have different pelvis headings.
  // Carry the selected source's upper-body frame through the live root,
  // then solve its top rotation relative to the unchanged native pelvis.
  // Copying only locals would apply the grenade arms in the rifle pelvis frame.
  const int32 Top=Ref.FindBoneIndex(TEXT("spine_01")),N=R.FindBoneIndex(TEXT("spine_01"));
  if(Top>=0&&N>=0&&Ref.GetParentIndex(Top)>=0){TArray<FTransform> Current;Components(Ref,L,Current);
   const FTransform Target=C[N]*C[0].Inverse()*Current[0];L[Top].SetRotation(Target.GetRelativeTransform(Current[Ref.GetParentIndex(Top)]).GetRotation());
  }
 }
}
}

void AParisFirstPersonApprovedActor::SetUnifiedObserver(bool B){
 if(!UnifiedPresentation)UnifiedPresentation=MakeUnique<FParisUnifiedPresentation>();auto& S=*UnifiedPresentation;auto* P=Cast<ACharacter>(GetOwner());if(!P)return;
 if(B&&!S.Observer){S.OriginalHidden=P->GetMesh()->bHiddenInGame;S.OriginalOwnerNoSee=P->GetMesh()->bOwnerNoSee;S.OriginalAnimTick=uint8(P->GetMesh()->VisibilityBasedAnimTickOption);P->GetMesh()->VisibilityBasedAnimTickOption=EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;}
 S.Observer=B;SetActorHiddenInGame(B);
 if(!B)P->GetMesh()->VisibilityBasedAnimTickOption=EVisibilityBasedAnimTickOption(S.OriginalAnimTick);
 if(!B){for(const auto& Entry:S.HiddenLegacyRifles)if(Entry.Key.IsValid())Entry.Key->SetActorHiddenInGame(Entry.Value);S.HiddenLegacyRifles.Reset();if(S.Actor.IsValid())S.Actor->SetActorHiddenInGame(true);if(!Dead(P)){P->GetMesh()->SetHiddenInGame(S.OriginalHidden);P->GetMesh()->SetOwnerNoSee(S.OriginalOwnerNoSee);}}
 UpdateUnifiedPresentation(FTransform::Identity);
}
void AParisFirstPersonApprovedActor::SetUnifiedRifleVisible(bool B){
 B=B&&!HasMedicalPoseSource();
 if(!UnifiedPresentation)UnifiedPresentation=MakeUnique<FParisUnifiedPresentation>();UnifiedPresentation->RifleVisible=B;Gun->SetVisibility(B,true);if(UnifiedPresentation->Rifle.IsValid())UnifiedPresentation->Rifle->SetVisibility(B,true);
}
USkinnedMeshComponent* AParisFirstPersonApprovedActor::UnifiedVisibleBody(){
 if(UnifiedPresentation&&UnifiedPresentation->Observer&&UnifiedPresentation->Body.IsValid())return UnifiedPresentation->Body.Get();return Pose;
}
UStaticMeshComponent* AParisFirstPersonApprovedActor::UnifiedVisibleRifle(){
 if(Dead(GetOwner()))return nullptr;
 if(UnifiedPresentation&&!UnifiedPresentation->RifleVisible)return nullptr;
 if(UnifiedPresentation&&UnifiedPresentation->Observer)return UnifiedPresentation->Rifle.Get();return Gun;
}
bool AParisFirstPersonApprovedActor::UnifiedNativeBodyDefaults(bool& Hidden,bool& OwnerNoSee,uint8& AnimTick) const{if(!UnifiedPresentation||!UnifiedPresentation->Observer)return false;const auto& S=*UnifiedPresentation;Hidden=S.OriginalHidden;OwnerNoSee=S.OriginalOwnerNoSee;AnimTick=S.OriginalAnimTick;return true;}
bool AParisFirstPersonApprovedActor::UnifiedObserver() const{return UnifiedPresentation&&UnifiedPresentation->Observer;}
void AParisFirstPersonApprovedActor::RefreshUnifiedPresentation(){const FTransform D=UnifiedPresentation?UnifiedPresentation->Recoil:FTransform::Identity;UpdateUnifiedPresentation(D);}
void AParisFirstPersonApprovedActor::DestroyUnifiedPresentation(){if(UnifiedPresentation){for(const auto& Entry:UnifiedPresentation->HiddenLegacyRifles)if(Entry.Key.IsValid())Entry.Key->SetActorHiddenInGame(Entry.Value);if(UnifiedPresentation->Actor.IsValid())UnifiedPresentation->Actor->Destroy();}UnifiedPresentation.Reset();}

void AParisFirstPersonApprovedActor::UpdateUnifiedPresentation(const FTransform& Delta){
 if(!Initialized)return;if(!UnifiedPresentation)UnifiedPresentation=MakeUnique<FParisUnifiedPresentation>();auto& S=*UnifiedPresentation;S.Recoil=Delta;
 auto* P=Cast<ACharacter>(GetOwner());if(!P)return;auto* Native=P->GetMesh();
 if(auto* F=FindFProperty<FObjectPropertyBase>(P->GetClass(),TEXT("WeaponAppearance")))if(auto* Old=Cast<AActor>(F->GetObjectPropertyValue_InContainer(P)))Old->SetActorHiddenInGame(true);
 if(!S.Observer||Dead(P)){if(S.Actor.IsValid())S.Actor->SetActorHiddenInGame(true);return;}
 if(!S.Actor.IsValid()){
  auto* A=GetWorld()->SpawnActor<AActor>();A->SetOwner(P);A->Tags.Add(TEXT("ParisUnifiedPerspectiveDisplay"));
  auto* B=NewObject<UPoseableMeshComponent>(A,TEXT("UnifiedBodyDisplay"));A->AddInstanceComponent(B);A->SetRootComponent(B);B->SetSkinnedAssetAndUpdate(Native->GetSkeletalMeshAsset());B->SetCollisionEnabled(ECollisionEnabled::NoCollision);B->SetCanEverAffectNavigation(false);B->SetForcedLOD(1);B->RegisterComponent();
  for(int32 I=0;I<Native->GetNumMaterials();++I)B->SetMaterial(I,Native->GetMaterial(I));
  auto* G=NewObject<UStaticMeshComponent>(A,TEXT("UnifiedRifleDisplay"));A->AddInstanceComponent(G);G->SetupAttachment(B,TEXT("hand_r"));G->SetStaticMesh(Gun->GetStaticMesh());G->SetCollisionEnabled(ECollisionEnabled::NoCollision);G->SetCanEverAffectNavigation(false);G->RegisterComponent();G->SetRelativeTransform(AcceptedRifleInHand());
  for(int32 I=0;I<Gun->GetNumMaterials();++I)G->SetMaterial(I,Gun->GetMaterial(I));
  S.Actor=A;S.Body=B;S.Rifle=G;
 }
 const auto& Ref=Native->GetSkeletalMeshAsset()->GetRefSkeleton();const auto& C=Native->GetComponentSpaceTransforms();if(C.Num()!=Ref.GetNum())return;
 TArray<FTransform> L;L.SetNum(C.Num());for(int32 I=0;I<C.Num();++I){const int32 Parent=Ref.GetParentIndex(I);L[I]=Parent>=0?C[I].GetRelativeTransform(C[Parent]):C[I];}
 const FName Current=Action(P);
 auto* Medical=UnifiedMedicalSource();
 // Preserve live pelvis/spine/legs for standing, crouched and prone support.
 // Only native clavicle/arm rotations enter the visible observer body.
 if(Medical)CopyArms(Ref,L,Medical);
 auto* Equipment=UnifiedEquipmentSource();
 // Retain the reviewed preparation fix: selection already equipped the prop.
 if(Equipment)CopyArms(Ref,L,Equipment,true);
 // Rifle Ready retains the complete live gameplay-body pose, including its
 // pelvis/spine/shoulder frame and locomotion/aim. The FP holding workspace
 // is camera-calibrated as a whole; transplanting its arm locals into this
 // different torso frame folds the arms away from the visible native rifle.
 if(S.RifleVisible)ApplySharedGrip(Ref,L,HoldingAppliedAlpha,false);
 const FName PoseKey=Medical?FName(TEXT("MedicalTreating")):Equipment&&Current==TEXT("Ready")?FName(TEXT("Equipped")):Equipment?UnifiedEquipmentLabel():Current;
 const double Now=GetWorld()->GetTimeSeconds();
 if(PoseKey!=S.PoseKey){S.TransitionFrom=S.PreviousPose;S.PoseKey=PoseKey;S.TransitionAt=Now;}
 const double Blend=FMath::Clamp((Now-S.TransitionAt)/.25,0.,1.);
 if(S.TransitionFrom.Num()==L.Num()&&Blend<1)for(int32 I=0;I<L.Num();++I)if(Under(Ref,I,TEXT("spine_01")))L[I].SetRotation(FQuat::Slerp(S.TransitionFrom[I].GetRotation(),L[I].GetRotation(),Blend).GetNormalized());
 S.PreviousPose=L;
 if(Equipment){ApplySmokeGripContact(Ref,L);ApplyFragGripContact(Ref,L);}
 TArray<FTransform> Before;Components(Ref,L,Before);S.RecoilHandDelta=0;
 if(RecoilActive&&S.RifleVisible&&Current==TEXT("Ready")){
  const int32 HR=Ref.FindBoneIndex(TEXT("hand_r")),HL=Ref.FindBoneIndex(TEXT("hand_l"));
  if(HR>=0&&HL>=0){const FTransform Right=Delta*Before[HR],Left=Before[HL].GetRelativeTransform(Before[HR])*Right;
   S.RecoilHandDelta=FVector::Distance(Right.GetLocation(),Before[HR].GetLocation());
   for(const auto& Pair:{TPair<FName,FTransform>(TEXT("hand_r"),Right),TPair<FName,FTransform>(TEXT("hand_l"),Left)}){
    const int32 H=Ref.FindBoneIndex(Pair.Key),Lower=Ref.GetParentIndex(H),Upper=Ref.GetParentIndex(Lower),Parent=Ref.GetParentIndex(Upper);
    FTransform U=Before[Upper],Lo=Before[Lower],Ha=Before[H];const double A=FVector::Distance(U.GetLocation(),Lo.GetLocation()),B=FVector::Distance(Lo.GetLocation(),Ha.GetLocation());
    AnimationCore::SolveTwoBoneIK(U,Lo,Ha,Lo.GetLocation(),Pair.Value.GetLocation(),A,B,false,1.,1.);Ha.SetRotation(Pair.Value.GetRotation());
    L[Upper]=U.GetRelativeTransform(Before[Parent]);L[Lower]=Lo.GetRelativeTransform(U);L[H]=Ha.GetRelativeTransform(Lo);
    S.MaxLengthError=FMath::Max(S.MaxLengthError,FMath::Max(FMath::Abs(FVector::Distance(U.GetLocation(),Lo.GetLocation())-A),FMath::Abs(FVector::Distance(Lo.GetLocation(),Ha.GetLocation())-B)));
   }
  }
 }
 S.Actor->SetActorHiddenInGame(false);S.Body->SetWorldTransform(Native->GetComponentTransform());S.Body->BoneSpaceTransforms=L;S.Body->MarkRefreshTransformDirty();S.Body->RefreshBoneTransforms(nullptr);
 // The native body-attached rifle is distinct from WeaponAppearance (the
 // old FP static rifle). OwnerNoSee is insufficient when viewing through a
 // camera actor. Hide only this player's superseded rifle mesh actors while
 // observing and restore each original flag on exit/death/world teardown.
 for(TActorIterator<AActor> It(GetWorld());It;++It){auto* Legacy=*It;
  if(Legacy==this||Legacy==S.Actor.Get()||Legacy->GetOwner()!=P)continue;
  TArray<UStaticMeshComponent*> Parts;Legacy->GetComponents(Parts);
  for(auto* Part:Parts)if(Part->GetStaticMesh()==Gun->GetStaticMesh()){
   const TWeakObjectPtr<AActor> Key(Legacy);if(!S.HiddenLegacyRifles.Contains(Key))S.HiddenLegacyRifles.Add(Key,Legacy->IsHidden());Legacy->SetActorHiddenInGame(true);break;
  }
 }
 S.Rifle->SetVisibility(S.RifleVisible,true);Native->SetHiddenInGame(true);Native->SetOwnerNoSee(true);SetActorHiddenInGame(true);S.Frame=GFrameCounter;
}
FString AParisFirstPersonApprovedActor::InspectUnifiedPresentation() const {
 auto O=MakeShared<FJsonObject>();O->SetBoolField(TEXT("observer"),UnifiedObserver());O->SetStringField(TEXT("action"),Action(GetOwner()).ToString());
 if(UnifiedPresentation){const auto& S=*UnifiedPresentation;O->SetBoolField(TEXT("rifle_visible"),S.RifleVisible);O->SetNumberField(TEXT("recoil_hand_delta_cm"),S.RecoilHandDelta);O->SetNumberField(TEXT("max_length_error_cm"),S.MaxLengthError);O->SetNumberField(TEXT("frame"),S.Frame);O->SetStringField(TEXT("body"),S.Body.IsValid()?S.Body->GetPathName():TEXT("None"));O->SetStringField(TEXT("rifle"),S.Rifle.IsValid()?S.Rifle->GetPathName():TEXT("None"));}
 FString R;FJsonSerializer::Serialize(O,TJsonWriterFactory<>::Create(&R));return R;
}
