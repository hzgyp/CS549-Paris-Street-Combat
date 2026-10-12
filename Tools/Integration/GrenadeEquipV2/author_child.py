from pathlib import Path
root=Path(__file__).resolve().parents[3];project=root/'tmp/g1-tactical-equipment-20261010/candidate_grenade_equip_v1/Project'
p=project/'Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private'
g=project/'Plugins/ParisGripBindingV18/Source/ParisGripBindingV18'
def edit(f,fn):t=f.read_text('utf-8');f.write_text(fn(t),encoding='utf-8')
def function(t,signature,new):
    s=t.index(signature);a=t.index('{',s);depth=1;i=a+1
    while depth:depth+=(t[i]=='{')-(t[i]=='}');i+=1
    return t[:s]+new+t[i:]
edit(g/'Public/ParisFPUpperBodyV19Actor.h',lambda t:t.replace('protected:\n','    // Transient display source only; no reflected/save fields or rifle constants.\n    void SetEquipmentPoseSource(USkeletalMeshComponent* Source, FName Label);\n    bool HasEquipmentPoseSource() const { return EquipmentPoseSource.IsValid(); }\nprotected:\n',1).replace('    bool SourceFrameCached = false;','    bool SourceFrameCached = false;\n    TWeakObjectPtr<USkeletalMeshComponent> EquipmentPoseSource;\n    FName EquipmentPoseLabel;\n    FVector EquipmentRootOffset=FVector::ZeroVector;\n    bool EquipmentFrameCached=false;'))
edit(g/'Private/ParisFPUpperBodyV19Actor.cpp',lambda t:t.replace('bool AParisFPUpperBodyV19Actor::PrepareHoldingSource(','''void AParisFPUpperBodyV19Actor::SetEquipmentPoseSource(USkeletalMeshComponent* InSource,FName Label)
{
    if(EquipmentPoseSource.Get()!=InSource){
        if(EquipmentPoseSource.IsValid())RemoveTickPrerequisiteComponent(EquipmentPoseSource.Get());
        EquipmentPoseSource=InSource;EquipmentFrameCached=false;
        if(InSource)AddTickPrerequisiteComponent(InSource);
    }
    EquipmentPoseLabel=Label;
}

bool AParisFPUpperBodyV19Actor::PrepareHoldingSource(''',1).replace('    TArray<FTransform> Target = InOutLocal;','    auto* EquipmentSource=EquipmentPoseSource.Get();\n    const bool Equipment=EquipmentSource&&SourceFrameCached;\n    if(Equipment)Action=EquipmentPoseLabel;\n    auto* MotionSource=Equipment?EquipmentSource:HoldingSource.Get();\n    TArray<FTransform> Target = InOutLocal;',1).replace('    if (Action == TEXT("Ready"))\n','    if (Action == TEXT("Ready")||Equipment)\n',1).replace('const auto& Ref = HoldingSource->GetSkeletalMeshAsset()->GetRefSkeleton();','const auto& Ref = MotionSource->GetSkeletalMeshAsset()->GetRefSkeleton();',1).replace('const auto& Components = HoldingSource->GetComponentSpaceTransforms();','const auto& Components = MotionSource->GetComponentSpaceTransforms();',1).replace('    if (PreviousSourcePose.IsEmpty())','''    if(Equipment){
        if(!EquipmentFrameCached){
            TArray<FTransform> EquipComponent;EquipComponent.SetNum(Target.Num());
            for(int32 I=0;I<Target.Num();++I){const int32 Parent=DisplayRef.GetParentIndex(I);EquipComponent[I]=Parent>=0?Target[I]*EquipComponent[Parent]:Target[I];}
            const int32 Hand=DisplayRef.FindBoneIndex(TEXT("hand_r"));
            const int32 HoldingHand=HoldingSource->GetSkeletalMeshAsset()->GetRefSkeleton().FindBoneIndex(TEXT("hand_r"));
            if(Hand==INDEX_NONE||HoldingHand==INDEX_NONE){BindingError=TEXT("Equipment hand frame absent");return false;}
            EquipmentRootOffset=HoldingSource->GetComponentSpaceTransforms()[HoldingHand].GetLocation()-EquipComponent[Hand].GetLocation();
            EquipmentFrameCached=true;
        }
        for(int32 I=0;I<Target.Num();++I)if(DisplayRef.GetParentIndex(I)==INDEX_NONE)Target[I].AddToTranslation(EquipmentRootOffset);
    }
    if (PreviousSourcePose.IsEmpty())''',1))
edit(project/'Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/ParisBridgeMissionV1.Build.cs',lambda t:t.replace('"AIModule", "NavigationSystem", "Json"','"AIModule", "NavigationSystem", "Json", "ParisGripBindingV18"'))
edit(p/'ParisEquipmentState.h',lambda t:t.replace('class UAnimSequence;','class USkeletalMeshComponent;\nclass UAnimSequence;').replace('    int32 OriginalAnimMode=0;','    TWeakObjectPtr<USkeletalMeshComponent> EquipmentPoseSource;\n    FString EquipmentPoseTag;\n    int32 OriginalAnimMode=0;'))
edit(p/'ParisTacticalEquipment.cpp',lambda t:t.replace('#include "ParisEquipmentState.h"','#include "ParisEquipmentState.h"\n#include "ParisFPUpperBodyV19Actor.h"'))
helper=(root/'Tools/Integration/GrenadeEquipV2/ParisGrenadeEquipPose.inl').read_text('utf-8')
(p/'ParisGrenadeEquipPose.inl').write_text(helper,encoding='utf-8')
edit(p/'ParisTacticalEquipment.cpp',lambda t:t.replace('void SelectionTick(', '#include "ParisGrenadeEquipPose.inl"\nvoid SelectionTick(',1).replace('    auto* P=UGameplayStatics::GetPlayerCharacter(W,0);\n    if(Dead(P)||(!M->AllowsPlay()', '    EquipmentPoseTick(W,S);\n    auto* P=UGameplayStatics::GetPlayerCharacter(W,0);\n    if(Dead(P)||(!M->AllowsPlay()',1))
edit(p/'ParisTacticalEquipment.cpp',lambda t:t.replace('    }\n}\nvoid EndThrow(', '    }\n    MountGrenade(W,S.SelectedVisual.Get());\n}\nvoid EndThrow(',1).replace('    BallTick(W,S,DT);SmokeTick', '    if(S.Held.IsValid())MountGrenade(W,S.Held.Get());\n    BallTick(W,S,DT);SmokeTick',1).replace('void ClearVisuals(FEquipmentSession& S){ClearSelectedVisual(S);','void ClearVisuals(FEquipmentSession& S){ClearEquipmentPose(S);ClearSelectedVisual(S);',1))
# Original prepare/release/commit/fuse functions stay byte-identical. The transient
# source follows their state after the actor tick rather than owning gameplay.
edit(p/'ParisTacticalEquipment.cpp',lambda t:t.replace('        S.EHeld=false;S.DisarmClock=0;S.InteractId.Empty();\n        if(S.PrimaryHeld)', '''        const int32 Next=NextAvailableSlot(S,S.SelectedSlot,Wheel);
        if(Next==S.SelectedSlot)return true;
        S.EHeld=false;S.DisarmClock=0;S.InteractId.Empty();
        if(S.PrimaryHeld)''',1).replace('S.SelectedSlot=(S.SelectedSlot+Wheel+3)%3;','S.SelectedSlot=Next;',1))
edit(p/'ParisCombatUI.cpp',lambda t:t.replace('Cycle rifle, frag and smoke; up reverses the order','Cycle available equipment; empty types are skipped'))
print('Authored grenade display source and available inventory wheel')
