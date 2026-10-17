// Tutorial schema2 is independent of the retained legacy schema1 validator.
namespace {
bool TN(const TSharedPtr<FJsonObject>& O,const TCHAR* K,double Lo,double Hi,bool Integer=false){double N;return O->TryGetNumberField(K,N)&&FMath::IsFinite(N)&&N>=Lo&&N<=Hi&&(!Integer||N==FMath::FloorToDouble(N));}
bool TV(const TSharedPtr<FJsonObject>& O,const TCHAR* K,FVector& P){const TArray<TSharedPtr<FJsonValue>>* A=nullptr;double X,Y,Z;if(!O->TryGetArrayField(K,A)||A->Num()!=3||!(*A)[0]->TryGetNumber(X)||!(*A)[1]->TryGetNumber(Y)||!(*A)[2]->TryGetNumber(Z))return false;P=FVector(X,Y,Z);return !P.ContainsNaN()&&P.GetAbsMax()<=1000000;}
TArray<TSharedPtr<FJsonValue>> TB(const bool Values[2]){return {MakeShared<FJsonValueBoolean>(Values[0]),MakeShared<FJsonValueBoolean>(Values[1])};}
bool ReadPair(const TSharedPtr<FJsonObject>& O,const TCHAR* K,bool Values[2]){const TArray<TSharedPtr<FJsonValue>>* A=nullptr;return O->TryGetArrayField(K,A)&&A->Num()==2&&(*A)[0]->TryGetBool(Values[0])&&(*A)[1]->TryGetBool(Values[1]);}
}
void Capture(const AParisBridgeMission* M,const TSharedPtr<FJsonObject>& Root){
    if(!Enabled())return;const auto& S=State(M);Root->SetNumberField(TEXT("schema"),2);auto T=MakeShared<FJsonObject>();
    T->SetNumberField(TEXT("schema"),1);T->SetStringField(TEXT("config"),TEXT("G1Tutorial20261013_fixed_roster6_v1"));
    T->SetNumberField(TEXT("step"),S.Stage);T->SetNumberField(TEXT("basic_mask"),S.Mask);T->SetArrayField(TEXT("joined"),TB(S.Joined));T->SetArrayField(TEXT("recruit_history"),TB(S.History));
    T->SetBoolField(TEXT("recruitment_skipped"),S.Skipped);T->SetBoolField(TEXT("combat_open"),S.CombatOpen);T->SetBoolField(TEXT("complete"),S.Done);T->SetBoolField(TEXT("cp0_saved"),S.CP0Saved);
    T->SetStringField(TEXT("checkpoint"),TrainingCheckpoint(M)?TEXT("CP0"):M->Phase==TEXT("Won")?TEXT("CP1"):TEXT("None"));Root->SetObjectField(TEXT("tutorial"),T);
}
void PrepareSavedState(const AParisBridgeMission* M,const TSharedPtr<FJsonObject>& Root){
    auto T=Root->GetObjectField(TEXT("tutorial"));if(TrainingCheckpoint(M))T->SetBoolField(TEXT("cp0_saved"),true);
    else if(M->Phase==TEXT("Won")){T->SetNumberField(TEXT("step"),Complete);T->SetBoolField(TEXT("complete"),true);}
}
bool ValidateEquipment(const TSharedPtr<FJsonObject>& Root,FString& Error){
    if(!ParisMedicalKits::Validate(Root,Error))return false;
    auto Bad=[&](const TCHAR* Why){Error=FString(TEXT("Tutorial equipment rejected: "))+Why;return false;};
    const TSharedPtr<FJsonObject>* Pointer=nullptr;if(!Root->TryGetObjectField(TEXT("equipment"),Pointer))return Bad(TEXT("missing object"));const auto& O=*Pointer;FString C;
    if(!TN(O,TEXT("schema"),2,3,true)||!O->TryGetStringField(TEXT("config"),C))return Bad(TEXT("schema/config"));
    const bool Consolidated=O->GetNumberField(TEXT("schema"))==3;
    if(C!=(Consolidated?TEXT("G1TutorialEquipment20261017_v3_single_training_supply"):TEXT("G1TutorialEquipment20261013_v2")))return Bad(TEXT("schema/config"));
    if(!TN(O,TEXT("frag"),0,4,true)||!TN(O,TEXT("smoke"),0,4,true)||!TN(O,TEXT("frag_thrown"),0,6,true)||!TN(O,TEXT("smoke_thrown"),0,6,true)||!TN(O,TEXT("grant"),0,40,true)||!TN(O,TEXT("frag_grant"),0,5,true)||!TN(O,TEXT("smoke_grant"),0,5,true))return Bad(TEXT("bounded inventory"));
    if(O->GetNumberField(TEXT("frag"))+O->GetNumberField(TEXT("frag_thrown"))!=1+O->GetNumberField(TEXT("frag_grant"))||O->GetNumberField(TEXT("smoke"))+O->GetNumberField(TEXT("smoke_thrown"))!=1+O->GetNumberField(TEXT("smoke_grant")))return Bad(TEXT("grenade conservation"));
    const TArray<TSharedPtr<FJsonValue>>* Supplies=nullptr;const TArray<TSharedPtr<FJsonValue>>* Traps=nullptr;
    if(!O->TryGetArrayField(TEXT("supplies"),Supplies)||Supplies->Num()!=3||!O->TryGetArrayField(TEXT("traps"),Traps)||Traps->Num()!=3)return Bad(TEXT("fixed three-site roster"));
    int Rounds=0,Frags=0,Smokes=0;
    const TSharedPtr<FJsonObject>* Tuto=nullptr;bool Open=false;if(!Root->TryGetObjectField(TEXT("tutorial"),Tuto)||!(*Tuto)->TryGetBoolField(TEXT("combat_open"),Open))return Bad(TEXT("phase identity"));
    for(int I=0;I<3;++I){const TSharedPtr<FJsonObject>* B=nullptr;const TSharedPtr<FJsonObject>* T=nullptr;FString Id,Status;bool Seen;
        const int RB=Consolidated?(I==0?24:I==1?16:0):(I==2?8:16),GB=Consolidated?(I==0?3:I==1?2:0):(I==2?1:2);
        if(!(*Supplies)[I]->TryGetObject(B)||!(*B)->TryGetStringField(TEXT("id"),Id)||Id!=TEXT("Supply")+FString::FromInt(I+1)||!TN(*B,TEXT("remaining"),0,RB,true)||!TN(*B,TEXT("frag_remaining"),0,GB,true)||!TN(*B,TEXT("smoke_remaining"),0,GB,true))return Bad(TEXT("supply identity/stock"));
        Rounds+=RB-int((*B)->GetNumberField(TEXT("remaining")));Frags+=GB-int((*B)->GetNumberField(TEXT("frag_remaining")));Smokes+=GB-int((*B)->GetNumberField(TEXT("smoke_remaining")));
        if(!(*Traps)[I]->TryGetObject(T)||!(*T)->TryGetStringField(TEXT("id"),Id)||Id!=TEXT("Trap")+FString::FromInt(I+1)||!(*T)->TryGetStringField(TEXT("state"),Status)||!(*T)->TryGetBoolField(TEXT("discovered"),Seen)||(Status!=TEXT("Dormant")&&Status!=TEXT("Armed")&&Status!=TEXT("Disarmed")&&Status!=TEXT("Spent")))return Bad(TEXT("trap identity/state"));
        if(I<2&&(!Open&&Status!=TEXT("Dormant")||Open&&Status==TEXT("Dormant")))return Bad(TEXT("combat mine activation"));
        if(I==2&&Status!=TEXT("Disarmed"))return Bad(TEXT("training mine completion"));
    }
    if(Rounds!=O->GetNumberField(TEXT("grant"))||Frags!=O->GetNumberField(TEXT("frag_grant"))||Smokes!=O->GetNumberField(TEXT("smoke_grant")))return Bad(TEXT("supply receipt sums"));
    TSet<FString> Active;
    for(const TCHAR* K:{TEXT("balls"),TEXT("clouds")}){const TArray<TSharedPtr<FJsonValue>>* A=nullptr;if(!O->TryGetArrayField(K,A)||A->Num()>12)return Bad(TEXT("active list"));
        for(const auto& Value:*A){const TSharedPtr<FJsonObject>* P=nullptr;FString Id,Kind;FVector Pos,Vel;
            if(!Value->TryGetObject(P)||!(*P)->TryGetStringField(TEXT("id"),Id)||Active.Contains(Id)||!TV(*P,TEXT("position"),Pos))return Bad(TEXT("active identity/position"));
            if(FString(K)==TEXT("balls")){if(!(*P)->TryGetStringField(TEXT("kind"),Kind)||(Kind!=TEXT("Frag")&&Kind!=TEXT("Smoke"))||!TV(*P,TEXT("velocity"),Vel)||Vel.Size()>5000||!TN(*P,TEXT("fuse"),.000001,3.5)||!TN(*P,TEXT("age"),0,3.5)||!FMath::IsNearlyEqual((*P)->GetNumberField(TEXT("fuse"))+(*P)->GetNumberField(TEXT("age")),3.5,.00001))return Bad(TEXT("projectile/fuse"));}
            else{Kind=TEXT("Smoke");if(!TN(*P,TEXT("life"),.000001,18))return Bad(TEXT("cloud lifetime"));}
            int Count=int(O->GetNumberField(Kind==TEXT("Frag")?TEXT("frag_thrown"):TEXT("smoke_thrown")));bool Committed=false;for(int J=1;J<=Count;++J)Committed|=Id==Kind+FString::FromInt(J);
            if(!Committed)return Bad(TEXT("uncommitted active item"));Active.Add(Id);
        }
    }return true;
}
bool Validate(const AParisBridgeMission* M,const TSharedPtr<FJsonObject>& O,const TArray<TObjectPtr<ACharacter>>& Actors,const TArray<FVector>& Initial,const TArray<int64>& Shots,FString& Error){
    auto Bad=[&](const TCHAR* Why){Error=FString(TEXT("Tutorial snapshot rejected: "))+Why;return false;};
    FString Map,Config,Phase;FVector Control;
    if(!O||!TN(O,TEXT("schema"),2,2,true)||!O->TryGetStringField(TEXT("mission"),Map)||Map!=M->MissionMap||!O->TryGetStringField(TEXT("config"),Config)||Config!=M->ConfigFingerprint||!TN(O,TEXT("serial"),1,2147483646,true)||!O->TryGetStringField(TEXT("phase"),Phase)||!TV(O,TEXT("control"),Control)||Control.GetAbsMax()>360)return Bad(TEXT("schema/mission/config/serial/control"));
    const TSharedPtr<FJsonObject>* TP=nullptr;if(!O->TryGetObjectField(TEXT("tutorial"),TP))return Bad(TEXT("tutorial object"));auto T=*TP;FString TC,CP;
    bool Joined[2],History[2],Skipped,Open,Done,Saved0;
    if(!TN(T,TEXT("schema"),1,1,true)||!T->TryGetStringField(TEXT("config"),TC)||TC!=TEXT("G1Tutorial20261013_fixed_roster6_v1")||!TN(T,TEXT("basic_mask"),BasicMask,BasicMask,true)||!ReadPair(T,TEXT("joined"),Joined)||!ReadPair(T,TEXT("recruit_history"),History)||!T->TryGetBoolField(TEXT("recruitment_skipped"),Skipped)||!T->TryGetBoolField(TEXT("combat_open"),Open)||!T->TryGetBoolField(TEXT("complete"),Done)||!T->TryGetBoolField(TEXT("cp0_saved"),Saved0)||!T->TryGetStringField(TEXT("checkpoint"),CP))return Bad(TEXT("training identities/progress"));
    if((Joined[0]&&!History[0])||(Joined[1]&&!History[1])||(!(History[0]&&History[1])&&!Skipped))return Bad(TEXT("recruitment history"));
    if(CP==TEXT("CP0")){if(Phase!=TEXT("TrainingCheckpoint")||!TN(T,TEXT("step"),CP0,CP0,true)||Open||Done||!Saved0)return Bad(TEXT("CP0 phase"));}
    else if(CP==TEXT("CP1")){if(Phase!=TEXT("Won")||!TN(T,TEXT("step"),Complete,Complete,true)||!Open||!Done)return Bad(TEXT("CP1 phase"));}
    else return Bad(TEXT("checkpoint identity"));
    if(!ValidateEquipment(O,Error))return false;
    const TArray<TSharedPtr<FJsonValue>>* Rows=nullptr;if(!O->TryGetArrayField(TEXT("actors"),Rows)||Rows->Num()!=6||Actors.Num()!=6||Initial.Num()!=6||Shots.Num()!=6)return Bad(TEXT("fixed actor roster"));
    const TCHAR* Ids[]={TEXT("Player"),TEXT("Ally1"),TEXT("Ally2"),TEXT("German1"),TEXT("German2"),TEXT("German3")};int Germans=0,Members=0;
    for(int I=0;I<6;++I){const TSharedPtr<FJsonObject>* RP=nullptr;FString Id,Class;FVector Pos,Rot;bool D;
        if(!(*Rows)[I]->TryGetObject(RP)||!IsValid(Actors[I])||!(*RP)->TryGetStringField(TEXT("id"),Id)||Id!=Ids[I]||!(*RP)->TryGetStringField(TEXT("class"),Class)||Class!=Actors[I]->GetClass()->GetPathName()||!TV(*RP,TEXT("location"),Pos)||!TV(*RP,TEXT("rotation"),Rot)||Rot.GetAbsMax()>360||!(*RP)->TryGetBoolField(TEXT("dead"),D))return Bad(TEXT("actor identity/class/transform"));
        auto A=*RP;if(!TN(A,TEXT("health"),0,Num(Actors[I],TEXT("MaxHealth")))||!TN(A,TEXT("loaded"),0,8,true)||!TN(A,TEXT("reserve"),0,10000,true)||!TN(A,TEXT("shots"),0,2147483646,true)||D!=(A->GetNumberField(TEXT("health"))==0)||I==0&&D)return Bad(TEXT("actor resources/death"));
        double Granted=I==0?O->GetObjectField(TEXT("equipment"))->GetNumberField(TEXT("grant")):0;
        if(A->GetNumberField(TEXT("loaded"))+A->GetNumberField(TEXT("reserve"))+A->GetNumberField(TEXT("shots"))!=Initial[I].Y+Initial[I].Z+Shots[I]+Granted)return Bad(TEXT("finite rifle conservation"));
        if(I>=3){if(!D)++Germans;if(CP==TEXT("CP0")&&(D||A->GetNumberField(TEXT("health"))!=Initial[I].X||A->GetNumberField(TEXT("shots"))!=Shots[I]))return Bad(TEXT("precombat guard mutation"));}
        if(I>0&&I<3&&Joined[I-1]&&!D)++Members;
        if(I==0){const auto* Default=Actors[0]->GetClass()->GetDefaultObject<ACharacter>();const double HH=Default->GetCapsuleComponent()->GetUnscaledCapsuleHalfHeight()*Actors[0]->GetCapsuleComponent()->GetShapeScale();const FVector Feet=Pos-FVector(0,0,HH),Goal=CP==TEXT("CP0")?CP0Feet:M->BridgeheadFeet;if(FVector::Dist2D(Feet,Goal)>M->CheckpointRadius+1||FMath::Abs(Feet.Z-Goal.Z)>100)return Bad(TEXT("checkpoint footprint"));}
    }
    if(Members>2||CP==TEXT("CP0")&&Germans!=3||CP==TEXT("CP1")&&Germans!=0)return Bad(TEXT("enemy/member counts"));return true;
}
void Restore(AParisBridgeMission* M,const TSharedPtr<FJsonObject>& Root){
    auto& S=State(M);auto T=Root->GetObjectField(TEXT("tutorial"));S.Configured=true;S.Stage=int(T->GetNumberField(TEXT("step")));S.Mask=int(T->GetNumberField(TEXT("basic_mask")));ReadPair(T,TEXT("joined"),S.Joined);ReadPair(T,TEXT("recruit_history"),S.History);
    S.Skipped=T->GetBoolField(TEXT("recruitment_skipped"));S.CombatOpen=T->GetBoolField(TEXT("combat_open"));S.Done=T->GetBoolField(TEXT("complete"));S.CP0Saved=T->GetBoolField(TEXT("cp0_saved"));S.Dialog=-1;S.StageAt=M->GetWorld()->GetTimeSeconds()-5;
    S.PreviousFeet=Pawn(M->GetWorld(),TEXT("Player"))->GetNavAgentLocation();Visibility(M);M->LivingAllies=JoinedCount(M);Log(M,TEXT("restored"));
}
