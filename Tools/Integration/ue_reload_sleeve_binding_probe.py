"""Transient same-phase full soldier/owner-arm comparison; no asset save."""
import builtins
import json
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/ReloadSleeveAdaptationV2/binding_probe_v2'
assert not OUT.exists()
OUT.mkdir(parents=True)
(OUT / 'source.py').write_bytes(Path(__file__).read_bytes())
matches = [c for c in unreal.ObjectIterator(unreal.SkeletalMeshComponent)
           if '/Engine/Transient.' in c.get_path_name()
           and c.get_editor_property('skeletal_mesh_asset')
           and c.get_editor_property('skeletal_mesh_asset').get_path_name().startswith(
               '/Game/ParisCombat/Characters/Adaptation/Meshes/SK_WWII_US_Paratrooper_simple_UE582_v1.')]
assert len(matches) == 1, [c.get_path_name() for c in matches]
parent = matches[0]
parent.set_play_rate(0)
parent.set_position(2.2, False)
actor = parent.get_owner()
assert actor.get_class().get_name() == 'AnimationEditorPreviewActor'
sub = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lib = unreal.SubobjectDataBlueprintFunctionLibrary
handles = sub.k2_gather_subobject_data_for_instance(actor)
ah = next(h for h in handles if lib.get_object(lib.get_data(h)) == actor)
handle, reason = sub.add_new_subobject(unreal.AddNewSubobjectParams(
    parent_handle=ah, new_class=unreal.SkeletalMeshComponent,
    blueprint_context=None, skip_mark_blueprint_modified=True))
owner = lib.get_object(lib.get_data(handle))
assert owner, str(reason)
owner.set_skeletal_mesh_asset(unreal.load_asset(
    '/Game/ParisCombat/Characters/FirstPersonContinuousArmsV3/SK_PC_ContinuousArmsV3'))
owner.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
owner.attach_to_component(parent, 'None', unreal.AttachmentRule.SNAP_TO_TARGET,
                          unreal.AttachmentRule.SNAP_TO_TARGET, unreal.AttachmentRule.SNAP_TO_TARGET, False)
# Diagnostic separation of two otherwise overlapping skins, NOT a gameplay fit.
owner.set_relative_location(unreal.Vector(70, 0, 0), False, False)
owner.set_leader_pose_component(parent, True, False)
owner.set_visibility(True, True)
builtins.cs549_sleeve_binding_probe = (parent, owner, handle, ah)
report = {'phase_s': 2.2, 'parent': parent.get_path_name(), 'owner': owner.get_path_name(),
          'world': actor.get_world().get_path_name(), 'native_assets_saved': False,
          'app_has_geometry_script': hasattr(unreal, 'GeometryScript_AssetUtils'),
          'geometry_apis': [n for n in dir(unreal) if 'GeometryScript' in n and any(s in n for s in ('Bone', 'Query', 'Asset'))]}
(OUT / 'result.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
unreal.log('CS549_SLEEVE_BINDING_PROBE_READY ' + json.dumps(report))
