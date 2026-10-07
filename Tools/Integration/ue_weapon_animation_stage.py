"""Transient actual-city candidate replacement; no map save or runtime callbacks."""
import os
import unreal
from weapon_animation_reuse_common import ROOT, STORE, PLAYER, OWNER, guard, read, sha


def candidate_records(include_owner=True):
    rows=read(STORE/'Evidence/WeaponAnimationReuseV1/retarget_v1/result.json')['packages']
    rows+=read(STORE/'Evidence/WeaponAnimationReuseV1/author_reload_v1/result.json')['packages']
    if include_owner:
        report=read(STORE/'Evidence/WeaponAnimationReuseV1/author_owner_v2/result.json')
        assert not report['errors'] and report['status'].startswith('saved_unselected')
        rows+=report['packages']
    for r in rows:
        p=ROOT/r['path'];assert sha(p)==r['sha256'] and p.stat().st_size==r['size_bytes'],r['path']
    return rows


def stage_candidate(include_owner=True):
    guard();records=candidate_records(include_owner)
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    old=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='PC_City_Player')
    gun=old.get_editor_property('WeaponAppearance')
    player=actors.spawn_actor_from_class(unreal.EditorAssetLibrary.load_blueprint_class(PLAYER),old.get_actor_location(),old.get_actor_rotation());assert player
    player.set_actor_label('PC_City_Player_AnimationTrial')
    player.set_editor_property('WeaponAppearance',gun)
    player.set_editor_property('auto_possess_player',unreal.AutoReceiveInput.PLAYER0)
    gun.set_editor_property('Combatant',player);gun.set_editor_property('GripMesh',player.mesh);gun.set_owner(player)
    assert gun.attach_to_component(player.mesh,'hand_r',unreal.AttachmentRule.KEEP_RELATIVE,unreal.AttachmentRule.KEEP_RELATIVE,unreal.AttachmentRule.KEEP_RELATIVE,False)
    previous=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='PC_Player_ContinuousArmsNativeV1')
    actors.destroy_actor(previous)
    path=OWNER if include_owner else '/Game/ParisCombat/Blueprints/PlayerActionsV1/BP_PCActionOwnerViewV1'
    view=actors.spawn_actor_from_class(unreal.EditorAssetLibrary.load_blueprint_class(path),player.get_actor_location(),unreal.Rotator());assert view
    view.set_actor_label('PC_AnimationOwnerViewTrial');view.set_editor_property('Combatant',player)
    actors.destroy_actor(old)
    return {'player_package':PLAYER,'owner_package':path,'files':records,'map_saved':False},player,view
