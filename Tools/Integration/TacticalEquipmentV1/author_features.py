"""Author additive equipment adapters while retaining cooked reflected layouts."""
from prepare import OUT,ROOT,write,sha,read
from pathlib import Path
import argparse,shutil
ap=argparse.ArgumentParser();ap.add_argument('revision');a=ap.parse_args()
project=OUT/a.revision/'Project';base=project/'Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1';here=Path(__file__).parent
for name in ['ParisTacticalEquipment.h','ParisTacticalEquipment.cpp','ParisEquipmentState.h','ParisEquipmentSave.cpp','ParisEquipmentSightBridge.h','ParisEquipmentWorld.inl','ParisEquipmentAudio.inl','ParisEquipmentChecks.inl']:
    shutil.copyfile(here/name,base/'Private'/name)
def change(path, replacements, prepend=b''):
    p=base/path;old=p.read_bytes();new=prepend+old
    for source,target in replacements:
        source=source.encode();target=target.encode();assert new.count(source)==1,(path,source);new=new.replace(source,target)
    p.write_bytes(new)
change('Private/ParisBridgeMission.cpp',[
 ('    return Json(O);\r\n}\r\n\r\nbool AParisBridgeMission::ValidateSnapshot','    ParisTacticalEquipment::CaptureEquipment(GetWorld(),O);\r\n    return Json(O);\r\n}\r\n\r\nbool AParisBridgeMission::ValidateSnapshot'),
 ('    int32 Germans=0;','    if(!ParisTacticalEquipment::ValidateEquipment(O,Error))return false;\r\n    int32 Germans=0;'),
 ('Total!=InitialResources[I].Y+InitialResources[I].Z+InitialShots[I]','Total!=InitialResources[I].Y+InitialResources[I].Z+InitialShots[I]+ParisTacticalEquipment::ValidatedGrant(O,I)'),
 ('    VerifiedRestoreState=CaptureSnapshot','    ParisTacticalEquipment::RestoreEquipment(GetWorld(),O);\r\n    VerifiedRestoreState=CaptureSnapshot'),
 ('PlayerOwner->LineOfSightTo(*I)) CachedEnemyLocations','PlayerOwner->LineOfSightTo(*I) && !ParisTacticalEquipment::Occluded(GetWorld(),Eye,I->GetActorLocation())) CachedEnemyLocations'),
 ('    for(const auto& V:CachedEnemyLocations) Dot(V,Danger,2.5);','    FVector EquipmentEye;FRotator EquipmentView;PlayerOwner->GetPlayerViewPoint(EquipmentEye,EquipmentView);\r\n    for(const auto& V:CachedEnemyLocations) if(!ParisTacticalEquipment::Occluded(GetWorld(),EquipmentEye,V)) Dot(V,Danger,2.5);'),
 ('    if(M->CheckpointPromptVisible)\r\n    {\r\n        Halo(960,822',
  '    if(Player && !M->CheckpointDialogVisible()) {\r\n        Text(ParisTacticalEquipment::HudInventory(GetWorld()),960,1018,13,Ivory,true,30);\r\n        const FString EquipmentHint=ParisTacticalEquipment::HudInteraction(GetWorld());\r\n        if(!EquipmentHint.IsEmpty() && !M->CheckpointPromptVisible) {Halo(960,814,310,44,.55);Text(EquipmentHint,960,796,15,Brass,true);const double Progress=ParisTacticalEquipment::HudProgress(GetWorld());if(Progress>0){Rect(820,832,280,4,Ink);Rect(820,832,280*Progress,4,Brass);}}\r\n    }\r\n    if(M->CheckpointPromptVisible)\r\n    {\r\n        Halo(960,822')
],b'#include "ParisTacticalEquipment.h"\r\n#include "ParisEquipmentState.h"\r\n')
change('Private/ParisMissionInteraction.cpp',[
 ('    if(Params.Event==IE_Pressed && Params.Key==EKeys::E) {M->InteractCheckpoint();return true;}',
  '    if(!InteractionMenuVisible() && !M->CheckpointDialogVisible() && ParisTacticalEquipment::Input(this,Params))return true;\r\n    if(Params.Event==IE_Pressed && Params.Key==EKeys::E) {M->InteractCheckpoint();return true;}')
],b'#include "ParisTacticalEquipment.h"\r\n')
change('Public/ParisBridgeMission.h',[
 ('    static AParisBridgeMission* Find(const UObject* Context);','    static AParisBridgeMission* Find(const UObject* Context);\r\n    bool ValidateEquipmentReviewPayload(const FString& Payload,FString& Error) const {return ValidateSnapshot(Payload,Error);}')
])
write(OUT/a.revision/'author.json',dict(status='authored_unbuilt',source_additions=[p.name for p in here.glob('*.cpp')],preserved_reflection='no original UPROPERTY/UFUNCTION changes',save_adapter='finite grant validated against fixed supply inventories; original six-actor checks retained'))
print('Four-feature adapters authored in independent source; runtime validation pending')
