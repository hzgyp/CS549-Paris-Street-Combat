// G1-only conservative constraint. Original collision and AI remain authoritative.
bool AParisBridgeMission::ApplyBridgeNavigationConstraint(FString& Error)
{
    if(bBridgeNavigationValidated) return true;
    if(Roster.Num()!=6 || !IsValid(Roster[0])) { Error=TEXT("Bridge constraint requires the original roster."); return false; }
    const FVector Feet(5192.972650,-20735.731259,128.136620);
    auto* C=Roster[0]->GetCapsuleComponent();
    const FVector Center=Feet+FVector(0,0,C->GetScaledCapsuleHalfHeight());
    const FVector Direction=(FVector(5225.223529,-20748,135.176471)-Feet).GetSafeNormal2D();
    FHitResult Hit; FCollisionQueryParams Q(SCENE_QUERY_STAT(ParisG1BridgeWitness),false,Roster[0]);
    const bool Blocked=GetWorld()->SweepSingleByChannel(Hit,Center,Center+Direction*60,FQuat::Identity,
        C->GetCollisionObjectType(),FCollisionShape::MakeCapsule(C->GetScaledCapsuleRadius(),C->GetScaledCapsuleHalfHeight()),
        Q,FCollisionResponseParams(C->GetCollisionResponseToChannels()));
    if(!Blocked || !Hit.GetActor() || Hit.GetActor()->GetName()!=TEXT("StaticMeshActor_1600"))
    { Error=TEXT("Bridge collision witness differs from the validated route."); return false; }
    ARecastNavMesh* Recast=nullptr;
    for(TActorIterator<ARecastNavMesh> I(GetWorld());I;++I)
    { if(Recast) { Error=TEXT("Bridge navigation data is ambiguous."); return false; } Recast=*I; }
    auto* Nav=FNavigationSystem::GetCurrent<UNavigationSystemV1>(GetWorld()); FNavLocation Point;
    if(!Nav || !Recast || !Nav->ProjectPointToNavigation(Feet,Point,FVector(50,50,100),Recast) || FVector::Dist(Point.Location,Feet)>50)
    { Error=TEXT("Bridge constraint projection differs from the validated route."); return false; }
    const TArray<FVector> Expected={FVector(5263,-20596,140),FVector(5491,-20691,120),FVector(5491,-20748,140),FVector(4940,-20748,130),FVector(5035,-20520,150)};
    TArray<FVector> Verts;
    if(!Recast->GetPolyVerts(Point.NodeRef,Verts) || Verts.Num()!=Expected.Num())
    { Error=TEXT("Bridge constraint topology differs from the validated route."); return false; }
    for(const FVector& V:Expected) if(!Verts.ContainsByPredicate([&V](const FVector& P){return FVector::Dist(V,P)<=0.1;}))
    { Error=TEXT("Bridge constraint geometry differs from the validated route."); return false; }
    const uint8 Before=Recast->GetPolyAreaID(Point.NodeRef);
    if(Before==Recast->GetAreaID(UNavArea_Null::StaticClass()) || !Recast->SetPolyArea(Point.NodeRef,UNavArea_Null::StaticClass()) ||
        Recast->GetPolyAreaID(Point.NodeRef)!=Recast->GetAreaID(UNavArea_Null::StaticClass()))
    { Error=TEXT("Bridge navigation constraint could not be applied."); return false; }
    bBridgeNavigationValidated=true;
    UE_LOG(LogTemp,Display,TEXT("PARIS_G1_NATIVE_BRIDGE_CONSTRAINT node=%llu vertices=%d area_before=%d area_after=%d hit_cm=%.6f projection_cm=%.6f"),
        uint64(Point.NodeRef),Verts.Num(),Before,Recast->GetPolyAreaID(Point.NodeRef),Hit.Distance,FVector::Dist(Point.Location,Feet));
    return true;
}
