"""New FP sleeve experiment import only; original skeleton/materials never saved."""
import hashlib,json,os,sys,traceback
from pathlib import Path
import unreal
sys.path.insert(0,str(Path(__file__).parent))
from common import ROOT,STORE,records,check
OUT=STORE/'Evidence/ReloadRepairV5'/os.environ['CS549_RELOAD_V5_IDENTITY'];assert not OUT.exists();OUT.mkdir()
(OUT/'source.py').write_bytes(Path(__file__).read_bytes());rows=records()
BASE='/Game/ParisCombat/Characters/ReloadRepairV5';NAME='SK_PC_SleeveWeightsV5';MESH=BASE+'/'+NAME
SRC='/Game/ParisCombat/Characters/FirstPersonContinuousArmsV3/SK_PC_ContinuousArmsV3'
r={'scope':__doc__,'errors':[],'packages':[],'map_saved':False,'visual_acceptance':False}
try:
    assert check(rows) and not unreal.EditorAssetLibrary.does_directory_exist(BASE)
    validation=json.loads((STORE/'Evidence/ReloadRepairV5/sleeve_weights_validate_v1/result.json').read_text())
    assert validation['fresh_import_pass'] and not validation['errors']
    original=unreal.load_asset(SRC);options=unreal.FbxImportUI()
    for name,value in {'import_mesh':True,'import_as_skeletal':True,'mesh_type_to_import':unreal.FBXImportType.FBXIT_SKELETAL_MESH,'automated_import_should_detect_type':False,'import_animations':False,'import_materials':False,'import_textures':False,'create_physics_asset':False,'skeleton':None}.items():options.set_editor_property(name,value)
    data=options.get_editor_property('skeletal_mesh_import_data')
    for name,value in {'update_skeleton_reference_pose':False,'use_t0_as_ref_pose':False,'import_uniform_scale':1.0}.items():data.set_editor_property(name,value)
    task=unreal.AssetImportTask();task.filename=str(STORE/'Evidence/ReloadRepairV5/sleeve_weights_offline_v2/SK_PC_SleeveWeightsV5.fbx');task.destination_path=BASE;task.destination_name=NAME
    task.automated=True;task.replace_existing=False;task.save=False;task.options=options
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task]);r['imported_paths']=list(task.imported_object_paths)
    mesh=unreal.load_asset(MESH);assert mesh and mesh.get_editor_property('skeleton')!=original.get_editor_property('skeleton')
    source_rows=original.get_editor_property('materials');source_map={str(m.material_slot_name):m.material_interface for m in source_rows}
    dest=mesh.get_editor_property('materials');r['materials']=[]
    for i,m in enumerate(dest):
        name=str(m.material_slot_name);assert name in source_map,(name,list(source_map));m.material_interface=source_map[name];dest[i]=m
        r['materials'].append({'slot':name,'native':m.material_interface.get_path_name()})
    mesh.set_editor_property('materials',dest)
    editor=unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem)
    a=unreal.new_object(unreal.SkeletalMeshComponent);a.set_skeletal_mesh_asset(original)
    b=unreal.new_object(unreal.SkeletalMeshComponent);b.set_skeletal_mesh_asset(mesh)
    an=[str(a.get_bone_name(i)) for i in range(a.get_num_bones())];bn=[str(b.get_bone_name(i)) for i in range(b.get_num_bones())]
    assert an==bn,'Bone order/hierarchy differs';r['bones']=len(an)
    assert all(str(editor.get_bone_parent(original,n))==str(editor.get_bone_parent(mesh,n)) for n in an)
    r['reference_translation_max_cm']=0.;r['reference_axis_max_delta']=0.
    for i,n in enumerate(an):
        t=a.get_ref_pose_transform(i);u=b.get_ref_pose_transform(i)
        r['reference_translation_max_cm']=max(r['reference_translation_max_cm'],(t.translation-u.translation).length())
        r['reference_axis_max_delta']=max(r['reference_axis_max_delta'],max((unreal.MathLibrary.transform_direction(t,v)-unreal.MathLibrary.transform_direction(u,v)).length() for v in (unreal.Vector(1,0,0),unreal.Vector(0,1,0),unreal.Vector(0,0,1))))
    assert r['reference_translation_max_cm']<.01 and r['reference_axis_max_delta']<.001
    for asset in (mesh,mesh.get_editor_property('skeleton')):
        assert asset.get_path_name().startswith(BASE+'/');assert unreal.EditorAssetLibrary.save_loaded_asset(asset,False)
    for p in sorted((STORE/'Content/ParisCombat/Characters/ReloadRepairV5').glob('*.uasset')):
        r['packages'].append({'path':p.relative_to(ROOT).as_posix(),'size_bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    assert len(r['packages'])==2 and check(rows);r['mesh_package']=MESH;r['status']='new_only_import_pass_requires_same_view_validation'
except Exception:r['errors'].append(traceback.format_exc());r['status']='failed_preserve_stop'
finally:
    r['protected_count']=len(rows);r['protected_records_unchanged']=check(rows)
    (OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n');unreal.log('CS549_SLEEVE_IMPORT '+r['status']);unreal.SystemLibrary.quit_editor()
