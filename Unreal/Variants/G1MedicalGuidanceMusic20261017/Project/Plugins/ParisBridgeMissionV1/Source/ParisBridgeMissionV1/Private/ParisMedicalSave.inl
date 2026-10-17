// Versioned optional extension. Old earned bytes are never rewritten on read.
namespace {
bool MN(const TSharedPtr<FJsonObject>& O,const TCHAR* K,double L,double H,bool Integer=true){double N;return O->TryGetNumberField(K,N)&&FMath::IsFinite(N)&&N>=L&&N<=H&&(!Integer||N==FMath::FloorToDouble(N));}
bool MV(const TSharedPtr<FJsonObject>& O,FVector& V){const TArray<TSharedPtr<FJsonValue>>* A=nullptr;double X,Y,Z;if(!O->TryGetArrayField(TEXT("position"),A)||A->Num()!=3||!(*A)[0]->TryGetNumber(X)||!(*A)[1]->TryGetNumber(Y)||!(*A)[2]->TryGetNumber(Z))return false;V=FVector(X,Y,Z);return !V.ContainsNaN()&&V.GetAbsMax()<1000000;}
}
void Capture(UWorld* W,const TSharedPtr<FJsonObject>& Root){
 if(!ParisTutorial::Enabled())return;auto& S=State(W);Sync(W,S);
 auto O=MakeShared<FJsonObject>();O->SetNumberField(TEXT("schema"),1);O->SetStringField(TEXT("config"),TEXT("ParisMedical20261017_50hp_2cap_held3s"));
 O->SetNumberField(TEXT("seed"),S.Seed);O->SetBoolField(TEXT("legacy_import"),S.Legacy);O->SetNumberField(TEXT("held"),S.Held);O->SetNumberField(TEXT("used"),S.Used);
 TArray<TSharedPtr<FJsonValue>> Rows;
 for(int I=0;I<4;++I){const auto& A=S.Sources[I];auto R=MakeShared<FJsonObject>();R->SetStringField(TEXT("id"),Ids[I]);R->SetBoolField(TEXT("eligible"),A.HasKit);R->SetNumberField(TEXT("state"),int(A.State));R->SetBoolField(TEXT("located"),A.Located);R->SetArrayField(TEXT("position"),{MakeShared<FJsonValueNumber>(A.Position.X),MakeShared<FJsonValueNumber>(A.Position.Y),MakeShared<FJsonValueNumber>(A.Position.Z)});Rows.Add(MakeShared<FJsonValueObject>(R));}
 O->SetArrayField(TEXT("sources"),Rows);Root->SetObjectField(TEXT("medical"),O);
}
bool Validate(const TSharedPtr<FJsonObject>& Root,FString& Error){
 auto Bad=[&](const TCHAR* Why){Error=FString(TEXT("Medical snapshot rejected: "))+Why;return false;};
 if(!Root.IsValid())return Bad(TEXT("null root"));
 if(!Root->HasField(TEXT("medical"))){
  const TSharedPtr<FJsonObject>* E=nullptr;double Version=0;
  if(Root->TryGetObjectField(TEXT("equipment"),E)&&(*E)->TryGetNumberField(TEXT("schema"),Version)&&Version==3)return Bad(TEXT("new equipment requires medical receipt"));
  return true;
 }
 if(!ParisTutorial::Enabled())return Bad(TEXT("tutorial-only extension"));
 const TSharedPtr<FJsonObject> *OP=nullptr,*TP=nullptr;FString Config;bool Legacy=false,Combat=false;
 if(!Root->TryGetObjectField(TEXT("medical"),OP)||(*OP)->Values.Num()!=7||!MN(*OP,TEXT("schema"),1,1)||!(*OP)->TryGetStringField(TEXT("config"),Config)||Config!=TEXT("ParisMedical20261017_50hp_2cap_held3s")||!MN(*OP,TEXT("seed"),1,4294967295.)||!(*OP)->TryGetBoolField(TEXT("legacy_import"),Legacy)||!MN(*OP,TEXT("held"),0,2)||!MN(*OP,TEXT("used"),0,4))return Bad(TEXT("schema/identity/bounds"));
 if(!Root->TryGetObjectField(TEXT("tutorial"),TP)||!(*TP)->TryGetBoolField(TEXT("combat_open"),Combat))return Bad(TEXT("tutorial phase"));
 const TArray<TSharedPtr<FJsonValue>> *Rows=nullptr,*Actors=nullptr;
 if(!(*OP)->TryGetArrayField(TEXT("sources"),Rows)||Rows->Num()!=4||!Root->TryGetArrayField(TEXT("actors"),Actors)||Actors->Num()!=6)return Bad(TEXT("fixed sources/actors"));
 const uint32 SeedValue=uint32((*OP)->GetNumberField(TEXT("seed")));int Claimed=0;
 for(int I=0;I<4;++I){const TSharedPtr<FJsonObject>* P=nullptr;FString Id;bool Eligible=false,Located=false;FVector Position;bool IsDead=false;
  if(!(*Rows)[I]->TryGetObject(P)||(*P)->Values.Num()!=5||!(*P)->TryGetStringField(TEXT("id"),Id)||Id!=Ids[I]||!(*P)->TryGetBoolField(TEXT("eligible"),Eligible)||Eligible!=ParisMedicalPolicy::Eligible(SeedValue,I)||!MN(*P,TEXT("state"),0,4)||!(*P)->TryGetBoolField(TEXT("located"),Located)||!MV(*P,Position))return Bad(TEXT("source identity/seed/state/position"));
  if(I<3){const TSharedPtr<FJsonObject>* A=nullptr;FString ActorId;double HP=0;if(!(*Actors)[I+3]->TryGetObject(A)||!(*A)->TryGetStringField(TEXT("id"),ActorId)||ActorId!=Ids[I]||!(*A)->TryGetBoolField(TEXT("dead"),IsDead)||!(*A)->TryGetNumberField(TEXT("health"),HP)||!FMath::IsFinite(HP)||IsDead!=(HP==0))return Bad(TEXT("authoritative death link"));}
  const Claim C=Claim(int((*P)->GetNumberField(TEXT("state"))));
  if(!ParisMedicalPolicy::ValidClaim(C,Eligible,IsDead,Legacy,I==3,Combat))return Bad(TEXT("source phase/death/claim"));
  if(C==Claim::Claimed){if(!Located)return Bad(TEXT("claimed source not located"));++Claimed;}
  if((Located&&C!=Claim::Available&&C!=Claim::Claimed)||((C==Claim::Waiting||C==Claim::Miss||C==Claim::Retired)&&!Position.IsNearlyZero(.000001)))return Bad(TEXT("location state"));
 }
 if(!ParisMedicalPolicy::Conserved(int((*OP)->GetNumberField(TEXT("held"))),int((*OP)->GetNumberField(TEXT("used"))),Claimed))return Bad(TEXT("finite medical conservation"));
 return true;
}
void Restore(UWorld* W,const TSharedPtr<FJsonObject>& Root){
 if(!ParisTutorial::Enabled())return;auto& Old=State(W);End(W,Old,TEXT(""));RemoveVisuals(Old);Old=FState();auto& S=Old;S.Initialized=true;
 auto* M=AParisBridgeMission::Find(W);S.Generation=M?M->RunGeneration:TEXT("medical-restore");
 if(!Root->HasField(TEXT("medical"))){
  S.Legacy=true;S.Seed=Seed(Root->GetStringField(TEXT("mission"))+TEXT("|")+Root->GetStringField(TEXT("config"))+TEXT("|")+FString::FromInt(int(Root->GetNumberField(TEXT("serial"))))+TEXT("|medical-legacy-v1"));
  const auto& Actors=Root->GetArrayField(TEXT("actors"));
  for(int I=0;I<4;++I){auto& A=S.Sources[I];A.HasKit=ParisMedicalPolicy::Eligible(S.Seed,I);if(I<3&&Actors[I+3]->AsObject()->GetBoolField(TEXT("dead")))A.State=Claim::Retired;}
  if(Root->GetObjectField(TEXT("tutorial"))->GetBoolField(TEXT("combat_open")))S.Sources[3].State=Claim::Retired;
  UE_LOG(LogTemp,Display,TEXT("PARIS_MEDICAL legacy_import held=0 used=0 deterministic_seed=%u; old dead sources retired"),S.Seed);
 }else{
  auto O=Root->GetObjectField(TEXT("medical"));S.Seed=uint32(O->GetNumberField(TEXT("seed")));S.Legacy=O->GetBoolField(TEXT("legacy_import"));S.Held=int(O->GetNumberField(TEXT("held")));S.Used=int(O->GetNumberField(TEXT("used")));
  const auto& Rows=O->GetArrayField(TEXT("sources"));for(int I=0;I<4;++I){auto R=Rows[I]->AsObject();auto& A=S.Sources[I];A.HasKit=R->GetBoolField(TEXT("eligible"));A.State=Claim(int(R->GetNumberField(TEXT("state"))));A.Located=R->GetBoolField(TEXT("located"));MV(R,A.Position);}
 }
 // No treatment timers, callbacks, resource grants or health writes on restoration.
 for(auto& A:S.Sources)Visual(W,A);
}
