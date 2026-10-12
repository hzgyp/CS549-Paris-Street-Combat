from pathlib import Path
import shutil
from prepare import OUT
here=Path(__file__).parent
base=OUT/'candidate_full_v12/Project/Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private'
assert not (OUT/'candidate_full_v12/build-game.json').exists()
p=here/'ParisTacticalEquipment.cpp';s=p.read_bytes()
needle=b'#include "Particles/ParticleSystemComponent.h"'
s=s.replace(needle,needle+b'\r\n#include "ParticleEmitterInstances.h"\r\n#include "Particles/SubUV/ParticleModuleSubUV.h"\r\n#include "Particles/Parameter/ParticleModuleParameterDynamic.h"')
p.write_bytes(s)
p=here/'ParisEquipmentSmoke.inl';s=p.read_bytes()
s=s.replace(b'auto* PS=NewObject<UParticleSystem>();',b'auto* SourceLOD=Source->Emitters[0]->LODLevels[0].Get();auto* PS=NewObject<UParticleSystem>();')
s=s.replace(b'LOD->RequiredModule=NewObject<UParticleModuleRequired>(PS)',b'LOD->RequiredModule=DuplicateObject<UParticleModuleRequired>(SourceLOD->RequiredModule,PS)')
s=s.replace(b'LOD->Modules={Life,Size,Velocity,Location,Color};',b'LOD->Modules={Life,Size,Velocity,Location,Color};for(auto* Module:SourceLOD->Modules)if(Module->IsA<UParticleModuleSubUV>()||Module->IsA<UParticleModuleParameterDynamic>())LOD->Modules.Add(DuplicateObject<UParticleModule>(Module,PS));')
p.write_bytes(s)
p=here/'ParisEquipmentState.h';s=p.read_bytes().replace(b'bool Paused=false;',b'bool Paused=false,PreviousHold=false;\r\n    double PreviousGeneration=-1;');p.write_bytes(s)
p=here/'ParisEquipmentWorld.inl';s=p.read_bytes()
needle=b'E.Paused=true;S.Evades.Add(E);'
assert s.count(needle)==1
s=s.replace(needle,b'E.Paused=true;E.PreviousHold=Flag(AI,TEXT("CombatHold"));E.PreviousGeneration=Num(AI,TEXT("CombatGeneration"));if(auto* F=FindFProperty<FBoolProperty>(AI->GetClass(),TEXT("CombatHold")))F->SetPropertyValue_InContainer(AI,true);SetNum(AI,TEXT("CombatGeneration"),Num(C,TEXT("RestoreGeneration")));S.Evades.Add(E);')
s=s.replace(b'AI->MoveToLocation(P.Location,35,true,true,true,false,nullptr,false);Event(W,TEXT("native_evade"),C->GetName());',b'const auto Result=AI->MoveToLocation(P.Location,35,true,true,true,false,nullptr,false);Event(W,TEXT("native_evade"),C->GetName()+TEXT(" to ")+P.Location.ToString(),int32(Result));')
needle=b'AI->StopMovement();if(!Dead(C)&&AParisBridgeMission::Find(W)->AllowsPlay())AI->GetBrainComponent()->ResumeLogic'
assert s.count(needle)==1
s=s.replace(needle,b'AI->StopMovement();if(auto* F=FindFProperty<FBoolProperty>(AI->GetClass(),TEXT("CombatHold")))F->SetPropertyValue_InContainer(AI,S.Evades[I].PreviousHold);SetNum(AI,TEXT("CombatGeneration"),S.Evades[I].PreviousGeneration);if(!Dead(C)&&AParisBridgeMission::Find(W)->AllowsPlay())AI->GetBrainComponent()->ResumeLogic')
p.write_bytes(s)
p=here/'ParisEquipmentChecks.inl';s=p.read_bytes()
diag=b'''void SmokeReceipt(UWorld* W,FEquipmentSession& S){auto O=MakeShared<FJsonObject>();TArray<TSharedPtr<FJsonValue>> Rows;for(const auto& C:S.Clouds)if(C.Effect.IsValid()){auto R=MakeShared<FJsonObject>();R->SetNumberField(TEXT("particles"),C.Effect->GetNumActiveParticles());auto* Required=C.Effect->Template->Emitters[0]->LODLevels[0]->RequiredModule.Get();R->SetStringField(TEXT("material"),Required->Material->GetPathName());R->SetNumberField(TEXT("atlas_x"),Required->SubImages_Horizontal);R->SetNumberField(TEXT("atlas_y"),Required->SubImages_Vertical);R->SetNumberField(TEXT("interpolation"),int32(Required->InterpolationMethod));if(!C.Effect->EmitterInstances.IsEmpty()&&C.Effect->EmitterInstances[0]->ActiveParticles){auto* P=C.Effect->EmitterInstances[0]->GetParticle(0);R->SetStringField(TEXT("size"),P->Size.ToString());R->SetNumberField(TEXT("alpha"),P->Color.A);}Rows.Add(MakeShared<FJsonValueObject>(R));}O->SetArrayField(TEXT("clouds"),Rows);FFileHelper::SaveStringToFile(JsonText(O),*(CheckOut/TEXT("SMOKE_RENDER.json")),FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);}\r\n'''
s=diag+s
s=s.replace(b'Picture(TEXT("smoke_dense.png"));',b'SmokeReceipt(W,S);Picture(TEXT("smoke_dense.png"));')
s=s.replace(b'bool Found=false;for(const auto& E:S.Evades)if(E.Pawn==TestAlly)Found=true;',b'bool Found=false;for(const auto& E:S.Evades)if(E.Pawn==TestAlly)Found=true;Event(W,TEXT("evade_actual_distance"),TestAlly->GetActorLocation().ToString(),FVector::Dist2D(TestAlly->GetActorLocation(),TestEvadeOrigin));')
p.write_bytes(s)
for name in ['ParisTacticalEquipment.cpp','ParisEquipmentState.h','ParisEquipmentWorld.inl','ParisEquipmentChecks.inl','ParisEquipmentSmoke.inl']:shutil.copyfile(here/name,base/name)
print('v12: retain cooked smoke atlas/SubUV/dynamic inputs; scoped hazard movement ownership and exact visual/movement telemetry')
