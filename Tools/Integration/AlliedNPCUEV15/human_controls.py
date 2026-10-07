"""Explicit user console commands only; no ticks, animation writes or ammo edits."""
import unreal

def current():
    world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    assert world,'PIE is not running'
    actor=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Character)
               if a.get_actor_label()=='PC_City_Ally1')
    return actor

def status():
    a=current()
    s={n:str(a.get_editor_property(n)) for n in ('ActionState','LoadedAmmo','ReserveAmmo','ShotOutcome')}
    unreal.log('ALLIED HUMAN '+str(s));return s

def reload():
    current().call_method('PC_RequestReload')
    return status()

def fire():
    a=current()
    a.call_method('PC_RequestFire',args=(a.get_actor_location()+unreal.Vector(0,0,40),a.get_actor_forward_vector()))
    return status()
