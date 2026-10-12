from pathlib import Path
root=Path(__file__).resolve().parents[3]
p=root/'tmp/g1-tactical-equipment-20261010/candidate_grenade_models_v1/Project/Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisTacticalEquipment.cpp'
t=p.read_text('utf-8')
old='''        const FVector Feet=P->GetActorLocation()-FVector(0,0,P->GetCapsuleComponent()->GetScaledCapsuleHalfHeight());
        FVector At;const FVector Forward=PC->GetControlRotation().Vector().GetSafeNormal2D();
        if(!Site(W,Feet+Forward*125,At)){FinishCheck(W,false,TEXT("ground_photo_native_admission"));return;}
'''
new='''        FVector Feet;if(!Access(W,S.Supplies[0].Position,Feet)){FinishCheck(W,false,TEXT("ground_photo_native_admission"));return;}
        FixtureFeet(W,P,Feet);const FVector At=S.Supplies[0].Position;
'''
assert old in t;t=t.replace(old,new)
# Add bounded intermediate frames to inspect the original moving and held poses.
t=t.replace('    if(CheckStep==1&&S.ThrowStage', '    if(CheckStep==1&&CheckClock>.48&&CheckClock<.48+DT)Picture(TEXT("frag_prepare.png"));\n    if(CheckStep==4&&CheckClock>.48&&CheckClock<.48+DT)Picture(TEXT("smoke_prepare.png"));\n    if(CheckStep==1&&S.ThrowStage')
p.write_text(t,encoding='utf-8')
