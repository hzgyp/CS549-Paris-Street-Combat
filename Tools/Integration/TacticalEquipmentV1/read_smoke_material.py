import unreal,json
from pathlib import Path
out=Path(r'D:\0.Rutgers\CS549\Project-New\tmp\g1-tactical-equipment-20261010\smoke-material-audit')
out.mkdir(exist_ok=True)
root='/Game/WW2City/Library_Meshingun/VFX_Meshingun/SmokeFog/Material/'
rows=[]
for name in ['MI_Smoke','MI_Smoke_Inst','M_SubUV_Blend']:
    obj=unreal.load_asset(root+name)
    lib=unreal.MaterialEditingLibrary
    r=dict(path=obj.get_path_name(),scalars={},vectors={})
    inst=isinstance(obj,unreal.MaterialInstanceConstant)
    for key in lib.get_scalar_parameter_names(obj):
        r['scalars'][str(key)]=float(lib.get_material_instance_scalar_parameter_value(obj,key) if inst else lib.get_material_default_scalar_parameter_value(obj,key))
    for key in lib.get_vector_parameter_names(obj):
        v=lib.get_material_instance_vector_parameter_value(obj,key) if inst else lib.get_material_default_vector_parameter_value(obj,key)
        r['vectors'][str(key)]=str(v)
    rows.append(r)
(out/'MATERIALS.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
unreal.log('PARIS_SMOKE_READ_ONLY_MATERIAL_AUDIT_COMPLETE')
