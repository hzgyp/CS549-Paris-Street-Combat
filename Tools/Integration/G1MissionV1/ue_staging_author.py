"""Save only visually reviewed allied staging and owned mission fingerprint."""
import json,os,shutil,sys,traceback
from pathlib import Path
import unreal
ROOT=Path(os.environ['CS549_G1_ROOT']);sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import STORE,guard_rows,guards_match,digest,package_file
from ue_formal_roster import actor_state,xyz
OUT=Path(os.environ['CS549_G1_OUT']);rows=guard_rows();report={'status':'initializing','errors':[],'map_saved':False}
config_file=STORE/'Evidence/G1MissionV1/staging_config_v2_20261008/config.json';config=json.loads(config_file.read_text())
prior=json.loads((STORE/'Evidence/G1MissionV1/bridge_hook_v1_20261008/result.json').read_text())
trial=STORE/'Evidence/G1MissionV1/spawn_view_v1_20261008'
try:
 proof=json.loads((trial/'result.json').read_text());review=json.loads((trial/'visual_review.json').read_text())
 assert proof['status']=='pass_spawnview_native_mission' and proof['protected_unchanged'] and all(proof['checks'].values())
 assert json.loads((trial/'audit.json').read_text())['status']=='pass_native_entry_audit'
 assert review['accepted_staging'] and review['config_sha256']==digest(config_file)
 assert all(digest(ROOT/f['path'])==f['sha256'] for f in review['images'])
 assert guards_match(rows) and all(digest(ROOT/f['path'])==f['sha256'] for f in prior['files'])
 old_slots=list((ROOT/'Unreal/ParisStreetCombat/Saved/SaveGames').glob('G1Functional2_20261008_*.sav'))
 report['old_controls']={p.relative_to(ROOT).as_posix():digest(p) for p in old_slots};assert len(old_slots)==2
 f=package_file(config['map']);shutil.copy2(f,OUT/'candidate_before.umap');assert digest(f)==digest(OUT/'candidate_before.umap')
 levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert levels.load_level(config['map'])
 editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);world=editor.get_editor_world()
 aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors();lookup={a.get_actor_label():a for a in aa}
 mesh=next(a for a in aa if isinstance(a,unreal.RecastNavMesh));before=json.loads(unreal.ParisMapSurveyLibrary.export_navmesh(mesh))
 report['before']=[actor_state(lookup[p['label']]) for p in config['roster']]
 for p in config['roster'][:3]:
  a=lookup[p['label']];feet=p['feet_cm'];h=a.capsule_component.get_scaled_capsule_half_height()
  assert a.set_actor_location_and_rotation(unreal.Vector(feet[0],feet[1],feet[2]+h+.5),unreal.Rotator(pitch=0,yaw=p['yaw'],roll=0),False,True)
 report['after']=[actor_state(lookup[p['label']]) for p in config['roster']]
 for i,(a,b) in enumerate(zip(report['before'],report['after'])):
  assert all(a[k]==b[k] for k in a if i>=3 or k not in ('location','rotation')),(i,a,b)
 mission=next(a for a in aa if isinstance(a,unreal.ParisBridgeMission))
 mission.set_editor_property('config_fingerprint',config['fingerprint']);mission.set_editor_property('slot_prefix',config['slot_prefix'])
 after=json.loads(unreal.ParisMapSurveyLibrary.export_navmesh(mesh));assert before==after
 assert guards_match(rows) and levels.save_current_level();report['map_saved']=True
 report['files']=[dict(x) for x in prior['files']]
 for x in report['files']:
  p=ROOT/x['path'];x.update(size_bytes=p.stat().st_size,sha256=digest(p))
 report.update(nav_tiles=after['active_tiles'],nav_polygons=len(after['polygons']),collision_restored=True,
  config_sha256=digest(config_file),config_fingerprint=config['fingerprint'],slot_prefix=config['slot_prefix'],
  protected_unchanged=guards_match(rows),old_controls_unchanged=all(digest(ROOT/p)==h for p,h in report['old_controls'].items()))
 assert report['protected_unchanged'] and report['old_controls_unchanged']
 report['status']='pass_visible_nearbank_staging_saved_runtime_unpassed'
except Exception:report['status']='failed_staging_author_preserve';report['errors'].append(traceback.format_exc());report['protected_unchanged']=guards_match(rows)
(OUT/'result.json').write_text(json.dumps(report,indent=2)+'\n');unreal.SystemLibrary.quit_editor()
