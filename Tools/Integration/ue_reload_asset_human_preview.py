"""User-requested preview-only asset review, not resumption of stopped AN001 repair.

Reviewed AN001 and FP001. Open source and retained derived reloads in native
Animation Asset Editor on Entry, without PIE/map save/authoring. Native VIEW
activation returned false in the first attempt; normal EDIT activation opens the
editor but is not an enforced read-only mode. Do not edit or save during review.
Early check: each native editor reports opened and all protected bytes match.
Stop on missing input/open failure; leave editor user-owned, no retry authoring.
"""
import json
import os
import sys
import traceback
from pathlib import Path
import unreal

sys.path.insert(0, str(Path(__file__).parent))
from weapon_animation_reuse_common import ROOT, RELOAD, SOURCE_RELOAD, guard, output, read, sha

out = output(os.environ['CS549_RELOAD_ASSET_REVIEW_ID'])
report = {'status': 'starting', 'errors': [], 'user_owned': True,
          'map_saved': False, 'native_assets_saved': False, 'pie_started': False,
          'mode': 'preview-only asset inspection; normal editor, no save or repair',
          'opened': []}
(out / 'source.py').write_bytes(Path(__file__).read_bytes())
try:
    report['protected_files_before'] = guard()
    assert not hasattr(unreal, 'ParisBlueprintAuthoring')
    inventory = read(ROOT / 'Assets/Integration/WEAPON_ANIMATION_REUSE_DRAFT_INVENTORY_20261004.json')
    for row in inventory['files']:
        p = ROOT / row['path']
        assert p.stat().st_size == row['size_bytes'] and sha(p) == row['sha256']
    editor = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
    # Open original D059 last so its unmodified mannequin action is foremost.
    for label, path in (
        ('old_bound_reload_rejected', '/Game/RifleAnimsetPro/Animations/InPlace/Rifle_Reload_2'),
        ('failed_retarged_allied_candidate', RELOAD),
        ('original_d059_aim_reload', SOURCE_RELOAD),
    ):
        asset = unreal.load_asset(path)
        assert asset and isinstance(asset, unreal.AnimSequence), path
        opened = editor.open_editor_for_assets([asset], unreal.AssetTypeActivationOpenedMethod.EDIT)
        assert opened, 'Native asset editor did not open ' + path
        report['opened'].append({'label': label, 'path': path,
                                 'duration_s': asset.get_play_length(), 'opened': bool(opened)})
    report['protected_files_after_open'] = guard()
    report['status'] = 'ready_for_human_asset_inspection'
except Exception:
    report['status'] = 'failed_asset_review_startup'
    report['errors'].append(traceback.format_exc())
    unreal.log_error(report['errors'][-1])
finally:
    (out / 'result.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    unreal.log('CS549_RELOAD_ASSET_REVIEW ' + report['status'])
    # No persistent Python updater or automatic shutdown of the user's editor.
