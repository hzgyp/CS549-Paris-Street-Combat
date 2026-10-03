"""Unselected player-only standard Blueprint aim convergence; reload keeps V3 wrist policy."""
import hashlib,json,os,sys,traceback
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[2]
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT=STORE/'Evidence/CityGameplay20261002/RifleCrosshairV4'/os.environ['CS549_PLAYER_RIFLE_AUTHOR_IDENTITY']
assert OUT.name.replace('_','').isalnum() and not OUT.exists();OUT.mkdir()
DEST='/Game/ParisCombat/Blueprints/WeaponAimingV4/BP_PC_PlayerRifleAimV4'
a=json.loads((ROOT/'Assets/Integration/CITY_RIFLE_ACTION_DRAFT_INVENTORY_20261002.json').read_text())
d=json.loads((ROOT/a['retained_dependency_inventory']).read_text())
records=a['files']+d['files']+a['retained_unselected_rejected_trial']
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert all(digest(ROOT/e['path'])==e['sha256'] for e in records)
assert not unreal.EditorAssetLibrary.does_asset_exist(DEST),'Preserve occupied trial'
sys.path.insert(0,str(Path(__file__).parent))
from ue_paris_graph_helpers import lib,pins,wire,pin,call,pure,get,run,value
r={'scope':__doc__,'status':'initializing','errors':[],'package':DEST}
def math(g,n,**inputs):return pure(g,'/Script/Engine.KismetMathLibrary.'+n,**inputs)
def branch(g,flow,cond):
    n=g.add_branch_node();wire(cond,pin(n,'Condition'));wire(flow,lib.find_execute_pin(n))
    return pin(n,'then',True),pin(n,'else',True)
try:
    bp=lib.create_blueprint_asset_with_parent(DEST,unreal.StaticMeshActor.static_class());assert bp
    events=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'EventGraph')
    player_cls=unreal.EditorAssetLibrary.load_blueprint_class('/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisPlayerV1')
    assert events.add_member_variable('GripMesh',lib.get_object_reference_type(unreal.SkeletalMeshComponent.static_class()))
    assert events.add_member_variable('Combatant',lib.get_object_reference_type(player_cls))
    assert events.add_member_variable('LeftShiftCm',lib.get_basic_type_by_name('real'),'0.5')
    for n in ('GripMesh','Combatant','LeftShiftCm'):lib.set_blueprint_variable_instance_editable(bp,n,True)
    assert lib.compile_blueprint(bp)
    cdo=unreal.get_default_object(unreal.EditorAssetLibrary.load_blueprint_class(DEST))
    tick=cdo.get_editor_property('primary_actor_tick');enum=type(tick.get_editor_property('tick_group'));tick.set_editor_property('tick_group',enum.TG_POST_UPDATE_WORK);cdo.set_editor_property('primary_actor_tick',tick)
    c=cdo.get_component_by_class(unreal.StaticMeshComponent);c.set_mobility(unreal.ComponentMobility.MOVABLE);c.set_static_mesh(unreal.load_asset('/Game/USParatrooper/Meshes/Weapon/Sm_M1_Garand'));c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    g=unreal.BlueprintGraphEditor.create_and_edit_function_graph(bp,'PC_UpdateRifleAttachment')
    mesh,actor=get(g,'GripMesh'),get(g,'Combatant')
    valid=math(g,'BooleanAND',A=pure(g,'/Script/Engine.KismetSystemLibrary.IsValid',Object=mesh),B=pure(g,'/Script/Engine.KismetSystemLibrary.IsValid',Object=actor))
    flow,invalid=branch(g,g.find_graph_entry_pin(),valid)
    flow,dead=branch(g,flow,math(g,'Not_PreBool',A=get(g,'IsDead',player_cls.get_path_name(),actor)))
    state=get(g,'ActionState',player_cls.get_path_name(),actor)
    ready=math(g,'EqualEqual_NameName',A=state,B='Ready');reload=math(g,'EqualEqual_NameName',A=state,B='Reloading')
    flow,other=branch(g,flow,math(g,'BooleanOR',A=ready,B=reload))
    def socket(n):return pure(g,'/Script/Engine.SceneComponent.GetSocketLocation',self=mesh,InSocketName=n)
    fs=('middle','ring','pinky');names=[f+'_0'+str(s)+'_r' for f in fs for s in (2,3)]+['thumb_02_r','thumb_03_r']
    right=socket(names[0])
    for n in names[1:]:right=math(g,'Add_VectorVector',A=right,B=socket(n))
    right=math(g,'Multiply_VectorFloat',A=right,B=1/len(names))
    anchor=math(g,'MakeVector',X=math(g,'Multiply_DoubleDouble',A=get(g,'LeftShiftCm'),B=-1),Y=-8,Z=0)
    def fit(rotation):
        t=math(g,'MakeTransform',Location='(X=0,Y=0,Z=0)',Rotation=rotation,Scale='(X=1,Y=1,Z=1)')
        return math(g,'Subtract_VectorVector',A=right,B=math(g,'TransformLocation',T=t,Location=anchor))
    held,reloading=branch(g,flow,ready)
    camera=get(g,'ParisPlayerCamera',player_cls.get_path_name(),actor)
    start=pure(g,'/Script/Engine.SceneComponent.K2_GetComponentLocation',self=camera)
    forward=pure(g,'/Script/Engine.SceneComponent.GetForwardVector',self=camera)
    end=math(g,'Add_VectorVector',A=start,B=math(g,'Multiply_VectorFloat',A=forward,B=20000))
    trace=call(g,'/Script/Engine.KismetSystemLibrary.LineTraceSingle',Start=start,End=end,TraceChannel='TraceTypeQuery1',bTraceComplex=False,bIgnoreSelf=True)
    array=g.create_node_from_name('Utilities|Array|MakeArray',unreal.Vector2D(),[]);assert array
    wire(pin(array,'Array',True),pin(trace,'ActorsToIgnore'));wire(actor,pin(array,'[0]'))
    held=run(g,held,trace)
    hit=call(g,'/Script/Engine.GameplayStatics.BreakHitResult',Hit=pin(trace,'OutHit',True))
    goal=math(g,'SelectVector',A=pin(hit,'ImpactPoint',True),B=end,bPickA=pin(trace,'ReturnValue',True))
    location=right
    for _ in range(4):
        look=call(g,'/Script/Engine.KismetMathLibrary.BreakRotator',InRot=math(g,'FindLookAtRotation',Start=location,Target=goal))
        rotation=math(g,'MakeRotator',Pitch=0,Yaw=math(g,'Subtract_DoubleDouble',A=pin(look,'Yaw',True),B=90),Roll=math(g,'Multiply_DoubleDouble',A=pin(look,'Pitch',True),B=-1))
        location=fit(rotation)
    run(g,held,call(g,'/Script/Engine.Actor.K2_SetActorLocationAndRotation',NewLocation=location,NewRotation=rotation,bSweep=False,bTeleport=True))
    wr=a['attachment_policy']['reload_wrist_relative_rotation']
    local=math(g,'MakeTransform',Location='(X=0,Y=0,Z=0)',Rotation=f'(Pitch={wr[0]},Yaw={wr[1]},Roll={wr[2]})',Scale='(X=1,Y=1,Z=1)')
    hand=pure(g,'/Script/Engine.SceneComponent.GetSocketTransform',self=mesh,InSocketName='hand_r')
    wrist=call(g,'/Script/Engine.KismetMathLibrary.BreakTransform',InTransform=math(g,'ComposeTransforms',A=local,B=hand))
    rotation=pin(wrist,'Rotation',True)
    run(g,reloading,call(g,'/Script/Engine.Actor.K2_SetActorLocationAndRotation',NewLocation=fit(rotation),NewRotation=rotation,bSweep=False,bTeleport=True))
    event=lib.add_event_override(bp,'ReceiveTick',unreal.IntPoint(0,0));assert event
    run(events,lib.find_then_pin(event),call(events,'PC_UpdateRifleAttachment'))
    begin=lib.add_event_override(bp,'ReceiveBeginPlay',unreal.IntPoint(0,300));assert begin
    flow,invalid=branch(events,lib.find_then_pin(begin),pure(events,'/Script/Engine.KismetSystemLibrary.IsValid',Object=get(events,'GripMesh')))
    flow=run(events,flow,call(events,'/Script/Engine.Actor.AddTickPrerequisiteComponent',PrerequisiteComponent=get(events,'GripMesh')))
    flow=run(events,flow,call(events,'/Script/Engine.Actor.SetTickGroup',NewTickGroup='TG_PostUpdateWork'))
    run(events,flow,call(events,'/Script/Engine.Actor.SetActorTickEnabled',bEnabled=True))
    assert lib.compile_blueprint(bp)
    r['graph_errors']=[str(n) for graph in lib.list_graphs(bp) for n in unreal.BlueprintGraphEditor.get_graph_editor(graph).list_nodes_with_errors()];assert not r['graph_errors']
    assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
    r['status']='saved_unselected_player_rifle_requires_runtime_contact_review'
except Exception:r['status']='failed';r['errors'].append(traceback.format_exc())
finally:
    p=STORE/('Content/'+DEST.removeprefix('/Game/')+'.uasset')
    if p.exists():r['saved_trial']={'package':DEST,'path':p.relative_to(ROOT).as_posix(),'size_bytes':p.stat().st_size,'sha256':digest(p)}
    r['protected_37_unchanged']=all(digest(ROOT/e['path'])==e['sha256'] for e in records)
    (OUT/'result.json').write_text(json.dumps(r,indent=2));unreal.SystemLibrary.quit_editor()
