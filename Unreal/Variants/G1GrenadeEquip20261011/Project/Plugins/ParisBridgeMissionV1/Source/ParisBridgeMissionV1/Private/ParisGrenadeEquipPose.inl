// Display-only existing animation source. Actual throw/resource/save state owns life.
int32 NextAvailableSlot(const FEquipmentSession& S,int32 Current,int32 Direction){
    for(int32 I=1;I<=3;++I){const int32 Slot=(Current+Direction*I+6)%3;if(Slot==0||(Slot==1?S.Frag:S.Smoke)>0)return Slot;}return 0;
}
void ClearEquipmentPose(FEquipmentSession& S){
    if(auto* C=S.EquipmentPoseSource.Get()){if(auto* D=Cast<AParisFPUpperBodyV19Actor>(C->GetOwner()))D->SetEquipmentPoseSource(nullptr,NAME_None,0);C->DestroyComponent();}
    S.EquipmentPoseSource.Reset();S.EquipmentPoseTag.Empty();
}
void EquipmentPoseTick(UWorld* W,FEquipmentSession& S){
    auto* P=UGameplayStatics::GetPlayerCharacter(W,0);auto* D=Cast<AParisFPUpperBodyV19Actor>(Display(W,P));
    const bool Throwing=!S.ThrowKind.IsEmpty();
    if(!D||Dead(P)||(!Throwing&&S.SelectedSlot==0)){ClearEquipmentPose(S);return;}
    if(!Throwing&&(S.SelectedSlot==1?S.Frag:S.Smoke)<=0){S.SelectedSlot=0;ClearEquipmentPose(S);HideGun(W,P,false);return;}
    if(!S.EquipmentPoseSource.IsValid()){
        auto* C=NewObject<USkeletalMeshComponent>(D);D->AddInstanceComponent(C);C->SetupAttachment(D->GetRootComponent());
        C->SetSkeletalMesh(P->GetMesh()->GetSkeletalMeshAsset());C->SetCollisionEnabled(ECollisionEnabled::NoCollision);C->SetCanEverAffectNavigation(false);
        C->SetVisibility(false);C->SetHiddenInGame(true);C->SetCastShadow(false);C->SetForcedLOD(1);C->VisibilityBasedAnimTickOption=EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
        C->RegisterComponent();S.EquipmentPoseSource=C;
    }
    const FString Stage=!Throwing?TEXT("Ready"):S.ThrowStage;
    if(S.EquipmentPoseTag!=Stage){
        const FString Suffix=Stage==TEXT("Ready")||Stage==TEXT("Hold")?TEXT("Loop"):Stage==TEXT("Start")?TEXT("Start"):Stage==TEXT("Cancel")?TEXT("Cancel"):TEXT("Far");
        const FString Path=TEXT("/Game/RifleAnimsetPro/Animations/InPlace/Rifle_Grenade_Throw_")+Suffix+TEXT(".Rifle_Grenade_Throw_")+Suffix;
        auto* Clip=LoadObject<UAnimSequence>(nullptr,*Path);
        checkf(Clip&&Clip->GetSkeleton()->IsCompatibleMesh(P->GetMesh()->GetSkeletalMeshAsset()),TEXT("Compatible cooked grenade display clip required"));
        S.EquipmentPoseSource->PlayAnimation(Clip,Suffix==TEXT("Loop"));
        const double ExteriorHeight=2*FMath::Max(GrenadeMesh(W,TEXT("Frag"))->GetBounds().BoxExtent.GetMax(),GrenadeMesh(W,TEXT("Smoke"))->GetBounds().BoxExtent.GetMax());
        D->SetEquipmentPoseSource(S.EquipmentPoseSource.Get(),FName(*(TEXT("Grenade")+Stage)),ExteriorHeight);
        S.EquipmentPoseTag=Stage;Event(W,TEXT("equipment_pose"),Path);
    }
}
void MountGrenade(UWorld* W,AActor* A){
    auto* P=UGameplayStatics::GetPlayerCharacter(W,0);auto* D=Display(W,P);auto* Pose=D?Cast<UPoseableMeshComponent>(Obj(D,TEXT("Pose"))):nullptr;
    if(!A||!Pose)return;
    const FTransform Hand=Pose->GetSocketTransform(TEXT("hand_r"));
    const FVector Palm=Pose->GetSocketLocation(TEXT("middle_01_r"));
    const FVector Tips=(Pose->GetSocketLocation(TEXT("middle_03_r"))+Pose->GetSocketLocation(TEXT("ring_03_r")))*.5;
    const FVector Up=(Pose->GetSocketLocation(TEXT("index_01_r"))-Pose->GetSocketLocation(TEXT("pinky_01_r"))).GetSafeNormal();
    FVector Facing=FVector::CrossProduct(Palm-Hand.GetLocation(),Up).GetSafeNormal();if(FVector::DotProduct(Facing,Tips-Palm)<0)Facing=-Facing;
    auto* Exterior=A->FindComponentByClass<UStaticMeshComponent>();if(!Exterior||!Exterior->GetStaticMesh())return;
    const auto Extent=Exterior->GetStaticMesh()->GetBounds().BoxExtent;
    const double Radius=FMath::Max(Extent.X,Extent.Y);
    const FVector PalmPlane=(Pose->GetSocketLocation(TEXT("index_01_r"))+Palm+Pose->GetSocketLocation(TEXT("ring_01_r"))+Pose->GetSocketLocation(TEXT("pinky_01_r")))*.25;
    const FVector Center=PalmPlane+Facing*Radius;
    A->SetActorRelativeLocation(Hand.InverseTransformPosition(Center));
    if(!Up.IsNearlyZero()&&!Facing.IsNearlyZero())A->SetActorRelativeRotation(Hand.InverseTransformRotation(FRotationMatrix::MakeFromZX(Up,Facing).ToQuat()));
}
