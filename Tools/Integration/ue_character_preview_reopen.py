"""Fresh-session read-only validation of the saved six-actor preview."""
import json
import traceback
from datetime import datetime
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[2]
assert Path(unreal.Paths.project_dir()).resolve() == (ROOT / 'Unreal/ParisStreetCombat').resolve()
OUT = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/P2'
previous = json.loads((OUT / 'presentation.json').read_text(encoding='utf-8'))
report = {'checked_at': datetime.now().astimezone().isoformat(),
    'engine': unreal.SystemLibrary.get_engine_version(), 'map': previous['map'],
    'actors': [], 'errors': [], 'scope': 'Fresh session saved scene/default animation references only; not PIE, gameplay, renderer, contact or packaging'}
try:
    if not previous.get('map_saved') or previous['errors']:
        raise RuntimeError('Do not certify an incomplete presentation save')
    if not unreal.EditorLevelLibrary.load_level(previous['map']):
        raise RuntimeError('Saved preview level did not reopen')
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    found = {actor.get_actor_label(): actor for actor in subsystem.get_all_level_actors()
             if actor.get_actor_label().startswith('P2_Preview_')}
    if len(found) != 6:
        raise RuntimeError('Expected exactly six saved preview actors')
    for expected in previous['actors']:
        actor = found[expected['label']]
        component = actor.get_component_by_class(unreal.SkeletalMeshComponent)
        mesh = component.get_skinned_asset()
        data = component.get_editor_property('animation_data')
        sequence = data.anim_to_play
        item = {'label': actor.get_actor_label(), 'mesh': mesh.get_path_name() if mesh else None,
                'sequence': sequence.get_path_name() if sequence else None,
                'looping': data.saved_looping, 'playing': data.saved_playing}
        item['pass'] = item['mesh'] == expected['mesh'] and item['sequence'] == expected['action'] and item['looping'] and item['playing']
        report['actors'].append(item)
        if not item['pass']:
            report['errors'].append('Saved defaults differ: ' + expected['label'])
except Exception:
    report['errors'].append(traceback.format_exc())
report['finished_at'] = datetime.now().astimezone().isoformat()
report['result'] = 'pass_saved_preview_reopen' if not report['errors'] else 'fail'
(OUT / 'fresh_reopen.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
unreal.log('CS549_PREVIEW_REOPEN_DONE ' + report['result'])
if report['errors']:
    raise RuntimeError('Read fresh_reopen.json for actual failures')
