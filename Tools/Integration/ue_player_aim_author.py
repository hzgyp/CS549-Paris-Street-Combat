"""New, unselected native player aim layer; original poses/models/city are guarded."""
import hashlib, json, os, sys, traceback
from pathlib import Path
import unreal
ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT = STORE/'Evidence/CityGameplay20261002/RifleCrosshairV4'/os.environ['CS549_PLAYER_AIM_AUTHOR_IDENTITY']
assert OUT.name.replace('_','').isalnum() and not OUT.exists()
OUT.mkdir(parents=True)
SOURCE='/Game/ParisCombat/Animation/DirectionalDraft/ABP_PC_Allied_Stride_v1'
DEST='/Game/ParisCombat/Animation/WeaponAimingV4/ABP_PC_PlayerAimV4'
inventory=json.loads((ROOT/'Assets/Integration/CITY_RIFLE_ACTION_DRAFT_INVENTORY_20261002.json').read_text())
deps=json.loads((ROOT/inventory['retained_dependency_inventory']).read_text())
records=inventory['files']+deps['files']+inventory['retained_unselected_rejected_trial']
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
assert all(digest(ROOT/e['path'])==e['sha256'] for e in records)
sys.path.insert(0,str(Path(__file__).parent))
from ue_paris_graph_helpers import lib,pins,wire,pin,call,pure,get,run,cast_to,value
r={'scope':__doc__,'status':'initializing','errors':[],'saved_trial':None}
def write(): (OUT/'result.json').write_text(json.dumps(r,indent=2))
def math(g,n,**inputs): return pure(g,'/Script/Engine.KismetMathLibrary.'+n,**inputs)
def put(g,flow,name,source):
    node=g.add_set_member_variable_node(name)
    value(pin(node,name),source)
    return run(g,flow,node)
def branch(g,flow,cond):
    n=g.add_branch_node();wire(cond,pin(n,'Condition'));wire(flow,lib.find_execute_pin(n))
    return pin(n,'then',True),pin(n,'else',True)
try:
    assert not unreal.EditorAssetLibrary.does_asset_exist(DEST),'Preserve occupied trial'
    aim=unreal.load_asset('/Game/RifleAnimsetPro/BlendSpaces/RifleStandAim')
    original=unreal.load_asset(SOURCE)
    assert aim and original
    r['skeletons']={'aim':aim.get_editor_property('skeleton').get_path_name(), 'source':original.get_editor_property('target_skeleton').get_path_name()}
    target_skeleton=original.get_editor_property('target_skeleton')
    source_skeleton=aim.get_editor_property('skeleton')
    r['existing_compatible_skeletons']={'target':str(target_skeleton.get_editor_property('compatible_skeletons')),
                                       'aim':str(source_skeleton.get_editor_property('compatible_skeletons'))}
    assert r['skeletons']['aim']==r['skeletons']['source'] or r['skeletons']['aim'] in r['existing_compatible_skeletons']['target'] or r['skeletons']['source'] in r['existing_compatible_skeletons']['aim'], 'Existing compatibility declaration required; do not change a vendor skeleton'
    registry=unreal.AssetRegistryHelpers.get_asset_registry()
    packages=set();pending=['/Game/RifleAnimsetPro/BlendSpaces/RifleStandAim']
    options=unreal.AssetRegistryDependencyOptions(True,True,False,False,False)
    while pending:
        p=pending.pop()
        if p in packages or not p.startswith('/Game/'):continue
        packages.add(p)
        pending.extend(str(x) for x in registry.get_dependencies(p,options))
    r['aim_dependencies']=[]
    for p in sorted(packages):
        f=STORE/('Content/'+p.removeprefix('/Game/')+'.uasset')
        assert f.is_file(),p
        r['aim_dependencies'].append({'package':p,'path':f.relative_to(ROOT).as_posix(),'size_bytes':f.stat().st_size,'sha256':digest(f)})
    bp=unreal.EditorAssetLibrary.duplicate_asset(SOURCE,DEST); assert bp
    events=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'EventGraph')
    assert events.add_member_variable('AimTargetWorld',lib.get_struct_type(unreal.load_object(None,'/Script/CoreUObject.Vector')),'(X=20000,Y=0,Z=160)')
    assert events.add_member_variable('AimAlpha',lib.get_basic_type_by_name('real'),'0')
    assert events.add_member_variable('AimEnabled',lib.get_basic_type_by_name('bool'),'true')
    assert lib.compile_blueprint(bp)
    axis=json.loads((OUT.parent/'upper_audit_v1/result.json').read_text())['calibration']['hand_r']['axis']
    r['author_helper']=json.loads(unreal.ParisBlueprintAuthoring.add_player_aim_layer(bp,unreal.Vector(*axis)))
    write();assert r['author_helper']['success']
    g=unreal.BlueprintGraphEditor.create_and_edit_function_graph(bp,'PC_UpdateAimTarget')
    flow=put(g,g.find_graph_entry_pin(),'AimAlpha',0)
    owner=pure(g,'/Script/Engine.AnimInstance.TryGetPawnOwner')
    valid=pure(g,'/Script/Engine.KismetSystemLibrary.IsValid',Object=owner)
    flow,invalid=branch(g,flow,valid)
    player_cls=unreal.EditorAssetLibrary.load_blueprint_class('/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisPlayerV1')
    flow,actor=cast_to(g,flow,owner,player_cls)
    enabled=math(g,'BooleanAND',A=get(g,'AimEnabled'),B=math(g,'EqualEqual_NameName',A=get(g,'ActionState',player_cls.get_path_name(),actor),B='Ready'))
    enabled=math(g,'BooleanAND',A=enabled,B=math(g,'Not_PreBool',A=get(g,'IsDead',player_cls.get_path_name(),actor)))
    flow,off=branch(g,flow,enabled)
    camera=get(g,'ParisPlayerCamera',player_cls.get_path_name(),actor)
    start=pure(g,'/Script/Engine.SceneComponent.K2_GetComponentLocation',self=camera)
    direction=pure(g,'/Script/Engine.SceneComponent.GetForwardVector',self=camera)
    end=math(g,'Add_VectorVector',A=start,B=math(g,'Multiply_VectorFloat',A=direction,B=20000))
    trace=call(g,'/Script/Engine.KismetSystemLibrary.LineTraceSingle',Start=start,End=end,TraceChannel='TraceTypeQuery1',bTraceComplex=False,bIgnoreSelf=True)
    # The animation instance is not the pawn: explicitly ignore its owning actor.
    array=g.create_node_from_name('Utilities|Array|MakeArray',unreal.Vector2D(),[])
    assert array,'Installed MakeArray node required'
    wire(pin(array,'Array',True),pin(trace,'ActorsToIgnore'))
    wire(actor,pin(array,'[0]'))
    flow=run(g,flow,trace)
    hit=call(g,'/Script/Engine.GameplayStatics.BreakHitResult',Hit=pin(trace,'OutHit',True))
    target=math(g,'SelectVector',A=pin(hit,'ImpactPoint',True),B=end,bPickA=pin(trace,'ReturnValue',True))
    flow=put(g,flow,'AimTargetWorld',target)
    put(g,flow,'AimAlpha',1)
    assert lib.compile_blueprint(bp)
    event=events.find_event_node('BlueprintUpdateAnimation'); assert event
    start_pin=lib.find_then_pin(event)
    old=pins.list_connected_pins(start_pin)
    assert len(old)==1,'Retain one original velocity update chain'
    pins.break_pin_links(start_pin)
    updater=call(events,'PC_UpdateAimTarget')
    flow=run(events,start_pin,updater);wire(flow,old[0])
    assert lib.compile_blueprint(bp)
    r['graph_errors']=[str(n) for graph in lib.list_graphs(bp) for n in unreal.BlueprintGraphEditor.get_graph_editor(graph).list_nodes_with_errors()]
    assert not r['graph_errors']
    assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
    r['status']='saved_unselected_player_aim_requires_runtime_contact_review'
except Exception:
    r['status']='failed';r['errors'].append(traceback.format_exc())
finally:
    file=STORE/('Content/'+DEST.removeprefix('/Game/')+'.uasset')
    if file.exists():r['saved_trial']={'package':DEST,'path':file.relative_to(ROOT).as_posix(),'size_bytes':file.stat().st_size,'sha256':digest(file)}
    r['protected_37_unchanged']=all(digest(ROOT/e['path'])==e['sha256'] for e in records)
    write();unreal.SystemLibrary.quit_editor()
