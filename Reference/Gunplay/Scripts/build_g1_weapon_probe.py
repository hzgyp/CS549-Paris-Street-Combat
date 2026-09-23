"""Add a disposable weapon integration driver only to the generated route probe map."""
from pathlib import Path
import sys
import unreal
sys.path.insert(0,str(Path(__file__).parent))
from g1_graph import *
from build_g1_landing_flow import build_hud
build_hud()
PATH='/Game/Normandy/Tests/BP_G1WeaponProbe'
MC='/Game/Normandy/Blueprints/Core/BP_MissionController.BP_MissionController_C'
PC='/Game/Normandy/Blueprints/Player/BP_NormandyPlayerCharacter.BP_NormandyPlayerCharacter_C'
WC='/Game/Normandy/Blueprints/Player/BP_WeaponComponent.BP_WeaponComponent_C'
bp=A.load_asset(PATH) if A.does_asset_exist(PATH) else L.create_blueprint_asset_with_parent(PATH,unreal.Actor.static_class())
g=function(bp,'DataSetup')
for n,t,d in [('TestState','int','0'),('ShotCount','int','0'),('Clock','real','0')]:member(g,bp,n,t,d)
L.remove_function_graph(bp,'DataSetup');compile_save(bp)
g=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'EventGraph');g.remove_nodes(g.list_all_nodes())
event=L.add_event_override(bp,'ReceiveTick',unreal.IntPoint(0,0))
find=call(g,'game.GetActorOfClass',ActorClass=MC);start=chain(op(event,'then'),find);mission=op(find)
start,_=branch(g,start,pure(g,'system.IsValid',Object=mission))
start,_=branch(g,start,pure(g,'math.GreaterEqual_IntInt',A=get(g,'Phase',MC,mission),B=3))
player=get(g,'PlayerRef',MC,mission);weapon=get(g,'WeaponComponent',PC,player)
start=chain(start,setv(g,'Clock',pure(g,'math.Add_DoubleDouble',A=get(g,'Clock'),B=op(event,'DeltaSeconds'))))
shoot,wait=branch(g,start,eq(g,get(g,'TestState'),0))
shoot,_=branch(g,shoot,pure(g,'math.GreaterEqual_DoubleDouble',A=get(g,'Clock'),B=.4))
controller=pure(g,'game.GetPlayerController',PlayerIndex=0)
shot=call(g,PC+'.Shoot',self=player)
second=call(g,PC+'.Shoot',self=player)
shoot=chain(shoot,setv(g,'Clock',0),call(g,'/Script/Engine.Controller.SetControlRotation',self=controller,NewRotation=pure(g,'math.MakeRotator',Pitch=-10,Yaw=0,Roll=0)),shot,second,setv(g,'ShotCount',pure(g,'math.Add_IntInt',A=get(g,'ShotCount'),B=1)))
reload,_=branch(g,shoot,eq(g,get(g,'ShotCount'),8))
start=chain(reload,call(g,PC+'.StartReload',self=player),setv(g,'TestState',1),setv(g,'Clock',0))
old=call(g,WC+'.CommitReload',self=weapon,ExpectedActionId=0);start=chain(start,old)
old_ok,old_fail=branch(g,start,invert(g,op(old,'Committed')))
chain(old_ok,log(g,'G1_WEAPON_PROBE stale reload callback rejected'))
chain(old_fail,log(g,'G1_WEAPON_PROBE FAIL stale callback accepted'))
ready,_=branch(g,wait,both(g,eq(g,get(g,'TestState'),1),pure(g,'math.Greater_DoubleDouble',A=get(g,'Clock'),B=2.8)))
condition=both(g,eq(g,get(g,'MagAmmo',WC,weapon),8),eq(g,get(g,'ReserveAmmo',WC,weapon),16))
condition=both(g,condition,both(g,eq(g,get(g,'ShotId',WC,weapon),8),invert(g,get(g,'bReloading',WC,weapon))))
ready=chain(ready,setv(g,'TestState',2))
yes,no=branch(g,ready,condition)
chain(yes,log(g,'G1_WEAPON_PROBE PASS: 8 shots; duplicate/cooldown requests rejected; reload 8/16; action released'),call(g,'system.ExecuteConsoleCommand',Command='HighResShot 1'),call(g,'/Script/Engine.Actor.SetActorTickEnabled',bEnabled='false'))
chain(no,log(g,'G1_WEAPON_PROBE FAIL: ammo/shot/reload state mismatch'),call(g,'/Script/Engine.Actor.SetActorTickEnabled',bEnabled='false'))
tidy(g);compile_save(bp)
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert level.load_level('/Game/Normandy/Tests/L_G1_RouteProbe')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in actors.get_all_level_actors():
    if a.get_actor_label()=='Development_WeaponProbe':actors.destroy_actor(a)
a=actors.spawn_actor_from_class(bp.generated_class(),unreal.Vector(0,0,1200));a.set_actor_label('Development_WeaponProbe')
assert level.save_current_level()
unreal.log('G1_WEAPON_PROBE saved; production map contains no test driver')
