"""Fresh-load adapted meshes and full-cycle directional CharacterMovement probes."""
import json
import math
import re
import traceback
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/P2/Movement'
command = unreal.SystemLibrary.get_command_line()
selected = re.search(r'-ParisVariant=(Allied_A|Allied_B|German_A|German_B)(?:\s|$)', command)
rate = re.search(r'-ParisFPS=(30|60|120)(?:\s|$)', command)
identity = re.search(r'-ParisProbeIdentity=(\w+)(?:\s|$)', command)
stride = '-ParisStride=true' in command
if selected and (not rate or not identity):
    raise RuntimeError('Single-case probing requires explicit FPS and unique identity')
DEST = OUT / ('movement_probe_' + identity.group(1) + '.json' if identity else 'movement_probe_v4.json')
if DEST.exists():
    raise RuntimeError('Refusing existing v4 evidence')
report = {'engine': unreal.SystemLibrary.get_engine_version(), 'cases': [], 'errors': [],
          'scope': 'Fixed-step transient World, full sampled cycles; not PIE/device input, city ground, packaging or measured FPS'}
def checkpoint():
    DEST.write_text(json.dumps(report, indent=2), encoding='utf-8')
checkpoint()
try:
    meshes = {
        'Allied_A': '/Game/ParisCombat/Characters/Adaptation/Meshes/SK_WWII_US_Paratrooper_simple_UE582_v1',
        'Allied_B': '/Game/ParisCombat/Characters/Adaptation/Meshes/SK_WWII_US_Paratrooper_simpleB_UE582_v1',
        'German_A': '/Game/ParisCombat/Animation/RetargetDraft/GermanTranslationV1/SK_PC_German_A_Translation_v1',
        'German_B': '/Game/ParisCombat/Animation/RetargetDraft/GermanTranslationV1/SK_PC_German_B_Translation_v1',
    }
    report['references'] = [json.loads(unreal.ParisBlueprintAuthoring.describe_reference_skeleton(p)) for p in meshes.values()]
    for label, path in meshes.items():
        unreal.load_asset(path)
    unreal.AutomationLibrary.finish_loading_before_screenshot()
    for label, mesh in meshes.items():
        if selected and label != selected.group(1):
            continue
        for fps in ((int(rate.group(1)),) if rate else (30,60,120)):
            case = json.loads(unreal.ParisBlueprintAuthoring.probe_movement(
                '/Game/ParisCombat/Blueprints/Characters/BP_PCPlayer.BP_PCPlayer_C', fps, mesh,
                '/Game/ParisCombat/Animation/DirectionalDraft/ABP_PC_' + label.split('_')[0] + ('_Stride_v1' if stride else '')))
            case['variant'] = label
            assert 'error' not in case, case
            phases = {p['phase']: p for p in case['phases']}
            case['criteria'] = {
                'forward_distance': 400 < phases['walk_forward']['dx_cm'] < 460,
                'right_distance': 270 < phases['walk_right']['dy_cm'] < 315,
                'backward_distance': -315 < phases['walk_backward']['dx_cm'] < -270,
                'left_distance': -315 < phases['walk_left']['dy_cm'] < -270,
                'braking': phases['run_brake']['end_speed_cm_s'] < .1,
                'wall_blocks': case['wall_penetration_cm'] < .1,
                'grounded': all(p['moving_on_ground'] for p in case['phases']),
                'finite_pose_series': all(p['pose_samples'] and all(math.isfinite(s['min_z_cm']) for s in p['pose_samples']) for p in case['phases']),
                'direction_axes': abs(phases['walk_forward']['VelocityForward']-150)<1 and abs(phases['walk_right']['VelocityRight']-150)<1
                    and abs(phases['walk_backward']['VelocityForward']+150)<1 and abs(phases['walk_left']['VelocityRight']+150)<1,
            }
            for p in case['phases']:
                z = [s['min_z_cm'] for s in p['pose_samples']]
                p['contact_range_cm'] = [min(z), max(z)]
                # Diagnostic bone drift only: lower foot with low vertical change.
                # A lifted foot or running flight is not a planted-foot failure.
                slips=[]
                for previous, current in zip(p['pose_samples'][20:], p['pose_samples'][21:]):
                    bone = 'foot_l' if current['foot_l'][2] <= current['foot_r'][2] else 'foot_r'
                    a,b=previous[bone],current[bone]
                    if abs(a[2]-b[2])*fps < 5:
                        slips.append(math.dist(a[:2],b[:2])*fps)
                p['lower_foot_low_vertical_motion_drift_cm_s'] = sorted(slips)[len(slips)//2] if slips else None
            case['result'] = 'pass_numeric_directional_only' if all(case['criteria'].values()) else 'fail_numeric'
            report['cases'].append(case)
            checkpoint()
    report['result'] = 'pass_numeric_directional_only' if all(c['result'].startswith('pass') for c in report['cases']) else 'fail_numeric'
except Exception:
    report['errors'].append(traceback.format_exc())
    report['result'] = 'fail'
checkpoint()
if report['errors']:
    raise RuntimeError(report['errors'][0])
unreal.log('CS549_DIRECTIONAL_PROBE_DONE ' + report['result'])
