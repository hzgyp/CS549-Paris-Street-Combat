"""Separate existing owner holding from full-body actions; new-only standard Blueprint."""
import hashlib,json,os,sys,traceback
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[2];STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT=STORE/'Evidence/PlayerActionsV1'/os.environ['CS549_ACTION_IDENTITY'];assert not OUT.exists();OUT.mkdir(parents=True)
sys.path.insert(0,str(Path(__file__).parent))
from ue_paris_graph_helpers import lib,pins,pin,wire,value,call,pure,get,run
SRC='/Game/ParisCombat/Blueprints/ContinuousArmsNativeV1/BP_PC_ContinuousArmsNativeV1'
DEST='/Game/ParisCombat/Blueprints/PlayerActionsV1/BP_PCActionOwnerViewV1'
PLAYER='/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisPlayerV1'
GUN='/Game/ParisCombat/Blueprints/WeaponAttachmentV3/BP_PC_RifleAttachmentV3'
records=json.loads((ROOT/'Assets/Sync/manifests/paris-gameplay-native-playtest.json').read_text())['files']
records+=json.loads((ROOT/'Assets/Integration/CITY_CONTINUOUS_ARMS_NATIVE_INVENTORY_20261003.json').read_text())['files']
def guard():return all(hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256'] for f in records)
assert guard();assert not unreal.EditorAssetLibrary.does_asset_exist(DEST)
r={'status':'authoring','errors':[],'packages':[],'map_saved':False}
(OUT/'source.py').write_bytes(Path(__file__).read_bytes())
def math(g,n,**kw):return pure(g,'/Script/Engine.KismetMathLibrary.'+n,**kw)
def branch(g,f,c):
    n=g.add_branch_node();wire(f,lib.find_execute_pin(n));wire(c,pin(n,'Condition'));return pin(n,'then',True),pin(n,'else',True)
def put(g,f,n,v,cls='',target=None):
    node=g.add_set_member_variable_node(n,cls)
    if target is not None:wire(target,lib.find_self_pin(node))
    value(pin(node,n),v);return run(g,f,node)
def cast(g,f,obj,cls):
    n=g.create_node_from_name('Utilities|Casting|CastToCharacter',unreal.Vector2D(),[obj]);assert n
    assert g.retarget_node_class(n,unreal.Character.static_class(),cls)
    wire(obj,pin(n,'Object'));wire(f,lib.find_execute_pin(n))
    out=[p for p in lib.list_all_pins(n) if str(pins.get_pin_name(p)).startswith('As')];assert len(out)==1
    return lib.find_then_pin(n),out[0]
try:
    playercls=unreal.EditorAssetLibrary.load_blueprint_class(PLAYER);guncls=unreal.EditorAssetLibrary.load_blueprint_class(GUN)
    bp=unreal.AssetToolsHelpers.get_asset_tools().duplicate_asset(DEST.rsplit('/',1)[1],DEST.rsplit('/',1)[0],unreal.load_asset(SRC));assert bp
    ev=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'EventGraph')
    ev.remove_nodes(ev.list_all_nodes())
    for n,t in [('PoseDriver',unreal.SkeletalMeshActor.static_class()),('PoseMesh',unreal.SkeletalMeshComponent.static_class()),('PoseGun',guncls),('BodySource',unreal.SkeletalMeshComponent.static_class())]:
        assert ev.add_member_variable(n,lib.get_object_reference_type(t))
    assert ev.add_member_variable('PoseMode',lib.get_basic_type_by_name('name'),'None')
    for n in ('PC_InitActionView','PC_UpdateActionViewPose','PC_CleanupActionView'):unreal.BlueprintGraphEditor.create_and_edit_function_graph(bp,n)
    assert lib.compile_blueprint(bp)
    g=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'PC_InitActionView');f=g.find_graph_entry_pin()
    f=put(g,f,'BodySource',get(g,'SourceMesh'))
    p=get(g,'Combatant');v=get(g,'SkeletalMeshComponent','/Script/Engine.SkeletalMeshActor')
    transform=pure(g,'/Script/Engine.Actor.GetTransform',self=p)
    spawn=call(g,'/Script/Engine.GameplayStatics.BeginDeferredActorSpawnFromClass',ActorClass='/Script/Engine.SkeletalMeshActor',SpawnTransform=transform,CollisionHandlingOverride='AlwaysSpawn',Owner=p)
    f=run(g,f,spawn)
    finish=call(g,'/Script/Engine.GameplayStatics.FinishSpawningActor',Actor=pin(spawn,'ReturnValue',True),SpawnTransform=transform)
    f=run(g,f,finish);f,a=cast(g,f,pin(finish,'ReturnValue',True),unreal.SkeletalMeshActor.static_class());f=put(g,f,'PoseDriver',a)
    f=put(g,f,'PoseMesh',pure(g,'/Script/Engine.Actor.GetComponentByClass',self=a,ComponentClass='/Script/Engine.SkeletalMeshComponent'))
    s=get(g,'PoseMesh')
    original=get(g,'BodySource')
    # Same rig/model, runtime reuse only, not a duplicated commercial file.
    f=run(g,f,call(g,'/Script/Engine.SkeletalMeshComponent.SetSkeletalMeshAsset',self=s,NewMesh=pure(g,'/Script/Engine.SkeletalMeshComponent.GetSkeletalMeshAsset',self=original)))
    f=put(g,f,'VisibilityBasedAnimTickOption','AlwaysTickPoseAndRefreshBones','/Script/Engine.SkinnedMeshComponent',s)
    f=run(g,f,call(g,'/Script/Engine.SceneComponent.K2_SetRelativeRotation',self=s,NewRotation='(Pitch=0,Yaw=-90,Roll=0)',bSweep=False,bTeleport=True))
    f=run(g,f,call(g,'/Script/Engine.PrimitiveComponent.SetCollisionEnabled',self=s,NewType='NoCollision'))
    f=run(g,f,call(g,'/Script/Engine.SceneComponent.SetVisibility',self=s,bNewVisibility=False,bPropagateToChildren=True))
    f=run(g,f,call(g,'/Script/Engine.SkeletalMeshComponent.PlayAnimation',self=s,NewAnimToPlay='/Game/RifleAnimsetPro/Animations/InPlace/Rifle_Idle.Rifle_Idle',bLooping=True))
    spawn=call(g,'/Script/Engine.GameplayStatics.BeginDeferredActorSpawnFromClass',ActorClass=guncls.get_path_name(),SpawnTransform=transform,CollisionHandlingOverride='AlwaysSpawn',Owner=p)
    f=run(g,f,spawn);f,newgun=cast(g,f,pin(spawn,'ReturnValue',True),guncls)
    f=put(g,f,'GripMesh',s,guncls.get_path_name(),newgun);f=put(g,f,'Combatant',p,guncls.get_path_name(),newgun)
    finish=call(g,'/Script/Engine.GameplayStatics.FinishSpawningActor',Actor=newgun,SpawnTransform=transform)
    f=run(g,f,finish);f=put(g,f,'PoseGun',newgun)
    f=run(g,f,call(g,'/Script/Engine.Actor.SetActorHiddenInGame',self=newgun,bNewHidden=True))
    f=run(g,f,call(g,'/Script/Engine.Actor.K2_AttachToComponent',self=newgun,Parent=s,SocketName='hand_r',LocationRule='KeepRelative',RotationRule='KeepRelative',ScaleRule='KeepRelative',bWeldSimulatedBodies=False))
    for target,fn,arg in [(s,'/Script/Engine.ActorComponent.AddTickPrerequisiteComponent',{'PrerequisiteComponent':original}),
                          (newgun,'/Script/Engine.Actor.AddTickPrerequisiteComponent',{'PrerequisiteComponent':s})]:
        f=run(g,f,call(g,fn,self=target,**arg))
    f=run(g,f,call(g,'/Script/Engine.Actor.AddTickPrerequisiteActor',PrerequisiteActor=newgun))
    f=put(g,f,'SourceMesh',s);f=put(g,f,'WorldGun',newgun)
    f=run(g,f,call(g,'/Script/Engine.SkinnedMeshComponent.SetLeaderPoseComponent',self=v,NewLeaderBoneComponent=s,bForceUpdate=True,bInFollowerShouldTickPose=False))
    f=run(g,f,call(g,'/Script/Engine.ActorComponent.AddTickPrerequisiteComponent',self=v,PrerequisiteComponent=s))
    put(g,f,'PoseMode','Holding')
    g=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'PC_UpdateActionViewPose');f=g.find_graph_entry_pin();s=get(g,'PoseMesh')
    ready=math(g,'EqualEqual_NameName',A=get(g,'ActionState',playercls.get_path_name(),get(g,'Combatant')),B='Ready')
    held,other=branch(g,f,ready)
    held,_=branch(g,held,math(g,'NotEqual_NameName',A=get(g,'PoseMode'),B='Holding'))
    held=run(g,held,call(g,'/Script/Engine.SkinnedMeshComponent.SetLeaderPoseComponent',self=s,bForceUpdate=True,bInFollowerShouldTickPose=False))
    held=run(g,held,call(g,'/Script/Engine.SkeletalMeshComponent.PlayAnimation',self=s,NewAnimToPlay='/Game/RifleAnimsetPro/Animations/InPlace/Rifle_Idle.Rifle_Idle',bLooping=True));put(g,held,'PoseMode','Holding')
    reload=math(g,'EqualEqual_NameName',A=get(g,'ActionState',playercls.get_path_name(),get(g,'Combatant')),B='Reloading')
    other,_=branch(g,other,reload);other,_=branch(g,other,math(g,'NotEqual_NameName',A=get(g,'PoseMode'),B='Reloading'))
    other=run(g,other,call(g,'/Script/Engine.SkinnedMeshComponent.SetLeaderPoseComponent',self=s,NewLeaderBoneComponent=get(g,'BodySource'),bForceUpdate=True,bInFollowerShouldTickPose=False));put(g,other,'PoseMode','Reloading')
    g=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'PC_CleanupActionView');f=g.find_graph_entry_pin()
    for name in ('PoseGun','PoseDriver','DisplayGun'):
        yes,no=branch(g,f,pure(g,'/Script/Engine.KismetSystemLibrary.IsValid',Object=get(g,name)))
        yes=run(g,yes,call(g,'/Script/Engine.Actor.K2_DestroyActor',self=get(g,name)))
        # New function per optional actor avoids exec merge assumptions.
        if name!='DisplayGun':
            # These spawned references always exist after successful initialization;
            # false path need not destroy other invalidated actors during teardown.
            f=yes
    ev=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'EventGraph')
    e=lib.add_event_override(bp,'ReceiveTick',unreal.IntPoint())
    done,init=branch(ev,lib.find_then_pin(e),get(ev,'Initialized'))
    init=run(ev,init,call(ev,'PC_InitOwnerDisplay'));init=run(ev,init,call(ev,'PC_InitActionView'))
    for f in (init,done):
        f=run(ev,f,call(ev,'PC_UpdateActionViewPose'));run(ev,f,call(ev,'PC_UpdateOwnerDisplay'))
    e=lib.add_event_override(bp,'ReceiveEndPlay',unreal.IntPoint());run(ev,lib.find_then_pin(e),call(ev,'PC_CleanupActionView'))
    assert lib.compile_blueprint(bp)
    r['graph_errors']=[str(n) for graph in lib.list_graphs(bp) for n in unreal.BlueprintGraphEditor.get_graph_editor(graph).list_nodes_with_errors()];assert not r['graph_errors']
    assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
    path=STORE/('Content/'+DEST.removeprefix('/Game/')+'.uasset');r['packages']=[{'package':DEST,'path':path.relative_to(ROOT).as_posix(),'size_bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}]
    r['status']='saved_unselected_owner_holding_separation_requires_fresh_tests'
except Exception:r['errors'].append(traceback.format_exc());r['status']='failed'
finally:
    r['protected_bytes_unchanged']=guard();(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n');unreal.SystemLibrary.quit_editor()
