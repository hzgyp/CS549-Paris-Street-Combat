"""Component-only owner-view cloth correction; preserve source clothing and physics."""
import hashlib,json,os,shutil,sys,traceback
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from ue_first_person_view_runtime import trial_records,VIEW,EVIDENCE
from ue_paris_graph_helpers import lib
OUT=EVIDENCE/os.environ['CS549_FP_IDENTITY'];assert not OUT.exists();OUT.mkdir()
inventory=ROOT/'Assets/Integration/FIRST_PERSON_VIEW_TRIAL_INVENTORY_20261002.json'
record=json.loads(inventory.read_text());trial_records()
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
shutil.copy2(inventory,OUT/'before_inventory.json')
for f in record['files']:
    p=ROOT/f['path'];copy=OUT/p.name;shutil.copy2(p,copy);assert digest(copy)==f['sha256']
r={'scope':__doc__,'errors':[],'status':'initializing'}
try:
    bp=unreal.load_asset(VIEW)
    cdo=unreal.get_default_object(unreal.EditorAssetLibrary.load_blueprint_class(VIEW))
    mesh=cdo.get_component_by_class(unreal.SkeletalMeshComponent)
    r['before']={n:mesh.get_editor_property(n) for n in ('disable_cloth_simulation','cloth_blend_weight')}
    mesh.set_editor_property('disable_cloth_simulation',True)
    mesh.set_editor_property('cloth_blend_weight',0.0)
    r['after']={n:mesh.get_editor_property(n) for n in ('disable_cloth_simulation','cloth_blend_weight')}
    assert lib.compile_blueprint(bp)
    assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
    for f in record['files']:
        p=ROOT/f['path'];f.update(size_bytes=p.stat().st_size,sha256=digest(p))
    record['previous_revision_backup']=OUT.relative_to(ROOT).as_posix()
    record['view_only_cloth']=r['after']
    record['status']='unselected_cloth_corrected_draft_requires_fresh_visual_and_combat_tests'
    inventory.write_text(json.dumps(record,indent=2)+'\n')
    r['status']='saved_only_owner_view_component_cloth_flags';r['files']=record['files']
except Exception:r['status']='failed';r['errors'].append(traceback.format_exc())
(OUT/'result.json').write_text(json.dumps(r,indent=2));unreal.SystemLibrary.quit_editor()
