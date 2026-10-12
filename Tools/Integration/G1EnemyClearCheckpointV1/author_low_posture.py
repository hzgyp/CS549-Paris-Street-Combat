"""Preserve the saved foot position with the existing standing lifecycle restore."""
from prepare import SOURCE
def main():
 p=SOURCE/'Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisBridgeMission.cpp'
 text=p.read_text(encoding='utf-8-sig')
 old='    FString Payload=CaptureSnapshot(Serial);\n    if(!ValidateSnapshot(Payload,Error))'
 assert text.count(old)==1
 new='''    FString Payload=CaptureSnapshot(Serial);
    // The original lifecycle loader restores a standing capsule, not an interrupted pose.
    // Convert only the player's saved centre so its feet remain at the captured height.
    // No new schema field, action/pose mutation or resource adjustment is needed.
    ACharacter* SavePlayer=Roster[0];
    const ACharacter* StandingPlayer=SavePlayer->GetClass()->GetDefaultObject<ACharacter>();
    const double StandingHalf=StandingPlayer->GetCapsuleComponent()->GetUnscaledCapsuleHalfHeight()*SavePlayer->GetCapsuleComponent()->GetShapeScale();
    const double SavedHalf=SavePlayer->GetCapsuleComponent()->GetScaledCapsuleHalfHeight();
    if(!FMath::IsNearlyEqual(StandingHalf,SavedHalf,.001))
    {
        auto SaveObject=Parse(Payload);auto SaveActor=SaveObject->GetArrayField(TEXT("actors"))[0]->AsObject();
        FVector SaveLocation;GetVector(SaveActor,TEXT("location"),SaveLocation);
        SaveLocation.Z+=StandingHalf-SavedHalf;SaveActor->SetArrayField(TEXT("location"),Vector(SaveLocation));
        Payload=Json(SaveObject);
        UE_LOG(LogTemp,Display,TEXT("PARIS_CHECKPOINT_FOOT_POSITION saved_half=%.6f standing_half=%.6f delta_z=%.6f"),SavedHalf,StandingHalf,StandingHalf-SavedHalf);
    }
    if(!ValidateSnapshot(Payload,Error))'''
 p.write_text(text.replace(old,new),encoding='utf-8')
 print('Low-posture journal centre normalized to original standing capsule; no new field/pose/resource change')
if __name__=='__main__':main()
