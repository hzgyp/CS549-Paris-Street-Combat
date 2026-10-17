// Smoke only. Mesh origin differs from the center of the measured exterior box.
FVector SmokeCenterOffset(const FVector& Scale){const auto& V=ParisSmokePresentation::BodyCenter;return FVector(V[0],V[1],V[2])*Scale;}
void ReadSmokeBody(UBoxComponent* Body,FSmokePose& Pose){
    if(!Body)return;
    Pose.Rotation=Body->GetComponentQuat();
    Pose.Position=Body->GetComponentLocation()-Pose.Rotation.RotateVector(SmokeCenterOffset(Pose.Scale));
    Pose.Linear=Body->GetPhysicsLinearVelocity();
    // Keep the existing projectile save admission speed bound, including a fall
    // outside the map. Ordinary contact/settling does not reach this ceiling.
    if(Pose.Linear.Size()>4999.){Pose.Linear=Pose.Linear.GetClampedToMaxSize(4999.);Body->SetPhysicsLinearVelocity(Pose.Linear);}
    Pose.Angular=Body->GetPhysicsAngularVelocityInDegrees();
    Pose.Sleeping=!Body->IsAnyRigidBodyAwake();Pose.Valid=true;
}
UBoxComponent* CreateSmokeBody(AActor* Actor,FSmokePose& Pose,FVector FallbackVelocity,bool Settled=false){
    check(Actor&&Actor->GetRootComponent());
    auto* MeshRoot=Actor->GetRootComponent();
    // Old saves have no orientation. Keep their age/life, initialize an awake body
    // without artificial spin for an already active cloud and let contact settle it.
    if(!Pose.Valid){Pose.Position=Actor->GetActorLocation();Pose.Rotation=Actor->GetActorQuat();Pose.Scale=Actor->GetActorScale3D();Pose.Linear=FallbackVelocity;Pose.Angular=Settled?FVector::ZeroVector:Pose.Rotation.RotateVector(FVector(30,130,90));Pose.Sleeping=false;Pose.Valid=true;}
    auto* Body=NewObject<UBoxComponent>(Actor);Actor->AddInstanceComponent(Body);
    Body->SetMobility(EComponentMobility::Movable);
    const auto& Half=ParisSmokePresentation::BodyHalf;
    Body->SetBoxExtent(FVector(Half[0],Half[1],Half[2])*Pose.Scale,false);
    Body->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);Body->SetCollisionObjectType(ECC_PhysicsBody);
    Body->SetCollisionResponseToAllChannels(ECR_Ignore);Body->SetCollisionResponseToChannel(ECC_WorldStatic,ECR_Block);Body->SetCollisionResponseToChannel(ECC_WorldDynamic,ECR_Block);
    Body->SetCanEverAffectNavigation(false);Body->SetGenerateOverlapEvents(false);Body->BodyInstance.bUseCCD=true;
    Body->SetWorldTransform(FTransform(Pose.Rotation,Pose.Position+Pose.Rotation.RotateVector(SmokeCenterOffset(Pose.Scale))));
    Actor->SetRootComponent(Body);MeshRoot->AttachToComponent(Body,FAttachmentTransformRules::KeepWorldTransform);
    MeshRoot->SetRelativeTransform(FTransform(FQuat::Identity,-SmokeCenterOffset(Pose.Scale),Pose.Scale));
    auto* Contact=NewObject<UPhysicalMaterial>(Body);Contact->Friction=.65f;Contact->Restitution=.2f;Body->SetPhysMaterialOverride(Contact);
    Body->RegisterComponent();Body->SetMassOverrideInKg(NAME_None,.5f,true);Body->SetLinearDamping(.2f);Body->SetAngularDamping(2.5f);
    Body->SetEnableGravity(true);Body->SetSimulatePhysics(true);Body->SetPhysicsMaxAngularVelocityInDegrees(600.f);
    Body->SetPhysicsLinearVelocity(Pose.Linear);Body->SetPhysicsAngularVelocityInDegrees(Pose.Angular);
    if(Pose.Sleeping)Body->PutRigidBodyToSleep();
    return Body;
}
FVector SmokeOutlet(const FSmokePose& Pose){return Pose.Position+Pose.Rotation.RotateVector(FVector(0,0,ParisSmokePresentation::OutletZ)*Pose.Scale);}
