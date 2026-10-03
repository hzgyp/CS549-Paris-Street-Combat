"""Select the documented coarse grip increment in the retained city; team map only."""
import hashlib
import json
import os
import traceback
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
IDENTITY = os.environ['CS549_GRIP_CITY_IDENTITY']
assert IDENTITY.replace('_', '').isalnum(), 'Safe evidence identity required'
OUT = STORE / 'Evidence/CityGameplay20261002/WeaponGrip' / IDENTITY
assert not OUT.exists(), 'Preserve occupied author identity'
OUT.mkdir(parents=True)
DEST = ROOT / 'Assets/Integration/CITY_WEAPON_GRIP_DRAFT_INVENTORY_20261002.json'
assert not DEST.exists(), 'Do not overwrite an existing grip checkpoint'
prior = json.loads((ROOT / 'Assets/Integration/CITY_NAVIGATION_DRAFT_INVENTORY_20261002.json').read_text())
old = json.loads((ROOT / 'Assets/Integration/RELOAD_DRAFT_SNAPSHOT_20261002.json').read_text())
trial = json.loads((OUT.parent / 'layer_fresh_v3/result.json').read_text())
assert trial['status'] == 'runtime_trial_pending_contact_review' and not trial['errors']
assert trial['protected_35_unchanged']
assert trial['joints'][-2]['velocity'][0] > 200, 'Actual walk sample required'
assert (OUT.parent / 'COARSE_CONTACT_REVIEW.json').exists(), 'Documented image review required'
review = json.loads((OUT.parent / 'COARSE_CONTACT_REVIEW.json').read_text())
assert review['coarse_contact_candidate_selected'] and not review['final_presentation_accepted']

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

records = prior['files'] + old['files'] + [trial['saved_trial']]
assert all((ROOT / e['path']).stat().st_size == e['size_bytes'] and digest(ROOT / e['path']) == e['sha256'] for e in records)
entry = '/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1'
map_item = next(e for e in prior['files'] if e['package'] == entry)
backup = OUT.parent / 'BeforeCityGrip/LV_ParisStreetCombat_V1.umap'
assert backup.stat().st_size == map_item['size_bytes'] and digest(backup) == map_item['sha256'], 'Closed-editor backup required'
report = {'scope': __doc__, 'status': 'initializing', 'errors': [], 'actors': [],
          'human_visual_review_pending': True, 'known_walk_view_gap': review['known_walk_view_gap']}

def write():
    (OUT / 'result.json').write_text(json.dumps(report, indent=2))

try:
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert levels.load_level(entry)
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    by_label = {a.get_actor_label(): a for a in actors}
    cls = unreal.EditorAssetLibrary.load_blueprint_class('/Game/ParisCombat/Animation/WeaponPresentationV1/ABP_PC_AlliedGripV1')
    selected = json.loads((OUT.parent / 'probe_v2/result.json').read_text())
    r = selected['experimental_relative_rotation']
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
        root.set_editor_property('relative_location', unreal.Vector(*selected['experimental_relative_location']))
        root.set_editor_property('relative_rotation', unreal.Rotator(pitch=r[0], yaw=r[1], roll=r[2]))
        report['actors'].append(suffix)
    assert levels.save_current_level()
    protected = [e for e in records if e['path'] != map_item['path']]
    report['protected_35_except_team_map_unchanged'] = all(digest(ROOT / e['path']) == e['sha256'] for e in protected)
    assert report['protected_35_except_team_map_unchanged']
    current = json.loads(json.dumps(prior))
    current.update(scope='Coarse Allied grip increment on retained navigation city; human visual/full presentation acceptance pending',
                   evidence=(OUT / 'result.json').relative_to(ROOT).as_posix(),
                   previous_checkpoint='CITY_NAVIGATION_DRAFT_INVENTORY_20261002.json; verified map rollback in private BeforeCityGrip',
                   known_walk_view_gap=review['known_walk_view_gap'])
    for e in current['files']:
        p = ROOT / e['path']
        e.update(size_bytes=p.stat().st_size, sha256=digest(p))
    extra = dict(trial['saved_trial'])
    extra['package'] = '/Game/ParisCombat/Animation/WeaponPresentationV1/ABP_PC_AlliedGripV1'
    current['files'].append(extra)
    current.update(file_count=len(current['files']), total_size_bytes=sum(e['size_bytes'] for e in current['files']))
    DEST.write_text(json.dumps(current, indent=2) + '\n')
    report['status'] = 'saved_coarse_grip_requires_fresh_regression_and_human_review'
    report['saved_inventory'] = DEST.relative_to(ROOT).as_posix()
except Exception:
    report['status'] = 'failed'
    report['errors'].append(traceback.format_exc())
finally:
    write()
    unreal.SystemLibrary.quit_editor()
