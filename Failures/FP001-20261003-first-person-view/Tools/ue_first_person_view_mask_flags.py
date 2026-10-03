"""Audit effective blending and explicitly select masked rendering on the two new instances."""
import hashlib,json,os,shutil,sys,traceback
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from ue_first_person_view_runtime import trial_records,EVIDENCE
OUT=EVIDENCE/os.environ['CS549_FP_IDENTITY'];assert not OUT.exists();OUT.mkdir()
inventory=ROOT/'Assets/Integration/FIRST_PERSON_VIEW_TRIAL_INVENTORY_20261002.json'
record=json.loads(inventory.read_text());trial_records()
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
shutil.copy2(inventory,OUT/'before_inventory.json')
for f in record['files']:
    p=ROOT/f['path'];copy=OUT/p.name;shutil.copy2(p,copy);assert digest(copy)==f['sha256']
r={'scope':__doc__,'errors':[],'materials':{},'status':'initializing'}
try:
    for label in ('Sleeves','Hands'):
        base=unreal.load_asset('/Game/ParisCombat/Materials/FirstPersonViewV1/M_PC_FirstPerson'+label+'V1')
        instance=unreal.load_asset('/Game/ParisCombat/Materials/FirstPersonViewV1/MI_PC_FirstPerson'+label+'V1')
        r['materials'][label]={'base_effective_blend_before':str(base.get_blend_mode()),'instance_effective_blend_before':str(instance.get_blend_mode())}
        overrides=instance.get_editor_property('base_property_overrides')
        overrides.set_editor_property('override_blend_mode',True)
        overrides.set_editor_property('blend_mode',unreal.BlendMode.BLEND_MASKED)
        instance.set_editor_property('base_property_overrides',overrides)
        unreal.MaterialEditingLibrary.update_material_instance(instance)
        r['materials'][label]['instance_effective_blend_after']=str(instance.get_blend_mode())
        assert instance.get_blend_mode()==unreal.BlendMode.BLEND_MASKED
        assert unreal.EditorAssetLibrary.save_loaded_asset(instance,only_if_is_dirty=False)
    for f in record['files']:
        p=ROOT/f['path'];f.update(size_bytes=p.stat().st_size,sha256=digest(p))
    record['previous_revision_backup']=OUT.relative_to(ROOT).as_posix()
    record['masked_material_opaque_assumption']=r['materials']
    record['status']='unselected_mask_flag_corrected_draft_requires_fresh_runtime_and_human_review'
    inventory.write_text(json.dumps(record,indent=2)+'\n')
    r['status']='saved_new_masked_material_flags';r['files']=record['files']
except Exception:r['status']='failed';r['errors'].append(traceback.format_exc())
(OUT/'result.json').write_text(json.dumps(r,indent=2));unreal.SystemLibrary.quit_editor()
