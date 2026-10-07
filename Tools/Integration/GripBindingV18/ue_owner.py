"""New native owner: one cached camera frame and actual hand socket gun attachment."""
import json,os,sys,traceback
from pathlib import Path
import unreal
sys.path.insert(0,str(Path(__file__).parent))
from common import ROOT,STORE,BASE,config,guard,inventory
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ue_paris_graph_helpers import lib,pins,pin,wire,value,call,pure,get,run,cast_to
OUT=BASE/os.environ['CS549_GRIP_BINDING_ID'];assert not OUT.exists();OUT.mkdir()
DEST='/Game/ParisCombat/Blueprints/GripBindingV18/BP_PCGripOwnerV18'
ANIM='/Game/ParisCombat/Animation/GripBindingV18/ABP_PCGripBindingV18'
PLAYER='/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisPlayerV1'
REFERENCE='/Game/ParisCombat/Blueprints/ContinuousArmsNativeV1/BP_PC_ContinuousArmsNativeV1'
r={'errors':[],'stages':[],'packages':[],'map_saved':False,'selected':False,'runtime':'engine AnimBP and K2 only; no Python runtime calls'}
def stage(n):
    r['stages'].append(n);(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n');unreal.log('GRIP_OWNER_V18 '+n)
def math(g,n,**v):return pure(g,'/Script/Engine.KismetMathLibrary.'+n,**v)
def branch(g,flow,c):
    n=g.add_branch_node();wire(flow,lib.find_execute_pin(n));wire(c,pin(n,'Condition'));return pin(n,'then',True),pin(n,'else',True)
def put(g,flow,name,v,cls='',target=None):
    n=g.add_set_member_variable_node(name,cls)
    if target is not None:wire(target,lib.find_self_pin(n))
    value(pin(n,name),v);return run(g,flow,n)
def vec(v):return f'(X={v[0]},Y={v[1]},Z={v[2]})'
def transform(g,row):
    rotation=unreal.Quat(*row['q']).rotator()
    return math(g,'MakeTransform',Location=vec(row['t']),Rotation=f'(Pitch={rotation.pitch},Yaw={rotation.yaw},Roll={rotation.roll})',Scale=vec(row['s']))
try:
    r['guards_before']=guard();assert not r['guards_before']['mismatches']
    proof=json.loads((BASE/'anim_author_v2/result.json').read_text());assert not proof['errors'] and proof['packages']
    assert inventory(ANIM)==proof['packages'][0]
    c=config();assert not hasattr(unreal,'ParisBlueprintAuthoring')
    assert not unreal.EditorAssetLibrary.does_asset_exist(DEST)
    playercls=unreal.EditorAssetLibrary.load_blueprint_class(PLAYER)
    referencecls=unreal.EditorAssetLibrary.load_blueprint_class(REFERENCE)
    animcls=unreal.EditorAssetLibrary.load_blueprint_class(ANIM)
    assert playercls and referencecls and animcls
    bp=lib.create_blueprint_asset_with_parent(DEST,unreal.SkeletalMeshActor.static_class());assert bp
    ev=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'EventGraph')
    for name,cls in (('Combatant',playercls),('ReferenceOwner',referencecls),('SourceMesh',unreal.SkeletalMeshComponent.static_class()),('DisplayGun',unreal.StaticMeshActor.static_class())):
        assert ev.add_member_variable(name,lib.get_object_reference_type(cls))
    for name in ('Combatant','ReferenceOwner'):lib.set_blueprint_variable_instance_editable(bp,name,True)
    assert ev.add_member_variable('Initialized',lib.get_basic_type_by_name('bool'),'false')
    for name in ('CameraT','OriginalGunCameraT','SourceHandT','SourceGunT','AssemblyFrame'):
        assert ev.add_member_variable(name,lib.get_struct_type(unreal.load_object(None,'/Script/CoreUObject.Transform')))
    assert lib.compile_blueprint(bp)
    cls=unreal.EditorAssetLibrary.load_blueprint_class(DEST);cdo=unreal.get_default_object(cls)
    mesh=cdo.get_component_by_class(unreal.SkeletalMeshComponent)
    mesh.set_skeletal_mesh_asset(unreal.load_asset(c['source_mesh']))
    mesh.set_anim_instance_class(animcls)
    mesh.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    mesh.set_only_owner_see(True);mesh.set_cast_shadow(False)
    mesh.set_forced_lod(1)
    tick=cdo.get_editor_property('primary_actor_tick')
    tick.set_editor_property('tick_group',unreal.TickGroup.TG_POST_UPDATE_WORK)
    tick.set_editor_property('start_with_tick_enabled',True);cdo.set_editor_property('primary_actor_tick',tick)
    stage('new_owner_variables_and_mesh_defaults')
    def refs(g):
        p=get(g,'Combatant');s=get(g,'SourceMesh');v=get(g,'SkeletalMeshComponent','/Script/Engine.SkeletalMeshActor')
        cam=get(g,'ParisPlayerCamera',playercls.get_path_name(),p)
        old=get(g,'ReferenceOwner');oldgun=get(g,'DisplayGun',referencecls.get_path_name(),old)
        return p,s,v,cam,old,oldgun
    g=unreal.BlueprintGraphEditor.create_and_edit_function_graph(bp,'PC_InitGripBindingV18')
    p,s,v,cam,old,oldgun=refs(g)
    flow,_=branch(g,g.find_graph_entry_pin(),pure(g,'/Script/Engine.KismetSystemLibrary.IsValid',Object=p))
    flow,_=branch(g,flow,pure(g,'/Script/Engine.KismetSystemLibrary.IsValid',Object=old))
    flow,_=branch(g,flow,get(g,'Initialized',referencecls.get_path_name(),old))
    flow=put(g,flow,'SourceMesh',get(g,'Mesh','/Script/Engine.Character',p))
    flow=run(g,flow,call(g,'/Script/Engine.Actor.SetOwner',NewOwner=p))
    flow=put(g,flow,'CameraT',pure(g,'/Script/Engine.SceneComponent.K2_GetComponentToWorld',self=cam))
    flow=put(g,flow,'OriginalGunCameraT',math(g,'MakeRelativeTransform',A=pure(g,'/Script/Engine.Actor.GetTransform',self=oldgun),RelativeTo=get(g,'CameraT')))
    flow=put(g,flow,'SourceHandT',pure(g,'/Script/Engine.SceneComponent.GetSocketTransform',self=s,InSocketName='hand_r',TransformSpace='RTS_Component'))
    flow=put(g,flow,'SourceGunT',math(g,'ComposeTransforms',A=transform(g,c['gun_hand_relative']),B=get(g,'SourceHandT')))
    flow=put(g,flow,'AssemblyFrame',math(g,'ComposeTransforms',A=math(g,'InvertTransform',T=get(g,'SourceGunT')),B=get(g,'OriginalGunCameraT')))
    flow=run(g,flow,call(g,'/Script/Engine.Actor.K2_AttachToComponent',Parent=cam,SocketName='None',LocationRule='SnapToTarget',RotationRule='SnapToTarget',ScaleRule='SnapToTarget',bWeldSimulatedBodies=False))
    flow=run(g,flow,call(g,'/Script/Engine.SceneComponent.K2_SetRelativeTransform',self=v,NewTransform=get(g,'AssemblyFrame'),bSweep=False,bTeleport=True))
    flow=run(g,flow,call(g,'/Script/Engine.ActorComponent.AddTickPrerequisiteComponent',self=v,PrerequisiteComponent=s))
    flow=run(g,flow,call(g,'/Script/Engine.Actor.AddTickPrerequisiteComponent',PrerequisiteComponent=s))
    flow=put(g,flow,'VisibilityBasedAnimTickOption','AlwaysTickPoseAndRefreshBones','/Script/Engine.SkinnedMeshComponent',v)
    inst=pure(g,'/Script/Engine.SkeletalMeshComponent.GetAnimInstance',self=v)
    flow,inst=cast_to(g,flow,inst,animcls)
    flow=put(g,flow,'PoseSource',s,animcls.get_path_name(),inst)
    spawn=call(g,'/Script/Engine.GameplayStatics.BeginDeferredActorSpawnFromClass',ActorClass='/Script/Engine.StaticMeshActor',SpawnTransform=pure(g,'/Script/Engine.Actor.GetTransform'),CollisionHandlingOverride='AlwaysSpawn',Owner=p)
    flow=run(g,flow,spawn)
    finish=call(g,'/Script/Engine.GameplayStatics.FinishSpawningActor',Actor=pin(spawn,'ReturnValue',True),SpawnTransform=pure(g,'/Script/Engine.Actor.GetTransform'))
    flow=run(g,flow,finish);flow,gun=cast_to(g,flow,pin(finish,'ReturnValue',True),unreal.StaticMeshActor.static_class())
    flow=put(g,flow,'DisplayGun',gun)
    gun=get(g,'DisplayGun');gm=get(g,'StaticMeshComponent','/Script/Engine.StaticMeshActor',gun)
    for function,args in (
        ('/Script/Engine.SceneComponent.SetMobility',{'self':gm,'NewMobility':'Movable'}),
        ('/Script/Engine.StaticMeshComponent.SetStaticMesh',{'self':gm,'NewMesh':'/Game/USParatrooper/Meshes/Weapon/Sm_M1_Garand.Sm_M1_Garand'}),
        ('/Script/Engine.PrimitiveComponent.SetCollisionEnabled',{'self':gm,'NewType':'NoCollision'}),
        ('/Script/Engine.PrimitiveComponent.SetOnlyOwnerSee',{'self':gm,'bNewOnlyOwnerSee':True}),
        ('/Script/Engine.PrimitiveComponent.SetCastShadow',{'self':gm,'NewCastShadow':False}),
        ('/Script/Engine.Actor.K2_AttachToComponent',{'self':gun,'Parent':v,'SocketName':'hand_r','LocationRule':'SnapToTarget','RotationRule':'SnapToTarget','ScaleRule':'SnapToTarget','bWeldSimulatedBodies':False}),
        ('/Script/Engine.SceneComponent.K2_SetRelativeTransform',{'self':gm,'NewTransform':transform(g,c['gun_hand_relative']),'bSweep':False,'bTeleport':True}),
        ('/Script/Engine.Actor.SetActorHiddenInGame',{'self':old,'bNewHidden':True}),
        ('/Script/Engine.Actor.SetActorHiddenInGame',{'self':oldgun,'bNewHidden':True})):
        flow=run(g,flow,call(g,function,**args))
    put(g,flow,'Initialized',True)
    stage('one_time_native_binding_and_camera_frame_graph')
    g=unreal.BlueprintGraphEditor.create_and_edit_function_graph(bp,'PC_UpdateGripBindingV18')
    p,s,v,cam,old,oldgun=refs(g)
    flow,_=branch(g,g.find_graph_entry_pin(),get(g,'Initialized'))
    inst=pure(g,'/Script/Engine.SkeletalMeshComponent.GetAnimInstance',self=v)
    flow,inst=cast_to(g,flow,inst,animcls)
    ready=math(g,'EqualEqual_NameName',A=get(g,'ActionState',playercls.get_path_name(),p),B='Ready')
    alpha=math(g,'SelectFloat',A=1.,B=0.,bPickA=ready)
    flow=put(g,flow,'GripAlpha',alpha,animcls.get_path_name(),inst)
    alive=math(g,'Not_PreBool',A=get(g,'IsDead',playercls.get_path_name(),p))
    for comp in (v,get(g,'StaticMeshComponent','/Script/Engine.StaticMeshActor',get(g,'DisplayGun'))):
        flow=run(g,flow,call(g,'/Script/Engine.SceneComponent.SetVisibility',self=comp,bNewVisibility=alive,bPropagateToChildren=False))
    stage('native_alpha_and_lifecycle_graph')
    ev=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'EventGraph')
    event=lib.add_event_override(bp,'ReceiveTick',unreal.IntPoint());assert event
    active,init=branch(ev,lib.find_then_pin(event),get(ev,'Initialized'))
    init=run(ev,init,call(ev,'PC_InitGripBindingV18'))
    for flow in (init,active):run(ev,flow,call(ev,'PC_UpdateGripBindingV18'))
    assert lib.compile_blueprint(bp)
    r['graph_errors']=[str(n) for graph in lib.list_graphs(bp) for n in unreal.BlueprintGraphEditor.get_graph_editor(graph).list_nodes_with_errors()];assert not r['graph_errors']
    assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
    r['packages']=[inventory(DEST)]
    r['status']='saved_unselected_native_owner_requires_actual_view_and_actions'
    stage('new_only_owner_saved')
except Exception:r['status']='stopped_owner_error';r['errors'].append(traceback.format_exc())
finally:
    r['guards_after']=guard();(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n')
    unreal.SystemLibrary.quit_editor()
