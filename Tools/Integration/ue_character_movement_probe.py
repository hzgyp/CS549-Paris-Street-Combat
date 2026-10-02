"""Fresh-load the saved draft and test actual CharacterMovement/Blueprint requests."""
import json
import math
import traceback
from datetime import datetime
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[2]
assert Path(unreal.Paths.project_dir()).resolve() == (ROOT / 'Unreal/ParisStreetCombat').resolve()
OUT = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/P2/Movement'
BP = '/Game/ParisCombat/Blueprints/Characters/'
ANIM = '/Game/ParisCombat/Animation/LocomotionDraft/'
MESH = '/Game/ParisCombat/Characters/Adaptation/Meshes/'
REPORT = {'started_at': datetime.now().astimezone().isoformat(), 'engine': unreal.SystemLibrary.get_engine_version(),
          'scope': 'Transient Game World fixed-step diagnostic, same Blueprint requests and native CharacterMovement; not PIE input-device, Nav/AI, city-ground or packaged acceptance',
          'cases': [], 'errors': []}


def checkpoint():
    (OUT / 'movement_probe_v3.json').write_text(json.dumps(REPORT, indent=2), encoding='utf-8')


if (OUT / 'movement_probe_v3.json').exists():
    raise RuntimeError('Refusing existing probe v3 evidence; preserve it and choose a new identity')
checkpoint()
try:
    authored = json.loads((OUT / 'authoring.json').read_text(encoding='utf-8'))
    if authored['errors'] or not authored['result'].startswith('saved_drafts'):
        raise RuntimeError('Authoring prerequisite failed')
    variants = {
        'Allied_A': 'SK_WWII_US_Paratrooper_simple_UE582_v1',
        'Allied_B': 'SK_WWII_US_Paratrooper_simpleB_UE582_v1',
        'German_A': 'SK_WWII_GermanSoldier_varA_UE582_v1',
        'German_B': 'SK_WWII_GermanSoldier_varB_UE582_v1',
    }
    for name in variants.values():
        unreal.load_asset(MESH + name)
    # Resolve native render resources before transient World captures.
    unreal.AutomationLibrary.finish_loading_before_screenshot()
    for label, name in variants.items():
        faction = label.split('_')[0]
        for fps in (30, 60, 120):
            case = json.loads(unreal.ParisBlueprintAuthoring.probe_movement(
                BP + 'BP_PCPlayer.BP_PCPlayer_C', fps, MESH + name, ANIM + 'ABP_PC_' + faction))
            case['variant'] = label
            if 'error' in case:
                raise RuntimeError(case['error'])
            phases = {p['phase']: p for p in case['phases']}
            criteria = {
                'walking_forward_400_to_460_cm': 400 <= phases['walk_forward']['dx_cm'] <= 460,
                'walking_right_270_to_315_cm': 270 <= phases['walk_right']['dy_cm'] <= 315,
                'braking_stops': phases['brake']['end_speed_cm_s'] < .1,
                'wall_blocks': case['wall_penetration_cm'] < .1 and 1000 <= phases['run_to_wall']['end_x_cm'] <= 1017,
                'settled_on_ground': all(p['moving_on_ground'] for p in case['phases']),
                'stable_capsule_clearance': all(1.5 <= p['capsule_floor_gap_min_cm'] <= p['capsule_floor_gap_max_cm'] <= 2.6 for p in case['phases'][1:]),
                'anim_tracks_planar_speed': all(abs(p.get('anim_ground_speed_cm_s', -999) - p['end_speed_cm_s']) < 10 for p in case['phases']),
                'finite_skinned_geometry': all(p['skinned_vertices'] > 0 and math.isfinite(p['geometry_min_world_z_cm']) for p in case['phases']),
            }
            case['criteria'] = criteria
            case['movement_result'] = 'pass' if all(criteria.values()) else 'fail'
            REPORT['cases'].append(case)
            checkpoint()
    REPORT['result'] = 'pass_numeric_movement_only' if all(c['movement_result'] == 'pass' for c in REPORT['cases']) else 'fail_numeric_movement'
except Exception:
    REPORT['errors'].append(traceback.format_exc())
    REPORT['result'] = 'fail'
REPORT['finished_at'] = datetime.now().astimezone().isoformat()
checkpoint()
unreal.log('CS549_MOVEMENT_PROBE_DONE ' + REPORT['result'])
if REPORT['errors']:
    raise RuntimeError('Read Movement/movement_probe.json for exact errors')
