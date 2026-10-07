"""Read native skin-query API and the frozen preview bone transforms only."""
import builtins
import json
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/ReloadSleeveAdaptationV2/skin_probe_v3'
assert not OUT.exists()
OUT.mkdir(parents=True)
(OUT / 'source.py').write_bytes(Path(__file__).read_bytes())
source, owner, _, _ = builtins.cs549_sleeve_binding_probe
def tr(t):
    return {'t': [t.translation.x, t.translation.y, t.translation.z],
            'q': [t.rotation.x, t.rotation.y, t.rotation.z, t.rotation.w],
            's': [t.scale3d.x, t.scale3d.y, t.scale3d.z]}
report = {'native_assets_saved': False, 'components': {}, 'api': {}}
for label, comp in (('allied', source), ('owner', owner)):
    mesh = comp.get_skeletal_mesh_asset()
    report['components'][label] = {'mesh': mesh.get_path_name(), 'phase': comp.get_position(),
        'postprocess': str(mesh.get_editor_property('post_process_anim_blueprint')),
        'world_transform': tr(comp.get_socket_transform('None', unreal.RelativeTransformSpace.RTS_WORLD)),
        'bones_component': {str(comp.get_bone_name(i)): tr(comp.get_socket_transform(comp.get_bone_name(i), unreal.RelativeTransformSpace.RTS_COMPONENT)) for i in range(comp.get_num_bones())}}
for label, cls, names in (
    ('asset', unreal.GeometryScript_AssetUtils, ('copy_mesh_from_skeletal_mesh',)),
    ('query', unreal.GeometryScript_MeshQueries, ('get_all_vertex_positions', 'get_vertex_position', 'get_triangle_indices', 'get_all_triangle_ids')),
    ('bone', unreal.GeometryScript_BoneWeights, ('get_vertex_bone_weights', 'get_all_bones_info')),
    ('lists', unreal.GeometryScript_List, ('convert_vector_list_to_array', 'convert_index_list_to_array'))
):
    for name in names:
        method = getattr(cls, name, None)
        report['api'][label + '.' + name] = method.__doc__ if method else None
    report['api'][label + '.available_names'] = [name for name in dir(cls) if not name.startswith('_')]
(OUT / 'result.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
unreal.log('CS549_SLEEVE_SKIN_QUERY_READY')
