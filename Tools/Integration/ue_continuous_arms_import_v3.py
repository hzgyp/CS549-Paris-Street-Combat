"""Import only the new complete-arm derivative; original skeleton and map never saved."""
import hashlib, json, os, traceback
from pathlib import Path
import unreal

ROOT=Path(__file__).resolve().parents[2]
EVIDENCE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/ContinuousArmsV3'
OUT=EVIDENCE/os.environ.get('CS549_ARMS_IMPORT_IDENTITY','native_import_v1')
assert not OUT.exists();OUT.mkdir()
(OUT/'source.py').write_bytes(Path(__file__).read_bytes())
records=json.loads((ROOT/'Failures/FP001-20261003-first-person-view/MANIFEST.json').read_text(encoding='utf-8-sig'))['protected_files']
assert json.loads((EVIDENCE/'exchange_v1/roundtrip_precision_v1.json').read_text())['passed']
BASE='/Game/ParisCombat/Characters/FirstPersonContinuousArmsV3'
MESH=BASE+'/SK_PC_ContinuousArmsV3'
SOURCE='/Game/ParisCombat/Characters/Adaptation/Meshes/SK_WWII_US_Paratrooper_simple_UE582_v1'
r={'scope':__doc__,'errors':[],'native_files':[],'saved_city_changed':False,'visual_acceptance':False}

def guard():
    return all((ROOT/f['path']).stat().st_size==f['size_bytes'] and hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256'] for f in records)

try:
    assert guard()
    assert not unreal.EditorAssetLibrary.does_asset_exist(MESH), 'Preserve occupied native identity'
    original=unreal.load_asset(SOURCE)
    options=unreal.FbxImportUI()
    options.set_editor_property('import_mesh',True)
    options.set_editor_property('import_as_skeletal',True)
    options.set_editor_property('mesh_type_to_import',unreal.FBXImportType.FBXIT_SKELETAL_MESH)
    options.set_editor_property('automated_import_should_detect_type',False)
    options.set_editor_property('import_animations',False)
    options.set_editor_property('import_materials',False)
    options.set_editor_property('import_textures',False)
    options.set_editor_property('create_physics_asset',False)
    # Deliberately no original skeleton binding: importer cannot merge into it.
    options.set_editor_property('skeleton',None)
    data=options.get_editor_property('skeletal_mesh_import_data')
    data.set_editor_property('update_skeleton_reference_pose',False)
    data.set_editor_property('use_t0_as_ref_pose',False)
    data.set_editor_property('import_uniform_scale',1.0)
    task=unreal.AssetImportTask()
    task.filename=str(EVIDENCE/'exchange_v1/SK_PC_ContinuousArmsV3.fbx')
    task.destination_path=BASE;task.destination_name='SK_PC_ContinuousArmsV3'
    task.automated=True;task.replace_existing=False;task.save=False;task.options=options
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    r['imported_paths']=list(task.imported_object_paths)
    mesh=unreal.load_asset(MESH)
    assert mesh
    assert mesh.get_editor_property('skeleton')!=original.get_editor_property('skeleton')
    source_rows=original.get_editor_property('materials')
    source_map={m.material_interface.get_name():m.material_interface for m in source_rows if m.material_interface}
    dest_rows=mesh.get_editor_property('materials')
    r['materials']=[]
    for slot_index,row in enumerate(dest_rows):
        name=str(row.material_slot_name).replace('_portable','')
        material=source_map.get(name)
        assert material, f'Unmapped material {name}: {list(source_map)}'
        row.material_interface=material
        dest_rows[slot_index]=row
        r['materials'].append({'slot':str(row.material_slot_name),'native':material.get_path_name()})
    mesh.modify();mesh.set_editor_property('materials',dest_rows)
    editor=unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem)
    a=unreal.new_object(unreal.SkeletalMeshComponent);a.set_skeletal_mesh_asset(original)
    b=unreal.new_object(unreal.SkeletalMeshComponent);b.set_skeletal_mesh_asset(mesh)
    source_names=[str(a.get_bone_name(i)) for i in range(a.get_num_bones())]
    new_names=[str(b.get_bone_name(i)) for i in range(b.get_num_bones())]
    r['source_bones']=source_names;r['new_bones']=new_names
    r['missing_source_bones']=sorted(set(source_names)-set(new_names))
    r['extra_bones']=sorted(set(new_names)-set(source_names))
    r['parent_mismatches']=[n for n in source_names if n in new_names and str(editor.get_bone_parent(original,n))!=str(editor.get_bone_parent(mesh,n))]
    required=[n for n in source_names if any(k in n for k in ('arm','hand','thumb','index','middle','ring','pinky','spine','clavicle'))]
    assert not (set(required)-set(new_names)),r
    assert not [n for n in r['parent_mismatches'] if n in required],r
    r['reference_bones']={}
    for n in required:
        t=a.get_ref_pose_transform(source_names.index(n));u=b.get_ref_pose_transform(new_names.index(n))
        r['reference_bones'][n]={'translation_delta_cm':(t.translation-u.translation).length(),
                                'axis_max_delta':max((unreal.MathLibrary.transform_direction(t,v)-unreal.MathLibrary.transform_direction(u,v)).length() for v in (unreal.Vector(1,0,0),unreal.Vector(0,1,0),unreal.Vector(0,0,1)))}
    r['reference_translation_max_cm']=max(v['translation_delta_cm'] for v in r['reference_bones'].values())
    r['reference_axis_max_delta']=max(v['axis_max_delta'] for v in r['reference_bones'].values())
    assert r['reference_translation_max_cm']<.01 and r['reference_axis_max_delta']<.001,r
    for asset in (mesh,mesh.get_editor_property('skeleton')):
        assert asset.get_path_name().startswith(BASE+'/')
        assert unreal.EditorAssetLibrary.save_loaded_asset(asset,False)
    assert guard()
    content=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Content/ParisCombat/Characters/FirstPersonContinuousArmsV3'
    for p in sorted(content.glob('*.uasset')):
        r['native_files'].append({'path':p.relative_to(ROOT).as_posix(),'size_bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    r['protected_40_unchanged']=True;r['status']='native_import_checked_not_visual_acceptance'
except Exception:
    r['errors'].append(traceback.format_exc());r['status']='failed'
finally:
    r['protected_40_unchanged']=guard()
    (OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    unreal.log('CS549_CONTINUOUS_ARMS_IMPORT '+r['status'])
