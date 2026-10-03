"""Reuse reviewed motion-probe functions for transient muzzle regression, not shipping code."""
import ast
import hashlib
import json
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/ContinuousArmsV3'

def trial_records():
    original = json.loads((ROOT/'Failures/FP001-20261003-first-person-view/MANIFEST.json').read_text(encoding='utf-8-sig'))['protected_files']
    derivative = json.loads((ROOT/'Assets/Integration/CONTINUOUS_ARMS_TRIAL_INVENTORY_20261003.json').read_text())['files']
    return original+derivative

class RuntimeTrial:
    """Only function definitions are reused; do not execute the probe's run/output/callback globals."""
    def __init__(self,world,player):
        records = trial_records()
        assert all(hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest() == f['sha256'] for f in records)
        path = Path(__file__).with_name('ue_continuous_arms_dynamic.py')
        code = path.read_text(encoding='utf-8')
        tree = ast.parse(code)
        names = {'xyz','prop','state','fingers','pose_delta','grasp','spawn','setup','update_display'}
        selected = [n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
        assert {n.name for n in selected} == names
        self.n = {'unreal':unreal,'world':world,'player':player,'native':json.loads((BASE/'native_material_v1/result.json').read_text()),
                  'report':{},'framing':None,'last_action':None}
        exec(compile(ast.Module(body=selected,type_ignores=[]),str(path),'exec'),self.n)
        self.n['setup']()
        self.n['update_display']()
        self.weapon = self.n['display']
        player.set_editor_property('WeaponAppearance',self.weapon)
        self.n['report']['display_bound_to_weapon_appearance'] = True
        self.n['report']['source_function_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        self.n['report']['implementation'] = 'Transient standard actors + diagnostic Python; no runtime/native gameplay selection'

    def update(self):
        self.n['update_display']()

    def snapshot(self):
        n = self.n
        c = n['eye']
        return {'finger_local_delta':n['pose_delta'](),
                'camera_relative_cm':n['xyz'](c.get_editor_property('relative_location')),
                'fov':c.get_editor_property('field_of_view'),
                'original_anim_class':n['source'].get_anim_instance().get_class().get_name(),
                'display_bound':n['player'].get_editor_property('WeaponAppearance') == self.weapon,
                'arms_visible':n['vm'].is_visible()}
