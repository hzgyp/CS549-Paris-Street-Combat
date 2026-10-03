"""Author only new same-model owner-view/copy-pose drafts; preserve all existing inputs."""
import hashlib,json,os,sys,traceback
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from ue_paris_graph_helpers import lib,pins,wire,pin,call,pure,get,run,value,cast_to
from ue_player_aim_runtime_preview import trial_records
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
EVIDENCE=STORE/'Evidence/CityGameplay20261002/FirstPersonViewV1'
OUT=EVIDENCE/os.environ['CS549_FP_IDENTITY']
assert OUT.name.replace('_','').isalnum() and not OUT.exists();OUT.mkdir(parents=True)
ANIM='/Game/ParisCombat/Animation/FirstPersonViewV1/ABP_PC_FirstPersonCopyV1'
VIEW='/Game/ParisCombat/Blueprints/FirstPersonViewV1/BP_PC_FirstPersonViewV1'
SOURCE='/Game/ParisCombat/Animation/DirectionalDraft/ABP_PC_Allied_Stride_v1'
inv=json.loads((ROOT/'Assets/Integration/CITY_RIFLE_ACTION_DRAFT_INVENTORY_20261002.json').read_text())
dep=json.loads((ROOT/inv['retained_dependency_inventory']).read_text())
records=inv['files']+dep['files']+inv['retained_unselected_rejected_trial']+trial_records()
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert all(digest(ROOT/e['path'])==e['sha256'] for e in records)
diagnosis=json.loads((EVIDENCE/'diagnosis_accepted.json').read_text())
assert diagnosis.get('strict_frozen_pass') is True,'Validated matched-phase isolation required before native authoring'
r={'scope':__doc__,'status':'initializing','errors':[],'files':[]}
def math(g,n,**args):return pure(g,'/Script/Engine.KismetMathLibrary.'+n,**args)
def put(g,flow,n,v):
    setter=g.add_set_member_variable_node(n);value(pin(setter,n),v);return run(g,flow,setter)
def branch(g,flow,condition):
    n=g.add_branch_node();wire(condition,pin(n,'Condition'));wire(flow,lib.find_execute_pin(n));return pin(n,'then',True),pin(n,'else',True)
def rot(g,look):
    split=call(g,'/Script/Engine.KismetMathLibrary.BreakRotator',InRot=look)
    return math(g,'MakeRotator',Pitch=0,Yaw=math(g,'Subtract_DoubleDouble',A=pin(split,'Yaw',True),B=90),Roll=math(g,'Multiply_DoubleDouble',A=pin(split,'Pitch',True),B=-1))
def transform(g,rotation,location='(X=0,Y=0,Z=0)'):
    return math(g,'MakeTransform',Location=location,Rotation=rotation,Scale='(X=1,Y=1,Z=1)')
try:
    assert not unreal.EditorAssetLibrary.does_asset_exist(ANIM) and not unreal.EditorAssetLibrary.does_asset_exist(VIEW),'Preserve occupied drafts'
    player_cls=unreal.EditorAssetLibrary.load_blueprint_class('/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisPlayerV1')
    view=lib.create_blueprint_asset_with_parent(VIEW,unreal.SkeletalMeshActor.static_class());assert view
    events=unreal.BlueprintGraphEditor.get_graph_editor_by_name(view,'EventGraph')
    assert events.add_member_variable('SourceMesh',lib.get_object_reference_type(unreal.SkeletalMeshComponent.static_class()))
    assert events.add_member_variable('Combatant',lib.get_object_reference_type(player_cls))
    assert events.add_member_variable('ReadyCameraTransform',lib.get_struct_type(unreal.load_object(None,'/Script/CoreUObject.Transform')))
    assert events.add_member_variable('RightGripCamera',lib.get_struct_type(unreal.load_object(None,'/Script/CoreUObject.Vector')),'(X=38,Y=14,Z=-16)')
    for n in ('SourceMesh','Combatant','RightGripCamera'):lib.set_blueprint_variable_instance_editable(view,n,True)
    assert lib.compile_blueprint(view)
    view_cls=unreal.EditorAssetLibrary.load_blueprint_class(VIEW)
    anim=unreal.EditorAssetLibrary.duplicate_asset(SOURCE,ANIM);assert anim
    ae=unreal.BlueprintGraphEditor.get_graph_editor_by_name(anim,'EventGraph')
    assert ae.add_member_variable('ViewSourceMesh',lib.get_object_reference_type(unreal.SkeletalMeshComponent.static_class()))
    assert lib.compile_blueprint(anim)
    r['copy_helper']=json.loads(unreal.ParisBlueprintAuthoring.build_first_person_copy_pose(anim));assert r['copy_helper']['success']
    update=ae.find_event_node('BlueprintUpdateAnimation');assert update
    start=lib.find_then_pin(update);pins.break_pin_links(start)
    flow,actor=cast_to(ae,start,pure(ae,'/Script/Engine.AnimInstance.GetOwningActor'),view_cls)
    put(ae,flow,'ViewSourceMesh',get(ae,'SourceMesh',view_cls.get_path_name(),actor))
    assert lib.compile_blueprint(anim)
    cdo=unreal.get_default_object(view_cls)
    component=cdo.get_component_by_class(unreal.SkeletalMeshComponent)
    component.set_skeletal_mesh_asset(unreal.load_asset('/Game/ParisCombat/Characters/Adaptation/Meshes/SK_WWII_US_Paratrooper_simple_UE582_v1'))
    component.set_anim_instance_class(unreal.EditorAssetLibrary.load_blueprint_class(ANIM))
    component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    component.set_only_owner_see(True);component.set_cast_shadow(False)
    component.set_editor_property('visibility_based_anim_tick_option',unreal.VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE_AND_REFRESH_BONES)
    tick=cdo.get_editor_property('primary_actor_tick');tick_enum=type(tick.get_editor_property('tick_group'))
    tick.set_editor_property('tick_group',tick_enum.TG_POST_UPDATE_WORK);cdo.set_editor_property('primary_actor_tick',tick)
    component.set_tick_group(tick_enum.TG_POST_UPDATE_WORK)
    g=unreal.BlueprintGraphEditor.create_and_edit_function_graph(view,'PC_UpdateFirstPersonView')
    source,combatant=get(g,'SourceMesh'),get(g,'Combatant')
    valid=math(g,'BooleanAND',A=pure(g,'/Script/Engine.KismetSystemLibrary.IsValid',Object=source),B=pure(g,'/Script/Engine.KismetSystemLibrary.IsValid',Object=combatant))
    flow,invalid=branch(g,g.find_graph_entry_pin(),valid)
    camera=get(g,'ParisPlayerCamera',player_cls.get_path_name(),combatant)
    ct=pure(g,'/Script/Engine.SceneComponent.K2_GetComponentToWorld',self=camera)
    ready=math(g,'EqualEqual_NameName',A=get(g,'ActionState',player_cls.get_path_name(),combatant),B='Ready')
    ready=math(g,'BooleanAND',A=ready,B=math(g,'Not_PreBool',A=get(g,'IsDead',player_cls.get_path_name(),combatant)))
    held,action=branch(g,flow,ready)
    def center(side):
        fs=('middle','ring','pinky') if side=='r' else ('index','middle','ring','pinky')
        ns=[f+'_0'+str(s)+'_'+side for f in fs for s in (2,3)]+['thumb_02_'+side,'thumb_03_'+side]
        points=[pure(g,'/Script/Engine.SceneComponent.GetSocketLocation',self=source,InSocketName=n) for n in ns]
        p=points[0]
        for q in points[1:]:p=math(g,'Add_VectorVector',A=p,B=q)
        return math(g,'Multiply_VectorFloat',A=p,B=1/len(points))
    right,left=center('r'),center('l')
    source_t=pure(g,'/Script/Engine.SceneComponent.K2_GetComponentToWorld',self=source)
    right_local=math(g,'InverseTransformLocation',T=source_t,Location=right)
    desired=math(g,'TransformLocation',T=ct,Location=get(g,'RightGripCamera'))
    start=pure(g,'/Script/Engine.SceneComponent.K2_GetComponentLocation',self=camera)
    end=math(g,'Add_VectorVector',A=start,B=math(g,'Multiply_VectorFloat',A=pure(g,'/Script/Engine.SceneComponent.GetForwardVector',self=camera),B=20000))
    trace=call(g,'/Script/Engine.KismetSystemLibrary.LineTraceSingle',Start=start,End=end,TraceChannel='TraceTypeQuery1',bTraceComplex=False,bIgnoreSelf=True)
    array=g.create_node_from_name('Utilities|Array|MakeArray',unreal.Vector2D(),[]);assert array
    wire(pin(array,'Array',True),pin(trace,'ActorsToIgnore'));wire(combatant,pin(array,'[0]'))
    held=run(g,held,trace)
    hit=call(g,'/Script/Engine.GameplayStatics.BreakHitResult',Hit=pin(trace,'OutHit',True))
    goal=math(g,'SelectVector',A=pin(hit,'ImpactPoint',True),B=end,bPickA=pin(trace,'ReturnValue',True))
    gun_location=desired
    for _ in range(4):
        gun_rotation=rot(g,math(g,'FindLookAtRotation',Start=gun_location,Target=goal))
        gun_location=math(g,'Subtract_VectorVector',A=desired,B=math(g,'TransformLocation',T=transform(g,gun_rotation),Location='(X=-0.5,Y=-8,Z=0)'))
    original_rotation=rot(g,math(g,'FindLookAtRotation',Start=right,Target=left))
    relative=math(g,'MakeRelativeTransform',A=source_t,RelativeTo=transform(g,original_rotation))
    rotated=math(g,'ComposeTransforms',A=relative,B=transform(g,gun_rotation))
    split=call(g,'/Script/Engine.KismetMathLibrary.BreakTransform',InTransform=rotated)
    rotation=pin(split,'Rotation',True)
    location=math(g,'Subtract_VectorVector',A=desired,B=math(g,'TransformLocation',T=transform(g,rotation),Location=right_local))
    new_transform=transform(g,rotation,location)
    held=run(g,held,call(g,'/Script/Engine.Actor.K2_SetActorTransform',NewTransform=new_transform,bSweep=False,bTeleport=True))
    put(g,held,'ReadyCameraTransform',math(g,'MakeRelativeTransform',A=new_transform,RelativeTo=ct))
    run(g,action,call(g,'/Script/Engine.Actor.K2_SetActorTransform',NewTransform=math(g,'ComposeTransforms',A=get(g,'ReadyCameraTransform'),B=ct),bSweep=False,bTeleport=True))
    event=lib.add_event_override(view,'ReceiveTick',unreal.IntPoint(0,0));assert event
    run(events,lib.find_then_pin(event),call(events,'PC_UpdateFirstPersonView'))
    begin=lib.add_event_override(view,'ReceiveBeginPlay',unreal.IntPoint(0,300));assert begin
    flow=lib.find_then_pin(begin)
    ownmesh=get(events,'SkeletalMeshComponent','/Script/Engine.SkeletalMeshActor')
    flow=run(events,flow,call(events,'/Script/Engine.Actor.AddTickPrerequisiteComponent',PrerequisiteComponent=get(events,'SourceMesh')))
    flow=run(events,flow,call(events,'/Script/Engine.Actor.SetTickGroup',NewTickGroup='TG_PostUpdateWork'))
    flow=run(events,flow,call(events,'/Script/Engine.ActorComponent.AddTickPrerequisiteActor',self=ownmesh,PrerequisiteActor=pure(events,'/Script/Engine.ActorComponent.GetOwner',self=ownmesh)))
    flow=run(events,flow,call(events,'/Script/Engine.ActorComponent.AddTickPrerequisiteComponent',self=ownmesh,PrerequisiteComponent=get(events,'SourceMesh')))
    for bone in ('neck_01','thigh_l','thigh_r'):
        flow=run(events,flow,call(events,'/Script/Engine.SkinnedMeshComponent.HideBoneByName',self=ownmesh,BoneName=bone,PhysBodyOption='PBO_None'))
    run(events,flow,call(events,'/Script/Engine.Actor.SetActorTickEnabled',bEnabled=True))
    assert lib.compile_blueprint(view)
    for bp in (anim,view):
        errors=[str(n) for graph in lib.list_graphs(bp) for n in unreal.BlueprintGraphEditor.get_graph_editor(graph).list_nodes_with_errors()]
        assert not errors,errors
        assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
    r['status']='saved_unselected_same_model_view_requires_runtime_validation'
except Exception:r['status']='failed';r['errors'].append(traceback.format_exc())
finally:
    for package in (ANIM,VIEW):
        f=STORE/('Content/'+package.removeprefix('/Game/')+'.uasset')
        if f.exists():r['files'].append({'package':package,'path':f.relative_to(ROOT).as_posix(),'size_bytes':f.stat().st_size,'sha256':digest(f)})
    r['protected_40_unchanged']=all(digest(ROOT/e['path'])==e['sha256'] for e in records)
    if not r['errors'] and r['protected_40_unchanged']:
        inventory=ROOT/'Assets/Integration/FIRST_PERSON_VIEW_TRIAL_INVENTORY_20261002.json'
        assert not inventory.exists()
        inventory.write_text(json.dumps({'schema_version':1,'record_date':'2026-10-02','owner':'yg745',
          'status':'unselected_unpublished_drafts_pending_runtime_and_human_review','author_evidence':OUT.relative_to(ROOT).as_posix(),
          'files':r['files'],'retained_original_count':40,'active_city_unchanged':True,'camera_unchanged':True,
          'scope':'Same source mesh and evaluated pose; owner-view rigid placement; no source geometry/finger/gameplay edits'},indent=2)+'\n')
    (OUT/'result.json').write_text(json.dumps(r,indent=2));unreal.SystemLibrary.quit_editor()
