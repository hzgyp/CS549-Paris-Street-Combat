"""Explicit struct-array material writeback on the two-file experimental derivative only."""
import hashlib,json,shutil,traceback
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[2]
E=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/ContinuousArmsV3'
OUT=E/'native_material_v1';assert not OUT.exists();OUT.mkdir()
(OUT/'source.py').write_bytes(Path(__file__).read_bytes())
previous=json.loads((E/'native_import_v2/result.json').read_text())
protected=json.loads((ROOT/'Failures/FP001-20261003-first-person-view/MANIFEST.json').read_text(encoding='utf-8-sig'))['protected_files']
def guard(records):return all((ROOT/f['path']).stat().st_size==f['size_bytes'] and hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256'] for f in records)
assert guard(protected+previous['native_files'])
r={'scope':__doc__,'errors':[],'before_files':previous['native_files'],'native_files':[]}
try:
    before=OUT/'Before';before.mkdir()
    for f in previous['native_files']:shutil.copy2(ROOT/f['path'],before/Path(f['path']).name)
    mesh=unreal.load_asset('/Game/ParisCombat/Characters/FirstPersonContinuousArmsV3/SK_PC_ContinuousArmsV3')
    slots=mesh.get_editor_property('materials')
    r['before_materials']=[s.material_interface.get_path_name() for s in slots]
    for i,slot in enumerate(slots):
        assert str(slot.material_slot_name)==previous['materials'][i]['slot']
        slot.material_interface=unreal.load_asset(previous['materials'][i]['native'])
        slots[i]=slot
    mesh.modify();mesh.set_editor_property('materials',slots)
    r['after_materials']=[s.material_interface.get_path_name() for s in mesh.get_editor_property('materials')]
    assert r['after_materials']==[m['native'] for m in previous['materials']]
    assert unreal.EditorAssetLibrary.save_loaded_asset(mesh,False)
    for f in previous['native_files']:
        p=ROOT/f['path'];r['native_files'].append({'path':f['path'],'size_bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    assert r['native_files'][1]==previous['native_files'][1], 'Skeleton was not part of material repair'
    r['protected_40_unchanged']=guard(protected);assert r['protected_40_unchanged']
    r['status']='saved_explicit_binding_requires_fresh_load'
except Exception:r['errors'].append(traceback.format_exc());r['status']='failed'
(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
