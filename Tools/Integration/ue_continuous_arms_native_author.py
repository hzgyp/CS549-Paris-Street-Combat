"""Author standard Blueprint owner display; Python never runs its gameplay update."""
import hashlib,json,os,sys,traceback
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[2]
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
identity=os.environ['CS549_ARMS_NATIVE_IDENTITY']
assert identity.replace('_','').isalnum()
OUT=STORE/'Evidence/ContinuousArmsNativeV1'/identity
assert not OUT.exists();OUT.mkdir(parents=True)
sys.path.insert(0,str(Path(__file__).parent))
from ue_continuous_arms_runtime_trial import trial_records
from ue_paris_graph_helpers import lib,pins,pin,wire,value,call,pure,get,run
records=trial_records()
def guard():return all((ROOT/f['path']).stat().st_size==f['size_bytes'] and hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256'] for f in records)
assert guard()
DEST='/Game/ParisCombat/Blueprints/ContinuousArmsNativeV1/BP_PC_ContinuousArmsNativeV1'
assert not unreal.EditorAssetLibrary.does_asset_exist(DEST),'Preserve occupied package'
r={'status':'authoring','errors':[],'package':DEST,'display_runtime':'standard Blueprint only','map_saved':False}
(OUT/'source.py').write_bytes(Path(__file__).read_bytes())
def write():(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n')
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
    out=[p for p in lib.list_all_pins(n) if str(pins.get_pin_name(p)).startswith('As')]
    assert len(out)==1;return lib.find_then_pin(n),out[0]
try:
    playercls=unreal.EditorAssetLibrary.load_blueprint_class('/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisPlayerV1')
    guncls=unreal.EditorAssetLibrary.load_blueprint_class('/Game/ParisCombat/Blueprints/WeaponAttachmentV3/BP_PC_RifleAttachmentV3')
    bp=lib.create_blueprint_asset_with_parent(DEST,unreal.SkeletalMeshActor.static_class());assert bp
    ev=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'EventGraph')
    for n,c in (('Combatant',playercls),('SourceMesh',unreal.SkeletalMeshComponent.static_class()),('WorldGun',guncls),('DisplayGun',unreal.StaticMeshActor.static_class())):
        assert ev.add_member_variable(n,lib.get_object_reference_type(c))
    lib.set_blueprint_variable_instance_editable(bp,'Combatant',True)
    for n in ('Initialized','HasFraming'):assert ev.add_member_variable(n,lib.get_basic_type_by_name('bool'),'false')
    for n in ('CameraT','FitGunT','ViewT','FramingT','SourceFromGunT'):
        assert ev.add_member_variable(n,lib.get_struct_type(unreal.load_object(None,'/Script/CoreUObject.Transform')))
    for n in ('Desired','Goal'):assert ev.add_member_variable(n,lib.get_struct_type(unreal.load_object(None,'/Script/CoreUObject.Vector')))
    assert ev.add_member_variable('FitRotation',lib.get_struct_type(unreal.load_object(None,'/Script/CoreUObject.Rotator')))
    assert lib.compile_blueprint(bp)
    cls=unreal.EditorAssetLibrary.load_blueprint_class(DEST);cdo=unreal.get_default_object(cls)
    vm=cdo.get_component_by_class(unreal.SkeletalMeshComponent)
    vm.set_skeletal_mesh_asset(unreal.load_asset('/Game/ParisCombat/Characters/FirstPersonContinuousArmsV3/SK_PC_ContinuousArmsV3'))
    vm.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION);vm.set_only_owner_see(True);vm.set_cast_shadow(False)
    tick=cdo.get_editor_property('primary_actor_tick');enum=type(tick.get_editor_property('tick_group'))
    tick.set_editor_property('tick_group',enum.TG_POST_UPDATE_WORK);tick.set_editor_property('start_with_tick_enabled',True)
    cdo.set_editor_property('primary_actor_tick',tick)
    def refs(g):
        p=get(g,'Combatant');s=get(g,'SourceMesh');w=get(g,'WorldGun');d=get(g,'DisplayGun')
        v=get(g,'SkeletalMeshComponent','/Script/Engine.SkeletalMeshActor')
        cam=get(g,'ParisPlayerCamera',playercls.get_path_name(),p)
        return p,s,w,d,v,cam
    g=unreal.BlueprintGraphEditor.create_and_edit_function_graph(bp,'PC_InitOwnerDisplay')
    p,s,w,d,v,cam=refs(g)
    f,_=branch(g,g.find_graph_entry_pin(),pure(g,'/Script/Engine.KismetSystemLibrary.IsValid',Object=p))
    f=put(g,f,'SourceMesh',get(g,'Mesh','/Script/Engine.Character',p))
    f,original=cast(g,f,get(g,'WeaponAppearance',playercls.get_path_name(),p),guncls)
    f=put(g,f,'WorldGun',original)
    f=run(g,f,call(g,'/Script/Engine.Actor.SetOwner',NewOwner=p))
    f=put(g,f,'VisibilityBasedAnimTickOption','AlwaysTickPoseAndRefreshBones','/Script/Engine.SkinnedMeshComponent',s)
    f=run(g,f,call(g,'/Script/Engine.PrimitiveComponent.SetOwnerNoSee',self=s,bNewOwnerNoSee=True))
    wc=get(g,'StaticMeshComponent','/Script/Engine.StaticMeshActor',w)
    f=run(g,f,call(g,'/Script/Engine.PrimitiveComponent.SetOwnerNoSee',self=wc,bNewOwnerNoSee=True))
    f=run(g,f,call(g,'/Script/Engine.SkinnedMeshComponent.SetLeaderPoseComponent',self=v,NewLeaderBoneComponent=s,bForceUpdate=True,bInFollowerShouldTickPose=False))
    f=run(g,f,call(g,'/Script/Engine.ActorComponent.AddTickPrerequisiteComponent',self=v,PrerequisiteComponent=s))
    f=run(g,f,call(g,'/Script/Engine.Actor.AddTickPrerequisiteComponent',PrerequisiteComponent=s))
    f=run(g,f,call(g,'/Script/Engine.Actor.AddTickPrerequisiteActor',PrerequisiteActor=w))
    spawn=call(g,'/Script/Engine.GameplayStatics.BeginDeferredActorSpawnFromClass',ActorClass='/Script/Engine.StaticMeshActor',SpawnTransform=pure(g,'/Script/Engine.Actor.GetTransform',self=w),CollisionHandlingOverride='AlwaysSpawn',Owner=p)
    f=run(g,f,spawn)
    finish=call(g,'/Script/Engine.GameplayStatics.FinishSpawningActor',Actor=pin(spawn,'ReturnValue',True),SpawnTransform=pure(g,'/Script/Engine.Actor.GetTransform',self=w))
    f=run(g,f,finish);f,created=cast(g,f,pin(finish,'ReturnValue',True),unreal.StaticMeshActor.static_class())
    f=put(g,f,'DisplayGun',created)
    dc=get(g,'StaticMeshComponent','/Script/Engine.StaticMeshActor',d)
    for fn,kw in (
        ('/Script/Engine.SceneComponent.SetMobility',{'self':dc,'NewMobility':'Movable'}),
        ('/Script/Engine.StaticMeshComponent.SetStaticMesh',{'self':dc,'NewMesh':get(g,'StaticMesh','/Script/Engine.StaticMeshComponent',wc)}),
        ('/Script/Engine.PrimitiveComponent.SetMaterial',{'self':dc,'ElementIndex':0,'Material':pure(g,'/Script/Engine.PrimitiveComponent.GetMaterial',self=wc,ElementIndex=0)}),
        ('/Script/Engine.PrimitiveComponent.SetCollisionEnabled',{'self':dc,'NewType':'NoCollision'}),
        ('/Script/Engine.PrimitiveComponent.SetOnlyOwnerSee',{'self':dc,'bNewOnlyOwnerSee':True}),
        ('/Script/Engine.PrimitiveComponent.SetCastShadow',{'self':dc,'NewCastShadow':False})):
        f=run(g,f,call(g,fn,**kw))
    f=put(g,f,'WeaponAppearance',d,playercls.get_path_name(),p)
    f=put(g,f,'Initialized',True)
    # Update cached transforms through exec setters, avoiding expanding pure-node trees.
    g=unreal.BlueprintGraphEditor.create_and_edit_function_graph(bp,'PC_UpdateOwnerDisplay')
    p,s,w,d,v,cam=refs(g)
    f,_=branch(g,g.find_graph_entry_pin(),get(g,'Initialized'))
    alive=math(g,'Not_PreBool',A=get(g,'IsDead',playercls.get_path_name(),p))
    f=run(g,f,call(g,'/Script/Engine.SceneComponent.SetVisibility',self=v,bNewVisibility=alive,bPropagateToChildren=False))
    f=run(g,f,call(g,'/Script/Engine.SceneComponent.SetVisibility',self=get(g,'StaticMeshComponent','/Script/Engine.StaticMeshActor',d),bNewVisibility=alive,bPropagateToChildren=False))
    f,_=branch(g,f,alive)
    f=put(g,f,'CameraT',pure(g,'/Script/Engine.SceneComponent.K2_GetComponentToWorld',self=cam))
    ready=math(g,'EqualEqual_NameName',A=get(g,'ActionState',playercls.get_path_name(),p),B='Ready')
    held,reload=branch(g,f,math(g,'BooleanOR',A=ready,B=math(g,'Not_PreBool',A=get(g,'HasFraming'))))
    held=put(g,held,'SourceFromGunT',math(g,'MakeRelativeTransform',A=pure(g,'/Script/Engine.SceneComponent.K2_GetComponentToWorld',self=s),RelativeTo=pure(g,'/Script/Engine.Actor.GetTransform',self=w)))
    held=put(g,held,'Desired',math(g,'TransformLocation',T=get(g,'CameraT'),Location='(X=22,Y=22,Z=-16)'))
    held=put(g,held,'Goal',math(g,'Add_VectorVector',A=pure(g,'/Script/Engine.SceneComponent.K2_GetComponentLocation',self=cam),B=math(g,'Multiply_VectorFloat',A=pure(g,'/Script/Engine.SceneComponent.GetForwardVector',self=cam),B=20000)))
    held=put(g,held,'FitGunT',math(g,'MakeTransform',Location=get(g,'Desired'),Rotation='(Pitch=0,Yaw=0,Roll=0)',Scale='(X=1,Y=1,Z=1)'))
    for _ in range(8):
        br=call(g,'/Script/Engine.KismetMathLibrary.BreakTransform',InTransform=get(g,'FitGunT'))
        look=call(g,'/Script/Engine.KismetMathLibrary.BreakRotator',InRot=math(g,'FindLookAtRotation',Start=pin(br,'Location',True),Target=get(g,'Goal')))
        held=put(g,held,'FitRotation',math(g,'MakeRotator',Pitch=0,Yaw=math(g,'Subtract_DoubleDouble',A=pin(look,'Yaw',True),B=90),Roll=math(g,'Multiply_DoubleDouble',A=pin(look,'Pitch',True),B=-1)))
        ori=math(g,'MakeTransform',Location='(X=0,Y=0,Z=0)',Rotation=get(g,'FitRotation'),Scale='(X=1,Y=1,Z=1)')
        held=put(g,held,'FitGunT',math(g,'MakeTransform',Location=math(g,'Subtract_VectorVector',A=get(g,'Desired'),B=math(g,'TransformLocation',T=ori,Location='(X=-0.5,Y=-8,Z=0)')),Rotation=get(g,'FitRotation'),Scale='(X=1,Y=1,Z=1)'))
    held=put(g,held,'ViewT',math(g,'ComposeTransforms',A=get(g,'SourceFromGunT'),B=get(g,'FitGunT')))
    held=put(g,held,'FramingT',math(g,'MakeRelativeTransform',A=get(g,'ViewT'),RelativeTo=get(g,'CameraT')))
    held=put(g,held,'HasFraming',True)
    reload=put(g,reload,'ViewT',math(g,'ComposeTransforms',A=get(g,'FramingT'),B=get(g,'CameraT')))
    reload=put(g,reload,'FitGunT',math(g,'ComposeTransforms',A=math(g,'MakeRelativeTransform',A=pure(g,'/Script/Engine.Actor.GetTransform',self=w),RelativeTo=pure(g,'/Script/Engine.SceneComponent.K2_GetComponentToWorld',self=s)),B=get(g,'ViewT')))
    for f in (held,reload):
        f=run(g,f,call(g,'/Script/Engine.Actor.K2_SetActorTransform',self=d,NewTransform=get(g,'FitGunT'),bSweep=False,bTeleport=True))
        run(g,f,call(g,'/Script/Engine.Actor.K2_SetActorTransform',NewTransform=get(g,'ViewT'),bSweep=False,bTeleport=True))
    event=lib.add_event_override(bp,'ReceiveTick',unreal.IntPoint());assert event
    initialized,init=branch(ev,lib.find_then_pin(event),get(ev,'Initialized'))
    init=run(ev,init,call(ev,'PC_InitOwnerDisplay'))
    for f in (init,initialized):run(ev,f,call(ev,'PC_UpdateOwnerDisplay'))
    assert lib.compile_blueprint(bp)
    r['graph_errors']=[str(n) for graph in lib.list_graphs(bp) for n in unreal.BlueprintGraphEditor.get_graph_editor(graph).list_nodes_with_errors()]
    assert not r['graph_errors']
    r['node_count']=sum(len(unreal.BlueprintGraphEditor.get_graph_editor(graph).get_all_nodes()) for graph in lib.list_graphs(bp)) if hasattr(g,'get_all_nodes') else None
    assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
    pth=STORE/('Content/'+DEST.removeprefix('/Game/')+'.uasset')
    r['saved_trial']={'package':DEST,'path':pth.relative_to(ROOT).as_posix(),'size_bytes':pth.stat().st_size,'sha256':hashlib.sha256(pth.read_bytes()).hexdigest()}
    r['status']='saved_unselected_native_display_requires_fresh_test'
except Exception:
    r['status']='failed';r['errors'].append(traceback.format_exc())
finally:
    r['protected_42_unchanged']=guard();write();unreal.SystemLibrary.quit_editor()
