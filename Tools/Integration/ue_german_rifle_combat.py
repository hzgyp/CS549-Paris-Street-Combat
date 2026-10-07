"""Retained combat regression with one-time action/German gun staging; no AI."""
import os
import sys
from pathlib import Path
import json
import hashlib
sys.path.insert(0, str(Path(__file__).parent))
import ue_player_actions_stage as action_stage
from ue_german_rifle_stage import stage_german_rifles

original = action_stage.stage_actions_actor


def combined_stage():
    r, player, view = original()
    r['german_integration'] = stage_german_rifles()
    return r, player, view


action_stage.stage_actions_actor = combined_stage
os.environ['CS549_ACTION_IDENTITY'] = os.environ['CS549_GERMAN_UE_IDENTITY']
# Apply the existing action-combat environment, but keep the legacy source bytes
# intact. The legacy "unarmed German" fixture is no longer unarmed after staging.
os.environ['CS549_COMBAT_PIE_IDENTITY'] = os.environ['CS549_ACTION_IDENTITY']
os.environ['CS549_CITY_NATIVE_CHECKPOINT'] = 'CITY_CONTINUOUS_ARMS_NATIVE_INVENTORY_20261003.json'
os.environ['CS549_CONTINUOUS_ARMS_NATIVE_TEST'] = '1'
os.environ['CS549_ACTIONS_NATIVE_TEST'] = '1'
for name in ('CS549_CONTINUOUS_ARMS_MUZZLE_PREVIEW', 'CS549_PLAYER_AIM_PREVIEW', 'CS549_FIRST_PERSON_VIEW_PREVIEW'):
    os.environ[name] = '0'
path = Path(__file__).with_name('ue_paris_combat_pie.py')
source = path.read_text()
old = """                before = state(enemy)
                enemy.call_method('PC_RequestFire', args=(origin_location, unreal.Vector(1, 0, 0)))
                after = state(enemy)
"""
new = """                # Single-call negative fixture only; native appearance is restored.
                fixture_weapon = enemy.get_editor_property('WeaponAppearance')
                assert fixture_weapon is not None
                enemy.set_editor_property('WeaponAppearance', None)
                try:
                    before = state(enemy)
                    enemy.call_method('PC_RequestFire', args=(origin_location, unreal.Vector(1, 0, 0)))
                    after = state(enemy)
                finally:
                    enemy.set_editor_property('WeaponAppearance', fixture_weapon)
                assert enemy.get_editor_property('WeaponAppearance') == fixture_weapon
"""
assert source.count(old) == 1, 'Review changed harness; never perform a broad replacement'
adapted = source.replace(old, new)
from german_rifle_ue_common import ROOT, STORE
proof = STORE / 'Evidence/GermanRifleUEV1' / (os.environ['CS549_GERMAN_UE_IDENTITY'] + '_harness')
assert not proof.exists(), 'Preserve occupied harness identity'
proof.mkdir(parents=True)
(proof / 'adapted_combat_source.py').write_text(adapted, encoding='utf-8')
(proof / 'fixture.json').write_text(json.dumps({
    'original_source': path.relative_to(ROOT).as_posix(),
    'original_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
    'adapted_sha256': hashlib.sha256(adapted.encode()).hexdigest(),
    'change': 'WeaponAppearance None only around one unarmed rejection call; restored in finally',
    'gameplay_source_changed': False, 'map_saved': False,
}, indent=2) + '\n', encoding='utf-8')
exec(compile(adapted, str(path), 'exec'), {'__file__': str(path), '__name__': '__main__'})
