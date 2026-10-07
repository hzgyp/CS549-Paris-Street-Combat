"""Hash-guarded editor-only staging of the action player and owner view. Never saves."""
import hashlib,json,os
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[2]
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
EVIDENCE=STORE/'Evidence/PlayerActionsV1'
def action_records():
    reports=[json.loads((EVIDENCE/os.environ.get('CS549_ACTION_SOURCE','author_v7')/'result.json').read_text()),
             json.loads((EVIDENCE/os.environ.get('CS549_ACTION_OWNER_SOURCE','owner_author_v2')/'result.json').read_text())]
    assert all(not r['errors'] and r['status'].startswith('saved_unselected') for r in reports)
    files=reports[0]['packages']+reports[1]['packages']+reports[0].get('source_guards',[])
    assert all(hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256'] for f in files)
    return files
def stage_actions_actor():
    files=action_records();player_package,view_package=(files[i]['package'] for i in (0,1))
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    old=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='PC_City_Player')
    gun=old.get_editor_property('WeaponAppearance')
    player=actors.spawn_actor_from_class(unreal.EditorAssetLibrary.load_blueprint_class(player_package),old.get_actor_location(),old.get_actor_rotation());assert player
    player.set_actor_label('PC_City_Player_ActionTrial');player.set_editor_property('WeaponAppearance',gun)
    player.set_editor_property('auto_possess_player',unreal.AutoReceiveInput.PLAYER0)
    gun.set_editor_property('Combatant',player);gun.set_editor_property('GripMesh',player.mesh);gun.set_owner(player)
    assert gun.attach_to_component(player.mesh,'hand_r',unreal.AttachmentRule.KEEP_RELATIVE,unreal.AttachmentRule.KEEP_RELATIVE,unreal.AttachmentRule.KEEP_RELATIVE,False)
    previous=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='PC_Player_ContinuousArmsNativeV1')
    actors.destroy_actor(previous)
    display=actors.spawn_actor_from_class(unreal.EditorAssetLibrary.load_blueprint_class(view_package),player.get_actor_location(),unreal.Rotator());assert display
    display.set_actor_label('PC_ActionOwnerViewTrial');display.set_editor_property('Combatant',player);actors.destroy_actor(old)
    return {'player_package':player_package,'view_package':view_package,'files':files,'map_saved':False},player,display
