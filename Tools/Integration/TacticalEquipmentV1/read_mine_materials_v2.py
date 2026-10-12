"""Read-only parameter audit; no asset/map saves."""
import unreal,json
from pathlib import Path
out=Path(r'D:/0.Rutgers/CS549/Project-New/tmp/g1-pressure-mine-20261011/material-audit-v2')
out.mkdir(parents=True,exist_ok=True)
lib=unreal.MaterialEditingLibrary
paths=['/InterchangeAssets/gltf/MaterialInstances/MI_Default_Opaque_DS', '/Engine/BasicShapes/BasicShapeMaterial','/Game/ParisCombat/Weapons/GermanRifleUEV1/ImportV1/GermanRifle_FineWood_V15/Materials/V15_FineWalnut_Handguard']
rows=[]
for path in paths:
    obj=unreal.load_asset(path)
    assert obj,path
    inst=isinstance(obj,unreal.MaterialInstanceConstant)
    row={'path':obj.get_path_name(),'parent':str(obj.get_editor_property('parent')) if inst else None,'scalars':{},'vectors':{},'textures':{},'switches':[]}
    for key in lib.get_scalar_parameter_names(obj):
        row['scalars'][str(key)]=float(lib.get_material_instance_scalar_parameter_value(obj,key) if inst else lib.get_material_default_scalar_parameter_value(obj,key))
    for key in lib.get_vector_parameter_names(obj):
        row['vectors'][str(key)]=str(lib.get_material_instance_vector_parameter_value(obj,key) if inst else lib.get_material_default_vector_parameter_value(obj,key))
    for key in lib.get_texture_parameter_names(obj):
        tex=lib.get_material_instance_texture_parameter_value(obj,key) if inst else lib.get_material_default_texture_parameter_value(obj,key)
        row['textures'][str(key)]=tex.get_path_name() if tex else None
    if hasattr(lib,'get_static_switch_parameter_names'):
        for key in lib.get_static_switch_parameter_names(obj): row['switches'].append({'name':str(key),'value':bool(lib.get_material_instance_static_switch_parameter_value(obj,key)) if inst else None})
    rows.append(row)
(out/'MATERIALS.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
unreal.log('PARIS_MINE_READ_ONLY_MATERIAL_AUDIT_COMPLETE')
