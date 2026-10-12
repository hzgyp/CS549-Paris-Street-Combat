from pathlib import Path
from prepare import OUT
import shutil
here=Path(__file__).parent
p=here/'ParisTacticalEquipment.cpp';s=p.read_bytes().replace(b'#include "AIController.h"',b'#include "AIController.h"\r\n#include "Navigation/PathFollowingComponent.h"');p.write_bytes(s)
p=here/'ParisEquipmentWorld.inl';s=p.read_bytes()
needle=b'if(Safe){const auto Result='
assert s.count(needle)==1
replacement=b'''if(Safe){FCollisionQueryParams Q(SCENE_QUERY_STAT(ParisEvadeClearance),false,C);IgnoreProps(W,Q);const auto* Capsule=C->GetCapsuleComponent();FVector Previous=C->GetActorLocation();for(int32 I=1;I<Path->PathPoints.Num();++I){const FVector Next=Path->PathPoints[I]+FVector(0,0,Capsule->GetScaledCapsuleHalfHeight()+2);FHitResult Hit;if(W->SweepSingleByChannel(Hit,Previous,Next,FQuat::Identity,ECC_Pawn,FCollisionShape::MakeCapsule(Capsule->GetScaledCapsuleRadius(),Capsule->GetScaledCapsuleHalfHeight()),Q)){Safe=false;break;}Previous=Next;}}if(Safe){const auto Result='''
s=s.replace(needle,replacement);p.write_bytes(s)
p=here/'ParisEquipmentChecks.inl';s=p.read_bytes()
needle=b'TestAlly=Tagged(W,TEXT("G1_Ally1"));TestEvadeOrigin=TestAlly->GetActorLocation();PC->SetControlRotation(FRotator(20,0,0));'
replacement=b'''TestAlly=Tagged(W,TEXT("G1_Ally1"));FVector Feet;bool Admitted=false;for(const double Yaw:{0.,90.,180.,270.,45.,135.,225.,315.})if(Site(W,P->GetActorLocation()+FVector(450,0,0).RotateAngleAxis(Yaw,FVector::UpVector),Feet)&&ClearRay(W,P->GetActorLocation(),Feet+FVector(0,0,100))){Admitted=true;break;}if(!Expect(W,Admitted,TEXT("evade_fixture_actual_capsule_path")))return;FixtureFeet(W,TestAlly.Get(),Feet);TestAlly->SetActorRotation((P->GetActorLocation()-TestAlly->GetActorLocation()).Rotation());TestAlly->GetController()->SetControlRotation(TestAlly->GetActorRotation());Event(W,TEXT("fixture"),TEXT("existing ally relocated to capsule-admitted controlled evade lane"));TestEvadeOrigin=TestAlly->GetActorLocation();PC->SetControlRotation(FRotator(20,0,0));'''
assert s.count(needle)==1;s=s.replace(needle,replacement)
needle=b'Event(W,TEXT("evade_actual_distance"),'
s=s.replace(needle,b'Event(W,TEXT("evade_movement_speed"),TestAlly->GetVelocity().ToString(),TestAlly->GetCharacterMovement()->MaxWalkSpeed);Event(W,TEXT("evade_path_status"),Name(TestAlly.Get(),TEXT("ActionState")).ToString(),int32(Cast<AAIController>(TestAlly->GetController())->GetPathFollowingComponent()->GetStatus()));'+needle)
p.write_bytes(s)
base=OUT/'candidate_full_v14/Project/Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private'
assert not (OUT/'candidate_full_v14/build-game.json').exists()
for name in ['ParisTacticalEquipment.cpp','ParisEquipmentWorld.inl','ParisEquipmentChecks.inl']:shutil.copyfile(here/name,base/name)
p=Path('Failures/MI027-20261011-smoke-atlas-hazard-owner/ANALYSIS.md');s=p.read_bytes();s+='\n\nv13 hazard 实测位移仍为0，原生 MoveTo 返回2(RequestSuccessful)，不能据此认定移动通过或证明单一所有权推断。后续对有限避险路径增加正式胶囊实际 sweep，拒绝有碰撞的Nav候选；独立诊断把现有盟军放到已测胶囊/完整路径的视线车道，并记录实际速度、模式/路径状态，不改普通出生点或造新NPC。失败原件和假设限制保留。\n'.encode();p.write_bytes(s)
print('v14 native capsule sweep admission and measured existing-ally controlled lane; rejected prior zero-distance evidence retained')
