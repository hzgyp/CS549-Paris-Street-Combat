"""One transient rifle component in the user's existing source preview only.

See RELOAD_GUN_PREVIEW_REVIEW_20261004.md. No assets/map/sockets/poses saved or
modified. Native socket attachment updates the rifle; no Python tick.
"""
import builtins
import json
import unreal

assert not hasattr(builtins, 'cs549_reload_preview_gun'), 'Preview already exists; do not duplicate'
matches = []
for item in unreal.ObjectIterator(unreal.SkeletalMeshComponent):
    mesh = item.get_editor_property('skeletal_mesh_asset')
    if mesh and mesh.get_path_name() == '/Game/Rifle_01/Character/Mesh/SK_Mannequin.SK_Mannequin':
        if item.get_path_name().startswith('/Engine/Transient.') and item.get_class().get_name() == 'DebugSkelMeshComponent':
            matches.append(item)
assert len(matches) == 1, 'Source preview component must be unique'
parent = matches[0]
actor = parent.get_owner()
assert actor.get_path_name().startswith('/Engine/Transient.')
assert actor.get_class().get_name() == 'AnimationEditorPreviewActor'
assert parent.does_socket_exist('hand_rSocket_Aim')
rifle = unreal.load_asset('/Game/USParatrooper/Meshes/Weapon/Sm_M1_Garand')
assert isinstance(rifle, unreal.StaticMesh)
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
library = unreal.SubobjectDataBlueprintFunctionLibrary
handles = subsystem.k2_gather_subobject_data_for_instance(actor)
actor_handles = [handle for handle in handles if library.get_object(library.get_data(handle)) == actor]
assert len(actor_handles) == 1
handle, reason = subsystem.add_new_subobject(unreal.AddNewSubobjectParams(
    parent_handle=actor_handles[0], new_class=unreal.StaticMeshComponent,
    blueprint_context=None, skip_mark_blueprint_modified=True))
gun = library.get_object(library.get_data(handle))
assert isinstance(gun, unreal.StaticMeshComponent), str(reason)
builtins.cs549_reload_preview_gun = (gun, handle, actor_handles[0])
assert gun.get_path_name().startswith(actor.get_path_name())
gun.set_mobility(unreal.ComponentMobility.MOVABLE)
gun.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
assert gun.set_static_mesh(rifle)
assert gun.attach_to_component(parent, 'hand_rSocket_Aim',
    unreal.AttachmentRule.SNAP_TO_TARGET, unreal.AttachmentRule.SNAP_TO_TARGET,
    unreal.AttachmentRule.KEEP_WORLD, False)
gun.set_visibility(True, True)
unreal.log('CS549_RELOAD_GUN_PREVIEW_ATTACHED ' + json.dumps({
    'parent': parent.get_path_name(), 'gun': gun.get_path_name(),
    'asset': rifle.get_path_name(), 'socket': 'hand_rSocket_Aim',
    'world_location': str(gun.get_world_location()),
    'relative_transform': str(gun.get_relative_transform()), 'saved': False}))
