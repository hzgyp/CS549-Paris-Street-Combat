// Included after the existing vector/number JSON helpers. No disk I/O here.
bool ReadSmokePose(const TSharedPtr<FJsonObject>& Item,FSmokePose& Pose){
    if(!Item->HasField(TEXT("smoke_pose")))return true;
    const TSharedPtr<FJsonObject>* Field=nullptr;
    if(!Item->TryGetObjectField(TEXT("smoke_pose"),Field))return false;const auto& O=*Field;
    if(O->Values.Num()!=7||!N(O,TEXT("version"),1,1,true)||!Vec(O,TEXT("position"),Pose.Position)||!Vec(O,TEXT("scale"),Pose.Scale)||!Vec(O,TEXT("linear"),Pose.Linear)||!Vec(O,TEXT("angular"),Pose.Angular)||!O->TryGetBoolField(TEXT("sleeping"),Pose.Sleeping))return false;
    const TArray<TSharedPtr<FJsonValue>>* Q=nullptr;
    if(!O->TryGetArrayField(TEXT("rotation"),Q)||Q->Num()!=4)return false;
    ParisSmokePresentation::PoseNumbers P{{Pose.Position.X,Pose.Position.Y,Pose.Position.Z},{Pose.Scale.X,Pose.Scale.Y,Pose.Scale.Z},{Pose.Linear.X,Pose.Linear.Y,Pose.Linear.Z},{Pose.Angular.X,Pose.Angular.Y,Pose.Angular.Z},{}};
    for(int32 I=0;I<4;++I)if(!(*Q)[I]->TryGetNumber(P.Rotation[I]))return false;
    if(!ParisSmokePresentation::Valid(P))return false;
    Pose.Rotation=FQuat(P.Rotation[0],P.Rotation[1],P.Rotation[2],P.Rotation[3]).GetNormalized();Pose.Valid=true;return true;
}
void WriteSmokePose(const TSharedPtr<FJsonObject>& Item,const FSmokePose& Pose){
    if(!Pose.Valid)return;
    auto O=MakeShared<FJsonObject>();O->SetNumberField(TEXT("version"),1);O->SetArrayField(TEXT("position"),V(Pose.Position));O->SetArrayField(TEXT("scale"),V(Pose.Scale));O->SetArrayField(TEXT("linear"),V(Pose.Linear));O->SetArrayField(TEXT("angular"),V(Pose.Angular));O->SetBoolField(TEXT("sleeping"),Pose.Sleeping);
    O->SetArrayField(TEXT("rotation"),{MakeShared<FJsonValueNumber>(Pose.Rotation.X),MakeShared<FJsonValueNumber>(Pose.Rotation.Y),MakeShared<FJsonValueNumber>(Pose.Rotation.Z),MakeShared<FJsonValueNumber>(Pose.Rotation.W)});Item->SetObjectField(TEXT("smoke_pose"),O);
}
bool ValidateSmokePoses(const TSharedPtr<FJsonObject>& Root,FString& Error){
    const TSharedPtr<FJsonObject>* Equipment=nullptr;
    if(!Root->TryGetObjectField(TEXT("equipment"),Equipment))return true; // Core validator owns missing/invalid equipment.
    for(const TCHAR* Key:{TEXT("balls"),TEXT("clouds")}){
        const TArray<TSharedPtr<FJsonValue>>* Items=nullptr;if(!(*Equipment)->TryGetArrayField(Key,Items))continue;
        for(const auto& Value:*Items){const TSharedPtr<FJsonObject>* Item=nullptr;if(!Value->TryGetObject(Item)||!(*Item)->HasField(TEXT("smoke_pose")))continue;
            FSmokePose Pose;FVector Position,Velocity;FString Kind;
            bool Valid=ReadSmokePose(*Item,Pose)&&Vec(*Item,TEXT("position"),Position);
            if(FString(Key)==TEXT("balls"))Valid=Valid&&(*Item)->TryGetStringField(TEXT("kind"),Kind)&&Kind==TEXT("Smoke")&&Vec(*Item,TEXT("velocity"),Velocity)&&Pose.Position.Equals(Position,.001)&&Pose.Linear.Equals(Velocity,.001);
            // A burning body can keep moving after ignition; its bounded visual
            // position must not replace or constrain the original cover anchor.
            if(!Valid){Error=TEXT("Equipment rejected: optional smoke pose");return false;}
        }
    }
    return true;
}
