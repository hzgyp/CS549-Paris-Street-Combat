"""Read-only material prerequisites, no asset setters/save/import."""
from pathlib import Path
import unreal,json
out=Path(r'D:/0.Rutgers/CS549/Project-New/tmp/g1-player-death-20261011/material-audit-v1');out.mkdir(exist_ok=True)
result=[];lib=unreal.MaterialEditingLibrary
for path in ['/Game/WW2City/Library_Meshingun/VFX_Meshingun/Firework/Material/M_Glow','/Game/MsvFx_MuzzleFlash_Pack/Sources/Materials/InstanceMTL/MI_Muzzle_Flash_01','/Game/MsvFx_MuzzleFlash_Pack/Sources/Materials/MasterMTL/M_Muzzle_Flash']:
    obj=unreal.load_asset(path);r=dict(path=path,loaded=bool(obj))
    if obj:
        inst=isinstance(obj,unreal.MaterialInstanceConstant);r['class']=obj.get_class().get_name();r['scalars']={};r['vectors']={}
        for key in lib.get_scalar_parameter_names(obj):r['scalars'][str(key)]=float(lib.get_material_instance_scalar_parameter_value(obj,key) if inst else lib.get_material_default_scalar_parameter_value(obj,key))
        for key in lib.get_vector_parameter_names(obj):r['vectors'][str(key)]=str(lib.get_material_instance_vector_parameter_value(obj,key) if inst else lib.get_material_default_vector_parameter_value(obj,key))
        if not inst:
            for field in ['blend_mode','shading_model']:
                try:r[field]=str(obj.get_editor_property(field))
                except Exception as e:r[field+'_unavailable']=str(e)
    result.append(r)
(out/'MATERIALS.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
unreal.log('PARIS_DEATH_READ_ONLY_MATERIAL_AUDIT_COMPLETE')
