"""Read-only 60 Hz complete-cycle causal comparison; modes restored, no package saves."""
import hashlib
import json
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT = STORE / 'Evidence/P2/Retarget/translation_compare_v1.json'
if OUT.exists():
    raise RuntimeError('Refusing existing causal comparison')
MESH = '/Game/ParisCombat/Characters/Adaptation/Meshes/'
models = ['SK_WWII_GermanSoldier_varA_UE582_v1', 'SK_WWII_US_Paratrooper_simple_UE582_v1']
native_files = list((STORE / 'Content/GermanSoldier').rglob('*.uasset'))
before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in native_files}
for mesh in models:
    unreal.load_asset(MESH + mesh)
unreal.AutomationLibrary.finish_loading_before_screenshot()
cases = []
for mesh in models:
    for clip in ('Rifle_Idle', 'Rifle_WalkFwdLoop', 'Rifle_RunFwdLoop', 'Rifle_StrafeLeftLoop', 'Rifle_WalkBwdLoop'):
        cases.append(json.loads(unreal.ParisBlueprintAuthoring.compare_translation_modes(
            MESH + mesh, '/Game/RifleAnimsetPro/Animations/InPlace/' + clip)))
after = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in native_files}
assert before == after, 'Original German package bytes changed'
OUT.write_text(json.dumps({'engine': unreal.SystemLibrary.get_engine_version(), 'cases': cases,
    'original_german_files_unchanged': len(before), 'scope': 'Read-only component pose comparison, no World movement/stride acceptance'}, indent=2), encoding='utf-8')
unreal.log('CS549_TRANSLATION_COMPARE_DONE')
