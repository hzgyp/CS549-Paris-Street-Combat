"""Author an isolated screenshot harness; never change the normal playtest."""
from prepare import ROOT, OUT, prepare, sha, write

REVISION = 'candidate_trap_picture_v1'
BASE = OUT / 'candidate_full_v16/Project'
PRIVATE = 'Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/'
write(OUT/'trap-picture-plan-20261011.json', {
    'request': 'Actual screenshot of the Trap2 that killed the player',
    'cases_read': ['MI023', 'MI025', 'MI026', 'MI029'],
    'change': 'Separate diagnostic source, camera relocation/FOV and marked screenshot only; ordinary Game and models unchanged',
    'early_acceptance': 'Exact Trap2 position/visual code, native floor/capsule/path and line of sight; normal FP initialized; source diff restricted to harness',
    'stop': 'Unknown game/editor session, failed geometry or original visual/source protection, compile/runtime failure; preserve evidence, no blind retry',
    'scope': 'Fixture screenshots, not a reconstruction of the user camera; marker exists only in the labelled diagnostic image',
})
prepare(REVISION, 'candidate_full_v16')
project = OUT/REVISION/'Project'
cpp = project/(PRIVATE+'ParisTacticalEquipment.cpp')
raw = cpp.read_bytes()
anchor = b'#include "ParisTacticalEquipment.h"'
assert raw.count(anchor) == 1
cpp.write_bytes(raw.replace(anchor, anchor+b'\r\n#include "DrawDebugHelpers.h"'))
checks = project/(PRIVATE+'ParisEquipmentChecks.inl')
raw = checks.read_bytes()
anchor = b'    if(CheckMode==TEXT("performance"))'
assert raw.count(anchor) == 1
harness = r'''
    if(CheckMode==TEXT("trap_picture")){
        auto& T=S.Traps[1];
        if(CheckStep==0){
            if(M->Phase!=TEXT("Ready")||!S.Initialized)return;
            auto* D=Display(W,P);if(!D||!Flag(D,TEXT("Initialized")))return;
            FVector Feet;bool Admitted=false;
            for(const FVector Offset:{FVector(0,-220,0),FVector(0,220,0),FVector(-220,0,0),FVector(220,0,0)})
                if(Site(W,T.Position+Offset,Feet)&&ClearRay(W,Feet+FVector(0,0,160),T.Position+FVector(0,0,10))){Admitted=true;break;}
            if(!Expect(W,Admitted,TEXT("Trap2_actual_floor_capsule_full_path_and_ray")))return;
            M->StartMission();HoldBrains(W);FixtureFeet(W,P,Feet);
            Event(W,TEXT("fixture"),TEXT("Screenshot only: real Trap2 unchanged; player relocated to admitted viewpoint; NPCs held"));
            CheckStep=150;CheckClock=0;return;
        }
        if(CheckStep==150&&CheckClock>1){AimPoint(PC,T.Position+FVector(0,0,6));CheckStep=151;CheckClock=0;return;}
        if(CheckStep==151&&CheckClock>1){
            FVector Eye;FRotator View;PC->GetPlayerViewPoint(Eye,View);
            auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("scope"),TEXT("Actual runtime Trap2; fixture viewpoint, held NPCs; marker only in explicitly labelled picture; not the user's recorded view"));
            O->SetStringField(TEXT("trap_id"),T.Id);O->SetStringField(TEXT("trap_position_cm"),T.Position.ToString());
            O->SetStringField(TEXT("player_location_cm"),P->GetActorLocation().ToString());O->SetStringField(TEXT("camera_location_cm"),Eye.ToString());
            O->SetStringField(TEXT("camera_rotation"),View.ToString());O->SetNumberField(TEXT("normal_fov"),PC->PlayerCameraManager->GetFOVAngle());
            O->SetNumberField(TEXT("close_fov"),40);O->SetStringField(TEXT("trap_state"),T.State);
            FFileHelper::SaveStringToFile(JsonText(O),*(CheckOut/TEXT("TRAP_VIEW.json")));
            Picture(TEXT("01_trap2_normal.png"));CheckStep=152;CheckClock=0;return;
        }
        if(CheckStep==152&&CheckClock>.5){
            DrawDebugSphere(W,T.Position+FVector(0,0,7),25,20,FColor::Yellow,true,-1,0,1.5);
            Notice(W,TEXT("DIAGNOSTIC YELLOW MARKER = TRAP2 / NOT A GAME WARNING"));
            CheckStep=153;CheckClock=0;return;
        }
        if(CheckStep==153&&CheckClock>.5){Picture(TEXT("02_trap2_marker.png"));CheckStep=154;CheckClock=0;return;}
        if(CheckStep==154&&CheckClock>.5){
            FlushPersistentDebugLines(W);PC->PlayerCameraManager->SetFOV(40);
            Notice(W,TEXT("DETAIL VIEW / FOV 40 / ACTUAL TRAP2 MODEL UNCHANGED"));
            CheckStep=155;CheckClock=0;return;
        }
        if(CheckStep==155&&CheckClock>1){Picture(TEXT("03_trap2_detail.png"));CheckStep=156;CheckClock=0;return;}
        if(CheckStep==156&&CheckClock>.5){FinishCheck(W,T.State==TEXT("Armed")&&!Dead(P),TEXT("Three actual runtime Trap2 pictures; normal, diagnostic marker, narrow-FOV detail; ordinary playtest unchanged"));return;}
        if(CheckClock>20)FinishCheck(W,false,TEXT("trap_picture_timeout"));return;
    }
'''.replace('\n','\r\n').encode()
checks.write_bytes(raw.replace(anchor,harness+anchor))
changed=[]
for folder in ['Config','Source','Plugins']:
    for src in (BASE/folder).rglob('*'):
        if not src.is_file() or any(v in src.relative_to(BASE).parts for v in ['Binaries','Intermediate']): continue
        target=project/src.relative_to(BASE)
        if sha(src)!=sha(target): changed.append(src.relative_to(BASE).as_posix())
assert set(changed)=={PRIVATE+'ParisTacticalEquipment.cpp',PRIVATE+'ParisEquipmentChecks.inl'}, changed
write(OUT/REVISION/'capture-source-diff.json', {'status':'capture_only','changed':changed,'all_other_source_files_exact':True,'ordinary_game_sha256':'ab48a534f7c957437d736d4d777128e316d819f8a9d81ebd0d22103ed1b59f1a'})
print('Capture-only harness prepared; current normal source/Game untouched')
