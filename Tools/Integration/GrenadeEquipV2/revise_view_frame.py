from pathlib import Path
root=Path(__file__).resolve().parents[3];project=root/'tmp/g1-tactical-equipment-20261010/candidate_grenade_equip_v1/Project'
g=project/'Plugins/ParisGripBindingV18/Source/ParisGripBindingV18';p=project/'Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private'
f=g/'Public/ParisFPUpperBodyV19Actor.h';t=f.read_text('utf-8').replace('USkeletalMeshComponent* Source, FName Label);','USkeletalMeshComponent* Source, FName Label, double ExteriorHeightCm);').replace('    bool EquipmentFrameCached=false;','    bool EquipmentFrameCached=false;\n    double EquipmentExteriorHeightCm=0;');f.write_text(t,encoding='utf-8')
f=g/'Private/ParisFPUpperBodyV19Actor.cpp';t=f.read_text('utf-8').replace('#include "Engine/SkeletalMesh.h"','#include "Engine/SkeletalMesh.h"\n#include "Camera/PlayerCameraManager.h"\n#include "GameFramework/PlayerController.h"\n#include "Kismet/GameplayStatics.h"')
t=t.replace('USkeletalMeshComponent* InSource,FName Label)','USkeletalMeshComponent* InSource,FName Label,double ExteriorHeightCm)').replace('    EquipmentPoseLabel=Label;','    EquipmentPoseLabel=Label;EquipmentExteriorHeightCm=ExteriorHeightCm;')
old='EquipmentRootOffset=HoldingSource->GetComponentSpaceTransforms()[HoldingHand].GetLocation()-EquipComponent[Hand].GetLocation();'
new='''auto* PC=UGameplayStatics::GetPlayerController(this,0);if(!PC||EquipmentExteriorHeightCm<=0){BindingError=TEXT("Equipment view contract absent");return false;}
            FVector Eye;FRotator View;PC->GetPlayerViewPoint(Eye,View);int32 Width,Height;PC->GetViewportSize(Width,Height);
            if(Width<=0||Height<=0){BindingError=TEXT("Equipment viewport absent");return false;}
            const double TanH=FMath::Tan(FMath::DegreesToRadians(PC->PlayerCameraManager->GetFOVAngle()*.5)),TanV=TanH*Height/Width;
            const double Depth=EquipmentExteriorHeightCm/(2*TanV*.24);
            const FVector Desired=Eye+View.Vector()*Depth+FRotationMatrix(View).GetUnitAxis(EAxis::Y)*(Depth*TanH*(2*.68-1))+FRotationMatrix(View).GetUnitAxis(EAxis::Z)*(Depth*TanV*(1-2*.70));
            EquipmentRootOffset=Pose->GetComponentTransform().InverseTransformPosition(Desired)-EquipComponent[Hand].GetLocation();'''
assert old in t;t=t.replace(old,new);f.write_text(t,encoding='utf-8')
f=p/'ParisGrenadeEquipPose.inl';t=f.read_text('utf-8').replace('SetEquipmentPoseSource(nullptr,NAME_None)','SetEquipmentPoseSource(nullptr,NAME_None,0)').replace('D->SetEquipmentPoseSource(S.EquipmentPoseSource.Get(),FName(*(TEXT("Grenade")+Stage)));','const double ExteriorHeight=2*FMath::Max(GrenadeMesh(W,TEXT("Frag"))->GetBounds().BoxExtent.GetMax(),GrenadeMesh(W,TEXT("Smoke"))->GetBounds().BoxExtent.GetMax());\n        D->SetEquipmentPoseSource(S.EquipmentPoseSource.Get(),FName(*(TEXT("Grenade")+Stage)),ExteriorHeight);');f.write_text(t,encoding='utf-8')
f=p/'ParisEquipmentWheelChecks.inl';t=f.read_text('utf-8')
old='if(CheckStep==1&&CheckClock>1){if(!GrenadeFrame(W,S,PC,TEXT("Frag_ready")))return;'
new='if(CheckStep==1&&CheckClock>1){Picture(TEXT("01_frag_ready.png"));CheckStep=101;CheckClock=0;}\n    else if(CheckStep==101&&CheckClock>.3&&!FScreenshotRequest::IsScreenshotRequested()){if(!GrenadeFrame(W,S,PC,TEXT("Frag_ready")))return;'
assert old in t;t=t.replace(old,new).replace('Picture(TEXT("01_frag_ready.png"));CheckStep=2;','CheckStep=2;')
t=t.replace('else if(CheckStep==7&&CheckClock>1){if(!GrenadeFrame(W,S,PC,TEXT("Smoke_ready")))return;Picture(TEXT("03_smoke_ready.png"));CheckStep=8;CheckClock=0;}','else if(CheckStep==7&&CheckClock>1){Picture(TEXT("03_smoke_ready.png"));CheckStep=107;CheckClock=0;}\n    else if(CheckStep==107&&CheckClock>.3&&!FScreenshotRequest::IsScreenshotRequested()){if(!GrenadeFrame(W,S,PC,TEXT("Smoke_ready")))return;CheckStep=8;CheckClock=0;}')
# Ready failure evidence is captured before evaluating the view gate; hold images
# follow after its ready pose has passed and inputs are deferred until completion.
f.write_text(t,encoding='utf-8')
f=root/'Docs/Development/MissionLoopV1/GRENADE_EQUIP_REVISION_IMPLEMENTATION_20261011_ZH.md';t=f.read_text('utf-8');t+='\n## v2显示锚修订（MI046）\n\nv1原枪握点锚导致Frag投影仅47.338%在屏内，停在早期门槛。新增有界投掷物显示布局：实际最大模型轴长＋当前FOV／视口解算24%画面高度及(0.68,0.70)中心，只改临时FP显示根，不改模型尺寸、身体、原镜头或枪械框架。先保存真实就绪图再查投影；维持0.75屏内比例门槛及人工实图复看，旧源／Game／诊断保持。\n';f.write_text(t,encoding='utf-8')
print('Model-sized projection frame; original camera/rifle untouched')
