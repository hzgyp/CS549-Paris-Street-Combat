"""One owned-controller bridge-policy override; original assets/map are read-only."""
import json,os,shutil,sys,traceback
from pathlib import Path
import unreal
ROOT=Path(os.environ['CS549_G1_ROOT']);sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import STORE,guard_rows,guards_match,digest,package_file
from ue_graph import lib,pins,call,pure,pin,run,branch
OUT=Path(os.environ['CS549_G1_OUT']);rows=guard_rows()
report={'errors':[],'status':'initializing','scope':'owned controller override only','controller_saved':False}
prior=json.loads((STORE/'Evidence/G1MissionV1/headings_v1_20261008/result.json').read_text())
config=json.loads((STORE/'Evidence/G1MissionV1/config_v1_20261008/config.json').read_text());settings=None
try:
 assert len(rows)==703 and guards_match(rows) and all(digest(ROOT/f['path'])==f['sha256'] for f in prior['files'])
 owned=package_file(config['controller']);shutil.copy2(owned,OUT/'controller_before.uasset');assert digest(owned)==digest(OUT/'controller_before.uasset')
 settings=unreal.get_default_object(unreal.load_class(None,'/Script/BlueprintGraph.BlueprintEditorSettings'))
 original=settings.get_editor_property('bEnableTypePromotion');settings.set_editor_property('bEnableTypePromotion',False)
 bp=unreal.load_asset(config['controller'])
 assert not any(g.get_name()=='PC_UpdateSquad' for g in lib.list_graphs(bp))
 graph=lib.add_function_override(bp,unreal.Name('PC_UpdateSquad'));assert graph
 g=unreal.BlueprintGraphEditor.get_graph_editor(graph);g.set_function_is_public()
 parents=[n for n in g.list_all_nodes() if 'CallParentFunction' in n.get_class().get_name()];assert len(parents)==1
 parent=parents[0];assert pins.break_pin_links(lib.find_execute_pin(parent))
 controller=pure(g,'/Script/AIModule.AIBlueprintHelperLibrary.GetAIController',ControlledActor=pure(g,'/Script/Engine.Controller.K2_GetPawn'))
 hook=call(g,'/Script/ParisBridgeMissionV1.ParisBridgeMissionLibrary.UpdateBridgeSquad',Controller=controller)
 flow=run(g,g.find_graph_entry_pin(),hook);_,fallback=branch(g,flow,pin(hook,'ReturnValue',True));run(g,fallback,parent)
 assert lib.compile_blueprint(bp)
 assert all(not unreal.BlueprintGraphEditor.get_graph_editor(x).list_nodes_with_errors() for x in lib.list_graphs(bp))
 assert guards_match(rows) and unreal.EditorAssetLibrary.save_loaded_asset(bp,False);report['controller_saved']=True
 report.update({k:prior[k] for k in ('map_saved','nav_polygons','nav_tiles','collision_restored')})
 report['files']=[dict(f) for f in prior['files']]
 for f in report['files']:
  p=ROOT/f['path'];f.update(size_bytes=p.stat().st_size,sha256=digest(p))
 maprow=next(f for f in prior['files'] if f['package']==config['map']);assert digest(ROOT/maprow['path'])==maprow['sha256']
 report['map_unchanged']=True;report['protected_unchanged']=guards_match(rows)
 report['status']='pass_owned_bridge_hook_saved_runtime_unpassed'
except Exception:report['errors'].append(traceback.format_exc());report['status']='failed_bridge_hook_preserve';report['protected_unchanged']=guards_match(rows)
finally:
 if settings is not None:settings.set_editor_property('bEnableTypePromotion',original)
 (OUT/'result.json').write_text(json.dumps(report,indent=2)+'\n')
 unreal.SystemLibrary.quit_editor()
