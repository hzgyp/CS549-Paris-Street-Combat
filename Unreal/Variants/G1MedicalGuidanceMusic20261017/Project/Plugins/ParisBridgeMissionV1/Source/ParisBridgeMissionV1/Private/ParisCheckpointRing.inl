// Presentation only. Save admission still uses the original registered XY/radius/grounded checks.
TArray<FVector> ParisCheckpointRingGeometry(const AParisBridgeMission* M){
 TArray<FVector> Points;if(!M||!M->CheckpointUnlocked()||M->Phase==TEXT("Lost")||M->Phase==TEXT("Error"))return Points;
 const FVector Center=ParisTutorial::Enabled()?ParisTutorial::CheckpointFeet(M):M->BridgeheadFeet;
 static TWeakObjectPtr<const AParisBridgeMission> CachedMission;static FVector CachedCenter;static double CachedRadius=0;static TArray<FVector> CachedPoints;
 if(CachedMission.Get()==M&&CachedCenter.Equals(Center,.001)&&CachedRadius==M->CheckpointRadius)return CachedPoints;
 FCollisionQueryParams Q(SCENE_QUERY_STAT(ParisCheckpointRingGround),false);
 const FCollisionObjectQueryParams Static(FCollisionObjectQueryParams::InitType::AllStaticObjects);
 double CenterZ=Center.Z;FHitResult Hit;
 if(M->GetWorld()->LineTraceSingleByObjectType(Hit,Center+FVector(0,0,200),Center-FVector(0,0,200),Static,Q)&&Hit.ImpactNormal.Z>=.6)CenterZ=Hit.ImpactPoint.Z;
 for(int I=0;I<96;++I){const double Angle=2*PI*I/96;FVector P=Center+FVector(FMath::Cos(Angle)*M->CheckpointRadius,FMath::Sin(Angle)*M->CheckpointRadius,0);P.Z=CenterZ;
  if(M->GetWorld()->LineTraceSingleByObjectType(Hit,P+FVector(0,0,150),P-FVector(0,0,150),Static,Q)&&Hit.ImpactNormal.Z>=.6)P.Z=Hit.ImpactPoint.Z;
  P.Z+=8;Points.Add(P);
 }CachedMission=M;CachedCenter=Center;CachedRadius=M->CheckpointRadius;CachedPoints=Points;return Points;
}
void ParisDrawCheckpointRing(AParisBridgeMission* M){
 const auto Points=ParisCheckpointRingGeometry(M);for(int I=0;I<Points.Num();++I)DrawDebugLine(M->GetWorld(),Points[I],Points[(I+1)%Points.Num()],FColor(202,171,105),false,-1,0,2.5);
 static TWeakObjectPtr<AParisBridgeMission> Last;static FString Key;
 const FString Current=ParisTutorial::Enabled()&&ParisTutorial::TrainingCheckpoint(M)?TEXT("CP0"):TEXT("CP1");
 if(Last.Get()!=M||Key!=Current){Last=M;Key=Current;double Low=DBL_MAX,High=-DBL_MAX;for(auto P:Points){Low=FMath::Min(Low,P.Z);High=FMath::Max(High,P.Z);}UE_LOG(LogTemp,Display,TEXT("PARIS_CHECKPOINT_RING id=%s samples=%d z_min=%.4f z_max=%.4f"),*Current,Points.Num(),Low,High);}
}
