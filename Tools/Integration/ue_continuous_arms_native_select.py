"""Select verified native owner display in team city; preserve exact V3 before bytes."""
import hashlib,json,os,sys,traceback
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[2];STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
sys.path.insert(0,str(Path(__file__).parent))
from ue_continuous_arms_native_runtime import PACKAGE,native_record
from ue_continuous_arms_runtime_trial import trial_records
OUT=STORE/'Evidence/ContinuousArmsNativeV1'/os.environ['CS549_ARMS_NATIVE_IDENTITY']
assert not OUT.exists();OUT.mkdir(parents=True)
DEST=ROOT/'Assets/Integration/CITY_CONTINUOUS_ARMS_NATIVE_INVENTORY_20261003.json'
assert not DEST.exists(),'Preserve occupied selection identity'
motion=json.loads((OUT.parent/'motion_v1/result.json').read_text())
combat=json.loads((STORE/'Evidence/CityGameplay20261002/Runtime/native_combat_v1/combat.json').read_text())
assert motion['status']=='native_motion_numeric_pass_requires_image_review' and not motion['errors'] and motion['native_bytes_unchanged']
assert all(motion['checks']['movement'].values()) and all(v for k,v in motion['checks'].items() if k!='movement')
assert combat['all_assertions_passed'] and combat['native_bytes_unchanged'] and not combat['errors']
review=json.loads((OUT.parent/'motion_v1/IMAGE_REVIEW.json').read_text())
assert review['actual_game_views_inspected'] and review['no_new_geometry_failure_observed']
records=trial_records()+[native_record()]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert all(sha(ROOT/f['path'])==f['sha256'] for f in records)
ENTRY='/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1'
map_record=next(f for f in records if f.get('package')==ENTRY)
backup=OUT/'BeforeNativeSelection.umap';backup.write_bytes((ROOT/map_record['path']).read_bytes());assert sha(backup)==map_record['sha256']
r={'status':'selecting','errors':[],'old_map':map_record,'backup':backup.relative_to(ROOT).as_posix(),'native_saved':False}
try:
    levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    subsystem=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors=subsystem.get_all_level_actors();player=next(a for a in actors if a.get_actor_label()=='PC_City_Player')
    assert not any(a.get_class().get_name()=='BP_PC_ContinuousArmsNativeV1_C' for a in actors)
    cls=unreal.EditorAssetLibrary.load_blueprint_class(PACKAGE)
    display=subsystem.spawn_actor_from_class(cls,player.get_actor_location(),unreal.Rotator())
    display.set_actor_label('PC_Player_ContinuousArmsNativeV1');display.set_editor_property('Combatant',player)
    assert levels.save_current_level();r['native_saved']=True
    assert all(sha(ROOT/f['path'])==f['sha256'] for f in records if f['path']!=map_record['path'])
    new=json.loads(json.dumps(records))
    for f in new:
        p=ROOT/f['path'];f.update(size_bytes=p.stat().st_size,sha256=sha(p))
    inventory={'schema_version':1,'date':'2026-10-03','owner':'yg745','status':'local_selected_unpublished_not_catalog_restore_authority',
       'scope':'Saved team-map native Blueprint first-person display; original source/camera/gunplay/NPC retained','files':new,'file_count':len(new),
       'total_size_bytes':sum(f['size_bytes'] for f in new),'previous_checkpoint':'CITY_RIFLE_ACTION_DRAFT_INVENTORY_20261002.json',
       'previous_map_private_backup':r['backup'],'plan':'Docs/Development/CONTINUOUS_ARMS_NATIVE_IMPLEMENTATION_V1.md',
       'runtime_display_python_required':False,'human_model_review':'Yupu reports preview model looks fine; stutter reported; native migration authorized',
       'native_motion_evidence':str(motion['status']),'native_combat_evidence':'native_combat_v1','selected_map_fresh_test_pending':True,
       'generic_m1_reload_gap':True,'performance_acceptance':False}
    DEST.write_text(json.dumps(inventory,indent=2)+'\n');r['new_inventory']=DEST.relative_to(ROOT).as_posix();r['status']='selected_native_display_requires_fresh_city_regression'
except Exception:r['status']='failed_preserve_selection_state';r['errors'].append(traceback.format_exc())
finally:
    (OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n');unreal.SystemLibrary.quit_editor()
