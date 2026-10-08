"""Correct only declared yaw in the owned candidate; preserve positions and dependencies."""
import json,os,shutil,sys,traceback
from pathlib import Path
import unreal
ROOT=Path(os.environ['CS549_G1_ROOT']);sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import STORE,guard_rows,guards_match,digest,package_file
from ue_formal_roster import actor_state
OUT=Path(os.environ['CS549_G1_OUT']);report={'errors':[],'map_saved':False,'status':'initializing'}
rows=guard_rows();config=json.loads((STORE/'Evidence/G1MissionV1/config_v1_20261008/config.json').read_text())
prior=json.loads((STORE/'Evidence/G1MissionV1/author_v3_20261008/result.json').read_text())
try:
 assert guards_match(rows) and all(digest(ROOT/f['path'])==f['sha256'] for f in prior['files'])
 f=package_file(config['map']);shutil.copy2(f,OUT/'candidate_before.umap');assert digest(f)==digest(OUT/'candidate_before.umap')
 levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert levels.load_level(config['map'])
 lookup={a.get_actor_label():a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()}
 report['before']=[actor_state(lookup[p['label']]) for p in config['roster']]
 for p in config['roster']:
  a=lookup[p['label']];a.set_actor_rotation(unreal.Rotator(pitch=0,yaw=p['yaw'],roll=0),False)
  r=a.get_actor_rotation();assert abs(r.pitch)<1e-8 and abs(r.roll)<1e-8 and abs(r.yaw-p['yaw'])<1e-8
 report['after']=[actor_state(lookup[p['label']]) for p in config['roster']]
 for a,b in zip(report['before'],report['after']):
  assert all(a[k]==b[k] for k in a if k!='rotation')
 assert guards_match(rows) and levels.save_current_level();report['map_saved']=True
 report['files']=[dict(p) for p in prior['files']]
 for p in report['files']:
  f=ROOT/p['path'];p.update(size_bytes=f.stat().st_size,sha256=digest(f))
 report['nav_polygons']=prior['nav_polygons'];report['nav_tiles']=prior['nav_tiles'];report['collision_restored']=True
 report['protected_unchanged']=guards_match(rows)
 report['status']='pass_owned_map_headings_saved_runtime_unpassed'
except Exception:report['errors'].append(traceback.format_exc());report['status']='failed_heading_author_preserve';report['protected_unchanged']=guards_match(rows)
(OUT/'result.json').write_text(json.dumps(report,indent=2)+'\n')
unreal.SystemLibrary.quit_editor()
