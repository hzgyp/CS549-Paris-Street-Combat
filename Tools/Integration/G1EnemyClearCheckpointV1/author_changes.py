"""Apply the documented admission change exactly once to the new snapshot."""
from prepare import SOURCE,author
def replace(p,old,new):
 s=p.read_text(encoding='utf-8-sig');assert s.count(old)==1,(p,old[:100]);p.write_text(s.replace(old,new),encoding='utf-8')
def main():
 b=SOURCE/'Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private'
 p=b/'ParisBridgeMission.cpp'
 replace(p,'''    if(Phase==TEXT("Clearing") && LivingDefenders==0 && DeathLedger.Contains(TEXT("German1")) && DeathLedger.Contains(TEXT("German2")) && DeathLedger.Contains(TEXT("German3"))) SetPhase(TEXT("Occupying"));
    if(Phase==TEXT("Occupying") && FVector::Dist2D(Feet,BridgeheadFeet)<=OccupyRadius && FMath::Abs(Feet.Z-BridgeheadFeet.Z)<=100 && P->GetCharacterMovement()->IsMovingOnGround())
    {
        // Keep the original squad route active until its actual arrival gate completes.
        // Restored terminal saves never enter this fresh-mission transition.
        if(!bBridgeTransitComplete) Feedback=TEXT("G1 guards cleared. Waiting for the squad to finish crossing.");
        else
        { SetPhase(TEXT("Won")); Feedback=TEXT("G1 secured. Enter the gold checkpoint circle to save."); GateBrains(false);
          if(auto* PC=UGameplayStatics::GetPlayerController(this,0)) { PC->ResetIgnoreMoveInput(); PC->ResetIgnoreLookInput(); } }
    }''','''    // User-selected rule: clearing this registered enemy group is the only objective gate.
    // A missed far-bank marker or unfinished squad transit must not strand a cleared checkpoint.
    if(CheckpointUnlocked())
    {
        SetPhase(TEXT("Won")); Feedback=TEXT("All G1 guards eliminated. Enter the gold checkpoint circle to save."); GateBrains(false);
        if(auto* PC=UGameplayStatics::GetPlayerController(this,0)) { PC->ResetIgnoreMoveInput(); PC->ResetIgnoreLookInput(); }
    }''')
 replace(p,'''    if(!bConfirmedSaveRequest || !CheckpointUnlocked() || !InsideCheckpoint() || Phase!=TEXT("Won"))
    { Feedback=TEXT("Enter the secured checkpoint circle and confirm with E."); return false; }
    if(!Roster.IsEmpty() && (Roster[0]->bIsCrouched || Number(Roster[0],TEXT("DesiredPosture"))!=0))
    { Feedback=TEXT("Stand up before saving this checkpoint."); return false; }
    FString Error;
    if(!IsSafeBoundary(Error) || (AllowsPlay() && SafeSeconds<2)) { Feedback=Error.IsEmpty()?TEXT("Wait two seconds at a safe settled boundary."):Error; return false; }
''','''    if(!bConfirmedSaveRequest || bTravelPending || !CheckpointUnlocked() || !InsideCheckpoint())
    { Feedback=TEXT("Eliminate all G1 guards, enter the gold circle and confirm with E."); return false; }
    // Snapshot/readback validation protects the transaction; posture, movement and squad
    // readiness are no longer gameplay admission requirements for a cleared checkpoint.
    FString Error;
''')
 replace(p,'TEXT("Stop moving and stand up. ESC cancels this request.")','TEXT("Eliminate all G1 guards. ESC cancels this request.")')
 p=b/'ParisMissionInteraction.cpp'
 replace(p,'''static double ParisInteractionPosture(const ACharacter* Player) {
    const auto* P=Player?FindFProperty<FNumericProperty>(Player->GetClass(),TEXT("DesiredPosture")):nullptr;
    if(!P)return -1;
    const void* V=P->ContainerPtrToValuePtr<void>(Player);
    return P->IsFloatingPoint()?P->GetFloatingPointPropertyValue(V):double(P->GetSignedIntPropertyValue(V));
}

''','')
 replace(p,'''    if(Phase!=TEXT("Won"))return TEXT("Finish securing G1 before saving.");
    if(!Roster.IsEmpty() && (Roster[0]->bIsCrouched || ParisInteractionPosture(Roster[0])!=0))
        return TEXT("Stand up before saving this checkpoint.");
    FString Reason;
    if(!IsSafeBoundary(Reason))return Reason;
''','''    if(bTravelPending)return TEXT("Wait for the mission to finish loading.");
''')
 print('Applied clear-only victory/save admission; transaction and source schema unchanged')
if __name__=='__main__':main()
