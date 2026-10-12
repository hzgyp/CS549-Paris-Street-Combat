from pathlib import Path
root=Path(__file__).resolve().parents[3];f=root/'tmp/g1-tactical-equipment-20261010/candidate_grenade_equip_v1/Project/Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisGrenadeEquipPose.inl'
t=f.read_text('utf-8');t=t.replace('    const FVector Center=(Palm+Tips)*.5;\n','')
key='    A->SetActorRelativeLocation(Hand.InverseTransformPosition(Center));'
new='''    auto* Exterior=A->FindComponentByClass<UStaticMeshComponent>();if(!Exterior||!Exterior->GetStaticMesh())return;
    const auto Extent=Exterior->GetStaticMesh()->GetBounds().BoxExtent;
    const double Radius=FMath::Max(Extent.X,Extent.Y);
    const FVector PalmPlane=(Pose->GetSocketLocation(TEXT("index_01_r"))+Palm+Pose->GetSocketLocation(TEXT("ring_01_r"))+Pose->GetSocketLocation(TEXT("pinky_01_r")))*.25;
    const FVector Center=PalmPlane+Facing*Radius;
    A->SetActorRelativeLocation(Hand.InverseTransformPosition(Center));'''
assert key in t;t=t.replace(key,new);f.write_text(t,encoding='utf-8')
f=root/'Docs/Development/MissionLoopV1/GRENADE_EQUIP_REVISION_IMPLEMENTATION_20261011_ZH.md';t=f.read_text('utf-8');t+='\n## v4掌面挂接（MI047）\n\nv3同镜头显隐诊断确认MkII确有渲染但被手挡住。只将旧掌指中点改为四指根平均掌面＋原外壳实际横截面半径，沿原动作掌面法线定位；不改动作／手指／模型／骨长／镜头，不扫描偏移。仍需有手的四个真实状态图可辨和原可见性／库存／回枪门槛，无遮手普通入口。\n';f.write_text(t,encoding='utf-8')
print('Palm-plane + actual exterior radius mount')
