"""Restore original Allied pose and adjust only rigid rifle attachments in the retained city."""
import hashlib
import json
import os
import traceback
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
IDENTITY = os.environ['CS549_RIFLE_TRANSFORM_AUTHOR_IDENTITY']
assert IDENTITY.replace('_', '').isalnum()
OUT = STORE / 'Evidence/CityGameplay20261002/WeaponTransformV2' / IDENTITY
assert not OUT.exists()
DEST = ROOT / 'Assets/Integration/CITY_WEAPON_TRANSFORM_DRAFT_INVENTORY_20261002.json'
assert not DEST.exists(), 'Never overwrite an occupied checkpoint'
prior = json.loads((ROOT / 'Assets/Integration/CITY_WEAPON_GRIP_DRAFT_INVENTORY_20261002.json').read_text())
deps = json.loads((ROOT / 'Assets/Integration/RELOAD_DRAFT_SNAPSHOT_20261002.json').read_text())
phases = json.loads((OUT.parent / 'phases_v2/result.json').read_text())
assert not phases['errors'] and phases['protected_36_unchanged'] and phases['source_clip_bytes_unchanged']
assert len(phases['samples']) == 6 and all(s['original_hand_transforms_unchanged'] for s in phases['samples'])
assert phases['phase_pose_variation_cm'] > 1
selected = phases['selected']
assert selected['name'] == 'hollow_fit_zero'
assert (ROOT / 'Docs/Development/WEAPON_TRANSFORM_ONLY_REPAIR_V2.md').exists()

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

records = prior['files'] + deps['files']
assert all((ROOT / e['path']).stat().st_size == e['size_bytes'] and digest(ROOT / e['path']) == e['sha256'] for e in records)
entry = '/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1'
map_item = next(e for e in prior['files'] if e['package'] == entry)
backup = OUT.parent / 'BeforeTransformOnly/LV_ParisStreetCombat_V1.umap'
assert backup.stat().st_size == map_item['size_bytes'] and digest(backup) == map_item['sha256'], 'Closed-editor verified rollback required'
original_cls = '/Game/ParisCombat/Animation/DirectionalDraft/ABP_PC_Allied_Stride_v1'
source_paths = [STORE / ('Content/RifleAnimsetPro/Animations/InPlace/' + n + '.uasset')
                for n in ('Rifle_Idle', 'Rifle_ShootOnce', 'Rifle_WalkFwdLoop', 'Rifle_Reload_2')]
source_hashes = {p: digest(p) for p in source_paths}
OUT.mkdir(parents=True)
report = {'scope': __doc__, 'status': 'initializing', 'errors': [], 'actors': [],
          'selected': selected, 'original_anim_class': original_cls, 'human_visual_review_pending': True}

def write():
    (OUT / 'result.json').write_text(json.dumps(report, indent=2))

try:
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert levels.load_level(entry)
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    by_label = {a.get_actor_label(): a for a in actors}
    cls = unreal.EditorAssetLibrary.load_blueprint_class(original_cls)
    r = selected['rotation']
    for suffix in ('Player', 'Ally1', 'Ally2'):
        soldier = by_label['PC_City_' + suffix]
        weapon = by_label['PC_M1_Appearance_' + suffix]
        assert weapon.get_attach_parent_actor() == soldier
        mesh = soldier.get_component_by_class(unreal.SkeletalMeshComponent)
        assert 'SK_WWII_US_Paratrooper_simple' in mesh.get_skeletal_mesh_asset().get_path_name()
        mesh.modify()
        mesh.set_anim_instance_class(cls)
        weapon.modify()
        root = weapon.static_mesh_component
        root.modify()
        assert root.get_editor_property('relative_scale3d') == unreal.Vector(1, 1, 1)
        root.set_editor_property('relative_location', unreal.Vector(*selected['location']))
        root.set_editor_property('relative_rotation', unreal.Rotator(pitch=r[0], yaw=r[1], roll=r[2]))
        report['actors'].append(suffix)
    assert levels.save_current_level()
    protected = [e for e in records if e['path'] != map_item['path']]
    report['protected_35_except_team_map_unchanged'] = all(digest(ROOT / e['path']) == e['sha256'] for e in protected)
    report['source_clips_unchanged'] = all(digest(p) == h for p, h in source_hashes.items())
    assert report['protected_35_except_team_map_unchanged'] and report['source_clips_unchanged']
    current = json.loads(json.dumps(prior))
    rejected = [e for e in current['files'] if e['package'].endswith('/ABP_PC_AlliedGripV1')]
    current['files'] = [e for e in current['files'] if e not in rejected]
    assert len(current['files']) == 7 and len(rejected) == 1
    current.update(scope='Original Allied stride pose, rigid rifle transform only; human contact/full presentation review pending',
                   evidence=(OUT / 'result.json').relative_to(ROOT).as_posix(),
                   previous_checkpoint='CITY_WEAPON_GRIP_DRAFT_INVENTORY_20261002.json; verified rejected map in private BeforeTransformOnly',
                   rifle_attachment=selected, original_allied_anim_class=original_cls,
                   retained_unselected_rejected_trial=rejected)
    for e in current['files']:
        p = ROOT / e['path']
        e.update(size_bytes=p.stat().st_size, sha256=digest(p))
    current.update(file_count=7, total_size_bytes=sum(e['size_bytes'] for e in current['files']))
    DEST.write_text(json.dumps(current, indent=2) + '\n')
    report['status'] = 'saved_transform_only_requires_fresh_regression_and_human_review'
    report['saved_inventory'] = DEST.relative_to(ROOT).as_posix()
except Exception:
    report['status'] = 'failed'
    report['errors'].append(traceback.format_exc())
finally:
    write()
    unreal.SystemLibrary.quit_editor()
