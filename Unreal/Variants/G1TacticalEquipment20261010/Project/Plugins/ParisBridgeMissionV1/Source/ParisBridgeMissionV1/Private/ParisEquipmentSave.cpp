#include "ParisEquipmentState.h"
#include "Engine/World.h"
#include "GameFramework/Actor.h"

namespace ParisTacticalEquipment {
namespace {
TArray<TSharedPtr<FJsonValue>> V(const FVector& P){return {MakeShared<FJsonValueNumber>(P.X),MakeShared<FJsonValueNumber>(P.Y),MakeShared<FJsonValueNumber>(P.Z)};}
bool Vec(const TSharedPtr<FJsonObject>& O,const TCHAR* K,FVector& Out){const TArray<TSharedPtr<FJsonValue>>* A=nullptr;if(!O->TryGetArrayField(K,A)||A->Num()!=3)return false;double X,Y,Z;if(!(*A)[0]->TryGetNumber(X)||!(*A)[1]->TryGetNumber(Y)||!(*A)[2]->TryGetNumber(Z))return false;Out=FVector(X,Y,Z);return !Out.ContainsNaN()&&Out.GetAbsMax()<1000000;}
bool N(const TSharedPtr<FJsonObject>& O,const TCHAR* K,double Low,double High,bool Integer=false){double X;return O->TryGetNumberField(K,X)&&FMath::IsFinite(X)&&X>=Low&&X<=High&&(!Integer||X==FMath::FloorToDouble(X));}
const FString Config=TEXT("G1Equipment_20261010_frag2_smoke2_sup16x2_trap2_physical_sites_v3");
}
void CaptureEquipment(UWorld* World,const TSharedPtr<FJsonObject>& Root) {
    auto& S=Session(World);auto O=MakeShared<FJsonObject>();O->SetNumberField(TEXT("schema"),1);O->SetStringField(TEXT("config"),Config);
    O->SetNumberField(TEXT("frag"),S.Frag);O->SetNumberField(TEXT("smoke"),S.Smoke);O->SetNumberField(TEXT("frag_thrown"),S.FragThrown);O->SetNumberField(TEXT("smoke_thrown"),S.SmokeThrown);O->SetNumberField(TEXT("grant"),S.Grant);
    TArray<TSharedPtr<FJsonValue>> Balls,Clouds,Traps,Supplies;
    for(const auto& B:S.Balls){auto A=MakeShared<FJsonObject>();A->SetStringField(TEXT("id"),B.Id);A->SetStringField(TEXT("kind"),B.Kind);A->SetArrayField(TEXT("position"),V(B.Position));A->SetArrayField(TEXT("velocity"),V(B.Velocity));A->SetNumberField(TEXT("fuse"),B.Fuse);A->SetNumberField(TEXT("age"),B.Age);Balls.Add(MakeShared<FJsonValueObject>(A));}
    for(const auto& C:S.Clouds){auto A=MakeShared<FJsonObject>();A->SetStringField(TEXT("id"),C.Id);A->SetArrayField(TEXT("position"),V(C.Position));A->SetNumberField(TEXT("life"),C.Life);Clouds.Add(MakeShared<FJsonValueObject>(A));}
    for(const auto& T:S.Traps){auto A=MakeShared<FJsonObject>();A->SetStringField(TEXT("id"),T.Id);A->SetStringField(TEXT("state"),T.State);A->SetBoolField(TEXT("discovered"),T.Discovered);Traps.Add(MakeShared<FJsonValueObject>(A));}
    for(const auto& B:S.Supplies){auto A=MakeShared<FJsonObject>();A->SetStringField(TEXT("id"),B.Id);A->SetNumberField(TEXT("remaining"),B.Remaining);Supplies.Add(MakeShared<FJsonValueObject>(A));}
    O->SetArrayField(TEXT("balls"),Balls);O->SetArrayField(TEXT("clouds"),Clouds);O->SetArrayField(TEXT("traps"),Traps);O->SetArrayField(TEXT("supplies"),Supplies);Root->SetObjectField(TEXT("equipment"),O);
}
bool ValidateEquipment(const TSharedPtr<FJsonObject>& Root,FString& Error) {
    // Legacy V5 has no equipment: the unchanged base validator still applies.
    if(!Root->HasField(TEXT("equipment")))return true;
    const TSharedPtr<FJsonObject>* P=nullptr;
    auto Reject=[&](const TCHAR* Why){Error=FString(TEXT("Equipment rejected: "))+Why;return false;};
    if(!Root->TryGetObjectField(TEXT("equipment"),P))return Reject(TEXT("object"));const auto& O=*P;FString C;
    if(!N(O,TEXT("schema"),1,1,true)||!O->TryGetStringField(TEXT("config"),C)||C!=Config)return Reject(TEXT("schema/config"));
    for(const TCHAR* K:{TEXT("frag"),TEXT("smoke"),TEXT("frag_thrown"),TEXT("smoke_thrown")})if(!N(O,K,0,2,true))return Reject(TEXT("inventory"));
    if(O->GetNumberField(TEXT("frag"))+O->GetNumberField(TEXT("frag_thrown"))!=2||O->GetNumberField(TEXT("smoke"))+O->GetNumberField(TEXT("smoke_thrown"))!=2||!N(O,TEXT("grant"),0,32,true))return Reject(TEXT("conservation"));
    TSet<FString> ActiveIds;
    auto ValidId=[&](const FString& Id,const FString& Kind){const int32 Count=int32(O->GetNumberField(Kind==TEXT("Frag")?TEXT("frag_thrown"):TEXT("smoke_thrown")));for(int32 I=1;I<=Count;++I)if(Id==Kind+FString::FromInt(I))return true;return false;};
    for(const TCHAR* Key:{TEXT("balls"),TEXT("clouds")}) {
        const TArray<TSharedPtr<FJsonValue>>* A=nullptr;if(!O->TryGetArrayField(Key,A)||A->Num()>4)return Reject(TEXT("active list"));
        for(const auto& Value:*A){const TSharedPtr<FJsonObject>* PItem=nullptr;if(!Value->TryGetObject(PItem))return Reject(TEXT("active object"));const auto& Item=*PItem;FString Id,Kind;FVector Pos,Vel;
            if(!Item->TryGetStringField(TEXT("id"),Id)||ActiveIds.Contains(Id)||!Vec(Item,TEXT("position"),Pos))return Reject(TEXT("active identity/position"));
            if(FString(Key)==TEXT("balls")){if(!Item->TryGetStringField(TEXT("kind"),Kind)||(Kind!=TEXT("Frag")&&Kind!=TEXT("Smoke"))||!Vec(Item,TEXT("velocity"),Vel)||Vel.Size()>5000||!N(Item,TEXT("fuse"),.000001,3.5)||!N(Item,TEXT("age"),0,3.5))return Reject(TEXT("projectile"));if(!FMath::IsNearlyEqual(Item->GetNumberField(TEXT("age"))+Item->GetNumberField(TEXT("fuse")),3.5,.00001))return Reject(TEXT("fuse conservation"));}
            else {Kind=TEXT("Smoke");if(!N(Item,TEXT("life"),.000001,18))return Reject(TEXT("smoke life"));}
            if(!ValidId(Id,Kind))return Reject(TEXT("uncommitted active item"));ActiveIds.Add(Id);
        }
    }
    const TArray<TSharedPtr<FJsonValue>> *Traps=nullptr,*Supplies=nullptr;
    if(!O->TryGetArrayField(TEXT("traps"),Traps)||Traps->Num()!=2||!O->TryGetArrayField(TEXT("supplies"),Supplies)||Supplies->Num()!=2)return Reject(TEXT("fixed site roster"));
    int32 Granted=0;
    for(int32 I=0;I<2;++I){const TSharedPtr<FJsonObject> *T=nullptr,*B=nullptr;FString Id,State;bool Discovered=false;
        if(!(*Traps)[I]->TryGetObject(T)||!(*T)->TryGetStringField(TEXT("id"),Id)||Id!=TEXT("Trap")+FString::FromInt(I+1)||!(*T)->TryGetStringField(TEXT("state"),State)||(State!=TEXT("Armed")&&State!=TEXT("Disarmed")&&State!=TEXT("Spent"))||!(*T)->TryGetBoolField(TEXT("discovered"),Discovered))return Reject(TEXT("trap state"));
        if(!(*Supplies)[I]->TryGetObject(B)||!(*B)->TryGetStringField(TEXT("id"),Id)||Id!=TEXT("Supply")+FString::FromInt(I+1)||!N(*B,TEXT("remaining"),0,16,true))return Reject(TEXT("supply state"));Granted+=16-int32((*B)->GetNumberField(TEXT("remaining")));
    }
    if(Granted!=O->GetNumberField(TEXT("grant")))return Reject(TEXT("supply receipt sum"));
    FString Phase;Root->TryGetStringField(TEXT("phase"),Phase);
    if(Phase==TEXT("Ready")&&(Granted||O->GetNumberField(TEXT("frag_thrown"))||O->GetNumberField(TEXT("smoke_thrown"))))return Reject(TEXT("unstarted resources"));
    return true;
}
double ValidatedGrant(const TSharedPtr<FJsonObject>& Root,int32 ActorIndex) {
    if(ActorIndex!=0)return 0;const TSharedPtr<FJsonObject>* O=nullptr;return Root->TryGetObjectField(TEXT("equipment"),O)?(*O)->GetNumberField(TEXT("grant")):0;
}
void RestoreEquipment(UWorld* World,const TSharedPtr<FJsonObject>& Root) {
    auto& S=Session(World);ClearVisuals(S);S.Balls.Reset();S.Clouds.Reset();S.Restored=true;
    // Legacy payload grants no new equipment or ammunition.
    if(!Root->HasField(TEXT("equipment"))){S.Frag=S.Smoke=0;S.FragThrown=S.SmokeThrown=2;S.Grant=0;CreateVisuals(World,S);return;}
    auto O=Root->GetObjectField(TEXT("equipment"));S.Frag=int32(O->GetNumberField(TEXT("frag")));S.Smoke=int32(O->GetNumberField(TEXT("smoke")));S.FragThrown=int32(O->GetNumberField(TEXT("frag_thrown")));S.SmokeThrown=int32(O->GetNumberField(TEXT("smoke_thrown")));S.Grant=int32(O->GetNumberField(TEXT("grant")));
    for(const auto& A:O->GetArrayField(TEXT("balls"))){auto B=A->AsObject();FBall Ball;Ball.Id=B->GetStringField(TEXT("id"));Ball.Kind=B->GetStringField(TEXT("kind"));Vec(B,TEXT("position"),Ball.Position);Vec(B,TEXT("velocity"),Ball.Velocity);Ball.Fuse=B->GetNumberField(TEXT("fuse"));Ball.Age=B->GetNumberField(TEXT("age"));S.Balls.Add(Ball);}
    for(const auto& A:O->GetArrayField(TEXT("clouds"))){auto C=A->AsObject();FSmoke Cloud;Cloud.Id=C->GetStringField(TEXT("id"));Vec(C,TEXT("position"),Cloud.Position);Cloud.Life=C->GetNumberField(TEXT("life"));S.Clouds.Add(Cloud);}
    const auto& Traps=O->GetArrayField(TEXT("traps"));const auto& Supplies=O->GetArrayField(TEXT("supplies"));
    for(int32 I=0;I<2;++I){S.Traps[I].State=Traps[I]->AsObject()->GetStringField(TEXT("state"));S.Traps[I].Discovered=Traps[I]->AsObject()->GetBoolField(TEXT("discovered"));S.Supplies[I].Remaining=int32(Supplies[I]->AsObject()->GetNumberField(TEXT("remaining")));}
    CreateVisuals(World,S);
}
}
