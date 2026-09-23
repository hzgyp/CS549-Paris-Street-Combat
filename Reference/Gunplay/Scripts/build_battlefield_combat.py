"""Damage, a stoppable MG emplacement and the shared player hit dispatch."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parent));from battlefield_common import *
if not A.does_asset_exist(path('BP_BattlePlayer01')):
    bp=create('BP_BattlePlayer01',A.load_blueprint_class('/Game/Normandy/Tests/BP_PlayerHandsReview'));g=graph(bp)
    for n,t,d in [('Health','real','100'),('LastDamageTime','real','-100'),('DamageTaken','real','0')]:
        unreal.log('BATTLE_PLAYER_FIELD '+n);member(g,bp,n,t,d)
    unreal.log('BATTLE_PLAYER_DAMAGE_EVENT')
    e=event(bp,'ReceiveAnyDamage');start,_=branch(g,op(e,'then'),pure(g,'math.Greater_DoubleDouble',A=get(g,'Health'),B=0))
    start=chain(start,setv(g,'Health',pure(g,'math.FClamp',Value=sub(g,get(g,'Health'),op(e,'Damage')),Min=0,Max=100)),setv(g,'LastDamageTime',now(g)),setv(g,'DamageTaken',add(g,get(g,'DamageTaken'),op(e,'Damage'))))
    dead,_=branch(g,start,pure(g,'math.LessEqual_DoubleDouble',A=get(g,'Health'),B=0))
    chain(dead,call(g,'/Script/Engine.CharacterMovementComponent.DisableMovement',self=get(g,'CharacterMovement')),setv(g,'bDisabled','true','/Game/Normandy/Blueprints/Player/BP_WeaponComponent.BP_WeaponComponent_C',get(g,'WeaponComponent')),log(g,'BATTLE_PLAYER_DOWN'))
    finish(bp)
if not A.does_asset_exist(path('BP_MGEmplacement01')):
    bp=create('BP_MGEmplacement01');root=assembly(bp)
    mat='/Game/Normandy/Materials/FirstKit/MI_ObstacleTimber';metal=path('M_DistantMetal');cube='/Engine/BasicShapes/Cube'
    # Broad supports are solid cover; only the firing assembly is damageable.
    for n,p,s in [('LeftCover',(0,-150,55),(2.4,1.1,1.1)),('RightCover',(0,150,55),(2.4,1.1,1.1)),('BaseCover',(30,0,35),(2.4,2.0,.7))]:part(bp,root,n,cube,mat,p,s,collision=True)
    c=part(bp,root,'Receiver',cube,metal,(-20,0,125),(.8,.75,.75),collision=True);c.component_tags=['DamageableTarget']
    c=part(bp,root,'Barrel','/Engine/BasicShapes/Cylinder',metal,(-100,0,128),(.09,.09,1.5),(90,0,0),True);c.component_tags=['DamageableTarget']
    part(bp,root,'MuzzleFlash', '/Engine/BasicShapes/Sphere',path('M_Flash'),(-180,0,128),(.22,.18,.18))
    g=graph(bp)
    for n,t,d in [('GunHealth','real','105'),('NextShot','real','2'),('LastShot','real','-100'),('BurstCount','int','0'),('ShotsFired','int','0')]:member(g,bp,n,t,d)
    member(g,bp,'ShotAim',L.get_struct_type(unreal.load_object(None,'/Script/CoreUObject.Vector')),'(X=0,Y=0,Z=0)')
    f=function(bp,'FireEmplacementRound');compile_save(bp)
    f=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'FireEmplacementRound')
    player=pure(f,'game.GetPlayerCharacter',PlayerIndex=0);start,_=branch(f,f.find_graph_entry_pin(),valid(f,player))
    muzzle=plus(f,loc(f),'(X=-180,Y=0,Z=128)')
    aim=plus(f,pure(f,'/Script/Engine.Actor.K2_GetActorLocation',self=player),v(f,pure(f,'math.RandomFloatInRange',Min=-140,Max=140),pure(f,'math.RandomFloatInRange',Min=-190,Max=190),pure(f,'math.RandomFloatInRange',Min=-55,Max=65)))
    # Store once: random aim must not be reevaluated independently by the
    # trace, tracer, impact and damage branches.
    start=chain(start,setv(f,'ShotAim',aim));aim=get(f,'ShotAim')
    trace=call(f,'system.LineTraceSingle',Start=muzzle,End=aim,TraceChannel='TraceTypeQuery3',bTraceComplex='false',DrawDebugType='None',bIgnoreSelf='true')
    start=chain(start,trace,setv(f,'LastShot',now(f)),setv(f,'ShotsFired',pure(f,'math.Add_IntInt',A=get(f,'ShotsFired'),B=1)),sound(f,'S_MGBurstShot',muzzle,.65))
    info=call(f,'game.BreakHitResult',Hit=op(trace,'OutHit'));end=pure(f,'math.SelectVector',A=op(info,'ImpactPoint'),B=aim,bPickA=op(trace))
    center=pure(f,'math.VLerp',A=muzzle,B=end,Alpha=.5);length=pure(f,'math.Divide_DoubleDouble',A=pure(f,'math.Vector_Distance',V1=muzzle,V2=end),B=100)
    a,b=spawn(f,'BP_BattleTracer01',center,pure(f,'math.FindLookAtRotation',Start=muzzle,Target=end),v(f,length,.015,.015));link(start,ip(a,'execute'))
    hit,_=branch(f,op(b,'then'),op(trace));a,b=spawn(f,'BP_BattleImpact01',op(info,'ImpactPoint'),scale='(X=.06,Y=.06,Z=.06)');link(hit,ip(a,'execute'))
    chain(op(b,'then'),sound(f,'S_DirtImpact',op(info,'ImpactPoint'),.35),call(f,'game.ApplyPointDamage',DamagedActor=op(info,'HitActor'),BaseDamage=6,HitFromDirection=pure(f,'math.Normal',A=diff(f,end,muzzle)),HitInfo=op(trace,'OutHit')))
    compile_save(bp)
    g=graph(bp);e=event(bp,'ReceiveTick');start=chain(op(e,'then'),call(g,'/Script/Engine.SceneComponent.SetVisibility',self=get(g,'MuzzleFlash'),bNewVisibility=both(g,pure(g,'math.Greater_DoubleDouble',A=get(g,'GunHealth'),B=0),lt(g,sub(g,now(g),get(g,'LastShot')),.075)),bPropagateToChildren='false'))
    alive,_=branch(g,start,both(g,pure(g,'math.Greater_DoubleDouble',A=get(g,'GunHealth'),B=0),ge(g,now(g),get(g,'NextShot'))))
    mission=call(g,'game.GetActorOfClass',ActorClass=MC);start=chain(alive,mission)
    start,_=branch(g,start,valid(g,op(mission)))
    active,_=branch(g,start,both(g,pure(g,'math.GreaterEqual_IntInt',A=get(g,'Phase',MC,op(mission)),B=1),pure(g,'math.Less_IntInt',A=get(g,'Phase',MC,op(mission)),B=5)))
    start=chain(active,own(g,bp,'FireEmplacementRound'),setv(g,'BurstCount',pure(g,'math.Add_IntInt',A=get(g,'BurstCount'),B=1)),setv(g,'NextShot',add(g,now(g),.13)))
    pause,_=branch(g,start,pure(g,'math.GreaterEqual_IntInt',A=get(g,'BurstCount'),B=6))
    chain(pause,setv(g,'BurstCount',0),setv(g,'NextShot',add(g,now(g),2.5)))
    e=event(bp,'ReceiveAnyDamage');alive,_=branch(g,op(e,'then'),pure(g,'math.Greater_DoubleDouble',A=get(g,'GunHealth'),B=0))
    start=chain(alive,setv(g,'GunHealth',pure(g,'math.FClamp',Value=sub(g,get(g,'GunHealth'),op(e,'Damage')),Min=0,Max=105)))
    dead,_=branch(g,start,pure(g,'math.LessEqual_DoubleDouble',A=get(g,'GunHealth'),B=0))
    a,b=spawn(g,'BP_BattleImpact01',plus(g,loc(g),'(X=0,Y=0,Z=110)'),scale='(X=.6,Y=.6,Z=.6)');link(dead,ip(a,'execute'))
    chain(op(b,'then'),call(g,'/Script/Engine.SceneComponent.SetVisibility',self=get(g,'Barrel'),bNewVisibility='false',bPropagateToChildren='false'),log(g,'BATTLE_MG_DISABLED'))
    finish(bp)
    default=unreal.get_default_object(bp.generated_class());default.tags=['Enemy','BattlefieldPrototype']
    for n,vv in [('GunHealth',105.),('NextShot',2.),('LastShot',-100.)]:default.set_editor_property(n,vv)
    kit.save(bp)
# Add one guarded dispatch to the existing weapon impact function. No rewrite.
bp=A.load_asset('/Game/Normandy/Blueprints/Player/BP_NormandyPlayerCharacter');g=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'ResolveImpact')
if not any(str(L.get_node_title(n)).replace(' ','')=='ApplyPointDamage' for n in g.list_all_nodes()):
    hit=op(g.find_graph_entry_pin().get_owning_node(),'Hit');info=call(g,'game.BreakHitResult',Hit=hit)
    # Insert before the existing impact response so all branches retain it.
    # Append to the solid-hit PrintString node: water continues to the original
    # ripple path; solid impacts retain their decal and status.
    tails=[n for n in g.list_all_nodes() if str(L.get_node_title(n))=='PrintString']
    end=next(n for n in tails if 'SOLID' in ip(n,'InString').get_pin_value())
    yes,_=branch(g,op(end,'then'),valid(g,op(info,'HitComponent')))
    yes,_=branch(g,yes,pure(g,'/Script/Engine.ActorComponent.ComponentHasTag',self=op(info,'HitComponent'),Tag='DamageableTarget'))
    chain(yes,call(g,'game.ApplyPointDamage',DamagedActor=op(info,'HitActor'),BaseDamage=35,HitFromDirection=pure(g,'math.Normal',A=diff(g,op(info,'TraceEnd'),op(info,'TraceStart'))),HitInfo=hit,EventInstigator=pure(g,'game.GetPlayerController',PlayerIndex=0)))
    compile_save(bp)
unreal.log('BATTLEFIELD_COMBAT_READY')
