namespace ParisPronePrediction
{
TWeakObjectPtr<ACharacter> Player;
bool Blocked=false;
}
// Read-only witness for the finite integration observer, not a pose override.
bool ParisProneFutureBlocked(const ACharacter* Player)
{ return ParisPronePrediction::Player.Get()==Player && ParisPronePrediction::Blocked; }

void AParisBridgePlayerController::PostProcessInput(const float DeltaTime,const bool bGamePaused)
{
    Super::PostProcessInput(DeltaTime,bGamePaused);
    auto* P=Cast<ACharacter>(GetPawn());
    ParisPronePrediction::Player=P;ParisPronePrediction::Blocked=false;
    if(!P || bGamePaused || !P->ActorHasTag(TEXT("G1_Player")) || Number(P,TEXT("DesiredPosture"))!=2 ||
       !P->bIsCrouched || !P->GetCharacterMovement()->IsMovingOnGround()) return;
    const FVector Input=P->GetPendingMovementInputVector();
    if(Input.SizeSquared()<=.01) return;
    const FVector Feet=P->GetNavAgentLocation(),Forward=P->GetActorForwardVector();
    const FVector Future=Feet+Input.GetSafeNormal()*60*FMath::Max(.1,double(DeltaTime));
    FCollisionQueryParams Q(SCENE_QUERY_STAT(ParisProneFuture),false,P);FHitResult H;
    bool Clear=!GetWorld()->SweepSingleByChannel(H,Feet+FVector(0,0,30),Future+FVector(0,0,30),P->GetActorQuat(),
        ECC_Visibility,FCollisionShape::MakeBox(FVector(130,55,28)),Q);
    for(double Offset:{-120.,0.,110.})
    {
        const FVector Point=Future+Forward*Offset;FHitResult Floor;
        const bool Hit=GetWorld()->LineTraceSingleByChannel(Floor,Point+FVector(0,0,40),Point-FVector(0,0,30),ECC_Visibility,Q);
        Clear&=Hit && Floor.ImpactNormal.Z>=.97 && FMath::Abs(Floor.ImpactPoint.Z-Future.Z)<=10;
    }
    if(!Clear)
    {
        ParisPronePrediction::Blocked=true;
        P->ConsumeMovementInputVector();P->GetCharacterMovement()->StopMovementImmediately();
        if(auto* M=AParisBridgeMission::Find(this)) M->Feedback=TEXT("Prone path blocked. S backs away; Z stands up.");
    }
}
