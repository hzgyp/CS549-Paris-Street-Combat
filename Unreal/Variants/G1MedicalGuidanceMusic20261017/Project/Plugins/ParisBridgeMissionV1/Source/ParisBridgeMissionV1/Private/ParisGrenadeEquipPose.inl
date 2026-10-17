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
    D->SetSmokeGripContact((Throwing?S.ThrowKind:(S.SelectedSlot==2?TEXT("Smoke"):TEXT("Frag")))==TEXT("Smoke")&&(!Throwing||!S.ThrowCommitted));
    D->SetFragGripContact((Throwing?S.ThrowKind:(S.SelectedSlot==2?TEXT("Smoke"):TEXT("Frag")))==TEXT("Frag")&&(!Throwing||!S.ThrowCommitted));
    if(!S.EquipmentPoseSource.IsValid()){
        auto* C=NewObject<USkeletalMeshComponent>(D);D->AddInstanceComponent(C);C->SetupAttachment(D->GetRootComponent());
        C->SetSkeletalMesh(P->GetMesh()->GetSkeletalMeshAsset());C->SetCollisionEnabled(ECollisionEnabled::NoCollision);C->SetCanEverAffectNavigation(false);
        C->SetVisibility(false);C->SetHiddenInGame(true);C->SetCastShadow(false);C->SetForcedLOD(1);C->VisibilityBasedAnimTickOption=EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
        C->RegisterComponent();S.EquipmentPoseSource=C;
    }
    const FString Stage=!Throwing?TEXT("Ready"):S.ThrowStage;
    if(S.EquipmentPoseTag!=Stage){
        // An equipped grenade is already held. FP preparation/cancellation
        // must not replay the third-person rifle-to-grenade transfer. The real
        // body's Start/Cancel and the original gameplay clocks remain unchanged.
        const bool Loop=Stage!=TEXT("Release");
        const FString Path=ParisActionBindings::GrenadeClip(FName(*Stage),true);
        auto* Clip=LoadObject<UAnimSequence>(nullptr,*Path);
        checkf(Clip&&Clip->GetSkeleton()->IsCompatibleMesh(P->GetMesh()->GetSkeletalMeshAsset()),TEXT("Compatible cooked grenade display clip required"));
        S.EquipmentPoseSource->PlayAnimation(Clip,Loop);
        // The component is created after actor ticking. Evaluate the chosen
        // clip now so first-frame calibration never reads its reference pose.
        S.EquipmentPoseSource->TickAnimation(0.f,false);
        S.EquipmentPoseSource->RefreshBoneTransforms();
        const double ExteriorHeight=2*FMath::Max(GrenadeMesh(W,TEXT("Frag"))->GetBounds().BoxExtent.GetMax(),GrenadeMesh(W,TEXT("Smoke"))->GetBounds().BoxExtent.GetMax());
        D->SetEquipmentPoseSource(S.EquipmentPoseSource.Get(),FName(*(TEXT("Grenade")+Stage)),ExteriorHeight);
        S.EquipmentPoseTag=Stage;Event(W,TEXT("equipment_pose"),Path);
    }
}
USkinnedMeshComponent* GrenadeMountComponent(UWorld* W){
    auto* P=UGameplayStatics::GetPlayerCharacter(W,0);auto* D=Display(W,P);
    if(!P)return nullptr;
    if(auto* Unified=ParisActionBindings::Display(P)){Unified->RefreshUnifiedPresentation();return ParisActionBindings::VisibleBody(P);}
    return D?Cast<USkinnedMeshComponent>(Obj(D,TEXT("Pose"))):nullptr;
}
void MountGrenade(UWorld* W,AActor* A){
    auto* Pose=GrenadeMountComponent(W);
    if(!A||!Pose)return;
    auto* Root=A->GetRootComponent();
    if(Root->GetAttachParent()!=Pose||Root->GetAttachSocketName()!=TEXT("hand_l"))
        A->AttachToComponent(Pose,FAttachmentTransformRules::SnapToTargetNotIncludingScale,TEXT("hand_l"));
    const FTransform Hand=Pose->GetSocketTransform(TEXT("hand_l"));
    const FVector Palm=Pose->GetSocketLocation(TEXT("middle_01_l"));
    const FVector Tips=(Pose->GetSocketLocation(TEXT("middle_03_l"))+Pose->GetSocketLocation(TEXT("ring_03_l")))*.5;
    const FVector Up=(Pose->GetSocketLocation(TEXT("index_01_l"))-Pose->GetSocketLocation(TEXT("pinky_01_l"))).GetSafeNormal();
    FVector Facing=FVector::CrossProduct(Palm-Hand.GetLocation(),Up).GetSafeNormal();if(FVector::DotProduct(Facing,Tips-Palm)<0)Facing=-Facing;
    auto* Exterior=A->FindComponentByClass<UStaticMeshComponent>();if(!Exterior||!Exterior->GetStaticMesh())return;
    const auto Extent=Exterior->GetStaticMesh()->GetBounds().BoxExtent;
    const double Radius=FMath::Max(Extent.X,Extent.Y);
    const FVector PalmPlane=(Pose->GetSocketLocation(TEXT("index_01_l"))+Palm+Pose->GetSocketLocation(TEXT("ring_01_l"))+Pose->GetSocketLocation(TEXT("pinky_01_l")))*.25;
    FVector Center=PalmPlane+Facing*Radius;
    // Each retained exterior has its own measured skin/chord envelope.
    if(GrenadeMeshCaches[1].IsValid()&&Exterior->GetStaticMesh()==GrenadeMeshCaches[1].Get()){
        ParisSmokeGripContact::FFrame Fit;
        if(ParisSmokeGripContact::Frame([&](FName N){return Pose->GetSocketLocation(N);},Fit))Center=Fit.Center;
    }
    if(GrenadeMeshCaches[0].IsValid()&&Exterior->GetStaticMesh()==GrenadeMeshCaches[0].Get()){
        ParisFragGripContact::FFrame Fit;
        if(ParisFragGripContact::Frame([&](FName N){return Pose->GetSocketLocation(N);},Fit))Center=Fit.Center;
    }
    A->SetActorRelativeLocation(Hand.InverseTransformPosition(Center));
    if(!Up.IsNearlyZero()&&!Facing.IsNearlyZero())A->SetActorRelativeRotation(Hand.InverseTransformRotation(FRotationMatrix::MakeFromZX(Up,Facing).ToQuat()));
}
