"""Export source textures and material parameters for a portable Blender source."""
import hashlib
import json
import traceback
from pathlib import Path
import unreal

LAB = Path(unreal.Paths.project_dir()).resolve()
OUT = LAB / 'Evidence/Repair20261001'
TEXTURES = OUT / 'Textures'
TEXTURES.mkdir(parents=True, exist_ok=True)
probe = json.loads((OUT / 'ue_repair_probe.json').read_text(encoding='utf-8'))
report = {'textures': [], 'errors': [], 'normal_convention': 'Source DirectX; invert green when wiring Blender tangent normals.'}
for item in probe['textures']:
    try:
        asset = unreal.load_asset(item['path'])
        data = unreal.AssetRegistryHelpers.get_asset_registry().get_asset_by_object_path(asset.get_path_name())
        source_format = str(data.get_tag_value('SourceFormat'))
        hdr = any(word in source_format.upper() for word in ('16F', '32F', 'RGBE', 'BGRE', 'FLOAT'))
        extension = '.exr' if hdr else '.png'
        file = TEXTURES / (item['path'].removeprefix('/Game/') + extension)
        file.parent.mkdir(parents=True, exist_ok=True)
        task = unreal.AssetExportTask()
        task.object, task.filename = asset, str(file)
        task.exporter = unreal.TextureExporterEXR() if hdr else unreal.TextureExporterPNG()
        task.automated, task.prompt, task.replace_identical = True, False, False
        if not file.exists() and not unreal.Exporter.run_asset_export_task(task):
            raise RuntimeError(str(list(task.errors)))
        report['textures'].append({**item, 'source_format': source_format, 'file': file.relative_to(OUT).as_posix(),
            'size_bytes': file.stat().st_size, 'sha256': hashlib.sha256(file.read_bytes()).hexdigest(),
            'flip_green_channel': asset.get_editor_property('flip_green_channel')})
    except Exception:
        report['errors'].append({'asset': item['path'], 'traceback': traceback.format_exc()})
(OUT / 'texture_exports.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
unreal.log('CS549_TEXTURE_EXPORT_DONE ' + str(len(report['textures'])))
