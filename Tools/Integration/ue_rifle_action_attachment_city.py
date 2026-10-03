"""Select the reviewed rifle-only attachment actor in the current retained city."""
import hashlib
import json
import os
import traceback
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT = STORE / 'Evidence/CityGameplay20261002/RifleActionAttachmentV3' / os.environ['CS549_RIFLE_ACTION_CITY_IDENTITY']
assert OUT.name.replace('_', '').isalnum() and not OUT.exists()
DEST = ROOT / 'Assets/Integration/CITY_RIFLE_ACTION_DRAFT_INVENTORY_20261002.json'
assert not DEST.exists(), 'Preserve occupied checkpoint'
inventory = json.loads((ROOT / 'Assets/Integration/CITY_WEAPON_TRANSFORM_DRAFT_INVENTORY_20261002.json').read_text())
deps = json.loads((ROOT / 'Assets/Integration/RELOAD_DRAFT_SNAPSHOT_20261002.json').read_text())
author = json.loads((OUT.parent / 'author_v4/result.json').read_text())
live = json.loads((OUT.parent / 'live_v2/result.json').read_text())
moving = json.loads((OUT.parent / 'live_v4/result.json').read_text())
assert author['status'] == 'saved_unselected_rifle_actor_requires_fresh_runtime_review' and not author['errors']
assert live['status'] == 'fresh_rifle_actor_requires_contact_review' and not live['errors'] and live['protected_37_unchanged']
assert live['max_walk_speed_cm_s'] > 100 and live['max_anchor_error_cm'] < 2
assert moving['status'] == 'fresh_rifle_actor_requires_contact_review' and not moving['errors'] and moving['protected_37_unchanged']
assert moving['moving_reload_frames'] > 10 and moving['max_anchor_error_cm'] < 2
assert (ROOT / 'Docs/Development/RIFLE_ACTION_ATTACHMENT_IMPLEMENTATION_V3.md').exists()

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

records = inventory['files'] + deps['files'] + inventory['retained_unselected_rejected_trial'] + [author['saved_trial']]
assert all((ROOT / e['path']).stat().st_size == e['size_bytes'] and digest(ROOT / e['path']) == e['sha256'] for e in records)
ENTRY = '/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1'
map_item = next(e for e in inventory['files'] if e['package'] == ENTRY)
backup = OUT.parent / 'BeforeActionAttachment/LV_ParisStreetCombat_V1.umap'
assert backup.stat().st_size == map_item['size_bytes'] and digest(backup) == map_item['sha256']
fit = json.loads((OUT.parent / 'fit_v2/result.json').read_text())
selected = next(c for s in fit['samples'] if s['clip'] == 'Rifle_Idle' for c in s['candidates'] if c['name'] == 'two_grasp_left0.5')
OUT.mkdir(parents=True)
report = {'scope': __doc__, 'status': 'initializing', 'errors': [], 'actors': [], 'initial_attachment': selected,
          'human_contact_review_pending': True, 'generic_reload_left_hand_gap': True}

def write():
    (OUT / 'result.json').write_text(json.dumps(report, indent=2))

try:
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert levels.load_level(ENTRY)
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    by_label = {a.get_actor_label(): a for a in subsystem.get_all_level_actors()}
    cls = unreal.EditorAssetLibrary.load_blueprint_class(author['package'])
    for suffix in ('Player', 'Ally1', 'Ally2'):
        soldier = by_label['PC_City_' + suffix]
        old = by_label['PC_M1_Appearance_' + suffix]
        mesh = soldier.get_component_by_class(unreal.SkeletalMeshComponent)
        assert old.get_attach_parent_actor() == soldier
        assert 'ABP_PC_Allied_Stride_v1' in mesh.get_editor_property('anim_class').get_path_name()
        new = subsystem.spawn_actor_from_class(cls, old.get_actor_location(), old.get_actor_rotation())
        new.set_actor_label('PC_M1_Appearance_' + suffix)
        new.set_owner(soldier)
        new.set_editor_property('GripMesh', mesh)
        new.set_editor_property('Combatant', soldier)
        new.set_editor_property('LeftShiftCm', .5)
        new.static_mesh_component.set_static_mesh(old.static_mesh_component.get_editor_property('static_mesh'))
        assert new.static_mesh_component.get_editor_property('relative_scale3d') == unreal.Vector(1, 1, 1)
        assert new.attach_to_component(mesh, 'hand_r', unreal.AttachmentRule.KEEP_RELATIVE,
                                      unreal.AttachmentRule.KEEP_RELATIVE, unreal.AttachmentRule.KEEP_RELATIVE, False)
        r = selected['rotation']
        new.static_mesh_component.set_editor_property('relative_location', unreal.Vector(*selected['location']))
        new.static_mesh_component.set_editor_property('relative_rotation', unreal.Rotator(pitch=r[0], yaw=r[1], roll=r[2]))
        soldier.modify()
        soldier.set_editor_property('WeaponAppearance', new)
        assert subsystem.destroy_actor(old)
        new.set_actor_label('PC_M1_Appearance_' + suffix)
        report['actors'].append(suffix)
    assert levels.save_current_level()
    report['protected_36_except_team_map_unchanged'] = all(digest(ROOT / e['path']) == e['sha256'] for e in records if e['path'] != map_item['path'])
    assert report['protected_36_except_team_map_unchanged']
    result = json.loads(json.dumps(inventory))
    result['files'].append(author['saved_trial'])
    for e in result['files']:
        p = ROOT / e['path']
        e.update(size_bytes=p.stat().st_size, sha256=digest(p))
    result.update(scope='Original Allied motions with gun-only dynamic attachment and 0.5 cm left shift; human contact review pending',
                  previous_checkpoint='CITY_WEAPON_TRANSFORM_DRAFT_INVENTORY_20261002.json; verified map in private BeforeActionAttachment',
                  rifle_attachment=selected, attachment_policy={'left_shift_cm': .5, 'ready': 'two grasp heading',
                  'reloading': 'original right wrist rotation with current right grasp anchor', 'tick_group': 'PostUpdateWork',
                  'finger_pose_modified': False, 'reload_wrist_relative_rotation': inventory['rifle_attachment']['rotation']},
                  evidence=(OUT / 'result.json').relative_to(ROOT).as_posix(),
                  file_count=8, total_size_bytes=sum(e['size_bytes'] for e in result['files']))
    DEST.write_text(json.dumps(result, indent=2) + '\n')
    report['status'] = 'saved_rifle_action_attachment_requires_city_regression_and_human_review'
    report['saved_inventory'] = DEST.relative_to(ROOT).as_posix()
except Exception:
    report['status'] = 'failed'
    report['errors'].append(traceback.format_exc())
finally:
    write()
    unreal.SystemLibrary.quit_editor()
