"""Read-only native bone/track diagnostics in the user's existing UE editor."""
import hashlib
import json
import math
import traceback
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT = STORE / 'Evidence/ReloadSleeveAdaptationV2/bone_audit_v1'
assert not OUT.exists(), 'Preserve occupied evidence identity'
OUT.mkdir(parents=True)
(OUT / 'source.py').write_bytes(Path(__file__).read_bytes())
report = {'scope': __doc__, 'errors': [], 'native_assets_saved': False,
          'models': {}, 'clips': {}, 'components': []}
rows = json.loads((ROOT / 'tmp/weapon-animation-reuse/preflight_v1.json').read_text())['files']
rows += json.loads((ROOT / 'Assets/Integration/WEAPON_ANIMATION_REUSE_DRAFT_INVENTORY_20261004.json').read_text())['files']

def guard():
    for row in rows:
        path = ROOT / row['path']
        assert path.stat().st_size == row['size_bytes']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256'], row['path']
    return len(rows)

def tr(t):
    return {'translation': [t.translation.x, t.translation.y, t.translation.z],
            'rotation': [t.rotation.x, t.rotation.y, t.rotation.z, t.rotation.w],
            'scale': [t.scale3d.x, t.scale3d.y, t.scale3d.z]}

try:
    guard()
    assert not hasattr(unreal, 'ParisBlueprintAuthoring')
    for label, path in {
        'source': '/Game/Rifle_01/Character/Mesh/SK_Mannequin',
        'allied': '/Game/ParisCombat/Characters/Adaptation/Meshes/SK_WWII_US_Paratrooper_simple_UE582_v1',
        'owner': '/Game/ParisCombat/Characters/FirstPersonContinuousArmsV3/SK_PC_ContinuousArmsV3'
    }.items():
        mesh = unreal.load_asset(path)
        modifier = unreal.SkeletonModifier()
        assert modifier.set_skeletal_mesh(mesh)
        names = [str(n) for n in modifier.get_all_bone_names()]
        report['models'][label] = {
            'path': path, 'skeleton': mesh.get_editor_property('skeleton').get_path_name(),
            'ref_local': {n: tr(modifier.get_bone_transform(n, False)) for n in names},
            'ref_component': {n: tr(modifier.get_bone_transform(n, True)) for n in names},
            'parents': {n: str(unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem).get_bone_parent(mesh, n)) for n in names}}
    report['api'] = {name: getattr(unreal.AnimationLibrary, name).__doc__
                     for name in ('get_bone_pose_for_time', 'get_bone_poses_for_time')}
    report['skeletal_component_api'] = [n for n in dir(unreal.SkeletalMeshComponent)
        if any(s in n.lower() for s in ('skin', 'refresh', 'tick_anim', 'update_anim', 'bone_transform'))]
    for label, path in {
        'source': '/Game/Rifle_01/Animation/In-Place/W2_Stand_Aim_Reload_IP',
        'failed': '/Game/ParisCombat/Animation/WeaponAnimationReuseV1/AS_PC_D059AimReloadV1',
        'control': '/Game/RifleAnimsetPro/Animations/InPlace/Rifle_Reload_2'
    }.items():
        clip = unreal.load_asset(path)
        names = [str(n) for n in unreal.AnimationLibrary.get_animation_track_names(clip)]
        report['clips'][label] = {'path': path, 'length_s': clip.get_play_length(),
            'tracks': names, 'samples': {}, 'skeleton': clip.get_editor_property('skeleton').get_path_name()}
        for phase in (0, .4, 1.2, 2.2, 3.4, 3.98):
            t = min(phase, clip.get_play_length() - .0001)
            report['clips'][label]['samples'][str(phase)] = {
                n: tr(unreal.AnimationLibrary.get_bone_pose_for_time(clip, n, t, False)) for n in names}
    for comp in unreal.ObjectIterator(unreal.SkeletalMeshComponent):
        mesh = comp.get_editor_property('skeletal_mesh_asset')
        if mesh and '/Engine/Transient.' in comp.get_path_name():
            report['components'].append({'path': comp.get_path_name(), 'mesh': mesh.get_path_name(),
                                         'class': comp.get_class().get_name()})
    report['status'] = 'read_only_data_collected_cause_not_yet_proved'
except Exception:
    report['errors'].append(traceback.format_exc())
    report['status'] = 'failed'
finally:
    report['protected_records_unchanged'] = guard()
    (OUT / 'result.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    unreal.log('CS549_RELOAD_SLEEVE_AUDIT ' + report['status'])
