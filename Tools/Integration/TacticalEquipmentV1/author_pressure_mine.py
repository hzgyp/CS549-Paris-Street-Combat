"""Independent mine revision from exact equipment v16; no original/native writes."""
from prepare import ROOT,OUT,prepare,write,sha
import argparse
ap=argparse.ArgumentParser();ap.add_argument('revision');a=ap.parse_args()
prepare(a.revision,'candidate_full_v16')
project=OUT/a.revision/'Project'
private=project/'Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private'

def edit(p,old,new):
    b=p.read_bytes();o=old.replace('\n','\r\n').encode();n=new.replace('\n','\r\n').encode()
    assert b.count(o)==1,(p.name,old[:100],b.count(o));p.write_bytes(b.replace(o,n))

cpp=private/'ParisTacticalEquipment.cpp'
edit(cpp,'#include "ParisTacticalEquipment.h"','#include "ParisTacticalEquipment.h"\n#include "Camera/PlayerCameraManager.h"\n#include "MeshDescription.h"\n#include "StaticMeshAttributes.h"\n#include "Engine/Texture2D.h"\n#include "ImageUtils.h"')
world=private/'ParisEquipmentWorld.inl'
edit(world,'void SiteVisuals(UWorld* W,FEquipmentSession& S){for(auto& T:S.Traps){T.Visual=Prop(W,TEXT("Trap"),T.Position);const FLinearColor Steel(.19,.22,.12);Part(T.Visual.Get(),TEXT("Cylinder"),FVector(.10,.10,.075),FVector(0,0,3.8),Steel);for(int32 I=0;I<3;++I)Part(T.Visual.Get(),TEXT("Cube"),FVector(.012,.012,.045),FVector((I-1)*2,0,9),Steel);if(T.State!=TEXT("Armed"))T.Visual->SetActorHiddenInGame(true);}', '#include "ParisPressureMineMesh.inl"\nvoid SiteVisuals(UWorld* W,FEquipmentSession& S){for(auto& T:S.Traps)PressureMineVisual(W,T);')
edit(world,'T.State==TEXT("Armed")&&T.Discovered&&VisiblePoint(W,P,T.Position+FVector(0,0,10),165,.65)','T.State==TEXT("Armed")&&T.Discovered&&FVector::Dist2D(P->GetActorLocation(),T.Position)<=200&&VisiblePoint(W,P,T.Position+FVector(0,0,6),400,.9)')
edit(world,'Num(C,TEXT("TeamId"))==0&&T.Discovered&&T.State==TEXT("Armed")','(Num(C,TEXT("TeamId"))==1||T.Discovered)&&T.State==TEXT("Armed")')
edit(world,'T.Discovered=true;Event(W,TEXT("trap_discovered"),T.Id);break;','T.Discovered=true;Event(W,TEXT("trap_discovered"),T.Id);Event(W,TEXT("mine_discovered_by"),T.Id+TEXT(" by ")+C->GetName());break;')
edit(world,'!Dead(C)&&Num(C,TEXT("TeamId"))==0&&FVector::Dist2D(C->GetActorLocation(),T.Position)<65&&FMath::Abs(C->GetActorLocation().Z-C->GetCapsuleComponent()->GetScaledCapsuleHalfHeight()-T.Position.Z)<80','FootTouchesMine(C,T)')
edit(world,'Blast(W,T.Position+FVector(0,0,15),T.Id,350,140);Event(W,TEXT("trap_triggered"),T.Id);','Event(W,TEXT("mine_trigger_actor"),T.Id+TEXT(" by ")+C->GetName(),Num(C,TEXT("TeamId")));Blast(W,T.Position+FVector(0,0,15),T.Id,350,140);Event(W,TEXT("trap_triggered"),T.Id);')
edit(world,'TEXT("TRAP DISARMED")','TEXT("MINE DISARMED")')
edit(cpp,'Event(W,TEXT("damage"),C->GetName(),Before-Num(C,TEXT("Health")));','Event(W,TEXT("damage"),C->GetName(),Before-Num(C,TEXT("Health")));Event(W,TEXT("damage_before_health"),C->GetName(),Before);Event(W,TEXT("damage_after_health"),C->GetName(),Num(C,TEXT("Health")));')
edit(cpp,'TEXT("HOLD E  DISARM ENEMY TRAP")','TEXT("HOLD E 2s  DISARM MINE")')
edit(cpp,'TEXT("ENEMY TRAP NEARBY  /  WATCH THE GROUND")','TEXT("ENEMY MINE NEARBY  /  WATCH THE GROUND")')
anchor='float HudProgress(UWorld* W){return float(Session(W).DisarmClock/2.);}'
edit(cpp,anchor,anchor+'\nTArray<TPair<FVector,float>> MineHints(UWorld* W){TArray<TPair<FVector,float>> H;auto* P=UGameplayStatics::GetPlayerCharacter(W,0);if(!P||Dead(P))return H;auto& S=Session(W);for(const auto& T:S.Traps)if(T.Discovered&&T.State==TEXT("Armed")&&VisiblePoint(W,P,T.Position+FVector(0,0,10),800,0))H.Emplace(T.Position+FVector(0,0,15),float(FVector::Dist2D(P->GetActorLocation(),T.Position)/100));return H;}')
header=private/'ParisTacticalEquipment.h'
edit(header,'float HudProgress(UWorld* World);','float HudProgress(UWorld* World);\nTArray<TPair<FVector,float>> MineHints(UWorld* World);')
build=private.parent/'ParisBridgeMissionV1.Build.cs'
edit(build,'"RenderCore", "RHI",','"RenderCore", "RHI", "MeshDescription", "StaticMeshDescription",')
mission=private/'ParisBridgeMission.cpp'
old='    if(!AllowsPlay())\n    {\n        if(Phase==TEXT("Won")) { UpdateCheckpointUI(); FString Reason; SafeSeconds=IsSafeBoundary(Reason)?SafeSeconds+DeltaSeconds:0; }'
new='''    // A cleared objective still allows movement and live map/equipment hazards.
    if(Phase==TEXT("Won"))
    {
        LivingAllies=0;
        for(int32 I=0;I<Roster.Num();++I) if(IsValid(Roster[I]))
        {
            if(Flag(Roster[I],TEXT("IsDead"))) DeathLedger.Add(StableIds[I]);
            else if(I>0&&I<3) ++LivingAllies;
        }
        if(DeathLedger.Contains(TEXT("Player"))) { SetCheckpointDialog(TEXT("None"),FString()); CheckpointPromptVisible=false; SetPhase(TEXT("Lost")); Feedback=TEXT("Player lost to a remaining hazard. F9 loads a save; F6 restarts."); GateBrains(false); return; }
    }
    if(!AllowsPlay())
    {
        if(Phase==TEXT("Won")) { UpdateCheckpointUI(); FString Reason; SafeSeconds=IsSafeBoundary(Reason)?SafeSeconds+DeltaSeconds:0; }'''
edit(mission,old,new)
anchor='        Text(ParisTacticalEquipment::HudInventory(GetWorld())'
b=mission.read_bytes();needle=anchor.encode();assert b.count(needle)==1
start=b.index(needle);lineend=b.index(b'\n',start)
draw='''
        for(const auto& Hint:ParisTacticalEquipment::MineHints(GetWorld()))
        {
            FVector2D Screen;if(!PlayerOwner->ProjectWorldLocationToScreen(Hint.Key,Screen))continue;
            const double MX=Screen.X/(Canvas->SizeX/1920.0),MY=Screen.Y/(Canvas->SizeY/1080.0);
            if(MX<100||MX>1820||MY<180||MY>900)continue;
            const auto MineColor=FLinearColor(1.f,.67f,.16f,1.f);
            Diamond(MX,MY,9,MineColor);Text(TEXT("!"),MX,MY-7,11,Ink,true);
            Text(FString::Printf(TEXT("MINE  %.1fm"),Hint.Value),MX,MY-39,13,MineColor,true);
        }
'''.replace('\n','\r\n').encode()
mission.write_bytes(b[:lineend+1]+draw+b[lineend+1:])
save=private/'ParisEquipmentSave.cpp'
edit(save,'const FString Config=TEXT("G1Equipment_20261010_frag2_smoke2_sup16x2_trap2_physical_sites_v3");','const FString Config=TEXT("G1PressureMine_20261011_disc28_ground_contact_disarm2m");\nconst FString CompatibleEquipmentV16=TEXT("G1Equipment_20261010_frag2_smoke2_sup16x2_trap2_physical_sites_v3");')
edit(save,'C!=Config)return Reject(TEXT("schema/config"));','(C!=Config&&C!=CompatibleEquipmentV16))return Reject(TEXT("schema/config"));')
for name in ['ParisPressureMineMesh.inl','ParisPressureMineChecks.inl']:
    src=ROOT/'Tools/Integration/TacticalEquipmentV1'/name;assert src.exists();(private/name).write_bytes(src.read_bytes().replace(b'\r\n',b'\n').replace(b'\n',b'\r\n'))
checks=private/'ParisEquipmentChecks.inl'
edit(checks,'void EquipmentCheck(', '#include "ParisPressureMineChecks.inl"\nvoid EquipmentCheck(')
anchor='    if(CheckMode==TEXT("performance"))'
edit(checks,anchor,'    if(CheckMode.StartsWith(TEXT("mine_"))){PressureMineCheck(W,M,S,PC,P,DT);return;}\n'+anchor)
write(OUT/a.revision/'mine-authoring.json',{'status':'independent_candidate','parent':'candidate_full_v16','model':'Assets/LocalWorking/Experiments/PressureMine/20261011-v1/finish_v2','native_writes':False,'finger_gun_ammo_transaction_changes':False,'config_compatibility':['exact_v16','legacy_v5'],'hazard_death_handling':'Won still records actual casualties and transitions to Lost if player dead'})
print('Pressure mine source ready')
