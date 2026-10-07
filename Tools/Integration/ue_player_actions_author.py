"""New-only engine Blueprint action authoring. No runtime Python or bridge nodes."""
import hashlib,json,os,sys,traceback
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[2]; STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT=STORE/'Evidence/PlayerActionsV1'/os.environ['CS549_ACTION_IDENTITY']
assert not OUT.exists();OUT.mkdir(parents=True)
sys.path.insert(0,str(Path(__file__).parent))
from ue_paris_graph_helpers import lib,pins,pin,wire,value,call,pure,get,run
DEST='/Game/ParisCombat/Blueprints/PlayerActionsV1/BP_PCParisPlayerActionsV6'
PARENT='/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisPlayerV1'
records=json.loads((ROOT/'Assets/Integration/CITY_CONTINUOUS_ARMS_NATIVE_INVENTORY_20261003.json').read_text())['files']
records+=json.loads((ROOT/'Assets/Sync/manifests/paris-gameplay-native-playtest.json').read_text())['files']
source_guards=[]
for p in (STORE/'Content/RifleAnimsetPro/Animations/InPlace').glob('*.uasset'):
    source_guards.append({'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
records+=source_guards
def guard():return all(hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256'] for f in records)
assert guard();assert not unreal.EditorAssetLibrary.does_asset_exist(DEST)
r={'errors':[],'status':'authoring','map_saved':False,'packages':[],'source_guards':source_guards}
(OUT/'source.py').write_bytes(Path(__file__).read_bytes())
def math(g,n,**kw):return pure(g,'/Script/Engine.KismetMathLibrary.'+n,**kw)
def branch(g,f,c):
    n=g.add_branch_node();wire(f,lib.find_execute_pin(n));wire(c,pin(n,'Condition'));return pin(n,'then',True),pin(n,'else',True)
def put(g,f,n,v,cls='',target=None):
    node=g.add_set_member_variable_node(n,cls)
    if target is not None:wire(target,lib.find_self_pin(node))
    value(pin(node,n),v);return run(g,f,node)
def fn(name):return unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,name)
def alive(g,f):return branch(g,f,math(g,'Not_PreBool',A=get(g,'IsDead')))[0]
def ready(g):return math(g,'EqualEqual_NameName',A=get(g,'ActionState'),B='Ready')
def standing(g):return math(g,'Not_PreBool',A=get(g,'bIsCrouched','/Script/Engine.Character'))
def grounded(g):
    mode=get(g,'MovementMode','/Script/Engine.CharacterMovementComponent',move(g))
    return math(g,'BooleanOR',A=math(g,'EqualEqual_ByteByte',A=mode,B=1),B=math(g,'EqualEqual_ByteByte',A=mode,B=2))
def cancel(g,f):return run(g,f,call(g,'PC_EndReload',ExpectedActionID=get(g,'ActionID'),ExpectedGeneration=get(g,'RestoreGeneration')))
def move(g):return get(g,'CharacterMovement','/Script/Engine.Character')
def mesh(g):return get(g,'Mesh','/Script/Engine.Character')
def cap(g):return get(g,'CapsuleComponent','/Script/Engine.Character')
def half(g):return pure(g,'/Script/Engine.CapsuleComponent.GetUnscaledCapsuleHalfHeight',self=cap(g))
def loc(g):return pure(g,'/Script/Engine.Actor.K2_GetActorLocation')
def plus(g,a,b):return math(g,'Add_VectorVector',A=a,B=b)
def vector(g,z):return math(g,'MakeVector',X=0,Y=0,Z=z)
def scaled(g,v,k):return math(g,'Multiply_VectorFloat',A=v,B=k)
def feet(g):return plus(g,loc(g),vector(g,math(g,'Multiply_DoubleDouble',A=half(g),B=-1)))
def choose_pose(g,f,clip,loop=True):
    # Tick switches only when clip or engine mode differs, never reinitializes a stable loop.
    asset='/Game/RifleAnimsetPro/Animations/InPlace/'+clip+'.'+clip
    changed=math(g,'BooleanOR',A=math(g,'NotEqual_NameName',A=get(g,'ActivePose'),B=clip),
        B=math(g,'NotEqual_ByteByte',A=get(g,'AnimationMode','/Script/Engine.SkeletalMeshComponent',mesh(g)),B=1))
    f,_=branch(g,f,changed);f=put(g,f,'ActivePose',clip)
    return run(g,f,call(g,'/Script/Engine.SkeletalMeshComponent.PlayAnimation',self=mesh(g),NewAnimToPlay=asset,bLooping=loop))
try:
    parent=unreal.EditorAssetLibrary.load_blueprint_class(PARENT)
    bp=lib.create_blueprint_asset_with_parent(DEST,parent);assert bp
    ev=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'EventGraph')
    for name,t,d in [('RunHeld','bool','false'),('SlowHeld','bool','false'),('WasFalling','bool','false'),
                     ('ProneClear','bool','false'),('ProneBlocked','bool','false'),('DesiredPosture','int','0'),
                     ('SeenGeneration','int','0'),('ActivePose','name','None'),('LocomotionState','name','Walk'),
                     ('LandUntil','real','0'),('ProneProbeAxis','real','0')]:
        assert ev.add_member_variable(name,lib.get_basic_type_by_name(t),d)
    assert lib.compile_blueprint(bp)
    for name in ('PC_ActionRunOn','PC_ActionRunOff','PC_ActionSlowOn','PC_ActionSlowOff','PC_ActionJump','PC_ActionJumpOff',
                 'PC_ActionCrouch','PC_ActionProne','PC_CheckProneClearance','PC_ActionFire','PC_ActionReload',
                 'PC_ActionTick','PC_UpdateActions','PC_UpdateActionPose','PC_PlayStandingPose','PC_PlayCrouchPose','PC_PlayPronePose',
                 'PC_ActionMoveForward','PC_ActionMoveRight','PC_ActionLookYaw'):
        graph=unreal.BlueprintGraphEditor.create_and_edit_function_graph(bp,name)
        if name=='PC_ActionTick':graph.add_graph_input_parameter('DeltaSeconds',lib.get_basic_type_by_name('real'))
        if name in ('PC_ActionMoveForward','PC_ActionMoveRight','PC_ActionLookYaw'):graph.add_graph_input_parameter('AxisValue',lib.get_basic_type_by_name('real'))
    assert lib.compile_blueprint(bp)
    cls=unreal.EditorAssetLibrary.load_blueprint_class(DEST);d=unreal.get_default_object(cls)
    m=d.character_movement; nav=m.get_editor_property('nav_agent_props');nav.set_editor_property('can_crouch',True);m.set_editor_property('nav_agent_props',nav)
    m.set_editor_property('crouched_half_height',60);m.set_editor_property('max_walk_speed_crouched',120);m.set_editor_property('jump_z_velocity',360)
    m.set_editor_property('can_walk_off_ledges_when_crouching',False)
    tick=d.get_editor_property('primary_actor_tick');tick.set_editor_property('start_with_tick_enabled',True);d.set_editor_property('primary_actor_tick',tick)
    # Guarded reload cancellation uses the existing transaction endpoint and IDs.
    for name,field,enabled in [('PC_ActionRunOn','RunHeld',True),('PC_ActionRunOff','RunHeld',False),('PC_ActionSlowOn','SlowHeld',True),('PC_ActionSlowOff','SlowHeld',False)]:
        g=fn(name);f=alive(g,g.find_graph_entry_pin())
        if field=='RunHeld' and enabled:f=cancel(g,f)
        put(g,f,field,enabled)
    g=fn('PC_ActionJump');f=alive(g,g.find_graph_entry_pin())
    legal=math(g,'BooleanAND',A=standing(g),B=grounded(g))
    legal=math(g,'BooleanAND',A=legal,B=math(g,'EqualEqual_IntInt',A=get(g,'DesiredPosture'),B=0));f,_=branch(g,f,legal)
    f=cancel(g,f);run(g,f,call(g,'/Script/Engine.Character.Jump'))
    g=fn('PC_ActionJumpOff');run(g,g.find_graph_entry_pin(),call(g,'/Script/Engine.Character.StopJumping'))
    for name,target in [('PC_ActionCrouch',1),('PC_ActionProne',2)]:
        g=fn(name);f=alive(g,g.find_graph_entry_pin());f,_=branch(g,f,grounded(g));f=cancel(g,f)
        f=put(g,f,'ProneProbeAxis',0)
        same,enter=branch(g,f,math(g,'EqualEqual_IntInt',A=get(g,'DesiredPosture'),B=target))
        put(g,same,'DesiredPosture',0)
        if target==2:
            enter=run(g,enter,call(g,'PC_CheckProneClearance'))
            enter,_=branch(g,enter,get(g,'ProneClear'))
        enter=put(g,enter,'RunHeld',False);put(g,enter,'DesiredPosture',target)
    # Measured prone head/hands/feet exceeded the old envelope. Pad actual bone extents.
    g=fn('PC_CheckProneClearance');f=g.find_graph_entry_pin();f=put(g,f,'ProneClear',True)
    base=feet(g);forward=pure(g,'/Script/Engine.Actor.GetActorForwardVector')
    center=plus(g,base,vector(g,30))
    velocity=pure(g,'/Script/Engine.Actor.GetVelocity')
    pending=pure(g,'/Script/Engine.Pawn.GetPendingMovementInputVector')
    intended=scaled(g,math(g,'Normal',A=pending),60)
    fallback=math(g,'SelectVector',A=intended,B=velocity,bPickA=math(g,'Greater_DoubleDouble',A=math(g,'VSizeSquared',A=pending),B=.01))
    requested=scaled(g,forward,math(g,'Multiply_DoubleDouble',A=get(g,'ProneProbeAxis'),B=60))
    direction=math(g,'SelectVector',A=requested,B=fallback,bPickA=math(g,'Greater_DoubleDouble',A=math(g,'Abs',A=get(g,'ProneProbeAxis')),B=.01))
    dt=math(g,'FMax',A=.1,B=pure(g,'/Script/Engine.GameplayStatics.GetWorldDeltaSeconds'))
    travel=math(g,'Multiply_VectorVector',A=direction,B=math(g,'MakeVector',X=dt,Y=dt,Z=dt))
    future=plus(g,center,travel)
    box=call(g,'/Script/Engine.KismetSystemLibrary.BoxTraceSingle',Start=center,End=future,HalfSize='(X=130,Y=55,Z=28)',
             Orientation=pure(g,'/Script/Engine.Actor.K2_GetActorRotation'),TraceChannel='TraceTypeQuery1',bTraceComplex=False,DrawDebugType='None',bIgnoreSelf=True)
    f=run(g,f,box);f=put(g,f,'ProneClear',math(g,'Not_PreBool',A=pin(box,'ReturnValue',True)))
    # Three floor supports prohibit unsupported ledges and steep/uneven ground.
    for offset in (-120,0,110):
        point=plus(g,base,scaled(g,forward,offset))
        tr=call(g,'/Script/Engine.KismetSystemLibrary.LineTraceSingle',Start=plus(g,point,vector(g,40)),End=plus(g,point,vector(g,-30)),
                TraceChannel='TraceTypeQuery1',bTraceComplex=False,DrawDebugType='None',bIgnoreSelf=True)
        f=run(g,f,tr)
        hit=call(g,'/Script/Engine.GameplayStatics.BreakHitResult',Hit=pin(tr,'OutHit',True))
        normal=call(g,'/Script/Engine.KismetMathLibrary.BreakVector',InVec=pin(hit,'ImpactNormal',True))
        height=call(g,'/Script/Engine.KismetMathLibrary.BreakVector',InVec=pin(hit,'ImpactPoint',True))
        floor=call(g,'/Script/Engine.KismetMathLibrary.BreakVector',InVec=base)
        okay=math(g,'BooleanAND',A=pin(tr,'ReturnValue',True),B=math(g,'GreaterEqual_DoubleDouble',A=pin(normal,'Z',True),B=.97))
        okay=math(g,'BooleanAND',A=okay,B=math(g,'LessEqual_DoubleDouble',A=math(g,'Abs',A=math(g,'Subtract_DoubleDouble',A=pin(height,'Z',True),B=pin(floor,'Z',True))),B=10))
        f=put(g,f,'ProneClear',math(g,'BooleanAND',A=get(g,'ProneClear'),B=okay))
    # Fire/reload wrappers preserve original functions and reject incompatible movement.
    for name,request in [('PC_ActionFire','PC_PlayerFire'),('PC_ActionReload','PC_RequestReload')]:
        g=fn(name);f=alive(g,g.find_graph_entry_pin())
        legal=math(g,'BooleanAND',A=grounded(g),B=math(g,'Not_PreBool',A=get(g,'RunHeld')))
        # Standing-only until posture-specific rifle contact is visually accepted.
        legal=math(g,'BooleanAND',A=legal,B=standing(g))
        legal=math(g,'BooleanAND',A=legal,B=math(g,'EqualEqual_IntInt',A=get(g,'DesiredPosture'),B=0))
        legal=math(g,'BooleanAND',A=legal,B=math(g,'Not_PreBool',A=get(g,'bPressedJump','/Script/Engine.Character')))
        f,_=branch(g,f,legal);run(g,f,call(g,request))
    # Tick always advances inherited reload polling before pose selection.
    g=fn('PC_ActionTick');entry=g.find_graph_entry_pin()
    f=run(g,entry,call(g,'PC_PollReloadPhase',DeltaSeconds=pin(entry.get_owning_node(),'DeltaSeconds',True)))
    f=alive(g,f)
    reset,normal=branch(g,f,math(g,'NotEqual_IntInt',A=get(g,'SeenGeneration'),B=get(g,'RestoreGeneration')))
    reset=put(g,reset,'SeenGeneration',get(g,'RestoreGeneration'))
    for n,v in [('RunHeld',False),('SlowHeld',False),('DesiredPosture',0),('ActivePose','None'),('WasFalling',False),('LandUntil',0),('ProneProbeAxis',0)]:reset=put(g,reset,n,v)
    # Merge the two paths through a separate update function, keeping pure getters ordered.
    for path in (reset,normal):run(g,path,call(g,'PC_UpdateActions'))
    g=fn('PC_UpdateActions');f=g.find_graph_entry_pin()
    # Request engine crouch/uncrouch. A crouch-to-prone change first safely stands;
    # if overhead clearance blocks that, the actual posture remains crouched.
    want_stand,want_low=branch(g,f,math(g,'EqualEqual_IntInt',A=get(g,'DesiredPosture'),B=0))
    want_stand=run(g,want_stand,call(g,'/Script/Engine.Character.UnCrouch'))
    crouch_target,prone_target=branch(g,want_low,math(g,'EqualEqual_IntInt',A=get(g,'DesiredPosture'),B=1))
    for path,height in ((crouch_target,60),(prone_target,34)):
        wrong=math(g,'BooleanAND',A=get(g,'bIsCrouched','/Script/Engine.Character'),B=math(g,'NotEqual_DoubleDouble',A=half(g),B=height))
        un,lower=branch(g,path,wrong)
        un=run(g,un,call(g,'/Script/Engine.Character.UnCrouch'))
        lower=run(g,lower,call(g,'/Script/Engine.CharacterMovementComponent.SetCrouchedHalfHeight',self=move(g),NewValue=height))
        lower=run(g,lower,call(g,'/Script/Engine.Character.Crouch'))
        for q in (un,lower):run(g,q,call(g,'PC_UpdateActionPose'))
    run(g,want_stand,call(g,'PC_UpdateActionPose'))
    g=fn('PC_UpdateActionPose');f=g.find_graph_entry_pin()
    crouched=get(g,'bIsCrouched','/Script/Engine.Character')
    low,high=branch(g,f,crouched)
    prone,crouch=branch(g,low,math(g,'Less_DoubleDouble',A=half(g),B=40))
    for q,speed,state in ((prone,60,'Prone'),(crouch,120,'Crouch')):
        q=put(g,q,'MaxWalkSpeedCrouched',speed,'/Script/Engine.CharacterMovementComponent',move(g));q=put(g,q,'LocomotionState',state)
        if state=='Prone':
            q=run(g,q,call(g,'PC_CheckProneClearance'));q=put(g,q,'ProneBlocked',math(g,'Not_PreBool',A=get(g,'ProneClear')))
            blocked,clear=branch(g,q,get(g,'ProneBlocked'))
            blocked=run(g,blocked,call(g,'/Script/Engine.MovementComponent.StopMovementImmediately',self=move(g)))
            blocked=run(g,blocked,call(g,'/Script/Engine.Pawn.ConsumeMovementInputVector'))
            for p in (blocked,clear):run(g,p,call(g,'PC_PlayPronePose'))
        else:run(g,q,call(g,'PC_PlayCrouchPose'))
    slow,fast=branch(g,high,get(g,'SlowHeld'))
    slow=put(g,slow,'MaxWalkSpeed',65,'/Script/Engine.CharacterMovementComponent',move(g));slow=put(g,slow,'LocomotionState','SlowWalk')
    run(g,slow,call(g,'PC_PlayStandingPose'))
    running,walking=branch(g,fast,get(g,'RunHeld'))
    for q,speed,state in ((running,300,'Run'),(walking,150,'Walk')):
        q=put(g,q,'MaxWalkSpeed',speed,'/Script/Engine.CharacterMovementComponent',move(g));q=put(g,q,'LocomotionState',state);run(g,q,call(g,'PC_PlayStandingPose'))
    for name,prefix,idle in [('PC_PlayCrouchPose','Rifle_Crouch_Walk','Rifle_CrouchLoop'),('PC_PlayPronePose','Rifle_Prone_Walk','Rifle_Prone')]:
        g=fn(name);f,_=branch(g,g.find_graph_entry_pin(),ready(g))
        speed=math(g,'VSizeXY',A=pure(g,'/Script/Engine.Actor.GetVelocity'))
        moving,idling=branch(g,f,math(g,'Greater_DoubleDouble',A=speed,B=5))
        choose_pose(g,idling,idle)
        forward=math(g,'Dot_VectorVector',A=pure(g,'/Script/Engine.Actor.GetVelocity'),B=pure(g,'/Script/Engine.Actor.GetActorForwardVector'))
        if name=='PC_PlayCrouchPose':
            side=math(g,'Dot_VectorVector',A=pure(g,'/Script/Engine.Actor.GetVelocity'),B=pure(g,'/Script/Engine.Actor.GetActorRightVector'))
            strafing,moving=branch(g,moving,math(g,'Greater_DoubleDouble',A=math(g,'Abs',A=side),B=math(g,'Abs',A=forward)))
            right,left=branch(g,strafing,math(g,'GreaterEqual_DoubleDouble',A=side,B=0))
            choose_pose(g,right,'Rifle_Crouch_WalkRt');choose_pose(g,left,'Rifle_Crouch_WalkLt')
        a,b=branch(g,moving,math(g,'GreaterEqual_DoubleDouble',A=forward,B=0))
        for q,suffix in ((a,'Fwd'),(b,'Bwd')):choose_pose(g,q,prefix+suffix)
    g=fn('PC_PlayStandingPose');f,_=branch(g,g.find_graph_entry_pin(),ready(g))
    falling,ground=branch(g,f,math(g,'EqualEqual_ByteByte',A=get(g,'MovementMode','/Script/Engine.CharacterMovementComponent',move(g)),B=3))
    falling=put(g,falling,'WasFalling',True);falling=put(g,falling,'LocomotionState','Jump')
    velocity=call(g,'/Script/Engine.KismetMathLibrary.BreakVector',InVec=pure(g,'/Script/Engine.Actor.GetVelocity'))
    up,down=branch(g,falling,math(g,'Greater_DoubleDouble',A=pin(velocity,'Z',True),B=0))
    choose_pose(g,up,'Rifle_Jump_Platformer_Start',False);choose_pose(g,down,'Rifle_Jump_Platformer_Fall',True)
    landed,steady=branch(g,ground,get(g,'WasFalling'))
    landed=put(g,landed,'WasFalling',False)
    landed=put(g,landed,'LandUntil',math(g,'Add_DoubleDouble',A=pure(g,'/Script/Engine.GameplayStatics.GetTimeSeconds'),B=.25))
    choose_pose(g,landed,'Rifle_Jump_Platformer_Land',False)
    finished,_=branch(g,steady,math(g,'GreaterEqual_DoubleDouble',A=pure(g,'/Script/Engine.GameplayStatics.GetTimeSeconds'),B=get(g,'LandUntil')))
    need,_=branch(g,finished,math(g,'NotEqual_ByteByte',A=get(g,'AnimationMode','/Script/Engine.SkeletalMeshComponent',mesh(g)),B=0))
    need=put(g,need,'ActivePose','None');run(g,need,call(g,'/Script/Engine.SkeletalMeshComponent.SetAnimationMode',self=mesh(g),InAnimationMode='AnimationBlueprint',bForceInitAnimScriptInstance=True))
    # No invented low-posture strafing; fixed prone yaw avoids rotating the long body through walls.
    g=fn('PC_ActionMoveForward');entry=g.find_graph_entry_pin();f=alive(g,entry)
    axis=pin(entry.get_owning_node(),'AxisValue',True)
    low,high=branch(g,f,math(g,'Less_DoubleDouble',A=half(g),B=40))
    low=put(g,low,'ProneProbeAxis',math(g,'FClamp',Value=axis,Min=-1,Max=1))
    low=run(g,low,call(g,'PC_CheckProneClearance'))
    low=put(g,low,'ProneBlocked',math(g,'Not_PreBool',A=get(g,'ProneClear')))
    clear,blocked=branch(g,low,get(g,'ProneClear'))
    run(g,clear,call(g,'PC_RequestMoveForward',AxisValue=axis))
    blocked=run(g,blocked,call(g,'/Script/Engine.MovementComponent.StopMovementImmediately',self=move(g)))
    run(g,blocked,call(g,'/Script/Engine.Pawn.ConsumeMovementInputVector'))
    high,_=branch(g,high,math(g,'NotEqual_IntInt',A=get(g,'DesiredPosture'),B=2))
    run(g,high,call(g,'PC_RequestMoveForward',AxisValue=axis))
    for name,request in [('PC_ActionMoveRight','PC_RequestMoveRight'),('PC_ActionLookYaw','PC_RequestLookYaw')]:
        g=fn(name);entry=g.find_graph_entry_pin();f=alive(g,entry)
        legal=math(g,'BooleanAND',A=math(g,'Greater_DoubleDouble',A=half(g),B=40),B=math(g,'NotEqual_IntInt',A=get(g,'DesiredPosture'),B=2))
        f,_=branch(g,f,legal);run(g,f,call(g,request,AxisValue=pin(entry.get_owning_node(),'AxisValue',True)))
    # Child input events override their inherited action binding, while inherited axes remain untouched.
    ev=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'EventGraph')
    for axis,request in [('PC_MoveForward','PC_ActionMoveForward'),('PC_MoveRight','PC_ActionMoveRight'),('PC_LookYaw','PC_ActionLookYaw')]:
        e=ev.create_node_from_name('Input|AxisEvents|'+axis,unreal.Vector2D(),[]);assert e
        run(ev,lib.find_then_pin(e),call(ev,request,AxisValue=pin(e,'AxisValue',True)))
    for action,press,release in [('PC_Run','PC_ActionRunOn','PC_ActionRunOff'),('PC_Slow','PC_ActionSlowOn','PC_ActionSlowOff'),
          ('PC_Jump','PC_ActionJump','PC_ActionJumpOff'),('PC_Crouch','PC_ActionCrouch',None),('PC_Prone','PC_ActionProne',None),
          ('PC_Fire','PC_ActionFire',None),('PC_Reload','PC_ActionReload',None)]:
        e=ev.create_node_from_name('Input|ActionEvents|'+action,unreal.Vector2D(),[]);assert e
        run(ev,pin(e,'Pressed',True),call(ev,press))
        if release:run(ev,pin(e,'Released',True),call(ev,release))
    e=lib.add_event_override(bp,'ReceiveTick',unreal.IntPoint());assert e
    run(ev,lib.find_then_pin(e),call(ev,'PC_ActionTick',DeltaSeconds=pin(e,'DeltaSeconds',True)))
    assert lib.compile_blueprint(bp)
    r['graph_errors']=[str(n) for graph in lib.list_graphs(bp) for n in unreal.BlueprintGraphEditor.get_graph_editor(graph).list_nodes_with_errors()]
    assert not r['graph_errors']
    assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
    p=STORE/('Content/'+DEST.removeprefix('/Game/')+'.uasset')
    r['packages'].append({'package':DEST,'path':p.relative_to(ROOT).as_posix(),'size_bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    r['status']='saved_unselected_actions_require_fresh_runtime_and_visual_review'
except Exception:r['status']='failed';r['errors'].append(traceback.format_exc())
finally:
    r['protected_43_unchanged']=guard();(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n');unreal.SystemLibrary.quit_editor()
