from prepare import OUT
from pathlib import Path
import shutil
here=Path(__file__).parent
p=here/'ParisTacticalEquipment.cpp';s=p.read_bytes()
headers=['Particles/ParticleEmitter.h','Particles/ParticleSpriteEmitter.h','Particles/ParticleLODLevel.h','Particles/ParticleModuleRequired.h','Particles/Spawn/ParticleModuleSpawn.h','Particles/Lifetime/ParticleModuleLifetime.h','Particles/Size/ParticleModuleSize.h','Particles/Velocity/ParticleModuleVelocity.h','Particles/Location/ParticleModuleLocation.h','Particles/Color/ParticleModuleColorOverLife.h','Distributions/DistributionFloatConstant.h','Distributions/DistributionFloatParticleParameter.h','Distributions/DistributionVectorConstant.h','Distributions/DistributionVectorUniform.h']
needle=b'#include "Particles/ParticleSystem.h"';assert s.count(needle)==1;s=s.replace(needle,needle+b'\r\n'+b'\r\n'.join(('#include "'+h+'"').encode() for h in headers))
needle=b'auto* P=UGameplayStatics::GetPlayerCharacter(W,0);O->SetStringField(TEXT("action")'
new=b'auto* P=UGameplayStatics::GetPlayerCharacter(W,0);O->SetStringField(TEXT("player_location"),P->GetActorLocation().ToString());O->SetNumberField(TEXT("player_health"),Num(P,TEXT("Health")));O->SetNumberField(TEXT("capsule_half"),P->GetCapsuleComponent()->GetScaledCapsuleHalfHeight());for(const TCHAR* Field:{TEXT("ShotOutcome"),TEXT("ShotAimPoint")})if(auto* F=FindFProperty<FProperty>(P->GetClass(),Field)){FString V;F->ExportText_InContainer(0,V,P,P,P,PPF_None);O->SetStringField(Field,V);}O->SetStringField(TEXT("action")'
assert s.count(needle)==1;s=s.replace(needle,new);p.write_bytes(s)
p=here/'ParisEquipmentWorld.inl';s=p.read_bytes();s=s.replace(b'FCollisionQueryParams Q(SCENE_QUERY_STAT(ParisEquipmentSite),true)',b'FCollisionQueryParams Q(SCENE_QUERY_STAT(ParisEquipmentSite),false)')
s=s.replace(b'void SmokeVisual(',b'#include "ParisEquipmentSmoke.inl"\r\nvoid SmokeVisual(',1)
begin=s.index(b'auto* PS=LoadObject<UParticleSystem>');end=s.index(b'auto* E=NewObject<UParticleSystemComponent>',begin);s=s[:begin]+b'auto* PS=DenseSmoke(C);'+s[end:]
s=s.replace(b'FVector(0,0,70)',b'FVector(0,0,100)').replace(b'SetRelativeScale3D(FVector(3))',b'SetRelativeScale3D(FVector(1))').replace(b'SetFloatParameter(TEXT("Opacity"),F)',b'SetFloatParameter(TEXT("Opacity"),.6f*F)').replace(b'FVector(3*FMath::Max(.1f,F))',b'FVector(FMath::Max(.01f,F))')
p.write_bytes(s)
p=here/'ParisEquipmentSave.cpp';s=p.read_bytes().replace(b'trap2_sites_v2',b'trap2_physical_sites_v3');p.write_bytes(s)
p=here/'ParisEquipmentChecks.inl';s=p.read_bytes()
s=s.replace(b'void HoldBrains(UWorld* W){for(auto* C:Combatants(W))if(auto* AI=Cast<AAIController>(C->GetController()))if(AI->GetBrainComponent())AI->GetBrainComponent()->PauseLogic(TEXT("Explicit equipment fixture isolation"));}',b'void HoldBrains(UWorld* W){for(auto* C:Combatants(W))if(auto* AI=Cast<AAIController>(C->GetController())){auto* F=AI->FindFunction(TEXT("PC_EnableCombat"));if(F){FStructOnScope V(F);if(auto* B=FindFProperty<FBoolProperty>(F,TEXT("Enabled")))B->SetPropertyValue_InContainer(V.GetStructMemory(),false);AI->ProcessEvent(F,V.GetStructMemory());}AI->StopMovement();if(AI->GetBrainComponent())AI->GetBrainComponent()->PauseLogic(TEXT("Explicit equipment fixture isolation"));}}')
s=s.replace(b'A.Add(A[0]);',b'const auto Duplicate=A[0];A.Add(Duplicate);')
s=s.replace(b'if(CheckStep==20&&CheckClock>.7)',b'if(CheckStep==20&&CheckClock>.3){AimPoint(PC,S.Traps[0].Position+FVector(0,0,10));CheckStep=201;CheckClock=0;}\r\n        else if(CheckStep==201&&CheckClock>.4)')
s=s.replace(b'else if(CheckStep==23&&CheckClock>.7)',b'else if(CheckStep==23&&CheckClock>.3){AimPoint(PC,S.Supplies[0].Position+FVector(0,0,25));CheckStep=203;CheckClock=0;}\r\n        else if(CheckStep==203&&CheckClock>.4)')
s=s.replace(b'auto* EB=Blackboard(TestEnemy.Get());auto* AB=Blackboard(TestAlly.Get());if(!Expect(W,EB&&AB,TEXT("original_blackboards")))return;',b'auto* EB=Blackboard(TestEnemy.Get());auto* AB=Blackboard(TestAlly.Get());if(!EB||!AB){FinishCheck(W,false,TEXT("original_blackboards"));return;}')
s=s.replace(b'TestHealth=Num(TestEnemy.Get(),TEXT("Health"));Tap(PC,EKeys::LeftMouseButton)',b'TestHealth=Num(TestEnemy.Get(),TEXT("Health"));if(!Expect(W,TestHealth==100,TEXT("isolated_smoke_target_remains_alive_before_shot")))return;Tap(PC,EKeys::LeftMouseButton)')
p.write_bytes(s)
base=OUT/'candidate_full_v11/Project/Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private';assert not (OUT/'candidate_full_v11/build-game.json').exists()
for name in ['ParisTacticalEquipment.h','ParisTacticalEquipment.cpp','ParisEquipmentState.h','ParisEquipmentSave.cpp','ParisEquipmentSightBridge.h','ParisEquipmentWorld.inl','ParisEquipmentAudio.inl','ParisEquipmentChecks.inl','ParisEquipmentSmoke.inl']:shutil.copyfile(here/name,base/name)
print('v11 authored: matching physical queries, bounded transient dense smoke and corrected diagnostic isolation/aim/array clone')
