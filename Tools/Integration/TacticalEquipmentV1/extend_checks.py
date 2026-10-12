"""Add bounded site diagnostics and fresh-process equipment restore checks."""
from pathlib import Path
from prepare import OUT
import shutil

here=Path(__file__).parent
world=here/'ParisEquipmentWorld.inl'
s=world.read_bytes()
begin=s.index(b'bool Site(UWorld* W,')
end=s.index(b'void SiteVisuals',begin)
site=r'''FString SiteFailure;
bool Site(UWorld* W,FVector XY,FVector& Out){
    SiteFailure.Empty();FCollisionQueryParams Q(SCENE_QUERY_STAT(ParisEquipmentSite),true);for(auto* C:Combatants(W))Q.AddIgnoredActor(C);IgnoreProps(W,Q);FHitResult Hit;
    if(!W->LineTraceSingleByChannel(Hit,FVector(XY.X,XY.Y,500),FVector(XY.X,XY.Y,-300),ECC_Visibility,Q)||Hit.ImpactNormal.Z<.7){SiteFailure=TEXT("ground/normal");return false;}
    Out=Hit.ImpactPoint;auto* Nav=FNavigationSystem::GetCurrent<UNavigationSystemV1>(W);FNavLocation Projected;
    if(!Nav||!Nav->ProjectPointToNavigation(Out,Projected,FVector(35,35,120))||FVector::Dist2D(Out,Projected.Location)>35){SiteFailure=FString::Printf(TEXT("nav_projection floor=%s actor=%s"),*Out.ToString(),*GetNameSafe(Hit.GetActor()));return false;}
    auto* P=UGameplayStatics::GetPlayerCharacter(W,0);const auto* Capsule=P->GetCapsuleComponent();
    TArray<FOverlapResult> Overlaps;W->OverlapMultiByChannel(Overlaps,Out+FVector(0,0,Capsule->GetScaledCapsuleHalfHeight()+1),FQuat::Identity,ECC_Pawn,FCollisionShape::MakeCapsule(Capsule->GetScaledCapsuleRadius(),Capsule->GetScaledCapsuleHalfHeight()),Q);
    for(const auto& Overlap:Overlaps)if(Overlap.bBlockingHit){SiteFailure=FString::Printf(TEXT("standing_capsule floor=%s actor=%s component=%s"),*Out.ToString(),*GetNameSafe(Overlap.GetActor()),*GetNameSafe(Overlap.GetComponent()));return false;}
    auto* Path=Nav->FindPathToLocationSynchronously(W,P->GetActorLocation(),Out,P);if(!Path||!Path->IsValid()||Path->IsPartial()){SiteFailure=FString::Printf(TEXT("full_path floor=%s nav=%s start=%s"),*Out.ToString(),*Projected.Location.ToString(),*P->GetActorLocation().ToString());return false;}return true;
}
'''.replace('\n','\r\n').encode()
s=s[:begin]+site+s[end:]
s=s.replace(b'FString::FromInt(I));return false;',b'FString::FromInt(I)+TEXT(" ")+SiteFailure);return false;')
# Check whole route segments, not only path nodes, for hazard avoidance.
s=s.replace(b'for(const auto& V:Path->PathPoints)if(FVector::Dist2D(V,Danger)<FVector::Dist2D(C->GetActorLocation(),Danger)-20)Safe=false;',b'for(int32 I=1;I<Path->PathPoints.Num();++I){const FVector A=Path->PathPoints[I-1],B=Path->PathPoints[I],AB=(B-A)*FVector(1,1,0);const double U=FMath::Clamp(FVector::DotProduct((Danger-A)*FVector(1,1,0),AB)/FMath::Max(1.,AB.SizeSquared()),0.,1.);if(FVector::Dist2D(A+AB*U,Danger)<FVector::Dist2D(C->GetActorLocation(),Danger)-20)Safe=false;}')
world.write_bytes(s)
core=here/'ParisTacticalEquipment.cpp';s=core.read_bytes()
s=s.replace(b'Pass?TEXT("pass_native_throw_early_gate_requires_image_review"):TEXT("failed")',b'Pass?FString(TEXT("pass_native_"))+CheckMode:FString(TEXT("failed_"))+CheckMode')
s=s.replace(b'M->Phase!=TEXT("Preparing")&&M->Phase!=TEXT("Error")&&!SetupSites(W,S)',b'CheckMode!=TEXT("survey")&&M->Phase!=TEXT("Preparing")&&M->Phase!=TEXT("Error")&&!SetupSites(W,S)')
core.write_bytes(s)
checks=here/'ParisEquipmentChecks.inl';s=checks.read_bytes()
needle=b'    if(CheckMode==TEXT("sites"))'
extra=r'''    if(CheckMode==TEXT("survey")){if(M->Phase!=TEXT("Ready"))return;TArray<TSharedPtr<FJsonValue>> Rows;
        const FVector Points[]={FVector(6487.5,-20837.5,0),FVector(7637.5,-20487.5,0),FVector(1612.5,-21012.5,0),FVector(6062.5,-20462.5,0),FVector(1912.5,-20662.5,0),FVector(5837.5,-20237.5,0),FVector(7087.5,-20287.5,0),FVector(6612.5,-20662.5,0),FVector(7387.5,-19937.5,0),FVector(7738.631,-21337.367,0),FVector(1812.5,-21162.5,0),FVector(6137.5,-20137.5,0),FVector(6637.5,-20137.5,0),FVector(7387.5,-20787.5,0)};
        for(const auto& Point:Points){FVector Feet;const bool Good=Site(W,Point,Feet);auto R=MakeShared<FJsonObject>();R->SetStringField(TEXT("xy"),Point.ToString());R->SetStringField(TEXT("feet"),Feet.ToString());R->SetBoolField(TEXT("pass"),Good);R->SetStringField(TEXT("reason"),SiteFailure);Rows.Add(MakeShared<FJsonValueObject>(R));}
        auto O=MakeShared<FJsonObject>();O->SetArrayField(TEXT("sites"),Rows);FFileHelper::SaveStringToFile(JsonText(O),*(CheckOut/TEXT("SITE_SURVEY.json")),FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);FinishCheck(W,true,TEXT("Bounded read-only site survey; no gameplay site adopted"));return;}
    if(CheckMode==TEXT("restore_equipment")||CheckMode==TEXT("restore_legacy")){
        if(CheckStep==0){if(M->Phase!=TEXT("Ready"))return;auto* D=Display(W,P);if(!D||!Flag(D,TEXT("Initialized")))return;CheckStep=80;CheckClock=0;Tap(PC,EKeys::F9);return;}
        if(CheckStep==80&&M->Phase==TEXT("Won")){if(!Expect(W,M->SaveSerial>=1&&M->LivingDefenders==0&&M->CheckpointUnlocked()&&S.Restored,TEXT("fresh_process_original_loader_restored")))return;
            const bool Legacy=CheckMode==TEXT("restore_legacy");if(!Expect(W,Legacy?(S.Frag==0&&S.Smoke==0&&S.Grant==0):(S.Frag==1&&S.Smoke==1&&S.Grant==16&&S.Traps[0].State==TEXT("Disarmed")&&S.Supplies[0].Remaining==0&&S.Balls.Num()==1&&S.Clouds.Num()==1),TEXT("finite_inventory_and_active_effects_restore")))return;
            if(!Legacy){if(!Expect(W,S.Balls[0].Fuse<3&&S.Balls[0].Fuse>2&&S.Clouds[0].Life<12&&S.Clouds[0].Life>10,TEXT("remaining_fuse_and_cloud_time_not_reset")))return;Supply(W,S,TEXT("Supply1"));if(!Expect(W,S.Grant==16&&Num(P,TEXT("ReserveAmmo"))==26,TEXT("spent_box_cannot_duplicate_after_load")))return;}
            Picture(TEXT("restored.png"));CheckStep=81;CheckClock=0;return;}
        if(CheckStep==81&&CheckClock>3.6){bool Stopped=true;for(auto* C:Combatants(W))if(Num(C,TEXT("TeamId"))==1){auto* I=C->GetMesh()->GetSingleNodeInstance();Stopped=Stopped&&Dead(C)&&I&&!I->IsPlaying();}if(!Expect(W,Stopped&&S.Balls.IsEmpty()&&S.Clouds.Num()<2&&Num(P,TEXT("Health"))>0,TEXT("terminal_corpses_and_single_expiration_after_three_seconds")))return;FinishCheck(W,true,TEXT("Real F9/new-world loader, finite inventory, no refill/timer reset, three-second terminal corpse check"));return;}
        if(CheckClock>20)FinishCheck(W,false,TEXT("restore_timeout"));return;
    }
'''.replace('\n','\r\n').encode()
assert s.count(needle)==1;s=s.replace(needle,extra+needle)
checks.write_bytes(s)

# The revision being compiled stays immutable. Refresh only a new child.
project=OUT/'candidate_full_v7/Project/Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private'
assert not (OUT/'candidate_full_v7/build-game.json').exists()
for name in ['ParisTacticalEquipment.h','ParisTacticalEquipment.cpp','ParisEquipmentState.h','ParisEquipmentSave.cpp','ParisEquipmentSightBridge.h','ParisEquipmentWorld.inl','ParisEquipmentAudio.inl','ParisEquipmentChecks.inl']:
    shutil.copyfile(here/name,project/name)
print('v7 authored: strict site diagnostics, segment-safe evade, real restore checks')
