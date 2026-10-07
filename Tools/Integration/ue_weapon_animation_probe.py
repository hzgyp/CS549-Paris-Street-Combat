"""Read-only assets + transient instance diagnostic after failed reload gate."""
import json,os,sys,traceback
from pathlib import Path
import unreal
sys.path.insert(0,str(Path(__file__).parent))
from weapon_animation_reuse_common import PLAYER,output,guard
from ue_paris_graph_helpers import lib,pins
OUT=output(os.environ['CS549_ANIMATION_IDENTITY'])
r={'status':'probing','errors':[],'states':{},'graph':{},'map_saved':False}
names=('Capacity','LoadedAmmo','ReserveAmmo','ReloadPlayRate','ReloadDuration','ReloadCommitTime','IsDead','ActionState','ActionID','RestoreGeneration','ReloadActionID','ReloadGeneration','ReloadElapsed','ReloadPhaseDriverEnabled')
def fields(obj):return {n:str(obj.get_editor_property(n)) for n in names}
try:
    guard();cls=unreal.EditorAssetLibrary.load_blueprint_class(PLAYER)
    r['cdo']=fields(unreal.get_default_object(cls))
    bp=unreal.load_asset(PLAYER)
    g=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'PC_RequestReload')
    for n in g.list_all_nodes():
        r['graph'][n.get_name()]=[{'name':str(pins.get_pin_name(p)), 'value':pins.get_pin_value(p),'connections':[str(pins.get_pin_name(q))+':'+q.get_owning_node().get_name() for q in pins.list_connected_pins(p)]} for p in lib.list_all_pins(n)]
    actor=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).spawn_actor_from_class(cls,unreal.Vector(0,0,100))
    r['states']['spawn']=fields(actor)
    actor.call_method('PC_ResetLifecycle');r['states']['reset']=fields(actor)
    actor.call_method('PC_RequestReload');r['states']['request']=fields(actor)
    r['position']=actor.mesh.get_position()
    r['status']='transient_instance_diagnostic_complete'
except Exception:r['errors'].append(traceback.format_exc());r['status']='failed'
finally:
    r['protected_files_unchanged']=guard()
    (OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    unreal.SystemLibrary.quit_editor()
