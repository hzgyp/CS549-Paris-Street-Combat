"""Import accepted GLB in a new UE-only rigid frame; never save source or map."""
import json
import os
import sys
import traceback
from pathlib import Path
import unreal

sys.path.insert(0, str(Path(__file__).parent))
from german_rifle_ue_common import ROOT, STORE, BASE, GLB, GUARDS, guard, read, sha, new_output

OUT = new_output(os.environ['CS549_GERMAN_UE_IDENTITY'])
(OUT / 'source.py').write_bytes(Path(__file__).read_bytes())
DEST = BASE + '/ImportV1'
MESH = DEST + '/SM_PC_GermanRifleV15'
r = {'status': 'starting', 'errors': [], 'engine': unreal.SystemLibrary.get_engine_version(),
     'source_glb_sha256': sha(GLB), 'native_namespace': DEST, 'map_saved': False}


def vector(v):
    return [v.x, v.y, v.z]


try:
    r['guard_count'] = guard()
    assert not hasattr(unreal, 'ParisBlueprintAuthoring')
    assert not unreal.EditorAssetLibrary.does_directory_exist(DEST), 'Preserve occupied native import identity'
    blueprint = unreal.load_asset('/Interchange/Pipelines/DefaultGLTFAssetsPipeline')
    assert blueprint
    pipeline = unreal.AssetToolsHelpers.get_asset_tools().duplicate_asset('P_PC_GermanGLTFImportV1', DEST, blueprint)
    assert pipeline
    # Engine-default glTF response retained; only explicit static import/frame options changed.
    mesh_pipeline = pipeline.get_editor_property('mesh_pipeline')
    mesh_pipeline.set_editor_property('combine_static_meshes_behavior', unreal.InterchangeCombineStaticMeshesBehavior.ALL)
    mesh_pipeline.set_editor_property('build_nanite', False)
    mesh_pipeline.set_editor_property('collision', False)
    mesh_pipeline.set_editor_property('import_skeletal_meshes', False)
    common = pipeline.get_editor_property('common_meshes_properties')
    common.set_editor_property('bake_meshes', True)
    common.set_editor_property('recompute_normals', False)
    common.set_editor_property('recompute_tangents', False)
    config = read(GUARDS)
    pipeline.set_editor_property('asset_name', 'SM_PC_GermanRifleV15')
    pipeline.set_editor_property('use_source_name_for_asset', False)
    pipeline.set_editor_property('asset_type_sub_folders', True)
    pipeline.set_editor_property('import_offset_rotation', unreal.Rotator(yaw=90))
    pipeline.set_editor_property('import_offset_translation', unreal.Vector(*config['native_import_offset_cm']))
    manager = unreal.InterchangeManager.get_interchange_manager_scripted()
    source = unreal.InterchangeManager.create_source_data(str(GLB))
    params = unreal.ImportAssetParameters()
    params.set_editor_property('is_automated', True)
    params.set_editor_property('replace_existing', False)
    params.set_editor_property('override_pipelines', [unreal.SoftObjectPath(pipeline.get_path_name()),
        unreal.SoftObjectPath('/Interchange/Pipelines/DefaultGLTFPipeline.DefaultGLTFPipeline')])
    assert manager.import_asset(DEST, source, params), 'Interchange import failed'
    paths = unreal.EditorAssetLibrary.list_assets(DEST, recursive=True, include_folder=False)
    objects = [unreal.load_asset(p) for p in paths]
    meshes = [a for a in objects if isinstance(a, unreal.StaticMesh)]
    assert len(meshes) == 1, f'Expected combined static mesh, got {len(meshes)}'
    mesh = meshes[0]
    r['mesh'] = mesh.get_path_name()
    r['triangles'] = mesh.get_num_triangles(0)
    bounds = mesh.get_bounding_box()
    r['bounds_min_cm'] = vector(bounds.min)
    r['bounds_max_cm'] = vector(bounds.max)
    r['dimensions_cm'] = vector(bounds.max - bounds.min)
    r['materials'] = [{'slot': str(s.material_slot_name), 'asset': s.material_interface.get_path_name() if s.material_interface else None} for s in mesh.get_editor_property('static_materials')]
    r['textures'] = [{'asset': a.get_path_name(), 'srgb': a.get_editor_property('srgb'),
        'compression': str(a.get_editor_property('compression_settings')),
        'mip_gen': str(a.get_editor_property('mip_gen_settings'))} for a in objects if isinstance(a, unreal.Texture2D)]
    r['native_asset_count'] = len(objects)
    assert r['triangles'] == 24466 and len(r['materials']) == 14
    assert abs(r['dimensions_cm'][1] - config['length_cm']) < .5, r['dimensions_cm']
    assert abs(r['bounds_max_cm'][1] - 83.23) < .5, 'Muzzle frame not applied'
    assert all(s['asset'] for s in r['materials']) and len(r['textures']) >= 36
    assert all(a.get_path_name().startswith(DEST + '/') for a in objects)
    r['material_parents'] = sorted({a.get_editor_property('parent').get_path_name() for a in objects if isinstance(a, unreal.MaterialInstanceConstant)})
    r['texture_parameters'] = {a.get_path_name(): [{'parameter': str(p.parameter_info.name), 'asset': p.parameter_value.get_path_name() if p.parameter_value else None} for p in a.get_editor_property('texture_parameter_values')] for a in objects if isinstance(a, unreal.MaterialInstanceConstant)}
    assert guard()
    for a in objects:
        assert unreal.EditorAssetLibrary.save_loaded_asset(a, False), a.get_path_name()
    content = STORE / 'Content' / DEST.removeprefix('/Game/')
    r['native_files'] = [{'path': p.relative_to(ROOT).as_posix(), 'size_bytes': p.stat().st_size, 'sha256': sha(p)} for p in sorted(content.rglob('*')) if p.is_file()]
    r['status'] = 'native_import_checked_requires_fresh_visual_review'
except Exception:
    r['status'] = 'failed'
    r['errors'].append(traceback.format_exc())
finally:
    r['protected_files_unchanged'] = bool(guard())
    (OUT / 'result.json').write_text(json.dumps(r, indent=2) + '\n', encoding='utf-8')
    unreal.log('CS549_GERMAN_IMPORT ' + r['status'])
    unreal.SystemLibrary.quit_editor()
