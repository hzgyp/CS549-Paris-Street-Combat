"""Same-geometry owner-view forearm mask; source materials and mesh remain untouched."""
import hashlib,json,os,shutil,sys,traceback
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from ue_first_person_view_runtime import trial_records,VIEW,EVIDENCE,STORE
from ue_paris_graph_helpers import lib
OUT=EVIDENCE/os.environ['CS549_FP_IDENTITY'];assert not OUT.exists();OUT.mkdir()
inventory=ROOT/'Assets/Integration/FIRST_PERSON_VIEW_TRIAL_INVENTORY_20261002.json'
record=json.loads(inventory.read_text());trial_records()
audit=json.loads((EVIDENCE/'material_audit_v1/result.json').read_text());assert not audit['errors'] and audit['clothing_asset_count']==0
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
shutil.copy2(inventory,OUT/'before_inventory.json')
for f in record['files']:
    p=ROOT/f['path'];copy=OUT/p.name;shutil.copy2(p,copy);assert digest(copy)==f['sha256']
r={'scope':__doc__,'errors':[],'status':'initializing','material_compilation':{}}
try:
    packages=[];assignments={};assets=[];editing=unreal.MaterialEditingLibrary
    for slot,label in ((2,'Sleeves'),(8,'Hands')):
        info=audit['materials'][str(slot)]
        source_instance=unreal.load_asset(info['instance']);source_base=unreal.load_asset(info['base'])
        assert source_instance.get_editor_property('parent')==source_base
        base_path='/Game/ParisCombat/Materials/FirstPersonViewV1/M_PC_FirstPerson'+label+'V1'
        instance_path='/Game/ParisCombat/Materials/FirstPersonViewV1/MI_PC_FirstPerson'+label+'V1'
        assert not unreal.EditorAssetLibrary.does_asset_exist(base_path) and not unreal.EditorAssetLibrary.does_asset_exist(instance_path)
        base=unreal.EditorAssetLibrary.duplicate_asset(source_base.get_path_name(),base_path)
        instance=unreal.EditorAssetLibrary.duplicate_asset(source_instance.get_path_name(),instance_path)
        assert base and instance
        base.set_editor_property('blend_mode',unreal.BlendMode.BLEND_MASKED)
        position=editing.create_material_expression(base,unreal.MaterialExpressionPreSkinnedPosition,-600,600)
        mask=editing.create_material_expression(base,unreal.MaterialExpressionCustom,-300,600)
        mask.set_editor_property('description','Owner-view forearms only; source vertices and pose unchanged')
        custom_input=unreal.CustomInput();custom_input.set_editor_property('input_name','P')
        mask.set_editor_property('inputs',[custom_input])
        mask.set_editor_property('code','return step(30.0, abs(P.x));')
        assert editing.connect_material_expressions(position,'',mask,'P')
        assert editing.connect_material_property(mask,'',unreal.MaterialProperty.MP_OPACITY_MASK)
        errors=editing.recompile_material(base);r['material_compilation'][label]=[str(e) for e in errors];assert not errors
        editing.set_material_instance_parent(instance,base);editing.update_material_instance(instance)
        packages.extend((base_path,instance_path));assets.extend((base,instance));assignments[slot]=instance
    bp=unreal.load_asset(VIEW)
    cdo=unreal.get_default_object(unreal.EditorAssetLibrary.load_blueprint_class(VIEW))
    mesh=cdo.get_component_by_class(unreal.SkeletalMeshComponent)
    for slot,instance in assignments.items():mesh.set_material(slot,instance)
    mesh.set_editor_property('disable_cloth_simulation',False);mesh.set_editor_property('cloth_blend_weight',1.0)
    assert lib.compile_blueprint(bp)
    for asset in assets+[bp]:assert unreal.EditorAssetLibrary.save_loaded_asset(asset,only_if_is_dirty=False)
    for package in packages:
        p=STORE/('Content/'+package.removeprefix('/Game/')+'.uasset')
        record['files'].append({'package':package,'path':p.relative_to(ROOT).as_posix()})
    for f in record['files']:
        p=ROOT/f['path'];f.update(size_bytes=p.stat().st_size,sha256=digest(p))
    record['previous_revision_backup']=OUT.relative_to(ROOT).as_posix()
    record['view_only_cloth']={'disable_cloth_simulation':False,'cloth_blend_weight':1.0,'source_clothing_assets':0}
    record['view_only_material_mask']='abs(PreSkinnedPosition.x) >= 30 cm; slots 2 and 8 only'
    record['status']='unselected_forearm_view_draft_requires_fresh_visual_and_combat_tests'
    inventory.write_text(json.dumps(record,indent=2)+'\n')
    r['status']='saved_only_new_materials_and_view';r['files']=record['files']
except Exception:r['status']='failed';r['errors'].append(traceback.format_exc())
(OUT/'result.json').write_text(json.dumps(r,indent=2));unreal.SystemLibrary.quit_editor()
