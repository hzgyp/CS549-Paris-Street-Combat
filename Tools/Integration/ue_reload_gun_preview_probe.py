"""Read-only discovery in the already-open reload Animation Editor.

Review plan: RELOAD_GUN_PREVIEW_REVIEW_20261004.md. No asset edits/save,
no new engine or PIE. Inspect only native preview metadata/component handles.
"""
import json
import unreal

animation = unreal.load_asset('/Game/Rifle_01/Animation/In-Place/W2_Stand_Aim_Reload_IP')
skeleton = animation.get_editor_property('skeleton')
report = {'animation': animation.get_path_name(), 'skeleton': skeleton.get_path_name(),
          'preview_structs': [name for name in dir(unreal) if 'PreviewAttach' in name or 'PreviewAssetAttach' in name],
          'components': []}
try:
    container = skeleton.get_editor_property('preview_attached_asset_container')
    report['container_type'] = type(container).__name__
    report['container_fields'] = [name for name in dir(container) if not name.startswith('_')]
except Exception as error:
    report['container_error'] = str(error)
for component in unreal.ObjectIterator(unreal.SkeletalMeshComponent):
    mesh = component.get_editor_property('skeletal_mesh_asset')
    if mesh and mesh.get_path_name().startswith('/Game/Rifle_01/Character/Mesh/SK_Mannequin.'):
        report['components'].append({'path': component.get_path_name(), 'class': component.get_class().get_name(),
                                     'outer': component.get_outer().get_path_name(),
                                     'registration_api': [name for name in dir(component) if 'register' in name]})
report['transient_component_api'] = {
    'gather': unreal.SubobjectDataSubsystem.k2_gather_subobject_data_for_instance.__doc__,
    'add': unreal.SubobjectDataSubsystem.add_new_subobject.__doc__,
    'params': unreal.AddNewSubobjectParams.__doc__,
    'object': unreal.SubobjectDataBlueprintFunctionLibrary.get_object.__doc__,
    'attach': unreal.SceneComponent.attach_to_component.__doc__,
}
unreal.log('CS549_RELOAD_GUN_PREVIEW_PROBE ' + json.dumps(report))
