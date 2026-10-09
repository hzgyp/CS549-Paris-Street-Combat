namespace ParisPlaytestUX
{
bool PutObject(UObject* Target,const TCHAR* Field,UObject* Value)
{
    auto* P=Target?FindFProperty<FObjectPropertyBase>(Target->GetClass(),Field):nullptr;
    if(!P || (Value && !Value->IsA(P->PropertyClass))) return false;
    P->SetObjectPropertyValue_InContainer(Target,Value); return true;
}
}

void AParisBridgeGameMode::StartPlay()
{
    ACharacter* Original=nullptr;
    for(TActorIterator<ACharacter> I(GetWorld());I;++I) if(I->ActorHasTag(TEXT("G1_Player")))
    { checkf(!Original,TEXT("Duplicate G1 player before action integration")); Original=*I; }
    UClass* Actions=LoadClass<ACharacter>(nullptr,TEXT("/Game/ParisCombat/Blueprints/PlayerActionsV1/BP_PCParisPlayerActionsV6.BP_PCParisPlayerActionsV6_C"));
    checkf(Original && Actions && Actions->IsChildOf(Original->GetClass()),TEXT("Exact compatible existing action player is required"));
    checkf(!Original->HasActorBegunPlay(),TEXT("Action integration must precede original BeginPlay"));
    ACharacter* Player=GetWorld()->SpawnActorDeferred<ACharacter>(Actions,Original->GetActorTransform(),nullptr,nullptr,ESpawnActorCollisionHandlingMethod::AlwaysSpawn);
    check(Player); Player->Tags=Original->Tags; Player->AutoPossessPlayer=EAutoReceiveInput::Player0;
    Player->SetActorEnableCollision(false);
    UGameplayStatics::FinishSpawningActor(Player,Original->GetActorTransform());
    checkf(Player->GetMesh()->GetSkeletalMeshAsset()==Original->GetMesh()->GetSkeletalMeshAsset(),TEXT("Source character mesh changed"));
    checkf(Player->GetMesh()->GetNumMaterials()==Original->GetMesh()->GetNumMaterials(),TEXT("Material count changed"));
    for(int32 I=0;I<Original->GetMesh()->GetNumMaterials();++I)
        checkf(Player->GetMesh()->GetMaterial(I)==Original->GetMesh()->GetMaterial(I),TEXT("Source material changed"));
    Player->GetMesh()->SetRelativeTransform(Original->GetMesh()->GetRelativeTransform());
    checkf(FMath::Abs(Player->GetCapsuleComponent()->GetUnscaledCapsuleHalfHeight()-Original->GetCapsuleComponent()->GetUnscaledCapsuleHalfHeight())<.01 &&
           FMath::Abs(Player->GetCapsuleComponent()->GetUnscaledCapsuleRadius()-Original->GetCapsuleComponent()->GetUnscaledCapsuleRadius())<.01,TEXT("Initial action capsule changed"));
    for(const TCHAR* Field:{TEXT("Health"),TEXT("LoadedAmmo"),TEXT("ReserveAmmo"),TEXT("Capacity"),TEXT("TeamId"),TEXT("ShotSequence"),TEXT("ActionID"),TEXT("RestoreGeneration")})
    { const double V=Number(Original,Field); checkf(FMath::IsFinite(V) && SetNumber(Player,Field,V),TEXT("Original resource interface changed")); }
    AActor* Gun=Cast<AActor>(Object(Original,TEXT("WeaponAppearance")));
    checkf(Gun && ParisPlaytestUX::PutObject(Player,TEXT("WeaponAppearance"),Gun),TEXT("Original weapon handoff failed"));
    for(TActorIterator<AActor> I(GetWorld());I;++I) if(*I!=Original && *I!=Player)
    {
        if(Object(*I,TEXT("Combatant"))==Original) check(ParisPlaytestUX::PutObject(*I,TEXT("Combatant"),Player));
        if(Object(*I,TEXT("GripMesh"))==Original->GetMesh()) check(ParisPlaytestUX::PutObject(*I,TEXT("GripMesh"),Player->GetMesh()));
        if(Object(*I,TEXT("SourceMesh"))==Original->GetMesh()) check(ParisPlaytestUX::PutObject(*I,TEXT("SourceMesh"),Player->GetMesh()));
        if(I->GetOwner()==Original) I->SetOwner(Player);
    }
    Gun->AttachToComponent(Player->GetMesh(),FAttachmentTransformRules::KeepRelativeTransform,TEXT("hand_r"));
    if(auto* PC=Cast<APlayerController>(Original->GetController())) PC->Possess(Player);
    Original->Tags.Remove(TEXT("G1_Player")); const FString OldClass=Original->GetClass()->GetPathName();
    Original->Destroy(); Player->SetActorEnableCollision(true);
    UE_LOG(LogTemp,Display,TEXT("PARIS_UX_ACTION_PLAYER old=%s new=%s original_gun=%s mesh_material_resources_exact=1"),*OldClass,*Player->GetClass()->GetPathName(),*Gun->GetPathName());
    Super::StartPlay();
}

bool AParisBridgeMission::CheckpointUnlocked() const
{
    return bRegistrySealed && LivingDefenders==0 && DeathLedger.Contains(TEXT("German1")) &&
        DeathLedger.Contains(TEXT("German2")) && DeathLedger.Contains(TEXT("German3"));
}
bool AParisBridgeMission::InsideCheckpoint() const
{
    if(!CheckpointUnlocked() || Roster.IsEmpty() || !IsValid(Roster[0]) || Flag(Roster[0],TEXT("IsDead"))) return false;
    auto* P=Roster[0].Get(); const FVector Feet=P->GetNavAgentLocation();
    return FVector::Dist2D(Feet,BridgeheadFeet)<=CheckpointRadius && FMath::Abs(Feet.Z-BridgeheadFeet.Z)<=100 && P->GetCharacterMovement()->IsMovingOnGround();
}
void AParisBridgeMission::UpdateCheckpointUI()
{
    if(!CheckpointUnlocked()) { CheckpointPromptVisible=false; return; }
    // Development candidate: a world-space ring at the surveyed G1 ground anchor.
    DrawDebugCircle(GetWorld(),BridgeheadFeet+FVector(0,0,7),CheckpointRadius,64,FColor(145,225,111),false,-1,0,5,FVector(1,0,0),FVector(0,1,0),false);
    const bool Inside=InsideCheckpoint();
    if(!Inside) { CheckpointPromptVisible=false; bCheckpointDismissed=false; }
    else if(!bCheckpointWasInside && !bCheckpointDismissed)
    { CheckpointPromptVisible=true; UE_LOG(LogTemp,Display,TEXT("PARIS_UX_CHECKPOINT_ENTER prompt=1 serial=%d autosave=0"),SaveSerial); }
    bCheckpointWasInside=Inside;
}
bool AParisBridgeMission::RequestCheckpointPrompt()
{
    if(!InsideCheckpoint()) { Feedback=TEXT("Clear all three guards, then enter the green checkpoint circle."); return false; }
    CheckpointPromptVisible=true; bCheckpointDismissed=false; return true;
}
void AParisBridgeMission::DismissCheckpointPrompt()
{
    CheckpointPromptVisible=false; bCheckpointDismissed=true;
    Feedback=TEXT("Checkpoint not saved. Leave and re-enter when ready.");
    UE_LOG(LogTemp,Display,TEXT("PARIS_UX_CHECKPOINT_DECLINED serial=%d"),SaveSerial);
}
bool AParisBridgeMission::ConfirmCheckpoint()
{
    if(!CheckpointPromptVisible || !InsideCheckpoint()) return false;
    TGuardValue<bool> Permit(bConfirmedSaveRequest,true);
    if(!SaveCheckpoint()) return false;
    CheckpointPromptVisible=false; bCheckpointDismissed=true;
    UE_LOG(LogTemp,Display,TEXT("PARIS_UX_CHECKPOINT_CONFIRMED serial=%d"),SaveSerial); return true;
}
