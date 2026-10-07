"""Read-only installed native motion/rig/binding audit, no new assets."""
import json
import math
import os
import sys
import traceback
from pathlib import Path
import unreal
sys.path.insert(0, str(Path(__file__).parent))
from weapon_animation_reuse_common import ROOT, STORE, SOURCE_RELOAD, SHOOT, output, guard
OUT = output(os.environ['CS549_ANIMATION_IDENTITY'])
r = {'status': 'auditing', 'errors': [], 'models': {}, 'clips': [], 'bindings': {}, 'map_saved': False}
(OUT / 'source.py').write_bytes(Path(__file__).read_bytes())


def transform(t):
    return {'translation': [t.translation.x, t.translation.y, t.translation.z],
            'rotation': [t.rotation.x, t.rotation.y, t.rotation.z, t.rotation.w],
            'scale': [t.scale3d.x, t.scale3d.y, t.scale3d.z]}


def rig(mesh):
    mod = unreal.SkeletonModifier()
    assert mod.set_skeletal_mesh(mesh)
    # Query-only modifier; never CommitSkeletonToSkeletalMesh.
    return {str(n): transform(mod.get_bone_transform(n, False)) for n in mod.get_all_bone_names()}


try:
    assert not hasattr(unreal, 'ParisBlueprintAuthoring')
    guard()
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    registry.search_all_assets(True)
    meshes = {
        'source': '/Game/Rifle_01/Character/Mesh/SK_Mannequin',
        'allied': '/Game/ParisCombat/Characters/Adaptation/Meshes/SK_WWII_US_Paratrooper_simple_UE582_v1',
        'german': '/Game/ParisCombat/Animation/RetargetDraft/GermanTranslationV1/SK_PC_German_A_Translation_v1'}
    for name, p in meshes.items():
        mesh = unreal.load_asset(p)
        assert mesh, p
        r['models'][name] = {'path': p, 'skeleton': mesh.get_editor_property('skeleton').get_path_name(), 'ref_local': rig(mesh)}
    src = r['models']['source']['ref_local']
    r['ref_differences'] = {}
    for name in ('allied', 'german'):
        target = r['models'][name]['ref_local']
        rows = []
        for bone in sorted(set(src) & set(target)):
            a, b = src[bone]['rotation'], target[bone]['rotation']
            dot = abs(sum(x * y for x, y in zip(a, b))) / math.sqrt(sum(x*x for x in a)*sum(x*x for x in b))
            rows.append({'bone': bone, 'rotation_deg': math.degrees(2*math.acos(min(1, dot))),
                         'translation_cm': math.dist(src[bone]['translation'], target[bone]['translation'])})
        r['ref_differences'][name] = {'bones': rows, 'source_only': sorted(set(src)-set(target)), 'target_only': sorted(set(target)-set(src))}
    for path in (SOURCE_RELOAD, '/Game/Rifle_01/Animation/In-Place/W2_Stand_Fire_Single_IP', SHOOT,
                 '/Game/RifleAnimsetPro/Animations/InPlace/Rifle_ShootLoop_Additive'):
        clip = unreal.load_asset(path)
        assert clip, path
        r['clips'].append({'path': path, 'duration': clip.get_play_length(),
            'skeleton': clip.get_editor_property('skeleton').get_path_name(),
            'root_motion': clip.get_editor_property('enable_root_motion'),
            'additive_type': str(clip.get_editor_property('additive_anim_type')),
            'tracks': [str(n) for n in unreal.AnimationLibrary.get_animation_track_names(clip)]})
    old = '/Game/RifleAnimsetPro/Animations/InPlace/Rifle_Reload_2'
    opts = unreal.AssetRegistryDependencyOptions(include_hard_package_references=True, include_soft_package_references=True)
    r['old_reload_referencers'] = sorted(str(x) for x in registry.get_referencers(old, opts))
    for path in ('/Game/ParisCombat/Blueprints/Characters/SimplifiedReloadDraft/BP_PCCombatantReloadV1',
                 '/Game/ParisCombat/Blueprints/PlayerActionsV1/BP_PCParisPlayerActionsV6'):
        bp = unreal.load_asset(path)
        rows = {}
        for graph in unreal.BlueprintEditorLibrary.list_graphs(bp):
            g = unreal.BlueprintGraphEditor.get_graph_editor(graph)
            rows[graph.get_name()] = [n.get_name() for n in g.list_all_nodes()]
        r['bindings'][path] = rows
    r['status'] = 'read_only_audit_complete_requires_target_trial'
except Exception:
    r['errors'].append(traceback.format_exc())
    r['status'] = 'failed'
finally:
    r['protected_files_unchanged'] = guard()
    (OUT / 'result.json').write_text(json.dumps(r, indent=2) + '\n', encoding='utf-8')
    unreal.SystemLibrary.quit_editor()
