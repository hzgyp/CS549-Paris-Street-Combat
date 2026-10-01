"""Inspect bounded repair inputs without changing vendor packages."""
import json
import traceback
from pathlib import Path
import unreal

LAB = Path(unreal.Paths.project_dir()).resolve()
OUT = LAB / 'Evidence/Repair20261001'
OUT.mkdir(parents=True, exist_ok=True)
report = {'engine': unreal.SystemLibrary.get_engine_version(), 'errors': [], 'materials': [],
          'textures': [], 'api': {}}
for name in ('MaterialEditingLibrary', 'Material', 'SkeletalMeshComponent',
             'SceneCaptureComponent2D', 'SkyLightComponent', 'EditorLevelLibrary', 'World'):
    report['api'][name] = [v for v in dir(getattr(unreal, name)) if any(w in v.lower()
        for w in ('expression', 'render', 'tick', 'register', 'update', 'parameter', 'capture', 'refresh'))]
report['exporters'] = [v for v in dir(unreal) if 'TextureExporter' in v]
inventory = json.loads((LAB / 'Evidence/ue_load_inventory.json').read_text(encoding='utf-8'))
for item in inventory['assets']:
    try:
        if item.get('class') not in ('Material', 'MaterialInstanceConstant', 'Texture2D'):
            continue
        asset = unreal.load_asset(item['path'])
        if isinstance(asset, unreal.Texture2D):
            report['textures'].append({'path': item['path'], 'name': asset.get_name(),
                'srgb': asset.get_editor_property('srgb'),
                'compression': str(asset.get_editor_property('compression_settings'))})
        else:
            row = {'path': item['path'], 'class': item['class'], 'parameters': {}}
            if isinstance(asset, unreal.MaterialInstanceConstant):
                row['parent'] = asset.get_editor_property('parent').get_path_name()
                for name in unreal.MaterialEditingLibrary.get_texture_parameter_names(asset):
                    tex = unreal.MaterialEditingLibrary.get_material_instance_texture_parameter_value(asset, name)
                    row['parameters'][str(name)] = tex.get_path_name() if tex else None
                for name in unreal.MaterialEditingLibrary.get_scalar_parameter_names(asset):
                    row.setdefault('scalars', {})[str(name)] = unreal.MaterialEditingLibrary.get_material_instance_scalar_parameter_value(asset, name)
            else:
                for name in unreal.MaterialEditingLibrary.get_texture_parameter_names(asset):
                    tex = unreal.MaterialEditingLibrary.get_material_default_texture_parameter_value(asset, name)
                    row['parameters'][str(name)] = tex.get_path_name() if tex else None
                row['graph'] = []
                for expression in unreal.MaterialEditingLibrary.get_material_expressions(asset):
                    node = {'name': expression.get_name(), 'class': expression.get_class().get_name()}
                    for prop in ('texture', 'parameter_name', 'mask_r', 'mask_g', 'mask_b', 'mask_a', 'const_a', 'const_b'):
                        try:
                            val = expression.get_editor_property(prop)
                            node[prop] = val.get_path_name() if isinstance(val, unreal.Object) else str(val)
                        except Exception:
                            pass
                    row['graph'].append(node)
            if isinstance(asset, unreal.Material) and 'M_Eye' in item['path']:
                row['properties'] = {}
                for prop in ('blend_mode', 'shading_model', 'two_sided', 'use_material_attributes', 'expressions'):
                    try:
                        row['properties'][prop] = str(asset.get_editor_property(prop))
                    except Exception as exc:
                        row['properties'][prop] = str(exc)
            report['materials'].append(row)
    except Exception:
        report['errors'].append({'path': item['path'], 'error': traceback.format_exc()})
(OUT / 'ue_repair_probe.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
unreal.log('CS549_REPAIR_PROBE_DONE')
