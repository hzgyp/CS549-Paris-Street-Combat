"""Run inside the isolated UE lab through PythonScript commandlet."""
import json
import os
import traceback
from pathlib import Path
from datetime import datetime
import unreal

LAB = Path(unreal.Paths.project_dir()).resolve()
OUT = LAB / 'Evidence'
repair_mode = os.environ.get('CS549_REPAIR_INVENTORY') == '1'
if repair_mode:
    OUT = LAB / 'Evidence/Repair20261001/FinalInventory'
OUT.mkdir(parents=True, exist_ok=True)
REPORT = {'engine': unreal.SystemLibrary.get_engine_version(),
          'started_at': datetime.now().astimezone().isoformat(),
          'project': str(LAB), 'mode': 'real UE load, no main-project changes',
          'assets': [], 'errors': []}


def save_report():
    (OUT / 'ue_load_inventory.json').write_text(json.dumps(REPORT, indent=2), encoding='utf-8')


def pathof(obj):
    return obj.get_path_name() if obj else None


registry = unreal.AssetRegistryHelpers.get_asset_registry()
registry.search_all_assets(True)
registry.scan_paths_synchronous(['/Game'], True)
records = sorted(registry.get_assets_by_path('/Game', recursive=True),
                 key=lambda a: (str(a.asset_class_path.asset_name) == 'World', str(a.package_name)))
if repair_mode:
    records = [data for data in records if not str(data.package_name).startswith('/Game/ParisCombat/Tests/')]
REPORT['registry_asset_count'] = len(records)
REPORT['api_probe'] = {name: [v for v in dir(getattr(unreal, name)) if any(
    word in v for word in ('bone', 'pose', 'export', 'lod', 'texture', 'retarget'))]
    for name in ('SkeletalMeshEditorSubsystem', 'AnimationLibrary', 'AnimPoseExtensions',
                 'SkeletalMeshComponent', 'FbxExportOption', 'MaterialEditingLibrary') if hasattr(unreal, name)}
skeletal_editor = unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem)
for index, data in enumerate(records):
    item = {'path': str(data.package_name), 'registry_class': str(data.asset_class_path.asset_name)}
    try:
        asset = data.get_asset()
        if not asset:
            raise RuntimeError('UE returned no loaded asset')
        item['loaded'] = True
        item['class'] = asset.get_class().get_name()
        if isinstance(asset, unreal.SkeletalMesh):
            item['skeleton'] = pathof(asset.get_editor_property('skeleton'))
            item['physics_asset'] = pathof(asset.get_editor_property('physics_asset'))
            item['lod_count'] = skeletal_editor.get_lod_count(asset)
            item['lod_vertices'] = [skeletal_editor.get_num_verts(asset, n) for n in range(item['lod_count'])]
            item['materials'] = [{'slot': str(m.material_slot_name), 'material': pathof(m.material_interface)}
                                 for m in asset.get_editor_property('materials')]
            component = unreal.new_object(unreal.SkeletalMeshComponent)
            component.set_skeletal_mesh_asset(asset)
            names = [component.get_bone_name(n) for n in range(component.get_num_bones())]
            item['bones'] = []
            for bone_index, name in enumerate(names):
                transform = component.get_ref_pose_transform(bone_index)
                translation = transform.translation
                item['bones'].append({'name': str(name),
                    'parent': str(skeletal_editor.get_bone_parent(asset, name)),
                    'ref_local_translation_cm': [translation.x, translation.y, translation.z],
                    'ref_local_rotation_xyzw': [transform.rotation.x, transform.rotation.y,
                                               transform.rotation.z, transform.rotation.w]})
            item['bone_count'] = len(names)
            item['morph_targets'] = [pathof(m) for m in asset.get_editor_property('morph_targets')]
        elif isinstance(asset, unreal.AnimSequence):
            item['skeleton'] = pathof(asset.get_editor_property('skeleton'))
            item['sequence_length'] = unreal.AnimationLibrary.get_sequence_length(asset)
            item['frames'] = unreal.AnimationLibrary.get_num_frames(asset)
            item['tracks'] = [str(n) for n in unreal.AnimationLibrary.get_animation_track_names(asset)]
            item['root_motion'] = asset.get_editor_property('enable_root_motion')
        elif isinstance(asset, unreal.Texture2D):
            item['width'] = asset.blueprint_get_size_x()
            item['height'] = asset.blueprint_get_size_y()
            item['registry_dimensions'] = str(data.get_tag_value('Dimensions'))
            item['dimension_limit'] = 'GetSize may expose a compile/streaming placeholder; compare registry source dimensions and completed renders.'
            item['srgb'] = asset.get_editor_property('srgb')
            item['compression'] = str(asset.get_editor_property('compression_settings'))
        elif isinstance(asset, unreal.MaterialInterface):
            item['textures'] = [pathof(t) for t in unreal.MaterialEditingLibrary.get_material_used_textures(asset)]
            if isinstance(asset, unreal.MaterialInstanceConstant):
                item['parent'] = pathof(asset.get_editor_property('parent'))
            item['texture_parameters'] = [str(n) for n in unreal.MaterialEditingLibrary.get_texture_parameter_names(asset)]
        elif isinstance(asset, unreal.StaticMesh):
            item['materials'] = [pathof(m.material_interface) for m in asset.get_editor_property('static_materials')]
    except Exception as exc:
        item['error'] = str(exc)
        REPORT['errors'].append({'path': item['path'], 'traceback': traceback.format_exc()})
    REPORT['assets'].append(item)
    if index % 20 == 0:
        unreal.log(f'CS549_LAB_PROGRESS {index + 1}/{len(records)} {item["path"]}')
        save_report()
save_report()
REPORT['finished_at'] = datetime.now().astimezone().isoformat()
REPORT['loaded_count'] = sum(bool(a.get('loaded')) for a in REPORT['assets'])
save_report()
unreal.log('CS549_LAB_INVENTORY_DONE ' + str(REPORT['loaded_count']))
