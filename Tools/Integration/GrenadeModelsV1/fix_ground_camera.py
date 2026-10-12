from pathlib import Path
root=Path(__file__).resolve().parents[3]
p=root/'tmp/g1-tactical-equipment-20261010/candidate_grenade_models_v1/Project/Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisTacticalEquipment.cpp'
t=p.read_text('utf-8');assert '#include "Camera/CameraActor.h"' not in t
t=t.replace('#include "Camera/PlayerCameraManager.h"','#include "Camera/PlayerCameraManager.h"\n#include "Camera/CameraActor.h"\n#include "Camera/CameraComponent.h"')
old='FixtureFeet(W,P,Feet);const FVector At=S.Supplies[0].Position;'
new='''FixtureFeet(W,P,Feet);const FVector At=S.Supplies[0].Position;
        if(S.Supplies[0].Visual.IsValid())S.Supplies[0].Visual->SetActorHiddenInGame(true);
        auto* Camera=W->SpawnActor<ACameraActor>();Camera->SetActorLocation(Feet+FVector(0,0,32));Camera->SetActorRotation((At+FVector(0,0,7)-Camera->GetActorLocation()).Rotation());Camera->GetCameraComponent()->SetFieldOfView(35);PC->SetViewTarget(Camera);if(auto* D=Display(W,P))D->SetActorHiddenInGame(true);'''
assert old in t;t=t.replace(old,new)
t=t.replace('two exterior display-only props on native ground; no gameplay ball/timer/actor damage','two exterior display-only props at verified supply feet; supply display hidden and independent close camera only in photo fixture; no gameplay ball/timer/actor damage')
p.write_text(t,encoding='utf-8')
