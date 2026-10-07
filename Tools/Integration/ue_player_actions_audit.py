"""Read-only installed native capability audit; no package saves."""
import json, os, traceback
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/PlayerActionsV1'/os.environ['CS549_ACTION_IDENTITY']
assert not OUT.exists(); OUT.mkdir(parents=True)
r={'errors':[], 'classes':{},'clips':[], 'graphs':{}, 'native_saved':False}
try:
    lib=unreal.BlueprintEditorLibrary
    for path in ('/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisPlayerV1',
                 '/Game/ParisCombat/Blueprints/Characters/SimplifiedReloadDraft/BP_PCCombatantReloadV1'):
        bp=unreal.load_asset(path); cls=unreal.EditorAssetLibrary.load_blueprint_class(path)
        d=unreal.get_default_object(cls)
        r['classes'][path]={'python_methods':[x for x in dir(d) if 'reload' in x.lower() or 'reset' in x.lower()]}
        if isinstance(d,unreal.Character):
            m=d.character_movement
            r['classes'][path].update(max_walk_speed=m.max_walk_speed, capsule_half=d.capsule_component.get_unscaled_capsule_half_height(), mesh_z=d.mesh.relative_location.z)
        r['graphs'][path]=[]
        for graph in lib.list_graphs(bp):
            g=unreal.BlueprintGraphEditor.get_graph_editor(graph)
            record={'name':graph.get_name(),'nodes':[]}
            for n in g.list_all_nodes():
                record['nodes'].append({'name':n.get_name(),'type':n.get_class().get_name(), 'pins':[
                    {'name':str(unreal.BlueprintGraphPinLibrary.get_pin_name(p)), 'value':str(unreal.BlueprintGraphPinLibrary.get_pin_value(p)) if hasattr(unreal.BlueprintGraphPinLibrary,'get_pin_value') else ''}
                    for p in lib.list_all_pins(n)]})
            r['graphs'][path].append(record)
    for name in ('Rifle_RunFwdLoop','Rifle_WalkFwdLoop','Rifle_CrouchLoop','Rifle_Crouch_WalkFwd','Rifle_Crouch_WalkBwd',
                 'Rifle_Prone','Rifle_Prone_WalkFwd','Rifle_Prone_WalkBwd','Rifle_Jump_Platformer_Start','Rifle_Jump_Platformer_Fall','Rifle_Jump_Platformer_Land'):
        a=unreal.load_asset('/Game/RifleAnimsetPro/Animations/InPlace/'+name)
        r['clips'].append({'name':name,'duration':a.get_play_length(),'skeleton':a.get_editor_property('skeleton').get_path_name(), 'root_motion':a.get_editor_property('enable_root_motion')})
    b=unreal.load_asset('/Game/ParisCombat/Animation/DirectionalDraft/BS_PC_Allied_Stride_v1')
    r['blend_samples']=str(b.get_editor_property('sample_data'))
    r['graph_api']=unreal.BlueprintGraphEditor.__doc__
    r['pin_api']=[x for x in dir(unreal.BlueprintGraphPinLibrary) if not x.startswith('_')]
    r['character_movement_api']=[x for x in dir(unreal.CharacterMovementComponent) if 'crouch' in x or 'jump' in x or 'nav_agent' in x]
except Exception:r['errors'].append(traceback.format_exc())
finally:
    (OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n');unreal.SystemLibrary.quit_editor()
