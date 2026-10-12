from pathlib import Path
here=Path(__file__).parent
p=here/'ParisTacticalEquipment.cpp';data=p.read_bytes()
needle=b'if(B.Kind==TEXT("Frag"))Blast(W,B.Position,B.Id);if(B.Visual.IsValid())'
assert data.count(needle)==1
data=data.replace(needle,b'if(B.Kind==TEXT("Frag"))Blast(W,B.Position,B.Id);else {FSmoke C;C.Id=B.Id;C.Position=B.Position;S.Clouds.Add(C);SmokeVisual(W,S.Clouds.Last());Event(W,TEXT("smoke_deployed"),B.Id);}if(B.Visual.IsValid())')
needle=b'S.Held->SetActorRelativeLocation(FVector(2,0,0));'
assert data.count(needle)==1
data=data.replace(needle,b'const FVector Palm=Pose->GetSocketLocation(TEXT("middle_01_r"));const FVector Tips=(Pose->GetSocketLocation(TEXT("middle_03_r"))+Pose->GetSocketLocation(TEXT("ring_03_r")))*.5;const FVector Center=(Palm+Tips)*.5;S.Held->SetActorRelativeLocation(Pose->GetSocketTransform(TEXT("hand_r")).InverseTransformPosition(Center));')
p.write_bytes(data)
print('Smoke deployment and separate new-prop palm landmark placement added; protected hand/gun bindings unchanged')
