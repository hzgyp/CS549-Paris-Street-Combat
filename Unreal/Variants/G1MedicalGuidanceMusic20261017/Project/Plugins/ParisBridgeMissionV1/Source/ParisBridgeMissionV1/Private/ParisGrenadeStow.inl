// Player observer presentation only. No inventory, throw, collision or save authority.
// Native packages and the first-person/death body are never edited.
void ClearStowedGrenade(FEquipmentSession& S){
    if(S.StowedFrag.IsValid())S.StowedFrag->Destroy();
    S.StowedFrag.Reset();
    if(S.StowBody.IsValid())S.StowBody->ShowMaterialSection(1,1,S.StowSectionWasShown,0);
    S.StowBody.Reset();
}

bool BeltMount(USkinnedMeshComponent* Body,UStaticMesh* Mesh,FTransform& Mount){
    const auto* Asset=Body?Body->GetSkinnedAsset():nullptr;
    if(!Asset||!Mesh)return false;
    const auto& Ref=Asset->GetRefSkeleton();
    const int32 Pelvis=Ref.FindBoneIndex(TEXT("pelvis")),Spine=Ref.FindBoneIndex(TEXT("spine_01"));
    const int32 Left=Ref.FindBoneIndex(TEXT("thigh_l")),Right=Ref.FindBoneIndex(TEXT("thigh_r"));
    const int32 Foot=Ref.FindBoneIndex(TEXT("foot_l")),Toe=Ref.FindBoneIndex(TEXT("ball_l"));
    if(Pelvis<0||Spine<0||Left<0||Right<0||Foot<0||Toe<0)return false;
    const auto& Local=Ref.GetRefBonePose();TArray<FTransform> Component;Component.SetNum(Local.Num());
    for(int32 I=0;I<Local.Num();++I){const int32 Parent=Ref.GetParentIndex(I);Component[I]=Parent>=0?Local[I]*Component[Parent]:Local[I];}
    const FVector Origin=Component[Pelvis].GetLocation();
    const FVector SpineOffset=Component[Spine].GetLocation()-Origin;
    const FVector Up=SpineOffset.GetSafeNormal();
    const FVector Across=FVector::VectorPlaneProject(Component[Left].GetLocation()-Component[Right].GetLocation(),Up).GetSafeNormal();
    FVector Forward=FVector::VectorPlaneProject(Component[Toe].GetLocation()-Component[Foot].GetLocation(),Up);
    Forward=(Forward-Across*FVector::DotProduct(Forward,Across)).GetSafeNormal();
    if(Up.IsNearlyZero()||Across.IsNearlyZero()||Forward.IsNearlyZero())return false;
    const auto Bounds=Mesh->GetBounds();
    const double HalfHip=FVector::Distance(Component[Left].GetLocation(),Component[Right].GetLocation())*.5;
    // v2 front/profile frames locate the belt above the pelvis joint and show
    // the initial low mount occluded by the hip bag. Raise to this rig belt
    // and allow exterior clearance; retain intact prop dimensions. The lever/top
    // sits at the belt and the intact original-sized body hangs below it.
    // Axes/hip width come from this rig, not FP hand offsets or another soldier.
    const FVector Belt=Origin+Up*FMath::Clamp(SpineOffset.Size()*1.4,14.,18.)
        +Across*(HalfHip+Bounds.BoxExtent.Y+8.)+Forward*(Bounds.BoxExtent.X+12.);
    const FQuat Rotation=FRotationMatrix::MakeFromXZ(Forward,Up).ToQuat();
    const FVector Center=Belt-Up*(Bounds.BoxExtent.Z-1.2);
    const FTransform InBody(Rotation,Center-Rotation.RotateVector(Bounds.Origin));
    Mount=InBody.GetRelativeTransform(Component[Pelvis]);
    return true;
}

void StowedGrenadeTick(UWorld* W,AParisBridgeMission* M,FEquipmentSession& S){
    auto* P=UGameplayStatics::GetPlayerCharacter(W,0);
    auto* D=Cast<AParisFirstPersonApprovedActor>(Display(W,P));
    auto* Body=D&&D->UnifiedObserver()?D->UnifiedVisibleBody():nullptr;
    // The inspected native grenade is material slot 1, section 1 of LOD0;
    // UnifiedBodyDisplay is already forced to LOD0. Never mask another rig.
    if(Dead(P)||!M||(!M->AllowsPlay()&&M->Phase!=TEXT("Won"))||!Body||
       !Body->GetSkinnedAsset()||Body->GetSkinnedAsset()->GetPathName()!=TEXT("/Game/ParisCombat/Characters/Adaptation/Meshes/SK_WWII_US_Paratrooper_simple_UE582_v1.SK_WWII_US_Paratrooper_simple_UE582_v1")||
       !Body->GetMaterial(1)||Body->GetMaterial(1)->GetPathName()!=TEXT("/Game/USParatrooper/Materials/MI_US_WWII_Grenade.MI_US_WWII_Grenade")){
        ClearStowedGrenade(S);return;
    }
    if(S.StowBody.Get()!=Body||!S.StowedFrag.IsValid()){
        ClearStowedGrenade(S);
        auto* Mesh=GrenadeMesh(W,TEXT("Frag"));FTransform Mount;
        if(!BeltMount(Body,Mesh,Mount))return; // Preserve the original display if fitting is unavailable.
        auto* A=Prop(W,TEXT("Frag"),P->GetActorLocation());
        A->SetOwner(P);A->Tags.Add(TEXT("ParisObserverStowedGrenade"));
        A->AttachToComponent(Body,FAttachmentTransformRules::KeepRelativeTransform,TEXT("pelvis"));
        A->SetActorRelativeTransform(Mount);
        S.StowedFrag=A;S.StowBody=Body;S.StowSectionWasShown=Body->IsMaterialSectionShown(1,0);
        Body->ShowMaterialSection(1,1,false,0);
    }
    // The body accessory is no longer a permanent, uncounted extra grenade.
    const bool Show=S.StowSectionWasShown&&S.Frag>0&&S.SelectedSlot!=1&&S.ThrowKind!=TEXT("Frag");
    if(S.StowedFrag.IsValid())S.StowedFrag->SetActorHiddenInGame(!Show);
}
