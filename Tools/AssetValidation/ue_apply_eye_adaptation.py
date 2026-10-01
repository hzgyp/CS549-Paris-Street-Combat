"""Save editor-aware adapted character packages without altering vendor assets."""
import json
import sys
import traceback
from pathlib import Path
import unreal

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ue_eye_repair import build_eye_material

LAB = Path(unreal.Paths.project_dir()).resolve()
OUT = LAB / 'Evidence/Repair20261001'
report = {'engine': unreal.SystemLibrary.get_engine_version(), 'models': [], 'errors': []}
sources = [('/Game/GermanSoldier/Meshes/SK_WWII_GermanSoldier_varA', 'German'),
    ('/Game/GermanSoldier/Meshes/SK_WWII_GermanSoldier_varB', 'German'),
    ('/Game/USParatrooper/Meshes/SK_WWII_US_Paratrooper_simple', 'Allied'),
    ('/Game/USParatrooper/Meshes/SK_WWII_US_Paratrooper_simpleB', 'Allied')]
for source, faction in sources:
    try:
        original = unreal.load_asset(source)
        target = '/Game/ParisCombat/Characters/Adaptation/Meshes/' + original.get_name() + '_UE582_v1'
        mesh = unreal.load_asset(target) if unreal.EditorAssetLibrary.does_asset_exist(target) else unreal.EditorAssetLibrary.duplicate_asset(source, target)
        mesh.modify()
        slots = mesh.get_editor_property('materials')
        replaced = []
        for n, slot in enumerate(slots):
            if slot.material_interface and 'eye' in slot.material_interface.get_path_name().lower():
                slot.material_interface = build_eye_material(faction)
                # Unreal Array iteration returns a struct copy. Assign it back explicitly.
                slots[n] = slot
                replaced.append(n)
        if len(replaced) != 1:
            raise RuntimeError('Expected exactly one eye slot: ' + str(replaced))
        mesh.set_editor_property('materials', slots)
        for n in replaced:
            actual = mesh.get_editor_property('materials')[n].material_interface
            if '/ParisCombat/Characters/Adaptation/Materials/M_EyePBR_' not in actual.get_path_name():
                raise RuntimeError('Eye material binding did not persist in the mesh property')
        if not unreal.EditorAssetLibrary.save_loaded_asset(mesh, False):
            raise RuntimeError('Could not save adapted mesh')
        report['models'].append({'source': source, 'adapted': target, 'eye_slots': replaced,
            'skeleton': mesh.get_editor_property('skeleton').get_path_name(),
            'physics_asset': mesh.get_editor_property('physics_asset').get_path_name()})
    except Exception:
        report['errors'].append(traceback.format_exc())
(OUT / 'native_adaptation.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
unreal.log('CS549_NATIVE_ADAPTATION_DONE')
