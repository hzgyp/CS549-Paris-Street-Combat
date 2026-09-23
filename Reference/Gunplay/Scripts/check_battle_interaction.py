"""Short editor-only check: real rifle traces disable a live emplacement."""
from pathlib import Path
import unreal,json,time
R=Path(__file__).resolve().parents[2];O=R/'Development/Evidence/G1/2026-09-21_battlefield';O.mkdir(parents=True,exist_ok=True)
world=unreal.EditorLevelLibrary.get_game_world();assert world
actors=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Actor)
gun=next(a for a in actors if a.get_class().get_name()=='BP_MGEmplacement01_C');director=next(a for a in actors if a.get_class().get_name()=='BP_BattleDirector01_C')
player=unreal.GameplayStatics.get_player_character(world,0);pc=unreal.GameplayStatics.get_player_controller(world,0);cam=unreal.GameplayStatics.get_player_camera_manager(world,0)
report={'time_before':unreal.GameplayStatics.get_time_seconds(world),'shots_before':gun.get_editor_property('ShotsFired'),'shells_before':director.get_editor_property('ShellCount'),'air_sent':director.get_editor_property('AirSent'),'health_before':player.get_editor_property('Health'),'gun_health_before':gun.get_editor_property('GunHealth'),'npc_damage':[{'actor':a.get_name(),'damage':a.get_editor_property('DamageReceived')} for a in actors if a.get_class().get_name()=='BP_BattleCrowd01_C' and a.get_editor_property('DamageReceived')>0],'test':'Temporary PIE-only reposition and camera aim; calls existing Shoot, not direct damage.'}
gun.set_actor_tick_enabled(False)
p=gun.get_actor_location();player.set_actor_location(unreal.Vector(p.x+350,p.y-450,p.z+180),False,True)
step={'n':0,'next':time.monotonic()+.5,'handle':None}
def advance(delta):
    if time.monotonic()<step['next']:return
    try:
        target=gun.get_actor_location()+unreal.Vector(-20,0,125)
        pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(cam.get_camera_location(),target))
        if 1<=step['n']<=3:player.call_method('Shoot')
        if step['n']==4:gun.set_actor_tick_enabled(True)
        if step['n']>=5:
            report.update({'gun_health_after':gun.get_editor_property('GunHealth'),'health_after':player.get_editor_property('Health'),'mag_after':player.get_editor_property('WeaponComponent').get_editor_property('MagAmmo')})
            (O/'interaction.json').write_text(json.dumps(report,indent=2));unreal.unregister_slate_post_tick_callback(step['handle']);unreal.log('BATTLE_INTERACTION_CHECK '+json.dumps(report));return
        step['n']+=1;step['next']=time.monotonic()+.45
    except Exception as e:
        report['error']=str(e);(O/'interaction.json').write_text(json.dumps(report,indent=2));unreal.unregister_slate_post_tick_callback(step['handle']);raise
step['handle']=unreal.register_slate_post_tick_callback(advance)
