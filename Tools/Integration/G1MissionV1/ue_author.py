"""New-map-only authoring. Original 703 protected rows must remain byte exact."""
import json,os,sys,time,traceback
from pathlib import Path
import unreal
ROOT=Path(os.environ['CS549_G1_ROOT'])
sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import STORE,digest,guard_rows,guards_match,package_file,DEST
from ue_graph import lib,call,get,put,run,pin
from ue_formal_roster import actor_state
config_file=STORE/'Evidence/G1MissionV1/config_v1_20261008/config.json'
config=json.loads(config_file.read_text());rows=guard_rows();assert rows==config['protected_rows'] and guards_match(rows)
OUT=Path(os.environ['CS549_G1_OUT']);assert OUT.is_dir() and not (OUT/'result.json').exists()
report={'status':'initializing','errors':[],'map_saved':False,'packages':[],'config_sha256':digest(config_file),'protected_count':703}
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);callback=None;started=time.monotonic();phase='setup'
settings=None;original=None;original_collision=[];nav=None;busy=False

def write():
 report['phase']=phase;(OUT/'result.json').write_text(json.dumps(report,indent=2)+'\n')
def finish(error=None):
 global callback,phase
 if error:report['errors'].append(error)
 if settings is not None:settings.set_editor_property('bEnableTypePromotion',original)
 report['protected_unchanged']=guards_match(rows)
 report['files']=[]
 for p in report['packages']:
  f=package_file(p)
  if f.exists():report['files'].append({'package':p,'path':f.relative_to(ROOT).as_posix(),'size_bytes':f.stat().st_size,'sha256':digest(f)})
 report['status']='failed_author_preserve' if report['errors'] or not report['protected_unchanged'] else 'pass_new_map_authored_runtime_unpassed'
 phase='done';write()
 if callback is not None:unreal.unregister_slate_post_tick_callback(callback);callback=None
 unreal.SystemLibrary.quit_editor()
def compile(bp):
 assert lib.compile_blueprint(bp)
 assert all(not unreal.BlueprintGraphEditor.get_graph_editor(g).list_nodes_with_errors() for g in lib.list_graphs(bp))
def tick(dt):
 global phase,busy
 if busy:return
 busy=True
 try:
  assert time.monotonic()-started<600,'Bounded author timeout'
  state=json.loads(unreal.ParisMapSurveyLibrary.navigation_build_state(nav));assert not state.get('error'),state
  if phase=='unlock':
   if state['manual_build_locked']:return
   unreal.SystemLibrary.execute_console_command(editor.get_editor_world(),'RebuildNavigation');phase='build';write();return
  if phase=='build':
   if unreal.NavigationSystemV1.is_navigation_being_built(editor.get_editor_world()) or time.monotonic()-started<15:return
   for a,enabled in original_collision:
    a.set_actor_enable_collision(enabled);assert a.get_actor_enable_collision()==enabled
   report['collision_restored']=True
   report['navigation_state']=state
   mesh=next(a for a in actors.get_all_level_actors() if isinstance(a,unreal.RecastNavMesh))
   exported=json.loads(unreal.ParisMapSurveyLibrary.export_navmesh(mesh));assert not exported.get('error') and len(exported['polygons'])>100
   report['nav_polygons']=len(exported['polygons']);report['nav_tiles']=exported['active_tiles']
   (OUT/'saved_navmesh.json').write_text(json.dumps(exported)+'\n')
   assert guards_match(rows)
   assert levels.save_current_level();report['map_saved']=True
   finish()
 except Exception:finish(traceback.format_exc())
 finally:busy=False

try:
 existing_map=package_file(config['map']).exists()
 if existing_map:
  proof=json.loads((STORE/'Evidence/G1MissionV1/author_v2_20261008/closure.json').read_text())
  assert proof['protected_unchanged'] and digest(package_file(config['map']))==proof['map_sha256']
  report['reused_exact_saved_copy']=proof['map_sha256']
 settings=unreal.get_default_object(unreal.load_class(None,'/Script/BlueprintGraph.BlueprintEditorSettings'))
 original=settings.get_editor_property('bEnableTypePromotion');settings.set_editor_property('bEnableTypePromotion',False)
 if unreal.EditorAssetLibrary.does_asset_exist(config['controller']):
  proof=json.loads((STORE/'Evidence/G1MissionV1/author_v1_20261008/closure.json').read_text())
  assert proof['protected_unchanged'] and digest(package_file(config['controller']))==proof['controller_sha256']
  report['reused_exact_controller']=proof['controller_sha256']
 else:
  bp=lib.create_blueprint_asset_with_parent(config['controller'],unreal.EditorAssetLibrary.load_blueprint_class(DEST+'/BP_PCNPCFormalCombatV1'));compile(bp)
  g=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'EventGraph')
  event=lib.add_event_override(bp,'ReceiveBeginPlay',unreal.IntPoint())
  use=call(g,'/Script/AIModule.AIController.UseBlackboard',BlackboardAsset=DEST+'/BB_PC_NPCInteractionV1')
  flow=run(g,lib.find_then_pin(event),use)
  put(g,flow,'NPCBlackboard',pin(use,'BlackboardComponent',True))
  compile(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,False)
 report['packages'].append(config['controller']);write()
 if not existing_map:
  assert levels.load_level('/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1')
  assert unreal.EditorLoadingAndSavingUtils.save_map(editor.get_editor_world(),config['map'])
 else:
  assert levels.load_level(config['map'])
 assert config['map'] in editor.get_editor_world().get_path_name()
 report['packages'].append(config['map']);report['initial_save_as']=True
 lookup={a.get_actor_label():a for a in actors.get_all_level_actors()}
 report['roster_before']=[actor_state(lookup[p['label']]) for p in config['roster']]
 cls=unreal.EditorAssetLibrary.load_blueprint_class(config['controller'])
 for p in config['roster']:
  a=lookup[p['label']];h=a.capsule_component.get_scaled_capsule_half_height();feet=p['feet_cm']
  assert a.set_actor_location_and_rotation(unreal.Vector(feet[0],feet[1],feet[2]+h+.5),unreal.Rotator(pitch=0,yaw=p['yaw'],roll=0),False,True)
  tags=list(a.get_editor_property('tags'));tags.append(unreal.Name('G1_'+p['id']));a.set_editor_property('tags',tags)
  if p['id']!='Player':a.set_editor_property('ai_controller_class',cls)
  original_collision.append((a,bool(a.get_actor_enable_collision())))
 report['roster_after']=[actor_state(lookup[p['label']]) for p in config['roster']]
 world=editor.get_editor_world();world.get_world_settings().set_editor_property('default_game_mode',unreal.ParisBridgeGameMode.static_class())
 mission=actors.spawn_actor_from_class(unreal.ParisBridgeMission,unreal.Vector(),unreal.Rotator());mission.set_actor_label('PC_G1_Mission')
 mission.set_editor_property('retained_tree',unreal.load_asset(DEST+'/BT_PC_NPCFormalCombatV1'))
 mission.set_editor_property('config_fingerprint',config['fingerprint'])
 bounds=next(a for a in actors.get_all_level_actors() if isinstance(a,unreal.NavMeshBoundsVolume))
 lo=config['navigation_bounds_cm']['min'];hi=config['navigation_bounds_cm']['max']
 bounds.set_actor_location(unreal.Vector(*[(a+b)/2 for a,b in zip(lo,hi)]),False,False)
 bounds.set_actor_scale3d(unreal.Vector(*[(b-a)/200 for a,b in zip(lo,hi)]))
 # Prevent stationary capsules cutting their initial cells, then restore exact flags before save/play.
 for a,_ in original_collision:a.set_actor_enable_collision(False)
 navs=[n for n in unreal.ObjectIterator(unreal.NavigationSystemV1) if 'Default__' not in n.get_path_name() and n.get_outer()==world]
 assert len(navs)==1;nav=navs[0];nav.on_navigation_bounds_updated(bounds)
 phase='unlock';write();callback=unreal.register_slate_post_tick_callback(tick)
except Exception:finish(traceback.format_exc())
