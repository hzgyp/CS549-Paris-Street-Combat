"""Read-only LOD0 skin edge audit at the frozen native target phase."""
# Failed once in the live editor with python311 access violation, exit3.
# The original executed source is retained in edge_audit_v1/source.py.
# Exact failing native call is unproved. Never repeat this read path in a
# user-owned editor; a future disposable-process diagnostic needs a new plan.
raise RuntimeError('Stopped AN002 diagnostic: preserve evidence; do not rerun')

import builtins
import json
import traceback
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/ReloadSleeveAdaptationV2/edge_audit_v1'
assert not OUT.exists()
OUT.mkdir(parents=True)
(OUT / 'source.py').write_bytes(Path(__file__).read_bytes())
r = {'native_assets_saved': False, 'errors': [], 'scope': __doc__}
try:
    parent, owner, _, _ = builtins.cs549_sleeve_binding_probe
    mesh = owner.get_skeletal_mesh_asset()
    dynamic = unreal.new_object(unreal.DynamicMesh)
    dynamic, outcome = unreal.GeometryScript_AssetUtils.copy_mesh_from_skeletal_mesh(
        mesh, dynamic, unreal.GeometryScriptCopyMeshFromAssetOptions(), unreal.GeometryScriptMeshReadLOD())
    r['copy_outcome'] = str(outcome)
    _, vector_list, gaps = unreal.GeometryScript_MeshQueries.get_all_vertex_positions(dynamic, False)
    positions = unreal.GeometryScript_List.convert_vector_list_to_array(vector_list)
    assert not gaps
    _, bones = unreal.GeometryScript_BoneWeights.get_all_bones_info(dynamic)
    modifier = unreal.SkeletonModifier()
    assert modifier.set_skeletal_mesh(mesh)
    refs = {str(b.name): modifier.get_bone_transform(b.name, True) for b in bones}
    poses = {str(b.name): parent.get_socket_transform(b.name, unreal.RelativeTransformSpace.RTS_COMPONENT) for b in bones}
    weights = []
    skinned = []
    for i, pos in enumerate(positions):
        _, w, valid = unreal.GeometryScript_BoneWeights.get_vertex_bone_weights(dynamic, i)
        assert valid
        entries = [(str(bones[b.bone_index].name), b.weight) for b in w]
        assert abs(sum(v for _, v in entries) - 1) < .001
        v = unreal.Vector()
        for name, weight in entries:
            local = unreal.MathLibrary.inverse_transform_location(refs[name], pos)
            v += unreal.MathLibrary.transform_location(poses[name], local) * weight
        skinned.append(v)
        weights.append(entries)
    _, ids, _ = unreal.GeometryScript_MeshQueries.get_all_triangle_i_ds(dynamic)
    ids = unreal.GeometryScript_List.convert_index_list_to_array(ids)
    edges = set()
    for i in ids:
        indices, valid = unreal.GeometryScript_MeshQueries.get_triangle_indices(dynamic, i)
        assert valid
        a, b, c = indices.x, indices.y, indices.z
        edges.update((tuple(sorted((a,b))), tuple(sorted((b,c))), tuple(sorted((c,a)))))
    metrics = []
    for a, b in edges:
        ref = (positions[a] - positions[b]).length()
        deformed = (skinned[a] - skinned[b]).length()
        if ref > .01:
            metrics.append({'vertices': [a,b], 'reference_cm': ref, 'deformed_cm': deformed,
                'ratio': deformed/ref, 'weights': [weights[a],weights[b]],
                'reference_positions': [[p.x,p.y,p.z] for p in (positions[a],positions[b])],
                'deformed_positions': [[p.x,p.y,p.z] for p in (skinned[a],skinned[b])]})
    metrics.sort(key=lambda x:x['deformed_cm'], reverse=True)
    r.update(mesh=mesh.get_path_name(), phase_s=parent.get_position(), vertex_count=len(positions),
        triangle_count=len(ids), edge_count=len(edges), longest_edges=metrics[:30],
        max_edge_ratio=max(x['ratio'] for x in metrics),
        over_10cm_edges=sum(x['deformed_cm']>10 for x in metrics),
        over_5x_edges=sum(x['ratio']>5 for x in metrics),
        status='cpu_linear_skin_read_only_not_render_acceptance')
except Exception:
    r['errors'].append(traceback.format_exc())
    r['status'] = 'failed'
finally:
    (OUT / 'result.json').write_text(json.dumps(r,indent=2)+'\n', encoding='utf-8')
    unreal.log('CS549_SLEEVE_EDGE_AUDIT ' + r['status'])
