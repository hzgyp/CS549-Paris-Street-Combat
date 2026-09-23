"""Integrate semi-auto input, two-stage traces and scoped prototype reload playback."""
from pathlib import Path
import sys
import unreal
sys.path.insert(0,str(Path(__file__).parent))
from g1_graph import *
import build_first_asset_kit as kit
ROOT=Path(__file__).resolve().parents[2]
PLAYER='/Game/Normandy/Blueprints/Player/BP_NormandyPlayerCharacter'
PC=PLAYER+'.BP_NormandyPlayerCharacter_C'
WEAPON='/Game/Normandy/Blueprints/Player/BP_WeaponComponent'
WC=WEAPON+'.BP_WeaponComponent_C'

def import_mesh(name):
    p='/Game/Normandy/Meshes/Weapons/'+name
    if A.does_asset_exist(p):return A.load_asset(p)
    task=unreal.AssetImportTask();task.filename=str(ROOT/'Assets/Source/Normandy/RiflePrototype'/(name+'.obj'));task.destination_path='/Game/Normandy/Meshes/Weapons';task.destination_name=name
    task.automated=True;task.save=True;task.factory=unreal.FbxFactory()
    o=unreal.FbxImportUI();o.import_mesh=True;o.import_materials=False;o.import_textures=False;o.automated_import_should_detect_type=False;o.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
    o.static_mesh_import_data.convert_scene=False;o.static_mesh_import_data.convert_scene_unit=False;o.static_mesh_import_data.combine_meshes=True;o.static_mesh_import_data.auto_generate_collision=False;task.options=o
    kit.TOOLS.import_asset_tasks([task]);return A.load_asset(p)

def visual(bp):
    sub=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);data=unreal.SubobjectDataBlueprintFunctionLibrary
    handles=sub.k2_gather_subobject_data_for_blueprint(bp)
    cam=next(h for h in handles if isinstance(data.get_object_for_blueprint(sub.k2_find_subobject_data_from_handle(h),bp),unreal.CameraComponent))
    camname=str(data.get_variable_name(sub.k2_find_subobject_data_from_handle(cam)))
    named={str(data.get_variable_name(sub.k2_find_subobject_data_from_handle(h))):h for h in handles}
    if all(name in named for name in ['RiflePose','RifleWood','RifleSteel','Muzzle','MuzzleFlash']):return camname
    def add(name,cls,parent):
        if name in named:h=named[name]
        else:
            h,reason=sub.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=parent,new_class=cls,blueprint_context=bp));assert data.is_handle_valid(h),reason;assert sub.rename_subobject(h,name)
        return h,data.get_object_for_blueprint(sub.k2_find_subobject_data_from_handle(h),bp)
    root,obj=add('RiflePose',unreal.SceneComponent,cam);obj.set_editor_property('relative_location',unreal.Vector(35,18,-14))
    for name,source,mat in [('RifleWood','SM_Rifle_WoodStudy','MI_ObstacleTimber'),('RifleSteel','SM_Rifle_SteelStudy','MI_ObstacleSteel')]:
        h,c=add(name,unreal.StaticMeshComponent,root);c.set_static_mesh(import_mesh(source));c.set_material(0,A.load_asset('/Game/Normandy/Materials/FirstKit/'+mat));c.set_collision_profile_name('NoCollision');c.set_editor_property('cast_shadow',False)
    h,muzzle=add('Muzzle',unreal.SceneComponent,root);muzzle.set_editor_property('relative_location',unreal.Vector(69,0,2.5))
    h,flash=add('MuzzleFlash',unreal.PointLightComponent,h);flash.set_editor_property('intensity',4000.);flash.set_editor_property('attenuation_radius',150.);flash.set_editor_property('cast_shadows',False);flash.set_editor_property('visible',False)
    compile_save(bp);return camname

def impact_material():
    p='/Game/Normandy/Materials/Weapons/M_ImpactMark'
    m=A.load_asset(p) if A.does_asset_exist(p) else kit.TOOLS.create_asset('M_ImpactMark','/Game/Normandy/Materials/Weapons',unreal.Material,unreal.MaterialFactoryNew())
    unreal.MaterialEditingLibrary.delete_all_material_expressions(m)
    m.set_editor_property('material_domain',unreal.MaterialDomain.MD_DEFERRED_DECAL);m.set_editor_property('blend_mode',unreal.BlendMode.BLEND_TRANSLUCENT)
    uv=kit.node(m,unreal.MaterialExpressionTextureCoordinate,-800,0)
    center=kit.node(m,unreal.MaterialExpressionConstant2Vector,-800,200,r=.5,g=.5)
    distance=kit.operation(m,unreal.MaterialExpressionDistance,uv,center,-550,0)
    scale=kit.scalar(m,'EdgeScale',2.3,-550,200);edge=kit.operation(m,unreal.MaterialExpressionMultiply,distance,scale,-300,0)
    inv=kit.node(m,unreal.MaterialExpressionOneMinus,-100,0);kit.wire(edge,inv,'Input')
    opacity=kit.node(m,unreal.MaterialExpressionSaturate,100,0);kit.wire(inv,opacity,'Input')
    color=kit.color(m,'ImpactColor',(.035,.027,.019),-100,250)
    kit.output(m,color,unreal.MaterialProperty.MP_BASE_COLOR);kit.output(m,opacity,unreal.MaterialProperty.MP_OPACITY);kit.finish_material(m)
    mi=kit.instance('MI_ImpactMark',m);return mi.get_path_name()

def weapon_core():
    bp=A.load_asset(WEAPON)
    if 'NextFireTime' in [str(n) for n in L.list_member_variable_names(bp)]:return
    g=function(bp,'RequestFire')
    member(g,bp,'NextFireTime','real','0');member(g,bp,'ShotId','int','0')
    result=g.add_graph_output_parameter('Accepted',L.get_basic_type_by_name('bool'));reject=g.add_return_node()
    clock=pure(g,'game.GetTimeSeconds')
    cond=both(g,pure(g,'math.Greater_IntInt',A=get(g,'MagAmmo'),B=0),invert(g,get(g,'bReloading')))
    cond=both(g,cond,invert(g,get(g,'bDisabled')));cond=both(g,cond,pure(g,'math.GreaterEqual_DoubleDouble',A=clock,B=get(g,'NextFireTime')))
    yes,no=branch(g,g.find_graph_entry_pin(),cond)
    value(result,'Accepted','true');value(reject,'Accepted','false')
    chain(yes,setv(g,'MagAmmo',pure(g,'math.Subtract_IntInt',A=get(g,'MagAmmo'),B=1)),setv(g,'NextFireTime',pure(g,'math.Add_DoubleDouble',A=clock,B=.25)),setv(g,'ShotId',pure(g,'math.Add_IntInt',A=get(g,'ShotId'),B=1)),result)
    chain(no,reject);tidy(g);compile_save(bp)

def build():
    weapon_core();impact=impact_material();bp=A.load_asset(PLAYER);camera_name=visual(bp)
    def weapon(g):return get(g,'WeaponComponent')
    def w(g,name):return get(g,name,WC,weapon(g))
    def own(g,name,**kw):return call(g,PC+'.'+name,**kw)
    def now(g):return pure(g,'game.GetTimeSeconds')
    def controller(g):return pure(g,'game.GetPlayerController',PlayerIndex=0)
    def pressed(g,key):return pure(g,'/Script/Engine.PlayerController.WasInputKeyJustPressed',self=controller(g),Key='(KeyName="'+key+'")')
    def down(g,key):return pure(g,'/Script/Engine.PlayerController.IsInputKeyDown',self=controller(g),Key='(KeyName="'+key+'")')
    g=function(bp,'WeaponSetup')
    for n,t,d in [('LastShotTime','real','-100'),('ReloadStartTime','real','0'),('ReloadActionId','int','-1'),('ReloadVisual','bool','false'),('ReloadCommitSent','bool','false'),('ShotStatus','string',''),('AimHeld','bool','false')]:member(g,bp,n,t,d)
    L.remove_function_graph(bp,'WeaponSetup')
    hit_type=L.get_struct_type(unreal.load_object(None,'/Script/Engine.HitResult'))
    for name,args in [('ResolveImpact',[('Hit',hit_type)]),('Shoot',[]),('StartReload',[]),('UpdateReload',[]),('PollFire',[]),('PollReload',[]),('PollCrouch',[]),('UpdateWeaponPose',[('Delta','real')])]:
        g=function(bp,name)
        for n,t in args:param(g,n,t)
    compile_save(bp)
    g=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'ResolveImpact');hit=op(g.find_graph_entry_pin().get_owning_node(),'Hit')
    info=call(g,'game.BreakHitResult',Hit=hit)
    rot=pure(g,'math.MakeRotFromX',X=op(info,'ImpactNormal'))
    decal=call(g,'game.SpawnDecalAtLocation',DecalMaterial=impact,DecalSize='(X=5,Y=4,Z=4)',Location=op(info,'ImpactPoint'),Rotation=rot,LifeSpan=12)
    chain(g.find_graph_entry_pin(),decal,setv(g,'ShotStatus','HIT'))
    g=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'Shoot')
    fire=call(g,WC+'.RequestFire',self=weapon(g));start=chain(g.find_graph_entry_pin(),fire)
    yes,_=branch(g,start,op(fire,'Accepted'))
    start=chain(yes,setv(g,'LastShotTime',now(g)),setv(g,'ShotStatus',''))
    mgr=pure(g,'game.GetPlayerCameraManager',PlayerIndex=0)
    camloc=pure(g,'/Script/Engine.PlayerCameraManager.GetCameraLocation',self=mgr)
    camrot=pure(g,'/Script/Engine.PlayerCameraManager.GetCameraRotation',self=mgr)
    view=pure(g,'math.MakeTransform',Location=camloc,Rotation=camrot,Scale='(X=1,Y=1,Z=1)')
    end=pure(g,'math.TransformLocation',T=view,Location='(X=15000,Y=0,Z=0)')
    muzzle=pure(g,'/Script/Engine.SceneComponent.K2_GetComponentLocation',self=get(g,'Muzzle'))
    def trace(name,startpos,endpos,**kw):return call(g,'system.'+name,Start=startpos,End=endpos,TraceChannel='TraceTypeQuery3',bTraceComplex='false',DrawDebugType='None',bIgnoreSelf='true',**kw)
    clearance=trace('SphereTraceSingle',camloc,muzzle,Radius=3)
    start=chain(start,clearance)
    blocked,clear=branch(g,start,op(clearance))
    chain(blocked,own(g,'ResolveImpact',Hit=op(clearance,'OutHit')),setv(g,'ShotStatus','MUZZLE BLOCKED'))
    camera_trace=trace('LineTraceSingle',camloc,end);start=chain(clear,camera_trace)
    aim_hit=call(g,'game.BreakHitResult',Hit=op(camera_trace,'OutHit'))
    aimpoint=pure(g,'math.SelectVector',A=op(aim_hit,'ImpactPoint'),B=end,bPickA=op(camera_trace))
    # Continue slightly past the camera hit: an endpoint exactly on a plane can miss
    # due to query precision when the second ray starts from a different location.
    ray=pure(g,'math.MakeTransform',Location=aimpoint,Rotation=pure(g,'math.FindLookAtRotation',Start=muzzle,Target=aimpoint),Scale='(X=1,Y=1,Z=1)')
    muzzle_end=pure(g,'math.TransformLocation',T=ray,Location='(X=5,Y=0,Z=0)')
    muzzle_trace=trace('LineTraceSingle',muzzle,muzzle_end);start=chain(start,muzzle_trace)
    hit,_=branch(g,start,op(muzzle_trace));chain(hit,own(g,'ResolveImpact',Hit=op(muzzle_trace,'OutHit')))
    g=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'StartReload')
    # Empty-only prototype avoids inventing a partial Garand reload animation.
    yes,_=branch(g,g.find_graph_entry_pin(),eq(g,w(g,'MagAmmo'),0))
    begin=call(g,WC+'.BeginReload',self=weapon(g));start=chain(yes,begin)
    yes,_=branch(g,start,pure(g,'math.GreaterEqual_IntInt',A=op(begin,'StartedActionId'),B=0))
    chain(yes,setv(g,'ReloadActionId',op(begin,'StartedActionId')),setv(g,'ReloadStartTime',now(g)),setv(g,'ReloadCommitSent','false'),setv(g,'ReloadVisual','true'))
    g=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'UpdateReload')
    active,_=branch(g,g.find_graph_entry_pin(),get(g,'ReloadVisual'))
    cancel,start=branch(g,active,w(g,'bDisabled'))
    chain(cancel,call(g,WC+'.EndReload',self=weapon(g),ExpectedActionId=get(g,'ReloadActionId')),setv(g,'ReloadVisual','false'))
    elapsed=pure(g,'math.Subtract_DoubleDouble',A=now(g),B=get(g,'ReloadStartTime'))
    commit,start=branch(g,start,both(g,invert(g,get(g,'ReloadCommitSent')),pure(g,'math.GreaterEqual_DoubleDouble',A=elapsed,B=1.4)))
    chain(commit,call(g,WC+'.CommitReload',self=weapon(g),ExpectedActionId=get(g,'ReloadActionId')),setv(g,'ReloadCommitSent','true'))
    finish,_=branch(g,start,pure(g,'math.GreaterEqual_DoubleDouble',A=elapsed,B=2.4))
    chain(finish,call(g,WC+'.EndReload',self=weapon(g),ExpectedActionId=get(g,'ReloadActionId')),setv(g,'ReloadVisual','false'))
    for name,key,target in [('PollFire','LeftMouseButton','Shoot'),('PollReload','R','StartReload')]:
        g=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,name);yes,_=branch(g,g.find_graph_entry_pin(),pressed(g,key));chain(yes,own(g,target))
    g=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'PollCrouch')
    yes,no=branch(g,g.find_graph_entry_pin(),down(g,'LeftControl'))
    chain(yes,call(g,'/Script/Engine.Character.Crouch'));chain(no,call(g,'/Script/Engine.Character.UnCrouch'))
    g=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'UpdateWeaponPose')
    aim=both(g,down(g,'RightMouseButton'),both(g,invert(g,get(g,'ReloadVisual')),invert(g,w(g,'bDisabled'))))
    start=chain(g.find_graph_entry_pin(),setv(g,'AimHeld',aim))
    fov=pure(g,'math.SelectFloat',A=70,B=90,bPickA=get(g,'AimHeld'))
    y=pure(g,'math.SelectFloat',A=0,B=18,bPickA=get(g,'AimHeld'))
    z=pure(g,'math.SelectFloat',A=-5,B=-14,bPickA=get(g,'AimHeld'))
    z=pure(g,'math.SelectFloat',A=-32,B=z,bPickA=get(g,'ReloadVisual'))
    recoil=pure(g,'math.FClamp',Value=pure(g,'math.Subtract_DoubleDouble',A=1,B=pure(g,'math.Divide_DoubleDouble',A=pure(g,'math.Subtract_DoubleDouble',A=now(g),B=get(g,'LastShotTime')),B=.14)),Min=0,Max=1)
    x=pure(g,'math.Subtract_DoubleDouble',A=35,B=pure(g,'math.Multiply_DoubleDouble',A=recoil,B=4))
    pose=call(g,'/Script/Engine.SceneComponent.K2_SetRelativeLocation',self=get(g,'RiflePose'),NewLocation=pure(g,'math.MakeVector',X=x,Y=y,Z=z),bSweep='false',bTeleport='true')
    chain(start,pose,call(g,'/Script/Engine.CameraComponent.SetFieldOfView',self=get(g,camera_name),InFieldOfView=fov),call(g,'/Script/Engine.SceneComponent.SetVisibility',self=get(g,'MuzzleFlash'),bNewVisibility=pure(g,'math.Greater_DoubleDouble',A=recoil,B=.6),bPropagateToChildren='false'))
    compile_save(bp)
    events=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'EventGraph')
    old=events.find_event_node('ReceiveTick')
    if old:
        # This child's Tick is owned by the weapon integration; parent input graphs are inherited.
        events.remove_nodes(events.list_all_nodes())
    tick=L.add_event_override(bp,'ReceiveTick',unreal.IntPoint(0,0));assert tick
    chain(op(tick,'then'),own(events,'PollFire'),own(events,'PollReload'),own(events,'UpdateReload'),own(events,'PollCrouch'),own(events,'UpdateWeaponPose',Delta=op(tick,'DeltaSeconds')))
    for name in L.list_graph_names(bp):tidy(unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,name))
    compile_save(bp)
    default=unreal.get_default_object(bp.generated_class());props=default.character_movement.get_editor_property('nav_agent_props');props.set_editor_property('can_crouch',True);default.character_movement.set_editor_property('nav_agent_props',props)
    assert A.save_loaded_asset(bp,only_if_is_dirty=False)
    unreal.log('G1_WEAPON integrated input/trace/empty reload prototype; historical hand/clip animation pending')

if __name__=='__main__':build()
