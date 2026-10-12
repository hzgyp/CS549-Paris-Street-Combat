"""Narrow runtime visual-only adaptation of the frozen 73-file parent."""
from pathlib import Path
root=Path(__file__).resolve().parents[3]
private=root/'tmp/g1-tactical-equipment-20261010/candidate_grenade_models_v1/Project/Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private'
template=(private/'ParisPressureMineMesh.inl').read_text('utf-8')
template=template[:template.index('\nvoid PressureMineVisual')]
template=template.replace('PressureMine','Grenade').replace('pressure mine','grenade').replace('Pressure mine','Grenade')
template=template.replace('GrenadeMeshCache;', 'GrenadeMeshCaches[2];').replace('GrenadeMaterialCache;', 'GrenadeMaterialCaches[2];')
template=template.replace('GrenadeMesh(UWorld* W){','GrenadeMesh(UWorld* W,const FString& Kind){\n    const int32 Index=Kind==TEXT("Frag")?0:1;const FString Stem=Index==0?TEXT("frag"):TEXT("smoke");\n    auto& GrenadeMeshCache=GrenadeMeshCaches[Index];auto& GrenadeMaterialCache=GrenadeMaterialCaches[Index];')
template=template.replace('TEXT("../../Equipment/Mine")','TEXT("../../Equipment/Grenades"),Kind')
template=template.replace('TEXT("mine_geometry.json")','(Stem+TEXT("_geometry.json"))')
template=template.replace('Count==10809','Count==(Index==0?2733:7562)')
for k in ['albedo','orm','normal']:template=template.replace('TEXT("mine_'+k+'.png")','(Stem+TEXT("_'+k+'.png"))')
template=template.replace('<40','<18').replace('TEXT("Blender exterior 10809 triangles / baked PBR / transient shader instance")','Kind+TEXT(" exterior / PBR / fixed original attachment")')
template+='''
void GrenadeVisual(UWorld* W,AActor* A,const FString& Kind){
    auto* C=NewObject<UStaticMeshComponent>(A);A->AddInstanceComponent(C);
    C->SetStaticMesh(GrenadeMesh(W,Kind));C->SetupAttachment(A->GetRootComponent());
    C->SetCollisionEnabled(ECollisionEnabled::NoCollision);C->SetCanEverAffectNavigation(false);C->RegisterComponent();
}
'''
(private/'ParisGrenadeMesh.inl').write_text(template,encoding='utf-8')
p=private/'ParisTacticalEquipment.cpp';text=p.read_text('utf-8')
start=text.index('AActor* Prop(');end=text.index('\n}',text.index('return A;',start))+2
old=text[start:end]
new=old[:old.index('const FLinearColor')]+'''if(Kind==TEXT("Frag")||Kind==TEXT("Smoke"))GrenadeVisual(W,A,Kind);return A;}'''
text=text[:start]+'#include "ParisGrenadeMesh.inl"\n'+new+text[end:]
assert 'Part(A,TEXT("Sphere"),FVector(.065' not in text
p.write_text(text,encoding='utf-8')
print('Authored Prop only + transient PBR helper; original BeginThrow/CommitThrow/save unchanged')
