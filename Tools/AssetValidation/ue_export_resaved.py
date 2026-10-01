"""Exchange exports from the resaved lab; no material-lossless claim."""
import hashlib
import json
import traceback
from datetime import datetime
from pathlib import Path
import unreal

LAB = Path(unreal.Paths.project_dir()).resolve()
OUT = LAB / 'Evidence'
EXPORTS = OUT / 'Exports/UE582Resaved'
EXPORTS.mkdir(parents=True, exist_ok=True)
inventory = json.loads((OUT / 'ue_load_inventory.json').read_text(encoding='utf-8'))
report = {'engine': unreal.SystemLibrary.get_engine_version(), 'fbx_compatibility': '2018',
          'started_at': datetime.now().astimezone().isoformat(), 'exports': [], 'errors': []}
options = unreal.FbxExportOption()
options.set_editor_property('fbx_export_compatibility', unreal.FbxExportCompatibility.FBX_2018)
options.set_editor_property('ascii', False)
options.set_editor_property('level_of_detail', False)
options.set_editor_property('collision', False)
options.set_editor_property('export_morph_targets', True)
options.set_editor_property('export_preview_mesh', False)
options.set_editor_property('bake_material_inputs', unreal.FbxMaterialBakeMode.DISABLED)
paths = [a['path'] for a in inventory['assets'] if a.get('class') == 'SkeletalMesh']
paths += ['/Game/RifleAnimsetPro/Animations/InPlace/' + name for name in
          ('Rifle_Idle', 'Rifle_WalkFwdLoop', 'Rifle_RunFwdLoop', 'Rifle_ShootOnce',
           'Rifle_Reload_2', 'Rifle_Hit_C_1', 'Rifle_Death_3')]
for path in paths:
    try:
        asset = unreal.EditorAssetLibrary.load_asset(path)
        file = EXPORTS / (asset.get_name() + '.fbx')
        task = unreal.AssetExportTask()
        task.object, task.filename, task.options = asset, str(file), options
        task.automated, task.prompt, task.replace_identical = True, False, True
        ok = unreal.Exporter.run_asset_export_task(task)
        report['exports'].append({'asset': path, 'class': asset.get_class().get_name(),
            'ok': bool(ok), 'file': file.relative_to(LAB).as_posix(),
            'size_bytes': file.stat().st_size if file.exists() else 0,
            'sha256': hashlib.sha256(file.read_bytes()).hexdigest() if file.exists() else None,
            'errors': list(task.errors)})
    except Exception:
        report['errors'].append({'asset': path, 'traceback': traceback.format_exc()})
report['finished_at'] = datetime.now().astimezone().isoformat()
(OUT / 'ue_resaved_exports.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
unreal.log('CS549_RESAVED_EXPORT_DONE ' + str(len(report['exports'])))
